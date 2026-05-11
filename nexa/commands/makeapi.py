import os

from nexa.core.utils.filesystem import (
    load_template,
    render_template,
    write_file
)

from nexa.core.mutators.django import (
    register_api,
    register_imports
)

from nexa.core.utils.fields import (
    generate_model_fields
)

from nexa.core.utils.strings import pluralize, pascal_case

def handle(args):

    if len(args) < 2:

        print(
            'Usage: nexa make:api <app> <model>'
        )

        return

    app_name = args[0]
    model_name = args[1]
    
    fields = []

    for arg in args:
        if arg.startswith('--fields='):
            raw_fields = arg.replace('--fields=', '').strip('"').strip("'")
            fields = [f.strip() for f in raw_fields.split(',')]
            
    model_fields = generate_model_fields(fields)
            
    class_name = pascal_case(model_name)
    file_name = model_name.lower()
    route_name = pluralize(file_name)

    app_path = os.path.join(
        os.getcwd(),
        'apps',
        app_name
    )

    if not os.path.exists(app_path):

        print(f'App "{app_name}" not found')

        return

    context = {
        'app_name': app_name,
        'class_name': class_name,
        'file_name': file_name,
        'route_name': route_name,
        'model_fields': model_fields
    }

    print(
        f'Generating API: {class_name}'
    )

    # =========================
    # MODEL
    # =========================

    model_template = load_template(
        'api/model.tpl'
    )

    model_content = render_template(
        model_template,
        context
    )

    write_file(
        os.path.join(
            app_path,
            'models',
            f'{file_name}.py'
        ),
        model_content
    )

    # =========================
    # SERIALIZER
    # =========================

    serializer_template = load_template(
        'api/serializer.tpl'
    )

    serializer_content = render_template(
        serializer_template,
        context
    )

    write_file(
        os.path.join(
            app_path,
            'serializers',
            f'{file_name}.py'
        ),
        serializer_content
    )

    # =========================
    # VIEW
    # =========================

    view_template = load_template(
        'api/view.tpl'
    )

    view_content = render_template(
        view_template,
        context
    )

    write_file(
        os.path.join(
            app_path,
            'views',
            f'{file_name}.py'
        ),
        view_content
    )

    # =========================
    # FRONTEND SERVICE
    # =========================

    service_template = load_template(
        'api/service.tpl'
    )

    service_content = render_template(
        service_template,
        context
    )

    write_file(
        os.path.join(
            app_path,
            'frontend',
            'src',
            'services',
            f'{file_name}.js'
        ),
        service_content
    )

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

    print(
        f'API "{class_name}" generated successfully'
    )