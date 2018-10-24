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
import math

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

    :param dx: time step size
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

    :param data: imported data frame with padding
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
    avg = (dy.max()-dy.min())*.25+dy.min()
    for index, y in enumerate(dy):
        if y - y_old > 0 and float(data.loc[index]['time']) > 0:
            go = True
        if y - y_old <= 0 and index -index_old > 5 and switch == False and go == True:
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

    :param duration: the time length of the data file for use as default
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
    if interval > duration:
        print('User Input Exceeds Data Duration. Default = ' + str(duration))
        out = list([duration, False])
    return out


def calc_avg(interval, found, dur):
    """

    :param interval: time length of data file
    :param found: dataframe holding indices, time and voltage measurements of detected peaks
    :param dur: calculated duration from calc_duration function
    :return: calculated bpm measurement
    """
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


def Hilbert(data, cutoff):
    """

    :param data: padded data
    :param cutoff: cutoff frequency for low pass filter
    :return: enveloped with low pass filter data
    """
    analytic_signal = hilbert(data['voltage'])
    amplitude_envelope = np.abs(analytic_signal)
    N = 2  # Filter order
    Wn = cutoff  # Cutoff frequency
    B, A = signal.butter(N, Wn, output='ba')
    filtered = signal.filtfilt(B, A, amplitude_envelope)
    #filtered = signal.filtfilt(B, A, filtered)
    return filtered


def edge_case(data):
    """

    :param data: read in data file
    :return: data file padded with -.25
    """
    extra = []
    headers = ['time', 'voltage']
    try:
        dt = data.loc[50]['time']-data.loc[49]['time']
    except TypeError:
        dt = float(data.loc[50]['time']) - float(data.loc[49]['time'])
    for x in range(0,200):
        extra.append([dt*x+float(data.loc[len(data['time'])-1]['time']), -0.25])
    extra = pd.DataFrame(extra, columns=headers)
    data = data.append(extra)
    data = data.reset_index()
    extra2 = []
    for x in range(0, 200):
        extra2.append([float(data.loc[0]['time']) - dt*200 + dt * x, -0.25])
    extra2 = pd.DataFrame(extra2, columns=headers)
    data = extra2.append(data)
    data = data.reset_index()
    return data


def check_spacing(found,data):
    """

    :param found: dataframe holding indices, time, and voltage of detected peaks
    :param data: padded data
    :return: boolean indicating if spacing of detected peaks is inconsistent and suspicious
    """
    difference = []
    old_x = 0
    for x in found['index']:
        difference.append(data.loc[x]['time']-data.loc[old_x]['time'])
        old_x = x
    if max(difference) - sum(difference)/len(difference) > 1:
        return True
    else:
        return False


def is_data_valid(data):
    """

    :param data: input raw dataframe with time column
    :return: data frame that removed all blank spaces or NaN
    """
    dropped = 0
    for index_, y in enumerate(data['time']):
        try:
            data['time'][index_] = float(y)
        except ValueError:
            print(data.loc[index_]['time'])
            data = data.drop(data.index[index_])
            dropped += 1
            print(y)
    for index_, y in enumerate(data['voltage']):
        try:
            data['voltage'][index_] = float(y)
        except ValueError:
            print(data.loc[index_]['voltage'])
            print(y)
            data = data.drop(data.index[index_])
            dropped += 1
    return data


def check_loop(found, data, filter_value, file):
    """

    :param found: dataframe containing indices, time, and voltage of peaks
    :param data: loaded padded data
    :param filter_value: low pass filter value
    :param file: file name
    :return: updated found file after checking suspicions
    """
    if not found.empty:
        check = check_spacing(found, data)
        counter = 0
        while check:
            filter_value += 0.002
            filtered = Hilbert(data, filter_value)
            plt.plot(data['time'], data['voltage'])
            plt.plot(data['time'], filtered)
            plt.title(str(file) + ' ' + str(counter))
            plt.show()
            # dy = find_peaks(data, filtered, dx)
            dx = data.drop([0, 0])
            found = find_peaks_two(dx, filtered, data)
            check = check_spacing(found, data)
            if counter == 3:
                check = False
            counter += 1

    return found


def write_excel(file_number, export_excel):
    wb = load_workbook('Beat_Tracking.xlsx')
    ws = wb.active
    counter = 0
    yellowFill = PatternFill(start_color='FFFFFF00',
                          end_color='FFFFFF00',
                          fill_type='solid')
    whiteFill = PatternFill(start_color='FFFFFFFF',
                          end_color='FFFFFFFF',
                          fill_type='solid')
    orangeFill = PatternFill(start_color='FFFF8C00',
                          end_color='FFFF8C00',
                          fill_type='solid')

    redFill =  PatternFill(start_color='FFFF0000',
                          end_color='FFFF0000',
                          fill_type='solid')
    greenFill =  PatternFill(start_color='FF00FF00',
                          end_color='FF00FF00',
                          fill_type='solid')
    for x in file_number:
        ws['C' + str(int(x) + 1)] = str(export_excel[counter])
        counter += 1
        try:
            if np.abs(int(ws['C'+ str(int(x) + 1)].value) - int(ws['B' + str(int(x) + 1)].value))>5:
                ws['C' + str(int(x) + 1)].fill = redFill
            elif np.abs(int(ws['C' + str(int(x) + 1)].value) - int(ws['B' + str(int(x) + 1)].value)) >2:
                ws['C' + str(int(x) + 1)].fill = orangeFill
            elif np.abs(int(ws['C'+ str(int(x) + 1)].value) - int(ws['B' + str(int(x) + 1)].value))>0:
                ws['C' + str(int(x) + 1)].fill = yellowFill
            elif np.abs(int(ws['C' + str(int(x) + 1)].value) - int(ws['B' + str(int(x) + 1)].value)) == 0:
                ws['C' + str(int(x) + 1)].fill = greenFill
            else:
                ws['C' + str(int(x) + 1)].fill = whiteFill
        except TypeError:
            print('File ' + str(x) + ' has not been tracked')
            ws['C' + str(int(x) + 1)].fill = whiteFill
    wb.save('Beat_Tracking.xlsx')

def main():
    """

    :return: saved json file of dictionary metrics that holds all requested values
    """
    plt.close('all')
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
                data = is_data_valid(data)
                try:
                    dx = data.loc[3]['time'] - data.loc[2]['time']
                except TypeError:
                    dx = float(data.loc[3]['time']) - float(data.loc[2]['time'])
                data = edge_case(data)
                filter_value = 0.008
                filtered = Hilbert(data, filter_value)
                dy = find_peaks(data, filtered, dx)
                dx = data.drop([0, 0])
                found = find_peaks_two(dx, filtered, data)
                found = check_loop(found, data, filter_value, file)
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

    write_excel(file_number, export_excel)


if __name__ == "__main__":
    main()