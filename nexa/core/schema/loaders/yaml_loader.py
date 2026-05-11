import yaml
import os
from nexa.core.schema import ProjectSchema, AppSchema, ModelSchema, FieldSchema

class YamlLoader:
    def load(self, file_path):
        """
        Loads a YAML file and converts it into a ProjectSchema hierarchy.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Schema file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        return self.parse_project(data)

    def parse_project(self, data):
        # Support both 'project: name' or 'project: { name: name }'
        project_data = data.get('project', {})
        if isinstance(project_data, str):
            project_name = project_data
        else:
            project_name = project_data.get('name', 'nexa_project')
            
        version = str(data.get('version', '1'))
        apps_data = data.get('apps', [])
        
        apps = []
        for app_data in apps_data:
            apps.append(self.parse_app(app_data))
            
        return ProjectSchema(name=project_name, version=version, apps=apps)

    def parse_app(self, data):
        app_name = data.get('name')
        models_data = data.get('models', [])
        
        models = []
        for model_data in models_data:
            models.append(self.parse_model(app_name, model_data))
            
        return AppSchema(name=app_name, models=models)

    def parse_model(self, app_name, data):
        model_name = data.get('name')
        fields_data = data.get('fields', [])
        
        # Support crud: true (shorthand) or crud: { enabled: true }
        raw_crud = data.get('crud', True)
        if isinstance(raw_crud, bool):
            crud = {"enabled": raw_crud}
        else:
            crud = raw_crud
        
        fields = []
        for field_data in fields_data:
            fields.append(self.parse_field(field_data))
            
        return ModelSchema(name=model_name, app=app_name, fields=fields, crud=crud)

    def parse_field(self, data):
        # Support both 'name: type' string or dict format
        if isinstance(data, str) and ':' in data:
            name, f_type = [part.strip() for part in data.split(':', 1)]
            return FieldSchema(name=name, type=f_type)
            
        return FieldSchema(
            name=data.get('name'),
            type=data.get('type'),
            required=data.get('required', True),
            to=data.get('to'),
            on_delete=data.get('on_delete', 'CASCADE')
        )
