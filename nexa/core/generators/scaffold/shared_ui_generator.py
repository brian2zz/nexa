import os
from nexa.core.generators.base import BaseGenerator
from nexa.core.registry import nexa_generator, PRIORITY_CORE

@nexa_generator("shared_ui", category="project", target="frontend", priority=PRIORITY_CORE - 50)
class SharedUiGenerator(BaseGenerator):
    """
    Generates the shared UI library in the root directory.
    """
    def __init__(self, project_schema=None):
        self.project_schema = project_schema
        self.context = {}

    def generate(self):
        shared_path = os.path.join(os.getcwd(), 'shared', 'ui')
        os.makedirs(shared_path, exist_ok=True)
        
        from nexa.core.utils.filesystem import load_template, render_template, write_file
        
        # 1. Generate BaseButton
        button_tpl = load_template('shared/base_button.tpl')
        write_file(os.path.join(shared_path, 'BaseButton.vue'), button_tpl)
        
        # print(f"    [Shared UI] Generated in {shared_path}")

    def build_context(self): pass
    def get_target_path(self): return ""
