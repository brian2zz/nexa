import os
from nexa.core.validators import SchemaValidator
from nexa.core.registry import generators, discover_core
from nexa.core.runtime.logger import logger
from nexa.core.mutators.django import (
    register_app,
    register_urls,
    register_api,
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
        self._ensure_core_saas_structure() # NEW: SaaS Foundation
        self._run_project_generators(project_schema, modes)

        # 3. Generation Phase (Per App & Model)
        self.logger.info(f"Step 3: Running generators...")
        
        # Determine the main app for URL registration
        main_app_name = None
        for app in project_schema.apps:
            if app.main:
                main_app_name = app.name
                break
        
        if not main_app_name:
            # Foundation app 'home' always acts as the master global gateway SPA by default
            main_app_name = 'home'

        for app in project_schema.apps:
            self.logger.info(f"Processing App: {app.name}")
            self._ensure_app_structure(app.name)
            
            if modes.get("backend"):
                register_app(app.name)
                # Register with main=True if it's the designated main app
                register_urls(app.name, is_main=(app.name == main_app_name))
            
            # Run App-level generators
            self._run_app_generators(app, modes)
            
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

    def _run_app_generators(self, app_schema, modes):
        """
        Runs generators that apply to a specific app (e.g. app-level entry points).
        """
        target_filters = ["any"]
        if modes.get("frontend"): target_filters.append("frontend")
        if modes.get("backend"): target_filters.append("backend")
        
        app_gens = generators.filter(category="app")
        for entry in app_gens:
            if entry.target in target_filters:
                entry.value(app_schema).generate()

    def _ensure_core_saas_structure(self):
        """
        Ensures the 'home' app exists with SaaS middleware (Tenant & Activity Log).
        """
        self._ensure_app_structure('home')
        
        # Register home in Django
        from nexa.core.mutators.django import register_app, register_urls
        register_app('home')
        register_urls('home', is_main=True)

        home_path = os.path.join(os.getcwd(), 'apps', 'home')
        middleware_path = os.path.join(home_path, 'middleware')
        os.makedirs(middleware_path, exist_ok=True)
        
        from nexa.core.utils.filesystem import write_file
        
        # 1. Tenant Middleware
        tenant_file = os.path.join(middleware_path, 'tenant.py')
        if not os.path.exists(tenant_file):
            write_file(tenant_file, "class TenantMiddleware:\n    def __init__(self, get_response):\n        self.get_response = get_response\n\n    def __call__(self, request):\n        # Logic to extract tenant from URL\n        return self.get_response(request)\n")

        # 2. Activity Log Middleware
        activity_file = os.path.join(middleware_path, 'activity.py')
        if not os.path.exists(activity_file):
            write_file(activity_file, "class ActivityLogMiddleware:\n    def __init__(self, get_response):\n        self.get_response = get_response\n\n    def __call__(self, request):\n        # Logic to log user activity\n        return self.get_response(request)\n")

        # 3. Generate Frontend entry bridge for home app
        from nexa.core.generators.scaffold.app_scaffolder import AppEntryGenerator
        from types import SimpleNamespace
        AppEntryGenerator(SimpleNamespace(name='home')).generate()

    def _ensure_project_structure(self):
        """
        Ensures global project files and folders exist.
        """
        cwd = os.getcwd()
        dirs = ['config', 'templates', 'static', 'media', 'shared', 'apps']
        for d in dirs:
            path = os.path.join(cwd, d)
            os.makedirs(path, exist_ok=True)
            if d == 'apps':
                init_file = os.path.join(path, '__init__.py')
                if not os.path.exists(init_file):
                    open(init_file, 'w').close()
            
        from nexa.core.utils.filesystem import load_template, render_template, write_file
        import subprocess
        
        # 0. Auto-initialize base Django project if settings.py is missing (Self-healing)
        settings_path = os.path.join(cwd, 'config', 'settings.py')
        if not os.path.exists(settings_path):
            self.logger.info("Base project structure missing. Auto-initializing Django project...")
            try:
                subprocess.run(['django-admin', 'startproject', 'config', cwd], check=True)
                
                # Apply base settings patches
                from nexa.core.mutators.django import register_nexa, patch_settings, patch_urls
                register_nexa(cwd)
                patch_settings(cwd)
                patch_urls(cwd)
                
                self.logger.success("Auto-initialization complete.")
            except Exception as e:
                self.logger.error(f"Failed to auto-initialize project: {e}")

        # Ensure root config files exist unconditionally (Self-healing)
        req_path = os.path.join(cwd, 'requirements.txt')
        if not os.path.exists(req_path):
            write_file(req_path, load_template('project/requirements.tpl'))
            
        pkg_path = os.path.join(cwd, 'package.json')
        if not os.path.exists(pkg_path):
            write_file(pkg_path, load_template('project/package.tpl'))
            
        vite_path = os.path.join(cwd, 'vite.config.js')
        if not os.path.exists(vite_path):
            write_file(vite_path, load_template('project/vite.tpl'))

        # 1. Ensure Global base.html exists
        base_html_path = os.path.join(cwd, 'templates', 'base.html')
        if not os.path.exists(base_html_path):
            try:
                base_tpl = load_template('project/base.tpl')
                write_file(base_html_path, render_template(base_tpl, {}))
            except:
                # Fallback if template missing
                write_file(base_html_path, "<html><body>{% block content %}{% endblock %}</body></html>")

        # 2. Ensure basic urls.py exists
        urls_path = os.path.join(cwd, 'config', 'urls.py')
        if not os.path.exists(urls_path):
            write_file(urls_path, "from django.urls import path, include\nfrom django.contrib import admin\n\nurlpatterns = [\n    path('admin/', admin.site.urls),\n]\n")

    def _ensure_app_structure(self, app_name):
        """
        Ensures the full Django app directory structure exists, matching 'nexa startapp' logic.
        """
        base_path = os.path.join(os.getcwd(), 'apps', app_name)
        subdirs = ['models', 'serializers', 'views', 'urls', 'services', 'migrations', 'templates', 'frontend/src/services']
        
        from nexa.core.utils.filesystem import load_template, render_template, write_file
        
        # 1. Create Directories & __init__.py files
        os.makedirs(base_path, exist_ok=True)
        app_init = os.path.join(base_path, '__init__.py')
        if not os.path.exists(app_init):
            write_file(app_init, "")

        for subdir in subdirs:
            path = os.path.join(base_path, subdir)
            os.makedirs(path, exist_ok=True)
            
            if subdir in ['models', 'serializers', 'views', 'urls', 'services', 'migrations']:
                init_file = os.path.join(path, '__init__.py')
                if not os.path.exists(init_file):
                    write_file(init_file, "")

        # 2. Create apps.py
        apps_file = os.path.join(base_path, 'apps.py')
        if not os.path.exists(apps_file):
            apps_tpl = load_template('app/apps.tpl')
            content = render_template(apps_tpl, {
                'app_name': app_name, 
                'app_class': app_name.capitalize() # Corrected key
            })
            write_file(apps_file, content)

        # 3. Create Web URLs & Views (for standard Django entry points)
        web_url_file = os.path.join(base_path, 'urls', 'web.py')
        if not os.path.exists(web_url_file):
            web_url_tpl = load_template('app/web.tpl') # This template has re_path catch-all
            content = render_template(web_url_tpl, {'app_name': app_name})
            write_file(web_url_file, content)

        web_view_file = os.path.join(base_path, 'views', 'web.py')
        if not os.path.exists(web_view_file):
            content = (
                "from django.shortcuts import render\n"
                "from django.conf import settings\n\n"
                f"def index(request):\n"
                f"    return render(request, '{app_name}/index.html', {{\n"
                f"        'app_name': '{app_name}',\n"
                f"        'debug': settings.DEBUG\n"
                f"    }})\n"
            )
            write_file(web_view_file, content)

        # 4. Create admin.py & tests.py
        admin_file = os.path.join(base_path, 'admin.py')
        if not os.path.exists(admin_file):
            write_file(admin_file, "from django.contrib import admin\n# Register your models here.\n")

        test_file = os.path.join(base_path, 'tests.py')
        if not os.path.exists(test_file):
            write_file(test_file, "from django.test import TestCase\n# Create your tests here.\n")

        # 5. Create API URLs structure
        api_url_file = os.path.join(base_path, 'urls', 'api.py')
        if not os.path.exists(api_url_file):
            write_file(api_url_file, "from django.urls import path, include\nfrom rest_framework.routers import DefaultRouter\n\nrouter = DefaultRouter()\n\nurlpatterns = [\n    path('', include(router.urls)),\n]\n")

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

        if modes.get("frontend") and model_schema.crud.enabled:
            from nexa.core.mutators.vue import register_vue_route, register_vue_nav
            register_vue_route(app_name, model_schema.name)
            register_vue_nav(app_name, model_schema.name)

