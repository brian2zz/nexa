import os
from nexa.core.utils.filesystem import (
    load_template,
    render_template,
    write_file
)

from nexa.core.mutators.django import (
    register_app,
    register_urls,
    register_api_urls
)

def handle(args):

    if not args:
        print('App name required')
        return

    app_name = args[0]

    app_path = os.path.join(
        os.getcwd(),
        'apps',
        app_name
    )

    # Ensure apps/__init__.py exists
    apps_init = os.path.join(
        os.getcwd(),
        'apps',
        '__init__.py'
    )

    if not os.path.exists(apps_init):
        with open(apps_init, 'w') as f:
            f.write('')

    print(f'Creating Nexa app: {app_name}')

    folders = [
        'models',
        'migrations',
        'serializers',
        'views',
        'services',
        'urls',
        'frontend',
        'templates',
        'static'
    ]

    # Create app root
    os.makedirs(app_path, exist_ok=True)

    # Create folders
    for folder in folders:
        os.makedirs(
            os.path.join(app_path, folder),
            exist_ok=True
        )
    
    template = load_template('app/apps.tpl')

    content = render_template(template, {
        'app_name': app_name,
        'app_class': app_name.capitalize()
    })

    write_file(
        os.path.join(app_path, 'apps.py'),
        content
    )

    api_template = load_template('app/urls.tpl')

    write_file(
        os.path.join(app_path, 'urls', 'api.py'),
        api_template
    )

    web_template = render_template(
        load_template('app/web.tpl'),
        {
            'app_name': app_name
        }
    )

    write_file(
        os.path.join(app_path, 'urls', 'web.py'),
        web_template
    )

    init_template = load_template('app/init.tpl')

    init_files = [
        os.path.join(app_path, '__init__.py'),
        os.path.join(app_path, 'models', '__init__.py'),
        os.path.join(app_path, 'migrations', '__init__.py'),
        os.path.join(app_path, 'views', '__init__.py'),
        os.path.join(app_path, 'serializers', '__init__.py'),
        os.path.join(app_path, 'services', '__init__.py'),
        os.path.join(app_path, 'urls', '__init__.py')
    ]

    for file in init_files:

        write_file(file, init_template)

    template_html = render_template(
        load_template('app/index.tpl'),
        {
            'app_name': app_name
        }
    )

    template_html = template_html.replace(
        '__APP_NAME__',
        app_name
    )

    template_dir = os.path.join(
        app_path,
        'templates',
        app_name
    )

    os.makedirs(template_dir, exist_ok=True)

    write_file(
        os.path.join(template_dir, 'index.html'),
        template_html
    )

    frontend_folders = [
        'src',
        'src/pages',
        'src/components',
        'src/router',
        'src/stores',
        'src/services'
    ] 

    for folder in frontend_folders:
        os.makedirs(
            os.path.join(app_path, 'frontend', folder),
            exist_ok=True
        )
    
    main_template = load_template('app/main.tpl')

    write_file(
        os.path.join(
            app_path,
            'frontend',
            'src',
            'main.js'
        ),
        main_template
    )

    appvue_template = load_template('app/appvue.tpl')

    write_file(
        os.path.join(
            app_path,
            'frontend',
            'src',
            'App.vue'
        ),
        appvue_template
    )

    register_app(app_name)
    register_urls(app_name)

    view_template = render_template(
        load_template('app/view.tpl'),
        {
            'app_name': app_name
        }
    )

    write_file(
        os.path.join(
            app_path,
            'views',
            'web.py'
        ),
        view_template
    )
    
    frontend_index = render_template(
        load_template('app/frontendindex.tpl'),
        {
            'app_name': app_name
        }
    )

    write_file(
        os.path.join(
            app_path,
            'frontend',
            'index.html'
        ),
        frontend_index
    )

    http_template = load_template('app/http.tpl')

    write_file(
        os.path.join(
            app_path,
            'frontend',
            'src',
            'services',
            'http.js'
        ),
        http_template
    )

    router_template = load_template('app/router.tpl')

    write_file(
        os.path.join(
            app_path,
            'frontend',
            'src',
            'router',
            'index.js'
        ),
        router_template
    )

    register_api_urls(app_name)

    print('App created successfully')