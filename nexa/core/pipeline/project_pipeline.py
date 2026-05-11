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

        # 2. Project-Level Scaffolding (Runs once)
        self.logger.info("Step 2: Scaffolding project-level structures...")
        self._ensure_project_structure()
        self._run_project_generators(project_schema, modes)

        # 3. Generation Phase (Per App & Model)
        self.logger.info(f"Step 3: Running generators...")
        
        for app in project_schema.apps:
            self.logger.info(f"Processing App: {app.name}")
            self._ensure_app_structure(app.name)
            
            if modes.get("backend"):
                register_api_urls(app.name)
            
            for model in app.models:
                self._generate_for_model(app.name, model, modes)

        self.logger.info("Pipeline Execution Finished.")

    def _run_project_generators(self, project_schema, modes):
        """
        Runs generators that apply to the whole project (e.g. shared UI).
        """
        target_filters = ["any"]
        if modes.get("frontend"): target_filters.append("frontend")
        
        project_gens = generators.filter(category="project")
        for entry in project_gens:
            if entry.target in target_filters:
                self.logger.log_task(f"Running {entry.category}.{entry.key}")
                # Project generators take the whole schema or nothing
                entry.value(project_schema).generate()

    def _ensure_project_structure(self):
        """
        Ensures global project files exist.
        """
        config_path = os.path.join(os.getcwd(), 'config')
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
        # Added 'services' to backend subdirs
        subdirs = ['models', 'serializers', 'views', 'urls', 'services', 'frontend/src/services']
        
        for subdir in subdirs:
            path = os.path.join(base_path, subdir)
            os.makedirs(path, exist_ok=True)
            
            if subdir in ['models', 'serializers', 'views', 'urls', 'services']:
                init_file = os.path.join(path, '__init__.py')
                if not os.path.exists(init_file):
                    with open(init_file, 'w') as f: f.write("")

        api_url_path = os.path.join(base_path, 'urls', 'api.py')
        if not os.path.exists(api_url_path):
            with open(api_url_path, 'w') as f:
                f.write("from django.urls import path, include\nfrom rest_framework.routers import DefaultRouter\n\nrouter = DefaultRouter()\n\nurlpatterns = [\n    path('', include(router.urls)),\n]\n")

    def _generate_for_model(self, app_name, model_schema, modes):
        """
        Orchestrates all generators for a single model.
        """
        self.logger.log_task(f"Generating components for: {model_schema.name}")
        
        target_filters = ["any"]
        if modes.get("backend"): target_filters.append("backend")
        if modes.get("frontend"): target_filters.append("frontend")

        # 1. API & Scaffold Generators (Sorted by Priority)
        # Category list: api, scaffold
        active_categories = ["api", "scaffold"]
        
        for cat in active_categories:
            cat_generators = generators.filter(category=cat)
            for entry in cat_generators:
                if entry.target in target_filters:
                    self.logger.log_task(f"Running {entry.category}.{entry.key} (prio: {entry.priority})")
                    entry.value(model_schema).generate()

        # 2. CRUD Generators (Only if enabled)
        if model_schema.crud.enabled:
            crud_generators = generators.filter(category="crud")
            for entry in crud_generators:
                if entry.target in target_filters:
                    self.logger.log_task(f"Running {entry.category}.{entry.key} (prio: {entry.priority})")
                    entry.value(model_schema).generate()
        
        # 3. Run Mutators (Registration)
        if modes.get("backend"):
            class_name = pascal_case(model_schema.name)
            file_name = model_schema.name.lower()
            route_name = pluralize(file_name)
            register_api(app_name, class_name, file_name, route_name)
            register_imports(app_name, class_name, file_name)
