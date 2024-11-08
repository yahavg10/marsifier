import logging
import os
from typing import NoReturn

from redis import Redis

from configurations.developer_config import SerializableType
from src.database.database_template import AbstractDbTemplate

logger = logging.getLogger(os.getenv("ENV"))


class RedisHandler(AbstractDbTemplate):
    def __init__(self, host: str, port: int, db: int, expiry: int):
        self.redis = Redis(
            host=host,
            port=port,
            db=db
        )
        self.expiry = expiry

    def write(self, **kwargs) -> NoReturn:
        try:
            self.redis.setex(kwargs["key"], self.expiry, kwargs["value"])
        except Exception as e:
            logger.error(str(e))

    def fetch(self, key: str) -> str:
        return self.redis.get(key)

    def exists(self, key: SerializableType) -> bool:
        return self.redis.exists(key)

    def delete(self, key: str):
        self.redis.delete(key)
        logger.info(f"Deleted Redis key {key}")
