import os
from nexa.core.generators.base import BaseGenerator
from nexa.core.schema.translators.django import generate_django_fields
from nexa.core.utils.strings import pascal_case, pluralize

from nexa.core.registry import nexa_generator, PRIORITY_CORE

@nexa_generator("model", category="api", target="backend", priority=PRIORITY_CORE + 1, metadata={"description": "Generates Django models"})
class ModelGenerator(BaseGenerator):
    template_path = 'api/model.tpl'

    def build_context(self):
        self.context = {
            'app_name': self.model_schema.app,
            'model_name': self.model_schema.name,
            'class_name': pascal_case(self.model_schema.name),
            'file_name': self.model_schema.name.lower(),
            'plural_name': pluralize(self.model_schema.name),
            'model_fields': generate_django_fields(self.model_schema.fields)
        }

    def get_target_path(self):
        file_name = self.model_schema.name.lower()
        return os.path.join(
            os.getcwd(), 
            'apps', 
            self.model_schema.app, 
            'models', 
            f'{file_name}.py'
        )

def generate_model(model_schema):
    generator = ModelGenerator(model_schema)
    generator.generate()
