import os
import subprocess

def handle(args):
    public_dir = os.path.join(os.getcwd(), 'public')
    if not os.path.exists(public_dir):
        print("Error: 'public' directory not found. Are you in a NexaPHP project root?")
        return

    host = '127.0.0.1'
    port = '8000'

    for arg in args:
        if arg.startswith('--host='):
            host = arg.split('=')[1]
        elif arg.startswith('--port='):
            port = arg.split('=')[1]

    print(f"Starting NexaPHP Backend Server on http://{host}:{port}")
    
    processes = []
    
    try:
        # Start PHP server
        php_proc = subprocess.Popen(['php', '-S', f'{host}:{port}', '-t', 'public/'])
        processes.append(php_proc)

        # Check for Vite/NPM
        if os.path.exists(os.path.join(os.getcwd(), 'package.json')):
            print("Starting Vite Frontend Server (npm run dev)...")
            npm_proc = subprocess.Popen(['npm', 'run', 'dev'], shell=(os.name == 'nt'))
            processes.append(npm_proc)

        print("Press Ctrl+C to stop all servers.")
        
        for p in processes:
            p.wait()

    except KeyboardInterrupt:
        print("\nStopping servers...")
        for p in processes:
            p.terminate()
        print("Servers stopped.")
