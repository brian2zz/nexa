from typing import List, Dict, Any
import json
from nexa.core.ai.cognitive.schema import HypothesisResult, EvidenceContext, Evidence
from nexa.core.agent.tools.registry import ToolRegistry
from nexa.core.agent.tools.knowledge import register_knowledge_tools

class KnowledgeAcquisitionEngine:
    """
    Tahap 3: Deterministic Knowledge Acquisition.
    Tidak menggunakan LLM. Langsung mengeksekusi tool berdasarkan search_targets.
    """
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.registry = ToolRegistry()
        register_knowledge_tools(self.registry, self.workspace_path)
        
    def gather(self, hypothesis_result: HypothesisResult) -> EvidenceContext:
        context = EvidenceContext()
        
        # Rank hypotheses (get top 2)
        sorted_hyps = sorted(hypothesis_result.hypotheses, key=lambda x: x.confidence, reverse=True)
        top_hyps = sorted_hyps[:2]
        
        for hyp in top_hyps:
            for target in hyp.search_targets:
                evidence = Evidence(target=target, found=False, content="")
                
                try:
                    if target.type == "symbol":
                        result = self.registry.execute("read_symbol", {"symbol_name": target.query})
                        
                        # Parsing JSON if valid
                        if isinstance(result, str) and result.startswith("["):
                            parsed = json.loads(result)
                            if parsed:
                                evidence.found = True
                                evidence.source_file = parsed[0].get("file", "")
                                evidence.start_line = parsed[0].get("lines", [0,0])[0]
                                evidence.end_line = parsed[0].get("lines", [0,0])[1]
                                evidence.content = parsed[0].get("code", "")
                        else:
                            evidence.content = str(result)
                            
                    elif target.type == "file":
                        result = self.registry.execute("file_read", {"filepath": target.query})
                        if "Error" not in result:
                            evidence.found = True
                            evidence.source_file = target.query
                            # Trim content if too long
                            if len(result) > 5000:
                                evidence.content = result[:5000] + "\n...[TRUNCATED]"
                            else:
                                evidence.content = result
                        else:
                            evidence.content = result
                            
                    elif target.type == "content":
                        result = self.registry.execute("content_search", {"query": target.query, "path": "."})
                        evidence.found = True if result and "No files found" not in result else False
                        evidence.content = str(result)[:3000]
                        
                except Exception as e:
                    evidence.content = f"Failed to acquire evidence: {e}"
                    
                context.evidences.append(evidence)
                
        return context
