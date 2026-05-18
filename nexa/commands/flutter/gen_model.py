import os
import json
import re
from nexa.core.runtime.command import BaseCommand

def to_camel_case(s):
    parts = s.replace("-", "_").split("_")
    if not parts:
        return ""
    return parts[0] + "".join(x.title() for x in parts[1:])

def to_snake_case(s):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class FlutterGenModelCommand(BaseCommand):
    """
    Generate a Dart Model class from a JSON file.
    Usage: nexa flutter gen-model <json_file_path> [--module=<module_name>] [--name=<model_class_name>]
    """
    def run(self):
        json_path = None
        module_name = None
        class_name_input = None

        # Parse arguments
        for arg in self.args:
            if arg.startswith('--module='):
                module_name = arg.split('=')[1].strip()
            elif arg.startswith('--name='):
                class_name_input = arg.split('=')[1].strip()
            elif not arg.startswith('--'):
                json_path = arg

        if not json_path:
            self.logger.error("JSON file path is required. Usage: nexa flutter gen-model <json_file_path> [--module=<module_name>] [--name=<model_class_name>]")
            return

        if not os.path.exists(json_path):
            self.logger.error(f"JSON file not found: {json_path}")
            return

        # 1. Parse JSON data
        try:
            with open(json_path, 'r') as f:
                raw_data = json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to parse JSON file: {e}")
            return

        # Handle list of objects
        if isinstance(raw_data, list):
            if not raw_data:
                self.logger.error("JSON array is empty. Cannot determine schema.")
                return
            data = raw_data[0]
        elif isinstance(raw_data, dict):
            data = raw_data
        else:
            self.logger.error("Invalid JSON format. Expected Object or Array of Objects.")
            return

        # 2. Determine class name
        if class_name_input:
            model_class = class_name_input
            if not model_class.endswith("Model") and not model_class.endswith("model"):
                model_class = model_class + "Model"
        else:
            base = os.path.splitext(os.path.basename(json_path))[0]
            model_class = "".join(x.capitalize() for x in base.replace("-", "_").split("_")) + "Model"

        # Force capitalize first letter of class name
        model_class = model_class[0].upper() + model_class[1:]

        self.logger.step(f"Generating Dart Model class '{model_class}' from '{json_path}'...")

        # 3. Analyze keys and map types
        fields = []
        for key, val in data.items():
            camel_key = to_camel_case(key)
            t = type(val)
            
            if t == int:
                dart_type = "int?"
                json_cast = f"as int?"
            elif t == float:
                dart_type = "double?"
                json_cast = f"as double?"
            elif t == bool:
                dart_type = "bool?"
                json_cast = f"as bool?"
            elif t == str:
                dart_type = "String?"
                json_cast = f"as String?"
            elif t == list:
                if val and all(isinstance(x, str) for x in val):
                    dart_type = "List<String>?"
                    json_cast = f"as List<String>?"
                elif val and all(isinstance(x, int) for x in val):
                    dart_type = "List<int>?"
                    json_cast = f"as List<int>?"
                elif val and all(isinstance(x, float) for x in val):
                    dart_type = "List<double>?"
                    json_cast = f"as List<double>?"
                elif val and all(isinstance(x, bool) for x in val):
                    dart_type = "List<bool>?"
                    json_cast = f"as List<bool>?"
                else:
                    dart_type = "List<dynamic>?"
                    json_cast = f"as List<dynamic>?"
            elif t == dict:
                dart_type = "Map<String, dynamic>?"
                json_cast = f"as Map<String, dynamic>?"
            elif val is None:
                dart_type = "dynamic"
                json_cast = ""
            else:
                dart_type = "dynamic"
                json_cast = ""

            # Specialized double/float cast safety in Dart
            if dart_type == "double?":
                from_json_expression = f"(json['{key}'] as num?)?.toDouble()"
            else:
                from_json_expression = f"json['{key}'] {json_cast}".strip()

            fields.append({
                "json_key": key,
                "dart_key": camel_key,
                "type": dart_type,
                "from_json": from_json_expression
            })

        # 4. Generate Dart code
        dart_code = f"class {model_class} {{\n"
        
        # Field declarations
        for f in fields:
            dart_code += f"  final {f['type']} {f['dart_key']};\n"
        
        dart_code += "\n"
        
        # Constructor
        dart_code += f"  {model_class}({{\n"
        for f in fields:
            dart_code += f"    this.{f['dart_key']},\n"
        dart_code += "  });\n\n"

        # fromJson factory
        dart_code += f"  factory {model_class}.fromJson(Map<String, dynamic> json) {{\n"
        dart_code += f"    return {model_class}(\n"
        for f in fields:
            dart_code += f"      {f['dart_key']}: {f['from_json']},\n"
        dart_code += "    );\n"
        dart_code += "  }\n\n"

        # toJson method
        dart_code += "  Map<String, dynamic> toJson() {\n"
        dart_code += "    return {\n"
        for f in fields:
            dart_code += f"      '{f['json_key']}': {f['dart_key']},\n"
        dart_code += "    };\n"
        dart_code += "  }\n"
        
        dart_code += "}\n"

        # 5. Determine target path and write
        snake_file_name = to_snake_case(model_class)
        if not snake_file_name.endswith("_model"):
            snake_file_name = snake_file_name + "_model"
        
        if module_name:
            target_dir = os.path.join(os.getcwd(), "lib", "modules", module_name, "data", "models")
            os.makedirs(target_dir, exist_ok=True)
            output_path = os.path.join(target_dir, f"{snake_file_name}.dart")
        else:
            output_path = os.path.join(os.getcwd(), f"{snake_file_name}.dart")

        with open(output_path, 'w') as f:
            f.write(dart_code)

        self.logger.success(f"Successfully generated Dart Model at: {output_path}")

def handle(args):
    cmd = FlutterGenModelCommand(args)
    cmd.run()
