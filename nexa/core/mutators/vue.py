import os
from pathlib import Path
from nexa.core.utils.strings import pascal_case, pluralize

def register_vue_route(app_name, model_name):
    """
    Registers a model's routes in the app's main router/index.js.
    """
    router_path = Path.cwd() / 'apps' / app_name / 'frontend' / 'src' / 'router' / 'index.js'
    
    if not router_path.exists():
        return

    with open(router_path, 'r', encoding='utf-8') as f:
        content = f.read()

    route_file = f"{model_name.lower()}Routes"
    import_line = f"import {route_file} from '../routes/{route_file}'\n"
    
    # 1. Inject Import
    if import_line not in content:
        if '// NEXA_ROUTE_IMPORTS' in content:
            content = content.replace('// NEXA_ROUTE_IMPORTS', f"// NEXA_ROUTE_IMPORTS\n{import_line}")
        else:
            # Fallback: add after first import
            lines = content.splitlines()
            last_import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('import '):
                    last_import_idx = i
            lines.insert(last_import_idx + 1, import_line.strip())
            content = '\n'.join(lines)

    # 2. Inject Route Spread
    spread_line = f"    ...{route_file},"
    if spread_line not in content:
        if '// NEXA_ROUTES' in content:
            content = content.replace('// NEXA_ROUTES', f"// NEXA_ROUTES\n{spread_line}")
        else:
            # Fallback: add before last ]
            content = content.replace('  ]\n})', f"    {spread_line}\n  ]\n}})")

    with open(router_path, 'w', encoding='utf-8') as f:
        f.write(content)

def register_vue_nav(app_name, model_name):
    """
    Adds a navigation link for the model to the app's Home.vue page.
    """
    home_path = Path.cwd() / 'apps' / app_name / 'frontend' / 'src' / 'pages' / 'Home.vue'
    
    if not home_path.exists():
        return

    with open(home_path, 'r', encoding='utf-8') as f:
        content = f.read()

    display_name = pascal_case(model_name)
    route_path = f"/{pluralize(model_name.lower())}"
    
    nav_link = (
        f"        <router-link to=\"{route_path}\" class=\"p-6 bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow group\">\n"
        f"          <h3 class=\"text-lg font-semibold text-gray-900 group-hover:text-blue-600\">{display_name}</h3>\n"
        f"          <p class=\"text-sm text-gray-500\">Manage {display_name.lower()} records</p>\n"
        f"        </router-link>\n"
    )

    if f"to=\"{route_path}\"" not in content:
        if '<!-- NEXA_NAV_LINKS -->' in content:
            content = content.replace('<!-- NEXA_NAV_LINKS -->', f"<!-- NEXA_NAV_LINKS -->\n{nav_link}")
        else:
            # Fallback: add before end of template
            content = content.replace('</template>', f"  {nav_link}\n</template>")

    with open(home_path, 'w', encoding='utf-8') as f:
        f.write(content)
