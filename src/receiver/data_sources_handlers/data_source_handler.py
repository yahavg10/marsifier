from abc import abstractmethod, ABC

from src.utils.annotations import Service


@Service
class DataSourceHandler(ABC):
    @abstractmethod
    def start(self):
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        raise NotImplementedError
