import redis.asyncio as redis
from app.core.config import settings


async def get_redis():
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        yield redis_client
    finally:
        await redis_client.close()
