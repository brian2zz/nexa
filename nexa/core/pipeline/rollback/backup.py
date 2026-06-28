import os
import shutil
from typing import List
from nexa.core.pipeline.rollback.base import RollbackStrategy

class BackupRollbackStrategy(RollbackStrategy):
    def __init__(self, cwd: str):
        self.cwd = cwd
        self.backup_dir = os.path.join(cwd, ".nexa", "backups")
        self.backed_up_files = []
        
    def backup(self, files: List[str]) -> bool:
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            self.backed_up_files = []
            
            for file_path in files:
                abs_path = os.path.join(self.cwd, file_path)
                if os.path.exists(abs_path):
                    backup_path = os.path.join(self.backup_dir, file_path.replace("/", "_").replace("\\", "_"))
                    shutil.copy2(abs_path, backup_path)
                    self.backed_up_files.append((abs_path, backup_path))
            return True
        except Exception as e:
            print(f"[!] Backup Failed: {e}")
            return False
            
    def rollback(self) -> bool:
        try:
            for abs_path, backup_path in self.backed_up_files:
                if os.path.exists(backup_path):
                    shutil.copy2(backup_path, abs_path)
            return True
        except Exception as e:
            print(f"[!] Rollback Failed: {e}")
            return False
            
    def commit(self) -> bool:
        try:
            for _, backup_path in self.backed_up_files:
                if os.path.exists(backup_path):
                    os.remove(backup_path)
            self.backed_up_files = []
            return True
        except Exception as e:
            print(f"[!] Commit Cleanup Failed: {e}")
            return False
