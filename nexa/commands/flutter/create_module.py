import os
from nexa.core.runtime.command import BaseCommand

class FlutterCreateModuleCommand(BaseCommand):
    """
    Create a new feature module in the Flutter project under lib/modules/.
    Usage: nexa flutter create-module <module_name>
    """
    def run(self):
        if not self.args:
            self.logger.error("Module name required")
            return

        module_name = self.args[0].lower().replace("-", "_")
        
        # 1. Verify pubspec.yaml and read package name
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

        self.logger.step(f"Creating Nexa Flutter module '{module_name}' for package '{package_name}'...")

        # 2. Check and build folder structure
        modules_dir = os.path.join(os.getcwd(), "lib", "modules")
        if not os.path.exists(modules_dir):
            os.makedirs(modules_dir, exist_ok=True)

        mod_dir = os.path.join(modules_dir, module_name)
        if os.path.exists(mod_dir):
            self.logger.error(f"Module '{module_name}' already exists.")
            return

        os.makedirs(os.path.join(mod_dir, "presentation"), exist_ok=True)
        os.makedirs(os.path.join(mod_dir, "application"), exist_ok=True)
        os.makedirs(os.path.join(mod_dir, "data", "models"), exist_ok=True)
        os.makedirs(os.path.join(mod_dir, "data", "repository"), exist_ok=True)

        class_name = module_name.capitalize()

        # 3. Generate templates
        # Route template (with correct package: prefix)
        route_code = f"""import 'package:go_router/go_router.dart';
import 'package:{package_name}/modules/{module_name}/presentation/{module_name}_page.dart';

final {module_name}ModuleRoutes = <GoRoute>[
  GoRoute(
    path: '/{module_name}',
    name: '{module_name}_route',
    builder: (context, state) => const {class_name}Page(),
  ),
];
"""
        with open(os.path.join(mod_dir, "presentation", "routes.dart"), "w") as f:
            f.write(route_code)

        # Page UI template
        page_code = f"""import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class {class_name}Page extends ConsumerWidget {{
  const {class_name}Page({{super.key}});

  @override
  Widget build(BuildContext context, WidgetRef ref) {{
    return Scaffold(
      appBar: AppBar(
        title: const Text('{class_name} Page'),
      ),
      body: const Center(
        child: Text('Welcome to {class_name} Module!'),
      ),
    );
  }}
}}
"""
        with open(os.path.join(mod_dir, "presentation", f"{module_name}_page.dart"), "w") as f:
            f.write(page_code)

        # Riverpod provider/application template
        provider_code = f"""import 'package:flutter_riverpod/flutter_riverpod.dart';

class {class_name}State {{
  final bool isLoading;
  final String? error;

  {class_name}State({{this.isLoading = false, this.error}});

  {class_name}State copyWith({{bool? isLoading, String? error}}) {{
    return {class_name}State(
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }}
}}

class {class_name}Notifier extends StateNotifier<{class_name}State> {{
  {class_name}Notifier() : super({class_name}State());

  Future<void> fetchData() async {{
    state = state.copyWith(isLoading: true);
    try {{
      // Fetch data logic
      state = state.copyWith(isLoading: false);
    }} catch (e) {{
      state = state.copyWith(isLoading: false, error: e.toString());
    }}
  }}
}}

final {module_name}Provider = StateNotifierProvider<{class_name}Notifier, {class_name}State>((ref) {{
  return {class_name}Notifier();
}});
"""
        with open(os.path.join(mod_dir, "application", f"{module_name}_provider.dart"), "w") as f:
            f.write(provider_code)

        # Model template
        model_code = f"""class {class_name}Model {{
  final int? id;
  final String? name;

  {class_name}Model({{this.id, this.name}});

  factory {class_name}Model.fromJson(Map<String, dynamic> json) {{
    return {class_name}Model(
      id: json['id'] as int?,
      name: json['name'] as String?,
    );
  }}

  Map<String, dynamic> toJson() {{
    return {{
      'id': id,
      'name': name,
    }};
  }}
}}
"""
        with open(os.path.join(mod_dir, "data", "models", f"{module_name}_model.dart"), "w") as f:
            f.write(model_code)

        # Repository template
        repository_code = f"""import 'package:{package_name}/core/services/http_service.dart';
import 'package:{package_name}/modules/{module_name}/data/models/{module_name}_model.dart';

class {class_name}Repository {{
  final HttpService _httpService;

  {class_name}Repository(this._httpService);

  Future<List<{class_name}Model>> getItems() async {{
    final response = await _httpService.request('/{module_name}');
    final data = response.data;
    if (data is List) {{
      return data.map((e) => {class_name}Model.fromJson(e as Map<String, dynamic>)).toList();
    }}
    return [];
  }}
}}
"""
        with open(os.path.join(mod_dir, "data", "repository", f"{module_name}_repository.dart"), "w") as f:
            f.write(repository_code)

        # 4. Inject routes into app_router.dart automatically
        router_path = os.path.join(os.getcwd(), "lib", "core", "router", "app_router.dart")
        if os.path.exists(router_path):
            self.logger.info("Automatically injecting module routes into app_router.dart...")
            with open(router_path, "r") as f:
                router_code = f.read()

            import_tag = "// [NEXA_ROUTE_IMPORTS]"
            array_tag = "// [NEXA_ROUTES_ARRAY]"

            if import_tag in router_code and array_tag in router_code:
                new_import = f"import 'package:{package_name}/modules/{module_name}/presentation/routes.dart';\n{import_tag}"
                new_array = f"...{module_name}ModuleRoutes,\n    {array_tag}"

                router_code = router_code.replace(import_tag, new_import)
                router_code = router_code.replace(array_tag, new_array)

                with open(router_path, "w") as f:
                    f.write(router_code)
                self.logger.success("Router registered successfully.")
            else:
                self.logger.warning("Could not find standard placeholder tags in app_router.dart. Registration skipped.")
        else:
            self.logger.warning("lib/core/router/app_router.dart not found. Skipped route injection.")

        self.logger.success(f"Nexa Flutter Module '{module_name}' generated successfully under lib/modules/")

def handle(args):
    cmd = FlutterCreateModuleCommand(args)
    cmd.run()
