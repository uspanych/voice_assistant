import asyncio

from aio_pika.abc import AbstractIncomingMessage

from adapters.rabbit import RMQ
from core.config import settings
from core.logger import logger
from worker import request_async_api


async def main():
    rabbit = RMQ()

    await rabbit.connect(settings.get_amqp_uri(), queue_name="voice_service")
    await rabbit.queue.bind(rabbit.exchange, routing_key="events.files")

    async with rabbit.queue.iterator() as iterator:
        message: AbstractIncomingMessage
        async for message in iterator:
            async with message.process(ignore_processed=True):
                logger.info("Получено новое сообщение в очереди")
                # request_async_api(message)
                request_async_api.delay(message.body)
                await message.ack()


if __name__ == "__main__":
    logger.info("Сервис запустился")
    asyncio.run(main())
