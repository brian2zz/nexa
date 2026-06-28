import time
import datetime
from typing import Optional
from .models import TransformationRequest, TransformationResult
from .factory import PromptFactory
from .processor import ResponseProcessor
from nexa.core.ai.providers.base import LLMProvider
from nexa.core.events.bus import PipelineBus
from nexa.core.models.events import EventContext
from nexa.core.models.enums import EventPriority

class TransformationEngine:
    """
    The orchestrator for AI Transformation (Phase 3.2).
    Pure Transformation. No file writing. Handles Retry Policy.
    """
    def __init__(self, provider: LLMProvider, bus: Optional[PipelineBus] = None):
        self.provider = provider
        self.processor = ResponseProcessor()
        self.bus = bus
        
    def transform(self, request: TransformationRequest, session_id: str = "default_session") -> TransformationResult:
        start_time = time.time()
        
        if self.bus:
            self.bus.publish(EventContext(
                event_name="BeforeTransformation",
                timestamp=datetime.datetime.now().isoformat(),
                source="TransformationEngine",
                priority=EventPriority.NORMAL,
                session_id=session_id,
                payload={"mode": request.mode.value}
            ))

        builder = PromptFactory.get_builder(request.mode)
        
        from datetime import datetime as dt
        current_time = dt.now().strftime("%A, %d %B %Y %H:%M:%S")
        time_context = f"[System Info: The current date and time is {current_time}]\n\n"
        
        system_prompt = time_context + builder.build_system_prompt(request)
        user_prompt = builder.build_user_prompt(request)
        
        retries = 0
        max_retries = request.max_retries
        
        last_error = None
        
        while retries <= max_retries:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            try:
                response_data = self.provider.generate(
                    messages=messages,
                    temperature=request.temperature
                )
            except Exception as e:
                response_data = {"content": ""}
                last_error = str(e)
            
            raw_response = response_data.get("content", "")
            
            result = self.processor.process(raw_response, request.mode)
            
            if result.success:
                end_time = time.time()
                duration = round(end_time - start_time, 2)
                # Fill metadata
                result.metadata["provider"] = getattr(self.provider, "name", "unknown")
                result.metadata["duration_seconds"] = duration
                result.metadata["retry_count"] = retries
                
                if self.bus:
                    self.bus.publish(EventContext(
                        event_name="AfterTransformation",
                        timestamp=datetime.datetime.now().isoformat(),
                        source="TransformationEngine",
                        priority=EventPriority.NORMAL,
                        session_id=session_id,
                        duration=duration,
                        payload={"provider": result.metadata["provider"], "retries": retries}
                    ))
                    
                return result
                
            # If failed, prepare for retry
            retries += 1
            last_error = result.error
            
            if self.bus and retries <= max_retries:
                self.bus.publish(EventContext(
                    event_name="RetryStarted",
                    timestamp=datetime.datetime.now().isoformat(),
                    source="TransformationEngine",
                    priority=EventPriority.HIGH,
                    session_id=session_id,
                    payload={"retry_number": retries, "last_error": str(last_error)}
                ))
                
            # Feed the error back into the prompt so LLM learns from its mistake
            user_prompt += f"\n\nSystem Error from previous attempt: {last_error}\nPlease fix the format and try again."
            
        # If we exhausted retries
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        
        failed_result = TransformationResult(success=False, operation=request.mode.value)
        failed_result.metadata["error_message"] = f"Failed after {retries} attempts. Last error: {last_error}"
        failed_result.metadata["retry_count"] = retries
        failed_result.metadata["duration_seconds"] = duration
        failed_result.metadata["provider"] = getattr(self.provider, "name", "unknown")
        
        if self.bus:
            self.bus.publish(EventContext(
                event_name="TransformationFailed",
                timestamp=datetime.datetime.now().isoformat(),
                source="TransformationEngine",
                priority=EventPriority.HIGH,
                session_id=session_id,
                duration=duration,
                payload={"error": str(last_error)}
            ))
            
        return failed_result
