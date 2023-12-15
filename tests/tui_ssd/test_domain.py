import pytest
from valid8 import ValidationError
from tui_ssd.domain import Temperature, Humidity, Wind, Condition, RecordDate, Record, SecureWeather


# TESTS FOR TEMPERATURE
@pytest.mark.parametrize('temp', [
    51,
    -51,
    'a',
    '',
    None
])
def test_wrong_temperature_raises_validation_error(temp):
    with pytest.raises(ValidationError):
        Temperature(temp)


@pytest.mark.parametrize('temp', [
    50,
    -50,
    6,
    0
])
def test_correct_temperature_creation_value_and_str(temp):
    obj = Temperature(temp)
    assert obj.value == temp
    assert str(obj) == str(temp)


# TESTS FOR HUMIDITY
@pytest.mark.parametrize('hum', [
    101,
    -1,
    'a',
    '',
    None
])
def test_wrong_humidity_raises_validation_error(hum):
    with pytest.raises(ValidationError):
        Humidity(hum)


@pytest.mark.parametrize('hum', [
    99,
    100,
    1,
    0
])
def test_correct_humidity_creation_value_and_str(hum):
    obj = Humidity(hum)
    assert obj.value == hum
    assert str(obj) == str(hum)


# TESTS FOR WIND
@pytest.mark.parametrize('win', [
    201,
    -1,
    'a',
    '',
    None
])
def test_wrong_wind_raises_validation_error(win):
    with pytest.raises(ValidationError):
        Wind(win)


@pytest.mark.parametrize('win', [
    200,
    0,
    15
])
def test_correct_wind_creation_value_and_str(win):
    obj = Wind(win)
    assert obj.value == win
    assert str(obj) == str(win)


# TESTS FOR CONDITION
def test_condition_cannot_be_created_directly_with_constructor():
    with pytest.raises(TypeError):
        Condition('1')


def test_dictionary_values_are_valid():
    obj = Condition.create('1')
    assert obj.values_dictionary[1] == "SUNNY"
    assert obj.values_dictionary[2] == "CLOUDY"
    assert obj.values_dictionary[3] == "RAINY"
    assert obj.values_dictionary[4] == "FLURRY"


@pytest.mark.parametrize('cond', [
    '-1',
    '5',
    'a',
    ''
])
def test_wrong_condition_creation_with_create_raises_validation_error(cond):
    with pytest.raises(ValidationError):
        Condition.create(cond)


@pytest.mark.parametrize('cond, expected_value', [
    ('1', 'SUNNY'),
    ('2', 'CLOUDY'),
    ('3', 'RAINY'),
    ('4', 'FLURRY')
])
def test_correct_condition_creation_value_and_str(cond, expected_value):
    obj = Condition.create(cond)
    assert obj.value == expected_value
    assert str(obj) == expected_value


# TESTS FOR RECORD DATE
@pytest.mark.parametrize('date, expected_value', [
    ('09/09/2000 15:34:11', "09/09/2000@15:34:11"),
    ('01/01/2000 00:00:00', '01/01/2000@00:00:00'),
    ('31/12/2999 23:59:59', '31/12/2999@23:59:59'),
])
def test_correct_date_creation(date, expected_value):
    obj = RecordDate.create(date)
    assert obj.value == expected_value


@pytest.mark.parametrize('date', [
    '29/02/2001 10:00:00',
    '31/11/2000 10:00:00',
    '30/11/2000 25:00:00',
    '30/11/2000 10:60:00',
    '30/11/2000 10:00:60',
    'a',
    '',
    ' ',
    '01/01/3000 10:00:00',
    '31/12/1999 10:00:00'
])
def test_wrong_date_raises_exception(date):
    with pytest.raises(ValueError):
        # ValidationError is inherited by ValueError, so we catch also the ValidationError exception here
        RecordDate.create(date)


# TESTS FOR RECORD CLASS
def test_correct_creation_of_a_record_instance():
    temperature = Temperature(17)
    humidity = Humidity(25)
    wind = Wind(5)
    condition = Condition.create('2')
    rec_date = RecordDate.create('29/02/2000 10:00:45')
    obj = Record(temperature, humidity, wind, condition, rec_date)
    assert obj.temperature.value == 17 and str(obj.temperature) == '17'
    assert obj.humidity.value == 25 and str(obj.humidity) == '25'
    assert obj.wind.value == 5 and str(obj.wind) == '5'
    assert obj.condition.value == str(obj.condition) == 'CLOUDY'
    assert obj.record_date.value == str(obj.record_date) == '29/02/2000@10:00:45'


# TODO: tests for SecureWeather class
# TEST FOR SECURE WEATHER CLASS
