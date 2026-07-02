import json
from typing import List, Dict, Any
from nexa.core.ai.providers.factory import ProviderFactory
from nexa.core.ai.cognitive.schema import HypothesisResult, Hypothesis, SearchTarget

class HypothesisEngine:
    """
    Tahap 2: Menghasilkan struktur data hipotesis berdasarkan Intent.
    """
    def __init__(self):
        self.provider = ProviderFactory.create()
        
    def generate(self, user_goal: str, project_facts: Dict = None, knowledge_context: str = "", conversation_memory: List[Dict] = None, capabilities: List[str] = None) -> HypothesisResult:
        sys_prompt = (
            "You are the Nexa Hypothesis Engine.\n"
            "Your task is to analyze the user's goal and generate 2-3 logical hypotheses about where the issue lies or where the feature should be built.\n"
            "You MUST output STRICT JSON matching this schema exactly:\n"
            "{\n"
            "  \"hypotheses\": [\n"
            "    {\n"
            "      \"id\": \"H1\",\n"
            "      \"description\": \"string\",\n"
            "      \"confidence\": integer (0-100),\n"
            "      \"search_targets\": [\n"
            "        {\"type\": \"symbol\", \"query\": \"function_or_class_name\"},\n"
            "        {\"type\": \"file\", \"query\": \"filename_or_path\"},\n"
            "        {\"type\": \"content\", \"query\": \"broad_search_keyword\"}\n"
            "      ]\n"
            "    }\n"
            "  ]\n"
            "}\n"
            "CRITICAL RULES:\n"
            "1. Do NOT hallucinate frameworks (e.g., React/Typescript) if the project is something else (like Django/Python). Use the Knowledge Context (Directory Tree) to understand the project structure.\n"
            "2. If you are not 100% sure of a file path, DO NOT guess the exact path or extension. Instead, use type 'content' with a broad keyword, or use type 'file' with just the base name (e.g., 'supplier' instead of 'SupplierIndex.tsx').\n"
            "3. Do NOT output anything else except the JSON object."
        )
        
        prompt = f"User Goal: {user_goal}\n"
        if project_facts:
            prompt += f"Project Facts: {json.dumps(project_facts)}\n"
        if knowledge_context:
            prompt += f"Knowledge Context (Directory Tree & Architecture):\n{knowledge_context}\n"
        if capabilities:
            prompt += f"Detected Capabilities (Use this hint to form relevant search targets): {capabilities}\n"
            
        messages = [{"role": "system", "content": sys_prompt}]
        
        if conversation_memory:
            for msg in conversation_memory:
                messages.append(msg)
                
        messages.append({"role": "user", "content": prompt})
        
        raw_resp = self.provider.generate(messages, tools=[])
        content = raw_resp.get("content", "") if isinstance(raw_resp, dict) else str(raw_resp)
        
        # Parse JSON
        try:
            # Basic cleanup if wrapped in markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
                
            data = json.loads(content)
            result = HypothesisResult()
            for h in data.get("hypotheses", []):
                targets = []
                for st in h.get("search_targets", []):
                    targets.append(SearchTarget(type=st.get("type"), query=st.get("query")))
                
                result.hypotheses.append(Hypothesis(
                    id=h.get("id", ""),
                    description=h.get("description", ""),
                    confidence=h.get("confidence", 0),
                    search_targets=targets
                ))
            return result
        except Exception as e:
            # Fallback hypothesis
            h = Hypothesis(
                id="H0", 
                description=f"Failed to generate hypotheses: {str(e)}", 
                confidence=0,
                search_targets=[]
            )
            return HypothesisResult(hypotheses=[h])
