import os
import sqlite3
import datetime
from pathlib import Path
from typing import List, Dict, Any

class PinnedMemoryManager:
    """
    Manages persistent pinned memory (important user notes/preferences) in chat_memory.db.
    """
    def __init__(self, db_path: str = None):
        if db_path is None:
            home_dir = str(Path.home())
            nexa_dir = os.path.join(home_dir, ".nexa")
            os.makedirs(nexa_dir, exist_ok=True)
            db_path = os.path.join(nexa_dir, "chat_memory.db")
            
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS pinned_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_path TEXT NOT NULL,
                    title TEXT,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source TEXT,
                    tags TEXT
                )
            ''')
            conn.commit()

    def get_all(self, project_path: str) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.execute(
                "SELECT id, content, created_at FROM pinned_memory WHERE project_path = ? ORDER BY id ASC", 
                (project_path,)
            )
            rows = cursor.fetchall()
            return [{"id": row[0], "content": row[1], "created_at": row[2]} for row in rows]

    def add(self, project_path: str, content: str, title: str = "", source: str = "manual", tags: str = "") -> int:
        with self._get_conn() as conn:
            cursor = conn.execute('''
                INSERT INTO pinned_memory (project_path, title, content, created_at, updated_at, source, tags) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (project_path, title, content, datetime.datetime.now(), datetime.datetime.now(), source, tags))
            conn.commit()
            return cursor.lastrowid

    def remove(self, project_path: str, pin_id: int) -> bool:
        with self._get_conn() as conn:
            cursor = conn.execute("DELETE FROM pinned_memory WHERE project_path = ? AND id = ?", (project_path, pin_id))
            conn.commit()
            return cursor.rowcount > 0

    def clear(self, project_path: str):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM pinned_memory WHERE project_path = ?", (project_path,))
            conn.commit()
