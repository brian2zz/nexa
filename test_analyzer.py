import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from nexa.core.ai.analyzer import AIAnalyzer, OutputFormatter
from nexa.core.ai.knowledge import ScannerResult, AnalyzerResult as StaticResult

class MockProvider:
    name = "MockProvider"
    model = "mock-model-v1"
    
    def generate(self, messages):
        # Returns a valid JSON string that the response parser will extract and the AIAdapter will map
        response = {
            "summary": "This is a great workspace module, but needs more security.",
            "scores": {
                "architecture": 9,
                "security": 6,
                "performance": 8
            },
            "technical_debt": [
                {"severity": "high", "file": "WorkspaceController.py", "issue": "No rate limiting"}
            ],
            "recommendations": [
                {"priority": "high", "description": "Implement rate limiting middleware"}
            ],
            "strengths": ["Clean separation of concerns"],
            "weaknesses": ["Lack of rate limiting"],
            "next_steps": ["Add rate limiting", "Write more unit tests"],
            "confidence": "High"
        }
        return json.dumps(response)

def test_analyzer():
    provider = MockProvider()
    analyzer = AIAnalyzer(provider=provider)
    formatter = OutputFormatter()
    
    scanner_result = ScannerResult(
        project_root="mock_project",
        files=[
            {"path": "WorkspaceController.py", "content": "import jwt\ndef invite(): pass"}
        ]
    )
    static_result = StaticResult(language="python", framework="Django")
    
    print("Running Analyzer Orchestration...")
    result = analyzer.analyze(
        goal="Analyze Workspace Security",
        scanner_result=scanner_result,
        static_result=static_result
    )
    
    if result.success:
        print("\n[SUCCESS] Analyzer pipeline completed successfully!")
        print("\n=== MARKDOWN OUTPUT ===")
        print(formatter.format(result.report, "markdown"))
        
        print("\n=== TEXT OUTPUT ===")
        print(formatter.format(result.report, "text"))
        
        print("\nWarnings:")
        for w in result.warnings:
            print(f"- {w}")
    else:
        print("\n[FAILED] Analyzer pipeline failed!")
        for e in result.errors:
            print(f"- {e}")

if __name__ == "__main__":
    test_analyzer()
