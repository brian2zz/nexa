import os
import subprocess
import json
from nexa.core.ai.scanner.detector import ProjectDetector

class WorkspaceManager:
    """
    Bertanggung jawab mengumpulkan intelijen proyek (Framework, Git, Patch terakhir)
    untuk disuntikkan ke dalam System Prompt LLM.
    """
    def __init__(self, cwd: str):
        self.cwd = cwd
        self.detector = ProjectDetector()
        
    def _get_git_branch(self) -> str:
        """Mengambil nama branch git saat ini menggunakan GitTool."""
        from nexa.core.agent.tools.knowledge.git import GitTool
        return GitTool(self.cwd).current_branch()
            
    def _get_last_backup_manifest(self) -> str:
        """Mengintip manifest backup terakhir dari Phase 3."""
        backup_dir = os.path.join(self.cwd, ".nexa", "backups")
        if not os.path.exists(backup_dir):
            return "No previous patches found."
            
        try:
            # Cari folder backup terbaru
            dirs = sorted([d for d in os.listdir(backup_dir) if os.path.isdir(os.path.join(backup_dir, d))])
            if not dirs:
                return "No previous patches found."
                
            latest = dirs[-1]
            manifest_path = os.path.join(backup_dir, latest, "manifest.json")
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                    return f"Last patch applied at {manifest.get('timestamp')}. Backup ID: {latest}"
        except Exception as e:
            return f"Error reading backups: {e}"
            
        return "No previous patches found."
        
    def generate_system_prompt(self) -> str:
        """
        Merakit System Prompt utuh yang kaya akan konteks untuk diserahkan ke LLM.
        """
        # 1. Deteksi Framework (menggunakan infrastruktur lama)
        proj_info = self.detector.detect(self.cwd)
        framework = proj_info.get("framework", "Unknown")
        language = proj_info.get("language", "Unknown")
        
        # 2. Intelijen Lingkungan
        git_branch = self._get_git_branch()
        last_patch = self._get_last_backup_manifest()
        
        # 3. Rakit Prompt
        prompt = (
            f"You are Nexa AI, a highly advanced Software Engineering Agent.\n"
            f"[WORKSPACE CONTEXT]\n"
            f"- Project Path : {self.cwd}\n"
            f"- Framework    : {framework} ({language})\n"
            f"- Git Branch   : {git_branch}\n"
            f"- Last Patch   : {last_patch}\n\n"
            f"[CRITICAL RULES]\n"
            f"1. You must follow the 'Pipeline Sovereignty Principle'.\n"
            f"2. You cannot write files directly. You must use 'submit_execution_plan'.\n"
        )
        return prompt
