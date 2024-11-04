from abc import ABC, abstractmethod

from src.utils.pool import PoolFactory


class DataSourceHandler(ABC):
    def __init__(self):
        self.strategy_pool = PoolFactory.create_pool_strategy()

    def get_strategy_pool(self):
        return self.strategy_pool

    @abstractmethod
    def fetch_data(self):
        raise NotImplementedError