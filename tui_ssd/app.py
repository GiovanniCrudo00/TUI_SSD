import csv
import sys
from pathlib import Path
from typing import Tuple

from valid8 import ValidationError

from tui_ssd.menu import *


class App:
    __filename = Path(__file__).parent.parent / 'default.csv'
    __delimiter = '\t'
    __restricted = False
    __restricted_author = Author("NONE")

    def __init__(self):
        self.__menu = Menu.Builder(Description('Spotify Music Archive'), auto_select=lambda: self.__check_restricted()) \
            .with_entry(Entry.create('1', 'Add song', on_selected=lambda: self.__add_song())) \
            .with_entry(Entry.create('2', 'Remove song by index', on_selected=lambda: self.__remove_song())) \
            .with_entry(Entry.create('3', 'Sort by title', on_selected=lambda: self.__sort_by_title())) \
            .with_entry(Entry.create('4', 'Sort by duration', on_selected=lambda: self.__sort_by_duration())) \
            .with_entry(Entry.create('5', 'Extract list of authors', on_selected=lambda: self.__list_of_authors())) \
            .with_entry(Entry.create('6', 'Restrict view to song of a given author', on_selected=lambda: self.__set_restricted_author())) \
            .with_entry(Entry.create('7', 'Remove restriction of author', on_selected=lambda: self.__remove_restriction())) \
            .with_entry(Entry.create('0', 'Exit', on_selected=lambda: print('Bye!'), is_exit=True)) \
            .build()
        self.__music_archive = MusicArchive()

    def __check_restricted(self) -> None:
        if not self.__restricted:
            self.__print_songs()
        else:
            self.__print_songs_restricted()

    def __remove_restriction(self) -> None:
        self.__restricted_author = Author("NONE")
        self.__restricted = False
        print("RESTRICTION REMOVED!")

    def __set_restricted_author(self) -> None:
        auth = self.__read("Author", Author)
        self.__restricted_author = auth
        self.__restricted = True

    def __print_songs_restricted(self) -> None:
        print_sep = lambda: print('-' * 100)
        print_sep()
        print(f"SONGS RESTRICTED TO {self.__restricted_author}")
        fmt = '%3s %-10s %-30s %-30s %10s'
        print(fmt % ('#', 'DURATION', 'TITLE', 'AUTHOR', 'GENRE'))
        print_sep()
        restricted_songs = self.__music_archive.filter_by_author(self.__restricted_author)
        for index in range(len(restricted_songs)):
            song = restricted_songs[index]
            print(fmt % (index + 1, song.duration.value, song.title.value, song.author.value, song.genre))
        print_sep()

    def __print_songs(self) -> None:
        print_sep = lambda: print('-' * 100)
        print_sep()
        fmt = '%3s %-10s %-30s %-30s %10s'
        print(fmt % ('#', 'DURATION', 'TITLE', 'AUTHOR', 'GENRE'))
        print_sep()
        for index in range(self.__music_archive.songs()):
            song = self.__music_archive.song(index)
            print(fmt % (index + 1, song.duration.value, song.title.value, song.author.value, song.genre))
        print_sep()

    def __add_song(self) -> None:
        song = Song(*self.__read_song())
        self.__music_archive.add_song(song)
        self.__save()
        print('Song added!')

    def __remove_song(self) -> None:
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

    def __sort_by_title(self) -> None:
        self.__music_archive.sort_by_title()
        self.__save()

    def __sort_by_duration(self) -> None:
        self.__music_archive.sort_by_duration()
        self.__save()

    def __list_of_authors(self) -> None:
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
