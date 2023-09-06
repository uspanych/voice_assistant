from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from models.base import PaginateQueryParams
from models.films import FilmDetailResponseModel, FilmResponseModel, FilmSort
from services.films import FilmService, get_film_service
from services.utils.constants import FILM_NOT_FOUND

router = APIRouter()


PaginateQuery = Annotated[PaginateQueryParams, Depends(PaginateQueryParams)]


@router.get(
    '/search',
    response_model=list[FilmResponseModel],
    description="Метод, возвращающий список найденных фильмов",
)
async def films_query_list(
        query: str,
        pagination: PaginateQuery,
        process_id: str = None,
        film_service: FilmService = Depends(get_film_service)
) -> list[FilmResponseModel]:

    films = await film_service.search_film_by_query(
        page_size=pagination.page_size,
        page_number=pagination.page_number,
        query=query,
        process_id=process_id
    )

    return films


@router.get(
    '/{film_id}',
    response_model=FilmDetailResponseModel,
    description="Метод, возвращающий фильм по его id"
)
async def film_details(
    film_id: str,
    film_service: FilmService = Depends(get_film_service)
) -> FilmDetailResponseModel:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=FILM_NOT_FOUND)
    return film


@router.get(
    '/',
    response_model=list[FilmResponseModel],
    description="Метод, возвращающий список всех фильмов"
)
async def films_list(
        pagination: PaginateQuery,
        genre: str | None = None,
        actor: str | None = None,
        writer: str | None = None,
        director: str | None = None,
        sort_by: FilmSort = FilmSort.down_imdb_rating,
        film_service: FilmService = Depends(get_film_service),
) -> list[FilmResponseModel]:

    films = await film_service.get_film_list(
        page_size=pagination.page_size,
        page_number=pagination.page_number,
        sort_by=sort_by,
        genre=genre,
        actor=actor,
        writer=writer,
        director=director,
    )

    return films
