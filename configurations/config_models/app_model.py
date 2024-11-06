import logging
from dataclasses import dataclass, is_dataclass, fields
from typing import Type, Dict, Any

from pydantic.types import T

from src.utils.annotations import Service



@dataclass
class Singleton:
    _instance = None

    def __new__(cls: Type["Singleton"], *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@Service
@dataclass
class AppConfig(Singleton):
    receivers: Dict[str, Any]
    databases: Dict[str, Any]
    sender: Dict[str, Any]
    pipeline: Dict[str, Any]

    @staticmethod
    def from_dict(data: dict, cls: Type[T]) -> Type[T]:
        if not is_dataclass(cls):
            raise ValueError(f"{cls} is not a dataclass type")

        kwargs = {
            f.name: (AppConfig.from_dict(data[f.name], f.type) if is_dataclass(f.type) else data[f.name])
            for f in fields(cls)
        }

        return cls(**kwargs)
