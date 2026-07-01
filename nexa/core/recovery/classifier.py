from typing import Type
from nexa.core.models.recovery import FailureContext, RecoveryPolicy
from nexa.core.recovery.strategy import (
    RecoveryStrategy, 
    RetryToolStrategy, 
    FallbackStrategy, 
    ReflectionStrategy, 
    ReplanningStrategy,
    AskHumanStrategy
)

class FailureClassifier:
    """Diagnoses the failure context and selects the appropriate recovery strategy."""
    
    def __init__(self):
        # Default policies for known failure types
        self.policies = {
            "SyntaxError": RecoveryPolicy(retry_limit=2, requires_reflection=True),
            "LogicError": RecoveryPolicy(retry_limit=1, requires_reflection=True),
            "ToolTimeout": RecoveryPolicy(retry_limit=3, requires_reflection=False),
            "EncodingError": RecoveryPolicy(retry_limit=0, requires_reflection=False, fallback_action="use_latin1"),
            "VerificationFailed": RecoveryPolicy(retry_limit=2, requires_reflection=True),
        }

    def classify(self, context: FailureContext, current_retry_count: int = 0) -> Type[RecoveryStrategy]:
        """Classifies the failure and maps it to a RecoveryStrategy class."""
        policy = self.policies.get(context.failure_type, RecoveryPolicy(retry_limit=1, requires_reflection=True))
        
        # 1. Check if we exceeded retry limits
        if current_retry_count > policy.retry_limit:
            # If we've retried too many times, maybe try a full replan or ask human
            if current_retry_count > policy.retry_limit + 1:
                return AskHumanStrategy
            return ReplanningStrategy
            
        # 2. Select strategy based on policy
        if policy.requires_reflection:
            return ReflectionStrategy
            
        if policy.fallback_action:
            return FallbackStrategy
            
        return RetryToolStrategy
