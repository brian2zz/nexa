import os
import shutil
import subprocess


def handle(args):

    print('Building Unified Nexa production assets...')

    package_json = os.path.join(os.getcwd(), 'package.json')
    if not os.path.exists(package_json):
        print('package.json not found in root')
        return

    # Run build at root
    subprocess.run(
        'npm run build',
        cwd=os.getcwd(),
        shell=True
    )

    apps_path = os.path.join(os.getcwd(), 'apps')
    dist_path = os.path.join(os.getcwd(), 'dist')
    manifest_path = os.path.join(dist_path, '.vite', 'manifest.json')

    if not os.path.exists(manifest_path):
        # Fallback for older Vite versions or different config
        manifest_path = os.path.join(dist_path, 'manifest.json')

    if not os.path.exists(manifest_path):
        print('Manifest not found. Make sure build succeeded.')
        return

    import json
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    if os.path.exists(apps_path):
        apps = os.listdir(apps_path)

        for app in apps:
            # Entry point for this app in manifest
            # Key format in manifest is relative path to root: "apps/app_name/frontend/index.html"
            entry_key = f'apps/{app}/frontend/index.html'
            entry = manifest.get(entry_key)

            if not entry:
                continue

            print(f'Distributing assets for: {app}')

            static_path = os.path.join(apps_path, app, 'static', app)
            os.makedirs(static_path, exist_ok=True)

            # Files to copy: main JS and CSS files
            files_to_copy = [entry.get('file')]
            files_to_copy.extend(entry.get('css', []))

            for rel_path in files_to_copy:
                source = os.path.join(dist_path, rel_path)
                destination = os.path.join(static_path, os.path.basename(rel_path))
                
                if os.path.exists(source):
                    shutil.copy2(source, destination)

    print('Running collectstatic...')
    subprocess.run(
        'python manage.py collectstatic --no-input',
        shell=True
    )

    print('Nexa production build complete')