from enum import Enum
from models.base import BaseOrjsonModel


class Person(BaseOrjsonModel):
    id: str
    full_name: str


class PersonPage(Person):
    films: list[dict]


class PersonSort(str, Enum):
    up_full_name = "full_name"
    down_full_name = '-full_name'
