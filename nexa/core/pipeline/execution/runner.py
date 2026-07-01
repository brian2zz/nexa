import subprocess
import time
from typing import Optional
from nexa.core.pipeline.execution.models import CommandRequest, CommandResult

class TerminalRunner:
    """
    The secure, simplified executor. 
    Only receives parsed CommandRequests.
    NEVER uses shell=True directly (unless cmd.exe is explicitly passed as the executable).
    """
    
    def execute(self, req: CommandRequest) -> CommandResult:
        start_time = time.time()
        
        try:
            # We strictly pass args as a list. shell=False is the default and mandated.
            # Since the parser ensures req.args is a full list containing the executable as the first element,
            # we just pass req.args as the first argument.
            result = subprocess.run(
                req.args,
                shell=False,
                cwd=req.cwd,
                env=req.env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=req.timeout
            )
            
            duration = time.time() - start_time
            return CommandResult(
                success=(result.returncode == 0),
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode,
                duration=duration,
                command=req.raw_command
            )
            
        except subprocess.TimeoutExpired as e:
            duration = time.time() - start_time
            return CommandResult(
                success=False,
                stdout=e.stdout.decode('utf-8', 'replace') if e.stdout else "",
                stderr=e.stderr.decode('utf-8', 'replace') if e.stderr else f"Timeout reached ({req.timeout}s).",
                returncode=-1,
                duration=duration,
                command=req.raw_command
            )
        except Exception as e:
            duration = time.time() - start_time
            return CommandResult(
                success=False,
                stdout="",
                stderr=f"Execution Error: {str(e)}",
                returncode=-1,
                duration=duration,
                command=req.raw_command
            )
