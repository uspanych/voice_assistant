from elasticsearch import AsyncElasticsearch, NotFoundError
from redis.asyncio import Redis
import json
import abc


class AbstractStorage(abc.ABC):
    @abc.abstractmethod
    async def get_by_id(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    async def search_data(self, *args, **kwargs):
        ...


class AbstractCache(abc.ABC):
    @abc.abstractmethod
    async def get_by_id(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    async def set_by_id(self, *args, **kwargs):
        ...


class ElasticStorage(AbstractStorage):
    def __init__(
            self,
            elastic: AsyncElasticsearch,
    ):
        self.elastic = elastic

    async def get_by_id(
            self,
            *args,
            **kwargs,
    ):
        try:
            doc = await self.elastic.get(
                index=kwargs.get('index'),
                id=kwargs.get('data_id'),
            )

        except NotFoundError:
            return None

        return doc['_source']

    async def search_data(
            self,
            *args,
            **kwargs,
    ) -> list[dict]:
        """Метод осуществляет поиск в Elasticsearch."""

        data = await self.elastic.search(
            index=kwargs.get('index'),
            body=kwargs.get('body'),
        )

        return [item['_source'] for item in data['hits']['hits']]


class RedisCache(AbstractCache):
    def __init__(
            self,
            redis: Redis,
    ):
        self.redis = redis

    async def get_by_id(self, *args, **kwargs):
        data = await self.redis.get(kwargs.get('key'))
        if not data:
            return None

        return json.loads(data)

    async def set_by_id(self, *args, **kwargs):
        await self.redis.set(
            kwargs.get('key'),
            kwargs.get('value'),
            kwargs.get('ttl'),
        )


class BaseService:
    """Класс реализует базовые функции для возможных сервисов."""

    def __init__(
            self,
            cache_handler: RedisCache,
            storage_handler: ElasticStorage,
    ):
        self.cache_handler = cache_handler
        self.storage_handler = storage_handler
        self.FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5

    async def get_data_by_id(
            self,
            data_id: str,
            index: str,
            ttl: int = 300,
            process_id: str = None
    ):
        """Метод возвращает запись по id."""

        cache_key = f'{data_id}-{index}'
        data = await self.cache_handler.get_by_id(
            key=cache_key,
        )

        if not data:
            data = await self.storage_handler.get_by_id(
                data_id=data_id,
                index=index,
            )

            if not data:
                return None

            await self.cache_handler.set_by_id(
                key=process_id,
                value=json.dumps(data),
                ttl=ttl,
            )

        return data

    async def get_list(
            self,
            index: str,
            body: str,
            sort_by: str = None,
            ttl: int = 300,
            sort_order: str = 'desc',
            page_size: int = 50,
            page_number: int = 1,
            genre: str = None,
            actor: str = None,
            director: str = None,
            writer: str = None,
            unique_key: str = None,
            process_id: str = None
    ):
        """Метод возвращает список записей."""

        cache_key = f'{index}-{sort_by}-{sort_order}-{page_size}-{page_number}-{genre}-{actor}-{director}-{writer}' \
                    f'-{unique_key}'

        data = await self.cache_handler.get_by_id(
            key=cache_key,
        )
        if not data:
            data = await self.storage_handler.search_data(
                index=index,
                body=body,
            )

            if not data:
                return []

            await self.cache_handler.set_by_id(
                key=cache_key,
                value=json.dumps(data),
                ttl=ttl,
            )

        return data

    async def search_by_query(
            self,
            index: str,
            body: str,
            query: str,
            ttl: int = 300,
            page_size: int = 50,
            page_number: int = 1,
            process_id: str = None
    ):
        """Метод осуществляет поиск записей по query."""

        cache_key = f'{index}-{query}-{ttl}-{page_size}-{page_number}'

        data = await self.cache_handler.get_by_id(
            key=cache_key,
        )

        if not data:
            data = await self.storage_handler.search_data(
                index=index,
                body=body,
            )

            if not data:
                if process_id is not None:
                    await self.cache_handler.set_by_id(
                        key=process_id,
                        value=json.dumps([]),
                        ttl=ttl,
                    )
                return []

            await self.cache_handler.set_by_id(
                key=cache_key,
                value=json.dumps(data),
                ttl=ttl,
            )
        
        if process_id is not None:
            await self.cache_handler.set_by_id(
                key=process_id,
                value=json.dumps(data),
                ttl=ttl,
            )

        return data
