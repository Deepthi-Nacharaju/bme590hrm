import pandas as pd
import os
import matplotlib.pyplot as plt
# Load all csv files from data folder

def load_csv():
    path = os.getcwd()
    new_path = os.getcwd() + '/data'
    os.chdir(new_path)
    for file in os.listdir(os.getcwd()):
        if file.split('.')[1] == 'csv':
            file.split('.')[0] = pd.read_csv(file)

def plot_data(data):
    plt.plot(data['time'], data['voltage'])
    plt.axis('tight')
    plt.ylabel('Voltage')
    plt.xlabel('Time (s)')
    plt.title('Data')
    plt.show()

def calc_duration(data):
    dur = data.loc[data.index[-1]]['time']-data.loc[1]['time']
    return dur

def calc_v_extreme(data):
    max_val = data['voltage'].max()
    min_val = data['voltage'].min()
    store = (max_val, min_val)
    return store


def main():
    headers = ['time','voltage']
    metrics = {}
    data = pd.read_csv("test_data1.csv", names=headers)
    plot_data(data)
    extreme = calc_v_extreme(data)
    metrics['voltage_extremes'] = extreme
    dur = calc_duration(data)
    metrics['duration']= dur
    print(metrics)

if __name__ == "__main__":
    main()

# Make a Data Analysis Folder
# os.chdir(path)
#new_path_2 = os.getcwd() + '/data_analysis' #save figures to this folder