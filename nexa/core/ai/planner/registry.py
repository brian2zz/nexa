class PlannerRegistry:
    def __init__(self):
        self._templates = []
        self._register_defaults()
        
    def register(self, keywords, template_class):
        self._templates.append({
            "keywords": [k.lower() for k in keywords],
            "template": template_class()
        })
        
    def _register_defaults(self):
        from .templates.auth import AuthTemplate
        from .templates.notification import NotificationTemplate
        from .templates.payment import PaymentTemplate
        from .templates.ui import UITemplate
        from .templates.feature import FeatureTemplate
        from .templates.generic import GenericTemplate
        
        self.register(['auth', 'login', 'register', 'jwt', 'logout'], AuthTemplate)
        self.register(['notification', 'email', 'push', 'alert'], NotificationTemplate)
        self.register(['payment', 'stripe', 'midtrans', 'checkout'], PaymentTemplate)
        self.register(['navbar', 'ui', 'button', 'component', 'modal', 'screen', 'page', 'sidebar', 'footer', 'layout', 'header'], UITemplate)
        
        # We will keep FeatureTemplate and GenericTemplate special cases.
        self.feature_template = FeatureTemplate()
        self.generic_template = GenericTemplate()
        
    def get_template(self, goal):
        goal_lower = goal.lower()
        
        for item in self._templates:
            if any(kw in goal_lower for kw in item['keywords']):
                return item['template']
                
        # Fallback to feature template if it looks like adding a feature
        if 'add' in goal_lower or 'create' in goal_lower or 'build' in goal_lower:
            return self.feature_template
            
        return self.generic_template
