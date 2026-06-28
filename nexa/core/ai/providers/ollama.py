import requests
from typing import List, Dict, Any
from .base import LLMProvider
from nexa.config import Config

class OllamaProvider(LLMProvider):
    def __init__(self):
        self.host = Config.get("ollama.host", "http://localhost:11434")
        self.model = Config.get("ollama.model", "qwen3:14b")
        
    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.2, tools: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.host.rstrip('/')}/api/chat"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 404:
                raise Exception(f"Model '{self.model}' not found in Ollama. Please pull it first using 'ollama pull {self.model}'.")
                
            response.raise_for_status()
            data = response.json()
            
            # The structure returned by Ollama /api/chat
            message_content = data.get("message", {}).get("content", "")
            
            usage_data = {
                "prompt_eval_count": data.get("prompt_eval_count", 0),
                "eval_count": data.get("eval_count", 0)
            }
            
            return {
                "content": message_content,
                "provider": "ollama",
                "model": self.model,
                "usage": usage_data
            }
            
        except requests.exceptions.ConnectionError:
            raise Exception("Ollama server is not running. Please start Ollama before using AI Provider.")
        except requests.exceptions.RequestException as e:
            # Re-raise standard exception if it's already caught above, or format custom message
            if "Model" in str(e) and "not found" in str(e):
                raise
            raise Exception(f"Error communicating with Ollama: {str(e)}")

    def health(self) -> bool:
        url = f"{self.host.rstrip('/')}/api/tags"
        try:
            response = requests.get(url, timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def list_models(self) -> List[str]:
        url = f"{self.host.rstrip('/')}/api/tags"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            return [model.get("name") for model in data.get("models", [])]
        except requests.exceptions.ConnectionError:
            raise Exception("Ollama server is not running. Please start Ollama before using AI Provider.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error communicating with Ollama: {str(e)}")
