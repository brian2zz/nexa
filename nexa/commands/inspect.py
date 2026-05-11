from nexa.core.registry import generators, discover_core
from nexa.core.runtime.command import BaseCommand

class InspectCommand(BaseCommand):
    """
    Inspect the Nexa Execution Graph and Registry.
    """
    def run(self):
        # Trigger discovery to see everything
        discover_core()
        
        self.logger.step("Nexa Inspector: Execution Graph")
        
        all_entries = generators.list_all(sort_by_priority=True)
        
        print(f"{'PRIORITY':<10} | {'CATEGORY':<10} | {'KEY':<20} | {'TARGET':<10}")
        print("-" * 60)
        
        for entry in all_entries:
            print(f"{entry.priority:<10} | {entry.category:<10} | {entry.key:<20} | {entry.target:<10}")
            if entry.metadata and 'description' in entry.metadata:
                print(f"           > {entry.metadata['description']}")

        print("\n[*] Total registered generators:", len(all_entries))

def handle(args):
    cmd = InspectCommand(args)
    cmd.run()
