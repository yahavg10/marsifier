import logging
import os
from typing import NoReturn

from injector import singleton

from configurations.config_models.app_model import AppConfig
from configurations.developer_config import SerializableType
from src.utils.annotations import Service, Inject
from src.utils.function_utils import object_functions_getter

logger = logging.getLogger(os.getenv("ENV"))


@singleton
@Service
class DataBase:
    def __init__(self, databases_directory: str) -> NoReturn:
        self.databases = object_functions_getter(databases_directory)

    @Inject("AppConfig")
    def setup_all_databases(self, app_config: AppConfig) -> NoReturn:
        conf = app_config.databases["types"]
        for db_name, db in self.databases.items():
            db.get("setup")(conf[db_name])

    def connect(self, database_name: str = None) -> NoReturn:
        db = self.databases.get(database_name) if database_name else None
        if db:
            db.get("connect")()
        else:
            logger.error(f"Database '{database_name}' not found.")
        if not database_name:
            for db in self.databases.values():
                db.get("connect")()

    def disconnect(self, database_name: str = None) -> NoReturn:
        db = self.databases.get(database_name) if database_name else None
        if db:
            db.get("disconnect")()
        else:
            logger.error(f"Database '{database_name}' not found.")
        if not database_name:
            for db in self.databases.values():
                db.get("disconnect")()

    def fetch(self, key: SerializableType, database_name: str = None) -> SerializableType:
        db = self.databases.get(database_name) if database_name else None
        if db:
            db.get("fetch")(key)
        else:
            logger.error(f"Database '{database_name}' not found.")
        if not database_name:
            all_data = {}
            for name, db in self.databases.items():
                all_data[name] = db.get("fetch")(key)
            return all_data

    def write(self, database_name: str = None, **kwargs) -> NoReturn:
        db = self.databases.get(database_name) if database_name else None
        if db:
            db.get("write")(**kwargs)
        else:
            logger.error(f"Database '{database_name}' not found.")
        if not database_name:
            for db in self.databases.values():
                db.get("write")(**kwargs)

    def delete(self, key: SerializableType, database_name=None) -> NoReturn:
        db = self.databases.get(database_name) if database_name else None
        if db:
            db.get("delete")(key)
        else:
            logger.error(f"Database '{database_name}' not found.")
        if not database_name:
            for db_name, db in self.databases.items():
                db.get("delete")(key)
