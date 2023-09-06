from enum import Enum

from models.base import BaseOrjsonModel


class FilmResponseModel(BaseOrjsonModel):
    id: str
    title: str
    imdb_rating: float | None = None


class FilmDetailResponseModel(FilmResponseModel):
    genres: list[dict] | None = None
    description: str | None = None
    directors: list[dict] | None = None
    actors_names: list[str] | None = None
    writers_names: list[str] | None = None
    actors: list[dict] | None = None
    writers: list[dict] | None = None


class FilmSort(str, Enum):
    up_imdb_rating = "imdb_rating"
    down_imdb_rating = '-imdb_rating'
