import csv
import sys
from typing import Tuple
from valid8 import ValidationError
from tui_ssd.menu import *
from tui_ssd.domain import *
import requests
import json
from random import randint, choice
import getpass
from os import system


class App:
    def __init__(self):
        self.__menu = Menu.Builder(Description('Your Secure Weather TUI'), auto_select=lambda: self.__connect()) \
            .with_entry(Entry.create('1', 'Add new record', on_selected=lambda: self.__add_record())) \
            .with_entry(Entry.create('2', 'Remove record', on_selected=lambda: self.__remove_record())) \
            .with_entry(Entry.create('3', 'Collect records from sensors', on_selected=lambda: self.__generate_records())) \
            .with_entry(Entry.create('4', 'Sort by temperature', on_selected=lambda: self.__sort_by_temperature())) \
            .with_entry(Entry.create('5', 'Sort by humidity', on_selected=lambda: self.__sort_by_humidity())) \
            .with_entry(Entry.create('6', 'Sort by wind', on_selected=lambda: self.__sort_by_wind())) \
            .with_entry(Entry.create('7', 'Sort by ascending date', on_selected=lambda: self.__sort_by_ascending_date())) \
            .with_entry(Entry.create('8', 'Update records list', on_selected=lambda: self.__load())) \
            .with_entry(Entry.create('0', 'Exit', on_selected=lambda: self.__logout(), is_exit=True)) \
            .build()
        self.__record_list = RecordList()
        self.__token = None
        self.__LOGIN_URL = "http://localhost:8000/api/v1/auth/login/"
        self.__RECORDS_URL = "http://localhost:8000/api/v1/records/"
        self.__LOGOUT_URL = "http://localhost:8000/api/v1/auth/logout/"

    def __connect(self) -> None:
        if self.__token is None:
            print("Hello user, please enter your credentials below.")
            while self.__token is None:
                username = input("Username: ")
                password = getpass.getpass("Password: ")

                user = Username(username)
                passw = Password(password)

                credentials = {'username': user.value, 'email': '', 'password': passw.value}
                req = requests.post(self.__LOGIN_URL, json=credentials)
                if req.status_code != 200:
                    print('Unable to login, please check your credentials...')
                else:
                    self.__token = req.json().get('key')
                    # If login is good load data and then print
                    if self.__record_list.records == 0:
                        self.__load()
                    self.__print_records()
        else:
            self.__print_records()

    def __logout(self) -> None:
        req = requests.post(self.__LOGOUT_URL, headers={'Authorization': f'Token {self.__token}'})
        self.__token = None
        print("Cya!")

    def __print_records(self) -> None:
        system('clear')
        print_sep = lambda: print('-' * 130)
        print_sep()
        fmt = '%-10s %-30s %-20s %-20s %-20s %-30s'
        print(fmt % ('#', 'CONDITION', 'TEMPERATURE (˚C)', 'HUMIDITY (%)', 'WIND (Km/h)', 'DATE'))
        print_sep()
        for index in range(self.__record_list.records):
            rec = self.__record_list.record(index)
            print(fmt % (index + 1, rec.condition.value, rec.temperature.value, rec.humidity.value,
                         rec.wind.value, rec.record_date.value))
        print_sep()

    def __add_record(self) -> None:
        record = Record(*self.__read_record())
        self.__save(record)
        self.__load()
        print('Record added!')

    def __remove_record(self) -> None:
        def builder(value: str) -> int:
            validate('value', int(value), min_value=0, max_value=self.__record_list.records)
            return int(value)

        index = self.__read__str('Index (0 to cancel)', builder)
        if index == 0:
            print('Cancelled!')
            return
        rec = self.__record_list.record(index - 1)
        self.__remove_from_db(rec)

    def __generate_records(self) -> None:
        for i in range(24):
            __today_date = datetime.now()
            __date = RecordDate.create(f"{__today_date.day}/{__today_date.month}/{__today_date.year} {i:02}:00")
            __temp = Temperature(randint(-50, 50))
            __hum = Humidity(randint(0, 100))
            __wind = Wind(randint(0, 200))
            __cond = Condition.create(choice(['1', '2', '3', '4']))

            __rec = Record(__temp, __hum, __wind, __cond, __date)
            self.__save(__rec)
        print('Data collected!')
        self.__load()

    def __sort_by_temperature(self) -> None:
        self.__record_list.sort_by_temperature()

    def __sort_by_humidity(self) -> None:
        self.__record_list.sort_by_humidity()

    def __sort_by_wind(self) -> None:
        self.__record_list.sort_by_wind()

    def __sort_by_ascending_date(self) -> None:
        self.__record_list.sort_by_ascending_date()

    def __save(self, rec: Record) -> None:
        __json_data = {'condition': rec.condition.enum_value, 'humidity': rec.humidity.value,
                       'temperature': rec.temperature.value, 'wind': rec.wind.value, 'date': rec.record_date.db_date}
        req = requests.post(self.__RECORDS_URL, headers={'Authorization': f'Token {self.__token}'}, data=__json_data)
        if req.status_code == 201 or req.status_code == 200:
            print('Record saved!')
        elif req.status_code == 405:
            print("Missing permissions to perform this action")
        else:
            print("Error when updating new data...")

    def __load(self) -> None:
        self.__record_list.dump_list()  # Clear old data

        # Fetch data from DB
        __records = requests.get(self.__RECORDS_URL, headers={'Authorization': f'Token {self.__token}'})
        __json_data = __records.json()
        # Here we have the data
        for i in __json_data:
            rec = Record(Temperature(i['temperature']), Humidity(i['humidity']), Wind(i['wind']),
                         Condition.create(i['condition']), RecordDate.parse(i['date']), id=Id(i['id']))

            self.__record_list.add_record(rec)

    def __remove_from_db(self, rec: Record) -> None:
        req = requests.delete(url=f"{self.__RECORDS_URL}{rec.id.value}/", headers={'Authorization': f'Token {self.__token}'})
        if req.status_code == 204 or req.status_code == 200:
            print('Record removed!')
            self.__load()
        elif req.status_code == 405:
            print("Missing permissions to perform this action")
        else:
            print("Error when updating new data...")

    def __run(self) -> None:
        self.__menu.run()

    # noinspection PyBroadException
    def run(self) -> None:
        """
        try:
            self.__run()
        except requests.exceptions.ConnectionError:
            print("Error while connecting, shutting down...")
        except:
            print('Panic error!', file=sys.stderr)
        """

        self.__run()  # TODO: Debug purpose remove when in production LAST THING TO REMOVE

    @staticmethod
    def __read__str(prompt: str, builder: Callable) -> Any:
        while True:
            try:
                line = input(f'{prompt}: ')
                res = builder(line.strip())
                return res
            except (TypeError, ValueError, ValidationError) as e:
                print(e)

    @staticmethod
    def __read_integer(prompt: str, builder: Callable) -> Any:
        while True:
            try:
                line = input(f'{prompt}: ')
                val = line.strip()
                res = builder(int(val))
                return res
            except (TypeError, ValueError, ValidationError) as e:
                print(e)

    def __read_record(self) -> Tuple[Temperature, Humidity, Wind, Condition, RecordDate]:
        temperature = self.__read_integer('Temperature (-50, +50)', Temperature)
        humidity = self.__read_integer('Humidity (0, 100)', Humidity)
        wind = self.__read_integer('Wind (0, 200)', Wind)
        condition = self.__read__str('Condition (1,2,3,4)', Condition.create)
        date = self.__read__str('Date (dd/mm/yyyy HH:MM)', RecordDate.create)
        return temperature, humidity, wind, condition, date


def main(name: str):
    if name == '__main__':
        App().run()


main(__name__)
