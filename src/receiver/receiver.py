from abc import ABC, abstractmethod
from typing import Dict

from injector import inject, singleton

from src.receiver.data_sources_handlers.data_source_handler import DataSourceHandler
from src.utils.annotations import Service


class Observer(ABC):
    @abstractmethod
    def update(self, data):
        raise NotImplementedError


@singleton
@Service
class Receiver:
    @inject
    def __init__(self, data_source_handlers: Dict[str, DataSourceHandler]):
        self.data_handlers = data_source_handlers

    def start(self, specific_handler_name: str = None):
        if specific_handler_name:
            self.data_handlers.get(specific_handler_name).stop()
        for data_handler in self.data_handlers.values():
            data_handler.start()

    def stop(self):
        for data_handler in self.data_handlers.values():
            data_handler.stop()

    def register_handler(self, handler_name: str, data_source_handler):
        self.data_handlers.update(handler_name, data_source_handler)

    def remove_handler(self, handler_name: str):
        self.data_handlers.pop(handler_name)
