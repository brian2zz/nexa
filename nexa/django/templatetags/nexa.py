import json
from pathlib import Path

from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.safestring import mark_safe


register = template.Library()


@register.simple_tag
def nexa_assets(app_name):

    # Development
    if settings.DEBUG:

        return mark_safe(
            f'''
            <script type="module"
                    src="http://localhost:5173/apps/{app_name}/frontend/src/main.js">
            </script>
            '''
        )

    # Production
    manifest_path = (
        Path(settings.BASE_DIR)
        / 'apps'
        / app_name
        / 'frontend'
        / 'dist'
        / '.vite'
        / 'manifest.json'
    )

    if not manifest_path.exists():

        return ''

    with open(manifest_path, 'r') as f:

        manifest = json.load(f)

    entry = manifest.get('index.html')

    if not entry:

        return ''

    js_file = entry.get('file')
    css_files = entry.get('css', [])

    tags = []

    # CSS
    for css in css_files:

        tags.append(
            f'<link rel="stylesheet" href="{static(f"{app_name}/{Path(css).name}")}">'
        )

    # JS
    tags.append(
        f'<script type="module" src="{static(f"{app_name}/{Path(js_file).name}")}"></script>'
    )

    return mark_safe('\n'.join(tags))