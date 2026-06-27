from .registry import PlannerRegistry

class Planner:
    def __init__(self):
        self.registry = PlannerRegistry()
        
    def plan(self, goal: str, context: dict = None) -> dict:
        context = context or {}
        template = self.registry.get_template(goal)
        return template.generate(goal, context)
