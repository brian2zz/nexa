from dataclasses import dataclass
from typing import Optional
from .schema import ExecutionPlan
from .formatter import PlanFormatter

@dataclass
class PlannerReport:
    """
    Wrapper for the result of the AI Planning Engine.
    """
    success: bool
    error_message: str
    plan: Optional[ExecutionPlan] = None
    
    def to_markdown(self) -> str:
        if not self.success:
            return f"❌ **Planning Failed:**\n{self.error_message}"
        if not self.plan:
            return "❌ **Planning Failed:** No plan generated."
            
        formatter = PlanFormatter()
        return formatter.to_markdown(self.plan)
        
    def to_json(self, pretty=True) -> str:
        if not self.success or not self.plan:
            import json
            return json.dumps({"success": False, "error": self.error_message})
        formatter = PlanFormatter()
        return formatter.to_json(self.plan, pretty)
