from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum

class ExecutionStrategy(Enum):
    STOP_ON_ERROR = "STOP_ON_ERROR"
    CONTINUE_ON_ERROR = "CONTINUE_ON_ERROR"
    FALLBACK = "FALLBACK"

@dataclass
class IntentRequest:
    """Raw output from LLM Planner."""
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CommandStep:
    """Translated from IntentRequest, ready for execution."""
    id: str
    executable: str
    args: List[str]
    strategy: ExecutionStrategy
    condition: Optional[str] = None
    timeout: int = 60
    risk_level: str = "UNKNOWN"
    cwd: str = ""
    env: Dict[str, str] = field(default_factory=dict)
    
    # Kept for compatibility with audit and runner
    raw_command: str = ""

@dataclass
class ExecutionStage:
    """Logical grouping of steps."""
    name: str
    steps: List[CommandStep] = field(default_factory=list)

@dataclass
class ExecutionPlan:
    """The final plan sent to Approval UI and Pipeline."""
    stages: List[ExecutionStage] = field(default_factory=list)
    estimated_duration: int = 0
    can_rollback: bool = False

@dataclass
class CommandRequest:
    """Legacy model for backward compatibility in policy evaluation."""
    raw_command: str
    executable: str
    args: List[str]
    cwd: str
    env: Dict[str, str] = field(default_factory=dict)
    timeout: int = 60

@dataclass
class CommandResult:
    """Represents the outcome of a terminal command execution."""
    success: bool
    stdout: str
    stderr: str
    returncode: int
    duration: float
    command: str
