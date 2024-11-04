from abc import ABC


class DataBaseHandler(ABC):
    def connect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    def fetch(self, key):
        raise NotImplementedError

    def write(self, **kwargs):
        raise NotImplementedError

    def delete(self, key: str):
        raise NotImplementedError
