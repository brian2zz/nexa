import os
from nexa.core.generators.base import BaseGenerator
from nexa.core.utils.strings import pascal_case, pluralize
from nexa.core.registry import nexa_generator, PRIORITY_EXTENSION

@nexa_generator("route", category="crud", target="frontend", priority=PRIORITY_EXTENSION + 40)
class RouteGenerator(BaseGenerator):
    template_path = 'crud/route.tpl'

    def build_context(self):
        self.context = {
            'model_name': self.model_schema.name,
            'class_name': pascal_case(self.model_schema.name),
            'plural_name': pluralize(self.model_schema.name),
            'route_path': pluralize(self.model_schema.name.lower())
        }

    def get_target_path(self):
        return os.path.join(
            os.getcwd(), 
            'apps', 
            self.model_schema.app, 
            'frontend', 'src', 'routes', 
            f"{self.model_schema.name.lower()}Routes.js"
        )
