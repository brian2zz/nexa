import sys
import time
import threading
from typing import Optional

class Spinner:
    """
    A simple terminal spinner context manager for long-running operations.
    """
    def __init__(self, message: str = "Processing...", delay: float = 0.1):
        self.spinner_chars = ['|', '/', '-', '\\']
        self.delay = delay
        self.message = message
        self.running = False
        self.spinner_thread: Optional[threading.Thread] = None

    def spin(self):
        idx = 0
        while self.running:
            sys.stdout.write(f'\r[ {self.spinner_chars[idx]} ] {self.message}')
            sys.stdout.flush()
            idx = (idx + 1) % len(self.spinner_chars)
            time.sleep(self.delay)

    def __enter__(self):
        self.running = True
        self.spinner_thread = threading.Thread(target=self.spin)
        self.spinner_thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        if self.spinner_thread:
            self.spinner_thread.join()
        # Clear the spinner line
        sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
        sys.stdout.flush()
