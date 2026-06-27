from .base import BaseTemplate

class FeatureTemplate(BaseTemplate):
    def generate(self, goal, context):
        framework = context.get('framework', 'unknown').lower()
        arch = context.get('architecture', [])
        important_files = context.get('important_files', [])
        
        goal_words = set(goal.lower().split())
        
        steps = []
        
        # Heuristic: Find important files that might be related to the goal
        related_files = []
        for file_path in important_files:
            file_name_lower = file_path.lower()
            if any(word in file_name_lower for word in goal_words if len(word) > 3):
                related_files.append(file_path.split('/')[-1].split('\\')[-1])
                
        # Inject dynamic context-aware steps if related files are found
        if related_files:
            for file in related_files:
                if 'Registry' in file or 'Config' in file:
                    steps.append({"title": f"Register Feature in {file}", "description": f"Add the new module/component to {file}."})
                elif 'Service' in file:
                    steps.append({"title": f"Update {file}", "description": "Add new business logic or integrate the new feature here."})
                elif '.vue' in file or '.jsx' in file or '.tsx' in file:
                    steps.append({"title": f"Update {file}", "description": "Integrate the new UI component into this layout/page."})
                else:
                    steps.append({"title": f"Modify {file}", "description": "Update this important file to support the new feature."})
        
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
