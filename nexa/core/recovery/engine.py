import datetime
from typing import Dict, Any, Optional
from nexa.core.events.bus import PipelineBus
from nexa.core.models.events import EventContext
from nexa.core.models.enums import EventPriority

from nexa.core.models.recovery import FailureContext, RecoveryRequest, RecoveryResult
from nexa.core.recovery.classifier import FailureClassifier
from nexa.core.recovery.memory import RecoveryMemory

class RecoveryEngine:
    """
    The Immune System of Nexa.
    Subscribes to failure events, diagnoses them, selects strategies, and triggers recovery.
    """
    
    def __init__(self, bus: PipelineBus, workspace_path: str):
        self.bus = bus
        self.classifier = FailureClassifier()
        self.memory = RecoveryMemory(workspace_path)
        
        # Subscribe to all failure boundaries
        self.bus.subscribe("KnowledgeFailed", self.handle_failure)
        self.bus.subscribe("PlanningFailed", self.handle_failure)
        self.bus.subscribe("TransformationFailed", self.handle_failure)
        self.bus.subscribe("PatchFailed", self.handle_failure)
        self.bus.subscribe("ExecutionFailed", self.handle_failure)
        self.bus.subscribe("VerificationFailed", self.handle_failure)

    def handle_failure(self, event: EventContext):
        """Called whenever a pipeline phase fails."""
        payload = event.payload or {}
        
        print(f"\n[!] RECOVERY ENGINE ACTIVATED: {event.event_name}")
        
        # 1. Build Failure Context
        context = FailureContext(
            failure_type=payload.get("failure_type", "UnknownError"),
            error_code=payload.get("error_code", "ERR_UNKNOWN"),
            stack_trace=payload.get("stack_trace", "No stack trace provided"),
            failed_step=event.event_name.replace("Failed", ""),
            workspace_context=payload.get("workspace_context", {}),
            tool_result=payload.get("tool_result"),
            verification_result=payload.get("verification_result")
        )
        
        error_signature = f"{context.failed_step}:{context.failure_type}:{context.error_code}"
        
        # 2. Check Recovery Memory
        historical_strategy = self.memory.recall(error_signature)
        if historical_strategy:
            print(f"[*] Recovery Memory matched! Historical strategy: {historical_strategy}")
        
        # 3. Classify Failure and Select Strategy
        # Simulated retry count for now
        retry_count = payload.get("retry_count", 0) 
        strategy_class = self.classifier.classify(context, retry_count)
        strategy_instance = strategy_class()
        
        print(f"[*] Selected Strategy: {strategy_class.__name__}")
        
        request = RecoveryRequest(
            previous_plan=payload.get("previous_plan", {}),
            failure_context=context
        )
        
        # 4. Execute Strategy
        result: RecoveryResult = strategy_instance.execute(request)
        
        # 5. Memorize Result (if we had a meaningful attempt)
        self.memory.memorize(
            failure_type=context.failure_type,
            error_signature=error_signature,
            strategy=strategy_class.__name__,
            success=result.success
        )
        
        # 6. Publish Recovery Result
        event_name = "RecoverySucceeded" if result.success else "RecoveryFailed"
        self.bus.publish(EventContext(
            event_name=event_name,
            timestamp=datetime.datetime.now().isoformat(),
            source="RecoveryEngine",
            priority=EventPriority.HIGH,
            session_id=event.session_id,
            payload={
                "strategy_used": result.strategy_used,
                "action_taken": result.action_taken,
                "new_plan": result.new_plan
            },
            correlation_id=event.correlation_id
        ))
        
        print(f"[*] Recovery Action Taken: {result.action_taken}\n")
