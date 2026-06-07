import os

def handle(args):
    if not args:
        print('Module name required')
        return

    module_name = args[0].lower()
    enterprise = '--enterprise' in args

    apps_dir = os.path.join(os.getcwd(), 'apps')
    if not os.path.exists(apps_dir):
        print("Error: 'apps' directory not found. Are you in a NexaPHP project root?")
        return

    module_dir = os.path.join(apps_dir, module_name)
    if os.path.exists(module_dir):
        print(f"Error: Module '{module_name}' already exists.")
        return

    # Create directories
    dirs_to_create = [
        'Models',
        'Controllers',
        'routes',
    ]

    if enterprise:
        dirs_to_create.extend(['Repositories', 'Services', 'Events', 'DTOs'])

    for d in dirs_to_create:
        os.makedirs(os.path.join(module_dir, d), exist_ok=True)

    # Create routes/api.php
    with open(os.path.join(module_dir, 'routes', 'api.php'), 'w') as f:
        f.write("<?php\n\n// Add your routes here using $r->addRoute(...)\n")

    # Create module.php manifest
    with open(os.path.join(module_dir, 'module.php'), 'w') as f:
        f.write(f"<?php\n\nreturn [\n    'name' => '{module_name}',\n    'version' => '1.0.0',\n    'requires' => [],\n    'exports' => []\n];\n")

    print(f"Module '{module_name}' created successfully in apps/{module_name}/")
