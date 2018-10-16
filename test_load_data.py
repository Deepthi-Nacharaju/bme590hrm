import pytest
from load_data import plot_data
from load_data import plot_derivative
form load_data import calc_duration


@pytest.mark.parametrize("data, index, expected",[
    ([1, 2, 3], 1, True),
    ]
                         )


def test_plot_data(data, index, expected):
    response = plot_data(data, index)
    assert response == expected


@pytest.mark.parametrize("data, expected",[
    (data, 75),
    ]
                         )

    
def test_calc_duration(data,expected):
    response = calc_duration(data)
    assert response == expected
