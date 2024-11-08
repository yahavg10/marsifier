import logging
import os
from typing import Dict, NoReturn

from injector import singleton

from src.receiver.data_sources_handlers.data_source_handler import DataSourceHandler
from src.utils.annotations import Service

logger = logging.getLogger(os.getenv("ENV"))


@singleton
@Service
class Receiver:
    def __init__(self, data_source_handlers: Dict[str, DataSourceHandler]) -> NoReturn:
        self.data_handlers = data_source_handlers

    def start(self, specific_handler_name: str = None) -> NoReturn:
        logger.debug("started receiver")
        if specific_handler_name:
            self.data_handlers.get(specific_handler_name).stop()
        for data_handler in self.data_handlers.values():
            data_handler.start()

    def stop(self):
        for data_handler in self.data_handlers.values():
            data_handler.stop()

    def register_handler(self, handler_name: str, data_source_handler: DataSourceHandler) -> NoReturn:
        self.data_handlers.update(handler_name, data_source_handler)

    def remove_handler(self, handler_name: str) -> NoReturn:
        self.data_handlers.pop(handler_name)
