from typing import List, Tuple
from nexa.core.pipeline.execution.models import CommandRequest
from nexa.core.pipeline.execution.rules import ValidationRule, ExecutableRule, DangerousFlagRule, WorkspaceRule

class PolicyEngine:
    """
    Evaluates a CommandRequest against a list of ValidationRules.
    """
    
    def __init__(self, rules: List[ValidationRule] = None):
        self.rules = rules or [
            ExecutableRule(),
            DangerousFlagRule(),
            WorkspaceRule()
        ]
        
    def evaluate(self, req: CommandRequest) -> Tuple[bool, str]:
        """
        Returns (True, "") if all rules pass.
        Returns (False, "Error message") if any rule fails.
        """
        for rule in self.rules:
            if not rule.validate(req):
                return False, f"Policy Violation: {rule.get_error()}"
                
        return True, ""
