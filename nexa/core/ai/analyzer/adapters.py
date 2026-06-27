from typing import Dict, Any
from .schema import TechnicalDebt, Recommendation, AnalysisReport

class StaticAdapter:
    def adapt(self, raw_data: Dict[str, Any], report: AnalysisReport):
        # Maps raw static analysis data into report
        # Mock implementation for V1
        report.architecture_score = raw_data.get("architecture_score", 0)
        report.maintainability_score = raw_data.get("maintainability_score", 0)

class KnowledgeAdapter:
    def adapt(self, knowledge_context: Any, report: AnalysisReport):
        # Maps Knowledge Engine metrics into report
        report.knowledge_version = "v2.3.1"
        report.summary += f"\nAnalyzed {knowledge_context.metrics.selected_files} files with compression ratio of {knowledge_context.metrics.compression_ratio:.1f}%."

class AIAdapter:
    def adapt(self, ai_parsed_json: Dict[str, Any], report: AnalysisReport):
        # Maps AI JSON response to report fields
        report.summary = ai_parsed_json.get("summary", report.summary)
        report.strengths = ai_parsed_json.get("strengths", [])
        report.weaknesses = ai_parsed_json.get("weaknesses", [])
        report.next_steps = ai_parsed_json.get("next_steps", [])
        report.confidence = ai_parsed_json.get("confidence", "Medium")
        
        # Override scores if AI provided them
        scores = ai_parsed_json.get("scores", {})
        if "architecture" in scores: report.architecture_score = scores["architecture"]
        if "security" in scores: report.security_score = scores["security"]
        if "performance" in scores: report.performance_score = scores["performance"]
        if "maintainability" in scores: report.maintainability_score = scores["maintainability"]
        if "testing" in scores: report.testing_score = scores["testing"]
        if "documentation" in scores: report.documentation_score = scores["documentation"]
        
        # Technical Debt
        for td in ai_parsed_json.get("technical_debt", []):
            report.technical_debt.append(TechnicalDebt(
                severity=td.get("severity", "medium"),
                file=td.get("file", "unknown"),
                issue=td.get("issue", "unknown")
            ))
            
        # Recommendations
        for rec in ai_parsed_json.get("recommendations", []):
            report.recommendations.append(Recommendation(
                priority=rec.get("priority", "medium"),
                description=rec.get("description", "")
            ))
