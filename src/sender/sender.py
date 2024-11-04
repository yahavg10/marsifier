import logging
from typing import Callable, NoReturn

import requests
import yaml
from requests import RequestException

from configurations.config_models.app_model import AppConfig
from src.utils.file_utils import load_configuration

prod_logger = logging.getLogger(name="production")
dev_logger = logging.getLogger(name="development")
app_config = load_configuration(AppConfig, yaml.safe_load)


def send_request(sender_type: str, payload_fn: Callable,
                 send_fn: Callable = requests.post) -> NoReturn:
    payload = payload_fn(app_config.sender[sender_type])
    try:
        prod_logger.info(f"Sending request to {app_config.sender['endpoint']} with payload: {payload}")
        response = send_fn(app_config.sender[sender_type], files=payload)
        dev_logger.info(response.json())
    except RequestException as e:
        prod_logger.error(f"Error during request: {str(e)}")
