import re
from typing import Tuple, List
from .base import Extractor

class PythonExtractor(Extractor):
    def extract(self, code: str, keywords: List[str]) -> Tuple[str, float, str, int]:
        total_lines = len(code.split('\n'))
        if total_lines < 200:
            return code, 1.0, "full_file", 4
            
        for k in keywords:
            # Try to find class
            class_pattern = rf'^class\s+{k}.*?(?:^\S|\Z)'
            match = re.search(class_pattern, code, re.MULTILINE | re.DOTALL)
            if match:
                # Python block parsing is tricky with regex due to indentation.
                # A simple heuristic: take everything until the next non-indented line.
                return match.group(0).strip(), 0.95, "regex", 1
                
            # Try to find def
            func_pattern = rf'^\s*def\s+{k}\s*\(.*?(?:^\S|\Z)'
            match = re.search(func_pattern, code, re.MULTILINE | re.DOTALL)
            if match:
                return match.group(0).strip(), 0.95, "regex", 1
                
        snippet, conf = self.get_keyword_window(code, keywords, 100)
        if snippet:
            return snippet, conf, "keyword_window", 3
            
        if total_lines <= 800:
            return code, 0.1, "full_file", 4
            
        return "", 0.0, "none", 0
