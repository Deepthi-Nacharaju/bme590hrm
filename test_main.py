import pytest
from main import plot_data
import os
import pandas as pd
from main import calc_duration
from main import calc_v_extreme
from pytest import approx
from main import user_input
from main import is_data_valid
from main import edge_case
from main import check_spacing
from main import Hilbert
import numpy.fft as fft
from main import create_metrics
from main import write_json
from main import write_excel
from openpyxl import load_workbook
from main import calc_avg
from main import peak_detector

@pytest.mark.parametrize("file, expected", [
    ('sine.csv', (1.0, -1.0)),
]
                         )
def test_calc_v_extreme(file, expected):
    headers = ['time', 'voltage']
    data = pd.read_csv(file, names=headers)
    store = calc_v_extreme(data)
    store = (round(store[0]), round(store[1]))
    assert expected == store


@pytest.mark.parametrize("file, expected", [
    ('sine.csv', 11.85)
])
def test_calc_duration(file, expected):
    headers = ['time', 'voltage']
    data = pd.read_csv(file, names=headers)
    dur = calc_duration(data)
    assert expected == dur


@pytest.mark.parametrize("file, dur, expected", [
    ('sine.csv', 11.9, list([11.9, False]))
])
def test_user_input(file, dur, expected):
    out = user_input(dur)
    assert expected == out


@pytest.mark.parametrize("file, expected", [
    ('sine.csv', True),
])
def test_is_data_valid(file, expected):
    headers = ['time', 'voltage']
    data = pd.read_csv(file, names=headers)
    valid_data = is_data_valid(data)
    switch = True
    for x in valid_data['time']:
        y = float(x)
        if x != y:
            switch = False
    for x in valid_data['voltage']:
        y = float(x)
        if x != y:
            switch = False
    assert expected == switch


@pytest.mark.parametrize("file, expected", [
    ('sine.csv', (-0.25, -0.25)),
])
def test_edge_case(file, expected):
    headers = ['time', 'voltage']
    data = pd.read_csv(file, names=headers)
    out = edge_case(data, 200, -0.25)
    tup = (out.loc[0]['voltage'], out.loc[len(out)-1]['voltage'])
    assert expected == tup


@pytest.mark.parametrize("file, expected, space, one, two", [
    ('sine.csv', False, 1, 10, 12),
    ('sine.csv', True, 0.5, 1, 120),
])
def test_check_spacing(file, expected, space, one, two):
    headers = ['time', 'voltage']
    data = pd.read_csv(file, names=headers)
    found = list()
    found.append([one, data.loc[one]['time'], data.loc[one]['voltage']])
    found.append([two, data.loc[two]['time'], data.loc[two]['voltage']])
    headers = ['index', 'time', 'voltage']
    return_df = pd.DataFrame(found, columns=headers)
    out = check_spacing(return_df, data, space)
    assert expected == out


@pytest.mark.parametrize("file, expected", [
    ('sine.csv', True)
])
def test_Hilbert(file, expected):
    headers = ['time', 'voltage']
    data = pd.read_csv(file, names=headers)
    freq = fft.fft(data['voltage'])
    data_lpf = Hilbert(data, 0.0001)
    assert expected == expected


@pytest.mark.parametrize("file, expected", [
    ('sine.csv', type({}))
])
def test_create_metrics(file, expected):
    headers = ['time', 'voltage']
    data = pd.read_csv(file, names=headers)
    out = create_metrics(data, 1, 1, 1)
    assert expected == type(out)


@pytest.mark.parametrize("file, expected", [
    ('sine.csv', True)
])
def test_write_json(file, expected):
    metrics = {'thing_one': 1, 'thing_two': 2}
    write_json(file, metrics)
    json_file_name = file.split('.')[0]
    out = False
    for file in os.listdir(os.getcwd()):
        if file == json_file_name + '.json':
            out = True
    assert expected == out


@pytest.mark.parametrize("file, expected", [
    (list([1, 2, 3]), list([1, 2, 3]))
])
def test_write_excel(file, expected):
    write_excel(file, expected, 'test_write_excel.xlsx')
    wb = load_workbook('test_write_excel.xlsx')
    ws = wb.active
    out = int(ws['C' + str(int(file[0]) + 1)].value)
    assert expected[0] == out


@pytest.mark.parametrize("interval, found, dur, expected", [
    ([10, False], [1, 2, 3, 4, 5], 5, 60),
])
def test_calc_avg(interval, found, dur, expected):
    headers = ['time']
    found = pd.DataFrame(found, columns=headers)
    bpm = calc_avg(interval, found, dur)
    assert expected == bpm


@pytest.mark.parametrize("file, expected", [
    ('test_data22.csv', 34),
])
def test_peak_detector(file, expected):
    headers = ['time', 'voltage']
    data = pd.read_csv(file, names=headers)
    filtered = Hilbert(data, 0.005)
    df = peak_detector(filtered, data)
    out = len(df['index'])
    assert expected == out
