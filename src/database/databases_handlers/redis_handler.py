import logging
import os
from typing import Any, Dict, NoReturn

from redis import Redis

from configurations.developer_config import SerializableType

logger = logging.getLogger(os.getenv("ENV"))

instance_mutable_data = {}


def get_instance_connection() -> Redis:
    if not hasattr(get_instance_connection, "_instance"):
        get_instance_connection.instance = Redis(**instance_mutable_data)
    return get_instance_connection.instance


def setup(config: Dict[str, Any]) -> NoReturn:
    instance_mutable_data["host"] = config["host"]
    instance_mutable_data["port"] = config["port"]
    instance_mutable_data["db"] = config["db"]


def write(key: SerializableType, expiry: int, value: SerializableType) -> NoReturn:
    try:
        get_instance_connection().setex(key, expiry, value)
    except Exception as e:
        logger.warning(str(e))
    logger.debug(f"Stored {value} in Redis with key {key}")


connect = lambda: get_instance_connection()

disconnect = lambda: get_instance_connection().close()

delete = lambda key: get_instance_connection().delete(key)

fetch = lambda key: get_instance_connection().get(key)

exists = lambda key: get_instance_connection().exists(key)
