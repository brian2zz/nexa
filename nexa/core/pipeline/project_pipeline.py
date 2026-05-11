import os
from nexa.core.validators import SchemaValidator
from nexa.core.generators.api import (
    generate_model,
    generate_serializer,
    generate_view,
    generate_service
)
from nexa.core.mutators.django import (
    register_api,
    register_api_urls,
    register_imports
)
from nexa.core.utils.strings import pascal_case, pluralize

class ProjectPipeline:
    def __init__(self):
        self.validator = SchemaValidator()

    def run(self, project_schema):
        """
        Executes the full generation pipeline for a project.
        """
        print(f"--- Starting Pipeline for Project: {project_schema.name} ---")
        
        # 1. Validation Phase
        print("Step 1: Validating project structure...")
        self.validator.validate_project_structure(project_schema)
        print("OK: Validation successful.")

        # 2. Project Scaffolding
        print("Step 2: Scaffolding project directories...")
        self._ensure_project_structure()

        # 3. Generation Phase
        for app in project_schema.apps:
            print(f"\nProcessing App: {app.name}")
            self._ensure_app_structure(app.name)
            
            # Register the app's API URLs to the main config/urls.py
            register_api_urls(app.name)
            
            for model in app.models:
                self._generate_api_for_model(app.name, model)

        print("\n--- Pipeline Completed Successfully ---")

    def _ensure_project_structure(self):
        """
        Ensures global project files exist (e.g., config/urls.py).
        """
        config_path = os.path.join(os.getcwd(), 'config')
        if not os.path.exists(config_path):
            os.makedirs(config_path, exist_ok=True)
            
        urls_path = os.path.join(config_path, 'urls.py')
        if not os.path.exists(urls_path):
            with open(urls_path, 'w') as f:
                f.write("from django.urls import path, include\n\nurlpatterns = [\n]\n")

    def _ensure_app_structure(self, app_name):
        """
        Ensures the standard Django app directory structure exists.
        """
        base_path = os.path.join(os.getcwd(), 'apps', app_name)
        subdirs = ['models', 'serializers', 'views', 'urls', 'frontend/src/services']
        
        for subdir in subdirs:
            path = os.path.join(base_path, subdir)
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                
                # Create __init__.py for Python packages
                if subdir in ['models', 'serializers', 'views', 'urls']:
                    init_file = os.path.join(path, '__init__.py')
                    if not os.path.exists(init_file):
                        with open(init_file, 'w') as f: f.write("")

        # Ensure urls/api.py exists for mutators
        api_url_path = os.path.join(base_path, 'urls', 'api.py')
        if not os.path.exists(api_url_path):
            with open(api_url_path, 'w') as f:
                f.write("from django.urls import path, include\nfrom rest_framework.routers import DefaultRouter\n\nrouter = DefaultRouter()\n\nurlpatterns = [\n    path('', include(router.urls)),\n]\n")

    def _generate_api_for_model(self, app_name, model_schema):
        """
        Orchestrates all generators and mutators for a single model.
        """
        print(f"  > Generating API for: {model_schema.name}")
        
        # Run Generators
        generate_model(model_schema)
        generate_serializer(model_schema)
        generate_view(model_schema)
        generate_service(model_schema)
        
        # Run Mutators (Registration)
        class_name = pascal_case(model_schema.name)
        file_name = model_schema.name.lower()
        route_name = pluralize(file_name)

        register_api(
            app_name,
            class_name,
            file_name,
            route_name
        )

        register_imports(
            app_name,
            class_name,
            file_name
        )
