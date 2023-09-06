from base import BaseOrjsonModel


class Person(BaseOrjsonModel):
    id: str
    full_name: str


class PersonPage(Person):
    films: list[dict]
