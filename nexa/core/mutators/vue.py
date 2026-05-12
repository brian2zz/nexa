import os
from pathlib import Path
from nexa.core.utils.strings import pascal_case, pluralize

def register_vue_route(app_name, model_name):
    """
    Registers a model's routes in both the app's router and the master gateway home app's router.
    """
    route_file = f"{model_name.lower()}Routes"
    
    # Target 1: Local App Router
    local_path = Path.cwd() / 'apps' / app_name / 'frontend' / 'src' / 'router' / 'index.js'
    local_import = f"import {route_file} from '../admin-nexa/routes/{route_file}'\n"
    
    # Target 2: Master Home Router
    home_path = Path.cwd() / 'apps' / 'home' / 'frontend' / 'src' / 'router' / 'index.js'
    home_import = f"import {route_file} from '../../../../{app_name}/frontend/src/admin-nexa/routes/{route_file}'\n"
    
    spread_line = f"    ...{route_file},"

    for r_path, imp_line in [(local_path, local_import), (home_path, home_import)]:
        if not r_path.exists():
            continue

        with open(r_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Inject Import
        if imp_line.strip() not in content and f"import {route_file}" not in content:
            if '// NEXA_ROUTE_IMPORTS' in content:
                content = content.replace('// NEXA_ROUTE_IMPORTS', f"// NEXA_ROUTE_IMPORTS\n{imp_line}")
            else:
                lines = content.splitlines()
                last_import_idx = 0
                for i, line in enumerate(lines):
                    if line.startswith('import '):
                        last_import_idx = i
                lines.insert(last_import_idx + 1, imp_line.strip())
                content = '\n'.join(lines)

        # 2. Inject Route Spread
        if spread_line not in content:
            if '// NEXA_ROUTES' in content:
                content = content.replace('// NEXA_ROUTES', f"// NEXA_ROUTES\n{spread_line}")
            else:
                content = content.replace('  ]\n})', f"    {spread_line}\n  ]\n}})")

        with open(r_path, 'w', encoding='utf-8') as f:
            f.write(content)

def register_vue_nav(app_name, model_name):
    """
    Injects management link card into admin-nexa/pages/Dashboard.vue for both the local app and the master gateway home app using named routing.
    """
    targets = [
        Path.cwd() / 'apps' / app_name / 'frontend' / 'src' / 'admin-nexa' / 'pages' / 'Dashboard.vue',
        Path.cwd() / 'apps' / 'home' / 'frontend' / 'src' / 'admin-nexa' / 'pages' / 'Dashboard.vue'
    ]

    display_name = pascal_case(model_name)
    route_name = f"{model_name.lower()}_list"

    card_link = (
        f"        <router-link :to=\"{{ name: '{route_name}' }}\" class=\"admin-card\">\n"
        f"          <h3 class=\"admin-card-title\">{display_name}</h3>\n"
        f"          <p class=\"admin-card-desc\">Kelola rekaman entitas {display_name.lower()} secara terenkapsulasi</p>\n"
        f"        </router-link>\n"
    )

    for dashboard_path in targets:
        if not dashboard_path.exists():
            continue

        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if f"name: '{route_name}'" not in content:
            if '<!-- ADMIN_MODULE_LINKS -->' in content:
                content = content.replace('<!-- ADMIN_MODULE_LINKS -->', f"<!-- ADMIN_MODULE_LINKS -->\n{card_link}")
            else:
                content = content.replace('</main>', f"  <div class=\"module-grid\">\n{card_link}  </div>\n</main>")

        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(content)
