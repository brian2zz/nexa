import os
import time
import signal
import subprocess


# pyrefly: ignore [missing-import]

processes = []


def start_process(command, cwd=None):

    process = subprocess.Popen(
        command,
        cwd=cwd,
        shell=True
    )

    processes.append(process)

    return process


def stop_processes():

    print('\nStopping Nexa environment...')

    for process in processes:

        try:
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
    print(f'Starting Django server at {host}...')
    start_process(
        f'python manage.py runserver {host}'
    )

    # Start Unified Vite Server
    package_json = os.path.join(os.getcwd(), 'package.json')
    if os.path.exists(package_json):
        print('Starting Unified Vite server...')
        
        # Pass backend URL to Vite for proxying
        env = os.environ.copy()
        env['NEXA_BACKEND_URL'] = f'http://{host}'
        
        subprocess.Popen(
            'npm run dev',
            cwd=os.getcwd(),
            shell=True,
            env=env
        )

    print('\nNexa environment running')
    print('Press CTRL+C to stop\n')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_processes()