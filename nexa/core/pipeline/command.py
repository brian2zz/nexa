import subprocess
import os
from typing import Tuple

class CommandPolicy:
    """
    Tugas: Mencegah eksekusi perintah destruktif (rm -rf, format, dsb).
    Mengizinkan eksekusi perintah aman (git, pytest, npm test, dsb).
    """
    BLACKLIST = ["rm -rf", "format", "mkfs", "dd", "shutdown", "reboot"]
    WHITELIST_PREFIXES = ["git", "pytest", "npm", "flutter", "python", "php", "composer", "nexa"]

    @classmethod
    def is_allowed(cls, command: str) -> bool:
        cmd_lower = command.lower().strip()
        
        # Cek Blacklist
        for bad in cls.BLACKLIST:
            if bad in cmd_lower:
                return False
                
        # Cek Whitelist Prefix
        first_word = cmd_lower.split(" ")[0] if " " in cmd_lower else cmd_lower
        if first_word in cls.WHITELIST_PREFIXES:
            return True
            
        # Default policy: Tolak jika tidak ada di whitelist
        return False


class TerminalRunner:
    """
    Tugas: Mengeksekusi perintah shell yang telah diloloskan oleh CommandPolicy.
    """
    def __init__(self, cwd: str):
        self.cwd = cwd
        
    def execute(self, command: str) -> Tuple[bool, str]:
        if not CommandPolicy.is_allowed(command):
            return False, f"Policy Violation: Command '{command}' is not allowed."
            
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=self.cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            output = result.stdout if result.returncode == 0 else result.stderr
            return result.returncode == 0, output
        except Exception as e:
            return False, f"Execution Error: {e}"
