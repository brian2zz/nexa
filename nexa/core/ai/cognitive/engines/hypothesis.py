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
            lines.append(f"- [H{h.get('id','?')}] {h.get('description','')} (confidence: {h.get('confidence',0)}%)")
        return "\n".join(lines)


class HypothesisEngine:
    """
    Tahap 2: Menghasilkan hipotesis berdasarkan Evidence yang sudah dikumpulkan.
    tools=[] SELALU kosong — engine ini hanya berpikir.
    """

    def __init__(self):
        self.provider = ProviderFactory.create()

    def generate(self, user_goal: str, evidence_bundle: EvidenceBundle,
                 project_facts: Dict = None, conversation_memory: List[Dict] = None) -> HypothesisResult:

        sys_prompt = (
            "You are the Nexa Hypothesis Engine.\n"
            "You receive a User Goal and an Evidence Bundle (already gathered from the codebase).\n"
            "Your task is to analyze the evidence and generate 2-3 precise hypotheses about:\n"
            "  - What is the root issue (if debugging/fixing)\n"
            "  - Where and how to implement the change (if building/modifying)\n\n"
            "You MUST output STRICT JSON:\n"
            "{\n"
            "  \"hypotheses\": [\n"
            "    {\n"
            "      \"id\": \"H1\",\n"
            "      \"description\": \"string — precise interpretation of what needs to happen\",\n"
            "      \"confidence\": integer (0-100),\n"
            "      \"evidence_references\": [\"string — which evidence supports this\"]\n"
            "    }\n"
            "  ]\n"
            "}\n"
            "CRITICAL RULES:\n"
            "1. Base hypotheses ONLY on evidence provided. Do NOT invent.\n"
            "2. If evidence shows the file exists and has specific content, reference it precisely.\n"
            "3. If evidence is insufficient, state that in description with confidence <= 30.\n"
            "4. ONLY output JSON."
        )

        # Build prompt with evidence
        evidence_text = evidence_bundle.to_context_text()
        prompt = f"User Goal: {user_goal}\n\n{evidence_text}"

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
                "confidence": 0,
                "evidence_references": []
            }])
