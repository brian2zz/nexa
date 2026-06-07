import os
import subprocess

def handle(args):
    print("Installing NexaPHP dependencies...")
    
    # Run composer install
    if os.path.exists(os.path.join(os.getcwd(), 'composer.json')):
        print("📦 [1/2] Running composer install...")
        try:
            subprocess.run(['composer', 'install'], check=True)
        except Exception as e:
            print(f"❌ Failed to run composer: {e}")
    else:
        print("⚠️ No composer.json found. Skipping PHP dependencies.")

    # Run npm install
    if os.path.exists(os.path.join(os.getcwd(), 'package.json')):
        print("📦 [2/2] Running npm install...")
        try:
            subprocess.run(['npm', 'install'], check=True, shell=(os.name == 'nt'))
        except Exception as e:
            print(f"❌ Failed to run npm: {e}")
    else:
        print("⚠️ No package.json found. Skipping JS dependencies.")

    print("✅ Installation complete!")
