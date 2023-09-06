from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from models.films import FilmResponseModel
from models.persons import Person, PersonSort, PersonPage
from services.persons import PersonService, get_person_service
from services.utils.constants import FILM_NOT_FOUND
from models.base import PaginateQueryParams
from typing import Annotated

router = APIRouter()

PaginateQuery = Annotated[PaginateQueryParams, Depends(PaginateQueryParams)]


@router.get(
    '/persons/search',
    response_model=list[PersonPage],
    description='Метод, выполняет поиск по запросу'
)
async def search_person(
        query: str,
        pagination: PaginateQuery,
        process_id: str = None,
        person_service: PersonService = Depends(get_person_service)
) -> list[PersonPage]:

    persons = await person_service.search_person_with_films(
        query=query,
        page_size=pagination.page_size,
        page_number=pagination.page_number,
        process_id=process_id
    )

    return persons


@router.get(
    '/{person_id}/film',
    response_model=list[FilmResponseModel],
    description="Метод, возвращает список фильмов по персоне"
)
async def films_persons(
        person_id: str, person_service: PersonService = Depends(get_person_service)
) -> FilmResponseModel:
    films = await person_service.get_films_with_person(
        person_id=person_id,
    )
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=FILM_NOT_FOUND)
    return films


@router.get(
    '/',
    response_model=list[Person],
    description="Метод, возвращающий список персон"
)
async def persons_list(
        pagination: PaginateQuery,
        sort_by: PersonSort = PersonSort.down_full_name,
        person_service: PersonService = Depends(get_person_service),
) -> list[Person]:

    persons = await person_service.get_persons_list(
        page_size=pagination.page_size,
        page_number=pagination.page_number,
        sort_by=sort_by,
    )

    return persons


@router.get(
    "/{person_id}",
    response_model=PersonPage,
    description="Метод, возвращающий персону по его id"
)
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)
                         ) -> Person:

    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=FILM_NOT_FOUND)
    return person
