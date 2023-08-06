import json
from uuid import UUID

import redis
from fastapi import Depends
from fastapi.encoders import jsonable_encoder

from ..database.redis_db import get_redis


class CacheRepository:
    _was_redis_disconnect = True

    def __init__(self, redis: redis.Redis = Depends(get_redis)):
        self.redis = redis
        self.ttl_sec = 3600

    @staticmethod
    def _handle_redis_exceptions(func):
        def wrapper(self, *args, **kwargs):
            try:
                if CacheRepository._was_redis_disconnect:
                    self.redis.flushdb()
                result = func(self, *args, **kwargs)
                CacheRepository._was_redis_disconnect = False
                return result
            except (redis.exceptions.TimeoutError, redis.exceptions.ConnectionError):
                CacheRepository._was_redis_disconnect = True
                return None

        return wrapper

    @_handle_redis_exceptions
    def set(self, item_id: UUID | str, item_data: dict | list[dict]) -> None:
        json_compatible_item_data = jsonable_encoder(item_data)
        serialized_item_data = json.dumps(json_compatible_item_data)
        self.redis.set(str(item_id), serialized_item_data, self.ttl_sec)

    @_handle_redis_exceptions
    def get(self, item_id: UUID | str) -> str | None:
        menu_cache = self.redis.get(str(item_id))
        if menu_cache is None:
            return None
        return menu_cache

    @_handle_redis_exceptions
    def delete(self, item_id: UUID | str) -> None:
        self.redis.delete(str(item_id))

    @_handle_redis_exceptions
    def flush(self) -> None:
        self.redis.flushdb()
