import pytest
from load_data import plot_data
import os
import pandas as pd
from load_data import plot_derivative
from load_data import calc_duration
from load_data import calc_v_extreme
from pytest import approx
from load_data import user_input
from load_data import is_data_valid
from load_data import edge_case


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


@pytest.mark.parametrize("file, expected",[
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
    out = edge_case(data)
    tup = (out.loc[0]['voltage'], out.loc[len(out)-1]['voltage'])
    assert expected == tup

#def test_plot_data(expected = 5):
    # headers = ['time', 'voltage']
    # data = pd.read_csv('sine.csv', names=headers)
    # file = 'sine.csv'
    # filtered = list(data)
    # index = pd.DataFrame([1, 2], columns='index')
    # headers = ['time', 'voltage']
    # data = pd.DataFrame(data, columns=headers)
    # plot_data(data, filtered, index['index'], file)
    # assert 5 == 5


#def test_plot_derivative(expected = 5):
    # headers = ['time', 'voltage']
    # data = pd.read_csv('sine.csv', names=headers)
    # file = 'sine.csv'
    # headers = ['time', 'voltage']
    # data = pd.DataFrame(data, columns=headers)
    # found = []
    # plot_derivative(data['time'], data['voltage'], found, file)
    #assert expected == expected
#@pytest.mark.parametrize("data, expected", [
#    (data, 75),
#    ]
#                         )
#def test_calc_duration(data, expected):
#    response = calc_duration(data)
#    assert response == expected
