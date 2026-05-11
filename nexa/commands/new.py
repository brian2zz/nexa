import os
import subprocess

from nexa.core.mutators.django import (
    register_nexa,
    patch_settings,
    patch_urls
)

from nexa.core.utils.filesystem import (
    load_template,
    write_file
)


def handle(args):

    if not args:

        print('Project name required')
        return

    project_name = args[0]

    print(f'Creating Nexa project: {project_name}')

    # Full project path
    project_path = os.path.join(
        os.getcwd(),
        project_name
    )

    # Create project folder
    os.makedirs(
        project_path,
        exist_ok=True
    )

    # Django project
    subprocess.run([
        'django-admin',
        'startproject',
        'config',
        project_path
    ])

    subprocess.run([
        'pip',
        'install',
        'whitenoise'
    ])

    # Nexa folders
    folders = [
        'apps',
        'templates',
        'static',
        'media'
    ]

    for folder in folders:

        path = os.path.join(project_path, folder)

        os.makedirs(
            path,
            exist_ok=True
        )

        if folder == 'apps':
            with open(os.path.join(path, '__init__.py'), 'w') as f:
                f.write('')

    # Register Nexa core
    register_nexa(project_path)
    patch_settings(project_path)
    patch_urls(project_path)

    # Requirements
    requirements_template = load_template(
        'project/requirements.tpl'
    )

    write_file(
        os.path.join(
            project_path,
            'requirements.txt'
        ),
        requirements_template
    )

    # Root package.json
    package_template = load_template(
        'project/package.tpl'
    )

    write_file(
        os.path.join(
            project_path,
            'package.json'
        ),
        package_template
    )

    # Root vite.config.js
    vite_template = load_template(
        'project/vite.tpl'
    )

    write_file(
        os.path.join(
            project_path,
            'vite.config.js'
        ),
        vite_template
    )

    print('Nexa structure created')
    print('Project created successfully')