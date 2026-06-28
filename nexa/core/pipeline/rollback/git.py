import subprocess
from typing import List
from nexa.core.pipeline.rollback.base import RollbackStrategy

class GitRollbackStrategy(RollbackStrategy):
    def __init__(self, cwd: str):
        self.cwd = cwd
        
    def backup(self, files: List[str]) -> bool:
        # Dalam strategi Git, kita bisa menggunakan git stash atau tidak sama sekali
        # karena perubahannya bisa di-reset.
        # Untuk kesederhanaan, kita anggap file sudah dalam pantauan Git (git status bersih).
        return True
        
    def rollback(self) -> bool:
        try:
            subprocess.run(["git", "reset", "--hard"], cwd=self.cwd, check=True)
            return True
        except Exception as e:
            print(f"[!] Git Rollback Failed: {e}")
            return False
            
    def commit(self) -> bool:
        # Tidak ada yang perlu dibersihkan untuk GitRollback
        return True
