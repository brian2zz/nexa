from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from nexa.core.models.enums import Status, Operation, RiskLevel, SearchStrategy

@dataclass
class PatchAnalysis:
    risk_level: RiskLevel
    risk_score: int
    risk_factors: List[str] = field(default_factory=list)
    needs_human_approval: bool = False

@dataclass
class PatchObject:
    path: str
    operation: Operation
    old_hash: Optional[str] = None
    new_hash: Optional[str] = None
    old_content: Optional[str] = None
    new_content: Optional[str] = None
    diff: Optional[str] = None
    summary: str = ""
    warnings: List[str] = field(default_factory=list)

@dataclass
class PatchResult:
    success: bool
    status: Status
    patches: List[PatchObject] = field(default_factory=list)
    analysis: Optional[PatchAnalysis] = None
    summary: str = ""
    additions: int = 0
    deletions: int = 0
    warnings: List[str] = field(default_factory=list)

@dataclass
class PatchRequest:
    # Menggunakan Dict sementara untuk TransformationResult agar tidak circular import.
    # Nanti sebaiknya membuat TransformationResult dataclass di dto/transformation.py
    transformation_result: Dict[str, Any]
    repository_root: str
    target_files: List[str]
    search_strategy: SearchStrategy = SearchStrategy.EXACT
