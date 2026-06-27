from abc import ABC, abstractmethod

class TokenEstimator(ABC):
    @abstractmethod
    def estimate(self, text: str) -> int:
        pass
