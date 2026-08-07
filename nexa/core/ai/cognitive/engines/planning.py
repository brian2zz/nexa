import json
from nexa.core.ai.providers.factory import ProviderFactory
from nexa.core.ai.cognitive.engines.reasoning import ReasoningResult
from nexa.core.ai.planner.schema import PlanningResult, WorkItem, AcceptanceCriterion, RiskItem, ConfidenceAssessment

class PlanningEngine:
    """
    Tahap 5: Planning Engine.
    Menerima ReasoningResult dan merumuskan Execution Plan.
    """
    def __init__(self):
        self.provider = ProviderFactory.create()
        
    def build(self, reasoning: ReasoningResult, user_goal: str) -> PlanningResult:
        sys_prompt = (
            "You are the Nexa Planning Engine.\n"
            "Your task is to take a highly detailed Root Cause Analysis (Reasoning Result) and formulate an actionable Execution Plan.\n"
            "You MUST output STRICT JSON matching this schema exactly:\n"
            "{\n"
            "  \"objective\": \"string (The primary software engineering objective)\",\n"
            "  \"constraints\": [\"string\"],\n"
            "  \"work_items\": [\n"
            "    {\n"
            "      \"title\": \"string\",\n"
            "      \"description\": \"string\",\n"
            "      \"affected_files\": [\"string\"],\n"
            "      \"objective\": \"string\"\n"
            "    }\n"
            "  ],\n"
            "  \"acceptance_criteria\": [\n"
            "    {\n"
            "      \"description\": \"string\",\n"
            "      \"priority\": \"MUST|SHOULD|COULD\",\n"
            "      \"verification_method\": \"string\"\n"
            "    }\n"
            "  ],\n"
            "  \"risk_analysis\": [\n"
            "    {\n"
            "      \"category\": \"Performance|Compatibility|Security|Rollback|Business\",\n"
            "      \"probability\": \"LOW|MEDIUM|HIGH\",\n"
            "      \"impact\": \"LOW|MEDIUM|HIGH\",\n"
            "      \"mitigation\": \"string\"\n"
            "    }\n"
            "  ],\n"
            "  \"clarifications\": [\"string (Questions for the user if evidence is missing)\"]\n"
            "}\n"
            "CRITICAL RULES:\n"
            "1. Do NOT invent files. Base everything on the provided reasoning.\n"
            "2. ALL knowledge acquisition has already been completed. DO NOT schedule exploratory work items like searching, finding, or reading files. Your Execution Plan must ONLY contain concrete modifications (CREATE, MODIFY, DELETE) or verification commands (pytest, build).\n"
            "3. If essential evidence is missing (e.g., a file was not found), DO NOT invent search tasks. Instead, populate the `clarifications` array with specific questions for the user (e.g., 'File X tidak ditemukan, di mana path-nya?'). Leave work_items empty if you cannot proceed without this clarification.\n"
            "4. ONLY output JSON."
        )
        
        prompt = (
            f"User Goal: {user_goal}\n\n"
            f"Root Cause deduced by Reasoning Engine:\n{reasoning.root_cause}\n\n"
            f"Evidence Trail:\n{json.dumps(reasoning.evidence_trail)}\n\n"
            f"Please formulate the Execution Plan."
        )
        
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
            
            work_items = []
            for wi in data.get("work_items", []):
                work_items.append(WorkItem(
                    title=wi.get("title", ""),
                    description=wi.get("description", ""),
                    affected_files=wi.get("affected_files", []),
                    objective=wi.get("objective", "")
                ))
                
            ac = []
            for a in data.get("acceptance_criteria", []):
                ac.append(AcceptanceCriterion(
                    description=a.get("description", ""),
                    priority=a.get("priority", "MUST"),
                    verification_method=a.get("verification_method", "")
                ))
                
            ra = []
            for r in data.get("risk_analysis", []):
                ra.append(RiskItem(
                    category=r.get("category", "General"),
                    probability=r.get("probability", "MEDIUM"),
                    impact=r.get("impact", "MEDIUM"),
                    mitigation=r.get("mitigation", "")
                ))
                
            return PlanningResult(
                goal=user_goal,
                summary=f"Cognitive Pipeline completed. Reasoning Engine Confidence: {reasoning.confidence}%",
                objective=data.get("objective", ""),
                constraints=data.get("constraints", []),
                work_items=work_items,
                acceptance_criteria=ac,
                risk_analysis=ra,
                clarifications=data.get("clarifications", []),
                confidence=ConfidenceAssessment(level="HIGH", score=reasoning.confidence, reason="Derived from deterministic evidence trail.", missing_information="None")
            )
        except Exception as e:
            return PlanningResult(
                goal=user_goal,
                summary=f"Failed to generate Execution Plan: {e}",
                objective="Error",
                constraints=[],
                work_items=[],
                acceptance_criteria=[],
                risk_analysis=[],
                confidence=ConfidenceAssessment(level="LOW", score=0, reason="JSON parse error", missing_information="")
            )
