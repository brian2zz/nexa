"""
Priority 2c: Hierarchical Memory Architecture

Arsitektur memori berjenjang Nexa AI:
  1. Conversation Memory  — Riwayat chat real-time (sudah ada via ChatMemoryManager)
  2. Working Memory       — Hipotesis & bukti aktif yang dikosongkan setelah task selesai
  3. Session Memory       — Rekam jejak problem-solving sepanjang sesi aktif
  4. Long-Term Memory     — Aturan arsitektur & gaya coding yang bersifat permanen (Pinned Memory)

Modul ini menyatukan keempatnya dalam satu antarmuka bersih.
"""

import os
import sqlite3
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class WorkingMemory:
    """
    Lapisan 2: Memori kerja jangka pendek.
    Menyimpan hipotesis aktif, bukti mentah, dan rootcause sementara.
    Dikosongkan (flush) setiap kali satu task selesai dieksekusi.
    TIDAK persisten ke disk — disimpan di RAM.
    """
    def __init__(self):
        self._store: Dict[str, Any] = {}

    def set(self, key: str, value: Any):
        self._store[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def flush(self):
        """Kosongkan semua memori kerja setelah task selesai."""
        self._store.clear()

    def snapshot(self) -> Dict[str, Any]:
        """Kembalikan salinan snapshot untuk disimpan ke Session Memory."""
        return dict(self._store)

    def summary_text(self) -> str:
        """Ringkasan singkat dari Working Memory untuk dijadikan input Session Memory."""
        lines = []
        for key, value in self._store.items():
            if isinstance(value, (str, int, float, bool)):
                lines.append(f"- {key}: {value}")
            elif isinstance(value, list):
                lines.append(f"- {key}: [{len(value)} items]")
        return "\n".join(lines) if lines else "(empty)"


class SessionMemory:
    """
    Lapisan 3: Rekam jejak problem-solving sepanjang sesi aktif.
    Disimpan ke SQLite dan dibersihkan saat sesi ditutup.
    """
    def __init__(self, db_path: str, session_id: int):
        self.db_path = db_path
        self.session_id = session_id
        self._init_table()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn

    def _init_table(self):
        with self._get_conn() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS session_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def record(self, event_type: str, summary: str):
        """
        Catat sebuah event ke dalam rekam jejak sesi ini.
        event_type: 'hypothesis', 'acquisition', 'reasoning', 'execution', 'error'
        """
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO session_events (session_id, event_type, summary, created_at) VALUES (?, ?, ?, ?)",
                (self.session_id, event_type, summary, datetime.datetime.now().isoformat())
            )
            conn.commit()

    def get_trail(self, limit: int = 10) -> List[Dict[str, str]]:
        """Ambil rekam jejak terbaru dari sesi ini."""
        with self._get_conn() as conn:
            cursor = conn.execute(
                "SELECT event_type, summary, created_at FROM session_events WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (self.session_id, limit)
            )
            rows = cursor.fetchall()
            return [{"event_type": r[0], "summary": r[1], "created_at": r[2]} for r in reversed(rows)]

    def format_for_context(self, limit: int = 5) -> str:
        """Format rekam jejak untuk disuntikkan sebagai konteks ke LLM."""
        trail = self.get_trail(limit)
        if not trail:
            return ""
        lines = ["[Session Trail]"]
        for event in trail:
            lines.append(f"- [{event['event_type']}] {event['summary']}")
        return "\n".join(lines)


class HierarchicalMemory:
    """
    Antarmuka tunggal yang menyatukan keempat lapisan memori Nexa AI.
    
    Penggunaan:
        memory = HierarchicalMemory(session_id=current_session_id)
        
        # Working memory (in-RAM, per-task)
        memory.working.set("hypotheses", [...])
        memory.working.flush()
        
        # Session trail (persistent per-session)
        memory.session.record("reasoning", "Root cause: missing return value")
        
        # Long-term (Pinned Memory) - delegated to PinnedMemoryManager
        memory.get_long_term_rules(project_path)
    """
    def __init__(self, session_id: int, db_path: str = None):
        if db_path is None:
            home_dir = str(Path.home())
            db_path = os.path.join(home_dir, ".nexa", "chat_memory.db")

        self.db_path = db_path
        self.session_id = session_id
        self.working = WorkingMemory()
        self.session = SessionMemory(db_path=db_path, session_id=session_id)

    def flush_working_to_session(self, goal_summary: str = ""):
        """
        Lifecycle hook: Dipanggil saat satu task selesai.
        Menyimpan snapshot Working Memory ke Session trail, lalu membersihkan Working Memory.
        """
        snapshot_text = self.working.summary_text()
        if snapshot_text and snapshot_text != "(empty)":
            summary = f"{goal_summary} | WM Snapshot: {snapshot_text[:300]}"
            self.session.record("working_memory_flush", summary)
        self.working.flush()

    def get_long_term_rules(self, project_path: str) -> List[Dict[str, Any]]:
        """Ambil aturan arsitektur permanen (Pinned Memory) untuk proyek ini."""
        from nexa.core.ai.memory.pinned_memory import PinnedMemoryManager
        pinned = PinnedMemoryManager(self.db_path)
        return pinned.get_all(project_path)

    def build_context_for_llm(self, project_path: str, include_session_trail: bool = True) -> str:
        """
        Membangun teks konteks gabungan dari semua lapisan memori
        yang relevan untuk disuntikkan ke system prompt LLM.
        """
        lines = []

        # Layer 4: Long-term rules
        rules = self.get_long_term_rules(project_path)
        if rules:
            lines.append("[Long-Term Rules & Preferences]")
            for r in rules:
                lines.append(f"- {r['content']}")
            lines.append("")

        # Layer 3: Session trail
        if include_session_trail:
            trail_text = self.session.format_for_context(limit=5)
            if trail_text:
                lines.append(trail_text)
                lines.append("")

        return "\n".join(lines)
