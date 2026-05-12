import os
from nexa.core.generators.base import BaseGenerator
from nexa.core.utils.strings import pascal_case
from nexa.core.registry import nexa_generator, PRIORITY_CORE

@nexa_generator("scaffold.entry", category="app", priority=PRIORITY_CORE + 10)
class AppEntryGenerator(BaseGenerator):
    """
    Generates the main entry points (index.html, main.js) and Django bridge for an app.
    """
    def __init__(self, app_schema):
        super().__init__(app_schema)
        self.app_schema = app_schema

    def generate(self):
        self.build_context()
        app_name = self.app_schema.name
        app_path = os.path.join(os.getcwd(), 'apps', app_name)
        app_frontend_path = os.path.join(app_path, 'frontend')
        app_templates_path = os.path.join(app_path, 'templates', app_name)
        
        from nexa.core.utils.filesystem import load_template, render_template, write_file
        
        # 1. Generate Vite index.html
        index_tpl = load_template('scaffold/vite_index.tpl')
        index_content = render_template(index_tpl, self.context)
        write_file(os.path.join(app_frontend_path, 'index.html'), index_content)
        
        # 2. Generate main.js
        main_tpl = load_template('scaffold/vite_main.tpl')
        main_content = render_template(main_tpl, self.context)
        write_file(os.path.join(app_frontend_path, 'src', 'main.js'), main_content)

        # 3. Generate App.vue
        app_vue_tpl = load_template('scaffold/vite_app.tpl')
        app_vue_content = render_template(app_vue_tpl, self.context)
        write_file(os.path.join(app_frontend_path, 'src', 'App.vue'), app_vue_content)

        # 4. Generate router/index.js
        router_path = os.path.join(app_frontend_path, 'src', 'router')
        os.makedirs(router_path, exist_ok=True)
        router_tpl = load_template('scaffold/vite_router.tpl')
        router_content = render_template(router_tpl, self.context)
        write_file(os.path.join(router_path, 'index.js'), router_content)

        # 5. Generate style.css
        style_tpl = load_template('scaffold/vite_style.tpl')
        style_content = render_template(style_tpl, self.context)
        write_file(os.path.join(app_frontend_path, 'src', 'style.css'), style_content)

        # 6. Generate pages/Home.vue
        pages_path = os.path.join(app_frontend_path, 'src', 'pages')
        os.makedirs(pages_path, exist_ok=True)
        home_tpl = load_template('scaffold/vite_home.tpl')
        home_content = render_template(home_tpl, self.context)
        write_file(os.path.join(pages_path, 'Home.vue'), home_content)

        # 7. Generate Django index.html (The bridge)
        django_index_tpl = load_template('scaffold/django_index.tpl')
        django_index_content = render_template(django_index_tpl, self.context)
        write_file(os.path.join(app_templates_path, 'index.html'), django_index_content)

    def build_context(self):
        self.context = {
            'app_name': self.app_schema.name,
            'class_name': pascal_case(self.app_schema.name),
        }
