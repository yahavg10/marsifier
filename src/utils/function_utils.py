import importlib
import inspect
import logging
import os
from typing import List, Dict

from configurations.config_models.app_model import AppConfig
from src.container import IoCContainer

dev_logger = logging.getLogger("development")

from configurations.developer_config import database_functions_template


def check_functions_template(database_functions: List):
    missing_params = [param for param in database_functions_template if
                      param not in database_functions]
    return len(missing_params) != 0


def object_functions_getter(directory: str):
    objects: Dict[str, Dict[str, callable]] = {}

    for filename in os.listdir(directory):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]  # Remove '_handler.py' extension
            module = importlib.import_module(f"{directory.replace('/', '.')}.{module_name}")
            objects[module_name.replace("_handler", "")] = {name: func for name, func in
                                                            inspect.getmembers(module, inspect.isfunction)}
            if not check_functions_template(objects[module_name.replace("_handler", "")].values()):
                objects.pop(module_name)
    return objects


def import_dynamic_model(class_model_config):
    try:
        module = importlib.import_module(class_model_config["model_path"])
        dynamic_class = getattr(module, class_model_config['model_name'])
        return dynamic_class
    except AttributeError as e:
        dev_logger.warning(
            f"class {class_model_config['model_name']} not found"
            f" in module {class_model_config['model_name']}")
        raise e
    except Exception as e:
        dev_logger.error(e)
        raise e


def get_receivers(config: AppConfig):
    receivers = {}
    for receiver_name, receiver_conf in config.receivers.items():
        receiver_model = import_dynamic_model(receiver_conf["path"])
        receivers[receiver_name] = receiver_model(**receiver_conf["conf"])
    return receivers


