from abc import ABC
from typing import NoReturn

from configurations.developer_config import SerializableType


class AbstractDbTemplate(ABC):
    def fetch(self, key: SerializableType) -> SerializableType:
        raise NotImplementedError

    def write(self, **kwargs) -> NoReturn:
        raise NotImplementedError

    def delete(self, key: SerializableType) -> NoReturn:
        raise NotImplementedError

    def exists(self, key: SerializableType) -> bool:
        raise NotImplementedError
