import os
import json

base_dir = "g:/project code/nexa"

# 1. nexa/core/ai/context_builder.py
context_builder_content = """class ContextBuilder:
    def build(self, project_framework, files_list):
        important_files = []
        framework = project_framework.lower()
        
        for f in files_list:
            path = f['path'].replace("\\\\", "/")
            path_lower = path.lower()
            
            # React / Next / Vue Ecosystem
            if framework in ['react_native', 'nextjs', 'nuxtjs', 'vuejs', 'reactjs']:
                if ('src/app.' in path_lower or 'src/index.' in path_lower or 
                    '/services/' in path_lower or '/context/' in path_lower or 
                    '/components/' in path_lower or '/hooks/' in path_lower):
                    important_files.append(path)
                    
            # Flutter
            elif framework == 'flutter':
                if ('lib/main.dart' in path_lower or '/screens/' in path_lower or 
                    '/controllers/' in path_lower or '/widgets/' in path_lower or
                    '/services/' in path_lower):
                    important_files.append(path)
                    
            # Django
            elif 'django' in framework:
                if ('models.py' in path_lower or 'views.py' in path_lower or 
                    'urls.py' in path_lower or 'serializers.py' in path_lower or
                    'services.py' in path_lower):
                    important_files.append(path)
                    
            # PHP (NexaPHP / Laravel / CI3)
            elif framework in ['nexaphp', 'laravel', 'codeigniter3']:
                if ('routes/' in path_lower or 'controllers/' in path_lower or 
                    'modules/' in path_lower or 'models/' in path_lower or
                    'services/' in path_lower):
                    important_files.append(path)
                    
            # Generic fallback
            else:
                if ('main.' in path_lower or 'app.' in path_lower or 'index.' in path_lower or
                    'routes' in path_lower or 'controllers' in path_lower or 'models' in path_lower):
                    important_files.append(path)
                    
        return {
            "framework": framework,
            "important_files": important_files
        }
"""

# 2. nexa/core/ai/analyzer.py
analyzer_content = """class Analyzer:
    def analyze_stats(self, project_framework, project_language, files_list):
        framework = project_framework.lower()
        
        summary = {
            "pages": 0, "components": 0, "hooks": 0, "services": 0, "contexts": 0,
            "screens": 0, "widgets": 0, "controllers": 0, "models": 0, "views": 0,
            "serializers": 0, "repositories": 0, "modules": 0, "entities": 0
        }
        
        for f in files_list:
            path = f['path'].lower().replace("\\\\", "/")
            
            # JS/TS ecosystem counting
            if framework in ['reactjs', 'nextjs', 'vuejs', 'react_native', 'nuxtjs']:
                if '/pages/' in path or '/app/' in path: summary['pages'] += 1
                if '/components/' in path: summary['components'] += 1
                if '/hooks/' in path or path.startswith('use'): summary['hooks'] += 1
                if '/services/' in path: summary['services'] += 1
                if '/context/' in path: summary['contexts'] += 1
                
            # Flutter counting
            elif framework == 'flutter':
                if '/screens/' in path: summary['screens'] += 1
                if '/widgets/' in path: summary['widgets'] += 1
                if '/controllers/' in path: summary['controllers'] += 1
                if '/services/' in path: summary['services'] += 1
                
            # Django counting
            elif 'django' in framework:
                if 'models.py' in path: summary['models'] += 1
                if 'views.py' in path: summary['views'] += 1
                if 'serializers.py' in path: summary['serializers'] += 1
                if 'services.py' in path or '/services/' in path: summary['services'] += 1
                if 'repositories.py' in path or '/repositories/' in path: summary['repositories'] += 1
                
            # NexaPHP / Laravel counting
            elif framework in ['nexaphp', 'laravel']:
                if '/modules/' in path: summary['modules'] += 1
                if '/controllers/' in path: summary['controllers'] += 1
                if '/services/' in path: summary['services'] += 1
                if '/repositories/' in path: summary['repositories'] += 1
                if '/entities/' in path or '/models/' in path: summary['entities'] += 1
                
            # Generic
            else:
                if '/controllers/' in path: summary['controllers'] += 1
                if '/models/' in path: summary['models'] += 1
                if '/views/' in path: summary['views'] += 1
                if '/services/' in path: summary['services'] += 1
                
        # Clean up empty stats
        cleaned_summary = {k: v for k, v in summary.items() if v > 0}
        
        return {
            "framework": framework,
            "language": project_language,
            "summary": cleaned_summary
        }
        
    def analyze_rules(self, files_list):
        warnings = []
        has_tests = False
        
        for f in files_list:
            path = f['path'].lower()
            size = f['size']
            
            if 'test' in path or 'spec.' in path:
                has_tests = True
                
            if size > 30000:
                warnings.append({
                    "type": "warning",
                    "message": f"Large file detected (>30KB): {f['path']}"
                })
                
        if not has_tests:
            warnings.append({
                "type": "warning",
                "message": "Project has no tests"
            })
            
        return warnings
"""

# 3. nexa/core/ai/planner.py
planner_content = """class Planner:
    def plan(self, goal):
        goal_lower = goal.lower()
        
        if 'auth' in goal_lower or 'login' in goal_lower or 'register' in goal_lower:
            return {
                "goal": goal,
                "complexity": "medium",
                "risk": "medium",
                "steps": [
                    {"title": "Setup Authentication Library", "description": "Install JWT or Session based auth library."},
                    {"title": "Create User Model", "description": "Define user schema with email and hashed password."},
                    {"title": "Create Auth Controllers", "description": "Implement register, login, and logout endpoints."},
                    {"title": "Add Auth Middleware", "description": "Protect private routes using middleware."},
                    {"title": "Build Frontend UI", "description": "Create login and register forms."}
                ]
            }
            
        if 'notification' in goal_lower or 'email' in goal_lower:
            return {
                "goal": goal,
                "complexity": "low",
                "risk": "low",
                "steps": [
                    {"title": "Setup Notification Provider", "description": "Integrate SMTP, FCM, or Pusher."},
                    {"title": "Create Notification Service", "description": "Build logic to send email/push notifications."},
                    {"title": "Create Notification UI", "description": "Add bell icon and dropdown in the frontend."}
                ]
            }
            
        if 'payment' in goal_lower or 'stripe' in goal_lower or 'checkout' in goal_lower:
            return {
                "goal": goal,
                "complexity": "high",
                "risk": "high",
                "steps": [
                    {"title": "Setup Payment Gateway Integration", "description": "Configure API keys for Stripe/Midtrans."},
                    {"title": "Create Webhook Handler", "description": "Handle asynchronous payment success/failure events securely."},
                    {"title": "Update Order Status", "description": "Change database order status upon successful payment."},
                    {"title": "Build Checkout UI", "description": "Integrate frontend payment elements/widgets."}
                ]
            }
            
        # Generic Template
        return {
            "goal": goal,
            "complexity": "medium",
            "risk": "low",
            "steps": [
                {"title": "Define Database Schema", "description": "Create migration and models for the new feature."},
                {"title": "Create Business Logic (Service)", "description": "Implement core feature logic in service layer."},
                {"title": "Expose API (Controller)", "description": "Create endpoints and validate inputs."},
                {"title": "Build UI Components", "description": "Implement screens and state management in frontend."}
            ]
        }
"""

# 4. nexa/commands/ai/analyze.py
cmd_analyze_content = """import os
import json

def handle(args):
    from nexa.core.ai.memory import Memory
    from nexa.core.ai.context_builder import ContextBuilder
    from nexa.core.ai.analyzer import Analyzer
    
    root_path = os.path.abspath(os.getcwd())
    memory = Memory()
    project = memory.get_project(root_path)
    
    if not project:
        print("[!] Project belum dipindai. Silakan jalankan 'nexa scan' terlebih dahulu.")
        return
        
    files = memory.get_files(project['id'])
    
    # Context Building
    cb = ContextBuilder()
    context = cb.build(project['framework'], files)
    
    # Analyzing
    analyzer = Analyzer()
    stats = analyzer.analyze_stats(project['framework'], project['language'], files)
    rules = analyzer.analyze_rules(files)
    
    result = {
        "framework": stats["framework"],
        "language": stats["language"],
        "summary": stats["summary"],
        "important_files": context["important_files"],
        "warnings": rules
    }
    
    print("[*] Running Static Analysis...")
    print(json.dumps(result, indent=2))
"""

# 5. nexa/commands/ai/plan.py
cmd_plan_content = """import os
import json

def handle(args):
    from nexa.core.ai.planner import Planner
    
    if not args:
        print("[!] Penggunaan: nexa plan \\"Deskripsi Fitur\\"")
        return
        
    goal = " ".join(args)
    planner = Planner()
    result = planner.plan(goal)
    
    print("[*] Generating Plan Template...")
    print(json.dumps(result, indent=2))
"""

files_to_write = {
    "nexa/core/ai/context_builder.py": context_builder_content,
    "nexa/core/ai/analyzer.py": analyzer_content,
    "nexa/core/ai/planner.py": planner_content,
    "nexa/commands/ai/analyze.py": cmd_analyze_content,
    "nexa/commands/ai/plan.py": cmd_plan_content,
}

for path, content in files_to_write.items():
    full_path = os.path.join(base_dir, path)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Scaffolding V3 complete!")
