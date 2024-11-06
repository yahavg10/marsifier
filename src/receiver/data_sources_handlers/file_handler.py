import atexit
import logging

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from configurations.developer_config import container, strategy_pool
from src.receiver.data_sources_handlers.data_source_handler import DataSourceHandler
from src.utils.annotations import Inject

prod_logger = logging.getLogger("production")
dev_logger = logging.getLogger("development")


class FileDataSourceHandler(DataSourceHandler, FileSystemEventHandler):
    def __init__(self, folder_to_monitor, file_age_limit):
        super().__init__()
        container.register_class(self)
        self.folder_to_monitor = folder_to_monitor
        self.file_age_limit = file_age_limit
        self.observer = Observer()
        self.observer.schedule(self, folder_to_monitor, recursive=False)
        # Timer(file_age_limit, delete_old_files).start()
        atexit.register(self.stop)

    def start(self):
        try:
            self.observer.start()
            self.observer.join()
        except KeyboardInterrupt:
            self.observer.stop()
            dev_logger.info("Monitoring stopped due to user interruption.")
        except Exception as e:
            self.observer.stop()
            prod_logger.error(str(e))

    def stop(self):
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            dev_logger.info("Observer has been shut down cleanly.")

    @Inject("PipelineRunner")
    def on_created(self, pipeline, event):
        strategy_pool.pool.submit(pipeline.run_pipeline,
                                  data=event.src_path)
