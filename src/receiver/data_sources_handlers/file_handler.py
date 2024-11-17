import atexit
import logging
import os
from threading import Timer
from typing import NoReturn

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from configurations.developer_config import container, strategy_pool
from src.pipeline_runner.pipeline_runner import PipelineRunner
from src.receiver.data_sources_handlers.data_source_handler import DataSourceHandler
from src.utils.annotations import Inject

logger = logging.getLogger(os.getenv("ENV"))


class FileDataSourceHandler(DataSourceHandler, FileSystemEventHandler):
    def __init__(self, folder_to_monitor: str, file_age_limit: int) -> NoReturn:
        super().__init__()
        container.register_class(self)
        self.folder_to_monitor = folder_to_monitor
        self.file_age_limit = file_age_limit
        self.observer = Observer()
        self.observer.schedule(self, folder_to_monitor, recursive=False)
        atexit.register(self.stop)

    def start(self) -> NoReturn:
        try:
            scan_existing_files = container.get_service("scan_existing_files")
            delete_old_files = container.get_service("delete_old_files")
            scan_existing_files()
            Timer(self.file_age_limit, delete_old_files).start()
            self.observer.start()
            self.observer.join()
        except KeyboardInterrupt:
            self.observer.stop()
            logger.info("Monitoring stopped due to user interruption.")
        except Exception as e:
            self.observer.stop()
            logger.error(str(e))

    def stop(self) -> NoReturn:
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            logger.info("Observer has been shut down cleanly.")

    @Inject("PipelineRunner")
    def on_closed(self, pipeline: PipelineRunner, event) -> NoReturn:
        strategy_pool.pool.submit(pipeline.run_pipeline,
                                  data=event.src_path)