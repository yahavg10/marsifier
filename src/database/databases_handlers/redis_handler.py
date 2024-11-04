import logging
from typing import Any, Dict

import redis

prod_logger = logging.getLogger("production")
dev_logger = logging.getLogger("development")

instance_mutable_data = {}


def get_instance_connection():
    if not hasattr(get_instance_connection, "_instance"):
        get_instance_connection.instance = redis.Redis(**instance_mutable_data)
    return get_instance_connection.instance


def setup(config: Dict[str, Any]):
    instance_mutable_data.update("host", config["host"])
    instance_mutable_data.update("port", config["port"])
    instance_mutable_data.update("db", config["db"])
    instance_mutable_data.update("decode_response", config["decode_response"])


def connect():
    get_instance_connection()


def disconnect():
    get_instance_connection().close()


def write(**kwargs):
    try:
        get_instance_connection().setex(kwargs["key"], kwargs["expiry"], kwargs["value"])
    except Exception as e:
        dev_logger.warning(str(e))
    dev_logger.debug(f"Stored {kwargs['value']} in Redis with key {kwargs['key']}")


def fetch(key: str) -> str:
    return get_instance_connection().get(key)


def delete(key: str):
    get_instance_connection().delete(key)
    dev_logger.info(f"Deleted Redis key {key}")
