import os
import sys
import subprocess
import threading
import time
from nexa.core.runtime.command import BaseCommand

try:
    import msvcrt
except ImportError:
    msvcrt = None

class FlutterRunCommand(BaseCommand):
    """
    Interactive Flutter runner with keypress interceptors:
    - 'c': flutter clean + flutter pub get, then hot restart/re-run
    - 's': Hot Restart (resets Riverpod app state)
    - 'p': Toggle Performance Overlay
    - 'e': Reload .env configurations & Hot Restart
    - Outputs HTTP logs dynamically in console from HttpService (GET /api/user 200 120ms)
    """
    def __init__(self, args):
        super().__init__(args)
        self.process = None

    def run(self):
        # Verify we are in a Flutter project
        if not os.path.exists("pubspec.yaml"):
            self.logger.error("pubspec.yaml not found in current directory. Run this inside a Flutter project root.")
            return

        self.logger.step("Starting Nexa Flutter Interactive Runner...")
        print("\033[95m\033[1mNexa Flutter Keyboard Shortcuts:\033[0m")
        print("  \033[92m[c]\033[0m Clean project + Pub Get + Restart")
        print("  \033[92m[s]\033[0m Reset App State (Riverpod Hot Restart)")
        print("  \033[92m[p]\033[0m Toggle Performance Overlay")
        print("  \033[92m[e]\033[0m Reload .env & Hot Restart")
        print("  \033[92m[r]\033[0m Hot Reload (native)")
        print("  \033[92m[R]\033[0m Hot Restart (native)")
        print("  \033[92m[q]\033[0m Quit Runner")
        print("  Network calls will be printed dynamically below.\n")

        self.start_flutter_process()

    def start_flutter_process(self):
        # Build command: 'flutter run' with any additional args supplied by user
        cmd_args = ['flutter', 'run'] + self.args
        
        # Use shell=True for windows path compatibility
        self.process = subprocess.Popen(
            cmd_args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )

        # Start stdout reading thread
        stdout_thread = threading.Thread(target=self.read_stdout)
        stdout_thread.daemon = True
        stdout_thread.start()

        # Start stderr reading thread
        stderr_thread = threading.Thread(target=self.read_stderr)
        stderr_thread.daemon = True
        stderr_thread.start()

        # Start keyboard listening thread
        if msvcrt:
            kbd_thread = threading.Thread(target=self.listen_keyboard)
            kbd_thread.daemon = True
            kbd_thread.start()
        else:
            self.logger.warning("Keyboard shortcuts are only supported on Windows terminals.")

        # Wait for the process to complete or terminate
        self.process.wait()

    def read_stdout(self):
        while True:
            line = self.process.stdout.readline()
            if not line:
                break
            
            try:
                line_str = line.decode('utf-8', errors='ignore')
            except Exception:
                continue
            
            # Check for network monitor interceptor prefix
            if '[NEXA_NET]' in line_str:
                parts = line_str.split('[NEXA_NET]')
                net_part = parts[1].strip()
                
                # e.g. GET /api/user 200 120ms
                net_details = net_part.split(' ')
                if len(net_details) >= 3:
                    method = net_details[0]
                    path = net_details[1]
                    status = net_details[2]
                    duration = net_details[3] if len(net_details) > 3 else ""
                    
                    # Colors
                    color = "\033[92m" # Green
                    try:
                        status_val = int(status)
                        if 300 <= status_val < 400:
                            color = "\033[93m" # Yellow
                        elif status_val >= 400:
                            color = "\033[91m" # Red
                    except ValueError:
                        if status != "200" and status != "201":
                            color = "\033[91m" # Red
                    
                    method_color = "\033[96m" # Cyan
                    if method in ["POST", "PUT"]:
                        method_color = "\033[94m" # Blue
                    elif method == "DELETE":
                        method_color = "\033[91m" # Red
                    
                    reset = "\033[0m"
                    bold = "\033[1m"
                    
                    # Print beautiful network log
                    sys.stdout.write(f"\n\033[95m[NET]\033[0m {bold}{method_color}{method}{reset} {path} -> {color}{status}{reset} \033[90m({duration})\033[0m\n")
                    sys.stdout.flush()
                else:
                    sys.stdout.write(f"\n\033[95m[NET]\033[0m {net_part}\n")
                    sys.stdout.flush()
            else:
                sys.stdout.write(line_str)
                sys.stdout.flush()

    def read_stderr(self):
        while True:
            line = self.process.stderr.readline()
            if not line:
                break
            try:
                line_str = line.decode('utf-8', errors='ignore')
                sys.stderr.write(line_str)
                sys.stderr.flush()
            except Exception:
                continue

    def listen_keyboard(self):
        while self.process.poll() is None:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                try:
                    char = key.decode('utf-8').lower()
                except Exception:
                    continue

                if char == 'q':
                    print("\n[*] Exiting Nexa Flutter Runner...")
                    self.process.terminate()
                    break
                elif char == 'c':
                    print("\n[*] Intercepted 'c': Running clean + pub get...")
                    self.process.terminate()
                    self.process.wait()
                    
                    # 1. Clean
                    print("[*] Running 'flutter clean'...")
                    subprocess.run(['flutter', 'clean'], shell=True)
                    
                    # 2. Pub Get
                    print("[*] Running 'flutter pub get'...")
                    subprocess.run(['flutter', 'pub', 'get'], shell=True)
                    
                    # 3. Restart
                    print("[*] Restarting application...")
                    # We start a new thread to restart so we don't block the keypress loop
                    threading.Thread(target=self.start_flutter_process).start()
                    break # Exit current listener thread
                elif char == 's':
                    print("\n[*] Intercepted 's': Resetting App State (Riverpod Hot Restart)...")
                    try:
                        self.process.stdin.write(b'R\n')
                        self.process.stdin.flush()
                    except Exception as e:
                        print(f"Error resetting state: {e}")
                elif char == 'p':
                    print("\n[*] Intercepted 'p': Toggling Performance Overlay...")
                    try:
                        self.process.stdin.write(b'P\n')
                        self.process.stdin.flush()
                    except Exception as e:
                        print(f"Error toggling performance: {e}")
                elif char == 'e':
                    print("\n[*] Intercepted 'e': Reloading .env configurations and Hot Restarting...")
                    try:
                        self.process.stdin.write(b'R\n')
                        self.process.stdin.flush()
                    except Exception as e:
                        print(f"Error sending Hot Restart: {e}")
                else:
                    # Pass default keypress directly to flutter process
                    try:
                        self.process.stdin.write(key + b'\n')
                        self.process.stdin.flush()
                    except Exception:
                        pass
            time.sleep(0.05)

def handle(args):
    cmd = FlutterRunCommand(args)
    cmd.run()
