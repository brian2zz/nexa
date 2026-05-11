import os
from nexa.core.generators.base import BaseGenerator
from nexa.core.utils.strings import pascal_case
from nexa.core.registry import nexa_generator, PRIORITY_CORE

@nexa_generator("backend_service", category="api", target="backend", priority=PRIORITY_CORE + 15)
class BackendServiceGenerator(BaseGenerator):
    template_path = 'scaffold/backend_service.tpl'

    def build_context(self):
        self.context = {
            'class_name': pascal_case(self.model_schema.name),
            'file_name': self.model_schema.name.lower()
        }

    def get_target_path(self):
        return os.path.join(
            os.getcwd(), 
            'apps', 
            self.model_schema.app, 
            'services', 
            f"{self.model_schema.name.lower()}.py"
        )
