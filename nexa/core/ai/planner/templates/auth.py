from .base import BaseTemplate

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
