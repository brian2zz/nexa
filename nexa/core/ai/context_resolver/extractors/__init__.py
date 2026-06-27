from .base import Extractor
from .php import PHPExtractor
from .python import PythonExtractor
from .generic import GenericExtractor

def get_extractor(extension: str) -> Extractor:
    ext = extension.lower()
    if ext == '.php':
        return PHPExtractor()
    elif ext == '.py':
        return PythonExtractor()
    return GenericExtractor()
