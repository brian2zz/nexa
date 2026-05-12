import os
from nexa.core.generators.base import BaseGenerator
from nexa.core.utils.strings import pascal_case, pluralize
from nexa.core.registry import nexa_generator, PRIORITY_EXTENSION

@nexa_generator("list_page", category="crud", target="frontend", priority=PRIORITY_EXTENSION + 10)
class ListPageGenerator(BaseGenerator):
    template_path = 'crud/list.tpl'

    def build_context(self):
        self.context = {
            'app_name': self.model_schema.app,
            'model_name': self.model_schema.name,
            'class_name': pascal_case(self.model_schema.name),
            'file_name': self.model_schema.name.lower(),
            'plural_name': pluralize(self.model_schema.name),
            'fields': self.model_schema.fields,
            'searchable': self.model_schema.crud.table.searchable,
            'sortable': self.model_schema.crud.table.sortable,
            'columns': self.model_schema.crud.table.columns or [f.name for f in self.model_schema.fields[:5]]
        }

    def get_target_path(self):
        return os.path.join(
            os.getcwd(), 
            'apps', 
            self.model_schema.app, 
            'frontend', 'src', 'admin-nexa', 'pages', 
            f"{pascal_case(self.model_schema.name)}List.vue"
        )
