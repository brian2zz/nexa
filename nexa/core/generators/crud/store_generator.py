import os
from nexa.core.generators.base import BaseGenerator
from nexa.core.utils.strings import pascal_case, pluralize
from nexa.core.registry import nexa_generator, PRIORITY_EXTENSION

@nexa_generator("store", category="crud", target="frontend", priority=PRIORITY_EXTENSION + 30)
class StoreGenerator(BaseGenerator):
    template_path = 'crud/store.tpl'

    def build_context(self):
        self.context = {
            'app_name': self.model_schema.app,
            'model_name': self.model_schema.name,
            'class_name': pascal_case(self.model_schema.name),
            'file_name': self.model_schema.name.lower(),
            'plural_name': pluralize(self.model_schema.name)
        }

    def get_target_path(self):
        return os.path.join(
            os.getcwd(), 
            'apps', 
            self.model_schema.app, 
            'frontend', 'src', 'stores', 
            f"{self.model_schema.name.lower()}Store.js"
        )
