import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class TechnicalDebt:
    severity: str
    file: str
    issue: str

@dataclass
class Recommendation:
    priority: str
    description: str

@dataclass
class ProviderMetadata:
    name: str = "Unknown"
    model: str = "Unknown"
    temperature: float = 0.0
    latency_sec: float = 0.0
    estimated_tokens: int = 0

@dataclass
class AnalysisReport:
    summary: str = ""
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    technical_debt: List[TechnicalDebt] = field(default_factory=list)
    recommendations: List[Recommendation] = field(default_factory=list)
    
    # Scores (1-10)
    architecture_score: int = 0
    security_score: int = 0
    performance_score: int = 0
    maintainability_score: int = 0
    testing_score: int = 0
    documentation_score: int = 0
    
    next_steps: List[str] = field(default_factory=list)
    confidence: str = "Medium"
    
    # Versions
    prompt_version: str = "v1.0"
    knowledge_version: str = "v2.3.1"
    
    provider_metadata: ProviderMetadata = field(default_factory=ProviderMetadata)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
        
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
        
    def to_markdown(self) -> str:
        md = f"# Project Analysis Report\n\n"
        md += f"**Confidence:** {self.confidence} | **Provider:** {self.provider_metadata.name} ({self.provider_metadata.model})\n\n"
        md += f"## Summary\n{self.summary}\n\n"
        
        md += "## Scores\n"
        md += f"- Architecture: {self.architecture_score}/10\n"
        md += f"- Security: {self.security_score}/10\n"
        md += f"- Performance: {self.performance_score}/10\n"
        md += f"- Maintainability: {self.maintainability_score}/10\n"
        md += f"- Testing: {self.testing_score}/10\n"
        md += f"- Documentation: {self.documentation_score}/10\n\n"
        
        md += "## Strengths\n" + "\n".join([f"- {s}" for s in self.strengths]) + "\n\n"
        md += "## Weaknesses\n" + "\n".join([f"- {w}" for w in self.weaknesses]) + "\n\n"
        
        md += "## Technical Debt\n"
        for t in self.technical_debt:
            md += f"- [{t.severity.upper()}] **{t.file}**: {t.issue}\n"
        md += "\n"
        
        md += "## Recommendations\n"
        for r in self.recommendations:
            md += f"- [{r.priority.upper()}] {r.description}\n"
        md += "\n"
        
        md += "## Next Steps\n" + "\n".join([f"- {n}" for n in self.next_steps]) + "\n"
        return md
        
    def to_text(self) -> str:
        txt = "=== ANALYSIS REPORT ===\n"
        txt += f"Summary: {self.summary}\n"
        txt += f"Scores -> Arch: {self.architecture_score}, Sec: {self.security_score}, Perf: {self.performance_score}, Maint: {self.maintainability_score}\n"
        txt += f"Tech Debt: {len(self.technical_debt)} issues found.\n"
        txt += f"Recommendations: {len(self.recommendations)} provided.\n"
        return txt

    def to_html(self) -> str:
        html = f"<html><body><h1>Project Analysis Report</h1>"
        html += f"<p><b>Confidence:</b> {self.confidence} | <b>Provider:</b> {self.provider_metadata.name}</p>"
        html += f"<h2>Summary</h2><p>{self.summary}</p>"
        html += "<h2>Scores</h2><ul>"
        html += f"<li>Architecture: {self.architecture_score}</li>"
        html += f"<li>Security: {self.security_score}</li>"
        html += f"<li>Performance: {self.performance_score}</li>"
        html += f"<li>Maintainability: {self.maintainability_score}</li>"
        html += f"<li>Testing: {self.testing_score}</li>"
        html += f"<li>Documentation: {self.documentation_score}</li>"
        html += "</ul></body></html>"
        return html

@dataclass
class AnalysisResult:
    success: bool
    report: Optional[AnalysisReport] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    raw_response: str = ""

@dataclass
class AnalysisSession:
    report: AnalysisReport
    knowledge_context: Any # KnowledgeContext from knowledge engine
    prompt_messages: List[Dict[str, str]]
    provider_metadata: ProviderMetadata
    raw_response: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "report": self.report.to_dict(),
            # Exclude full context and prompt from dump to avoid massive files, just keep metadata
            "provider_metadata": asdict(self.provider_metadata),
            "raw_response": self.raw_response
        }
