import os
from nexa.core.generators.base import BaseGenerator
from nexa.core.utils.strings import pascal_case, pluralize

from nexa.core.registry import nexa_generator, PRIORITY_CORE

@nexa_generator("service", category="api", target="frontend", priority=PRIORITY_CORE + 4, metadata={"description": "Generates Frontend services"})
class ServiceGenerator(BaseGenerator):
    template_path = 'api/service.tpl'

    def build_context(self):
        file_name = self.model_schema.name.lower()
        self.context = {
            'app_name': self.model_schema.app,
            'model_name': self.model_schema.name,
            'class_name': pascal_case(self.model_schema.name),
            'file_name': file_name,
            'plural_name': pluralize(self.model_schema.name),
            'route_name': pluralize(file_name)
        }

    def get_target_path(self):
        file_name = self.model_schema.name.lower()
        return os.path.join(
            os.getcwd(), 
            'apps', 
            self.model_schema.app, 
            'frontend', 
            'src', 
            'services', 
            f'{file_name}.js'
        )

def generate_service(model_schema):
    generator = ServiceGenerator(model_schema)
    generator.generate()
