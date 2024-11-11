import logging
import os
import threading
import time
from contextlib import contextmanager
from typing import List
from typing import NoReturn

from configurations.config_models.app_model import AppConfig
from configurations.developer_config import strategy_pool
from src.database.database import DataBase
from src.pipeline_runner.pipeline_runner import PipelineRunner
from src.utils.annotations import Inject

db_lock = threading.Lock()
logger = logging.getLogger(os.getenv("ENV"))


@Inject("DataBase")
def delete_from_db(database: DataBase, common_name: str, suffix: str, database_name: str = None) -> NoReturn:
    try:
        database.fetch(common_name) and database.delete(key=common_name,
                                                        database_name=database_name)
        logger.info(f"Cleaned up {common_name + suffix}")
    except Exception as e:
        logger.warning(f"Error cleaning up files: {str(e)}")


def delete_all_united_files(common_name: str, app_config: AppConfig) -> NoReturn:
    suffixes = app_config.sender["file_invoker"]["params"]["suffixes"]
    file_path = app_config.receivers['file']['conf']['folder_to_monitor'] + "/" + common_name

    for suffix in suffixes:
        if os.path.exists(file_path + suffix):
            os.remove(file_path + suffix) and delete_from_db(common_name, suffix)


@Inject("AppConfig")
def delete_old_files(app_config: AppConfig) -> NoReturn:
    directory = app_config.receivers['file']['conf']['folder_to_monitor']
    age_limit = app_config.receivers['file']['conf']['file_age_limit']

    now = time.time()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and now - os.path.getmtime(file_path) > age_limit:
            os.remove(file_path)


@Inject("AppConfig")
def determine_part(app_config: AppConfig, file_name: str) -> str:
    suffixes = app_config.sender["file_invoker"]["params"]["suffixes"]
    return next((suffix for suffix in suffixes if suffix in file_name), "unknown_part")


def get_file_name(src_path: str) -> str:
    return os.path.basename(src_path.replace('\\', '/'))


@Inject("AppConfig")
def get_united_name(app_config: AppConfig, file_name: str) -> str:
    suffixes = app_config.sender["file_invoker"]["params"]["suffixes"]
    common_name = file_name.replace(next((suffix for suffix in suffixes if suffix in file_name), ""), "") \
        .replace(".jpg", "")
    return common_name


def get_valid_files(folder_path: str) -> List[str]:
    return [
        entry for entry in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, entry))
    ]


@Inject("AppConfig", "PipelineRunner")
def scan_existing_files(app_config: AppConfig, pipeline: PipelineRunner) -> NoReturn:
    folder_path = app_config.pipeline["folder_path"]
    valid_files = get_valid_files(folder_path)

    for valid_file in valid_files:
        file_path = os.path.join(folder_path, valid_file).replace("\\", "/")
        logger.info(f"Processing file: {os.path.basename(file_path)}")
        strategy_pool.pool.submit(pipeline.run_pipeline,
                                  data=file_path)


@contextmanager
def acquire_lock(lock: threading.Lock):
    acquired = lock.acquire()
    try:
        yield acquired
    finally:
        if acquired:
            lock.release()


@Inject("AppConfig", "DataBase", "send")
def process_by_existence(app_config, database, send_fn, common_name: str) -> NoReturn:
    exists_in_db = 0
    with acquire_lock(db_lock) as acquired:
        if not acquired:
            logger.warning("Could not acquire lock. Retrying might be necessary.")
        exists_in_db = database.exists(database_name="redis", key=common_name)

    if exists_in_db != 0:
        send_fn(common_name, "file_invoker")
        delete_all_united_files(common_name=common_name, app_config=app_config)
    else:
        database.write(
            database_name="redis",
            key=common_name,
            value=f"{app_config.pipeline['folder_path']}/{common_name}",
        )
