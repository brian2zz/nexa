import time
from .models import TransformationRequest, TransformationResult
from .factory import PromptFactory
from .processor import ResponseProcessor
from nexa.core.ai.providers.base import LLMProvider

class TransformationEngine:
    """
    The orchestrator for AI Transformation (Phase 3.2).
    Pure Transformation. No file writing. Handles Retry Policy.
    """
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.processor = ResponseProcessor()
        
    def transform(self, request: TransformationRequest) -> TransformationResult:
        builder = PromptFactory.get_builder(request.mode)
        
        system_prompt = builder.build_system_prompt(request)
        user_prompt = builder.build_user_prompt(request)
        
        retries = 0
        max_retries = request.max_retries
        
        start_time = time.time()
        last_error = None
        
        while retries <= max_retries:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response_data = self.provider.generate(
                messages=messages,
                temperature=request.temperature
            )
            
            raw_response = response_data.get("content", "")
            
            result = self.processor.process(raw_response, request.mode)
            
            if result.success:
                end_time = time.time()
                # Fill metadata
                result.metadata["provider"] = getattr(self.provider, "name", "unknown")
                result.metadata["duration_seconds"] = round(end_time - start_time, 2)
                result.metadata["retry_count"] = retries
                return result
                
            # If failed, prepare for retry
            retries += 1
            last_error = result.error
            # Feed the error back into the prompt so LLM learns from its mistake
            user_prompt += f"\n\nSystem Error from previous attempt: {last_error}\nPlease fix the format and try again."
            
        # If we exhausted retries
        end_time = time.time()
        failed_result = TransformationResult(success=False, operation=request.mode.value)
        failed_result.metadata["error_message"] = f"Failed after {retries} attempts. Last error: {last_error}"
        failed_result.metadata["retry_count"] = retries
        failed_result.metadata["duration_seconds"] = round(end_time - start_time, 2)
        failed_result.metadata["provider"] = getattr(self.provider, "name", "unknown")
        
        return failed_result
