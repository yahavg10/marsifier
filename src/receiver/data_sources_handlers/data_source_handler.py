from abc import abstractmethod

from src.utils.pool import PoolFactory


class DataSourceHandler:
    strategy_pool = None

    def __init__(self, pool_type, max_workers):
        self.strategy_pool = PoolFactory.create_pool_strategy(pool_type, max_workers)

    def get_strategy_pool(self):
        return self.strategy_pool

    @abstractmethod
    def start(self):
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        raise NotImplementedError
