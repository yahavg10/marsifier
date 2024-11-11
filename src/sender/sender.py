import logging
import os
from typing import NoReturn, Callable

from requests import RequestException

from configurations.config_models.app_model import AppConfig
from configurations.developer_config import default_send_fn
from src.sender.payload_methods import file_invoker
from src.utils.annotations import Inject

logger = logging.getLogger(name=os.getenv("ENV"))


@Inject("AppConfig")
def send(app_config: AppConfig, common_name: str, sender_type: str, payload_fn=file_invoker,
         send_method: Callable = default_send_fn) -> NoReturn:
    try:
        app_config.sender[sender_type]["params"]["common_name"] = common_name
        payload = payload_fn(**app_config.sender[sender_type]["params"])
        logger.info(payload)
        response = send_method(app_config.sender[sender_type]["endpoint"], files=payload)
        logger.info(response.json())
        logger.error(response.json())
    except RequestException as e:
        logger.warning(f"Error during request: {str(e)}")
