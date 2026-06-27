import sqlite3
import json
from typing import Any, Optional
from .base import BaseCache

class SQLiteCache(BaseCache):
    def __init__(self, db_path: str = "knowledge_cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')

    def get(self, key: str) -> Optional[Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT value FROM cache WHERE key = ?', (key,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
        return None

    def set(self, key: str, value: Any) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('INSERT OR REPLACE INTO cache (key, value) VALUES (?, ?)', (key, json.dumps(value)))

    def clear(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM cache')
