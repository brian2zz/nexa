from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from nexa.core.models.recovery import RecoveryRequest, RecoveryResult

class RecoveryStrategy(ABC):
    """Base class for all recovery strategies."""
    
    @abstractmethod
    def execute(self, request: RecoveryRequest) -> RecoveryResult:
        """Executes the specific recovery strategy."""
        pass

class RetryToolStrategy(RecoveryStrategy):
    """Strategy to retry a failed tool execution without LLM reflection."""
    
    def execute(self, request: RecoveryRequest) -> RecoveryResult:
        # For example, handle a ToolTimeout
        return RecoveryResult(
            success=False, 
            strategy_used="RetryToolStrategy",
            action_taken="Retried tool execution (Simulation)"
        )

class FallbackStrategy(RecoveryStrategy):
    """Strategy to use a fallback mechanism (e.g., fallback encoding) without LLM reflection."""
    
    def execute(self, request: RecoveryRequest) -> RecoveryResult:
        return RecoveryResult(
            success=False,
            strategy_used="FallbackStrategy",
            action_taken="Applied fallback action (Simulation)"
        )

class ReflectionStrategy(RecoveryStrategy):
    """Strategy that triggers the LLM to reflect and fix the issue (e.g., Syntax Error)."""
    
    def execute(self, request: RecoveryRequest) -> RecoveryResult:
        # Here we would call the LLM with the Reflection Prompt
        return RecoveryResult(
            success=False,
            strategy_used="ReflectionStrategy",
            action_taken="Triggered Reflection Engine (Simulation)"
        )

class ReplanningStrategy(RecoveryStrategy):
    """Strategy that aborts current plan and requests the Planner to start over."""
    
    def execute(self, request: RecoveryRequest) -> RecoveryResult:
        return RecoveryResult(
            success=False,
            strategy_used="ReplanningStrategy",
            action_taken="Triggered full Replanning (Simulation)"
        )

class AskHumanStrategy(RecoveryStrategy):
    """Strategy that escalates the failure to the user via Approval UI."""
    
    def execute(self, request: RecoveryRequest) -> RecoveryResult:
        return RecoveryResult(
            success=False,
            strategy_used="AskHumanStrategy",
            action_taken="Escalated to Human Approval UI"
        )
