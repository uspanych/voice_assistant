from http import HTTPStatus

import aiohttp
import pytest
from functional.settings import test_settings

pytestmark = pytest.mark.asyncio


async def test_get_all_persons(es_write_data, client_session):
    url = test_settings.service_url + '/api/v1/persons'

    async with client_session.get(url) as response:
        body = await response.json()

        assert response.status == HTTPStatus.OK
        assert len(body) == 6
        assert body[0]['full_name'] == "Biba"


async def test_get_all_persons_first_page(es_write_data, client_session):
    url = test_settings.service_url + '/api/v1/persons'

    async with client_session.get(url, params=dict(page_number=1, page_size=1)) as response:
        body = await response.json()

        assert response.status == HTTPStatus.OK
        assert len(body) == 1
        assert body[0]['full_name'] == "Biba"


async def test_get_all_persons_desc(es_write_data, client_session):
    url = test_settings.service_url + '/api/v1/persons'

    async with client_session.get(url, params=dict(sort_by="full_name")) as response:
        body = await response.json()

        assert response.status == HTTPStatus.OK
        assert len(body) == 6
        assert body[0]['full_name'] == "Stive Jobs"


@pytest.mark.parametrize(
    'id',
    [
        222,
        111,
        333,
        123,
        444,
        112,
    ]
)
async def test_get_persons_by_id(es_write_data, client_session, id):
    url = test_settings.service_url + f'/api/v1/persons/{id}'

    async with client_session.get(url) as response:
        body = await response.json()

        assert response.status == HTTPStatus.OK
        assert str(body['id']) == str(id)


@pytest.mark.parametrize(
    'id',
    [
        222,
        111,
        333,
        123,
        444,
        112,
    ]
)
async def test_get_films_of_person_by_id(es_write_data, client_session, id):
    url = test_settings.service_url + f'/api/v1/persons/{id}/film'

    async with client_session.get(url) as response:
        body = await response.json()

        assert response.status == HTTPStatus.OK
        assert len(body) == 10


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'query': 'Kelvin Clein'},
            {'status': HTTPStatus.OK, 'length': 1}
        ),
        (
            {'query': 'Mashed potato'},
            {'status': HTTPStatus.OK, 'length': 0}
        ),
    ]
)
async def test_person_search(es_write_data, client_session, query_data, expected_answer):
    url = test_settings.service_url + '/api/v1/persons/persons/search'

    async with client_session.get(url, params=query_data) as response:
        body = await response.json()

        assert len(body) == expected_answer['length']
        assert response.status == expected_answer['status']


@pytest.mark.parametrize(
    'parameter',
    [
        -1,
        "string",
        100000000000000000000,
        "@^$"
    ]
)
async def test_get_all_persons_with_bad_page_number(es_write_data, client_session, p):
    url = test_settings.service_url + '/api/v1/persons'

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
async def test_get_all_persons_with_bad_page_size(es_write_data, client_session, p):
    url = test_settings.service_url + '/api/v1/persons'

    async with client_session.get(url, params=dict(page_size=p)) as response:
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
