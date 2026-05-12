import os
from nexa.core.generators.base import BaseGenerator
from nexa.core.utils.strings import pascal_case, pluralize
from nexa.core.registry import nexa_generator, PRIORITY_EXTENSION

@nexa_generator("form_page", category="crud", target="frontend", priority=PRIORITY_EXTENSION + 20)
class FormPageGenerator(BaseGenerator):
    template_path = 'crud/form.tpl'

    def build_context(self):
        self.context = {
            'app_name': self.model_schema.app,
            'model_name': self.model_schema.name,
            'class_name': pascal_case(self.model_schema.name),
            'file_name': self.model_schema.name.lower(),
            'plural_name': pluralize(self.model_schema.name),
            'fields': self.model_schema.fields,
            'layout': self.model_schema.crud.form.layout
        }

    def get_target_path(self):
        return os.path.join(
            os.getcwd(), 
            'apps', 
            self.model_schema.app, 
            'frontend', 'src', 'admin-nexa', 'pages', 
            f"{pascal_case(self.model_schema.name)}Form.vue"
        )
