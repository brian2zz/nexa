import os
import shutil

base_dir = "g:/project code/nexa"
planner_dir = os.path.join(base_dir, "nexa/core/ai/planner")
old_planner_file = os.path.join(base_dir, "nexa/core/ai/planner.py")

# Remove old file if it exists
if os.path.exists(old_planner_file):
    os.remove(old_planner_file)

# Create new directory structure
os.makedirs(os.path.join(planner_dir, "templates"), exist_ok=True)

# 1. nexa/core/ai/planner/__init__.py
init_content = "from .planner import Planner\nfrom .registry import PlannerRegistry\n"
with open(os.path.join(planner_dir, "__init__.py"), "w", encoding='utf-8') as f: f.write(init_content)

# 2. nexa/core/ai/planner/planner.py
planner_content = """from .registry import PlannerRegistry

class Planner:
    def __init__(self):
        self.registry = PlannerRegistry()
        
    def plan(self, goal: str, context: dict = None) -> dict:
        context = context or {}
        template = self.registry.get_template(goal)
        return template.generate(goal, context)
"""
with open(os.path.join(planner_dir, "planner.py"), "w", encoding='utf-8') as f: f.write(planner_content)

# 3. nexa/core/ai/planner/registry.py
registry_content = """class PlannerRegistry:
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
"""
with open(os.path.join(planner_dir, "registry.py"), "w", encoding='utf-8') as f: f.write(registry_content)

# 4. nexa/core/ai/planner/templates/__init__.py
with open(os.path.join(planner_dir, "templates", "__init__.py"), "w", encoding='utf-8') as f: f.write("")

# 5. nexa/core/ai/planner/templates/base.py
base_content = """class BaseTemplate:
    def generate(self, goal: str, context: dict) -> dict:
        raise NotImplementedError("Template must implement generate method")
        
    def response(self, goal: str, complexity: str, risk: str, steps: list) -> dict:
        return {
            "goal": goal,
            "complexity": complexity,
            "risk": risk,
            "steps": steps
        }
"""
with open(os.path.join(planner_dir, "templates", "base.py"), "w", encoding='utf-8') as f: f.write(base_content)

# 6. nexa/core/ai/planner/templates/auth.py
auth_content = """from .base import BaseTemplate

class AuthTemplate(BaseTemplate):
    def generate(self, goal, context):
        framework = context.get('framework', 'unknown').lower()
        steps = []
        
        if framework in ['reactjs', 'nextjs', 'vuejs', 'nuxtjs', 'react_native']:
            steps = [
                {"title": "Setup AuthContext", "description": "Manage JWT tokens and user session in context."},
                {"title": "Create authService", "description": "API calls to login/register endpoints."},
                {"title": "Create Login and Register Forms", "description": "Build UI and handle form validation."}
            ]
        elif framework == 'flutter':
            steps = [
                {"title": "Setup AuthProvider / AuthController", "description": "Manage token using SharedPreferences."},
                {"title": "Create AuthService", "description": "Handle HTTP requests for authentication."},
                {"title": "Build Login Screen", "description": "Form widget with validation."}
            ]
        elif framework == 'nexaphp':
            steps = [
                {"title": "Create Auth Module", "description": "Scaffold auth module directory structure."},
                {"title": "Create User Entity", "description": "Database schema for users."},
                {"title": "Create Auth Controller", "description": "Handle API login and JWT generation."},
                {"title": "Register Auth Routes", "description": "Add routes for login and register."}
            ]
        elif framework in ['laravel', 'django', 'fastapi']:
            steps = [
                {"title": "Create User Model/Entity", "description": "Database schema for users."},
                {"title": "Create Auth Controller", "description": "Handle API login and JWT generation."},
                {"title": "Add Auth Middleware", "description": "Protect private routes from unauthorized access."}
            ]
        else:
            steps = [
                {"title": "Setup Authentication Library", "description": "Install JWT or Session based auth library."},
                {"title": "Create User Model", "description": "Define user schema with email and hashed password."},
                {"title": "Create Auth Controllers", "description": "Implement register, login, and logout endpoints."}
            ]
            
        return self.response(goal, "medium", "medium", steps)
"""
with open(os.path.join(planner_dir, "templates", "auth.py"), "w", encoding='utf-8') as f: f.write(auth_content)

# 7. nexa/core/ai/planner/templates/ui.py
ui_content = """from .base import BaseTemplate

class UITemplate(BaseTemplate):
    def generate(self, goal, context):
        framework = context.get('framework', 'unknown').lower()
        component_name = goal.title().replace('Add ', '').replace('Create ', '').replace(' ', '')
        steps = []
        
        if framework in ['reactjs', 'nextjs', 'vuejs', 'nuxtjs', 'react_native']:
            ext = ".vue" if "vue" in framework else ".jsx"
            steps = [
                {"title": f"Create {component_name}{ext}", "description": "Create the new UI component file."},
                {"title": "Integrate with Layout", "description": "Place the component in the main layout or specific page."},
                {"title": "Add Interaction Elements", "description": "Add sub-components like switchers, buttons, or links."},
                {"title": "Update State/Store", "description": "Update relevant context, Vuex, or Redux store if interaction is needed."}
            ]
        elif framework == 'flutter':
            steps = [
                {"title": f"Create {component_name}Widget", "description": "Create the stateless or stateful widget."},
                {"title": "Integrate with Screen", "description": "Add widget to the target screen."},
                {"title": "Bind Controller", "description": "Connect UI interactions to state controller."}
            ]
        elif framework in ['nexaphp', 'laravel', 'django', 'fastapi']:
            steps = [
                {"title": "Create Template View", "description": "Create HTML/Blade/Twig/Django template file."},
                {"title": "Update Base Layout", "description": "Include the new UI element in the base layout."},
                {"title": "Pass Data from Controller", "description": "Ensure backend route passes necessary data to the view."}
            ]
        else:
            steps = [
                {"title": "Create UI Element", "description": "Write HTML and CSS for the new element."},
                {"title": "Add Interactivity", "description": "Write vanilla JS to handle events."}
            ]
            
        return self.response(goal, "low", "low", steps)
"""
with open(os.path.join(planner_dir, "templates", "ui.py"), "w", encoding='utf-8') as f: f.write(ui_content)

# 8. nexa/core/ai/planner/templates/feature.py
feature_content = """from .base import BaseTemplate

class FeatureTemplate(BaseTemplate):
    def generate(self, goal, context):
        framework = context.get('framework', 'unknown').lower()
        arch = context.get('architecture', [])
        
        steps = []
        
        if framework == 'nexaphp':
            steps.append({"title": "Create Module Directory", "description": "Scaffold feature module."})
            steps.append({"title": "Create Controller", "description": "Handle incoming requests."})
            if "Service Layer" in arch or True:
                steps.append({"title": "Create Service", "description": "Implement core business logic."})
            if "Repository Pattern" in arch or True:
                steps.append({"title": "Create Repository", "description": "Handle database queries."})
            steps.append({"title": "Create Entity", "description": "Define data structure."})
            steps.append({"title": "Register Routes", "description": "Map API endpoints."})
            
        elif framework == 'laravel':
            steps.append({"title": "Create Database Migration", "description": "Create migration for the new feature."})
            steps.append({"title": "Create Model", "description": "Define relationships and fillables."})
            steps.append({"title": "Create Controller", "description": "Expose web/api routes."})
            if "Service Layer" in arch:
                steps.append({"title": "Create Service Class", "description": "Extract logic from controller."})
                
        elif 'django' in framework:
            steps.append({"title": "Define Model", "description": "Add new model in models.py and run makemigrations."})
            steps.append({"title": "Create Serializer", "description": "Create DRF serializer if API is needed."})
            steps.append({"title": "Create View/ViewSet", "description": "Implement the business logic in views."})
            if "Service Layer" in arch:
                steps.append({"title": "Create Service Function", "description": "Extract complex logic from view."})
            steps.append({"title": "Register URLs", "description": "Map the view to urls.py."})
            
        elif framework in ['reactjs', 'nextjs', 'vuejs', 'nuxtjs']:
            steps.append({"title": "Define API Interface", "description": "Create service/api client methods."})
            if "Custom Hooks" in arch:
                steps.append({"title": "Create Custom Hook / Composable", "description": "Extract logic for data fetching."})
            steps.append({"title": "Build Component", "description": "Create the UI to consume the data."})
            if "Context API" in arch:
                steps.append({"title": "Update Context", "description": "Expose feature state globally."})
                
        elif framework == 'flutter':
            steps.append({"title": "Create Data Model", "description": "Define Dart class with fromJson/toJson."})
            steps.append({"title": "Create Repository/Service", "description": "Implement API fetching logic."})
            steps.append({"title": "Create Controller/Provider", "description": "Manage state for the UI."})
            steps.append({"title": "Build Screen", "description": "Consume the state in Flutter UI."})
            
        else:
            steps.append({"title": "Define Schema", "description": "Create models/migrations."})
            steps.append({"title": "Implement Logic", "description": "Create controller/service."})
            steps.append({"title": "Build UI", "description": "Integrate feature in frontend."})
            
        return self.response(goal, "medium", "medium", steps)
"""
with open(os.path.join(planner_dir, "templates", "feature.py"), "w", encoding='utf-8') as f: f.write(feature_content)

# 9. nexa/core/ai/planner/templates/generic.py
generic_content = """from .base import BaseTemplate

class GenericTemplate(BaseTemplate):
    def generate(self, goal, context):
        steps = [
            {"title": "Analyze Requirements", "description": "Understand what needs to be changed."},
            {"title": "Implement Feature", "description": "Write code to fulfill the requirement."},
            {"title": "Test Implementation", "description": "Ensure the feature works as expected."}
        ]
        return self.response(goal, "medium", "low", steps)
"""
with open(os.path.join(planner_dir, "templates", "generic.py"), "w", encoding='utf-8') as f: f.write(generic_content)

# 10. nexa/core/ai/planner/templates/notification.py
notification_content = """from .base import BaseTemplate

class NotificationTemplate(BaseTemplate):
    def generate(self, goal, context):
        steps = [{"title": "Setup Notification Provider", "description": "Integrate SMTP/FCM."}]
        return self.response(goal, "low", "low", steps)
"""
with open(os.path.join(planner_dir, "templates", "notification.py"), "w", encoding='utf-8') as f: f.write(notification_content)

# 11. nexa/core/ai/planner/templates/payment.py
payment_content = """from .base import BaseTemplate

class PaymentTemplate(BaseTemplate):
    def generate(self, goal, context):
        steps = [{"title": "Setup Payment Gateway Integration", "description": "Configure API keys."}]
        return self.response(goal, "high", "high", steps)
"""
with open(os.path.join(planner_dir, "templates", "payment.py"), "w", encoding='utf-8') as f: f.write(payment_content)

print("Scaffolding V4 complete!")
