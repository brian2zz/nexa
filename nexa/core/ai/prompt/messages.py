from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class PromptMessages:
    messages: List[Dict[str, str]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    estimated_tokens: int = 0
    selected_files: List[str] = field(default_factory=list)
    task: str = ""
    goal: str = ""
