from http import HTTPStatus

import pytest
import aiohttp
from functional.settings import test_settings

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'query': 'The Star'},
            {'status': HTTPStatus.OK, 'length': 50}
        ),
        (
            {'query': 'Mashed potato'},
            {'status': HTTPStatus.OK, 'length': 0}
        ),
    ]
)
async def test_search(es_write_data, client_session, query_data, expected_answer):
    url = test_settings.service_url + '/api/v1/films/search'

    async with client_session.get(url, params=query_data) as response:
        body = await response.json()

        assert len(body) == expected_answer['length']
        assert response.status == expected_answer['status']
