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
        
        for step in plan.execution_steps:
            if step.action.lower() in ["create", "modify"]:
                target_path = os.path.join(context.project_path, step.target)
                
                # Make sure directory exists
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                
                with Spinner(f"[{step.action.upper()}] Generating code for {step.target}..."):
                    code = self.generator.generate_file(plan, context, step.target, step.description)
                
                if code:
                    try:
                        with open(target_path, 'w', encoding='utf-8') as f:
                            f.write(code)
                        print(f"  [+] {step.target} written successfully.")
                    except Exception as e:
                        print(f"  [!] Failed to write {step.target}: {e}")
                else:
                    print(f"  [!] Generator returned empty code for {step.target}")
            
            elif step.action.lower() == "command":
                print(f"  [*] Skipping shell command for security: {step.target}")
            
        print("[*] Execution Complete!\n")
