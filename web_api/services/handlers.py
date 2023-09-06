import abc
from adapters.rabbit import RMQ
from redis.asyncio import Redis
import json


class AbstractStorage(abc.ABC):
    @abc.abstractmethod
    async def set_by_id(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(self, *args, **kwargs):
        raise NotImplementedError


class AbstractQueue(abc.ABC):
    @abc.abstractmethod
    async def send_data(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    async def read_data(self, *args, **kwargs):
        raise NotImplementedError


class RedisStorage(AbstractStorage):
    def __init__(
            self,
            redis: Redis,
    ):
        self.redis = redis

    async def get_by_id(self, *args, **kwargs) -> dict | None:
        data = await self.redis.get(kwargs.get('key'))
        if not data:
            return None

        return json.loads(data)

    async def set_by_id(self, *args, **kwargs) -> None:
        await self.redis.set(
            kwargs.get('key'),
            kwargs.get('value'),
            kwargs.get('ttl'),
        )


class RabbitMq(AbstractQueue):
    def __init__(
        self,
        rabbit: RMQ,
    ):
        self.rabbit = rabbit

    async def send_data(self, *args, **kwargs):
        await self.rabbit.send(
            routing_key=kwargs.get('routing_key'),
            data=kwargs.get('data'),
            correlation_id=kwargs.get('correlation_id')
        )

    async def read_data(self, *args, **kwargs):
        await self.rabbit.consume_queue(
            func=kwargs.get('func'),
            binding_keys=kwargs.get('binding_keys'),
            queue_name=kwargs.get('queue_name'),
        )
