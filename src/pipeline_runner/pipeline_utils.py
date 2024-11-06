import logging
import os
import time
from threading import Lock
from typing import NoReturn

from src.utils.annotations import Inject

db_lock = Lock()

prod_logger = logging.getLogger("production")
dev_logger = logging.getLogger("development")


@Inject("DataBase")
def delete_from_db(database, common_name: str, suffix: str, database_name: str = None) -> NoReturn:
    try:
        database.fetch(common_name) and database.delete(key=common_name,
                                                        database_name=database_name)
        dev_logger.info(f"Cleaned up {common_name + suffix}")
    except Exception as e:
        prod_logger.warning(f"Error cleaning up files: {str(e)}")


@Inject("AppConfig")
def delete_all_united_files(app_config, common_name: str) -> NoReturn:
    suffixes = app_config.sender["file_invoker"]["suffixes"]
    file_path = app_config.receivers['file']['conf']['folder_to_monitor'] + "/" + common_name

    for suffix in suffixes:
        if os.path.exists(file_path + suffix):
            os.remove(file_path + suffix) and delete_from_db(common_name, suffix)


@Inject("AppConfig")
def delete_old_files(app_config):
    directory = app_config.receivers['file']['conf']['folder_to_monitor']
    age_limit = app_config.receivers['file']['conf']['file_age_limit']

    now = time.time()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and now - os.path.getmtime(file_path) > age_limit:
            os.remove(file_path)


@Inject("AppConfig")
def determine_part(app_config, file_name: str) -> str:
    suffixes = app_config.sender["file_invoker"]["suffixes"]
    return next((suffix for suffix in suffixes if suffix in file_name), "unknown_part")


def get_file_name(src_path) -> str:
    return os.path.basename(src_path.replace('\\', '/'))


@Inject("AppConfig")
def get_united_name(app_config, file_name: str) -> str:
    suffixes = app_config.sender["file_invoker"]["suffixes"]
    common_name = file_name.replace(next((suffix for suffix in suffixes if suffix in file_name), ""), "") \
        .replace(".jpg", "")
    return common_name


def scan_existing_files(orchestrator) -> NoReturn:
    folder_path = orchestrator.configuration.components.pipeline_executor["folder_path"]

    def is_valid_file(file_name: str) -> bool:
        fpath = os.path.join(folder_path, file_name)
        if os.path.isfile(fpath):
            return True
        else:
            dev_logger.warning(f"File failed filter (not a file): {file_path}")
            return False

    valid_files = filter(is_valid_file, os.listdir(folder_path))

    for valid_file in valid_files:
        file_path = os.path.join(folder_path, valid_file).replace("\\", "/")
        dev_logger.info(f"Processing file: {file_path}")
        orchestrator.pipeline_executor.strategy_pool.pool.submit(orchestrator.pipeline_executor.process,
                                                                 kwargs={'event_type': None, 'src_path': file_path})


@Inject("AppConfig", "DataBase")
def process_by_existence(app_config, database, common_name: str) -> NoReturn:
    prod_logger.error(common_name)
    with db_lock:
        exists_in_db = database.fetch(database_name="redis", key=common_name)
        if exists_in_db is not None:
            pass
        else:
            database.store(database_name="redis",
                           key=common_name,
                           expiry=app_config.databases["types"]["redis"]["expiry"])
