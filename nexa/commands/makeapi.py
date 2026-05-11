import os

from nexa.core.schema import FieldSchema, ModelSchema
from nexa.core.generators.api import (
    generate_model,
    generate_serializer,
    generate_view,
    generate_service
)
from nexa.core.mutators.django import (
    register_api,
    register_imports
)
from nexa.core.utils.strings import pascal_case, pluralize

def handle(args):
    if len(args) < 2:
        print('Usage: nexa make:api <app> <model>')
        return

    app_name = args[0]
    model_name = args[1]
    
    # 1. Parse fields from CLI (Bridge to Schema)
    field_schemas = []
    for arg in args:
        if arg.startswith('--fields='):
            raw_fields = arg.replace('--fields=', '').strip('"').strip("'")
            for f in raw_fields.split(','):
                if ':' in f:
                    name, f_type = [part.strip() for part in f.split(':', 1)]
                    field_schemas.append(FieldSchema(name=name, type=f_type))
            
    # 2. Create ModelSchema object (Self-contained with app info)
    model_schema = ModelSchema(
        name=model_name, 
        app=app_name, 
        fields=field_schemas
    )
            
    # 3. Check app existence
    app_path = os.path.join(os.getcwd(), 'apps', model_schema.app)
    if not os.path.exists(app_path):
        print(f'App "{model_schema.app}" not found')
        return

    print(f'Generating API components for: {pascal_case(model_schema.name)}')

    # 4. Use Generators (Only passing the schema)
    generate_model(model_schema)
    generate_serializer(model_schema)
    generate_view(model_schema)
    generate_service(model_schema)

    # 5. Mutate Project
    class_name = pascal_case(model_name)
    file_name = model_name.lower()
    route_name = pluralize(file_name)

    register_api(
        app_name,
        class_name,
        file_name,
        route_name
    )

    register_imports(
        app_name,
        class_name,
        file_name
    )

    print(f'API "{class_name}" generated successfully using Schema Engine')