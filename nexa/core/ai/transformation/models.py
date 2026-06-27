from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

class TransformationMode(Enum):
    GENERATE = "generate"
    MODIFY = "modify"
    REFACTOR = "refactor"
    REPAIR = "repair"
    OPTIMIZE = "optimize"
    TRANSLATE = "translate"
    EXPLAIN = "explain"
    SUMMARIZE = "summarize"

@dataclass
class TransformationRequest:
    mode: TransformationMode
    execution_plan: Dict[str, Any]      # The parsed JSON of Execution Plan
    context_bundle: Dict[str, Any]      # The context dict from ContextResolver
    user_instruction: str = ""          # Optional additional instruction
    system_override: str = ""           # Optional system prompt override
    provider_options: Dict[str, Any] = field(default_factory=dict)
    temperature: float = 0.2            # Default low for coding tasks
    timeout: int = 60                   # Timeout in seconds
    max_retries: int = 3                # Number of retries on format failure

@dataclass
class TransformationResult:
    success: bool
    operation: str = ""                 # Type of operation performed
    generated_code: str = ""            # The pure extracted code block
    explanation: str = ""               # LLM's explanation of the code
    warnings: list = field(default_factory=list)
    confidence: float = 0.0             # Extracted or estimated confidence
    
    # Observability Metadata
    metadata: Dict[str, Any] = field(default_factory=lambda: {
        "provider": "unknown",
        "model": "unknown",
        "estimated_tokens": 0,
        "completion_tokens": 0,
        "duration_seconds": 0.0,
        "retry_count": 0,
        "error_message": None
    })
    
    @property
    def error(self) -> Optional[str]:
        return self.metadata.get("error_message")
