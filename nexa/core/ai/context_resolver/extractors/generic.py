from typing import Tuple, List
from .base import Extractor

class GenericExtractor(Extractor):
    """
    Fallback extractor for unknown languages.
    """
    def extract(self, code: str, keywords: List[str]) -> Tuple[str, float, str, int]:
        total_lines = len(code.split('\n'))
        if total_lines < 200:
            return code, 1.0, "full_file", 4
            
        snippet, conf = self.get_keyword_window(code, keywords, 100)
        if snippet:
            return snippet, conf, "keyword_window", 3
            
        if total_lines <= 800:
            return code, 0.1, "full_file", 4
            
        return "", 0.0, "none", 0
