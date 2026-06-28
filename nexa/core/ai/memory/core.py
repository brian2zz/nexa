import os
import sqlite3
import datetime
from pathlib import Path
from typing import List, Dict, Tuple

class ChatMemoryManager:
    """
    Manages persistent chat memory using SQLite.
    Sessions are scoped by project paths.
    """
    def __init__(self, db_path: str = None):
        if db_path is None:
            home_dir = str(Path.home())
            nexa_dir = os.path.join(home_dir, ".nexa")
            os.makedirs(nexa_dir, exist_ok=True)
            db_path = os.path.join(nexa_dir, "chat_memory.db")
            
        self.db_path = db_path
        self._init_db()
        self.cleanup_sessions()
        
    def cleanup_sessions(self):
        """
        Membersihkan database dari:
        1. Sesi yang kosong (0 pesan)
        2. Sesi yang lebih tua dari 3 hari
        """
        with self._get_conn() as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Hapus sesi yang lebih dari 3 hari
            three_days_ago = datetime.datetime.now() - datetime.timedelta(days=3)
            conn.execute("DELETE FROM sessions WHERE created_at < ?", (three_days_ago,))
            
            # Hapus sesi yang tidak punya message sama sekali
            conn.execute('''
                DELETE FROM sessions 
                WHERE id NOT IN (SELECT DISTINCT session_id FROM messages)
            ''')
            conn.commit()
        
    def _get_conn(self):
        return sqlite3.connect(self.db_path)
        
    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
                )
            ''')
            conn.commit()
            
    def create_session(self, project_path: str) -> int:
        with self._get_conn() as conn:
            cursor = conn.execute(
                "INSERT INTO sessions (project_path, created_at) VALUES (?, ?)", 
                (project_path, datetime.datetime.now())
            )
            conn.commit()
            return cursor.lastrowid
            
    def save_message(self, session_id: int, role: str, content: str):
        if not session_id:
            return
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (session_id, role, content, datetime.datetime.now())
            )
            conn.commit()
            
    def load_session_messages(self, session_id: int, limit: int = 6) -> List[Dict[str, str]]:
        """
        Load the last N messages of a session. Default limit is 6 (3 pairs).
        """
        with self._get_conn() as conn:
            # Order by id DESC to get the latest, then reverse it for chronological order
            cursor = conn.execute(
                "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, limit)
            )
            rows = cursor.fetchall()
            messages = [{"role": row[0], "content": row[1]} for row in rows]
            messages.reverse()
            return messages

    def get_project_sessions(self, project_path: str, limit: int = 10) -> List[Tuple[int, str, int]]:
        """
        Returns list of (session_id, created_at_str, message_count).
        """
        with self._get_conn() as conn:
            cursor = conn.execute(
                '''
                SELECT s.id, s.created_at, COUNT(m.id) as msg_count 
                FROM sessions s
                LEFT JOIN messages m ON s.id = m.session_id
                WHERE s.project_path = ?
                GROUP BY s.id
                ORDER BY s.id DESC
                LIMIT ?
                ''',
                (project_path, limit)
            )
            return cursor.fetchall()
            
    def delete_session(self, session_id: int) -> bool:
        """Deletes a specific session and its messages (handled by CASCADE if FK is ON, but we explicitly delete to be safe)."""
        with self._get_conn() as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            conn.commit()
            return cursor.rowcount > 0
            
    def clear_project_sessions(self, project_path: str) -> int:
        """Deletes all sessions for a given project path."""
        with self._get_conn() as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.execute("DELETE FROM sessions WHERE project_path = ?", (project_path,))
            conn.commit()
            return cursor.rowcount

class Memory:
    """
    Legacy memory for nexa scan and analyze.
    """
    def __init__(self, db_path=None):
        if db_path is None:
            home_dir = str(Path.home())
            nexa_dir = os.path.join(home_dir, ".nexa")
            os.makedirs(nexa_dir, exist_ok=True)
            db_path = os.path.join(nexa_dir, "nexa.db")
            
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE,
                    framework TEXT,
                    language TEXT,
                    last_scan TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    path TEXT,
                    extension TEXT,
                    size INTEGER,
                    last_modified TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                )
            ''')
            conn.commit()

    def get_project(self, path):
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT * FROM projects WHERE path = ?", (path,))
            row = cursor.fetchone()
            if row:
                return {'id': row[0], 'path': row[1], 'framework': row[2], 'language': row[3]}
            return None

    def get_files(self, project_id):
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT * FROM files WHERE project_id = ?", (project_id,))
            rows = cursor.fetchall()
            return [{'path': row[2], 'extension': row[3], 'size': row[4]} for row in rows]
            
    def save_project(self, path, framework, language):
        with self._get_conn() as conn:
            cursor = conn.execute(
                "INSERT INTO projects (path, framework, language, last_scan) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(path) DO UPDATE SET framework=excluded.framework, language=excluded.language, last_scan=excluded.last_scan",
                (path, framework, language, datetime.datetime.now())
            )
            if cursor.lastrowid:
                return cursor.lastrowid
            cursor = conn.execute("SELECT id FROM projects WHERE path = ?", (path,))
            return cursor.fetchone()[0]

    def save_files(self, project_id, files):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM files WHERE project_id = ?", (project_id,))
            conn.executemany(
                "INSERT INTO files (project_id, path, extension, size, last_modified) VALUES (?, ?, ?, ?, ?)",
                [(project_id, f['path'], f['extension'], f.get('size', 0), datetime.datetime.now()) for f in files]
            )
            conn.commit()
