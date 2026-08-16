import re
import json
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from nexa.core.ai.providers.factory import ProviderFactory


@dataclass
class ClarificationQuestion:
    key: str          # Identifier: "file_path", "component_name", dll.
    question: str     # Teks pertanyaan yang ditampilkan ke user
    hint: str = ""    # Contoh atau petunjuk jawaban


@dataclass
class ClarificationResult:
    needs_clarification: bool
    questions: List[ClarificationQuestion] = field(default_factory=list)
    enriched_goal: str = ""   # user_goal yang sudah diperkaya dengan jawaban


class ClarificationEngine:
    """
    Mendeteksi ambiguitas dalam user_goal dan HANYA mengajukan pertanyaan
    jika prompt benar-benar underspecified / ambigu (seperti sistem Antigravity).
    Jika prompt sudah jelas, terperinci, atau memiliki context teknis yang cukup,
    engine ini otomatis melewatinya tanpa mengganggu user.
    """

    def is_prompt_self_contained(self, user_goal: str) -> bool:
        """
        Cek apakah prompt sudah cukup detail dan mandiri sehingga TIDAK butuh klarifikasi.
        """
        clean = user_goal.strip()
        words = clean.split()
        
        # 1. Prompt panjang/detail (> 25 kata) hampir selalu memiliki spesifikasi cukup
        if len(words) >= 25:
            return True

        # 2. Prompt terstruktur (mengandung markdown list, bullet points, headers, atau skema DB)
        if re.search(r"(###|\d+\.\s+\*\*|(?m)^\s*-\s+|table\s+|schema|column|database)", clean, re.IGNORECASE):
            return True

        # 3. Prompt yang eksplisit menyebutkan file path / namespace / extension
        if re.search(r"(\.php|\.py|\.dart|\.js|\.ts|\.json|\.html|\.css|app/|src/|routes/|models/|controllers/)", clean, re.IGNORECASE):
            return True

        # 4. Prompt pertanyaan investigasi ('dimana', 'bagaimana', 'kenapa', 'cari', 'search', 'find')
        if re.search(r"\b(dimana|di mana|bagaimana|kenapa|mengapa|cari|search|find|list|show|cek|check|jelaskan|explain)\b", clean, re.IGNORECASE):
            return True

        return False

    def evaluate(self, user_goal: str) -> ClarificationResult:
        """
        Evaluasi apakah user_goal membutuhkan klarifikasi.
        Menganalisis prompt terlebih dahulu sebelum memutuskan bertanya.
        """
        # Jika prompt sudah jelas & detail, jangan tanya apapun
        if self.is_prompt_self_contained(user_goal):
            return ClarificationResult(
                needs_clarification=False,
                questions=[],
                enriched_goal=user_goal
            )

        # Jika prompt sangat pendek (misal: "bikin tombol", "ubah modul", "tambah fitur"),
        # tanyakan secara cerdas & kontekstual menggunakan LLM atau rule terarah
        goal_lower = user_goal.lower()
        
        # Coba evaluasi menggunakan LLM cepat jika tersedia
        try:
            provider = ProviderFactory.create()
            prompt = (
                "You are an intelligent task analyzer for a software CLI agent.\n"
                "Evaluate if the user's prompt is too vague to be safely executed without knowing the target file, component, or specific requirements.\n\n"
                f"User Prompt: \"{user_goal}\"\n\n"
                "If the prompt is clear enough (or an exploration question), respond with JSON:\n"
                "{\"needs_clarification\": false, \"questions\": []}\n\n"
                "If it is EXTREMELY vague (e.g., 'ubah tombol', 'bikin modul baru', 'perbaiki error' without any context), formulate at most 1-2 concise, highly relevant questions in the user's language.\n"
                "JSON format:\n"
                "{\n"
                "  \"needs_clarification\": true,\n"
                "  \"questions\": [\n"
                "    {\"key\": \"target_scope\", \"question\": \"Pertanyaan singkat dan tepat?\", \"hint\": \"contoh petunjuk relevan\"}\n"
                "  ]\n"
                "}\n"
                "Respond ONLY with raw JSON."
            )
            raw = provider.generate([
                {"role": "system", "content": "You are a concise intent and ambiguity validator. Output strict JSON only."},
                {"role": "user", "content": prompt}
            ])
            content = (raw.get("content", "") if isinstance(raw, dict) else str(raw)).strip()
            # Clean markdown formatting if present
            if content.startswith("```"):
                content = re.sub(r"^```[a-zA-Z]*\n?", "", content)
                content = re.sub(r"\n?```$", "", content)
            
            data = json.loads(content)
            if not data.get("needs_clarification"):
                return ClarificationResult(needs_clarification=False, questions=[], enriched_goal=user_goal)
            
            questions = [
                ClarificationQuestion(
                    key=q.get("key", f"clarification_{i}"),
                    question=q.get("question", ""),
                    hint=q.get("hint", "")
                )
                for i, q in enumerate(data.get("questions", []))
                if q.get("question")
            ]
            return ClarificationResult(
                needs_clarification=len(questions) > 0,
                questions=questions,
                enriched_goal=user_goal
            )
        except Exception:
            # Fallback jika offline/LLM error: hanya tanya jika prompt < 6 kata dan ambigu
            words = goal_lower.split()
            if len(words) <= 5 and any(w in goal_lower for w in ["ubah", "ganti", "edit", "tombol", "warna"]):
                return ClarificationResult(
                    needs_clarification=True,
                    questions=[
                        ClarificationQuestion(
                            key="target_scope",
                            question="Komponen atau bagian file mana yang ingin diubah?",
                            hint="Sebutkan nama file atau deskripsi bagian yang ingin dimodifikasi"
                        )
                    ],
                    enriched_goal=user_goal
                )

        return ClarificationResult(
            needs_clarification=False,
            questions=[],
            enriched_goal=user_goal
        )

    def ask_user(self, user_goal: str) -> str:
        """
        Alur interaktif CLI: jika butuh klarifikasi, tampilkan pertanyaan yang relevan.
        """
        result = self.evaluate(user_goal)

        if not result.needs_clarification:
            return user_goal

        # Tampilkan pertanyaan klarifikasi
        YELLOW = '\033[93m'
        CYAN   = '\033[96m'
        RESET  = '\033[0m'
        BOLD   = '\033[1m'

        print(f"\n{YELLOW}╔══ Nexa membutuhkan sedikit klarifikasi ══╗{RESET}")
        print(f"{YELLOW}║{RESET} Untuk memastikan eksekusi sesuai yang Anda inginkan:")
        print(f"{YELLOW}╚{'═' * 42}╝{RESET}\n")

        answers = {}
        for i, q in enumerate(result.questions, 1):
            print(f"{BOLD}[{i}/{len(result.questions)}] {q.question}{RESET}")
            if q.hint:
                print(f"     {CYAN}Petunjuk: {q.hint}{RESET}")
            answer = input("     > ").strip()
            if answer:
                answers[q.key] = answer
            print()

        if not answers:
            # User melewatkan pertanyaan (tekan Enter saja)
            print(f"{YELLOW}[*] Melanjutkan dengan analisis mandiri...{RESET}\n")
            return user_goal

        # Gabungkan jawaban ke dalam goal yang diperkaya
        enrichment_parts = []
        for key, answer in answers.items():
            enrichment_parts.append(f"{key}: {answer}")

        enriched = (
            f"{user_goal}\n"
            f"[User Clarification]\n"
            + "\n".join(f"- {p}" for p in enrichment_parts)
        )

        print(f"{CYAN}[*] Menerapkan klarifikasi Anda. Melanjutkan ke rencana eksekusi...{RESET}\n")
        return enriched

