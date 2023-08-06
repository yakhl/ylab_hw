import redis

from .env_var import REDIS_HOST, REDIS_PORT

pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    db=0,
    socket_timeout=0.1,
)


def get_redis():
    return redis.Redis(connection_pool=pool)
