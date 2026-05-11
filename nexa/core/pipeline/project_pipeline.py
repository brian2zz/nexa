import os
from nexa.core.validators import SchemaValidator
from nexa.core.registry import generators, discover_core
from nexa.core.runtime.logger import logger
from nexa.core.mutators.django import (
    register_api,
    register_api_urls,
    register_imports
)
from nexa.core.utils.strings import pascal_case, pluralize

class ProjectPipeline:
    def __init__(self):
        self.validator = SchemaValidator()
        self.logger = logger
        discover_core()

    def run(self, project_schema, modes=None):
        """
        Executes the full generation pipeline for a project.
        Modes: {"backend": bool, "frontend": bool, "dry_run": bool}
        """
        modes = modes or {"backend": True, "frontend": True, "dry_run": False}
        
        self.logger.step(f"Starting Pipeline for Project: {project_schema.name}")
        
        # 1. Validation Phase
        self.logger.info("Step 1: Validating project structure...")
        self.validator.validate_project_structure(project_schema)
        self.logger.info("OK: Validation successful.")

        if modes.get("dry_run"):
            self.logger.warning("Dry run enabled. Skipping file creation.")
            return

        # 2. Project Scaffolding
        self.logger.info("Step 2: Scaffolding project directories...")
        self._ensure_project_structure()

        # 3. Generation Phase
        self.logger.info(f"Step 3: Running generators...")
        
        for app in project_schema.apps:
            self.logger.info(f"Processing App: {app.name}")
            self._ensure_app_structure(app.name)
            
            # Register the app's API URLs to the main config/urls.py
            if modes.get("backend"):
                register_api_urls(app.name)
            
            for model in app.models:
                self._generate_api_for_model(app.name, model, modes)

        self.logger.info("Pipeline Execution Finished.")

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

    def _generate_api_for_model(self, app_name, model_schema, modes):
        """
        Orchestrates all generators and mutators for a single model using the Registry.
        """
        self.logger.log_task(f"Generating components for: {model_schema.name}")
        
        # Determine which generators to run based on modes
        target_filters = []
        if modes.get("backend"): target_filters.append("backend")
        if modes.get("frontend"): target_filters.append("frontend")
        # If both are true or neither is true (default), we might need to handle 'any'
        target_filters.append("any")

        # 1. Dynamically run API generators (Sorted by Priority)
        api_generators = generators.filter(category="api")
        for entry in api_generators:
            if entry.target not in target_filters:
                continue
            self.logger.log_task(f"Running {entry.category}.{entry.key} (prio: {entry.priority})")
            entry.value(model_schema).generate()

        # 2. Dynamically run CRUD generators (Only if enabled)
        if model_schema.crud.enabled:
            crud_generators = generators.filter(category="crud")
            for entry in crud_generators:
                if entry.target not in target_filters:
                    continue
                self.logger.log_task(f"Running {entry.category}.{entry.key} (prio: {entry.priority})")
                entry.value(model_schema).generate()
        
        # 3. Run Mutators (Registration) - Only for backend
        if modes.get("backend"):
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
