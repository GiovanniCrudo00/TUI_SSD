import csv
import sys
from pathlib import Path
from typing import Tuple

from valid8 import ValidationError

from tui_ssd.menu import *


# TODO: Implement and modify this after the implementation of domain
# TODO: When sorting by something is activated, maintain the sorting until something else is selected (by default no sorting)


class App:
    def __init__(self):
        self.__menu = Menu.Builder(Description('Your Secure Weather TUI'), auto_select=lambda: self.__print_records()) \
            .with_entry(Entry.create('1', 'Add new record', on_selected=lambda: self.__add_record())) \
            .with_entry(Entry.create('2', 'Collect records from sensors', on_selected=lambda: self.__generate_records())) \
            .with_entry(Entry.create('3', 'Sort by humidity', on_selected=lambda: self.__sort_by_humidity())) \
            .with_entry(Entry.create('4', 'Sort by temperature', on_selected=lambda: self.__sort_by_temperature())) \
            .with_entry(Entry.create('5', 'Sort by wind', on_selected=lambda: self.__sort_by_wind())) \
            .with_entry(Entry.create('6', 'Sort by ascending date', on_selected=lambda: self.__sort_by_wind())) \
            .with_entry(Entry.create('0', 'Exit', on_selected=lambda: print('Cya!'), is_exit=True)) \
            .build()
        self.__record_list = RecordList()

    # TODO: Continue to modify from here
    def __print_records(self) -> None:
        print_sep = lambda: print('-' * 100)
        print_sep()
        fmt = '%3s %-10s %-30s %-30s %10s'
        print(fmt % ('#', 'DURATION', 'TITLE', 'AUTHOR', 'GENRE'))
        print_sep()
        for index in range(self.__music_archive.songs()):
            song = self.__music_archive.song(index)
            print(fmt % (index + 1, song.duration.value, song.title.value, song.author.value, song.genre))
        print_sep()

    def __add_record(self) -> None:
        song = Song(*self.__read_song())
        self.__music_archive.add_song(song)
        self.__save()
        print('Song added!')

    def __generate_records(self) -> None:
        def builder(value: str) -> int:
            validate('value', int(value), min_value=0, max_value=self.__music_archive.songs())
            return int(value)

        index = self.__read('Index (0 to cancel)', builder)
        if index == 0:
            print('Cancelled!')
            return
        self.__music_archive.remove_song(index - 1)
        self.__save()
        print('Song removed!')

    def __sort_by_wind(self) -> None:
        self.__music_archive.sort_by_title()
        self.__save()

    def __sort_by_temperature(self) -> None:
        self.__music_archive.sort_by_duration()
        self.__save()

    def __sort_by_humidity(self) -> None:
        rst = self.__music_archive.list_of_authors
        print("LIST OF AUTHORS:")
        print(str(rst))

    def __run(self) -> None:
        try:
            self.__load()
        except ValueError as e:
            print(e)
            print('Continuing with an empty list of songs...')

        self.__menu.run()

    # noinspection PyBroadException
    def run(self) -> None:
        try:
            self.__run()
        except:
            print('Panic error!', file=sys.stderr)

    def __load(self) -> None:
        if not Path(self.__filename).exists():
            return

        with open(self.__filename) as file:
            reader = csv.reader(file, delimiter=self.__delimiter)
            for row in reader:
                validate('row length', row, length=4)
                duration = Duration.parse(row[0])
                title = Title(row[1])
                author = Author(row[2])
                genre = Genre(row[3])
                self.__music_archive.add_song(Song(duration, title, author, genre))

    def __save(self) -> None:
        with open(self.__filename, 'w') as file:
            writer = csv.writer(file, delimiter=self.__delimiter, lineterminator='\n')
            for index in range(self.__music_archive.songs()):
                song = self.__music_archive.song(index)
                writer.writerow([song.duration, song.title, song.author, song.genre])

    @staticmethod
    def __read(prompt: str, builder: Callable) -> Any:
        while True:
            try:
                line = input(f'{prompt}: ')
                res = builder(line.strip())
                return res
            except (TypeError, ValueError, ValidationError) as e:
                print(e)

    def __read_song(self) -> Tuple[Duration, Title, Author, Genre]:
        duration = self.__read('Duration', Duration.parse)
        title = self.__read('Title', Title)
        author = self.__read('Author', Author)
        genre = self.__read('Genre', Genre)
        return duration, title, author, genre


def main(name: str):
    if name == '__main__':
        App().run()


main(__name__)
