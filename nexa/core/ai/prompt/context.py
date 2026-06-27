from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class PromptContext:
    task: str
    goal: str
    framework: str = ""
    language: str = ""
    architecture: str = ""
    statistics: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    project_health: str = "Unknown"
    risk_score: str = "Low"
    important_files: List[str] = field(default_factory=list)
    selected_files: List[Dict[str, str]] = field(default_factory=list)
    caveman_level: str = "none"
    # selected_files format: [{"path": "...", "content": "..."}]
