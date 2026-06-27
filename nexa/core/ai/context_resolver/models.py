from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class ContextBundle:
    goal: str
    project_facts: Dict[str, str] = field(default_factory=dict)
    pinned_memory: List[Dict[str, Any]] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    snippets: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    # Quality Metrics
    estimated_tokens: int = 0
    compression_ratio: float = 0.0
    selection_method: str = "none"
    fallback_level: int = 0
    confidence: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "goal": self.goal,
            "estimated_tokens": self.estimated_tokens,
            "compression_ratio": self.compression_ratio,
            "selection_method": self.selection_method,
            "fallback_level": self.fallback_level,
            "confidence": self.confidence,
            "files": self.files,
            "snippets": self.snippets,
            "dependencies": self.dependencies
        }
