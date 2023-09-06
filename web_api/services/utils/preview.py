from adapters import rabbit, redis
from redis.asyncio import Redis
from core.config import settings


async def startup() -> None:
    redis.redis = Redis(
        host=settings.redis_host,
        port=settings.redis_port
    )
    rabbit.rabbit = rabbit.RMQ()
    await rabbit.rabbit.connect(
        url=settings.get_amqp_uri()
    )


async def shutdown() -> None:
    if rabbit.rabbit:
        await rabbit.rabbit.close()

    if redis.redis:
        await redis.redis.close()
