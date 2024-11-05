import logging
import os
from threading import Lock
from typing import NoReturn, List

db_lock = Lock()

logger = logging.getLogger(name="finals_logger")


def delete_from_db(orchestrator, common_name: str, suffix: str) -> NoReturn:
    try:
        orchestrator.database.db_instance.get(common_name) and orchestrator.database.delete(key=common_name)
        logger.info(f"Cleaned up {common_name + suffix}")
    except Exception as e:
        logger.error(f"Error cleaning up files: {str(e)}")


def delete_all_united_files(common_name: str, orchestrator, suffixes) -> NoReturn:
    file_path = orchestrator.configuration.components.pipeline_executor["folder_path"] + "/" + common_name
    [os.remove(file_path + suffix) and delete_from_db(common_name, orchestrator, suffix) for suffix in suffixes if
     os.path.exists(file_path + suffix)]


def determine_part(file_name: str, suffixes) -> str:
    return next((suffix for suffix in suffixes if suffix in file_name), "unknown_part")


def get_file_name(event) -> str:
    return os.path.basename(event.replace('\\', '/'))


def get_united_name(file_name: str, suffixes: List[str]) -> str:
    common_name = file_name.replace(next((suffix for suffix in suffixes if suffix in file_name), ""), "") \
        .replace(".jpg", "")
    return common_name


fetch = lambda orchestrator, common_name, suffix: (
    orchestrator.sender.send_request(orchestrator.configuration.components.sender["api_url"],
                                     orchestrator.configuration.components.pipeline_executor["folder_path"],
                                     common_name),
    delete_all_united_files(common_name, orchestrator)
)

store = lambda orchestrator, common_name, suffix: (
    orchestrator.database.store(kwargs={"key": common_name,
                                        "expiry": orchestrator.configuration.components.pipeline_executor[
                                            "expiry_delay"],
                                        "value": f"{orchestrator.configuration.components.pipeline_executor['folder_path']}/{common_name}{suffix}"}),
)


def scan_existing_files(orchestrator) -> NoReturn:
    folder_path = orchestrator.configuration.components.pipeline_executor["folder_path"]

    def is_valid_file(file_name: str) -> bool:
        fpath = os.path.join(folder_path, file_name)
        if os.path.isfile(fpath):
            return True
        else:
            logger.warning(f"File failed filter (not a file): {file_path}")
            return False

    valid_files = filter(is_valid_file, os.listdir(folder_path))

    for valid_file in valid_files:
        file_path = os.path.join(folder_path, valid_file).replace("\\", "/")
        logger.info(f"Processing file: {file_path}")
        orchestrator.pipeline_executor.strategy_pool.pool.submit(orchestrator.pipeline_executor.process,
                                                                 kwargs={'event_type': None, 'src_path': file_path})


def process_by_existence(orchestrator, common_name: str, suffix: str) -> NoReturn:
    with db_lock:
        exists_in_db = orchestrator.database.db_instance.get(common_name)
        if exists_in_db is not None:
            fetch(orchestrator, common_name, suffix)
        else:
            store(orchestrator, common_name, suffix)
