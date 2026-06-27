class BaseTemplate:
    def generate(self, goal: str, context: dict) -> dict:
        raise NotImplementedError("Template must implement generate method")
        
    def response(self, goal: str, complexity: str, risk: str, steps: list) -> dict:
        return {
            "goal": goal,
            "complexity": complexity,
            "risk": risk,
            "steps": steps
        }
