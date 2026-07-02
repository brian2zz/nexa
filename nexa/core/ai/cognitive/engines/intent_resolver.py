import re
from typing import List

class IntentResolver:
    """
    Tahap 1: Menganalisis User Goal menggunakan heuristic dasar (Rule Engine).
    Tidak menggunakan LLM. Mengembalikan daftar 'capabilities' yang dibutuhkan.
    """
    def __init__(self):
        # Mapping dari keyword/regex ke daftar capabilities
        self.rules = [
            (r"(?i)\b(commit|git|push|pull|branch|merge)\b", ["git_status", "git_diff", "git_execute", "git_log"]),
            (r"(?i)\b(baca|lihat|tampilkan|open|read)\b.*\b(file|berkas)\b", ["read_file", "file_lookup", "view_file"]),
            (r"(?i)\b(apa fungsi|apa itu|bagaimana kerja|jelaskan|fungsi|class|metode|method)\b", ["read_symbol", "semantic_search", "content_search"]),
            (r"(?i)\b(cari|temukan|search|find)\b", ["content_search", "search_code", "find_file"]),
            (r"(?i)\b(error|bug|rusak|gagal|fix|perbaiki)\b", ["read_symbol", "content_search", "file_lookup", "read_file", "semantic_search"]),
        ]
        
    def resolve(self, user_goal: str) -> List[str]:
        """
        Mengembalikan daftar unik capability yang relevan berdasarkan goal.
        """
        capabilities = set()
        
        for pattern, caps in self.rules:
            if re.search(pattern, user_goal):
                capabilities.update(caps)
                
        # Fallback if no specific intent matched
        if not capabilities:
            # We assume general coding task: needs symbols, files, and content search
            capabilities.update(["read_symbol", "semantic_search", "file_lookup", "read_file", "content_search"])
            
        return list(capabilities)
