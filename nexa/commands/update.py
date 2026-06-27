import os
import sys
import subprocess

def run_update(repo_url: str = None):
    """
    Updates the Nexa Framework globally via pip.
    """
    if not repo_url:
        # Fallback to the user's github repo when public. 
        # Since we don't know the exact username right now, we can use a placeholder,
        # but in production, this should be the exact github URL.
        repo_url = "git+https://github.com/brian2zz/nexa.git"
        
    print(f"\033[94m[*] Menjemput pembaruan Nexa terbaru dari {repo_url}...\033[0m")
    
    try:
        # Run pip install --upgrade
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", repo_url],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(result.stdout)
            print("\033[92m[+] Nexa berhasil diperbarui ke versi terbaru!\033[0m")
            print("\033[92m[+] Semua perintah 'nexa' dan 'nexa ai' sekarang menggunakan versi terbaru.\033[0m")
        else:
            print("\033[91m[!] Gagal memperbarui Nexa.\033[0m")
            print(result.stderr)
            
    except Exception as e:
        print(f"\033[91m[!] Terjadi kesalahan sistem: {str(e)}\033[0m")
