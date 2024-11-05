import logging.config as log
import os
from typing import Callable

import yaml

from configurations.config_models.app_model import AppConfig


def load_configuration(config_model: AppConfig, load_conf_fn: Callable):
    with open(file=os.environ["APP_CONFIG_PATH"]) as config_file:
        config_data = load_conf_fn(config_file)
    configuration = config_model.from_dict(config_data, config_model)
    return configuration


def setup_logger():
    with open(file=os.environ["LOG_CONFIG_PATH"]) as config_file:
        config = yaml.safe_load(config_file.read())
    log.dictConfig(config)
