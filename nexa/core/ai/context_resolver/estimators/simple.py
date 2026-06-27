import math
from .base import TokenEstimator

class SimpleTokenEstimator(TokenEstimator):
    """
    V1 Token Estimator using rule-of-thumb: 1 token ≈ 4 characters.
    """
    def estimate(self, text: str) -> int:
        if not text:
            return 0
        return math.ceil(len(text) / 4)
