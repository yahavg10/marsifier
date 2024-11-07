import importlib
import inspect
import logging
import os
from typing import List, Dict, Any, Type

from configurations.config_models.app_model import AppConfig
from src.database.abstract_database import AbstractDbTemplate
from src.receiver.data_sources_handlers.data_source_handler import DataSourceHandler

logger = logging.getLogger(os.getenv("ENV"))

from configurations.developer_config import database_functions_template


def check_functions_template(database_functions: List) -> int:
    missing_params = [param for param in database_functions_template if
                      param not in database_functions]
    return len(missing_params) != 0


def object_classes_getter(config, directory: str, base_class: Type = AbstractDbTemplate)\
        -> Dict[str, Any]:
    objects: Dict[str, Any] = {}

    for filename in os.listdir(directory):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]  # Remove '.py' extension
            module = importlib.import_module(f"{directory.replace('/', '.')}.{module_name}")

            for name, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, base_class) and cls is not base_class:
                    instance_name = module_name.replace("_handler", "")
                    objects[instance_name] = cls(**config["types"][instance_name])

    return objects


def import_dynamic_model(class_model_config: str) -> Any:
    try:
        module = importlib.import_module(class_model_config["model_path"])
        dynamic_class = getattr(module, class_model_config['model_name'])
        return dynamic_class
    except AttributeError as e:
        logger.warning(
            f"class {class_model_config['model_name']} not found"
            f" in module {class_model_config['model_name']}")
        raise e
    except Exception as e:
        logger.error(e)
        raise e


def get_receivers(config: AppConfig) -> Dict[str, DataSourceHandler]:
    receivers = {}
    for receiver_name, receiver_conf in config.receivers.items():
        receiver_model = import_dynamic_model(receiver_conf["path"])
        receivers[receiver_name] = receiver_model(**receiver_conf["conf"])
    return receivers
