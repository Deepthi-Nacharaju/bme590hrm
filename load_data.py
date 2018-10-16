import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy
from numpy import diff
import scipy

# Load all csv files from data folder

def load_csv():
    path = os.getcwd()
    new_path = os.getcwd() + '/data'
    os.chdir(new_path)
    for file in os.listdir(os.getcwd()):
        if file.split('.')[1] == 'csv':
            file.split('.')[0] = pd.read_csv(file)

def plot_data(data,index):
    data_points =[]
    headers = ['time','voltage']
    for x in index:
        data_points.append([data.loc[x+2]['time'], data.loc[x+2]['voltage']])
    data_points_df= pd.DataFrame(data_points, columns = headers)
    plt.plot(data['time'], data['voltage'])
    plt.scatter(data_points_df['time'], data_points_df['voltage'], c='red')
    plt.axis('tight')
    plt.ylabel('Voltage')
    plt.xlabel('Time (s)')
    plt.title('ECG with Peak Detection')
    plt.legend(['ECG','Peak Detected'])
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
            return_values.append([index,dx.loc[index]['time'], y])
            indices.append(index)
            index_old = index
        y_old = y

    headers = ['index','time','voltage']
    return_df = pd.DataFrame(return_values,columns = headers)
    return return_df

def main():
    headers = ['time','voltage']
    metrics = {}
    data = pd.read_csv("test_data1.csv", names=headers)
    extreme = calc_v_extreme(data)
    metrics['voltage_extremes'] = extreme
    dur = calc_duration(data)
    metrics['duration']= dur
    dy = find_peaks(data)
    dx = data.drop([0, 0])
    found = find_peaks_two(dx, dy)
    plt.plot(dx['time'], dy)
    plt.scatter(found['time'],found['voltage'], c='red')
    plt.title('First Derivative with Peak Detection')
    plt.show()
    plot_data(data, found['index'])
    metrics['num_beats'] = len(found['time'])
    metrics['beats'] = found['time']
    print(metrics)

if __name__ == "__main__":
    main()

# Make a Data Analysis Folder
# os.chdir(path)
#new_path_2 = os.getcwd() + '/data_analysis' #save figures to this folder