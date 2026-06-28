from typing import List, Dict, Any
from .base import LLMProvider
import json

class MockProvider(LLMProvider):
    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.2, tools: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Extract intent from messages
        intent = ""
        for msg in messages:
            content = msg.get("content", "").lower()
            if "analyze" in content:
                intent = "analyze"
            elif "plan" in content:
                intent = "plan"
                
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
            
        elif intent == 'plan':
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
