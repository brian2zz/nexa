import uuid
import os
from typing import Optional
from nexa.core.pipeline.execution.models import IntentRequest, CommandStep, ExecutionStrategy
from nexa.core.pipeline.execution.parser import CommandParser

class CommandResolver:
    """
    Translates abstract IntentRequests from the LLM into concrete CommandSteps
    that the OS can execute.
    """
    
    def __init__(self, cwd: str):
        self.cwd = cwd
        self.parser = CommandParser()
        
    def resolve(self, intent: IntentRequest, strategy: ExecutionStrategy = ExecutionStrategy.STOP_ON_ERROR) -> Optional[CommandStep]:
        step_id = f"step_{uuid.uuid4().hex[:8]}"
        
        # 1. Fallback Intent: terminal_command
        # This is for backward compatibility and to handle raw strings during migration
        if intent.action == "terminal_command":
            raw_cmd = intent.parameters.get("command", "")
            success, err, reqs = self.parser.parse_all(raw_cmd, self.cwd)
            if success and reqs:
                # Just take the first parsed command for now if it's a direct fallback
                _, req = reqs[0]
                return CommandStep(
                    id=step_id,
                    executable=req.executable,
                    args=req.args,
                    strategy=strategy,
                    cwd=req.cwd,
                    env=req.env,
                    raw_command=req.raw_command
                )
            return None
            
        # 2. Specific Domain Intents (Example integrations for future)
        if intent.action == "git_add":
            path = intent.parameters.get("path", ".")
            return CommandStep(
                id=step_id,
                executable="git",
                args=["add", path],
                strategy=strategy,
                cwd=self.cwd,
                env=os.environ.copy(),
                raw_command=f"git add {path}"
            )
            
        if intent.action == "git_commit":
            message = intent.parameters.get("message", "Auto-commit")
            return CommandStep(
                id=step_id,
                executable="git",
                args=["commit", "-m", message],
                strategy=strategy,
                cwd=self.cwd,
                env=os.environ.copy(),
                raw_command=f"git commit -m '{message}'"
            )
            
        if intent.action == "file_delete":
            path = intent.parameters.get("path", "")
            return CommandStep(
                id=step_id,
                executable="cmd.exe",
                args=["/c", "del", path],
                strategy=strategy,
                cwd=self.cwd,
                env=os.environ.copy(),
                raw_command=f"del {path}"
            )
            
        # If we reach here, the intent is unknown
        return None
