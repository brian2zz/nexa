import os
from nexa.core.ai.planner.schema import ExecutionPlan, PlannerContext
from nexa.core.ai.executor.generator import AIGenerator
from nexa.core.utils.spinner import Spinner

class AIExecutor:
    """
    Executes an ExecutionPlan by looping through its steps, calling the Generator, and writing files.
    """
    def __init__(self):
        self.generator = AIGenerator()

    def execute(self, plan: ExecutionPlan, context: PlannerContext):
        print(f"\n[*] Starting Execution of: {plan.goal}")
        
        for stage in getattr(plan, 'stages', []):
            for intent in stage.intents:
                # Basic mapping for backward compatibility during transition
                action = intent.action.lower()
                target = intent.parameters.get("target", intent.parameters.get("path", ""))
                description = intent.description
                
                if action in ["create", "modify"]:
                    if not target:
                        continue
                        
                    target_path = os.path.join(context.project_path, target)
                    
                    # Make sure directory exists
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    
                    with Spinner(f"[{action.upper()}] Generating code for {target}..."):
                        code = self.generator.generate_file(plan, context, target, description)
                    
                    if code:
                        try:
                            with open(target_path, 'w', encoding='utf-8') as f:
                                f.write(code)
                            print(f"  [+] {target} written successfully.")
                        except Exception as e:
                            print(f"  [!] Failed to write {target}: {e}")
                    else:
                        print(f"  [!] Generator returned empty code for {target}")
                
                elif action == "terminal_command":
                    print(f"  [*] Terminal command execution is delegated to the ExecutionLayer.")
            
        print("[*] Execution Complete!\n")
