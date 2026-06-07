import os
import subprocess

def handle(args):
    bin_path = os.path.join(os.getcwd(), 'bin', 'nexa')
    if not os.path.exists(bin_path):
        print("Error: 'bin/nexa' not found. Are you in a NexaPHP project root?")
        return

    print("Running database migrations...")
    try:
        subprocess.run(['php', bin_path, 'migrate', '--no-interaction'], check=True)
        print("✅ Migrations applied successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error applying migration: {e}")
    except FileNotFoundError:
        print("Error: 'php' command not found. Please ensure PHP is installed and in your PATH.")
