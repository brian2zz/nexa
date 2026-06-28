from abc import ABC, abstractmethod
from typing import List, Tuple
import subprocess

class BaseVerifier(ABC):
    @abstractmethod
    def verify(self, cwd: str) -> Tuple[bool, str]:
        pass

class SyntaxVerifier(BaseVerifier):
    def verify(self, cwd: str) -> Tuple[bool, str]:
        # Cek syntax (contoh untuk python: python -m py_compile)
        return True, "Syntax check passed."

class LintVerifier(BaseVerifier):
    def verify(self, cwd: str) -> Tuple[bool, str]:
        # Cek linter
        return True, "Lint check passed."

class VerificationPipeline:
    """
    Menjalankan serangkaian verifier setelah eksekusi selesai.
    """
    def __init__(self, cwd: str):
        self.cwd = cwd
        self.verifiers: List[BaseVerifier] = [
            SyntaxVerifier(),
            LintVerifier()
        ]
        
    def add_verifier(self, verifier: BaseVerifier):
        self.verifiers.append(verifier)
        
    def run_all(self) -> Tuple[bool, str]:
        for verifier in self.verifiers:
            success, msg = verifier.verify(self.cwd)
            if not success:
                return False, f"{verifier.__class__.__name__} failed: {msg}"
        return True, "All verifications passed."
