import requests
import os
import json
from typing import List, Dict, Any
from .base import LLMProvider
from nexa.config import Config

class GeminiProvider(LLMProvider):
    def __init__(self):
        self.api_key = Config.get("gemini.api_key", os.environ.get("GEMINI_API_KEY", ""))
        self.model = Config.get("gemini.model", "gemini-2.5-flash")
        
        if not self.api_key:
            raise ValueError("Gemini API Key is missing. Set GEMINI_API_KEY environment variable or 'gemini.api_key' in config.")

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.2, tools: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Transform OpenAI format to Gemini format
        contents = []
        system_instruction = None
        
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            
            if role == "system":
                # Aggregate system prompts
                if system_instruction is None:
                    system_instruction = content
                else:
                    system_instruction += "\n\n" + content
            elif role == "user":
                contents.append({
                    "role": "user",
                    "parts": [{"text": content}]
                })
            elif role == "assistant":
                contents.append({
                    "role": "model",
                    "parts": [{"text": content}]
                })
                
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature
            }
        }
        
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }
            
        if tools:
            # Transform OpenAI tools to Gemini function_declarations
            function_declarations = []
            for t in tools:
                if t.get("type") == "function":
                    func_data = t.get("function", {})
                    gemini_func = {
                        "name": func_data.get("name"),
                        "description": func_data.get("description", ""),
                    }
                    if "parameters" in func_data:
                        gemini_func["parameters"] = func_data["parameters"]
                    function_declarations.append(gemini_func)
            
            if function_declarations:
                payload["tools"] = [{"functionDeclarations": function_declarations}]
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 400:
                raise Exception(f"Bad Request: {response.text}")
            elif response.status_code == 401 or response.status_code == 403:
                raise Exception("Unauthorized: Invalid Gemini API Key.")
                
            response.raise_for_status()
            data = response.json()
            
            candidates = data.get("candidates", [])
            if not candidates:
                return {"content": ""}
                
            candidate = candidates[0]
            parts = candidate.get("content", {}).get("parts", [])
            
            if not parts:
                return {"content": ""}
                
            # Check for tool calls (functionCall)
            for part in parts:
                if "functionCall" in part:
                    fc = part["functionCall"]
                    name = fc.get("name")
                    args = fc.get("args", {})
                    return {
                        "tool_calls": [
                            {
                                "function": {
                                    "name": name,
                                    "arguments": json.dumps(args)
                                }
                            }
                        ]
                    }
                    
                if "text" in part:
                    return {"content": part["text"]}
                    
            return {"content": ""}
            
        except Exception as e:
            raise Exception(f"Gemini API Error: {str(e)}")

    def health(self) -> bool:
        return bool(self.api_key)

    def list_models(self) -> List[str]:
        return ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"]
