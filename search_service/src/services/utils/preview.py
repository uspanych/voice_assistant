from db import redis, elastic
from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch
from core.config import settings


async def startup() -> None:
    redis.redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    elastic.es = AsyncElasticsearch(
        hosts=[f'{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}'])


async def shutdown() -> None:
    if redis.redis:
        await redis.redis.close()

    if elastic.es:
        await elastic.es.close()
