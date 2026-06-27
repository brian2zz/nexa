import os
import json

def handle(args):
    from nexa.core.ai.scanner.detector import ProjectDetector
    from nexa.core.ai.scanner.scanner import FileScanner
    from nexa.core.ai.memory import Memory
    
    root_path = os.path.abspath(os.getcwd())
    
    # 1. Deteksi
    print(f"[*] Mendeteksi project di {root_path} ...")
    detector = ProjectDetector()
    project_info = detector.detect(root_path)
    print(f"[+] Terdeteksi Framework: {project_info['framework']} (Bahasa: {project_info['language']})")
    
    # 2. Pemindaian
    print("[*] Memindai file project...")
    scanner = FileScanner()
    files = scanner.scan(root_path)
    print(f"[+] Ditemukan {len(files)} file yang valid.")
    
    # 3. Penyimpanan
    print("[*] Menyimpan ke memori SQLite...")
    memory = Memory()
    project_id = memory.save_project(root_path, project_info['framework'], project_info['language'])
    memory.save_files(project_id, files)
    
    # Phase 2.11: Update Project Facts Automatically
    from nexa.core.ai.memory.project_facts import ProjectFactsManager
    facts_mgr = ProjectFactsManager()
    new_facts = {
        "framework": project_info['framework'],
        "language": project_info['language'],
        "project_name": os.path.basename(root_path),
        "total_files_scanned": str(len(files))
    }
    facts_mgr.update_from_scan(root_path, new_facts)
    
    print("[+] Pemindaian Selesai!")
