import os
from nexa.core.generators.base import BaseGenerator
from nexa.core.schema.translators.django import generate_django_fields
from nexa.core.utils.strings import pascal_case

class ModelGenerator(BaseGenerator):
    template_path = 'api/model.tpl'

    def build_context(self):
        self.context = {
            'app_name': self.model_schema.app,
            'class_name': pascal_case(self.model_schema.name),
            'file_name': self.model_schema.name.lower(),
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
