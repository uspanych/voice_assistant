from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from models.base import PaginateQueryParams
from models.genres import (GenreDetailResponseModel, GenreResponseModel,
                           GenreSort)
from services.genres import GenreService, get_genre_service
from services.utils.constants import FILM_NOT_FOUND

router = APIRouter()


PaginateQuery = Annotated[PaginateQueryParams, Depends(PaginateQueryParams)]


@router.get(
    "/{genre_id}",
    response_model=GenreDetailResponseModel,
    description="Метод, возвращающий жанр по его id"
)
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)
                        ) -> GenreDetailResponseModel:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=FILM_NOT_FOUND)
    return genre


@router.get(
    '/',
    response_model=list[GenreResponseModel],
    description="Метод, возвращающий список жанров"
)
async def films_list(
    pagination: PaginateQuery,
    sort_by: GenreSort = GenreSort.down_name,
    genre_service: GenreService = Depends(get_genre_service),
) -> list[GenreResponseModel]:

    films = await genre_service.get_genres_list(
        page_size=pagination.page_size,
        page_number=pagination.page_number,
        sort_by=sort_by,
    )

    return films
