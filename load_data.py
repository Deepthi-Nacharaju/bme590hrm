import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy
from numpy import diff
import sys
import scipy
import json


def plot_data(data, index):
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


def plot_derivative(dx, dy, found):
    plt.plot(dx['time'], dy)
    plt.scatter(found['time'], found['voltage'], c='red')
    plt.title('First Derivative with Peak Detection')
    plt.show()


def calc_duration(data):
    dur = data.loc[data.index[-1]]['time']-data.loc[1]['time']
    return dur


def calc_v_extreme(data):
    max_val = data['voltage'].max()
    min_val = data['voltage'].min()
    store = (max_val, min_val)
    return store


def find_peaks(data):
    dx = data.loc[3]['time']-data.loc[2]['time']
    dy = diff(data['voltage'])/dx
    return dy


def find_peaks_two(dx, dy):
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


def user_input():
    try:
        interval = sys.argv[1]
    except:
        interval = 60
    return interval


def create_metrics(interval, found, extreme, dur):
    metrics = dict()
    metrics['voltage_extremes'] = extreme
    metrics['duration'] = dur
    metrics['num_beats'] = len(found['time'])
    metrics['beats'] = found['time']
    bpm = metrics['num_beats'] / metrics['duration'] * interval
    metrics['mean_hr_bpm'] = bpm
    print(metrics)
    return metrics


def write_json(file, metrics):
    json_name = file.split('.')[0] + '.json'
    with open(json_name, 'w') as outfile:
        json.dump(metrics, outfile)


def main():
    interval = user_input()
    path = os.getcwd()
    new_path = os.getcwd() + '/data'
    os.chdir(new_path)
    headers = ['time', 'voltage']
    for file in os.listdir(os.getcwd()):
        if file.split('.')[1] == 'csv':
            data = pd.read_csv(file, names=headers)
            extreme = calc_v_extreme(data)
            dur = calc_duration(data)
            dy = find_peaks(data)
            dx = data.drop([0, 0])
            found = find_peaks_two(dx, dy)
            metrics = create_metrics(interval, found, extreme, dur)
            plot_derivative(dx, dy, found)
            plot_data(data, found['index'])
            write_json(file, metrics)


if __name__ == "__main__":
    main()