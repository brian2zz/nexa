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

    def transform(self, plan: Dict[str, Any], cwd: str = ".") -> List[TransformationResult]:
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
                
                # Baca file asli jika ada
                original_content = ""
                import os
                
                abs_target = target if os.path.isabs(target) else os.path.join(cwd, target)
                
                if os.path.exists(abs_target):
                    try:
                        with open(abs_target, 'r', encoding='utf-8') as f:
                            original_content = f.read()
                    except Exception:
                        pass
                
                messages = [
                    {"role": "system", "content": "You are a pure code generator. Output ONLY the raw code for the requested file, without markdown formatting or reasoning. You MUST output the ENTIRE file completely rewritten with the changes applied. Do NOT output partial snippets. Do NOT output diffs. Output the FULL file contents from start to finish."},
                    {"role": "user", "content": f"Target: {target}\nDescription: {desc}\n\nOriginal File Content:\n{original_content}\n\nOutput the full raw code."}
                ]
                
                if self.provider:
                    try:
                        resp = self.provider.generate(messages, temperature=0.0)
                        raw_code = resp.get("content", "")
                        # Bersihkan markdown jika LLM masih nakal
                        if raw_code.startswith("```"):
                            lines = raw_code.split("\n")
                            if len(lines) >= 2:
                                # Cari penutup markdown terakhir
                                end_idx = len(lines) - 1
                                while end_idx > 0 and not lines[end_idx].strip() == "```":
                                    end_idx -= 1
                                if end_idx > 0:
                                    raw_code = "\n".join(lines[1:end_idx])
                                else:
                                    raw_code = "\n".join(lines[1:])
                    except Exception as e:
                        raw_code = f"ERROR: {e}"
                else:
                    raw_code = "# Mock Generated Code"
                    
                results.append(TransformationResult(step, raw_code))
            else:
                # Untuk COMMAND atau DELETE, tidak perlu LLM nulis kode
                results.append(TransformationResult(step, ""))
                
        return results
