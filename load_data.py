import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy
from numpy import diff
import sys
import scipy
import json
import logging

def plot_data(data, index):
    """

    :param data: dataframe from reading csv
    :param index: where beats occur in dataframe
    :return: labeled plot with both data and red markers of peak detection
    """
    data_points = []
    headers = ['time', 'voltage']
    for x in index:
        data_points.append([data.loc[x+2]['time'], data.loc[x+2]['voltage']])
    data_points_df = pd.DataFrame(data_points, columns=headers)
    plt.plot(data['time'], data['voltage'])
    plt.scatter(data_points_df['time'], data_points_df['voltage'], c='red')
    plt.axis('tight')
    plt.ylabel('Voltage')
    plt.xlabel('Time (s)')
    plt.title('ECG with Peak Detection')
    plt.legend(['ECG', 'Peak Detected'])
    plt.show()
    logging.info('This only outputs a plot')


def plot_derivative(dx, dy, found):
    """

    :param dx: time dataframe adjusted for derivative array size change
    :param dy: derivative of data
    :param found: dataframe containing index, time, and voltage of beats detected
    :return: labeled plot with both derivative data and red markers of peak detection
    """
    plt.plot(dx['time'], dy)
    plt.scatter(found['time'], found['voltage'], c='red')
    plt.title('First Derivative with Peak Detection')
    plt.show()
    logging.info('only outputs a plot')


def calc_duration(data):
    """

    :param data: dataframe from reading csv
    :return: duration of time column in data
    """
    dur = data.loc[data.index[-1]]['time']-data.loc[1]['time']
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


def find_peaks(data):
    """

    :param data: dataframe from reading csv
    :return: differentiated voltage array
    """
    dx = data.loc[3]['time']-data.loc[2]['time']
    dy = diff(data['voltage'])/dx
    return dy


def find_peaks_two(dx, dy):
    """

    :param dx: time dataframe adjusted for derivative array size change
    :param dy: differentiated voltage array
    :return: data frame containing indices, time, and voltage where peak occurs
    """
    peak_max = dy.max()*.5
    d = {'indices': [], 'time': [], 'voltage': []}
    return_values = []
    y_old = 0
    index_old = -999
    indices = []
    for index, y in enumerate(dy):
        if y - y_old < 0 and y > peak_max and index -index_old > 4:
            return_values.append([index, dx.loc[index]['time'], y])
            indices.append(index)
            index_old = index
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


def main():
    """

    :return: saved json file of dictionary metrics that holds all requested values
    """

    path = os.getcwd()
    new_path = os.getcwd() + '/data'
    os.chdir(new_path)
    headers = ['time', 'voltage']
    for file in os.listdir(os.getcwd()):
        if file.split('.')[1] == 'csv':
            data = pd.read_csv(file, names=headers)
            extreme = calc_v_extreme(data)
            dur = calc_duration(data)
            interval = user_input(dur)
            dy = find_peaks(data)
            dx = data.drop([0, 0])
            found = find_peaks_two(dx, dy)
            bpm = calc_avg(interval, found, dur)
            metrics = create_metrics(found, extreme, dur, bpm)
            plot_derivative(dx, dy, found)
            plot_data(data, found['index'])
            write_json(file, metrics)


if __name__ == "__main__":
    main()