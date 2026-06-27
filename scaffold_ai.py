import os

base_dir = "g:/project code/nexa"
dirs = [
    "nexa/core/ai",
    "nexa/core/ai/scanner",
    "nexa/core/ai/scanner/adapters",
    "nexa/core/ai/providers",
    "nexa/commands/ai"
]

for d in dirs:
    os.makedirs(os.path.join(base_dir, d), exist_ok=True)

files = {
    "nexa/core/ai/__init__.py": "",
    "nexa/core/ai/config.py": "class AgentConfig:\n    DB_PATH = 'nexa_ai_memory.db'\n",
    "nexa/core/ai/memory.py": "import sqlite3\nclass Memory:\n    def __init__(self, db_path='nexa_ai_memory.db'):\n        self.conn = sqlite3.connect(db_path)\n        self._init_db()\n    def _init_db(self):\n        pass\n",
    "nexa/core/ai/scanner/__init__.py": "",
    "nexa/core/ai/scanner/detector.py": "class ProjectDetector:\n    def detect(self):\n        return {'framework': 'django', 'language': 'python'}\n",
    "nexa/core/ai/scanner/scanner.py": "class FileScanner:\n    def scan(self, framework):\n        return {'files': []}\n",
    "nexa/core/ai/scanner/adapters/__init__.py": "",
    "nexa/core/ai/scanner/adapters/base.py": "class BaseAdapter:\n    pass\n",
    "nexa/core/ai/providers/__init__.py": "",
    "nexa/core/ai/providers/base.py": "class LLMProvider:\n    def generate(self, prompt):\n        raise NotImplementedError\n",
    "nexa/core/ai/providers/mock.py": "from .base import LLMProvider\nimport json\nclass MockProvider(LLMProvider):\n    def generate(self, prompt):\n        return json.dumps({'status': 'mocked_success', 'data': []})\n",
    "nexa/core/ai/context_builder.py": "class ContextBuilder:\n    pass\n",
    "nexa/core/ai/analyzer.py": "class Analyzer:\n    def __init__(self, provider):\n        self.provider = provider\n    def analyze(self):\n        return self.provider.generate('analyze')\n",
    "nexa/core/ai/planner.py": "class Planner:\n    def __init__(self, provider):\n        self.provider = provider\n    def plan(self):\n        return self.provider.generate('plan')\n",
    "nexa/commands/ai/__init__.py": "",
    "nexa/commands/ai/scan.py": "def handle(args):\n    from nexa.core.ai.scanner.detector import ProjectDetector\n    d = ProjectDetector()\n    print(f'Running Scan... Detected: {d.detect()}')\n",
    "nexa/commands/ai/tree.py": "def handle(args):\n    print('Running Tree...')\n",
    "nexa/commands/ai/analyze.py": "def handle(args):\n    from nexa.core.ai.analyzer import Analyzer\n    from nexa.core.ai.providers.mock import MockProvider\n    analyzer = Analyzer(MockProvider())\n    print(f'Running Analyze... Result: {analyzer.analyze()}')\n",
    "nexa/commands/ai/plan.py": "def handle(args):\n    from nexa.core.ai.planner import Planner\n    from nexa.core.ai.providers.mock import MockProvider\n    planner = Planner(MockProvider())\n    print(f'Running Plan... Result: {planner.plan()}')\n",
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path)
    if not os.path.exists(full_path):
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
print('Done scaffolding')
