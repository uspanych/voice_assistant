from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.genres import (GenreDetailResponseModel, GenreResponseModel,
                           GenreSort)
from services.utils.body_elastic import get_body_search

from .base import BaseService, ElasticStorage, RedisCache


class GenreService(BaseService):
    """Метод реализует возможность получения жанров."""

    async def get_by_id(
            self,
            genre_id: str,
    ) -> GenreDetailResponseModel | None:
        """Метод возвращает жанр по id."""

        data = await self.get_data_by_id(
            genre_id,
            'genres',
            self.FILM_CACHE_EXPIRE_IN_SECONDS,
        )

        return data

    async def get_genres_list(
            self,
            sort_by: GenreSort = GenreSort.down_name,
            page_size: int = 50,
            page_number: int = 1
    ) -> list[GenreResponseModel] | None:
        """Метод возвращает список жанров."""

        sort_order = 'desc' if sort_by == 'name' else 'asc'
        body = get_body_search(
            size=page_size,
            sort_by='name',
            offset=(page_size * page_number) - page_size,
            sort_order=sort_order
        )

        data_list = await self.get_list(
            index='genres',
            sort_by='name',
            body=body,
            ttl=self.FILM_CACHE_EXPIRE_IN_SECONDS,
            sort_order=sort_order,
            page_size=page_size,
            page_number=page_number,
        )

        return data_list


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(RedisCache(redis), ElasticStorage(elastic))
