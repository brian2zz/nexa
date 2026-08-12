import os
import sys
from nexa.config import Config

def handle(args):
    if sys.stdout.encoding != 'utf-8' and hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    if not args:
        print("[!] Penggunaan: nexa plan \"Deskripsi Fitur\"")
        return
        
    goal = " ".join(args)
    cwd = os.path.abspath(os.getcwd())
    
    from nexa.core.ai.agent_loop import AILoopEngine
    from nexa.core.ai.planner.formatter import PlanFormatter
    from nexa.core.ai.planner.schema import PlannerContext
    
    planner_context = PlannerContext(
        project_path=cwd,
        user_goal=goal,
        knowledge_context="",
        project_facts={},
        pinned_memory=[],
        conversation_memory=[]
    )
    
    engine = AILoopEngine()
    
    print("[*] Generating Plan...")
    report = engine.run_loop(planner_context, session_id=0)
    
    if report.success:
        GREEN = '\033[92m'
        RESET = '\033[0m'
        print(f"\n{GREEN}{PlanFormatter().to_markdown(report.plan)}{RESET}\n")
    else:
        RED = '\033[91m'
        RESET = '\033[0m'
        print(f"\n{RED}Plan generation failed: {report.error_message}{RESET}\n")
