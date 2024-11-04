import atexit
import logging
from typing import NoReturn

from watchdog.observers import Observer

from src.receiver.data_sources_handlers.data_source_handler_template import DataSourceHandlerTemplate

prod_logger = logging.getLogger("production")
dev_logger = logging.getLogger("development")


class FileDataSourceHandler(DataSourceHandlerTemplate):
    def __init__(self, folder_to_monitor):
        super().__init__()
        self.folder_to_monitor = folder_to_monitor
        self.observer = Observer()
        self.observer.schedule(self.fetch_data, folder_to_monitor, recursive=False)
        atexit.register(self.shutdown_observer)

    def fetch_data(self):
        super().get_strategy_pool().pool.submit(self.pipeline_executor.process,
                                                         kwargs={})
        return {"data": "sample file data"}

    def start_observer(self) -> NoReturn:
        try:
            self.observer.start()
            self.observer.join()
        except KeyboardInterrupt:
            self.observer.stop()
            dev_logger.info("Monitoring stopped due to user interruption.")
        except Exception as e:
            self.observer.stop()
            prod_logger.error(str(e))

    def shutdown_observer(self, observer):
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            dev_logger.info("Observer has been shut down cleanly.")
