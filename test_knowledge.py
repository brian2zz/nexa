import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from nexa.core.ai.knowledge import KnowledgeEngine, ScannerResult, AnalyzerResult

def test_knowledge_engine():
    # Mock data
    scanner_result = ScannerResult(
        files=[
            {"path": "auth_controller.py", "content": "import jwt\ndef login():\n    pass"},
            {"path": "user_model.py", "content": "class User:\n    pass"},
            {"path": "unrelated.py", "content": "print('hello')"}
        ]
    )
    analyzer_result = AnalyzerResult(language="python")
    
    engine = KnowledgeEngine()
    
    context = engine.build(
        goal="implement login feature",
        task="analyze",
        scanner_result=scanner_result,
        analyzer_result=analyzer_result
    )
    
    print("=== SELECTED FILES ===")
    for f in context.selected_files:
        print(f.path, "| Reason:", f.selection_reason, "| Score:", f.score)
        
    print("\n=== METRICS ===")
    print(context.metrics)
    
    print("\n=== SUMMARY ===")
    print(context.summary)

if __name__ == "__main__":
    test_knowledge_engine()
