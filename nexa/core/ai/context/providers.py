from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseContextProvider(ABC):
    """Abstract base class for all Context Providers."""
    @abstractmethod
    def provide(self, cwd: str, **kwargs) -> str:
        pass

class GitContextProvider(BaseContextProvider):
    """Provides deep context about Git status and diffs."""
    def provide(self, cwd: str, **kwargs) -> str:
        from nexa.core.agent.tools.knowledge.git import GitTool
        tool = GitTool(cwd)
        
        status = tool.status()
        diff = tool.diff()
        branch = tool.current_branch()
        
        context = (
            f"--- GIT CONTEXT ---\n"
            f"Branch: {branch}\n\n"
            f"[GIT STATUS]\n{status}\n\n"
            f"[GIT DIFF]\n{diff}\n"
            f"-------------------\n"
        )
        return context

class ProjectContextProvider(BaseContextProvider):
    """Provides deep context about project structure."""
    def provide(self, cwd: str, **kwargs) -> str:
        from nexa.core.agent.workspace import WorkspaceManager
        # We can extract more structure here using FileTool tree
        return "--- PROJECT CONTEXT ---\n(Tree injection to be implemented)\n-------------------\n"

class LogContextProvider(BaseContextProvider):
    """Provides deep context about recent errors or logs."""
    def provide(self, cwd: str, **kwargs) -> str:
        return "--- LOG CONTEXT ---\n(Log parsing to be implemented)\n-------------------\n"
