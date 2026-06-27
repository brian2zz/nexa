from typing import List
from .models import KnowledgeFile

class RankingManager:
    """
    Sorts files based on their assigned score.
    """
    def rank(self, files: List[KnowledgeFile]) -> List[KnowledgeFile]:
        # Sort descending by score
        return sorted(files, key=lambda f: f.score, reverse=True)
