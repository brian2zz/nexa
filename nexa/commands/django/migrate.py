import sys
import subprocess
import os

def handle(args):
    """
    Executes Django database migrations (makemigrations & migrate).
    """
    if not os.path.exists('manage.py'):
        print("[!] Error: 'manage.py' tidak ditemukan. Pastikan Anda berada di root project Django.")
        return

    print("[Nexa Django] Menjalankan migrasi database...")
    try:
        # 1. Jalankan makemigrations jika ada argumen atau untuk mendeteksi perubahan model
        print(" -> python manage.py makemigrations")
        subprocess.run([sys.executable, 'manage.py', 'makemigrations', *args], check=True)

        # 2. Jalankan migrate
        print(" -> python manage.py migrate")
        subprocess.run([sys.executable, 'manage.py', 'migrate', *args], check=True)

        print("✅ [Nexa Django] Migrasi database berhasil diterapkan.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Error saat migrasi: {e}")
    except FileNotFoundError:
        print("[!] Error: Python/Django command tidak ditemukan.")
