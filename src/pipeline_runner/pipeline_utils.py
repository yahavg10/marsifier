import logging
import os
from threading import Lock
from typing import NoReturn, List

from configurations.developer_config import container
from src.utils.annotations import Inject

db_lock = Lock()

prod_logger = logging.getLogger("production")
dev_logger = logging.getLogger("development")


def delete_from_db(common_name: str, suffix: str, database_name: str = None) -> NoReturn:
    try:
        container.database.fetch(common_name) and container.database.delete(key=common_name,
                                                                            database_name=database_name)
        dev_logger.info(f"Cleaned up {common_name + suffix}")
    except Exception as e:
        prod_logger.warning(f"Error cleaning up files: {str(e)}")


def delete_all_united_files(common_name: str, orchestrator, suffixes) -> NoReturn:
    file_path = orchestrator.configuration.components.pipeline_executor["folder_path"] + "/" + common_name
    [os.remove(file_path + suffix) and delete_from_db(common_name, orchestrator, suffix) for suffix in suffixes if
     os.path.exists(file_path + suffix)]


def determine_part(file_name: str, suffixes) -> str:
    return next((suffix for suffix in suffixes if suffix in file_name), "unknown_part")


def get_file_name(src_path) -> str:
    return os.path.basename(src_path.replace('\\', '/'))


@Inject("AppConfig")
def get_united_name(file_name: str) -> str:
    suffixes = container.inject_dependencies(get_united_name).sender["file_invoker"]["suffixes"]
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


@Inject("DataBase")
def process_by_existence(common_name: str) -> NoReturn:
    database = container.inject_dependencies(process_by_existence)
    with db_lock:
        exists_in_db = database.fetch(database_name="redis", key=common_name)
        if exists_in_db is not None:
            fetch(common_name)
        else:
            store(common_name)
