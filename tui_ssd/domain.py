from dataclasses import dataclass, InitVar, field
from typing import Any, List, Optional
from valid8 import validate
from typeguard import typechecked
from validation.regex import pattern
import re
from types import MappingProxyType
from datetime import datetime


@typechecked
@dataclass(frozen=True)
class Id:
    value: int

    def __post_init__(self):
        validate('value', self.value, min_value=1, max_value=99999, instance_of=int)


@typechecked
@dataclass(frozen=True, order=True)
class Temperature:
    value: int

    def __post_init__(self):
        validate('value', self.value, min_value=-50, max_value=50, instance_of=int)

    def __str__(self):
        return str(self.value)


@typechecked
@dataclass(frozen=True, order=True)
class Humidity:
    value: int

    def __post_init__(self):
        validate('value', self.value, min_value=0, max_value=100, instance_of=int)

    def __str__(self):
        return str(self.value)


@typechecked
@dataclass(frozen=True, order=True)
class Wind:
    value: int

    def __post_init__(self):
        validate('value', self.value, min_value=0, max_value=200, instance_of=int)

    def __str__(self):
        return str(self.value)


@typechecked
@dataclass(frozen=True)
class Condition:
    """
        Since we take the value as a string ['1' to '4'] and then we need to cast it into a static string value
        [SUNNY, CLOUDY, RAINY, FLURRY] we need a builder and a parse method to cast it.
    """
    __condition_value: int
    create_key: InitVar[Any] = field(default="it must be the __create_key")
    __create_key = object()

    def __post_init__(self, create_key):
        validate('condition_value', self.__condition_value, min_value=1, max_value=4, instance_of=int)
        validate('create_key', create_key, equals=self.__create_key)

    @property
    def values_dictionary(self) -> MappingProxyType:
        """
            MappingProxyType is a class of the standard python module types.
            It allows us to have an immutable copy of the mapped object (such as a dictionary)
            not allowing any direct modification of the view
        """
        return MappingProxyType({1: 'SUNNY', 2: 'CLOUDY', 3: 'RAINY', 4: 'FLURRY'})

    def __str__(self):
        return self.values_dictionary[self.__condition_value]

    @property
    def value(self) -> str:
        return self.values_dictionary[self.__condition_value]

    @property
    def enum_value(self) -> str:
        return str(self.__condition_value)

    @staticmethod
    def create(value: str) -> 'Condition':
        validate('value', value, min_len=1, max_len=1, instance_of=str, custom=pattern(r'[0-4]{1}'))
        integer_value = int(value)
        validate('integer_value', integer_value, min_value=1, max_value=4, instance_of=int)
        return Condition(integer_value, Condition.__create_key)


@typechecked
@dataclass(frozen=True, order=True)
class RecordDate:
    __date_value: datetime
    __create_key = object()
    __MIN_DATA = datetime(2000, 1, 1, 0, 0)
    __MAX_DATA = datetime(2999, 12, 31, 23, 59)
    create_key: InitVar[Any] = field(default="it must be the __create_key")

    def __post_init__(self, create_key):
        validate('condition_value', self.__date_value, min_value=self.__MIN_DATA, max_value=self.__MAX_DATA)
        validate('create_key', create_key, equals=self.__create_key)

    @property
    def value(self) -> str:
        return str(f"{self.day:02}/{self.month:02}/{self.year:04} at {self.hour:02}:{self.minute:02}")

    @property
    def db_date(self) -> str:
        return str(f"{self.year:04}-{self.month:02}-{self.day:02}T{self.hour:02}:{self.minute:02}")

    def __str__(self):
        return str(f"{self.day:02}/{self.month:02}/{self.year:04} at {self.hour:02}:{self.minute:02}")

    @property
    def year(self) -> int:
        return self.__date_value.year

    @property
    def month(self) -> int:
        return self.__date_value.month

    @property
    def day(self) -> int:
        return self.__date_value.day

    @property
    def hour(self) -> int:
        return self.__date_value.hour

    @property
    def minute(self) -> int:
        return self.__date_value.minute

    @staticmethod
    def create(value: str) -> 'RecordDate':
        """
            I expect from input a date like "09/09/2000 15:29:33"
        """
        __tmp_date, __tmp_time = value.split(' ')
        __day, __month, __year = __tmp_date.split('/')
        __hour, __minute = __tmp_time.split(':')

        __created_date = datetime(int(__year), int(__month), int(__day), int(__hour), int(__minute))

        return RecordDate(__created_date, RecordDate.__create_key)

    @staticmethod
    def parse(value: str) -> 'RecordDate':
        # The date in the database is in the format 2023-12-08T12:20:00+01:00

        __create_date = datetime.strptime(value.split('+')[0], '%Y-%m-%dT%H:%M:%S')
        return RecordDate(__create_date, RecordDate.__create_key)


@typechecked
@dataclass(frozen=True, order=True)
class Record:
    temperature: Temperature
    humidity: Humidity
    wind: Wind
    condition: Condition
    record_date: RecordDate
    id: Optional[Id] = None


@typechecked
@dataclass(frozen=True)
class RecordList:
    __records: List[Record] = field(default_factory=list, init=False)

    @property
    def records(self) -> int:  # Return the  number of records in the list (Utility method)
        return len(self.__records)

    def record(self, index: int) -> Record:  # Given an index return a record
        validate("record_index", index, min_value=0, max_value=self.records - 1)
        return self.__records[index]

    def add_record(self, rec: Record) -> None:
        self.__records.append(rec)

    def dump_list(self) -> None:
        self.__records.clear()

    def sort_by_temperature(self) -> None:
        self.__records.sort(key=lambda x: x.temperature)

    def sort_by_humidity(self) -> None:
        self.__records.sort(key=lambda x: x.humidity)

    def sort_by_wind(self) -> None:
        self.__records.sort(key=lambda x: x.wind)

    def sort_by_ascending_date(self) -> None:
        self.__records.sort(key=lambda x: x.record_date)
