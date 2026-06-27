import re
import hashlib
from typing import List, Tuple
from .cache.base import BaseCache
from .cache.memory import MemoryCache

class DependencyParser:
    """
    Regex-based dependency parser for V1.
    """
    def __init__(self, cache: BaseCache = None):
        self.cache = cache or MemoryCache()
        self.patterns = {
            "python": [
                (r"^\s*import\s+([a-zA-Z0-9_\.]+)", "IMPORTS"),
                (r"^\s*from\s+([a-zA-Z0-9_\.]+)\s+import", "IMPORTS")
            ],
            "php": [
                (r"^\s*use\s+([a-zA-Z0-9_\\]+)", "USES"),
                (r"class\s+[a-zA-Z0-9_]+\s+extends\s+([a-zA-Z0-9_]+)", "EXTENDS"),
                (r"class\s+[a-zA-Z0-9_]+\s+implements\s+([a-zA-Z0-9_,\s]+)", "IMPLEMENTS"),
                (r"require(_once)?\s*\(?['\"]([^'\"]+)['\"]", "REQUIRES"),
                (r"include(_once)?\s*\(?['\"]([^'\"]+)['\"]", "REQUIRES")
            ],
            "javascript": [
                (r"import\s+.*from\s+['\"]([^'\"]+)['\"]", "IMPORTS"),
                (r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)", "REQUIRES")
            ]
        }

    def parse(self, content: str, language: str, path: str) -> List[Tuple[str, str]]:
        lang = language.lower()
        if lang not in self.patterns:
            return []
            
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        cache_key = f"deps_{path}_{content_hash}"
        
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        results = []
        for pattern, rel_type in self.patterns[lang]:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                target = match.group(1).strip()
                if rel_type == "IMPLEMENTS" and "," in target:
                    for t in target.split(","):
                        results.append((t.strip(), rel_type))
                else:
                    results.append((target, rel_type))
                    
        self.cache.set(cache_key, results)
        return results
