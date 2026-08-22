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
                params = intent.get("parameters", {})
                target = params.get("target") or \
                         params.get("path") or \
                         params.get("command") or ""
                         
                steps.append({
                    "action": intent.get("action", ""),
                    "target": target,
                    "description": intent.get("description", ""),
                    "content": params.get("content", "")
                })
        
        for step in steps:
            action = step.get("action", "").upper()
            target = step.get("target", "")
            desc = step.get("description", "")
            preset_content = step.get("content", "")

            # If preset content is already provided (e.g. extracted YAML for nexa.yaml), use it directly
            if preset_content:
                results.append(TransformationResult(step, preset_content))
                continue

            if action in ["CREATE", "MODIFY"]:
                # Kirim prompt statis ke LLM untuk mendapatkan kodenya saja
                import os
                
                # Baca file asli jika ada
                original_content = ""
                abs_target = target if os.path.isabs(target) else os.path.join(cwd, target)
                
                if os.path.exists(abs_target):
                    try:
                        with open(abs_target, 'r', encoding='utf-8') as f:
                            original_content = f.read()
                    except Exception:
                        pass
                
                # Fallback to CREATE if file does not exist yet on disk
                if action == "MODIFY" and not original_content:
                    action = "CREATE"
                    step["action"] = "CREATE"

                # --- AST Patch Engine: SEARCH/REPLACE Block Format ---
                # For MODIFY: LLM only returns changed blocks, not full file.
                # For CREATE: LLM returns full file (no choice here, it's new).
                if action == "MODIFY":
                        
                    system_msg = (
                        "You are a precise code patch generator.\n"
                        "You will be given a file and a description of what to change.\n"
                        "You MUST output ONLY the specific SEARCH/REPLACE blocks for the changes, in this EXACT format:\n\n"
                        "<<<< SEARCH\n"
                        "... exact original lines to find ...\n"
                        "====\n"
                        "... new replacement lines ...\n"
                        ">>>> REPLACE\n\n"
                        "RULES:\n"
                        "1. SEARCH block must match the original file EXACTLY (whitespace included).\n"
                        "2. You can have MULTIPLE blocks if changing multiple locations.\n"
                        "3. Output NOTHING else — no explanations, no markdown, no extra text.\n"
                        "4. Keep search blocks as SHORT as possible (only the lines you are changing + 1-2 lines of context)."
                    )
                    user_msg = f"Target: {target}\nChange Description: {desc}\n\nOriginal File Content:\n{original_content}\n\nOutput SEARCH/REPLACE blocks ONLY."
                else:
                    system_msg = (
                        "You are a pure code generator.\n"
                        "Output ONLY the complete raw code for the new file, without any markdown formatting, explanations, or reasoning."
                    )
                    user_msg = f"Target: {target}\nDescription: {desc}\n\nOutput the full raw code."
                    
                messages = [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
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
