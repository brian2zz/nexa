import shlex
import os
from typing import Tuple, List
from nexa.core.pipeline.execution.models import CommandRequest

class CommandParser:
    """
    Parses a raw command string into secure CommandRequest(s).
    Properly handles sequential operators (&&, ;) to allow multi-step commands
    without relying on insecure shell=True evaluation.
    Rejects dangerous redirect operators (|, >, <).
    Handles Windows built-in commands by wrapping them with cmd.exe /c.
    """
    
    # Operators we will handle explicitly by splitting
    CHAIN_OPERATORS = ["&&", ";"]
    
    # Operators we strictly forbid (no pipes or file redirects for now for max security)
    FORBIDDEN_OPERATORS = ["||", "|", ">", "<", ">>", "<<"]
    
    WINDOWS_BUILTINS = [
        "del", "rm", "mkdir", "md", "cp", "copy", "mv", "move", 
        "dir", "ls", "echo", "type", "cat", "cd"
    ]
    
    def parse(self, raw_command: str, cwd: str, env: dict = None) -> Tuple[bool, str, CommandRequest]:
        """Legacy parse method for single commands. Kept for backward compatibility."""
        success, err, reqs = self.parse_all(raw_command, cwd, env)
        if not success or not reqs:
            return False, err, None
        if len(reqs) > 1:
            return False, "Multiple commands detected but single command expected.", None
        return True, "", reqs[0][1]

    def parse_all(self, raw_command: str, cwd: str, env: dict = None) -> Tuple[bool, str, List[Tuple[str, CommandRequest]]]:
        """
        Parses a chain of commands.
        Returns: (success, error_msg, [(operator, CommandRequest), ...])
        """
        if not raw_command or not raw_command.strip():
            return False, "Command is empty.", []
            
        try:
            tokens = shlex.split(raw_command, posix=False)
        except ValueError as e:
            return False, f"Syntax Error (unmatched quotes): {e}", []
            
        if not tokens:
            return False, "Command parsed to empty tokens.", []
            
        # 1. Shell Injection Check for Forbidden Operators
        for token in tokens:
            if any(op in token for op in self.FORBIDDEN_OPERATORS):
                return False, f"Shell Injection Detected: Token '{token}' contains restricted shell operators (pipes/redirects are blocked).", []
                
        # 2. Split by CHAIN_OPERATORS
        commands = []
        current_op = ""
        current_args = []
        
        # A little helper to process collected args
        def flush_command():
            if not current_args:
                return True, ""
                
            executable = current_args[0].lower()
            args = list(current_args)
            
            if executable in self.WINDOWS_BUILTINS:
                args = ["cmd.exe", "/c"] + args
                executable = "cmd.exe"
                
            clean_args = [arg.strip('"\'') for arg in args]
            
            req = CommandRequest(
                raw_command=" ".join(current_args),
                executable=executable,
                args=clean_args,
                cwd=cwd,
                env=env or os.environ.copy()
            )
            commands.append((current_op, req))
            current_args.clear()
            return True, ""

        for token in tokens:
            if token in self.CHAIN_OPERATORS:
                flush_command()
                current_op = token
            else:
                current_args.append(token)
                
        flush_command()
        
        return True, "", commands
