import pytest
from unittest.mock import patch, mock_open, Mock, call

from tui_ssd.app import App, main
from tui_ssd.domain import *


@pytest.fixture
def dummy_data():
    data = [
        [17, 25, 5, '1', '29/02/2000 10:00:45'],
        [21, 87, 110, '3', '20/10/2022 11:54:49'],
    ]
    return '\n'.join(['\t'.join(d) for d in data])


@patch('builtins.input', side_effect=['0'])
@patch('builtins.print')
def test_app_main(mocked_print, mocked_input):
    with patch('builtins.open', mock_open()):
        main('__main__')
        mocked_print.assert_any_call('*** Your Secure Weather TUI ***')
        mocked_print.assert_any_call('0:\tExit')
        mocked_print.assert_any_call('Cya!')
        mocked_input.assert_called()


# TODO: Test add a new record
# TODO: Test app resist to wrong values from inputs
# TODO: Test remove a record
# TODO: Test the user can cancel the removal of a record
# TODO: Test sorting by temperature
# TODO: Test sorting by humidity
# TODO: Test sorting by wind
# TODO: Test sorting by date
# TODO: Test the global exception handler
