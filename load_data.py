import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from numpy import diff
import sys
import scipy
import scipy.signal as signal
from scipy.signal import hilbert, chirp
import json
import logging
from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

def plot_data(data, filtered, index, file):
    """

    :param data: dataframe from reading csv
    :param index: where beats occur in dataframe
    :return: labeled plot with both data and red markers of peak detection
    """
    data_points = []
    headers = ['time', 'voltage']
    for x in index:
        #data_points.append([data.loc[x]['time'], data.loc[x]['voltage']])
        data_points.append([data.loc[x]['time'], filtered[x]])

    data_points_df = pd.DataFrame(data_points, columns=headers)
    plt.plot(data['time'], data['voltage'])
    plt.scatter(data_points_df['time'], data_points_df['voltage'], c='red')
    plt.plot(data['time'], filtered)
    plt.axis('tight')
    plt.ylabel('Voltage')
    plt.xlabel('Time (s)')
    plt.title('ECG with Peak Detection: ' + str(file))
    plt.legend(['ECG', 'LPF Envelope', 'Detected Peak'])
    plt.show()
    logging.info('This only outputs a plot')
    return filtered


def plot_derivative(dx, dy, found, file):
    """

    :param file: Name of working file
    :param dx: time dataframe adjusted for derivative array size change
    :param dy: derivative of data
    :param found: dataframe containing index, time, and voltage of beats detected
    :return: labeled plot with both derivative data and red markers of peak detection
    """
    plt.plot(dx['time'], dy)
    #plt.plot(data['time'], filtered)
    plt.scatter(found['time'], found['voltage'], c='red')
    plt.title('First Derivative with Peak Detection: ' + str(file))
    plt.show()
    logging.info('only outputs a plot')


def calc_duration(data):
    """

    :param data: dataframe from reading csv
    :return: duration of time column in data
    """
    try:
        dur = data.loc[data.index[-1]]['time']-data.loc[1]['time']
    except TypeError:
        dur = float(data.loc[data.index[-1]]['time']) - float(data.loc[1]['time'])
    return dur


def calc_v_extreme(data):
    """

    :param data: dataframe from reading csv
    :return: tuple containing minimum and maximum values
    """
    max_val = data['voltage'].max()
    min_val = data['voltage'].min()
    store = (max_val, min_val)
    return store


def find_peaks(data, filtered, dx):
    """

    :param filtered: Hilbert Filtered data
    :param data: dataframe from reading csv
    :return: differentiated voltage array
    """
    #try:
    dy = diff(filtered)/dx
    #except TypeError:
     #   dx = float(data.loc[3]['time'])-float(data.loc[2]['time'])
      #  dy = list()
        #for x, num in enumerate(data['voltage']):
         #   if not x == 0:
          #      dy.append(diff([data.loc[x]['voltage'], data.loc[x]['voltage']])/dx)
    return dy


def find_peaks_two(dx, dy, data):
    """

    :param data: original data frame
    :param dx: time dataframe adjusted for derivative array size change
    :param dy: differentiated voltage array
    :return: data frame containing indices, time, and voltage where peak occurs
    """
    peak_max = dy.max()*.35
    #peak_max = 0
    d = {'indices': [], 'time': [], 'voltage': []}
    return_values = []
    y_old = dy[0]
    index_old = -999
    indices = []
    switch = False
    go = False
    avg = sum(dy)/len(dy)
    avg = (dy.max()-dy.min())*.25+dy.min()
    for index, y in enumerate(dy):
        if y - y_old > 0 and data.loc[index]['time'] > 0:
            go = True
        if y - y_old <= 0 and y > avg and index -index_old > 5 and switch == False and go == True:
            if index_old == -999 or go == True: #data.loc[index]['time']-data.loc[index_old]['time'] > 0.001:
                return_values.append([index, dx.loc[index]['time'], y])
                indices.append(index)
                index_old = index
                switch = True
        if y - y_old > 0 and go == True:
            switch = False
        y_old = y
    headers = ['index', 'time', 'voltage']
    return_df = pd.DataFrame(return_values, columns=headers)
    return return_df


def user_input(duration):
    """

    :return: user chosen input for time window over which to average
    """
    try:
        interval_one = sys.argv[1]
        interval_two = sys.argv[2]
        interval = list([float(interval_one),float(interval_two)])
        out = list([interval, True])
    except IndexError:
        interval = duration
        print('No Time Window Indicated. Default = ' + str(interval))
        out = list([interval, False])
    logging.debug('What type of error does this cause? --> IndexError')
    return out


def calc_avg(interval, found, dur):
    if not interval[1]:
        bpm = int(float(len(found['time']))/dur*60)
    else:
        bpm_range = interval[0]
        bpm_count = 0
        for x in found['time']:
            if x > bpm_range[0] and x < bpm_range[1]:
                bpm_count += 1
        bpm = float(bpm_count)/(float(bpm_range[1])-float(bpm_range[0]))*60

    return bpm


def create_metrics(found, extreme, dur, bpm):
    """

    :param found: dataframe containing indices, time, and voltage columns for where peaks occur
    :param extreme: tuple containing max and min values
    :param dur: duration of time vector from input
    :param bpm: average bpm calculations in chosen interval
    :return: dictionary called metrics that holds all requested values
    """
    metrics = dict()
    metrics['voltage_extremes'] = extreme
    metrics['duration'] = dur
    metrics['num_beats'] = len(found['time'])
    metrics['mean_hr_bpm'] = bpm
    metrics['beats'] = list(found['time'])
    print(metrics)
    logging.info('Final Dictionary Creation')
    return metrics


def write_json(file, metrics):
    """

    :param file: name of imported csv file
    :param metrics: requested output that needs to be saved as a json
    :return: saves metrics into json
    """
    json_name = file.split('.')[0] + '.json'
    with open(json_name, 'w') as outfile:
        json.dump(metrics, outfile)

    logging.info('make sure everything in metrics is a dictionary and NOT a dataframe')

def Hilbert(data):
    analytic_signal = hilbert(data['voltage'])
    amplitude_envelope = np.abs(analytic_signal)
    N = 2  # Filter order
    Wn = 0.008  # Cutoff frequency
    B, A = signal.butter(N, Wn, output='ba')
    filtered = signal.filtfilt(B, A, amplitude_envelope)
    #filtered = signal.filtfilt(B, A, filtered)
    return filtered

def edge_case(data):
    extra = []
    headers = ['time', 'voltage']
    dt = data.loc[50]['time']-data.loc[49]['time']
    for x in range(0,200):
        extra.append([dt*x+data.loc[len(data['time'])-1]['time'], -0.25])
    extra = pd.DataFrame(extra, columns=headers)
    data = data.append(extra)
    data = data.reset_index()
    extra2 = []
    for x in range(0, 200):
        extra2.append([data.loc[0]['time'] - dt*200+ dt * x, -0.25])
    extra2 = pd.DataFrame(extra2, columns=headers)
    data = extra2.append(data)
    data = data.reset_index()
    return data

def main():
    """

    :return: saved json file of dictionary metrics that holds all requested values
    """
    plt.close('all')
    path = os.getcwd()
    new_path = os.getcwd() + '/data'
    os.chdir(new_path)
    headers = ['time', 'voltage']
    export_excel = list()
    file_number = list()
    for file in os.listdir(os.getcwd()):
        print(file)
        try:
            if file.split('.')[1] == 'csv':
                data = pd.read_csv(file, names=headers)
                extreme = calc_v_extreme(data)
                dur = calc_duration(data)
                interval = user_input(dur)
                dx = data.loc[3]['time'] - data.loc[2]['time']
                data = edge_case(data)
                filtered = Hilbert(data)
                dy = find_peaks(data, filtered, dx)
                dx = data.drop([0, 0])
                found = find_peaks_two(dx, filtered, data)
                bpm = calc_avg(interval, found, dur)
                metrics = create_metrics(found, extreme, dur, bpm)
                plot_derivative(dx, dy, found, file)
                plot_data(data, filtered, found['index'], file)
                write_json(file, metrics)
                export_excel.append(metrics['num_beats'])
                numb = file.split('.')[0]
                numb = numb.split('data')[1]
                file_number.append(numb)
        except IndexError:
            print('Ignore Folder')

    wb = load_workbook('Beat_Tracking.xlsx')
    ws = wb.active
    counter = 0
    yellowFill = PatternFill(start_color='FFFFFF00',
                          end_color='FFFFFF00',
                          fill_type='solid')
    whiteFill = PatternFill(start_color='FFFFFFFF',
                          end_color='FFFFFFFF',
                          fill_type='solid')
    for x in file_number:
        ws['C' + str(int(x) + 1)] = str(export_excel[counter])
        counter += 1
        try:
            if int(ws['C'+ str(int(x) + 1)].value) != int(ws['B' + str(int(x) + 1)].value):
                ws['C' + str(int(x) + 1)].fill = yellowFill
            else:
                ws['C' + str(int(x) + 1)].fill = whiteFill
        except TypeError:
            print('File ' + str(x) + ' has not been tracked')
    wb.save('Beat_Tracking.xlsx')

if __name__ == "__main__":
    main()