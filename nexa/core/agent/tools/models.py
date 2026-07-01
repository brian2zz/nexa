from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class ToolMetadata:
    """
    Metadata for a tool to be used by the ToolPrioritizer.
    """
    name: str
    cost: int
    latency: str  # e.g., "fast", "medium", "slow"
    category: str  # e.g., "git", "file", "knowledge", "search", "write"
    read_only: bool
    priority: int
    capabilities: List[str] = field(default_factory=list)
    confidence: Optional[float] = 1.0


@dataclass
class KnowledgeRequest:
    """
    A request from the Provider-Agnostic Planner to fetch context.
    The Planner doesn't need to know the tool names.
    """
    need: str # This should match a capability (e.g., 'file_lookup', 'content_search')
    intent_domain: Optional[str] = None
    parameters: Optional[dict] = None
