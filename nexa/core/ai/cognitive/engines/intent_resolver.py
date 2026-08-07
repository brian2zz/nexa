"""
IntentResolver — Tahap 1: Resolusi Intent ke Need[]

Rule Engine murni (tanpa LLM). Menganalisis user_goal dengan regex
dan mengembalikan daftar Need yang semantik.

Filosofi: "IntentResolver tidak tahu ada tool bernama 'git_status'.
           Ia hanya tahu bahwa user membutuhkan REPOSITORY_STATUS."
"""

import re
from typing import List
from nexa.core.ai.knowledge.need import Need


class IntentResolver:
    """
    Menganalisis User Goal menggunakan heuristic + regex.
    Mengembalikan Need[] — bukan tools, bukan capabilities string.
    """

    # Mapping: (regex_pattern, [Need, ...])
    # Urutan rule penting: yang lebih spesifik di atas.
    RULES = [
        # --- Git ---
        (r"(?i)\b(commit|push|pull|merge|rebase|branch|stash)\b",
            [Need.REPOSITORY_STATUS, Need.CODE_DIFF, Need.GIT_HISTORY, Need.CURRENT_BRANCH]),

        (r"(?i)\b(status|perubahan apa|apa yang berubah|diff)\b",
            [Need.REPOSITORY_STATUS, Need.CODE_DIFF]),

        # --- Frontend / Template ---
        (r"(?i)\b(template|html|tampilan|halaman|page|view|rubah.*warna|ganti.*warna|warna.*button|button.*warna|btn-\w+)\b",
            [Need.TEMPLATE_LOOKUP, Need.CSS_INSPECTION]),

        (r"(?i)\b(css|style|class|bootstrap|btn|tombol|button)\b",
            [Need.CSS_INSPECTION, Need.TEMPLATE_LOOKUP]),

        (r"(?i)\b(static|asset|javascript|js|css file|image|img)\b",
            [Need.STATIC_ASSETS, Need.FILE_LOOKUP]),

        # --- Code Intelligence ---
        (r"(?i)\b(apa fungsi|bagaimana kerja|jelaskan|fungsi|class|method|metode|def |function)\b",
            [Need.SYMBOL_DEFINITION, Need.CONTENT_SEARCH]),

        (r"(?i)\b(cari|temukan|search|find|grep|dimana|where is)\b",
            [Need.CONTENT_SEARCH, Need.FILE_LOOKUP]),

        # --- File System ---
        (r"(?i)\b(baca|lihat|tampilkan|open|read|isi file|konten)\b.*\b(file|berkas)\b",
            [Need.FILE_CONTENT, Need.FILE_LOOKUP]),

        (r"(?i)\b(struktur|directory|folder|tree)\b",
            [Need.PROJECT_STRUCTURE]),

        # --- Database / Model ---
        (r"(?i)\b(model|database|db|migration|migrate|schema|table)\b",
            [Need.MODEL_DEFINITION, Need.MIGRATION_STATUS]),

        # --- Error / Bug ---
        (r"(?i)\b(error|bug|rusak|gagal|fix|perbaiki|masalah|issue|crash)\b",
            [Need.SYMBOL_DEFINITION, Need.CONTENT_SEARCH, Need.FILE_LOOKUP]),
    ]

    # Needs yang selalu disertakan sebagai fallback minimal
    FALLBACK_NEEDS = [Need.CONTENT_SEARCH, Need.FILE_LOOKUP]

    def resolve(self, user_goal: str) -> List[Need]:
        """
        Mengembalikan daftar Need yang unik dan relevan berdasarkan goal.
        """
        needs: set = set()

        for pattern, matched_needs in self.RULES:
            if re.search(pattern, user_goal):
                needs.update(matched_needs)

        # Sertakan Need yang sudah eksplisit disebutkan via path hints
        if re.search(r'modules?/|templates?/|\.html\b', user_goal):
            needs.add(Need.FILE_CONTENT)
            needs.add(Need.TEMPLATE_LOOKUP)

        # Fallback jika tidak ada rule yang cocok
        if not needs:
            needs.update(self.FALLBACK_NEEDS)

        return list(needs)
