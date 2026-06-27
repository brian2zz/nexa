import re
from typing import Tuple, List
from .base import Extractor

class PHPExtractor(Extractor):
    def extract(self, code: str, keywords: List[str]) -> Tuple[str, float, str, int]:
        total_lines = len(code.split('\n'))
        if total_lines < 200:
            return code, 1.0, "full_file", 4
            
        # Level 1: Regex Extraction (Targeting classes/functions with keywords)
        for k in keywords:
            # Try to find class
            class_pattern = rf'(?:abstract\s+)?class\s+{k}.*?\{{.*?^\}}'
            match = re.search(class_pattern, code, re.MULTILINE | re.DOTALL)
            if match:
                return match.group(0), 0.95, "regex", 1
                
            # Try to find function
            func_pattern = rf'(?:public\s+|protected\s+|private\s+)?function\s+{k}.*?\{{.*?^\s*\}}'
            match = re.search(func_pattern, code, re.MULTILINE | re.DOTALL)
            if match:
                return match.group(0), 0.95, "regex", 1
                
        # Level 2: Class/Function Detector (Simple parser)
        # (For V1, if regex fails, we skip straight to Keyword Window)
        
        # Level 3: Keyword Window
        snippet, conf = self.get_keyword_window(code, keywords, 100)
        if snippet:
            return snippet, conf, "keyword_window", 3
            
        # Level 4: Full File (only if < 800 lines)
        if total_lines <= 800:
            return code, 0.1, "full_file", 4
            
        return "", 0.0, "none", 0
