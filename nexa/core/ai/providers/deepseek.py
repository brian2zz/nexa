import requests
import os
from typing import List, Dict, Any
from .base import LLMProvider
from nexa.config import Config

class DeepSeekProvider(LLMProvider):
    def __init__(self):
        self.api_key = Config.get("deepseek.api_key", os.environ.get("DEEPSEEK_API_KEY", ""))
        self.host = Config.get("deepseek.host", "https://api.deepseek.com")
        self.model = Config.get("deepseek.model", "deepseek-chat")
        
        if not self.api_key:
            raise ValueError("DeepSeek API Key is missing. Set DEEPSEEK_API_KEY environment variable or 'deepseek.api_key' in config.")

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.2, tools: List[Dict[str, Any]] = None) -> Dict[str, Any]:
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
        
        if tools:
            payload["tools"] = tools
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            # Handle specific API errors
            if response.status_code == 401:
                raise Exception("Unauthorized: Invalid DeepSeek API Key.")
            elif response.status_code == 402:
                raise Exception("Payment Required: Insufficient balance in DeepSeek account.")
                
            response.raise_for_status()
            data = response.json()
            
            message_dict = data.get("choices", [{}])[0].get("message", {})
            message_content = message_dict.get("content", "")
            tool_calls = message_dict.get("tool_calls", [])
            
            usage_data = data.get("usage", {})
            
            return {
                "content": message_content,
                "tool_calls": tool_calls,
                "provider": "deepseek",
                "model": self.model,
                "usage": {
                    "prompt_eval_count": usage_data.get("prompt_tokens", 0),
                    "eval_count": usage_data.get("completion_tokens", 0)
                }
            }
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error communicating with DeepSeek API: {str(e)}")

    def health(self) -> bool:
        # DeepSeek currently doesn't have a specific public unauthenticated ping endpoint,
        # but returning True if API key is set is a reasonable fallback, or we can check balance.
        return bool(self.api_key)

    def list_models(self) -> List[str]:
        # DeepSeek models
        return ["deepseek-chat", "deepseek-coder"]
