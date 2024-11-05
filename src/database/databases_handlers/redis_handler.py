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
    instance_mutable_data["host"] = config["host"]
    instance_mutable_data["port"] = config["port"]
    instance_mutable_data["db"] = config["db"]


def write(key, expiry, value):
    try:
        get_instance_connection().setex(key, expiry, value)
    except Exception as e:
        dev_logger.warning(str(e))
    dev_logger.debug(f"Stored {value} in Redis with key {key}")


connect = lambda: get_instance_connection()

disconnect = lambda: get_instance_connection().close()

delete = lambda key: get_instance_connection().delete(key)

fetch = lambda key: get_instance_connection().get(key)

exists = lambda key: get_instance_connection().exists(key)
