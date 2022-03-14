from abc import ABC, abstractmethod
from typing import Any, List


class LoxCallable(ABC):
    @abstractmethod
    def call(interpreter, arguments: List[Any]):
        ...

    @abstractmethod
    def arity() -> int:
        ...
