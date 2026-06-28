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
        payload = context.payload or {}
        self.current_plan = payload.get("plan", {})
        
        # Mengekstrak informasi Patch/Plan (Simulasi)
        files = payload.get("files", [])
        risk = payload.get("risk", "UNKNOWN")
        additions = payload.get("additions", 0)
        deletions = payload.get("deletions", 0)
        
        print("\n" + "═" * 40)
        print(" PATCH SUMMARY (INTERACTIVE WORKFLOW)")
        print("═" * 40)
        print(f" Files Impacted : {len(files)}")
        print(f" Lines Changed  : +{additions} / -{deletions}")
        
        # Pewarnaan Risk Level
        risk_color = '\033[91m' if risk.upper() == 'HIGH' else '\033[93m' if risk.upper() == 'MEDIUM' else '\033[92m'
        reset = '\033[0m'
        print(f" Risk Level     : {risk_color}{risk}{reset}")
        print("─" * 40)
        print(" [A] Approve       [D] View Diff")
        print(" [R] Reject        [T] Run Tests")
        print(" [Q] Abort")
        print("═" * 40)
        
        self._prompt_loop(context.correlation_id)
        
    def _prompt_loop(self, correlation_id: str):
        while self.is_waiting:
            choice = input("Nexa[Approval]> ").strip().upper()
            
            if choice == 'A':
                print("[*] Patch Approved. Executing...")
                
                from nexa.core.models.enums import EventPriority
                import datetime
                
                self.bus.publish(EventContext(
                    event_name="ApprovalGranted",
                    timestamp=datetime.datetime.now().isoformat(),
                    source="ApprovalUI",
                    priority=EventPriority.HIGH,
                    session_id="", # Interactive tak punya session statis langsung
                    payload={"status": "approved", "plan": self.current_plan}, 
                    correlation_id=correlation_id
                ))
                self.is_waiting = False
            elif choice in ['R', 'Q']:
                print("[!] Patch Rejected/Aborted.")
                self.bus.publish(EventContext("ApprovalRejected", payload={"reason": "User aborted"}, correlation_id=correlation_id))
                self.is_waiting = False
            elif choice == 'D':
                print("[*] Showing Diff (Simulasi):")
                print("   + def new_feature(): pass")
                print("   - old_feature()")
            elif choice == 'T':
                print("[*] Running Verification Engine tests... (Simulasi: PASS)")
            else:
                print("[!] Invalid option.")
