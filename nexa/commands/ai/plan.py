import os
import json

def handle(args):
    from nexa.core.ai.planner import Planner
    from nexa.core.ai.memory import Memory
    from nexa.core.ai.context_builder import ContextBuilder
    from nexa.core.ai.analyzer import Analyzer
    
    if not args:
        print("[!] Penggunaan: nexa plan \"Deskripsi Fitur\"")
        return
        
    goal = " ".join(args)
    
    root_path = os.path.abspath(os.getcwd())
    memory = Memory()
    project = memory.get_project(root_path)
    
    context = {}
    if project:
        files = memory.get_files(project['id'])
        
        cb = ContextBuilder()
        cb_context = cb.build(project['framework'], files)
        
        analyzer = Analyzer()
        stats = analyzer.analyze_stats(project['framework'], project['language'], files)
        
        context['framework'] = project['framework']
        context['architecture'] = stats.get('architecture', [])
        context['statistics'] = stats.get('statistics', {})
        context['important_files'] = cb_context.get('important_files', [])
        
    planner = Planner()
    result = planner.plan(goal, context)
    
    print("[*] Generating Plan Template...")
    print(json.dumps(result, indent=2))
