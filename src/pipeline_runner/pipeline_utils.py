import logging
import os
import time
from threading import Lock
from typing import NoReturn, List

from configurations.config_models.app_model import AppConfig
from configurations.developer_config import strategy_pool
from src.pipeline_runner.pipeline_runner import PipelineRunner
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


def get_valid_files(folder_path: str) -> List:
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
        dev_logger.info(f"Processing file: {os.path.basename(file_path)}")
        time.sleep(1.0)
        strategy_pool.pool.submit(pipeline.run_pipeline,
                                  data=file_path)


@Inject("AppConfig", "DataBase", "send")
def process_by_existence(app_config, database, send_fn, common_name: str) -> NoReturn:
    with db_lock:
        # db_lock.acquire()
        exists_in_db = database.fetch(database_name="redis", key=common_name)
        # db_lock.release()
        print(exists_in_db)
        if exists_in_db is not None:
            send_fn(common_name, "file_invoker")
            delete_all_united_files(common_name=common_name)
        else:
            database.write(database_name="redis",
                           key=common_name,
                           value=f"{app_config.pipeline['folder_path']}/{common_name}",
                           expiry=app_config.databases["types"]["redis"]["expiry"])
