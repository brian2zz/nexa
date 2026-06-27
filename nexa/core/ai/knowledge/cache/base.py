from abc import ABC, abstractmethod
from typing import Any, Optional

class BaseCache(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass
