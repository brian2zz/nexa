import json
import re
from typing import Dict, Any, Tuple
from .schema import ExecutionPlan

class PlanValidator:
    """
    Validates JSON output from the AI and converts it to an ExecutionPlan.
    """
    def extract_json(self, text: str) -> str:
        """Extract JSON block from markdown if present."""
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            return match.group(1)
            
        # Fallback: find the first { and last }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            return text[start:end+1]
            
        return text

    def validate(self, raw_text: str) -> Tuple[bool, str, ExecutionPlan]:
        """
        Returns (success, error_message, execution_plan).
        """
        json_str = self.extract_json(raw_text)
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            return False, f"Failed to parse JSON: {str(e)}\nRaw output: {raw_text}", None
            
        # Required fields check
        required_keys = ['goal', 'summary', 'execution_steps']
        missing = [k for k in required_keys if k not in data]
        if missing:
            return False, f"JSON missing required fields: {', '.join(missing)}", None
            
        try:
            plan = ExecutionPlan.from_dict(data)
            return True, "", plan
        except Exception as e:
            return False, f"Failed to map JSON to ExecutionPlan: {str(e)}", None
