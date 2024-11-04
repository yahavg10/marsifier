import logging

import redis

from src.database.databases_handlers.database_handler import DataBaseHandler

prod_logger = logging.getLogger("production")
dev_logger = logging.getLogger("development")


class RedisHandler(DataBaseHandler):
    def __init__(self, host: str, port: int, db: int, decode_response: bool):
        self.host = host
        self.port = port
        self.db = db
        self.decode_response = decode_response
        self._instance = redis.Redis

    def connect(self):
        self._instance = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            decode_responses=self.decode_response
        )

    def disconnect(self):
        self._instance.close()

    def write(self, **kwargs):
        try:
            self._instance.setex(kwargs["key"], kwargs["expiry"], kwargs["value"])
        except Exception as e:
            dev_logger.warning(str(e))
        dev_logger.debug(f"Stored {kwargs['value']} in Redis with key {kwargs['key']}")

    def fetch(self, key: str) -> str:
        return self._instance.get(key)

    def delete(self, key: str):
        self._instance.delete(key)
        dev_logger.info(f"Deleted Redis key {key}")
