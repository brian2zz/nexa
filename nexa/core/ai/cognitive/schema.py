from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Hypothesis:
    id: str
    description: str
    confidence: int  # 0-100

@dataclass
class HypothesisResult:
    hypotheses: List[Hypothesis] = field(default_factory=list)

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

@dataclass
class ReasoningResult:
    root_cause: str
    evidence_trail: List[str] = field(default_factory=list)
    contradictions_found: bool = False
    confidence: int = 0
