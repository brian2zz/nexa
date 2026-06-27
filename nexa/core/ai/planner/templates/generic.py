from .base import BaseTemplate

class GenericTemplate(BaseTemplate):
    def generate(self, goal, context):
        steps = [
            {"title": "Analyze Requirements", "description": "Understand what needs to be changed."},
            {"title": "Implement Feature", "description": "Write code to fulfill the requirement."},
            {"title": "Test Implementation", "description": "Ensure the feature works as expected."}
        ]
        return self.response(goal, "medium", "low", steps)
