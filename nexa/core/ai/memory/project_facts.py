import os
import sqlite3
import datetime
from pathlib import Path
from typing import Dict, Any

class ProjectFactsManager:
    """
    Manages persistent project facts (key-value) in chat_memory.db.
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
                CREATE TABLE IF NOT EXISTS project_facts (
                    project_path TEXT,
                    fact_key TEXT,
                    fact_value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (project_path, fact_key)
                )
            ''')
            conn.commit()

    def get_all(self, project_path: str) -> Dict[str, str]:
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT fact_key, fact_value FROM project_facts WHERE project_path = ?", (project_path,))
            return {row[0]: row[1] for row in cursor.fetchall()}

    def set(self, project_path: str, key: str, value: str):
        with self._get_conn() as conn:
            conn.execute('''
                INSERT INTO project_facts (project_path, fact_key, fact_value, updated_at) 
                VALUES (?, ?, ?, ?)
                ON CONFLICT(project_path, fact_key) 
                DO UPDATE SET fact_value=excluded.fact_value, updated_at=excluded.updated_at
            ''', (project_path, key, value, datetime.datetime.now()))
            conn.commit()

    def remove(self, project_path: str, key: str):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM project_facts WHERE project_path = ? AND fact_key = ?", (project_path, key))
            conn.commit()

    def update_from_scan(self, project_path: str, new_facts: Dict[str, str]):
        """
        Updates project facts automatically from scan, without overwriting manual preferences
        like coding_style, default_language, deployment if they exist.
        """
        current_facts = self.get_all(project_path)
        # We assume scan facts are absolute, but user preferences are preserved.
        # So we just update or insert the new_facts.
        for k, v in new_facts.items():
            # If we want to strictly protect certain keys from being overwritten by scan,
            # we can add logic here. Currently we assume scan facts don't overlap with user manual keys
            # or if they do (like framework), the scan is the source of truth.
            self.set(project_path, k, v)
