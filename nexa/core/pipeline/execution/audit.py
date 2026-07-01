import os
import sqlite3
import hashlib
from datetime import datetime
from nexa.core.pipeline.execution.models import CommandResult

class AuditService:
    """
    Logs all terminal executions for auditing and Phase 6 (Recovery/Learning) purposes.
    """
    
    def __init__(self, workspace_path: str):
        self.db_path = os.path.join(workspace_path, ".nexa", "execution_audit.db")
        self._ensure_db()
        
    def _ensure_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command_hash TEXT,
                    command TEXT,
                    success BOOLEAN,
                    returncode INTEGER,
                    duration REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            
    def log(self, result: CommandResult):
        cmd_hash = hashlib.sha256(result.command.encode('utf-8')).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO audit_log (command_hash, command, success, returncode, duration)
                VALUES (?, ?, ?, ?, ?)
            ''', (cmd_hash, result.command, result.success, result.returncode, result.duration))
            conn.commit()
