from redis import asyncio as aioredis

from core.configs.env_var import REDIS_HOST, REDIS_PORT

pool = aioredis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    db=0,
)


def get_redis():
    return aioredis.Redis(connection_pool=pool)
