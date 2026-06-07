import os
import subprocess
from nexa.core.schema.loaders.yaml_loader import YamlLoader
from nexa.commands.php.make_module import handle as make_module_handle
from nexa.core.utils.filesystem import render_template, load_template, write_file
from nexa.core.utils.strings import pascal_case, pluralize

def handle(args):
    yaml_path = 'nexa.yaml'
    if len(args) > 0 and not args[0].startswith('--'):
        yaml_path = args[0]

    try:
        loader = YamlLoader()
        project = loader.load(yaml_path)
    except Exception as e:
        print(f"Could not load {yaml_path}: {e}")
        return

    for app in project.apps:
        app_name = app.name
        if not app_name:
            continue
        
        # Check if module exists, if not create it
        app_dir = os.path.join(os.getcwd(), 'apps', app_name)
        if not os.path.exists(app_dir):
            make_module_handle([app_name])
            
        for model in app.models:
            model_name = model.name
            fields = [{'name': f.name, 'type': f.type, 'required': getattr(f, 'required', False)} for f in model.fields]
            
            # Generate Model PHP file
            generate_model(app_name, model_name, fields)
            
            # Generate Controller PHP file
            generate_controller(app_name, model_name)
            
            # Vue CRUD Frontend is now fully Dynamic via Runtime Reflection!
            
    print("\n[NexaPHP] Code Generation Complete.")
    print("[NexaPHP] Running automatic database migrations (makemigrations & migrate)...")
    
    # Auto Migration
    try:
        # Assuming the environment is correct and vendor bin is usable
        # In windows, it might just be `php bin/nexa makemigrations`
        subprocess.run(['php', 'bin/nexa', 'makemigrations'], check=True)
        subprocess.run(['php', 'bin/nexa', 'migrate', '--no-interaction'], check=True)
        print("[OK] Database migrations applied successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Migration failed. Please check your Doctrine configuration or run manually. Error: {e}")
    except FileNotFoundError:
        print("[ERROR] 'php' command or 'bin/nexa' not found. Cannot run migrations.")

def generate_model(app_name, model_name, fields):
    namespace = f"Apps\\{app_name.capitalize()}\\Models"
    
    properties = []
    for f in fields:
        fname = f.get('name')
        ftype = f.get('type')
        
        # Mapping to PHP types and Doctrine types
        php_type = 'string'
        doc_type = 'string'
        precision_attr = ''
        if ftype == 'integer':
            php_type = 'int'
            doc_type = 'integer'
        elif ftype == 'decimal' or ftype == 'float':
            php_type = 'float'
            doc_type = 'decimal'
            precision_attr = ', precision: 10, scale: 2'
        elif ftype == 'boolean':
            php_type = 'bool'
            doc_type = 'boolean'
        elif ftype == 'date':
            php_type = '\\DateTime'
            doc_type = 'date'
        
        req = not getattr(f, 'required', False)
        null_attr = 'true' if req else 'false'
        
        properties.append(f"    #[Column(type: '{doc_type}'{precision_attr}, nullable: {null_attr})]")
        properties.append(f"    public {php_type}{'|null' if req else ''} ${fname};")
        
    properties_str = "\n\n".join(properties)
    
    content = f"""<?php

namespace {namespace};

use Doctrine\\ORM\\Mapping\\Entity;
use Doctrine\\ORM\\Mapping\\Table;
use Doctrine\\ORM\\Mapping\\Id;
use Doctrine\\ORM\\Mapping\\Column;
use Doctrine\\ORM\\Mapping\\GeneratedValue;
use Nexa\\NexaModel;

#[Entity]
#[Table(name: '{app_name}_{model_name.lower()}s')]
class {model_name} extends NexaModel
{{
    #[Id]
    #[Column(type: 'integer')]
    #[GeneratedValue]
    public int $id;

{properties_str}
}}
"""
    model_path = os.path.join(os.getcwd(), 'apps', app_name, 'Models', f'{model_name}.php')
    with open(model_path, 'w') as f:
        f.write(content)
        
def generate_controller(app_name, model_name):
    namespace = f"Apps\\{app_name.capitalize()}\\Controllers"
    model_class = f"Apps\\{app_name.capitalize()}\\Models\\{model_name}"
    
    content = f"""<?php

namespace {namespace};

use {model_class};

class {model_name}Controller
{{
    public function index()
    {{
        $items = {model_name}::all();
        // Simplified formatting for brevity
        $result = [];
        foreach ($items as $item) {{
            $result[] = ['id' => $item->id];
        }}
        return ['data' => $result];
    }}
}}
"""
    ctrl_path = os.path.join(os.getcwd(), 'apps', app_name, 'Controllers', f'{model_name}Controller.php')
    with open(ctrl_path, 'w') as f:
        f.write(content)

def generate_vue_crud(app_name, model_name, fields):
    class_name = pascal_case(model_name)
    plural_name = pluralize(model_name).lower()
    route_path = f"{app_name}/{plural_name}"
    
    # Nexa Admin API format: /nexa-admin/api/data/Apps\Inventory\Models\Product
    api_endpoint = f"/nexa-admin/api/data/Apps\\\\{app_name.capitalize()}\\\\Models\\\\{class_name}"

    context = {
        'app_name': app_name,
        'model_name': model_name,
        'class_name': class_name,
        'plural_name': plural_name,
        'route_path': route_path,
        'api_endpoint': api_endpoint,
        'columns': [f.get('name') for f in fields],
        'fields': fields
    }

    base_dir = os.path.join(os.getcwd(), 'resources', 'js', 'admin-nexa')
    
    # 1. List.vue
    list_tpl = load_template('crud/list.tpl')
    write_file(os.path.join(base_dir, 'pages', f"{class_name}List.vue"), render_template(list_tpl, context))
    
    # 2. Form.vue
    form_tpl = load_template('crud/form.tpl')
    write_file(os.path.join(base_dir, 'pages', f"{class_name}Form.vue"), render_template(form_tpl, context))
    
    # 3. Store.js
    store_tpl = load_template('crud/store.tpl')
    write_file(os.path.join(base_dir, 'stores', f"{model_name.lower()}Store.js"), render_template(store_tpl, context))
    
    # 4. Routes.js
    route_tpl = load_template('crud/route.tpl')
    write_file(os.path.join(base_dir, 'routes', f"{model_name.lower()}Routes.js"), render_template(route_tpl, context))

def register_vue_route(app_name, model_name):
    route_file = f"{model_name.lower()}Routes"
    router_path = os.path.join(os.getcwd(), 'resources', 'js', 'router', 'index.js')
    
    if not os.path.exists(router_path):
        return

    with open(router_path, 'r', encoding='utf-8') as f:
        content = f.read()

    imp_line = f"import {route_file} from '../admin-nexa/routes/{route_file}'"
    spread_line = f"    ...{route_file},"

    if imp_line not in content:
        content = content.replace('// NEXA_ROUTE_IMPORTS', f"// NEXA_ROUTE_IMPORTS\n{imp_line}")
        
    if spread_line not in content:
        content = content.replace('// NEXA_ROUTES', f"// NEXA_ROUTES\n{spread_line}")

    with open(router_path, 'w', encoding='utf-8') as f:
        f.write(content)

def register_vue_nav(app_name, model_name):
    dashboard_path = os.path.join(os.getcwd(), 'resources', 'js', 'admin-nexa', 'pages', 'Dashboard.vue')
    
    if not os.path.exists(dashboard_path):
        return

    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()

    display_name = pascal_case(model_name)
    route_name = f"{model_name.lower()}_list"

    card_link = (
        f"        <router-link :to=\"{{ name: '{route_name}' }}\" class=\"admin-card\">\n"
        f"          <h3 class=\"admin-card-title\">{display_name}</h3>\n"
        f"          <p class=\"admin-card-desc\">Kelola rekaman entitas {display_name.lower()} secara terenkapsulasi</p>\n"
        f"        </router-link>"
    )

    if f"name: '{route_name}'" not in content:
        content = content.replace('<!-- ADMIN_MODULE_LINKS -->', f"<!-- ADMIN_MODULE_LINKS -->\n{card_link}")

    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(content)
