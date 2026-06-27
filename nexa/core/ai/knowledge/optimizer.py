from abc import ABC, abstractmethod
from typing import List
from .models import KnowledgeFile

class BaseOptimizer(ABC):
    @abstractmethod
    def optimize(self, ranked_files: List[KnowledgeFile]) -> List[KnowledgeFile]:
        pass

class RuleBasedOptimizer(BaseOptimizer):
    """
    First generation 'Caveman' optimizer for context reduction.
    """
    def __init__(self, max_files: int = 9):
        self.max_files = max_files

    def optimize(self, ranked_files: List[KnowledgeFile]) -> List[KnowledgeFile]:
        """
        Takes ranked files and applies cut-off and cleanup rules.
        """
        # Cut-off to Top N files
        optimized = ranked_files[:self.max_files]
        
        # Cleanup
        for f in optimized:
            f.content = f.content.strip()
            
        return optimized
