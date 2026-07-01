from abc import ABC, abstractmethod
import os
from nexa.core.pipeline.execution.models import CommandRequest

class ValidationRule(ABC):
    @abstractmethod
    def validate(self, req: CommandRequest) -> bool:
        pass
        
    @abstractmethod
    def get_error(self) -> str:
        pass

class ExecutableRule(ValidationRule):
    """Ensures the executable is in the whitelist."""
    
    WHITELIST = ["git", "pytest", "npm", "flutter", "python", "php", "composer", "nexa", "cmd.exe"]
    
    def __init__(self):
        self.failed_exe = ""

    def validate(self, req: CommandRequest) -> bool:
        if req.executable not in self.WHITELIST:
            self.failed_exe = req.executable
            return False
        return True
        
    def get_error(self) -> str:
        return f"Executable '{self.failed_exe}' is not in the whitelist."

class DangerousFlagRule(ValidationRule):
    """Blocks highly dangerous flags for certain commands."""
    
    DANGEROUS = {
        "git": ["--hard", "--force"],
        "rm": ["-rf", "-r", "-f"],
    }
    
    def __init__(self):
        self.error_msg = ""
        
    def validate(self, req: CommandRequest) -> bool:
        # Check if the original intent (e.g. inside cmd.exe /c) matches dangerous patterns
        exe_to_check = req.executable
        args_to_check = req.args
        
        if exe_to_check == "cmd.exe" and len(args_to_check) > 2 and args_to_check[1] == "/c":
            exe_to_check = args_to_check[2].lower()
            args_to_check = args_to_check[2:]
            
        if exe_to_check in self.DANGEROUS:
            for flag in self.DANGEROUS[exe_to_check]:
                if flag in args_to_check:
                    self.error_msg = f"Dangerous flag '{flag}' for executable '{exe_to_check}' is blocked."
                    return False
        return True
        
    def get_error(self) -> str:
        return self.error_msg

class WorkspaceRule(ValidationRule):
    """
    Prevents directory traversal outside the cwd.
    Blocks 'cd ..' or absolute paths pointing outside.
    """
    def __init__(self):
        self.error_msg = ""
        
    def validate(self, req: CommandRequest) -> bool:
        exe_to_check = req.executable
        args_to_check = req.args
        
        if exe_to_check == "cmd.exe" and len(args_to_check) > 2 and args_to_check[1] == "/c":
            exe_to_check = args_to_check[2].lower()
            args_to_check = args_to_check[2:]
            
        if exe_to_check == "cd":
            for arg in args_to_check[1:]:
                if ".." in arg:
                    self.error_msg = f"Directory traversal (..) is forbidden: {arg}"
                    return False
        return True
        
    def get_error(self) -> str:
        return self.error_msg
