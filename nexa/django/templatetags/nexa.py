import json
from pathlib import Path

from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def nexa_assets(app_name):

    app_name = str(app_name.encode("utf-8"), "utf-8")
    base_dir = str(settings.BASE_DIR)

    # Development
    if settings.DEBUG:
        return mark_safe(
            f'''
            <script type="module" src="http://localhost:5173/static/@vite/client"></script>
            <script type="module" src="http://localhost:5173/static/apps/{app_name}/frontend/src/main.js"></script>
            '''
        )

    # Production: Baca manifest.json di root dist folder
    manifest_path = Path(base_dir, "dist", ".vite", "manifest.json")

    if not manifest_path.exists():
        return ''

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    # Sesuaikan kunci pencarian dengan hasil Vite yang build semua app jadi satu
    entry_key = f"apps/{app_name}/frontend/index.html"
    entry = manifest.get(entry_key)

    if not entry:
        return ''

    js_file = entry.get('file')
    css_files = entry.get('css', [])

    tags = []

    # CSS
    for css in css_files:
        tags.append(
            f'<link rel="stylesheet" href="{static(css)}">'
        )

    # JS
    tags.append(
        f'<script type="module" src="{static(js_file)}"></script>'
    )

    return mark_safe('\n'.join(tags))
