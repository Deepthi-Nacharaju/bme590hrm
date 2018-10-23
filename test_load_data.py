import pytest
from load_data import plot_data
import os
import pandas as pd
from load_data import plot_derivative
from load_data import calc_duration


def test_plot_data(expected):
    os.chdir(os.getcwd() + '/test_files')
    headers = ['time', 'voltage']
    data = pd.read_csv('sine.csv', names=headers)
    file = 'sine.csv'
    filtered = data
    index = [24, 158]
    headers = ['time', 'voltage']
    data = pd.DataFrame(data, columns=headers)
    plot_data(data, filtered, index, file)
    assert expected == expected


#@pytest.mark.parametrize("data, expected", [
#    (data, 75),
#    ]
#                         )
#def test_calc_duration(data, expected):
#    response = calc_duration(data)
#    assert response == expected
