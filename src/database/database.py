import logging
from typing import Any

from src.utils.function_utils import object_functions_getter

prod_logger = logging.getLogger("production")
dev_logger = logging.getLogger("development")


class DataBase:
    def __init__(self, databases_directory):
        self.databases = object_functions_getter(databases_directory)

    def setup_all_databases(self, databases_config):
        for db_name, db in self.databases.items():
            db.get("setup")(databases_config[db_name.replace("_handler", "")])

    def connect(self, database_name=None):
        db = self.databases.get(database_name) if database_name else None
        if db:
            db.connect()
        else:
            dev_logger.error(f"Database '{database_name}' not found.")
        if not database_name:
            for db in self.databases.values():
                db.connect()

    def disconnect(self, database_name=None):
        db = self.databases.get(database_name) if database_name else None
        if db:
            db.disconnect()
        else:
            dev_logger.error(f"Database '{database_name}' not found.")
        if not database_name:
            for db in self.databases.values():
                db.disconnect()

    def fetch(self, key, database_name=None):
        db = self.databases.get(database_name) if database_name else None
        if db:
            db.fetch(key)
        else:
            dev_logger.error(f"Database '{database_name}' not found.")
        if not database_name:
            all_data = {}
            for name, db in self.databases.items():
                all_data[name] = db.fetch_data(key)
            return all_data

    def write(self, database_name=None, **kwargs):
        db = self.databases.get(database_name) if database_name else None
        if db:
            db.write(kwargs)
        else:
            dev_logger.error(f"Database '{database_name}' not found.")
            if not database_name:
                for db_name, db in self.databases.items():
                    db.get("write")(kwargs[db_name.replace("_handler", "")])

    def delete(self, key: Any, database_name=None):
        db = self.databases.get(database_name) if database_name else None
        if db:
            db.get("delete")(key)
        else:
            dev_logger.error(f"Database '{database_name}' not found.")
        if not database_name:
            for db_name, db in self.databases.items():
                db.get("delete")(key)
