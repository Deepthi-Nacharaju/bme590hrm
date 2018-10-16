import pytest
from load_data import plot_data


@pytest.mark.parametrize("data, index, expected",[
    ([1, 2, 3], 1, True),
    ]
                         )
def test_plot_data(data, index, expected):
    response = plot_data(data, index)
    assert response == expected
