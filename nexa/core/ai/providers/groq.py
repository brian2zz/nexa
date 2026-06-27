import requests
import os
from typing import List, Dict, Any
from .base import LLMProvider
from nexa.config import Config

class GroqProvider(LLMProvider):
    def __init__(self):
        self.api_key = Config.get("groq.api_key", os.environ.get("GROQ_API_KEY", ""))
        self.host = Config.get("groq.host", "https://api.groq.com/openai/v1")
        self.model = Config.get("groq.model", "llama-3.1-8b-instant")
        
        if not self.api_key:
            raise ValueError("Groq API Key is missing. Set GROQ_API_KEY environment variable or 'groq.api_key' in config.")

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.2) -> Dict[str, Any]:
        url = f"{self.host.rstrip('/')}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            # Handle specific API errors
            if response.status_code == 401:
                raise Exception("Unauthorized: Invalid Groq API Key.")
            
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as he:
                try:
                    error_detail = response.json()
                    raise Exception(f"{str(he)} - Detail: {error_detail}")
                except:
                    raise Exception(f"{str(he)} - Response: {response.text}")
                
            data = response.json()
            
            message_content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage_data = data.get("usage", {})
            
            return {
                "content": message_content,
                "provider": "groq",
                "model": self.model,
                "usage": {
                    "prompt_eval_count": usage_data.get("prompt_tokens", 0),
                    "eval_count": usage_data.get("completion_tokens", 0)
                }
            }
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error communicating with Groq API: {str(e)}")

    def health(self) -> bool:
        return bool(self.api_key)

    def list_models(self) -> List[str]:
        return ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"]
