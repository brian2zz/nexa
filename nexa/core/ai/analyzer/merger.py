from typing import Dict, Any
from .schema import AnalysisReport
from .adapters import StaticAdapter, KnowledgeAdapter, AIAdapter

class Merger:
    """
    Merges data from various sources into a unified AnalysisReport using Adapters.
    """
    def __init__(self):
        self.static_adapter = StaticAdapter()
        self.knowledge_adapter = KnowledgeAdapter()
        self.ai_adapter = AIAdapter()

    def merge(self, 
              static_data: Dict[str, Any], 
              knowledge_context: Any, 
              ai_parsed_json: Dict[str, Any], 
              provider_metadata: Any) -> AnalysisReport:
              
        report = AnalysisReport(provider_metadata=provider_metadata)
        
        self.static_adapter.adapt(static_data, report)
        self.knowledge_adapter.adapt(knowledge_context, report)
        self.ai_adapter.adapt(ai_parsed_json, report)
        
        return report
