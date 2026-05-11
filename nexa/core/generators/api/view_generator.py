import os
from nexa.core.generators.base import BaseGenerator
from nexa.core.utils.strings import pascal_case

from nexa.core.registry import nexa_generator, PRIORITY_CORE

@nexa_generator("view", category="api", target="backend", priority=PRIORITY_CORE + 3, metadata={"description": "Generates DRF viewsets"})
class ViewGenerator(BaseGenerator):
    template_path = 'api/view.tpl'

    def build_context(self):
        self.context = {
            'app_name': self.model_schema.app,
            'class_name': pascal_case(self.model_schema.name),
            'file_name': self.model_schema.name.lower()
        }

    def get_target_path(self):
        file_name = self.model_schema.name.lower()
        return os.path.join(
            os.getcwd(), 
            'apps', 
            self.model_schema.app, 
            'views', 
            f'{file_name}.py'
        )

def generate_view(model_schema):
    generator = ViewGenerator(model_schema)
    generator.generate()
