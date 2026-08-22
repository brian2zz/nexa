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
                parts_list = []
                if content:
                    parts_list.append({"text": content})
                if "tool_calls" in msg:
                    for tc in msg["tool_calls"]:
                        fname = tc.get("function", {}).get("name")
                        fargs_raw = tc.get("function", {}).get("arguments", "{}")
                        try:
                            fargs = json.loads(fargs_raw) if isinstance(fargs_raw, str) else fargs_raw
                        except Exception:
                            fargs = {}
                        parts_list.append({"functionCall": {"name": fname, "args": fargs}})
                if parts_list:
                    contents.append({
                        "role": "model",
                        "parts": parts_list
                    })
            elif role == "tool":
                tname = msg.get("name", "tool")
                contents.append({
                    "role": "function",
                    "parts": [{
                        "functionResponse": {
                            "name": tname,
                            "response": {"output": content}
                        }
                    }]
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
        else:
            # If tools is None but history contains function calls/responses, check if any tool message was used
            has_functions = any(c.get("role") == "function" or any("functionCall" in p for p in c.get("parts", [])) for c in contents)
            if has_functions:
                # Provide dummy or standard tool declaration to keep Gemini session valid
                pass
        
        try:
            import time
            max_retries = 4
            for attempt in range(max_retries):
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        sleep_time = 2 ** (attempt + 1)
                        print(f"       [API Limit Reached] Waiting {sleep_time}s before retrying...")
                        time.sleep(sleep_time)
                        continue
                    else:
                        raise Exception("429 Too Many Requests: Rate limit exceeded after retries. Please wait a minute.")
                elif response.status_code == 400:
                    raise Exception(f"Bad Request: {response.text}")
                elif response.status_code == 401 or response.status_code == 403:
                    raise Exception("Unauthorized: Invalid Gemini API Key.")
                    
                response.raise_for_status()
                break
                
            data = response.json()
            
            candidates = data.get("candidates", [])
            if not candidates:
                return {"content": ""}
                
            candidate = candidates[0]
            parts = candidate.get("content", {}).get("parts", [])
            
            if not parts:
                return {"content": ""}
                
            text_parts = []
            tool_calls = []
            
            # Check for text and tool calls (functionCall)
            for part in parts:
                if "text" in part and part["text"]:
                    text_parts.append(part["text"])
                if "functionCall" in part:
                    fc = part["functionCall"]
                    name = fc.get("name")
                    args = fc.get("args", {})
                    tool_calls.append({
                        "id": f"call_{len(tool_calls)+1}",
                        "type": "function",
                        "function": {
                            "name": name,
                            "arguments": json.dumps(args) if isinstance(args, dict) else str(args)
                        }
                    })
                    
            res = {}
            if text_parts:
                res["content"] = "\n".join(text_parts)
            if tool_calls:
                res["tool_calls"] = tool_calls
                
            return res if res else {"content": ""}
            
        except Exception as e:
            raise Exception(f"Gemini API Error: {str(e)}")

    def stream(self, messages: List[Dict[str, str]], temperature: float = 0.2, tools: List[Dict[str, Any]] = None):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:streamGenerateContent?alt=sse&key={self.api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        contents = []
        system_instruction = None
        
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "system":
                system_instruction = content if system_instruction is None else system_instruction + "\n\n" + content
            elif role == "user":
                contents.append({"role": "user", "parts": [{"text": content}]})
            elif role == "assistant":
                contents.append({"role": "model", "parts": [{"text": content}]})
                
        payload = {
            "contents": contents,
            "generationConfig": {"temperature": temperature}
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
            
        try:
            with requests.post(url, headers=headers, json=payload, stream=True, timeout=60) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        decoded = line.decode('utf-8')
                        if decoded.startswith('data: '):
                            json_str = decoded[6:]
                            try:
                                data = json.loads(json_str)
                                candidates = data.get("candidates", [])
                                if candidates:
                                    parts = candidates[0].get("content", {}).get("parts", [])
                                    for part in parts:
                                        if "text" in part:
                                            yield part["text"]
                            except json.JSONDecodeError:
                                pass
        except Exception as e:
            raise Exception(f"Gemini API Stream Error: {str(e)}")

    def health(self) -> bool:
        return bool(self.api_key)

    def list_models(self) -> List[str]:
        return ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"]
