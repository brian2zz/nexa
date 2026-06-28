import os
from typing import List
from nexa.core.pipeline.transformation import TransformationResult

class PatchResult:
    def __init__(self, target: str, action: str, content: str = "", command: str = ""):
        self.target = target
        self.action = action
        self.content = content
        self.command = command

class PatchEngine:
    """
    Tugas: Mengubah TransformationResult (kode mentah) menjadi PatchResult yang siap diaplikasikan.
    Di sini kalkulasi diff/merge bisa dilakukan secara deterministik.
    """
    def calculate(self, transform_results: List[TransformationResult]) -> List[PatchResult]:
        patches = []
        for tr in transform_results:
            action = tr.step.get("action", "").upper()
            target = tr.step.get("target", "")
            
            if action in ["CREATE", "MODIFY"]:
                patches.append(PatchResult(target=target, action=action, content=tr.raw_code))
            elif action == "DELETE":
                patches.append(PatchResult(target=target, action=action))
            elif action == "COMMAND":
                patches.append(PatchResult(target=target, action=action, command=tr.step.get("description", "")))
                
        return patches

class PatchApplier:
    """
    Tugas: Menerapkan ApprovedPatch ke Filesystem.
    """
    def __init__(self, cwd: str):
        self.cwd = cwd
        
    def apply(self, patch: PatchResult) -> bool:
        target_path = os.path.join(self.cwd, patch.target)
        
        try:
            if patch.action in ["CREATE", "MODIFY"]:
                # Pastikan direktori ada
                os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(patch.content)
            elif patch.action == "DELETE":
                if os.path.exists(target_path):
                    os.remove(target_path)
            return True
        except Exception as e:
            print(f"[!] Gagal menerapkan patch ke {patch.target}: {e}")
            return False
