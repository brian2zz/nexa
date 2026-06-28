from typing import List, Dict
from nexa.core.ai.memory.core import ChatMemoryManager

class ContextWindow:
    """
    Bertugas mengukur ukuran konteks (misalnya token count) 
    untuk mencegah LLM melampaui limit.
    """
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        
    def estimate_tokens(self, text: str) -> int:
        # Pendekatan kasar: 1 kata ~ 1.3 token
        return int(len(text.split()) * 1.3)
        
    def is_overflowing(self, messages: List[Dict[str, str]]) -> bool:
        total = sum(self.estimate_tokens(m['content']) for m in messages)
        return total > self.max_tokens

class SummaryBuilder:
    """
    Bertugas merangkum percakapan lama menjadi satu paragraf 
    agar riwayat tetap terjaga tanpa boros token.
    """
    def summarize(self, old_messages: List[Dict[str, str]]) -> str:
        # Secara ideal ini memanggil LLM (Prompt: "Rangkum percakapan ini...")
        # Untuk Sprint 2 (tanpa LLM yang menyala), kita menggunakan peringkasan fallback.
        summary = "Ringkasan Obrolan Sebelumnya: "
        topics = set()
        for m in old_messages:
            if "login" in m['content'].lower(): topics.add("Login")
            if "bug" in m['content'].lower(): topics.add("Bug Fixing")
            if "database" in m['content'].lower(): topics.add("Database")
            
        if topics:
            return summary + ", ".join(topics) + "."
        return summary + "Berbagai diskusi teknis."

class ConversationManager:
    """
    Menggabungkan Memory Store (SQLite), Context Window, dan Summary Builder.
    """
    def __init__(self, memory_manager: ChatMemoryManager):
        self.memory = memory_manager
        self.window = ContextWindow()
        self.summarizer = SummaryBuilder()
        
    def get_context_bundle(self, session_id: int) -> List[Dict[str, str]]:
        """
        Mengambil riwayat percakapan. Jika terlalu panjang,
        bagian lama akan dirangkum (Summary).
        """
        # Ambil 10 pesan terakhir dari database
        raw_messages = self.memory.load_session_messages(session_id, limit=10)
        
        if not raw_messages:
            return []
            
        if self.window.is_overflowing(raw_messages):
            # Pisahkan 4 pesan lama dan 6 pesan terbaru
            old_messages = raw_messages[:-6]
            recent_messages = raw_messages[-6:]
            
            summary_text = self.summarizer.summarize(old_messages)
            
            # Ganti pesan lama dengan 1 pesan summary
            bundled_messages = [{"role": "system", "content": summary_text}]
            bundled_messages.extend(recent_messages)
            
            return bundled_messages
            
        return raw_messages
