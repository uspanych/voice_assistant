from .handlers import AbstractStorage, AbstractQueue, RedisStorage, RabbitMq
import uuid
from aio_pika.exceptions import AMQPException
from core.logger import logger
from functools import lru_cache
from redis.asyncio import Redis
from fastapi import Depends
from adapters.rabbit import get_rabbit, RMQ
from adapters.redis import get_redis
import base64

class SearchService:

    def __init__(
        self,
        storage_handler: AbstractStorage,
        queue_handler: AbstractQueue,
    ):
        self.storage_handler = storage_handler
        self.queue_handler = queue_handler

    async def create_task(
        self,
        audio_file,
    ) -> uuid.UUID:
        """Метод получает на вход аудио файл и отдает uuid задачи."""

        process_id = uuid.uuid4()

        # print(await audio_file.read())

        content = base64.b64encode(await audio_file.read()).decode()
        try:
            if audio_file:
                print('Файл получен')

            await self.queue_handler.send_data(
                data={
                    'process_id': process_id,
                    'file': content
                },
                routing_key='events.files',
                correlation_id=process_id
            )

            return process_id

        except AMQPException as error:
            logger.error(f'Ошибка сервиса WebApi - {error}')

    async def get_status_task(
        self,
        process_id: str
    ):

        result = await self.storage_handler.get_by_id(
            key=process_id
        )
        # TODO: Поставить условие на проверку статуса if else
        print(result)


@lru_cache()
def get_search_service(
    storage: Redis = Depends(get_redis),
    queue: RMQ = Depends(get_rabbit),
) -> SearchService:
    return SearchService(
        storage_handler=RedisStorage(storage),
        queue_handler=RabbitMq(queue),
    )
