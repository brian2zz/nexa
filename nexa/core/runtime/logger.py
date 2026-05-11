import sys

class NexaLogger:
    """
    Standardized logging for Nexa Framework.
    Supports different levels and can be expanded for colors or JSON.
    """
    def __init__(self, verbose=True):
        self.verbose = verbose

    def info(self, message):
        if self.verbose:
            print(f"[*] {message}")

    def success(self, message):
        print(f"\n[SUCCESS] {message}")

    def error(self, message):
        print(f"[ERROR] {message}", file=sys.stderr)

    def warning(self, message):
        print(f"[WARNING] {message}")

    def step(self, name):
        if self.verbose:
            print(f"\n--- {name} ---")

    def log_task(self, message):
        if self.verbose:
            print(f"    > {message}")

# Global instance
logger = NexaLogger()
