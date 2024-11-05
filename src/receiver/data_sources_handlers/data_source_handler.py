from abc import ABC, abstractmethod

from configurations.developer_config import container
from src.utils.annotations import Inject
from src.utils.pool import PoolFactory


class DataSourceHandler(ABC):
    strategy_pool = None

    def __init__(self):
        @Inject("AppConfig")
        def set_strategy_pool():
            app_config = container.inject_dependencies(set_strategy_pool)
            self.strategy_pool = PoolFactory.create_pool_strategy(pool_type=app_config.pool["handling_way"],
                                                                  max_workers=app_config.pool["max_workers"])
        set_strategy_pool()

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
