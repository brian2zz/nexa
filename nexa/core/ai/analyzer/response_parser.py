import json
import re
from typing import Dict, Any, Tuple

class ResponseParser:
    """
    Extracts, repairs, parses, and validates JSON from the Provider response.
    """
    
    def parse(self, raw_response: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        Returns (is_valid, parsed_json_or_empty, error_message)
        """
        # 1. Extract JSON block if it's wrapped in markdown ```json ... ```
        extracted = raw_response
        match = re.search(r'```(?:json)?(.*?)```', raw_response, re.DOTALL)
        if match:
            extracted = match.group(1).strip()
            
        # 2. Try parse
        try:
            parsed = json.loads(extracted)
            return True, parsed, ""
        except json.JSONDecodeError as e:
            # 3. Simple repair attempts could go here (e.g. trailing commas)
            # For now, we just fail gracefully and let the orchestrator retry
            return False, {}, f"Invalid JSON format. Error: {str(e)}"
