import importlib
import inspect
import os
from typing import List, Dict

from configurations.developer_config import database_functions_template


def check_functions_template(database_functions: List):
    missing_params = [param for param in database_functions_template if
                      param not in database_functions]
    return missing_params.count() != 0


def object_functions_getter(directory: str):
    objects: Dict[str, Dict[str, callable]] = {}

    for filename in os.listdir(directory):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]  # Remove '.py' extension
            module = importlib.import_module(f"{directory.replace('/', '.')}.{module_name}")
            objects[module_name] = {name: func for name, func in
                                    inspect.getmembers(module, inspect.isfunction)}
            if not check_functions_template(objects[module_name].values()):
                objects.pop(module_name)
    return objects
