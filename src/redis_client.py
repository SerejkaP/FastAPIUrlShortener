from redis import Redis, asyncio as aioredis
from config import REDIS_URL

redis_client: Redis = None


async def init_redis():
    global redis_client
    redis_client = await aioredis.from_url(REDIS_URL, decode_responses=True)


async def close_redis():
    if redis_client is not None:
        await redis_client.close()


async def get_redis():
    """Безопасный доступ к Redis"""
    if redis_client is None:
        raise RuntimeError(
            "Redis не инициализирован! Запусти init_redis() перед использованием.")
    return redis_client
