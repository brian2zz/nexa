import subprocess
import os
from nexa.core.runtime.command import BaseCommand

class FlutterDoctorCommand(BaseCommand):
    """
    Diagnose the development environment for Nexa Flutter.
    """
    def run(self):
        self.logger.step("Nexa Flutter Doctor: Diagnosing Environment")
        
        checks = [
            ("Flutter SDK", self.check_flutter),
            ("Dart SDK", self.check_dart),
            ("Project Context (pubspec.yaml)", self.check_pubspec),
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
            self.logger.success("Flutter environment is healthy! You are ready to build dynamic modules.")
        else:
            self.logger.warning("Some checks failed. Please resolve the issues above before building modules.")

    def check_flutter(self):
        try:
            out = subprocess.check_output(["flutter", "--version"], stderr=subprocess.STDOUT).decode().strip()
            # Extract first line for clean version info
            first_line = out.split('\n')[0]
            return True, first_line
        except Exception:
            return False, "Flutter SDK is not found in PATH."

    def check_dart(self):
        try:
            out = subprocess.check_output(["dart", "--version"], stderr=subprocess.STDOUT).decode().strip()
            return True, out
        except Exception:
            return False, "Dart SDK is not found in PATH."

    def check_pubspec(self):
        if os.path.exists("pubspec.yaml"):
            # Try to read package name
            package_name = None
            with open("pubspec.yaml", "r") as f:
                for line in f:
                    if line.strip().startswith("name:"):
                        package_name = line.split(":")[1].strip()
                        break
            if package_name:
                return True, f"Found pubspec.yaml (Package name: '{package_name}')"
            return True, "Found pubspec.yaml (Name not specified)"
        return False, "pubspec.yaml not found in current directory. Run commands inside your Flutter project root."

def handle(args):
    cmd = FlutterDoctorCommand(args)
    cmd.run()
