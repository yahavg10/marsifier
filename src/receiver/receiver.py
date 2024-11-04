from abc import ABC, abstractmethod

from injector import inject, singleton

from src.annotations import Service


class Observer(ABC):
    @abstractmethod
    def update(self, data):
        raise NotImplementedError


@singleton
@Service
class Receiver:
    @inject
    def __init__(self, data_source_handlers):
        self.data_handlers = data_source_handlers

    def register_observer(self, data_source_handler):
        self.data_handlers.append(data_source_handler)

    def remove_handlers(self, data_source_handler):
        self.data_handlers.remove(data_source_handler)
