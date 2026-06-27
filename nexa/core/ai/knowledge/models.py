from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ScannerResult:
    files: List[Dict[str, Any]] = field(default_factory=list)
    project_root: str = ""

@dataclass
class AnalyzerResult:
    framework: str = "Unknown"
    language: str = "Unknown"
    architecture: str = "Unknown"
    warnings: List[str] = field(default_factory=list)

@dataclass
class IntentContext:
    domain: str = ""
    keywords: List[str] = field(default_factory=list)

@dataclass
class FileSummary:
    purpose: str = ""
    language: str = ""
    imports: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    widgets: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

@dataclass
class KnowledgeFile:
    path: str
    language: str = "unknown"
    score: float = 0.0
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    selection_reason: List[str] = field(default_factory=list)
    summary: FileSummary = field(default_factory=FileSummary)
    tags: List[str] = field(default_factory=list)
    content: str = ""

@dataclass
class KnowledgeEdge:
    source: str
    target: str
    relation_type: str # IMPORTS, CALLS, USES, EXTENDS, IMPLEMENTS, REQUIRES

@dataclass
class KnowledgeNode:
    path: str
    dependencies: List[KnowledgeEdge] = field(default_factory=list)

@dataclass
class KnowledgeReport:
    project_files: int = 0
    selected_files: int = 0
    ignored_files: int = 0
    compression_ratio: float = 0.0
    estimated_tokens: int = 0
    largest_file: int = 0
    average_file_size: float = 0.0
    average_dependency: float = 0.0
    graph_nodes: int = 0
    graph_edges: int = 0
    coverage_percentage: float = 0.0
    processing_time_sec: float = 0.0
    cache_hit_rate: float = 0.0

@dataclass
class KnowledgeContext:
    selected_files: List[KnowledgeFile] = field(default_factory=list)
    selected_modules: List[str] = field(default_factory=list)
    dependency_graph: Dict[str, KnowledgeNode] = field(default_factory=dict)
    ranking: List[str] = field(default_factory=list)
    metrics: KnowledgeReport = field(default_factory=KnowledgeReport)
    project_name: str = ""
    framework: str = ""
    language: str = ""
