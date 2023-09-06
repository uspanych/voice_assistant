from http import HTTPStatus

import pytest
import aiohttp
from functional.settings import test_settings

pytestmark = pytest.mark.asyncio


async def test_get_all_genres(es_write_data, client_session):
    url = test_settings.service_url + '/api/v1/genres'

    async with client_session.get(url) as response:
        body = await response.json()

        assert response.status == HTTPStatus.OK
        assert len(body) == 2
        assert body[0]['name'] == "Action"


async def test_get_all_genres_first_page(es_write_data, client_session):
    url = test_settings.service_url + '/api/v1/genres'

    async with client_session.get(url, params=dict(page_number=1, page_size=1)) as response:
        body = await response.json()

        assert response.status == HTTPStatus.OK
        assert len(body) == 1
        assert body[0]['name'] == "Action"


async def test_get_all_genres_desc(es_write_data, client_session):
    url = test_settings.service_url + '/api/v1/genres'

    async with client_session.get(url, params=dict(sort_by="name")) as response:
        body = await response.json()

        assert response.status == HTTPStatus.OK
        assert len(body) == 2
        assert body[0]['name'] == "Sci-Fi"


@pytest.mark.parametrize(
    'id',
    [
        566,
        679,
    ]
)
async def test_get_genre_by_id(es_write_data, client_session, id):
    url = test_settings.service_url + f'/api/v1/genres/{id}'

    async with client_session.get(url) as response:
        body = await response.json()

        assert response.status == HTTPStatus.OK
        assert str(body['id']) == str(id)


@pytest.mark.parametrize(
    'parameter',
    [
        -1,
        "string",
        100000000000000000000,
        "@^$"
    ]
)
async def test_get_all_genres_with_bad_page_number(es_write_data, client_session, p):
    url = test_settings.service_url + '/api/v1/genres'

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
async def test_get_all_genres_with_bad_page_size(es_write_data, client_session, p):
    url = test_settings.service_url + '/api/v1/genres'

    async with client_session.get(url, params=dict(page_size=p)) as response:
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
