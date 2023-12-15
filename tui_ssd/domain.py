from dataclasses import dataclass, InitVar, field
from typing import Any, List
from valid8 import validate
from typeguard import typechecked
from validation.regex import pattern
import re
from types import MappingProxyType


"""
DOMAIN PRIMITIVES
    Temperature: int                            Class:[DONE] Tests:[DONE]
    Humidity: int                               Class:[DONE] Tests:[DONE]
    Wind: int                                   Class:[DONE] Tests:[DONE]
    Condition: Enum from 1 to 4                 Class:[DONE-REVIEW] Tests:[DONE-REVIEW]
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
    def values_dictionary(self) -> MappingProxyType:  # TODO: Parlare cu gabriele "u capu progettu"
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
@dataclass(frozen=True, order=True)
class RecordDate:
    ...

