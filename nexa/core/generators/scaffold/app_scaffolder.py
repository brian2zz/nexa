import os
from nexa.core.generators.base import BaseGenerator
from nexa.core.utils.strings import pascal_case
from nexa.core.registry import nexa_generator, PRIORITY_CORE

@nexa_generator("app_entry", category="scaffold", target="frontend", priority=PRIORITY_CORE - 10)
class AppEntryGenerator(BaseGenerator):
    """
    Generates index.html and main.js for each app to support multi-entry Vite.
    """
    def generate(self):
        self.build_context()
        app_frontend_path = os.path.join(os.getcwd(), 'apps', self.model_schema.app, 'frontend')
        
        # 1. Generate index.html
        from nexa.core.utils.filesystem import load_template, render_template, write_file
        
        index_tpl = load_template('scaffold/vite_index.tpl')
        index_content = render_template(index_tpl, self.context)
        write_file(os.path.join(app_frontend_path, 'index.html'), index_content)
        
        # 2. Generate main.js
        main_tpl = load_template('scaffold/vite_main.tpl')
        main_content = render_template(main_tpl, self.context)
        write_file(os.path.join(app_frontend_path, 'src', 'main.js'), main_content)

    def build_context(self):
        self.context = {
            'class_name': pascal_case(self.model_schema.app),
            'app_name': self.model_schema.app
        }

    def get_target_path(self):
        # Dummy because we override generate()
        return ""
