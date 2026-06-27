from typing import List
from .models import ScannerResult, KnowledgeFile, IntentContext
from .matcher import IntentMatcher

class CandidateSelector:
    """
    Selects initial candidate files based on intent and keywords.
    """
    def __init__(self):
        self.matcher = IntentMatcher()

    def select(self, scanner_result: ScannerResult, intent: IntentContext) -> List[KnowledgeFile]:
        keywords = self.matcher.match(intent)
        candidates = []
        
        for file_info in scanner_result.files:
            path = file_info.get("path", "")
            content = file_info.get("content", "")
            
            is_match = False
            path_lower = path.lower()
            reasons = []
            
            if not keywords:
                is_match = True
                reasons.append("Fallback selection")
            else:
                for kw in keywords:
                    if kw in path_lower:
                        is_match = True
                        reasons.append(f"Goal keyword matched '{kw}' in path")
                    elif kw in content.lower():
                        is_match = True
                        reasons.append(f"Goal keyword matched '{kw}' in content")
                        
            if is_match:
                # Remove duplicate reasons
                reasons = list(set(reasons))
                candidates.append(KnowledgeFile(
                    path=path,
                    content=content,
                    selection_reason=reasons
                ))
                
        return candidates
