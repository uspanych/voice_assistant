import json
from functools import lru_cache

from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.films import FilmResponseModel
from models.persons import Person, PersonPage, PersonSort
from redis.asyncio import Redis
from services.utils.body_elastic import (get_body_query, get_body_search,
                                         get_body_search_with_films)

from .base import BaseService, ElasticStorage, RedisCache


class PersonService(BaseService):
    """Класс реализует возможность получения персоналий."""

    async def get_by_id(
            self,
            person_id: str,
    ) -> PersonPage | None:
        """Метод возвращает персону по id."""

        data = await self.get_data_by_id(
            person_id,
            'persons',
            self.FILM_CACHE_EXPIRE_IN_SECONDS,
        )

        final_dict = {
            'id': person_id,
            'full_name': data.get('full_name'),
            'films': [],
        }

        body = get_body_search_with_films(
            value=person_id,
            field='id'
        )

        data_list = await self.get_list(
            index='movies',
            body=body,
        )

        for item in data_list:
            roles = []
            for person in item.get('actors'):
                if person.get('id') == person_id:
                    roles.append('actor')

            for person in item.get('directors'):
                if person.get('id') == person_id:
                    roles.append('director')

            for person in item.get('writers'):
                if person.get('id') == person_id:
                    roles.append('writer')

            final_dict['films'].append(
                {
                    'id': item.get('id'),
                    'roles': roles,
                }
            )

        return final_dict

    async def get_persons_list(
            self,
            sort_by: PersonSort = PersonSort.down_full_name,
            page_size: int = 50,
            page_number: int = 1
    ) -> list[Person] | None:
        """Метод возвращает список персоналий."""

        sort_order = 'desc' if sort_by == 'full_name' else 'asc'
        body = get_body_search(
            size=page_size,
            sort_by='full_name',
            offset=(page_size * page_number) - page_size,
            sort_order=sort_order
        )

        data_list = await self.get_list(
            index='persons',
            sort_by='full_name',
            body=body,
            ttl=self.FILM_CACHE_EXPIRE_IN_SECONDS,
            sort_order=sort_order,
            page_size=page_size,
            page_number=page_number,
        )

        return data_list

    async def get_films_with_person(
            self,
            person_id: str,
    ) -> FilmResponseModel | None:
        """Метод возвращает фильмы с участием выбранного персонажа."""

        body = get_body_search_with_films(
            field='id',
            value=person_id,
        )

        data_list = await self.get_list(
            index='movies',
            body=body,
            unique_key=person_id
        )

        return data_list

    async def search_person_with_films(
            self,
            query: str,
            page_size: int = 50,
            page_number: int = 1,
            process_id: str = None
    ) -> list[PersonPage] | None:

        body_person = get_body_query(
            field='full_name',
            value=query,
            size=page_size,
            offset=(page_size * page_number) - page_size,
        )

        data_list_person = await self.get_list(
            index='persons',
            body=body_person,
            unique_key=query,
            page_size=page_size,
            page_number=page_number,
            process_id=process_id
        )

        persons_list = []

        for person in data_list_person:

            final_dict = {
                'id': person.get('id'),
                'full_name': person.get('full_name'),
                'films': [],
            }

            body = get_body_search_with_films(
                value=person.get('id'),
                field='id'
            )

            data_list = await self.get_list(
                index='movies',
                body=body,
                unique_key=person.get('id')
            )

            for movie in data_list:
                roles = []
                for item in movie.get('actors'):
                    if item.get('id') == person.get('id'):
                        roles.append('actor')

                for item in movie.get('directors'):
                    if item.get('id') == person.get('id'):
                        roles.append('director')

                for item in movie.get('writers'):
                    if item.get('id') == person.get('id'):
                        roles.append('writer')

                final_dict['films'].append(
                    {
                        'id': movie.get('id'),
                        'roles': roles,
                    }
                )

            persons_list.append(final_dict)
        if process_id:
            await self.cache_handler.set_by_id(
                key=process_id,
                value=json.dumps(persons_list),
                ttl=300,
            )
        return persons_list


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(RedisCache(redis), ElasticStorage(elastic))
