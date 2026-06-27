from .base import BaseTemplate

class PaymentTemplate(BaseTemplate):
    def generate(self, goal, context):
        steps = [{"title": "Setup Payment Gateway Integration", "description": "Configure API keys."}]
        return self.response(goal, "high", "high", steps)
