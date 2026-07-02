import json
import re
from typing import Dict, Any, Tuple
from .schema import PlanningResult

class PlanValidator:
    """
    Validates JSON output from the AI and converts it to a PlanningResult.
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

    def validate(self, raw_text: str) -> Tuple[bool, str, PlanningResult]:
        """
        Returns (success, error_message, planning_result).
        """
        json_str = self.extract_json(raw_text)
        try:
            data = json.loads(json_str, strict=False)
        except json.JSONDecodeError as e:
            return False, f"Failed to parse JSON: {str(e)}\nRaw output: {raw_text}", None
            
        required_keys = ['objective', 'work_items']
        missing = [k for k in required_keys if k not in data]
        if missing:
            return False, f"JSON missing required fields: {', '.join(missing)}\nFound keys: {list(data.keys())}\nRaw data: {data}", None
            
        try:
            plan = PlanningResult.from_dict(data)            
            return True, "", plan
            
        except Exception as e:
            return False, f"Unexpected validation error: {str(e)}", None

    def validate_dataclass(self, plan: PlanningResult) -> tuple[bool, str, Any]:
        """
        Validates an already constructed PlanningResult dataclass.
        """
        if not isinstance(plan, PlanningResult):
            return False, "Not a valid PlanningResult object", None
            
        if not plan.goal:
            return False, "Missing goal", None
            
        if not plan.work_items:
            return False, "Missing work_items. AI must define at least one work item.", None
            
        return True, "", plan
