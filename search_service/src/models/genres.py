from enum import Enum
from models.base import BaseOrjsonModel


class GenreResponseModel(BaseOrjsonModel):
    id: str
    name: str


class GenreDetailResponseModel(GenreResponseModel):
    description: str | None


class GenreSort(str, Enum):
    up_name = "name"
    down_name = '-name'
