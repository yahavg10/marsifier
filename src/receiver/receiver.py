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
    def __init__(self, data_handler):
        self.data_handler = data_handler
        self._observers = []

    def register_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def notify_observers(self, data):
        for observer in self._observers:
            observer.update(data)

    def receive_data(self):
        data = self.data_handler.fetch_data()
        print("Receiver: Data received:", data)
        self.notify_observers(data)  # Notify all observers when new data is received
