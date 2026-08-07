from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class SearchTarget:
    type: str
    query: str
    path: str = "."

@dataclass
class Evidence:
    target: SearchTarget
    found: bool
    content: str
    source_file: str = ""
    start_line: int = 0
    end_line: int = 0

@dataclass
class EvidenceContext:
    evidences: List[Evidence] = field(default_factory=list)


