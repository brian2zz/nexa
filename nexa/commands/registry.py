"""
Central Registry for Nexa CLI Commands.
"""

GROUPS = {
    "django": [
        {"name": "new", "module": "nexa.commands.django.new", "usage": "nexa django new <project_name>", "description": "Create a new Django project"},
        {"name": "startapp", "module": "nexa.commands.django.startapp", "usage": "nexa django startapp <app_name>", "description": "Create a new Django app"},
        {"name": "generate", "module": "nexa.commands.django.generate", "usage": "nexa django generate <type> [args]", "description": "Scaffold Django components (models, views, etc.)"},
        {"name": "make:api", "module": "nexa.commands.django.makeapi", "usage": "nexa django make:api", "description": "Generate REST API from models"},
        {"name": "build", "module": "nexa.commands.django.build", "usage": "nexa django build", "description": "Build the Django project"},
        {"name": "install", "module": "nexa.commands.django.install", "usage": "nexa django install", "description": "Install project dependencies"},
        {"name": "migrate", "module": "nexa.commands.django.migrate", "usage": "nexa django migrate", "description": "Run Django database migrations"},
        {"name": "run", "module": "nexa.commands.django.run", "usage": "nexa django run", "description": "Run Django development server"},
        {"name": "doctor", "module": "nexa.commands.django.doctor", "usage": "nexa django doctor", "description": "Check Django project health"},
        {"name": "inspect", "module": "nexa.commands.django.inspect", "usage": "nexa django inspect", "description": "Inspect project structure"},
        {"name": "dev", "module": "nexa.commands.django.dev", "usage": "nexa django dev", "description": "Start development tools"},
    ],
    "flutter": [
        {"name": "new", "module": "nexa.commands.flutter.new", "usage": "nexa flutter new <project_name>", "description": "Create a new Flutter project"},
        {"name": "create-module", "module": "nexa.commands.flutter.create_module", "usage": "nexa flutter create-module <module_name>", "description": "Create a new Flutter module"},
        {"name": "gen-model", "module": "nexa.commands.flutter.gen_model", "usage": "nexa flutter gen-model", "description": "Generate models from JSON"},
        {"name": "generate", "module": "nexa.commands.flutter.generate", "usage": "nexa flutter generate", "description": "Scaffold Flutter components"},
        {"name": "run", "module": "nexa.commands.flutter.run", "usage": "nexa flutter run", "description": "Run Flutter application"},
        {"name": "doctor", "module": "nexa.commands.flutter.doctor", "usage": "nexa flutter doctor", "description": "Check Flutter installation health"},
    ],
    "php": [
        {"name": "new", "module": "nexa.commands.php.new", "usage": "nexa php new <project_name>", "description": "Create a new PHP project"},
        {"name": "make:module", "module": "nexa.commands.php.make_module", "usage": "nexa php make:module <name>", "description": "Create a new module"},
        {"name": "make:model", "module": "nexa.commands.php.make_model", "usage": "nexa php make:model <name>", "description": "Create a new model"},
        {"name": "generate", "module": "nexa.commands.php.generate", "usage": "nexa php generate", "description": "Scaffold PHP components"},
        {"name": "make:migration", "module": "nexa.commands.php.make_migration", "usage": "nexa php make:migration <name>", "description": "Create a database migration"},
        {"name": "migrate", "module": "nexa.commands.php.migrate", "usage": "nexa php migrate", "description": "Run database migrations"},
        {"name": "install", "module": "nexa.commands.php.install", "usage": "nexa php install", "description": "Install dependencies"},
        {"name": "run", "module": "nexa.commands.php.run", "usage": "nexa php run", "description": "Run PHP server"},
    ],
    "ai": [
        {"name": "shell", "module": "nexa.commands.ai.shell", "usage": "nexa ai shell", "description": "Enter the AI interactive shell"},
        {"name": "scan", "module": "nexa.commands.ai.scan", "usage": "nexa ai scan", "description": "Scan and index the project"},
        {"name": "tree", "module": "nexa.commands.ai.tree", "usage": "nexa ai tree", "description": "Show the project tree map"},
        {"name": "analyze", "module": "nexa.commands.ai.analyze", "usage": "nexa ai analyze", "description": "Analyze project architecture"},
        {"name": "plan", "module": "nexa.commands.ai.plan", "usage": "nexa ai plan <goal>", "description": "Generate an execution plan"},
        {"name": "create", "module": "nexa.commands.ai.create", "usage": "nexa ai create <description>", "description": "Autonomous scaffolding generator"},
        {"name": "explain", "module": "nexa.commands.ai.explain", "usage": "nexa ai explain", "description": "Explain code or project structure"},
        {"name": "ask", "module": "nexa.commands.ai.ask", "usage": "nexa ai ask <question>", "description": "Ask a question about the project"},
    ]
}

def render_root_help():
    print("Nexa CLI - Framework Developer Tool")
    print("Usage: nexa <command_group> <subcommand> [args]")
    print("\nAvailable Command Groups:")
    print("  django   - Commands for Django projects")
    print("  flutter  - Commands for Flutter projects")
    print("  php      - Commands for PHP projects")
    print("  ai       - AI Assistant and analysis commands")
    print("\nGlobal Commands:")
    print("  update   - Update Nexa CLI")
    print("  version  - Show version information")
    print("  help     - Show this help message")
    print("\nFor more info on a specific group, run: nexa <group> help")

def render_group_help(group: str):
    if group not in GROUPS:
        print(f"[!] Unknown group: {group}")
        return
        
    print(f"Nexa {group.title()} CLI")
    print(f"Usage: nexa {group} <subcommand> [args]")
    print("\nAvailable subcommands:")
    for cmd in GROUPS[group]:
        if not cmd.get("hidden", False):
            name = cmd["name"].ljust(15)
            print(f"  {name} - {cmd['description']}")

def render_command_help(group: str, cmd_name: str):
    if group not in GROUPS:
        return
        
    for cmd in GROUPS[group]:
        if cmd["name"] == cmd_name:
            print(f"Command: {cmd['name']}")
            print(f"Usage:   {cmd['usage']}")
            print(f"Desc:    {cmd['description']}")
            return
            
    print(f"[!] Command '{cmd_name}' not found in group '{group}'.")
