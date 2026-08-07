from typing import List, Dict, Any
from .base import LLMProvider
import json

class MockProvider(LLMProvider):
    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.2, tools: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Extract intent from messages
        intent = ""
        for msg in messages:
            content = msg.get("content", "").lower()
            if "nexa hypothesis engine" in content:
                intent = "hypothesis"
            elif "nexa reasoning engine" in content:
                intent = "reasoning"
            elif "nexa ai planner" in content or "planning engine" in content:
                intent = "plan"
            elif "analyze" in content:
                intent = "analyze"
                
        # If the old format is accidentally passed as string (for backward compatibility during transition)
        if isinstance(messages, str):
            intent = messages
            
        content_response = ""
        
        if intent == 'analyze':
            data = {
                "strengths": ["Arsitektur modular", "Penggunaan ORM yang baik"],
                "problems": ["Beberapa file terlalu besar", "Kurangnya unit test di module X"],
                "risks": ["Potensi N+1 query problem", "Dependency Y sudah usang"],
                "recommendations": ["Refactor view.py menjadi service layer", "Tambahkan test coverage minimal 80%"]
            }
            content_response = json.dumps(data, indent=2)
            
        elif intent == 'hypothesis':
            data = {
                "hypotheses": [
                    {
                        "description": "Mocked hypothesis",
                        "search_targets": ["mocked_target.py"]
                    }
                ]
            }
            content_response = json.dumps(data, indent=2)
            
        elif intent == 'reasoning':
            data = {
                "root_cause": "Mocked root cause",
                "evidence_trail": ["Found something in mocked_target.py"],
                "contradictions_found": False,
                "confidence": 95
            }
            content_response = json.dumps(data, indent=2)
            
        elif intent == 'plan':
            data = {
                "objective": "Mocked plan objective",
                "constraints": ["mock_constraint"],
                "work_items": [
                    {
                        "title": "Mock Work Item",
                        "description": "Do something mocky",
                        "affected_files": ["mocked_target.py"],
                        "objective": "Fix mock issue"
                    }
                ],
                "acceptance_criteria": [
                    {
                        "description": "It works",
                        "priority": "MUST",
                        "verification_method": "pytest"
                    }
                ],
                "risk_analysis": [
                    {
                        "category": "Performance",
                        "probability": "LOW",
                        "impact": "LOW",
                        "mitigation": "None"
                    }
                ],
                "clarifications": []
            }
            content_response = json.dumps(data, indent=2)
            
        else:
            content_response = json.dumps({'status': 'mocked_success', 'data': []})
            
        return {
            "content": content_response,
            "provider": "mock",
            "model": "mock-model",
            "usage": {}
        }

    def health(self) -> bool:
        return True

    def list_models(self) -> List[str]:
        return ["mock-model-1", "mock-model-2"]
