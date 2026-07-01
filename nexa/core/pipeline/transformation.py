import json
from typing import Dict, Any, List
from nexa.core.ai.providers.factory import ProviderFactory

class TransformationResult:
    def __init__(self, step: Dict[str, Any], raw_code: str):
        self.step = step
        self.raw_code = raw_code

class TransformationEngine:
    """
    Tugas: Menerima ExecutionPlan dan untuk setiap langkah modifikasi file, 
    ia meminta LLM (secara deterministik/tanpa reasoning) untuk menuliskan kode mentahnya.
    """
    def __init__(self):
        try:
            self.provider = ProviderFactory.create()
        except Exception:
            self.provider = None

    def transform(self, plan: Dict[str, Any]) -> List[TransformationResult]:
        results = []
        steps = []
        for stage in plan.get("stages", []):
            for intent in stage.get("intents", []):
                # Map IntentNode back to legacy dict format for TransformationResult
                target = intent.get("parameters", {}).get("target") or \
                         intent.get("parameters", {}).get("path") or \
                         intent.get("parameters", {}).get("command") or ""
                         
                steps.append({
                    "action": intent.get("action", ""),
                    "target": target,
                    "description": intent.get("description", "")
                })
        
        for step in steps:
            action = step.get("action", "").upper()
            if action in ["CREATE", "MODIFY"]:
                # Kirim prompt statis ke LLM untuk mendapatkan kodenya saja
                target = step.get("target", "")
                desc = step.get("description", "")
                
                messages = [
                    {"role": "system", "content": "You are a pure code generator. Output ONLY the raw code for the requested file, without markdown formatting or reasoning."},
                    {"role": "user", "content": f"Target: {target}\nDescription: {desc}\nOutput the raw code."}
                ]
                
                if self.provider:
                    try:
                        resp = self.provider.generate(messages, temperature=0.0)
                        raw_code = resp.get("content", "")
                        # Bersihkan markdown jika LLM masih nakal
                        if raw_code.startswith("```"):
                            lines = raw_code.split("\n")
                            if len(lines) >= 2:
                                raw_code = "\n".join(lines[1:-1])
                    except Exception as e:
                        raw_code = f"ERROR: {e}"
                else:
                    raw_code = "# Mock Generated Code"
                    
                results.append(TransformationResult(step, raw_code))
            else:
                # Untuk COMMAND atau DELETE, tidak perlu LLM nulis kode
                results.append(TransformationResult(step, ""))
                
        return results
