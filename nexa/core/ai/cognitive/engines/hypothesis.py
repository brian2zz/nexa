"""
HypothesisEngine — Tahap 2: Pembuat Hipotesis

Menerima EvidenceBundle yang sudah dikumpulkan oleh KnowledgeOrchestrator
dan menghasilkan hipotesis tentang APA yang terjadi atau APA yang perlu dilakukan.

Hipotesis di sini bersifat murni interpretatif — bukan instruksi pencarian.
Semua pencarian sudah selesai sebelum tahap ini.

Filosofi: "HypothesisEngine hanya berpikir. Ia tidak mencari."
"""

import json
from typing import List, Dict, Optional
from nexa.core.ai.providers.factory import ProviderFactory
from nexa.core.ai.knowledge.evidence import EvidenceBundle


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


class HypothesisEngine:
    """
    Tahap 2: Menghasilkan hipotesis berdasarkan Evidence yang sudah dikumpulkan.
    tools=[] SELALU kosong — engine ini hanya berpikir.
    """

    def __init__(self):
        self.provider = ProviderFactory.create()

    def generate(self, user_goal: str,
                 project_facts: Dict = None, conversation_memory: List[Dict] = None, evidence_bundle = None) -> HypothesisResult:

        sys_prompt = (
            "You are the Nexa Hypothesis Engine.\n"
            "Your task is to analyze the User Goal and generate 1-2 initial hypotheses about what needs to be changed or investigated.\n"
            "You MUST also define 'search_targets' to guide the knowledge orchestrator in finding the right files or symbols.\n\n"
            "You MUST output STRICT JSON:\n"
            "{\n"
            "  \"hypotheses\": [\n"
            "    {\n"
            "      \"id\": \"H1\",\n"
            "      \"description\": \"string — precise interpretation of what needs to happen\",\n"
            "      \"search_targets\": [\"string — e.g. file names, function names, or keywords to search for\"]\n"
            "    }\n"
            "  ]\n"
            "}\n"
            "CRITICAL RULES:\n"
            "1. Generate reasonable guesses based on common software architecture.\n"
            "2. 'search_targets' should be specific (e.g. 'auth_controller.py', 'btn-primary', 'login_user()').\n"
            "3. ONLY output JSON."
        )

        prompt = f"User Goal: {user_goal}\n"
        if evidence_bundle:
            prompt += f"\nEvidence Gathered So Far:\n{evidence_bundle.to_context_text()}"

        if project_facts:
            prompt += f"\n\nProject Facts: {json.dumps(project_facts)}"

        messages = [{"role": "system", "content": sys_prompt}]

        if conversation_memory:
            for msg in conversation_memory:
                messages.append(msg)

        messages.append({"role": "user", "content": prompt})

        raw_resp = self.provider.generate(messages, tools=[])  # tools=[] — tidak boleh memanggil tool
        content = raw_resp.get("content", "") if isinstance(raw_resp, dict) else str(raw_resp)

        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()

            data = json.loads(content)
            return HypothesisResult(hypotheses=data.get("hypotheses", []))

        except Exception as e:
            return HypothesisResult(hypotheses=[{
                "id": "H0",
                "description": f"Failed to generate hypotheses: {e}",
                "search_targets": []
            }])
