from typing import Union, List, Dict

import requests

from src.container import IoCContainer
from src.utils.pool import PoolFactory

container = IoCContainer()
strategy_pool = PoolFactory.create_pool_strategy("multithread", 3000)

SerializableType = Union[
    int, float, str, bool, None,
    List["SerializableType"],
    Dict[str, "SerializableType"]
]


database_functions_template = ("get_instance_connection", "setup",
                               "connect", "disconnect",
                               "write", "fetch", "delete", "exists")


default_send_fn = requests.post


pipeline_steps = [
    {
        "name": "get_file_name"
    },
    {
        "name": "get_united_name",
    },
    {
        "name": "process_by_existence",
    }
]
