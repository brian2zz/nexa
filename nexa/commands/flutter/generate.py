import os
import time
import re
from nexa.core.schema.loaders.yaml_loader import YamlLoader
from nexa.core.validators.schema_validator import SchemaValidationError
from nexa.core.runtime.command import BaseCommand

def to_camel_case(s):
    parts = s.replace("-", "_").split("_")
    if not parts:
        return ""
    return parts[0] + "".join(x.title() for x in parts[1:])

def to_snake_case(s):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class FlutterGenerateCommand(BaseCommand):
    """
    Generate Flutter modules from a YAML schema.
    Usage: nexa flutter generate [schema.yaml]
    """
    def run(self):
        # 1. Determine Schema File
        schema_file = 'nexa.yaml'
        for arg in self.args:
            if not arg.startswith('--') and arg.endswith('.yaml'):
                schema_file = arg
                break

        if not os.path.exists(schema_file):
            self.logger.error(f"Schema file '{schema_file}' not found.")
            return

        # 2. Check Flutter environment
        if not os.path.exists("pubspec.yaml"):
            self.logger.error("pubspec.yaml not found in current directory. Run this inside a Flutter project root.")
            return

        package_name = None
        with open("pubspec.yaml", "r") as f:
            for line in f:
                if line.strip().startswith("name:"):
                    package_name = line.split(":")[1].strip()
                    break

        if not package_name:
            self.logger.error("Failed to read package name from pubspec.yaml")
            return

        self.logger.step(f"Nexa Flutter Engine: Starting generation from '{schema_file}'...")
        start_time = time.time()

        try:
            # 3. Load Schema
            loader = YamlLoader()
            project = loader.load(schema_file)

            # 4. Process each app -> model -> generate flutter module
            modules_dir = os.path.join(os.getcwd(), "lib", "modules")
            os.makedirs(modules_dir, exist_ok=True)

            routes_to_inject = []

            for app in project.apps:
                for model in app.models:
                    module_name = to_snake_case(model.name)
                    class_name = "".join(x.capitalize() for x in module_name.split("_"))

                    self.logger.info(f"Generating module '{module_name}' for model '{class_name}'...")
                    self.generate_module(module_name, class_name, model, package_name)
                    routes_to_inject.append((module_name, class_name))

            self.inject_routes(routes_to_inject, package_name)

            duration = time.time() - start_time
            self.logger.success(f"Flutter project architecture generated in {duration:.2f}s.")

        except SchemaValidationError as e:
            self.render_errors(e.errors)
        except Exception as e:
            self.logger.error(f"FATAL ERROR: {str(e)}")

    def generate_module(self, module_name, class_name, model, package_name):
        mod_dir = os.path.join(os.getcwd(), "lib", "modules", module_name)
        os.makedirs(os.path.join(mod_dir, "presentation"), exist_ok=True)
        os.makedirs(os.path.join(mod_dir, "application"), exist_ok=True)
        os.makedirs(os.path.join(mod_dir, "data", "models"), exist_ok=True)
        os.makedirs(os.path.join(mod_dir, "data", "repository"), exist_ok=True)

        self.generate_routes(mod_dir, module_name, class_name, package_name)
        self.generate_page(mod_dir, module_name, class_name)
        self.generate_provider(mod_dir, module_name, class_name)
        self.generate_model(mod_dir, module_name, class_name, model)
        self.generate_repository(mod_dir, module_name, class_name, package_name)

    def generate_routes(self, mod_dir, module_name, class_name, package_name):
        route_code = f"import 'package:go_router/go_router.dart';\nimport 'package:{package_name}/modules/{module_name}/presentation/{module_name}_page.dart';\n\nfinal {module_name}ModuleRoutes = <GoRoute>[\n  GoRoute(\n    path: '/{module_name}',\n    name: '{module_name}_route',\n    builder: (context, state) => const {class_name}Page(),\n  ),\n];\n"
        with open(os.path.join(mod_dir, "presentation", "routes.dart"), "w") as f:
            f.write(route_code)

    def generate_page(self, mod_dir, module_name, class_name):
        page_code = f"import 'package:flutter/material.dart';\nimport 'package:flutter_riverpod/flutter_riverpod.dart';\n\nclass {class_name}Page extends ConsumerWidget {{\n  const {class_name}Page({{super.key}});\n\n  @override\n  Widget build(BuildContext context, WidgetRef ref) {{\n    return Scaffold(\n      appBar: AppBar(\n        title: const Text('{class_name} Page'),\n      ),\n      body: const Center(\n        child: Text('Welcome to {class_name} Module!'),\n      ),\n    );\n  }}\n}}\n"
        with open(os.path.join(mod_dir, "presentation", f"{module_name}_page.dart"), "w") as f:
            f.write(page_code)

    def generate_provider(self, mod_dir, module_name, class_name):
        provider_code = f"import 'package:flutter_riverpod/flutter_riverpod.dart';\n\nclass {class_name}State {{\n  final bool isLoading;\n  final String? error;\n\n  {class_name}State({{this.isLoading = false, this.error}});\n\n  {class_name}State copyWith({{bool? isLoading, String? error}}) {{\n    return {class_name}State(\n      isLoading: isLoading ?? this.isLoading,\n      error: error ?? this.error,\n    );\n  }}\n}}\n\nclass {class_name}Notifier extends StateNotifier<{class_name}State> {{\n  {class_name}Notifier() : super({class_name}State());\n\n  Future<void> fetchData() async {{\n    state = state.copyWith(isLoading: true);\n    try {{\n      // Fetch data logic\n      state = state.copyWith(isLoading: false);\n    }} catch (e) {{\n      state = state.copyWith(isLoading: false, error: e.toString());\n    }}\n  }}\n}}\n\nfinal {module_name}Provider = StateNotifierProvider<{class_name}Notifier, {class_name}State>((ref) {{\n  return {class_name}Notifier();\n}});\n"
        with open(os.path.join(mod_dir, "application", f"{module_name}_provider.dart"), "w") as f:
            f.write(provider_code)

    def generate_model(self, mod_dir, module_name, class_name, model):
        fields = []
        model_fields = model.fields if hasattr(model, 'fields') and model.fields else []
        
        if not any(f.name.lower() == 'id' for f in model_fields):
            fields.append({"dart_key": "id", "type": "int?", "json_key": "id", "from_json": "json['id'] as int?"})

        for f in model_fields:
            camel_key = to_camel_case(f.name)
            dart_type = "dynamic"
            json_cast = ""
            
            t = f.type.lower() if hasattr(f, 'type') else "string"
            if t in ["integer", "int"]:
                dart_type = "int?"
                json_cast = "as int?"
            elif t in ["decimal", "float", "double"]:
                dart_type = "double?"
                json_cast = "as double?"
            elif t in ["boolean", "bool"]:
                dart_type = "bool?"
                json_cast = "as bool?"
            elif t in ["string", "text", "char", "email", "url", "image"]:
                dart_type = "String?"
                json_cast = "as String?"
            elif t == "foreignkey":
                dart_type = "int?"
                json_cast = "as int?"

            if dart_type == "double?":
                from_json = f"(json['{f.name}'] as num?)?.toDouble()"
            else:
                from_json = f"json['{f.name}'] {json_cast}".strip()

            fields.append({
                "dart_key": camel_key,
                "type": dart_type,
                "json_key": f.name,
                "from_json": from_json
            })

        dart_code = f"class {class_name}Model {{\n"
        for f in fields:
            dart_code += f"  final {f['type']} {f['dart_key']};\n"
        
        dart_code += "\n"
        dart_code += f"  {class_name}Model({{\n"
        for f in fields:
            dart_code += f"    this.{f['dart_key']},\n"
        dart_code += "  });\n\n"

        dart_code += f"  factory {class_name}Model.fromJson(Map<String, dynamic> json) {{\n"
        dart_code += f"    return {class_name}Model(\n"
        for f in fields:
            dart_code += f"      {f['dart_key']}: {f['from_json']},\n"
        dart_code += "    );\n"
        dart_code += "  }\n\n"

        dart_code += "  Map<String, dynamic> toJson() {\n"
        dart_code += "    return {\n"
        for f in fields:
            dart_code += f"      '{f['json_key']}': {f['dart_key']},\n"
        dart_code += "    };\n"
        dart_code += "  }\n"
        dart_code += "}\n"

        with open(os.path.join(mod_dir, "data", "models", f"{module_name}_model.dart"), "w") as f:
            f.write(dart_code)

    def generate_repository(self, mod_dir, module_name, class_name, package_name):
        repository_code = f"import 'package:{package_name}/core/services/http_service.dart';\nimport 'package:{package_name}/modules/{module_name}/data/models/{module_name}_model.dart';\n\nclass {class_name}Repository {{\n  final HttpService _httpService;\n\n  {class_name}Repository(this._httpService);\n\n  Future<List<{class_name}Model>> getItems() async {{\n    final response = await _httpService.request('/api/v1/{module_name}/');\n    final data = response.data;\n    if (data != null && data['results'] != null) {{\n        final results = data['results'] as List;\n        return results.map((e) => {class_name}Model.fromJson(e as Map<String, dynamic>)).toList();\n    }} else if (data is List) {{\n      return data.map((e) => {class_name}Model.fromJson(e as Map<String, dynamic>)).toList();\n    }}\n    return [];\n  }}\n}}\n"
        with open(os.path.join(mod_dir, "data", "repository", f"{module_name}_repository.dart"), "w") as f:
            f.write(repository_code)

    def inject_routes(self, routes_to_inject, package_name):
        router_path = os.path.join(os.getcwd(), "lib", "core", "router", "app_router.dart")
        if not os.path.exists(router_path):
            self.logger.warning("lib/core/router/app_router.dart not found. Skipped route injection.")
            return

        with open(router_path, "r") as f:
            router_code = f.read()

        import_tag = "// [NEXA_ROUTE_IMPORTS]"
        array_tag = "// [NEXA_ROUTES_ARRAY]"

        if import_tag not in router_code or array_tag not in router_code:
            self.logger.warning("Could not find standard placeholder tags in app_router.dart. Registration skipped.")
            return

        for module_name, class_name in routes_to_inject:
            # Check if already injected
            import_str = f"import 'package:{package_name}/modules/{module_name}/presentation/routes.dart';"
            if import_str not in router_code:
                new_import = f"{import_str}\n{import_tag}"
                router_code = router_code.replace(import_tag, new_import)

            array_str = f"...{module_name}ModuleRoutes,"
            if array_str not in router_code:
                new_array = f"{array_str}\n    {array_tag}"
                router_code = router_code.replace(array_tag, new_array)

        with open(router_path, "w") as f:
            f.write(router_code)
        self.logger.success("All module routes registered successfully.")

    def render_errors(self, errors):
        self.logger.error("!!! SCHEMA VALIDATION FAILED !!!")
        print("\n" + "!" * 60)
        for error in errors:
            print(f"  [ERROR] [{error.code.upper()}] {error.message}")
            if hasattr(error, 'model') and error.model:
                app_name = error.app if hasattr(error, 'app') else 'Unknown'
                field_name = error.field if hasattr(error, 'field') and error.field else 'Any'
                print(f"          > Location: App({app_name}) -> Model({error.model}) -> Field({field_name})")
        print("!" * 60 + "\n")
        self.logger.warning("Please fix the issues in your schema and re-run generation.")

def handle(args):
    cmd = FlutterGenerateCommand(args)
    cmd.run()
