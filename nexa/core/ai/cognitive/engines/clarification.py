"""
ClarificationEngine — Tahap 0.5: Clarification Gate

Sebelum pipeline LLM berjalan, engine ini mengevaluasi apakah user_goal cukup
spesifik untuk dikerjakan dengan aman. Jika tidak, ia mengajukan pertanyaan 
yang tepat kepada user langsung di terminal.

Tujuan utama: Menggantikan halusinasi dengan dialog.

Alur:
    user_goal
        |
    [ClarificationEngine]
        |-- CLEAR  -> lanjutkan ke pipeline normal
        |-- NEEDS_CLARIFICATION -> tanya user, gabungkan jawaban, lanjutkan
"""

import re
import json
from typing import List, Optional
from dataclasses import dataclass, field


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
    Mendeteksi ambiguitas dalam user_goal dan mengajukan pertanyaan 
    yang tepat kepada user secara interaktif di terminal.
    """

    # --- Rule-based ambiguity patterns ---
    # Setiap pola memetakan kata kunci ambigu ke pertanyaan yang relevan
    AMBIGUITY_RULES = [
        {
            "pattern": r"\b(button|btn|tombol)\b",
            "context_negative": r"(btn-[a-z]+|class\s*=|<button)",  # sudah spesifik
            "key": "button_location",
            "question": "Tombol yang dimaksud ada di file/halaman mana?",
            "hint": "modules/fastpos/templates/fastpos/configuration/supplier/index.html"
        },
        {
            "pattern": r"\b(template|halaman|page|view)\b",
            "context_negative": r"(modules/|templates/|\.html)",   # sudah ada path
            "key": "template_path",
            "question": "Path atau nama file template yang ingin diubah?",
            "hint": "modules/fastpos/templates/fastpos/configuration/supplier/index.html"
        },
        {
            "pattern": r"\b(rubah|ubah|ganti|change|update|modify)\b",
            "context_negative": r"(dari\s+\w+\s+ke|from\s+\w+\s+to|btn-\w+)",
            "key": "change_detail",
            "question": "Apa tepatnya yang ingin diubah? (dari apa ke apa)",
            "hint": "dari btn-primary ke btn-success, atau dari warna merah ke hijau"
        },
        {
            "pattern": r"\b(warna|color|colour)\b",
            "context_negative": r"(btn-[a-z]+|#[0-9a-fA-F]{3,6}|rgb\()",
            "key": "color_target",
            "question": "Warna apa yang diinginkan? (nama kelas Bootstrap atau kode warna)",
            "hint": "btn-success, btn-primary, btn-danger, atau #28a745"
        },
        {
            "pattern": r"\b(module|modul|fitur|feature|component|komponen)\b",
            "context_negative": r"(modules/|nexa/|fastpos|hrm|inventory)",
            "key": "module_name",
            "question": "Module atau komponen mana yang dimaksud?",
            "hint": "fastpos, hrm, inventory, atau nama folder di bawah modules/"
        },
    ]

    def evaluate(self, user_goal: str) -> ClarificationResult:
        """
        Evaluasi apakah user_goal membutuhkan klarifikasi.
        Returns ClarificationResult.
        """
        goal_lower = user_goal.lower()
        questions_needed: List[ClarificationQuestion] = []

        for rule in self.AMBIGUITY_RULES:
            pattern = rule["pattern"]
            context_neg = rule.get("context_negative", "")

            # Cek apakah pola ambigu ditemukan
            if not re.search(pattern, goal_lower, re.IGNORECASE):
                continue

            # Cek apakah sudah ada konteks yang cukup (negative pattern)
            if context_neg and re.search(context_neg, user_goal, re.IGNORECASE):
                continue

            # Tambahkan pertanyaan jika belum ada key yang sama
            if not any(q.key == rule["key"] for q in questions_needed):
                questions_needed.append(ClarificationQuestion(
                    key=rule["key"],
                    question=rule["question"],
                    hint=rule.get("hint", "")
                ))

        return ClarificationResult(
            needs_clarification=len(questions_needed) > 0,
            questions=questions_needed,
            enriched_goal=user_goal
        )

    def ask_user(self, user_goal: str) -> str:
        """
        Alur utama: evaluasi, tanya jika perlu, kembalikan goal yang diperkaya.
        Dipanggil dari shell.py sebelum pipeline dijalankan.
        
        Returns enriched user_goal (string gabungan goal asli + jawaban user).
        """
        result = self.evaluate(user_goal)

        if not result.needs_clarification:
            return user_goal

        # Tampilkan pertanyaan klarifikasi
        YELLOW = '\033[93m'
        CYAN   = '\033[96m'
        RESET  = '\033[0m'
        BOLD   = '\033[1m'

        print(f"\n{YELLOW}╔══ Nexa membutuhkan klarifikasi ══╗{RESET}")
        print(f"{YELLOW}║{RESET} Saya menemukan beberapa informasi yang perlu diperjelas")
        print(f"{YELLOW}║{RESET} agar tidak salah mengeksekusi perintah Anda.")
        print(f"{YELLOW}╚{'═' * 35}╝{RESET}\n")

        answers = {}
        for i, q in enumerate(result.questions, 1):
            print(f"{BOLD}[{i}/{len(result.questions)}] {q.question}{RESET}")
            if q.hint:
                print(f"     {CYAN}Contoh: {q.hint}{RESET}")
            answer = input("     > ").strip()
            if answer:
                answers[q.key] = answer
            print()

        if not answers:
            # User melewatkan semua pertanyaan (tekan Enter saja)
            print(f"{YELLOW}[*] Melanjutkan dengan informasi yang tersedia...{RESET}\n")
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

        print(f"{CYAN}[*] Goal diperkaya dengan klarifikasi Anda. Melanjutkan pipeline...{RESET}\n")
        return enriched
