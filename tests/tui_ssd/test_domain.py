import pytest
from valid8 import ValidationError
from tui_ssd.domain import *


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


# TESTS FOR ID
@pytest.mark.parametrize('id_val', [
    1,
    33,
    99999
])
def test_correct_id_creation_value(id_val):
    obj = Id(id_val)
    assert obj.value == id_val


@pytest.mark.parametrize('id_val', [
    0,
    100000,
    -1,
    'a',
    '',
    None
])
def test_wrong_id_raises_validation_error(id_val):
    with pytest.raises(ValidationError):
        Id(id_val)


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
    assert obj.enum_value == cond


# TESTS FOR RECORD DATE
@pytest.mark.parametrize('date, expected_value', [
    ('09/09/2000 15:34', "09/09/2000 at 15:34"),
    ('01/01/2000 00:00', '01/01/2000 at 00:00'),
    ('31/12/2999 23:59', '31/12/2999 at 23:59'),
])
def test_correct_date_creation(date, expected_value):
    obj = RecordDate.create(date)
    assert obj.value == expected_value


def test_correct_date_parsing_from_database():
    obj = RecordDate.parse('2023-12-08T12:20:00+01:00')
    assert obj.value == '08/12/2023 at 12:20'
    assert obj.db_date == '2023-12-08T12:20'


def test_wrong_date_parsing_raises_exception():
    with pytest.raises(ValueError):
        RecordDate.parse('a')


@pytest.mark.parametrize('date', [
    '29/02/2001 10:00',
    '31/11/2000 10:00',
    '30/11/2000 25:00',
    '30/11/2000 10:60',
    'a',
    '',
    ' ',
    '01/01/3000 10:00',
    '31/12/1999 10:00'
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
    rec_date = RecordDate.create('29/02/2000 10:00')
    obj = Record(temperature, humidity, wind, condition, rec_date)
    assert obj.temperature.value == 17 and str(obj.temperature) == '17'
    assert obj.humidity.value == 25 and str(obj.humidity) == '25'
    assert obj.wind.value == 5 and str(obj.wind) == '5'
    assert obj.condition.value == str(obj.condition) == 'CLOUDY'
    assert obj.record_date.value == str(obj.record_date) == '29/02/2000 at 10:00'


def test_correct_record_creation_with_optional_field():  # TODO: Write this
    temperature = Temperature(18)
    humidity = Humidity(26)
    wind = Wind(10)
    condition = Condition.create('3')
    rec_date = RecordDate.create('29/03/2000 15:10')
    rec_id = Id(45)
    obj = Record(temperature, humidity, wind, condition, rec_date, id=rec_id)
    assert obj.temperature.value == 18 and str(obj.temperature) == '18'
    assert obj.humidity.value == 26 and str(obj.humidity) == '26'
    assert obj.wind.value == 10 and str(obj.wind) == '10'
    assert obj.condition.value == str(obj.condition) == 'RAINY'
    assert obj.record_date.value == str(obj.record_date) == '29/03/2000 at 15:10'
    assert obj.id == rec_id


# TEST FOR SECURE WEATHER CLASS
@pytest.fixture
def dummy_records() -> list[Record]:
    return [
        Record(Temperature(17), Humidity(25), Wind(5), Condition.create('1'), RecordDate.create('29/02/2000 10:00')),
        Record(Temperature(21), Humidity(87), Wind(110), Condition.create('3'), RecordDate.create('20/10/2022 11:54')),
        Record(Temperature(36), Humidity(40), Wind(0), Condition.create('1'), RecordDate.create('05/08/2023 13:00')),
        Record(Temperature(-5), Humidity(4), Wind(20), Condition.create('4'), RecordDate.create('09/09/2000 21:12'))
    ]


@pytest.fixture
def my_record_list(dummy_records) -> RecordList:
    sw = RecordList()
    for rec in dummy_records:
        sw.add_record(rec)
    return sw


def test_correct_creation_of_records_list(my_record_list, dummy_records):
    assert my_record_list.records == len(dummy_records)
    for i in range(my_record_list.records):
        assert my_record_list.record(i) == dummy_records[i]


def test_wrong_index_raises_validation_error(my_record_list):
    with pytest.raises(ValidationError):
        my_record_list.record(99)


def test_correct_sorting_of_a_records_by_temperature(my_record_list, dummy_records):
    my_record_list.sort_by_temperature()
    dummy_records.sort(key=lambda x: x.temperature)
    for i in range(my_record_list.records):
        assert my_record_list.record(i) == dummy_records[i]


def test_correct_sorting_of_a_records_by_humidity(my_record_list, dummy_records):
    my_record_list.sort_by_humidity()
    dummy_records.sort(key=lambda x: x.humidity)
    for i in range(my_record_list.records):
        assert my_record_list.record(i) == dummy_records[i]


def test_correct_sorting_of_a_records_by_wind(my_record_list, dummy_records):
    my_record_list.sort_by_wind()
    dummy_records.sort(key=lambda x: x.wind)
    for i in range(my_record_list.records):
        assert my_record_list.record(i) == dummy_records[i]


def test_correct_sorting_of_a_records_by_date(my_record_list, dummy_records):
    my_record_list.sort_by_ascending_date()
    dummy_records.sort(key=lambda x: x.record_date)
    for i in range(my_record_list.records):
        assert my_record_list.record(i) == dummy_records[i]


def test_correct_list_dumping(my_record_list):
    my_record_list.dump_list()
    assert my_record_list.records == 0


def test_correct_sorting_by_date_after_parsing():
    rec1 = Record(Temperature(17), Humidity(25), Wind(5), Condition.create('1'), RecordDate.parse('2023-03-01T00:00:00+01:00'))
    rec2 = Record(Temperature(21), Humidity(87), Wind(110), Condition.create('3'), RecordDate.parse('2023-01-01T00:00:00+01:00'))
    rec3 = Record(Temperature(36), Humidity(40), Wind(0), Condition.create('1'), RecordDate.parse('2023-02-01T00:00:00+01:00'))
    rc = RecordList()
    rc.add_record(rec1)
    rc.add_record(rec2)
    rc.add_record(rec3)

    rc.sort_by_ascending_date()
    assert rc.record(0) == rec2


@pytest.mark.parametrize('value', [
    'Mr_Bean_',
    'mr_bean_user',
    'mr_be@n-@',
])
def test_correct_username_creation_value_and_str(value):
    obj = Username(value)
    assert str(obj) == value
    assert obj.value == value


@pytest.mark.parametrize('value', [
    'mr',
    '',
    ' ',
    '1767user6181',
    None
])
def test_wrong_username_raises_exception(value):
    with pytest.raises(ValidationError):
        Username(value)


@pytest.mark.parametrize('value', [
    'password_123',
    'my-secure_p@ssword78',
    'pass_word_123',
])
def test_correct_password_creation_value_and_str(value):
    obj = Password(value)
    assert str(obj) == value
    assert obj.value == value


@pytest.mark.parametrize('value', [
    '98891787831',  # No only numeric passwords (django specs)
    '',
    ' ',
    'pass',
    None
])
def test_wrong_password_raises_exception(value):
    with pytest.raises(ValidationError):
        Password(value)
