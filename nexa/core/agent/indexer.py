import os
import sqlite3
import threading
from typing import List, Dict, Optional

class WorkspaceIndexer:
    """
    Scans the workspace directory and builds a SQLite index for lightning-fast file lookups.
    """
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.db_path = os.path.join(workspace_path, ".nexa", "workspace.db")
        self._ensure_db()

    def _ensure_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filepath TEXT UNIQUE,
                    filename TEXT,
                    extension TEXT,
                    size INTEGER,
                    last_modified REAL
                )
            ''')
            # Create indexes for fast lookup
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_filename ON files(filename)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_extension ON files(extension)')
            conn.commit()

    def scan_workspace(self, async_scan: bool = True):
        """
        Scans the workspace and updates the SQLite database.
        """
        if async_scan:
            t = threading.Thread(target=self._do_scan)
            t.daemon = True
            t.start()
        else:
            self._do_scan()

    def _do_scan(self):
        ignore_dirs = {'.git', 'node_modules', 'vendor', '__pycache__', '.nexa', '.venv', 'venv'}
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if table already has data
            cursor.execute('SELECT count(*) FROM files')
            if cursor.fetchone()[0] > 0:
                # Already indexed, skip re-scan for now
                return
                
            # Table is empty, proceed with scan
            
            for root, dirs, files in os.walk(self.workspace_path):
                # Modify dirs in-place to skip ignored directories
                dirs[:] = [d for d in dirs if d not in ignore_dirs]
                
                for file in files:
                    filepath = os.path.join(root, file)
                    rel_path = os.path.relpath(filepath, self.workspace_path)
                    _, ext = os.path.splitext(file)
                    try:
                        stat = os.stat(filepath)
                        cursor.execute('''
                            INSERT INTO files (filepath, filename, extension, size, last_modified)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (rel_path, file, ext.lower(), stat.st_size, stat.st_mtime))
                    except Exception:
                        # Ignore unreadable files
                        pass
            conn.commit()

    def query_files(self, extension: Optional[str] = None, name: Optional[str] = None) -> List[Dict]:
        """
        Queries the database for files matching criteria.
        Returns lightning-fast results instead of walking the disk.
        """
        query = "SELECT filepath, filename, size FROM files WHERE 1=1"
        params = []
        
        if extension:
            if not extension.startswith('.'):
                extension = '.' + extension
            query += " AND extension = ?"
            params.append(extension.lower())
            
        if name:
            # Using LIKE for partial matches
            query += " AND filename LIKE ?"
            params.append(f"%{name}%")
            
        query += " LIMIT 100" # Limit results to prevent context bloat
        
        results = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                for row in cursor.fetchall():
                    results.append({
                        "filepath": row[0],
                        "filename": row[1],
                        "size": row[2]
                    })
        except sqlite3.Error as e:
            results.append({"error": str(e)})
            
        return results
