from abc import ABC, abstractmethod
from typing import Tuple, List

class Extractor(ABC):
    @abstractmethod
    def extract(self, code: str, keywords: List[str]) -> Tuple[str, float, str, int]:
        """
        Returns: (snippet, confidence, selection_method, fallback_level)
        Selection Methods: 'regex', 'class_detector', 'keyword_window', 'full_file'
        """
        pass

    def get_keyword_window(self, code: str, keywords: List[str], window_lines: int = 100) -> Tuple[str, float]:
        """
        Fallback Level 3: Returns +/- window_lines around the first found keyword.
        """
        lines = code.split('\n')
        for k in keywords:
            for i, line in enumerate(lines):
                if k.lower() in line.lower():
                    start = max(0, i - window_lines)
                    end = min(len(lines), i + window_lines)
                    snippet = "\n".join(lines[start:end])
                    return snippet, 0.55
        return "", 0.0
