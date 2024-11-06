import logging
from typing import NoReturn, Callable

from requests import RequestException

from configurations.developer_config import container, default_send_fn
from src.sender.payload_methods import file_invoker
from src.utils.annotations import Inject

prod_logger = logging.getLogger(name="production")
dev_logger = logging.getLogger(name="development")


@Inject("AppConfig")
def send(app_config, common_name, sender_type, payload_fn=file_invoker,
         send_method: Callable = default_send_fn) -> NoReturn:
    try:
        app_config.sender[sender_type].update("common_name", common_name)
        payload = payload_fn(** app_config.sender[sender_type])

        response = send_method(app_config.sender[sender_type]["endpoint"], json=payload)
        dev_logger.info(response.json())
    except RequestException as e:
        prod_logger.error(f"Error during request: {str(e)}")
