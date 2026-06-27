import os
from nexa.core.ai.planner import AIPlannerEngine, PlannerContext
from nexa.core.ai.executor.builder import AIExecutor
from nexa.core.utils.spinner import Spinner

def handle(args):
    if not args:
        print("Usage: nexa create \"<Project Description>\"")
        return
        
    description = " ".join(args)
    cwd = os.getcwd()
    
    # Prompt for framework if not specified in text
    frameworks = ["NexaPHP", "Django", "Flutter", "Lainnya (Biar AI yang tentukan)"]
    print("\n[?] Framework apa yang ingin Anda gunakan untuk proyek ini?")
    for i, f in enumerate(frameworks, 1):
        print(f"  {i}. {f}")
        
    try:
        choice = int(input("> ").strip())
        if 1 <= choice <= 3:
            description += f" (Framework: {frameworks[choice-1]})"
    except Exception:
        pass # Ignore invalid input, AI will guess
        
    planner_context = PlannerContext(
        project_path=cwd,
        knowledge_context="",
        project_facts={},
        pinned_memory=[],
        conversation_memory=[],
        user_goal=description
    )
    
    planner = AIPlannerEngine()
    print("\n[*] Menyusun arsitektur proyek...")
    with Spinner("Planning Execution..."):
        report = planner.plan(planner_context)
        
    if not report.success:
        print(f"\n[!] Gagal membuat rencana: {report.error_message}")
        return
        
    GREEN = '\033[92m'
    RESET = '\033[0m'
    print(f"\n{GREEN}{report.to_markdown()}{RESET}\n")
    
    ans = input("[?] Eksekusi rencana ini dan bangun file fisiknya? (Y/n): ").strip().lower()
    if ans in ['y', 'yes', '']:
        executor = AIExecutor()
        executor.execute(report.plan, planner_context)
    else:
        print("[-] Pembuatan proyek dibatalkan.")
