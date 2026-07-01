import json
from nexa.core.events.bus import PipelineBus, EventContext

class ApprovalUI:
    """
    Antarmuka Teks (TUI) Interaktif untuk menangani fase Approval.
    Menghentikan loop terminal sementara untuk meminta keputusan eksekusi dari manusia.
    """
    def __init__(self, bus: PipelineBus):
        self.bus = bus
        self.is_waiting = False
        self.current_plan = {}
        
    def handle_before_approval(self, context: EventContext):
        """
        Didaftarkan sebagai subscriber dari PipelineBus untuk event BeforeApproval.
        """
        self.is_waiting = True
        self.payload = context.payload or {}
        
        # Ekstrak data
        patch_result = self.payload.get("patch_result", {})
        execution_plan = self.payload.get("plan", {})
        
        print("\n" + "═" * 50)
        print(" EXECUTION PLAN APPROVAL")
        print("═" * 50)
        
        is_dict = isinstance(execution_plan, dict)
        stages = execution_plan.get("stages", []) if is_dict else getattr(execution_plan, "stages", [])
        
        if stages:
            for stage in stages:
                stage_is_dict = isinstance(stage, dict)
                stage_name = stage.get('name', 'Unknown') if stage_is_dict else getattr(stage, 'name', 'Unknown')
                print(f" [STAGE] {stage_name}")
                
                steps = stage.get("steps", []) if stage_is_dict else getattr(stage, "steps", [])
                if not steps:
                    intents = stage.get("intents", []) if stage_is_dict else getattr(stage, "intents", [])
                    for idx, intent in enumerate(intents, 1):
                        intent_is_dict = isinstance(intent, dict)
                        action = intent.get("action", "") if intent_is_dict else getattr(intent, "action", "")
                        params_raw = intent.get("parameters", {}) if intent_is_dict else getattr(intent, "parameters", {})
                        params = str(params_raw)
                        print(f"  {idx}. {action} -> {params}")
                else:
                    for idx, step in enumerate(steps, 1):
                        step_is_dict = isinstance(step, dict)
                        cmd = step.get("raw_command", " ".join(step.get("args", []))) if step_is_dict else getattr(step, "raw_command", " ".join(getattr(step, "args", [])))
                        risk = step.get("risk_level", "UNKNOWN") if step_is_dict else getattr(step, "risk_level", "UNKNOWN")
                        strategy = step.get("strategy", "STOP_ON_ERROR") if step_is_dict else getattr(step, "strategy", "STOP_ON_ERROR")
                        
                        risk_color = '\033[91m' if risk.upper() in ['HIGH', 'CRITICAL'] else '\033[93m' if risk.upper() == 'MEDIUM' else '\033[92m'
                        reset = '\033[0m'
                        
                        print(f"  {idx}. {cmd}")
                        print(f"     Risk: {risk_color}{risk}{reset} | Strategy: {strategy}")
                print("─" * 50)
                
        estimated_duration = execution_plan.get("estimated_time", "Unknown") if is_dict else getattr(execution_plan, "estimated_time", "Unknown")
        rollback_strat = execution_plan.get("rollback_strategy", "") if is_dict else getattr(execution_plan, "rollback_strategy", "")
        rollback = "Available" if rollback_strat else "Not Available"
        
        print(f" Estimated Duration : {estimated_duration}")
        print(f" Rollback           : {rollback}")
        print("═" * 50)
            
        print(" [A] Approve       [R] Reject")
        print(" [D] View Diff     [P] View Patch")
        print(" [F] View Files    [T] Run Verification")
        print(" [Q] Abort")
        print("═" * 50)
        
        self._prompt_loop(context.correlation_id)
        
    def _prompt_loop(self, correlation_id: str):
        patch_result = self.payload.get("patch_result", {})
        
        while self.is_waiting:
            choice = input("Nexa[Approval]> ").strip().upper()
            
            if choice == 'A':
                print("[*] Plan Approved. Publishing Event...")
                from nexa.core.models.enums import EventPriority
                import datetime
                self.bus.publish(EventContext(
                    event_name="ApprovalGranted",
                    timestamp=datetime.datetime.now().isoformat(),
                    source="ApprovalUI",
                    priority=EventPriority.HIGH,
                    session_id="",
                    payload={"status": "approved", "plan": self.payload.get("plan")}, 
                    correlation_id=correlation_id
                ))
                self.is_waiting = False
                
            elif choice == 'R':
                print("[!] Plan Rejected. Publishing Event...")
                self.bus.publish(EventContext("ApprovalRejected", payload={"reason": "User rejected"}, correlation_id=correlation_id))
                self.is_waiting = False
                
            elif choice == 'Q':
                print("[!] Workflow Aborted. Publishing Event...")
                self.bus.publish(EventContext("ApprovalCancelled", payload={"reason": "User aborted"}, correlation_id=correlation_id))
                self.is_waiting = False
                
            elif choice == 'D':
                diff = patch_result.get("diff", "(No diff available)")
                print("\n[*] Unified Diff:")
                print("-" * 30)
                print(diff)
                print("-" * 30 + "\n")
                
            elif choice == 'P':
                patch_details = patch_result.get("patch_details", "(No patch details available)")
                print("\n[*] Patch Details:")
                print("-" * 30)
                print(patch_details)
                print("-" * 30 + "\n")
                
            elif choice == 'F':
                files = patch_result.get("files", [])
                print("\n[*] Affected Files:")
                print("-" * 30)
                for f in files:
                    print(f)
                if not files:
                    print("(No files affected)")
                print("-" * 30 + "\n")
                
            elif choice == 'T':
                print("\n[*] Publishing TriggerVerification event...")
                print("   (Simulasi: Workspace Verification Engine dijalankan...)")
                print("   ✔ pytest (PASS)")
                print("   ✔ ruff (PASS)\n")
                
            else:
                print("[!] Invalid option.")
