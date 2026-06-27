import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from nexa.core.ai.knowledge import KnowledgeEngine, ScannerResult, AnalyzerResult

def print_inspect():
    print("Knowledge Engine Benchmark")
    print("============================")
    
    scanner_result = ScannerResult(
        project_root="workspace_project",
        files=[
            {"path": "WorkspaceController.py", "content": "import WorkspaceService\nimport jwt\ndef invite_member():\n    pass"},
            {"path": "WorkspaceService.py", "content": "import WorkspaceRepository\nclass WorkspaceService:\n    pass"},
            {"path": "WorkspaceRepository.py", "content": "class WorkspaceRepository:\n    pass"},
            {"path": "unrelated_1.py", "content": "print('hello')"},
            {"path": "unrelated_2.py", "content": "def test(): pass"},
            {"path": "unrelated_3.py", "content": "def foo(): pass"},
        ]
    )
    analyzer_result = AnalyzerResult(language="python")
    
    engine = KnowledgeEngine()
    
    context = engine.build(
        goal="Workspace Invitation",
        task="analyze",
        scanner_result=scanner_result,
        analyzer_result=analyzer_result
    )
    
    print(f"Goal:\n{context.metrics.project_files} Project Files -> {context.metrics.selected_files} Selected")
    print("============================")
    print(f"Intent Domain: {context.selected_modules[0] if context.selected_modules else 'general'}")
    print("============================")
    
    print("Selected Files:")
    for f in context.selected_files:
        print(f"\n{int(f.score)}  {f.path}")
        print("Reason:")
        for r in f.selection_reason:
            print(f"- {r}")
            
    print("\n============================")
    print(f"Compression: {context.metrics.compression_ratio:.1f}%")
    print(f"Estimated Tokens: {context.metrics.estimated_tokens}")
    print(f"Processing Time: {context.metrics.processing_time_sec:.4f} sec")
    print("============================")

if __name__ == "__main__":
    print_inspect()
