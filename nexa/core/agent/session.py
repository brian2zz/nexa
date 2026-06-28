from typing import Optional
from nexa.core.ai.memory.core import ChatMemoryManager

class SessionRecoveryManager:
    """
    Bertugas memulihkan (resume) sesi obrolan lama jika pengguna
    menyalakan kembali NexaAgent setelah ditutup.
    """
    def __init__(self, memory_manager: ChatMemoryManager):
        self.memory = memory_manager
        
    def prompt_recovery(self, cwd: str) -> Optional[int]:
        """
        Memeriksa apakah ada sesi sebelumnya di proyek ini.
        Jika ada, tanya pengguna apakah ingin melanjutkannya.
        Mengembalikan session_id lama, atau None jika memulai baru.
        """
        # Ambil maksimal 5 sesi terakhir untuk proyek ini
        sessions = self.memory.get_project_sessions(cwd, limit=5)
        
        # Filter sesi yang benar-benar memiliki pesan
        valid_sessions = [s for s in sessions if s[2] > 0]
        
        if not valid_sessions:
            return None
            
        last_session = valid_sessions[0]
        session_id = last_session[0]
        created_at = last_session[1]
        msg_count = last_session[2]
        
        print(f"\n[*] Welcome back!")
        print(f"    Last active session found: {created_at} ({msg_count} messages)")
        
        # Tampilkan pesan terakhir (potongan)
        recent = self.memory.load_session_messages(session_id, limit=1)
        if recent:
            last_msg = recent[0]['content']
            snippet = last_msg[:50] + "..." if len(last_msg) > 50 else last_msg
            print(f"    Last context: \"{snippet}\"")
            
        while True:
            choice = input(f"\nDo you want to continue this session? [Y/n]: ").strip().lower()
            if choice in ['', 'y', 'yes']:
                print(f"[*] Resuming Session ID: {session_id}\n")
                return session_id
            elif choice in ['n', 'no']:
                print(f"[*] Starting a brand new session.\n")
                return None
            else:
                print("[!] Invalid option. Type Y or N.")
