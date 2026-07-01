from abc import ABC, abstractmethod
from typing import List
from nexa.core.agent.tools.models import ToolMetadata

class BasePriorityStrategy(ABC):
    """
    Abstract base class for tool prioritization strategies.
    """
    @abstractmethod
    def sort_tools(self, tools: List[ToolMetadata]) -> List[ToolMetadata]:
        pass

class CheapestFirst(BasePriorityStrategy):
    """
    Prioritizes tools with the lowest cost.
    """
    def sort_tools(self, tools: List[ToolMetadata]) -> List[ToolMetadata]:
        return sorted(tools, key=lambda t: (t.cost, -t.priority))

class FastestFirst(BasePriorityStrategy):
    """
    Prioritizes tools with the fastest latency.
    """
    def sort_tools(self, tools: List[ToolMetadata]) -> List[ToolMetadata]:
        latency_map = {"fast": 1, "medium": 2, "slow": 3}
        return sorted(tools, key=lambda t: (latency_map.get(t.latency, 4), -t.priority))

class Balanced(BasePriorityStrategy):
    """
    Balances cost and latency. 
    """
    def sort_tools(self, tools: List[ToolMetadata]) -> List[ToolMetadata]:
        latency_map = {"fast": 1, "medium": 2, "slow": 3}
        # Example balanced score: cost * latency_weight
        return sorted(tools, key=lambda t: ((t.cost + 1) * latency_map.get(t.latency, 4), -t.priority))
