from dataclasses import dataclass, InitVar, field
from typing import Any, List
from valid8 import validate
from typeguard import typechecked
from validation.regex import pattern
import re
from types import MappingProxyType
from datetime import datetime

"""
DOMAIN PRIMITIVES
    Temperature: int                            Class:[DONE] Tests:[DONE]
    Humidity: int                               Class:[DONE] Tests:[DONE]
    Wind: int                                   Class:[DONE] Tests:[DONE]
    Condition: Enum from 1 to 4                 Class:[DONE] Tests:[DONE]
    Date: datetime.datetime python class        Class:[] Tests:[]
    
AGGREGATE
    Record                                      Class:[] Tests:[]
    SecureWeather                               Class:[] Tests:[]
"""


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

    @staticmethod
    def create(value: str) -> 'Condition':
        validate('value', value, min_len=1, max_len=1, instance_of=str, custom=pattern(r'[0-4]{1}'))
        integer_value = int(value)
        validate('integer_value', integer_value, min_value=1, max_value=4, instance_of=int)
        return Condition(integer_value, Condition.__create_key)


@typechecked
@dataclass(frozen=True)
class RecordDate:
    __date_value: datetime
    create_key: InitVar[Any] = field(default="it must be the __create_key")
    __create_key = object()
    __MIN_DATA = datetime(2000, 1, 1, 0, 0, 0)
    __MAX_DATA = datetime(2999, 12, 31, 23, 59, 59)

    def __post_init__(self, create_key):
        validate('condition_value', self.__date_value, min_value=self.__MIN_DATA, max_value=self.__MAX_DATA,
                 instance_of=datetime)
        validate('create_key', create_key, equals=self.__create_key)

    @property
    def value(self) -> str:  # TODO: Complete this
        return str(f"{self.day:02}/{self.month:02}/{self.year:04}@{self.hour:02}:{self.minute:02}:{self.second:02}")

    def __str__(self):  # TODO: Complete this
        return str(f"{self.day:02}/{self.month:02}/{self.year:04}@{self.hour:02}:{self.minute:02}:{self.second:02}")

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

    @property
    def second(self) -> int:
        return self.__date_value.second

    @staticmethod
    def create(value: str) -> 'RecordDate':
        # "2023-12-08T23:54:00+01:00"
        """
            I expect from input a date like "09/09/2000 15:29:33"
        """
        __tmp_date, __tmp_time = value.split(' ')
        __day, __month, __year = __tmp_date.split('/')
        __hour, __minute, __second = __tmp_time.split(':')

        __created_date = datetime(int(__year), int(__month), int(__day), int(__hour), int(__minute), int(__second))

        return RecordDate(__created_date, RecordDate.__create_key)

