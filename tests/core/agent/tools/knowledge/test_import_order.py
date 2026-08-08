import subprocess
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
for _ in range(5):
    PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)

IMPORT_CASES = [
    "import nexa.core.ai.knowledge",
    "from nexa.core.ai.knowledge import KnowledgeOrchestrator, CapabilityResolver",
    "from nexa.core.ai.knowledge.orchestrator import KnowledgeOrchestrator",
    "from nexa.core.agent.tools.knowledge import register_knowledge_tools",
    "from nexa.core.agent.tools.knowledge.file import FileTool",
    "from nexa.core.ai.knowledge.cache.sqlite import SQLiteCache",
]

class TestImportOrder:
    def test_import_orders_do_not_circular_import(self):
        for stmt in IMPORT_CASES:
            result = subprocess.run(
                [sys.executable, "-X", "utf8", "-c", stmt],
                capture_output=True, text=True,
                cwd=PROJECT_ROOT,
            )
            assert result.returncode == 0, (
                f"Import FAILED: {stmt}\n{result.stderr}"
            )
