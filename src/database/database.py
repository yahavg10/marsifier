import logging
import os
from typing import NoReturn

from configurations.config_models.app_model import AppConfig
from configurations.developer_config import SerializableType
from src.utils.annotations import Service, Inject
from src.utils.function_utils import object_classes_getter

logger = logging.getLogger(os.getenv("ENV"))


@Service
class DataBase:

    def __init__(self, databases_directory: str) -> NoReturn:
        self.databases = {}
        self.databases_directory = databases_directory

    @Inject("AppConfig")
    def setup_all_databases(self, app_config: AppConfig) -> NoReturn:
        self.databases = object_classes_getter(config=app_config.databases,
                                               directory=self.databases_directory)

    def fetch(self, key: SerializableType, database_name: str = None) -> SerializableType:
        # self.setup_all_databases()
        db = self.databases.get(database_name) if database_name else None
        if db:
            return db.fetch(key)
        elif database_name is not None:
            logger.exception(f"Database '{database_name}' not found.")
        if not database_name:
            all_data = {}
            for name, db in self.databases.items():
                all_data[name] = db.fetch(key)
            return all_data

    def write(self, database_name: str = None, **kwargs) -> NoReturn:
        # self.setup_all_databases()
        db = self.databases.get(database_name) if database_name else None
        if db:
            db.write(**kwargs)
        elif database_name is not None:
            logger.exception(f"Database '{database_name}' not found.")
        if not database_name:
            for db in self.databases.values():
                db.write(**kwargs)

    def delete(self, key: SerializableType, database_name=None) -> NoReturn:
        # self.setup_all_databases()
        db = self.databases.get(database_name) if database_name else None
        if db:
            db.delete(key)
        elif database_name is not None:
            logger.exception(f"Database '{database_name}' not found.")
        if not database_name:
            for db_name, db in self.databases.items():
                db.delete(key)

    def exists(self, key: SerializableType, database_name=None) -> bool:
        # self.setup_all_databases()
        db = self.databases.get(database_name) if database_name else None
        if db:
            return db.exists(key)
        elif database_name is not None:
            logger.exception(f"Database '{database_name}' not found.")
        if not database_name:
            for db_name, db in self.databases.items():
                pass
                if db.exists(key):
                    return True
        return False
