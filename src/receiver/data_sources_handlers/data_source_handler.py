from abc import ABC, abstractmethod

from configurations.developer_config import app_config
from src.utils.pool import PoolFactory


class DataSourceHandler(ABC):
    strategy_pool = None

    def __init__(self):
        self.strategy_pool = PoolFactory.create_pool_strategy(pool_type=app_config.pool["handling_way"],
                                                              max_workers=app_config.pool["max_workers"])

    def get_strategy_pool(self):
        return self.strategy_pool

    @abstractmethod
    def handle(self, event):
        raise NotImplementedError

    @abstractmethod
    def start(self):
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        raise NotImplementedError
