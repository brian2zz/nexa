import sys
import os
import subprocess
from nexa.core.runtime.command import BaseCommand

class DoctorCommand(BaseCommand):
    """
    Diagnose the development environment for Nexa.
    """
    def run(self):
        self.logger.step("Nexa Doctor: Diagnosing Environment")
        
        checks = [
            ("Python", self.check_python),
            ("Node.js", self.check_node),
            ("Django", self.check_django),
            ("Vite", self.check_vite),
            ("Schema (nexa.yaml)", self.check_schema),
        ]

        all_ok = True
        for name, func in checks:
            ok, msg = func()
            if ok:
                print(f"  [PASS] {name}: {msg}")
            else:
                print(f"  [FAIL] {name}: {msg}")
                all_ok = False

        if all_ok:
            self.logger.success("Environment is healthy! You are ready to build.")
        else:
            self.logger.warning("Some checks failed. Please fix the issues above before proceeding.")

    def check_python(self):
        v = sys.version_info
        return True, f"{v.major}.{v.minor}.{v.micro}"

    def check_node(self):
        try:
            out = subprocess.check_output(["node", "--version"], stderr=subprocess.STDOUT).decode().strip()
            return True, out
        except:
            return False, "Node.js not found in PATH."

    def check_django(self):
        try:
            import django
            return True, django.get_version()
        except ImportError:
            return False, "Django is not installed in the current environment."

    def check_vite(self):
        # Check in local node_modules or global
        try:
            # Try running npx vite --version
            out = subprocess.check_output(["npx", "vite", "--version"], stderr=subprocess.STDOUT).decode().strip()
            return True, out
        except:
            return False, "Vite/NPX not found."

    def check_schema(self):
        if os.path.exists("nexa.yaml"):
            return True, "Found nexa.yaml"
        return False, "nexa.yaml not found in current directory."

def handle(args):
    cmd = DoctorCommand(args)
    cmd.run()
