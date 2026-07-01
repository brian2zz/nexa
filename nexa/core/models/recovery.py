from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from nexa.core.models.enums import EventPriority

@dataclass
class FailureContext:
    """Represents the context of a failure from any phase of the pipeline."""
    failure_type: str        # e.g., 'SyntaxError', 'ToolTimeout', 'EncodingError'
    error_code: str          # e.g., 'ERR_PARSE', 'ERR_TOOL_001'
    stack_trace: str         # The raw error message or stack trace
    failed_step: str         # Phase name: Knowledge, Planner, Transformation, Patch, Execution, Verification
    workspace_context: Dict[str, Any] = field(default_factory=dict)
    tool_result: Optional[str] = None
    verification_result: Optional[str] = None

@dataclass
class RecoveryPolicy:
    """Defines how a specific type of failure should be handled."""
    retry_limit: int = 0
    requires_reflection: bool = False
    fallback_action: Optional[str] = None

@dataclass
class RecoveryRequest:
    """The request object passed to the Recovery Engine."""
    previous_plan: Dict[str, Any]
    failure_context: FailureContext
    knowledge_bundle: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RecoveryResult:
    """The outcome of the Recovery Strategy."""
    success: bool
    strategy_used: str
    new_plan: Optional[Dict[str, Any]] = None
    action_taken: str = ""
    error_message: Optional[str] = None
