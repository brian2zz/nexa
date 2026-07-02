import os
import sqlite3
import threading
from typing import List, Dict, Optional
from nexa.core.utils.path import get_project_nexa_dir

class WorkspaceIndexer:
    """
    Scans the workspace directory and builds a SQLite index for lightning-fast file lookups.
    """
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.db_path = os.path.join(get_project_nexa_dir(workspace_path), "workspace.db")
        self._ensure_db()

    def _ensure_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Phase 5: Drop legacy DB if it doesn't have the new tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='symbols'")
            if not cursor.fetchone():
                cursor.execute("DROP TABLE IF EXISTS files")
                
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
            
            # Phase 5: AST Semantic Indexing
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS symbols (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER,
                    name TEXT,
                    type TEXT,
                    start_line INTEGER,
                    end_line INTEGER,
                    FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_symbol_name ON symbols(name)')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS imports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER,
                    name TEXT,
                    source TEXT,
                    FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE
                )
            ''')
            
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
                        
                        file_id = cursor.lastrowid
                        
                        # Phase 5: Semantic AST Indexing
                        if ext.lower() == '.py':
                            symbols, imports = self._parse_python_ast(filepath)
                            for sym in symbols:
                                cursor.execute('''
                                    INSERT INTO symbols (file_id, name, type, start_line, end_line)
                                    VALUES (?, ?, ?, ?, ?)
                                ''', (file_id, sym[0], sym[1], sym[2], sym[3]))
                            for imp in imports:
                                cursor.execute('''
                                    INSERT INTO imports (file_id, name, source)
                                    VALUES (?, ?, ?)
                                ''', (file_id, imp[0], imp[1]))
                                
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

    def _parse_python_ast(self, filepath: str) -> tuple[List[tuple], List[tuple]]:
        """
        Parses a python file using the built-in ast module.
        Returns (symbols, imports)
        symbols: [(name, type, start_line, end_line)]
        imports: [(name, source)]
        """
        import ast
        symbols = []
        imports = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    symbols.append((node.name, 'class', node.lineno, getattr(node, 'end_lineno', node.lineno)))
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    symbols.append((node.name, 'function', node.lineno, getattr(node, 'end_lineno', node.lineno)))
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append((alias.name, None))
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        imports.append((alias.name, node.module))
        except Exception:
            pass
        return symbols, imports

    def query_symbols(self, name: str) -> List[Dict]:
        """
        Queries the database for symbols matching the name.
        Returns a list of dictionaries with semantic information.
        """
        query = '''
            SELECT s.name, s.type, s.start_line, s.end_line, f.filepath 
            FROM symbols s
            JOIN files f ON s.file_id = f.id
            WHERE s.name LIKE ?
            LIMIT 50
        '''
        results = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (f"%{name}%",))
                for row in cursor.fetchall():
                    results.append({
                        "name": row[0],
                        "type": row[1],
                        "start_line": row[2],
                        "end_line": row[3],
                        "filepath": row[4]
                    })
        except sqlite3.Error as e:
            results.append({"error": str(e)})
            
        return results
