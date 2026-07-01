from nexa.core.pipeline.execution.models import CommandStep, CommandRequest
from typing import Union

class RiskAnalyzer:
    """
    Analyzes a CommandStep (or CommandRequest) and assigns a risk score.
    """
    
    # Executables that are inherently read-only or low risk
    LOW_RISK = ["git status", "git log", "pytest", "python --version", "php -v", "dir", "ls", "echo", "type", "cat"]
    
    # Executables that modify state locally
    MEDIUM_RISK = ["npm", "composer", "flutter", "python", "php", "mkdir", "md", "cp", "copy", "mv", "move", "del", "rm", "git add", "git commit"]
    
    # Executables that affect remote state or major structural changes
    HIGH_RISK = ["git push", "git pull", "git merge", "git rebase"]
    
    # Executables that are highly destructive
    CRITICAL_RISK = ["git reset --hard", "git clean -fd"]
    
    def analyze(self, req: Union[CommandRequest, CommandStep]) -> str:
        """Returns LOW, MEDIUM, HIGH, or CRITICAL."""
        
        exe = req.executable
        args_str = " ".join(req.args).lower()
        full_cmd = f"{exe} {args_str}".strip()
        
        risk = "UNKNOWN"
        
        # Check CRITICAL
        for crit in self.CRITICAL_RISK:
            if full_cmd.startswith(crit):
                risk = "CRITICAL"
                break
                
        # Check HIGH
        if risk == "UNKNOWN":
            for high in self.HIGH_RISK:
                if full_cmd.startswith(high):
                    risk = "HIGH"
                    break
                    
        # Check LOW
        if risk == "UNKNOWN":
            for low in self.LOW_RISK:
                if full_cmd.startswith(low):
                    risk = "LOW"
                    break
                    
        # Default for known mutating tools is MEDIUM
        if risk == "UNKNOWN":
            if exe in ["cmd.exe", "npm", "composer", "flutter", "python", "php", "git"]:
                risk = "MEDIUM"
                
        # If the input is a CommandStep, inject the risk directly
        if isinstance(req, CommandStep):
            req.risk_level = risk
            
        return risk
