import asyncio
from typing import Any

import orjson
from aio_pika import DeliveryMode, Exchange, ExchangeType, connect_robust
from aio_pika.abc import AbstractQueue
from aio_pika.channel import Channel
from aio_pika.connection import Connection
from aio_pika.message import Message


class RMQ:
    def __init__(self) -> None:
        self.connection: Connection | None = None
        self.channel: Channel | None = None
        self.exchange: Exchange | None = None
        self.queue: AbstractQueue | None = None

    async def connect(
        self,
        url: str,
        queue_name: str,
        topic_name: str = "topic_v1"
    ):
        self.topic_name = topic_name
        self.connection = await connect_robust(
            url=url,
            loop=asyncio.get_running_loop()
        )

        self.channel = await self.connection.channel()

        self.exchange = await self.channel.declare_exchange(
            self.topic_name,
            ExchangeType.TOPIC
        )
        self.queue = await self.channel.declare_queue(queue_name, durable=True)

    async def send(
        self,
        routing_key: str,
        data: dict,
        correlation_id,
    ) -> None:

        message = Message(
            body=self._serialize(data),
            content_type="application/json",
            correlation_id=correlation_id,
            delivery_mode=DeliveryMode.PERSISTENT
        )
        await self.exchange.publish(message, routing_key, timeout=10)


    @staticmethod
    def _serialize(data: Any) -> bytes:
        return orjson.dumps(data)

    @staticmethod
    def _deserialize(data: bytes) -> Any:
        return orjson.loads(data)

    async def close(self):
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()


rabbit: RMQ | None = None


async def get_rabbit() -> RMQ:
    return rabbit