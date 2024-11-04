from abc import ABC, abstractmethod
from typing import List

from injector import inject, singleton

from src.annotations import Service
from src.receiver.data_sources_handlers.data_source_handler_template import DataSourceHandler


class Observer(ABC):
    @abstractmethod
    def update(self, data):
        raise NotImplementedError


@singleton
@Service
class Receiver:
    @inject
    def __init__(self, data_source_handlers: List[DataSourceHandler]):
        self.data_handlers = data_source_handlers

    def start(self):
        for data_handler in self.data_handlers:
            data_handler.start()

    def stop(self):
        for data_handler in self.data_handlers:
            data_handler.stop()

    def register_handler(self, data_source_handler):
        self.data_handlers.append(data_source_handler)

    def remove_handler(self, data_source_handler):
        self.data_handlers.remove(data_source_handler)
