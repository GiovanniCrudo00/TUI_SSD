import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, Mock, call, MagicMock
from tui_ssd.app import App, main
from tui_ssd.domain import *


@pytest.fixture
def my_json():
    return [{
        "id": 44,
        "condition": "1",
        "humidity": 60,
        "temperature": 40,
        "wind": 20,
        "date": "2022-10-20T11:54:00+02:00"
    }, {
        "id": 45,
        "condition": "1",
        "humidity": 90,
        "temperature": 34,
        "wind": 17,
        "date": "2022-10-20T14:54:00+02:00"
    }]


@patch('getpass.getpass', side_effect=['valid_password'])
@patch('builtins.input', side_effect=['valid_username', 'valid_password', '0'])
@patch('builtins.print')
@patch('requests.post')
@patch('requests.get')
def test_app_connect_correct_login_and_logout(mocked_get, mocked_post, mocked_print, mocked_input, mocked_getpass, my_json):
    mocked_response = Mock()
    mocked_response.status_code = 200
    mocked_post.return_value = mocked_response

    mocked_response_get = Mock()
    mocked_response_get.status_code = 200
    mocked_response_get.json.return_value = my_json
    mocked_get.return_value = mocked_response_get

    main('__main__')
    mocked_print.assert_any_call('*** Your Secure Weather TUI ***')
    mocked_print.assert_any_call('Hello user, please enter your credentials below.')
    mocked_input.assert_any_call('Username: ')
    mocked_getpass.assert_any_call('Password: ')
    mocked_post.assert_any_call('http://localhost:8000/api/v1/auth/login/',
                                json={'username': 'valid_username', 'email': '', 'password': 'valid_password'})
    assert mocked_get.call_count == 1  # get records
    mocked_print.assert_any_call('0:\tExit')
    mocked_print.assert_any_call('Cya!')


@patch('getpass.getpass', side_effect=['fake_pass'])
@patch('builtins.input', side_effect=['fake_username', 'fake_pass', '1', '40', '60', '13', '1', '20/10/2022 11:54', '0'])
@patch('builtins.print')
@patch('requests.post')
@patch('requests.get')
def test_app_add_new_record(mocked_get, mocked_post, mocked_print, mocked_input, mocked_getpass, my_json):
    mocked_response = Mock()
    mocked_response.status_code = 200
    mocked_post.return_value = mocked_response

    mocked_response_get = Mock()
    mocked_response_get.status_code = 200
    mocked_response_get.json.return_value = my_json
    mocked_get.return_value = mocked_response_get

    App().run()
    assert mocked_post.call_count == 3  # Login, add record, logout
    mocked_get.assert_called()
    assert list(filter(lambda x: '20/10/2022 at 11:54' in str(x), mocked_print.mock_calls))
    mocked_input.assert_called()
    mocked_print.assert_any_call('Cya!')


@patch('getpass.getpass', side_effect=['fake_pass'])
@patch('builtins.input', side_effect=['fake_username', 'fake_pass', '1', '160', '40', '60',
                                      '13', '1', 'wrong_date', '20/10/2022 11:54', '0'])
@patch('builtins.print')
@patch('requests.post')
@patch('requests.get')
def test_app_add_new_record_resists_wrong_values(mocked_get, mocked_post, mocked_print, mocked_input, mocked_getpass, my_json):
    mocked_response = Mock()
    mocked_response.status_code = 200
    mocked_post.return_value = mocked_response

    mocked_response_get = Mock()
    mocked_response_get.status_code = 200
    mocked_response_get.json.return_value = my_json
    mocked_get.return_value = mocked_response_get

    App().run()
    assert mocked_post.call_count == 3  # Login, add record, logout
    mocked_get.assert_called()
    assert list(filter(lambda x: '20/10/2022 at 11:54' in str(x), mocked_print.mock_calls))
    mocked_print.assert_any_call('Record added!')
    mocked_input.assert_called()
    mocked_print.assert_any_call('Cya!')


@patch('getpass.getpass', side_effect=['fake_pass'])
@patch('builtins.input', side_effect=['fake_username', 'fake_pass', '2', '0', '0'])
@patch('builtins.print')
@patch('requests.post')
@patch('requests.get')
def test_app_remove_record_can_be_cancelled(mocked_get, mocked_post, mocked_print, mocked_input, mocked_getpass, my_json):
    mocked_response = Mock()
    mocked_response.status_code = 200
    mocked_post.return_value = mocked_response

    mocked_response_get = Mock()
    mocked_response_get.status_code = 200
    mocked_get.return_value = mocked_response_get
    mocked_response_get.json.return_value = my_json

    App().run()
    mocked_input.assert_called()
    mocked_print.assert_any_call('Cancelled!')
    mocked_print.assert_any_call('Cya!')


@patch('getpass.getpass', side_effect=['fake_pass'])
@patch('builtins.input', side_effect=['fake_username', 'fake_pass', '2', '1', '0'])
@patch('builtins.print')
@patch('requests.post')
@patch('requests.get')
@patch('requests.delete')
def test_app_correct_remove_record(mocked_delete, mocked_get, mocked_post, mocked_print, mocked_input, mocked_getpass, my_json):
    mocked_response = MagicMock()
    mocked_response.status_code = 200
    mocked_post.return_value = mocked_response
    mocked_token = mocked_post().json().get()

    mocked_response_get = Mock()
    mocked_response_get.status_code = 200
    mocked_get.return_value = mocked_response_get
    mocked_response_get.json.return_value = my_json

    mocked__res_delete = Mock()
    mocked__res_delete.status_code = 204

    App().run()
    mocked_input.assert_called()
    mocked_delete.assert_called_with(url=f'http://localhost:8000/api/v1/records/{44}/',
                                     headers={'Authorization': f'Token {mocked_token}'})
    mocked_print.assert_any_call('Cya!')


@patch('getpass.getpass', side_effect=['fake_pass'])
@patch('builtins.input', side_effect=['fake_username', 'fake_pass', '3', '0'])
@patch('builtins.print')
@patch('requests.post')
@patch('requests.get')
def test_app_correct_generation_of_records(mocked_get, mocked_post, mocked_print, mocked_input, mocked_getpass, my_json):
    mocked_response = MagicMock()
    mocked_response.status_code = 200
    mocked_post.return_value = mocked_response
    mocked_response_post = [MagicMock(status_code=201) for _ in range(24)]
    mocked_response.side_effect = mocked_response_post
    # mocked_token = mocked_post().json().get()

    mocked_response_get = Mock()
    mocked_response_get.status_code = 200
    mocked_get.return_value = mocked_response_get
    mocked_response_get.json.return_value = my_json

    App().run()
    mocked_input.assert_called()
    assert mocked_post.call_count == 26  # Login, 24 add to db, Logout

    for res in mocked_response_post:  # Test 24 response with 201 code (effective save to database)
        assert res.status_code == 201

    mocked_print.assert_any_call('Cya!')


@patch('getpass.getpass', side_effect=['fake_pass'])
@patch('builtins.input', side_effect=['fake_username', 'fake_pass', '4', '0'])
@patch('builtins.print')
@patch('requests.post')
@patch('requests.get')
def test_app_sorting_by_temperature(mocked_get, mocked_post, mocked_print, mocked_input, mocked_getpass, my_json):
    mocked_response = MagicMock()
    mocked_response.status_code = 200
    mocked_post.return_value = mocked_response

    mocked_response_get = Mock()
    mocked_response_get.status_code = 200
    mocked_get.return_value = mocked_response_get
    mocked_response_get.json.return_value = my_json
    App().run()
    """
        Here we are accessing at the 26th and 27th position of the list of calls of the mocked_print
        We are asserting that the date (used as identifier to avoid ambiguities between numbers) are printed in 
        the correct order (sorted by temperature) on the screen  
    """
    first_rec = mocked_print.call_args_list[26]
    second_rec = mocked_print.call_args_list[27]

    assert '20/10/2022 at 14:54' in first_rec.args[0]
    assert '20/10/2022 at 11:54' in second_rec.args[0]

    mocked_print.assert_any_call('Cya!')


@patch('getpass.getpass', side_effect=['fake_pass'])
@patch('builtins.input', side_effect=['fake_username', 'fake_pass', '5', '0'])
@patch('builtins.print')
@patch('requests.post')
@patch('requests.get')
def test_app_sorting_by_humidity(mocked_get, mocked_post, mocked_print, mocked_input, mocked_getpass, my_json):
    mocked_response = MagicMock()
    mocked_response.status_code = 200
    mocked_post.return_value = mocked_response

    mocked_response_get = Mock()
    mocked_response_get.status_code = 200
    mocked_get.return_value = mocked_response_get
    mocked_response_get.json.return_value = my_json
    App().run()

    first_rec = mocked_print.call_args_list[26]
    second_rec = mocked_print.call_args_list[27]

    assert '20/10/2022 at 11:54' in first_rec.args[0]
    assert '20/10/2022 at 14:54' in second_rec.args[0]

    mocked_print.assert_any_call('Cya!')


@patch('getpass.getpass', side_effect=['fake_pass'])
@patch('builtins.input', side_effect=['fake_username', 'fake_pass', '6', '0'])
@patch('builtins.print')
@patch('requests.post')
@patch('requests.get')
def test_app_sorting_by_wind(mocked_get, mocked_post, mocked_print, mocked_input, mocked_getpass, my_json):
    mocked_response = MagicMock()
    mocked_response.status_code = 200
    mocked_post.return_value = mocked_response

    mocked_response_get = Mock()
    mocked_response_get.status_code = 200
    mocked_get.return_value = mocked_response_get
    mocked_response_get.json.return_value = my_json
    App().run()

    first_rec = mocked_print.call_args_list[26]
    second_rec = mocked_print.call_args_list[27]

    assert '20/10/2022 at 14:54' in first_rec.args[0]
    assert '20/10/2022 at 11:54' in second_rec.args[0]

    mocked_print.assert_any_call('Cya!')


@patch('getpass.getpass', side_effect=['fake_pass'])
@patch('builtins.input', side_effect=['fake_username', 'fake_pass', '7', '0'])
@patch('builtins.print')
@patch('requests.post')
@patch('requests.get')
def test_app_sorting_by_date(mocked_get, mocked_post, mocked_print, mocked_input, mocked_getpass, my_json):
    mocked_response = MagicMock()
    mocked_response.status_code = 200
    mocked_post.return_value = mocked_response

    mocked_response_get = Mock()
    mocked_response_get.status_code = 200
    mocked_get.return_value = mocked_response_get
    mocked_response_get.json.return_value = my_json
    App().run()

    first_rec = mocked_print.call_args_list[26]
    second_rec = mocked_print.call_args_list[27]

    assert '20/10/2022 at 11:54' in first_rec.args[0]
    assert '20/10/2022 at 14:54' in second_rec.args[0]

    mocked_print.assert_any_call('Cya!')


# TODO: test wrong credentials provided
@patch('getpass.getpass', side_effect=['wrong_pass', 'valid_pass'])
@patch('builtins.input', side_effect=['fake_username', 'wrong_pass', 'username', 'valid_pass', '0', '0'])
@patch('builtins.print')
@patch('requests.post')
@patch('requests.get')
def test_app_wrong_credentials_given(mocked_get, mocked_post, mocked_print, mocked_input, mocked_getpass, my_json):
    mocked_bad_response = MagicMock()
    mocked_bad_response.status_code = 400

    mocked_ok_response = MagicMock()
    mocked_ok_response.status_code = 200

    """
        Here we are configuring 3 side effects on the two posts bacause:
            The first is a post that gives 400 bad request with the wrong credentials
            The second post gives 200 OK  
        We use the side effect of the second post also to pass the logout, since we are manually setting
        the 3 side_effects the test is unable to use the same post with 200 code to pass the login and logout.
        Hence we need to pass the second post's side effect 2 times, in order the posts are headed to:
            First login with wrong credentials (mocked by the response code 400 of the first post mock)
            Second login with correct credentials (mocked by 200 OK of the second post mock)
            Logout after a correct login (mocked also by the second post that gives 200 OK)
    """
    mocked_post.side_effect = [mocked_bad_response, mocked_ok_response, mocked_ok_response]

    main('__main__')

    mocked_post.assert_any_call('http://localhost:8000/api/v1/auth/login/',
                                json={'username': 'fake_username', 'email': '', 'password': 'wrong_pass'})

    mocked_print.assert_any_call('Unable to login, please check your credentials...')


# TODO: test permission restrictions
# TODO: test the fetch of data from db 8. of menu
# TODO: Test the global exception handler
