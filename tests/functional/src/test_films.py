from http import HTTPStatus


import pytest
from functional.settings import test_settings

pytestmark = pytest.mark.asyncio


async def test_get_all_persons(es_write_data, client_session):
    url = test_settings.service_url + '/api/v1/films'

    async with client_session.get(url) as response:
        body = await response.json()

        assert response.status == HTTPStatus.OK
        assert len(body) == 50
        assert body[0]['title'] == "The Star"


async def test_get_all_persons_first_page(es_write_data, client_session):
    url = test_settings.service_url + '/api/v1/films'

    async with client_session.get(url, params=dict(page_number=1, page_size=1)) as response:
        body = await response.json()

        assert response.status == HTTPStatus.OK
        assert len(body) == 1
        assert body[0]['title'] == "The Star"


@pytest.mark.parametrize(
    'id',
    [
        "1f90980e-e7c9-4fac-a1e4-f34409daeff2",
    ]
)
async def test_get_film_by_id(es_write_data, client_session, id):
    url = test_settings.service_url + f'/api/v1/films/{id}'

    async with client_session.get(url) as response:
        body = await response.json()

        assert response.status == HTTPStatus.OK
        assert body["id"] == id


@pytest.mark.parametrize(
    'parameter',
    [
        -1,
        "string",
        100000000000000000000,
        "@^$"
    ]
)
async def test_get_films_with_bad_page_number(es_write_data, client_session, p):
    url = test_settings.service_url + f'/api/v1/films/'

    async with client_session.get(url, params=dict(page_number=p)) as response:
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    'parameter',
    [
        -1,
        "string",
        100000000000000000000,
        "@^$"
    ]
)
async def test_get_films_with_bad_page_size(es_write_data, client_session, p):
    url = test_settings.service_url + f'/api/v1/films/'

    async with client_session.get(url, params=dict(page_size=p)) as response:
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
