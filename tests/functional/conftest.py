from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from functional.settings import test_settings
import pytest_asyncio
import aiohttp
import asyncio
from redis.asyncio import Redis
from functional.testdata.schemes import GENRES_SCHEMA, MOVIES_SCHEMA, PERSONS_SCHEMA
from functional.testdata.es_data import get_es_data


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def es_client():
    es_client = AsyncElasticsearch(hosts=test_settings.es_host)
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(scope='session')
async def re_client():
    re_client = Redis(host=test_settings.redis_host, port=test_settings.redis_port)
    yield re_client
    await re_client.close()


@pytest_asyncio.fixture(scope='session')
async def client_session():
    client_session = aiohttp.ClientSession()
    yield client_session
    await client_session.close()


@pytest_asyncio.fixture()
async def es_create_scheme(es_client):
    await es_client.indices.create(
        index='movies',
        body=MOVIES_SCHEMA,
    )
    await es_client.indices.create(
        index='genres',
        body=GENRES_SCHEMA,
    )
    await es_client.indices.create(
        index='persons',
        body=PERSONS_SCHEMA,
    )


@pytest_asyncio.fixture
async def es_write_data(es_client, re_client, es_create_scheme):
    documents = []
    test_data = get_es_data()
    for item in test_data:
        index = item.pop('index')
        documents.append(
            {
                "_index": index,
                "_id": item.get('id'),
                "_source": item,
            }
        )

    await async_bulk(es_client, documents)
    await es_client.indices.refresh()

    yield

    for _index in test_settings.es_index.split(', '):
        await es_client.indices.delete(
            index=_index,
        )

    await re_client.flushdb()
