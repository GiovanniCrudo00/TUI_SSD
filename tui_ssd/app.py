import csv
import sys
from typing import Tuple

from valid8 import ValidationError

from tui_ssd.menu import *
from tui_ssd.domain import *
import requests
import json


class App:
    def __init__(self):
        self.__menu = Menu.Builder(Description('Your Secure Weather TUI'), auto_select=lambda: self.__connect()) \
            .with_entry(Entry.create('1', 'Add new record', on_selected=lambda: self.__add_record())) \
            .with_entry(Entry.create('2', 'Remove record', on_selected=lambda: self.__remove_record())) \
            .with_entry(Entry.create('3', 'Collect records from sensors', on_selected=lambda: self.__generate_records())) \
            .with_entry(Entry.create('4', 'Sort by temperature', on_selected=lambda: self.__sort_by_temperature())) \
            .with_entry(Entry.create('5', 'Sort by humidity', on_selected=lambda: self.__sort_by_humidity())) \
            .with_entry(Entry.create('6', 'Sort by wind', on_selected=lambda: self.__sort_by_wind())) \
            .with_entry(Entry.create('7', 'Sort by ascending date', on_selected=lambda: self.__sort_by_wind())) \
            .with_entry(Entry.create('0', 'Exit', on_selected=lambda: self.__logout(), is_exit=True)) \
            .build()
        self.__record_list = RecordList()
        self.__token = None
        self.__LOGIN_URL = "http://localhost:8000/api/v1/auth/login/"
        self.__RECORDS_URL = "http://localhost:8000/api/v1/records/"
        self.__LOGOUT_URL = "http://localhost:8000/api/v1/auth/logout/"

    def __connect(self) -> None:  # TODO: Implement connection to database
        # Do something to connect maybe username and password and set the token, then if everything is good show the menu loop
        # If everything is fine print records
        """
            Since this method is called everytime the records are printed in loop,
            avoid reconnecting if a token is already set
        """
        # Temporary code down
        credentials = {'username': 'normal_user', 'email': '', 'password': 'password_123'}
        req = requests.post(self.__LOGIN_URL, json=credentials)
        self.__token = req.json().get('key')
        print(self.__token)  # TODO: Remove this, used for debug

        self.__print_records()

    def __logout(self) -> None:
        req = requests.post(self.__LOGOUT_URL, headers={'Authorization': f'Token {self.__token}'})
        self.__token = None
        print("Cya!")

    def __print_records(self) -> None:
        # Here we make the request for the records
        __records = requests.get(self.__RECORDS_URL, headers={'Authorization': f'Token {self.__token}'})
        __json_data = __records.json()
        # Here we have the data
        for i in __json_data:
            # TODO: Create an object and use the method __add_record to add it to the list
            print(i['condition'])
            print(i['temperature'])
            print(i['humidity'])
            print(i['wind'])
            # The date is in the format 2023-12-08T12:20:00+01:00
            # TODO: Implement method parse_date to parse the data to our TUI format 29/02/2000 10:00:45
            print(i['date'])

        # Here we print it
        print_sep = lambda: print('-' * 130)
        print_sep()
        fmt = '%-10s %-30s %-20s %-20s %-20s %-30s'
        print(fmt % ('#', 'CONDITION', 'TEMPERATURE', 'HUMIDITY', 'WIND', 'DATE'))
        print_sep()
        for index in range(self.__record_list.records):
            rec = self.__record_list.record(index)
            print(fmt % (index + 1, rec.condition.value, rec.temperature.value, rec.humidity.value,
                         rec.wind.value, rec.record_date.value))
        print_sep()

    def __add_record(self) -> None:  # TODO: modify and adjust
        song = Song(*self.__read_song())
        self.__music_archive.add_song(song)
        self.__save()
        print('Song added!')

    def __remove_record(self) -> None:  # TODO: modify and adjust
        def builder(value: str) -> int:
            validate('value', int(value), min_value=0, max_value=self.__record_list.records)
            return int(value)

        index = self.__read('Index (0 to cancel)', builder)
        if index == 0:
            print('Cancelled!')
            return
        self.__music_archive.remove_song(index - 1)
        self.__save()
        print('Song removed!')

    def generate_records(self) -> None:  # TODO: implement method to generate data from sensors
        ...

    def __sort_by_temperature(self) -> None:
        self.__record_list.sort_by_temperature()

    def __sort_by_humidity(self) -> None:
        self.__record_list.sort_by_humidity()

    def __sort_by_wind(self) -> None:
        self.__record_list.sort_by_wind()

    def __sort_by_ascending_date(self) -> None:
        self.__record_list.sort_by_ascending_date()

    def __save(self) -> None:  # TODO: Implement method to save to database
        ...

    def __load(self) -> None:  # TODO: Implement method to fetch to database
        print("No records found")

    def __run(self) -> None:
        try:
            self.__load()
        except ValueError as e:
            print(e)
            print("Error when connecting to backend...")

        self.__menu.run()
    # noinspection PyBroadException
    def run(self) -> None:
        # try:
        #     self.__run()
        # except:
        #     print('Panic error!', file=sys.stderr)
        self.__run()  # TODO: Debug purpose remove when in production

    @staticmethod
    def __read(prompt: str, builder: Callable) -> Any:
        while True:
            try:
                line = input(f'{prompt}: ')
                res = builder(line.strip())
                return res
            except (TypeError, ValueError, ValidationError) as e:
                print(e)

    def __read_record(self) -> Tuple[Temperature, Humidity, Wind, Condition, RecordDate]:
        temperature = self.__read('Temperature (-50, +50)', Temperature)
        humidity = self.__read('Humidity (0, 100)', Humidity)
        wind = self.__read('Wind (0, 200)', Wind)
        condition = self.__read('Condition (1,2,3,4)', Condition.create)
        date = self.__read('Date (dd/mm/yyyy HH:MM:SS)', RecordDate.create)
        return temperature, humidity, wind, condition, date


def main(name: str):
    if name == '__main__':
        App().run()


main(__name__)
