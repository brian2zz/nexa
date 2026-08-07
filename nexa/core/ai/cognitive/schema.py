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


class HypothesisResult:
    """Hasil interpretasi HypothesisEngine — daftar hipotesis teks."""
    def __init__(self, hypotheses: List[Dict] = None):
        self.hypotheses = hypotheses or []

    def top(self, n: int = 2) -> List[Dict]:
        sorted_h = sorted(self.hypotheses, key=lambda x: x.get("confidence", 0), reverse=True)
        return sorted_h[:n]

    def summary_text(self) -> str:
        lines = []
        for h in self.hypotheses:
            targets = ", ".join(h.get('search_targets', []))
            target_str = f" [Targets: {targets}]" if targets else ""
            lines.append(f"- [H{h.get('id','?')}] {h.get('description','')}{target_str}")
        return "\n".join(lines)


class ReasoningResult:
    """Hasil analisis ReasoningEngine."""
    def __init__(self, root_cause: str, evidence_trail: list = None,
                 contradictions_found: bool = False, confidence: int = 0):
        self.root_cause = root_cause
        self.evidence_trail = evidence_trail or []
        self.contradictions_found = contradictions_found
        self.confidence = confidence
