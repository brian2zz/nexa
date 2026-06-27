import os
import json
import datetime
from .schema import AnalysisSession

class HistoryManager:
    """
    Saves AnalysisSession to .nexa/analysis/ for future comparison.
    """
    def __init__(self, project_root: str):
        self.history_dir = os.path.join(project_root, ".nexa", "analysis")
        os.makedirs(self.history_dir, exist_ok=True)
        
    def save(self, session: AnalysisSession) -> str:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f"{timestamp}.json"
        filepath = os.path.join(self.history_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(session.to_dict(), f, indent=2)
            
        return filepath
