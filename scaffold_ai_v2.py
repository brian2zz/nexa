import os
import json

base_dir = "g:/project code/nexa"

# 1. nexa/core/ai/config.py
config_content = """import os

class AgentConfig:
    DB_PATH = '.nexa/agent.db'
    IGNORE_LIST = [
        '.git',
        'node_modules',
        'vendor',
        'dist',
        'build',
        '__pycache__',
        '.idea',
        '.vscode',
        '.nexa',
        'nexa.egg-info',
        'nexa_framework.egg-info'
    ]
"""

# 2. nexa/core/ai/memory.py
memory_content = """import sqlite3
import os

class Memory:
    def __init__(self, db_path=None):
        from .config import AgentConfig
        self.db_path = db_path or AgentConfig.DB_PATH
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                root_path TEXT UNIQUE,
                framework TEXT,
                language TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                path TEXT,
                extension TEXT,
                size INTEGER,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()

    def save_project(self, root_path, framework, language):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO projects (root_path, framework, language) VALUES (?, ?, ?)',
            (root_path, framework, language)
        )
        self.conn.commit()
        
        cursor.execute('SELECT id FROM projects WHERE root_path = ?', (root_path,))
        return cursor.fetchone()[0]

    def save_files(self, project_id, files_list):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM files WHERE project_id = ?', (project_id,))
        for f in files_list:
            cursor.execute(
                'INSERT INTO files (project_id, path, extension, size) VALUES (?, ?, ?, ?)',
                (project_id, f['path'], f['extension'], f['size'])
            )
        self.conn.commit()

    def get_project(self, root_path):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, framework, language FROM projects WHERE root_path = ?', (root_path,))
        row = cursor.fetchone()
        return {'id': row[0], 'framework': row[1], 'language': row[2]} if row else None

    def get_files(self, project_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT path, extension, size FROM files WHERE project_id = ?', (project_id,))
        return [{'path': r[0], 'extension': r[1], 'size': r[2]} for r in cursor.fetchall()]
"""

# 3. nexa/core/ai/scanner/detector.py
detector_content = """import os

class ProjectDetector:
    def detect(self, root_path="."):
        # Check files from the root_path
        
        # Django
        if os.path.exists(os.path.join(root_path, "manage.py")):
            return {"framework": "django", "language": "python"}
            
        # Flutter
        if os.path.exists(os.path.join(root_path, "pubspec.yaml")):
            return {"framework": "flutter", "language": "dart"}
            
        # Laravel
        if os.path.exists(os.path.join(root_path, "artisan")) and os.path.exists(os.path.join(root_path, "composer.json")):
            return {"framework": "laravel", "language": "php"}
            
        # CodeIgniter 3
        if os.path.exists(os.path.join(root_path, "application", "config", "config.php")):
            return {"framework": "codeigniter3", "language": "php"}
            
        # NexaPHP
        if os.path.exists(os.path.join(root_path, "modules")) and os.path.exists(os.path.join(root_path, "routes")) and os.path.exists(os.path.join(root_path, "composer.json")):
            return {"framework": "nexaphp", "language": "php"}
            
        # Generic PHP
        if os.path.exists(os.path.join(root_path, "composer.json")):
            return {"framework": "generic_php", "language": "php"}
            
        # Generic Python
        if os.path.exists(os.path.join(root_path, "requirements.txt")) or os.path.exists(os.path.join(root_path, "pyproject.toml")) or os.path.exists(os.path.join(root_path, "setup.py")):
            return {"framework": "generic_python", "language": "python"}
            
        return {"framework": "unknown", "language": "unknown"}
"""

# 4. nexa/core/ai/scanner/scanner.py
scanner_content = """import os

class FileScanner:
    def scan(self, root_path="."):
        from ..config import AgentConfig
        ignore_list = AgentConfig.IGNORE_LIST
        
        scanned_files = []
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Ignore directories
            dirnames[:] = [d for d in dirnames if d not in ignore_list and not d.startswith('.')]
            
            for file in filenames:
                file_path = os.path.join(dirpath, file)
                rel_path = os.path.relpath(file_path, root_path)
                
                # Normalize slashes for consistency
                rel_path = rel_path.replace("\\\\", "/")
                
                _, ext = os.path.splitext(file)
                try:
                    size = os.path.getsize(file_path)
                except Exception:
                    size = 0
                    
                scanned_files.append({
                    "path": rel_path,
                    "extension": ext.lstrip('.'),
                    "size": size
                })
                
        return scanned_files
"""

# 5. nexa/core/ai/providers/mock.py
mock_content = """from .base import LLMProvider
import json

class MockProvider(LLMProvider):
    def generate(self, prompt):
        if prompt == 'analyze':
            # Format realis untuk analyzer
            data = {
                "strengths": ["Arsitektur modular", "Penggunaan ORM yang baik"],
                "problems": ["Beberapa file terlalu besar", "Kurangnya unit test di module X"],
                "risks": ["Potensi N+1 query problem", "Dependency Y sudah usang"],
                "recommendations": ["Refactor view.py menjadi service layer", "Tambahkan test coverage minimal 80%"]
            }
            return json.dumps(data, indent=2)
            
        elif prompt == 'plan':
            # Format realis untuk planner
            data = {
                "goal": "Implement JWT Authentication",
                "complexity": "medium",
                "risk": "low",
                "steps": [
                    {"title": "Setup JWT Library", "description": "Install djangorestframework-simplejwt and add to INSTALLED_APPS."},
                    {"title": "Configure Settings", "description": "Set REST_FRAMEWORK defaults and configure SIMPLE_JWT settings like ACCESS_TOKEN_LIFETIME."},
                    {"title": "Update URLs", "description": "Add token obtain and refresh endpoints to urls.py."},
                    {"title": "Test Authentication", "description": "Verify token generation using postman or curl."}
                ]
            }
            return json.dumps(data, indent=2)
            
        return json.dumps({'status': 'mocked_success', 'data': []})
"""

# 6. nexa/commands/ai/scan.py
cmd_scan_content = """import os
import json

def handle(args):
    from nexa.core.ai.scanner.detector import ProjectDetector
    from nexa.core.ai.scanner.scanner import FileScanner
    from nexa.core.ai.memory import Memory
    
    root_path = os.path.abspath(os.getcwd())
    
    # 1. Deteksi
    print(f"🕵️  Mendeteksi project di {root_path} ...")
    detector = ProjectDetector()
    project_info = detector.detect(root_path)
    print(f"✅ Terdeteksi Framework: {project_info['framework']} (Bahasa: {project_info['language']})")
    
    # 2. Pemindaian
    print("🔍 Memindai file project...")
    scanner = FileScanner()
    files = scanner.scan(root_path)
    print(f"✅ Ditemukan {len(files)} file yang valid.")
    
    # 3. Penyimpanan
    print("💾 Menyimpan ke memori SQLite...")
    memory = Memory()
    project_id = memory.save_project(root_path, project_info['framework'], project_info['language'])
    memory.save_files(project_id, files)
    
    print("✨ Pemindaian Selesai!")
"""

# 7. nexa/commands/ai/tree.py
cmd_tree_content = """import os

def handle(args):
    from nexa.core.ai.memory import Memory
    
    root_path = os.path.abspath(os.getcwd())
    memory = Memory()
    project = memory.get_project(root_path)
    
    if not project:
        print("❌ Project belum dipindai. Silakan jalankan 'nexa scan' terlebih dahulu.")
        return
        
    files = memory.get_files(project['id'])
    if not files:
        print("❌ Tidak ada file ditemukan di database.")
        return
        
    print(f"🌳 Project Tree for: {os.path.basename(root_path)} ({project['framework']})")
    
    # Build tree
    tree = {}
    for f in files:
        parts = f['path'].split('/')
        current = tree
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]
            
    def print_tree(d, indent=""):
        items = list(d.keys())
        for i, key in enumerate(items):
            is_last = (i == len(items) - 1)
            prefix = "└── " if is_last else "├── "
            print(indent + prefix + key)
            
            if d[key]:
                next_indent = indent + ("    " if is_last else "│   ")
                print_tree(d[key], next_indent)
                
    print(os.path.basename(root_path))
    print_tree(tree)
"""

# 8. nexa/core/ai/analyzer.py
analyzer_content = """class Analyzer:
    def __init__(self, provider):
        self.provider = provider
        
    def analyze(self):
        return self.provider.generate('analyze')
"""

# 9. nexa/core/ai/planner.py
planner_content = """class Planner:
    def __init__(self, provider):
        self.provider = provider
        
    def plan(self):
        return self.provider.generate('plan')
"""

files_to_write = {
    "nexa/core/ai/config.py": config_content,
    "nexa/core/ai/memory.py": memory_content,
    "nexa/core/ai/scanner/detector.py": detector_content,
    "nexa/core/ai/scanner/scanner.py": scanner_content,
    "nexa/core/ai/providers/mock.py": mock_content,
    "nexa/commands/ai/scan.py": cmd_scan_content,
    "nexa/commands/ai/tree.py": cmd_tree_content,
    "nexa/core/ai/analyzer.py": analyzer_content,
    "nexa/core/ai/planner.py": planner_content,
}

for path, content in files_to_write.items():
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Scaffolding V2 complete!")
