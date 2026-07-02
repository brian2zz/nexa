import json
from nexa.core.ai.providers.factory import ProviderFactory
from nexa.core.ai.cognitive.schema import EvidenceContext, ReasoningResult

class ReasoningEngine:
    """
    Tahap 4: Reasoning Engine.
    Menerima EvidenceContext dan merumuskan Root Cause.
    """
    def __init__(self):
        self.provider = ProviderFactory.create()
        
    def analyze(self, evidence_context: EvidenceContext, user_goal: str) -> ReasoningResult:
        sys_prompt = (
            "You are the Nexa Reasoning Engine.\n"
            "Your task is to analyze the provided Evidence gathered from the codebase and deduce the Root Cause of the user's issue.\n"
            "If the user is asking to build a feature, deduce where and how the feature should integrate with the evidence.\n"
            "You MUST output STRICT JSON matching this schema exactly:\n"
            "{\n"
            "  \"root_cause\": \"string (Deep analysis of what is actually happening based on the evidence)\",\n"
            "  \"evidence_trail\": [\"string (e.g. 'supplierView.py (line 82) -> requestAjax() does not return X')\"],\n"
            "  \"contradictions_found\": boolean (true if evidence contradicts the initial assumption),\n"
            "  \"confidence\": integer (0-100)\n"
            "}\n"
            "CRITICAL: DO NOT output any planning steps. ONLY deduction and reasoning. ONLY JSON."
        )
        
        evidence_str = ""
        for i, ev in enumerate(evidence_context.evidences):
            evidence_str += f"--- Evidence {i+1} ---\n"
            evidence_str += f"Target: {ev.target.type} = {ev.target.query}\n"
            evidence_str += f"Found: {ev.found}\n"
            evidence_str += f"Source: {ev.source_file} (Lines {ev.start_line}-{ev.end_line})\n"
            evidence_str += f"Content:\n{ev.content}\n\n"
            
        prompt = f"User Goal: {user_goal}\n\nEvidence Gathered:\n{evidence_str}"
        
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt}
        ]
        
        raw_resp = self.provider.generate(messages, tools=[])
        content = raw_resp.get("content", "") if isinstance(raw_resp, dict) else str(raw_resp)
        
        # Parse JSON
        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
                
            data = json.loads(content)
            return ReasoningResult(
                root_cause=data.get("root_cause", ""),
                evidence_trail=data.get("evidence_trail", []),
                contradictions_found=data.get("contradictions_found", False),
                confidence=data.get("confidence", 0)
            )
        except Exception as e:
            return ReasoningResult(
                root_cause=f"Reasoning failed due to parsing error: {e}\nRaw Content:\n{content}",
                evidence_trail=[],
                contradictions_found=False,
                confidence=0
            )
