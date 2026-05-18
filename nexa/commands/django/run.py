import os
import time
import subprocess

# Global list to track processes
processes = []

def start_process(command, cwd=None, env=None):
    """
    Starts a process and tracks it in the global list.
    On Windows, uses CREATE_NEW_PROCESS_GROUP for cleaner termination.
    """
    process = subprocess.Popen(
        command,
        cwd=cwd,
        shell=True,
        env=env,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    )
    processes.append(process)
    return process

def stop_processes():
    """
    Gracefully (or forcefully on Windows) stops all tracked processes.
    """
    print('\nStopping Nexa environment...')
    for process in processes:
        try:
            if os.name == 'nt':
                # Force kill process tree on Windows to ensure no zombie nodes/npm
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)], 
                             capture_output=True, check=False)
            else:
                process.terminate()
        except Exception:
            pass
    print('All processes stopped')

def handle(args):
    host = '127.0.0.1:8000'
    for arg in args:
        if arg.startswith('--host='):
            host = arg.split('=')[1]

    print(f'Starting Nexa development environment at {host}...\n')

    # Start Django
    print(f'[*] Starting Django server at {host}...')
    start_process(
        f'python manage.py runserver {host}'
    )

    # Start Unified Vite Server
    package_json = os.path.join(os.getcwd(), 'package.json')
    if os.path.exists(package_json):
        print('[*] Starting Unified Vite server...')
        
        # Pass backend URL to Vite for proxying
        env = os.environ.copy()
        env['NEXA_BACKEND_URL'] = f'http://{host}'
        
        # Track Vite process
        start_process(
            'npm run dev',
            cwd=os.getcwd(),
            env=env
        )

    print('\n[READY] Nexa environment running')
    print('Press CTRL+C to stop\n')

    try:
        while True:
            # Health check for all processes
            for p in processes:
                if p.poll() is not None:
                    print(f"\n[ERROR] A service (PID: {p.pid}) has stopped unexpectedly.")
                    stop_processes()
                    return
            time.sleep(1)
    except KeyboardInterrupt:
        stop_processes()
    except Exception as e:
        print(f"Error during execution: {e}")
        stop_processes()