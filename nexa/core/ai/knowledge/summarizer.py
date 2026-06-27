import re
import hashlib
from typing import Dict, Any
from .models import FileSummary
from .cache.base import BaseCache
from .cache.memory import MemoryCache

class RegexSummarizer:
    """
    Regex-based summarizer extracting functions, classes, imports, etc.
    """
    def __init__(self, cache: BaseCache = None):
        self.cache = cache or MemoryCache()
        self.patterns = {
            "python": {
                "functions": r"^\s*def\s+([a-zA-Z0-9_]+)\s*\(",
                "classes": r"^\s*class\s+([a-zA-Z0-9_]+)\s*[:\(]",
                "imports": r"^\s*(?:import|from)\s+([a-zA-Z0-9_\.]+)"
            },
            "php": {
                "functions": r"^\s*(?:public|protected|private|static)?\s*function\s+([a-zA-Z0-9_]+)\s*\(",
                "classes": r"^\s*(?:abstract\s+)?class\s+([a-zA-Z0-9_]+)",
                "imports": r"^\s*use\s+([a-zA-Z0-9_\\]+)"
            },
            "javascript": {
                "functions": r"(?:function\s+([a-zA-Z0-9_]+)\s*\()|(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*(?:function|\([^)]*\)\s*=>)",
                "classes": r"^\s*class\s+([a-zA-Z0-9_]+)",
                "imports": r"import\s+.*from\s+['\"]([^'\"]+)['\"]",
                "exports": r"export\s+(?:default\s+)?(?:class|function|const|let|var)\s+([a-zA-Z0-9_]+)"
            },
            "flutter": {
                "widgets": r"class\s+([a-zA-Z0-9_]+)\s+extends\s+(?:StatefulWidget|StatelessWidget)",
                "functions": r"^\s*(?:[a-zA-Z0-9_<>]+)\s+([a-zA-Z0-9_]+)\s*\(",
                "classes": r"^\s*class\s+([a-zA-Z0-9_]+)",
                "imports": r"import\s+['\"]([^'\"]+)['\"]"
            }
        }

    def summarize(self, content: str, language: str, path: str) -> FileSummary:
        lang = language.lower()
        if lang not in self.patterns:
            return FileSummary(purpose="Unknown language", language=lang)
            
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        cache_key = f"summary_{path}_{content_hash}"
        
        cached = self.cache.get(cache_key)
        if cached is not None:
            # We assume cached is a dict representation for easy SQLite serialization, need to convert back to FileSummary
            if isinstance(cached, dict):
                return FileSummary(**cached)
            return cached

        summary = FileSummary(language=lang)
        
        # Extract based on available patterns for the language
        lang_patterns = self.patterns[lang]
        
        if "functions" in lang_patterns:
            for match in re.finditer(lang_patterns["functions"], content, re.MULTILINE):
                name = match.group(1) if match.group(1) else (match.group(2) if len(match.groups()) > 1 else None)
                if name: summary.functions.append(name)
                
        if "classes" in lang_patterns:
            for match in re.finditer(lang_patterns["classes"], content, re.MULTILINE):
                summary.classes.append(match.group(1))
                
        if "imports" in lang_patterns:
            for match in re.finditer(lang_patterns["imports"], content, re.MULTILINE):
                summary.imports.append(match.group(1))

        if "exports" in lang_patterns:
            for match in re.finditer(lang_patterns["exports"], content, re.MULTILINE):
                summary.exports.append(match.group(1))
                
        if "widgets" in lang_patterns:
            for match in re.finditer(lang_patterns["widgets"], content, re.MULTILINE):
                summary.widgets.append(match.group(1))

        # We store as dict in cache to make SQLite serialization easy
        self.cache.set(cache_key, summary.__dict__)
        return summary
