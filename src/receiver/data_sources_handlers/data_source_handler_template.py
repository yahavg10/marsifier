from abc import ABC, abstractmethod


class DataSourceHandlerTemplate(ABC):
    @abstractmethod
    def fetch_data(self):
        raise NotImplementedError