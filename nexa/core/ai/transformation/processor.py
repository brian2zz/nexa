import re
from .models import TransformationResult, TransformationMode

class ResponseProcessor:
    """
    Parses, validates, and normalizes the raw string response from LLM.
    """
    def process(self, raw_response: str, mode: TransformationMode) -> TransformationResult:
        if not raw_response or not raw_response.strip():
            return TransformationResult(success=False, metadata={"error_message": "Empty response from LLM"})
            
        result = TransformationResult(success=True, operation=mode.value)
        
        # If mode is analyzer type, we just pass the full text as explanation
        if mode in [TransformationMode.EXPLAIN, TransformationMode.SUMMARIZE, TransformationMode.TRANSLATE]:
            result.explanation = raw_response.strip()
            return result
            
        # For code-generating modes, we extract markdown block
        pattern = r"```(?:\w+)?\n(.*?)```"
        match = re.search(pattern, raw_response, re.DOTALL)
        
        if match:
            result.generated_code = match.group(1).strip()
            # Everything before the block can be explanation
            explanation = raw_response[:match.start()].strip()
            if explanation:
                result.explanation = explanation
        else:
            # Format failed (no markdown block found)
            result.success = False
            result.metadata["error_message"] = "No valid markdown code block found in response."
            
        return result
