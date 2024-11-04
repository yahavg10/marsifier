import logging

prod_logger = logging.getLogger("production")
dev_logger = logging.getLogger("development")


class DataBase:
    def __init__(self, databases):
        self.databases = {db.__class__.__name__: db for db in databases}

    def connect(self, database_name=None):
        db = self.databases.get(database_name) if database_name else None
        if db:
            db.connect()
        else:
            dev_logger.error(f"Database '{database_name}' not found.")
        if not db:
            for db in self.databases.values():
                db.connect()

    def disconnect(self, database_name=None):
        db = self.databases.get(database_name) if database_name else None
        if db:
            db.disconnect()
        else:
            dev_logger.error(f"Database '{database_name}' not found.")
        if not db:
            for db in self.databases.values():
                db.disconnect()

    def fetch(self, key, database_name=None):
        db = self.databases.get(database_name) if database_name else None
        if db:
            db.fetch(key)
        else:
            dev_logger.error(f"Database '{database_name}' not found.")
        if not db:
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
        for db in self.databases.values():
            db.write_data(kwargs[db.__class__.__name__])
