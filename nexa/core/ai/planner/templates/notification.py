from .base import BaseTemplate

class NotificationTemplate(BaseTemplate):
    def generate(self, goal, context):
        steps = [{"title": "Setup Notification Provider", "description": "Integrate SMTP/FCM."}]
        return self.response(goal, "low", "low", steps)
