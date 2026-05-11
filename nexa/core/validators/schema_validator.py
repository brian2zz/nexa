from dataclasses import dataclass
from nexa.core.schema.translators.django import DJANGO_FIELD_MAP

@dataclass
class NexaError:
    code: str
    message: str
    model: str = None
    field: str = None
    app: str = None

class SchemaValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors
        messages = [f"[{e.code}] {e.message} (App: {e.app}, Model: {e.model}, Field: {e.field})" for e in errors]
        super().__init__("\n".join(messages))

class SchemaValidator:
    def __init__(self):
        self.errors = []
        self.valid_types = list(DJANGO_FIELD_MAP.keys())

    def validate(self, project):
        self.errors = []
        
        if not project.name.strip():
            self.errors.append(NexaError(code="empty_project_name", message="Project name cannot be empty"))

        app_names = set()
        for app in project.apps:
            if not app.name.strip():
                self.errors.append(NexaError(code="empty_app_name", message="App name cannot be empty"))
            
            if app.name in app_names:
                self.errors.append(NexaError(code="duplicate_app", message=f"Duplicate app name: {app.name}", app=app.name))
            app_names.add(app.name)

            self.validate_app(app)

        if self.errors:
            raise SchemaValidationError(self.errors)
        
        return True

    def validate_app(self, app):
        model_names = set()
        for model in app.models:
            if not model.name.strip():
                self.errors.append(NexaError(code="empty_model_name", message="Model name cannot be empty", app=app.name))
            
            if model.name in model_names:
                self.errors.append(NexaError(code="duplicate_model", message=f"Duplicate model: {model.name}", app=app.name, model=model.name))
            model_names.add(model.name)

            self.validate_model(model)

    def validate_model(self, model):
        field_names = set()
        for field in model.fields:
            if not field.name.strip():
                self.errors.append(NexaError(code="empty_field_name", message="Field name cannot be empty", app=model.app, model=model.name))
            
            if field.name in field_names:
                self.errors.append(NexaError(code="duplicate_field", message=f"Duplicate field: {field.name}", app=model.app, model=model.name, field=field.name))
            field_names.add(field.name)

            if field.type not in self.valid_types:
                self.errors.append(NexaError(
                    code="invalid_field_type",
                    message=f"Invalid type '{field.type}'. Supported: {', '.join(self.valid_types)}",
                    app=model.app, model=model.name, field=field.name
                ))
            
            # Relationship Validation
            if field.type in ['foreignkey', 'manytomany', 'onetoone']:
                if not field.to:
                    self.errors.append(NexaError(
                        code="missing_relation_target",
                        message=f"Field '{field.name}' is a relation but has no 'to' attribute",
                        app=model.app, model=model.name, field=field.name
                    ))
                else:
                    if not self._model_exists(field.to, model.app):
                        self.errors.append(NexaError(
                            code="broken_relation",
                            message=f"Relation target '{field.to}' not found in project",
                            app=model.app, model=model.name, field=field.name
                        ))

    def _model_exists(self, target, current_app):
        if not hasattr(self, 'namespaced_models'):
            return True
            
        # Support "app.Model" or just "Model"
        if "." in target:
            return target in self.namespaced_models
        
        # If no namespace, check in current app first, then others
        target_with_app = f"{current_app}.{target}"
        if target_with_app in self.namespaced_models:
            return True
            
        # Check if model name exists in ANY app (risky if duplicates exist, but we check for duplicates)
        return any(target == m.split('.')[1] for m in self.namespaced_models)

    def validate_project_structure(self, project):
        # Build "app.Model" index
        self.namespaced_models = []
        for app in project.apps:
            for model in app.models:
                self.namespaced_models.append(f"{app.name}.{model.name}")
        
        return self.validate(project)
