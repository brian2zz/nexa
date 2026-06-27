from typing import List
from nexa.core.ai.knowledge.engine import KnowledgeEngine

class DependencyResolver:
    """
    Expands the context by fetching connected files up to a certain depth.
    """
    def __init__(self, engine: KnowledgeEngine):
        self.engine = engine

    def resolve(self, project_path: str, files: List[str], depth: int = 1) -> List[str]:
        # Connect to KnowledgeEngine to fetch graph dependencies
        # Since KnowledgeEngine is already built (Phase 2.3), we'd query it.
        # For this skeleton, we just return the input files as a placeholder.
        return list(set(files))
