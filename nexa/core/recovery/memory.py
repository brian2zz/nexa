import os
import sqlite3
from typing import Optional, Dict

class RecoveryMemory:
    """SQLite-backed Memory for Learning from Failures."""
    
    def __init__(self, workspace_path: str):
        self.db_path = os.path.join(workspace_path, ".nexa", "recovery_memory.db")
        self._ensure_db()

    def _ensure_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recovery_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    failure_type TEXT,
                    error_signature TEXT,
                    strategy_used TEXT,
                    success BOOLEAN,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Indexes for fast lookup of previous solutions
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_err_sig ON recovery_history(error_signature)')
            conn.commit()

    def memorize(self, failure_type: str, error_signature: str, strategy: str, success: bool):
        """Stores the result of a recovery attempt."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO recovery_history (failure_type, error_signature, strategy_used, success)
                VALUES (?, ?, ?, ?)
            ''', (failure_type, error_signature, strategy, success))
            conn.commit()

    def recall(self, error_signature: str) -> Optional[str]:
        """Recalls the last successful strategy used for a specific error signature."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT strategy_used FROM recovery_history 
                WHERE error_signature = ? AND success = 1
                ORDER BY timestamp DESC LIMIT 1
            ''', (error_signature,))
            row = cursor.fetchone()
            if row:
                return row[0]
        return None
