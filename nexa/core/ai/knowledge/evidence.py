"""
EvidenceBundle — Output terstruktur dari Knowledge Orchestrator.

EvidenceBundle adalah "hasil riset" yang bersih dan sudah tervalidasi.
Ia dikonsumsi oleh Reasoning, Planning, dan Transformation — 
tidak satupun dari mereka perlu memanggil tool sendiri.

Filosofi: "Planner hanya membaca. Planner tidak mencari."
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from nexa.core.ai.knowledge.need import Need


@dataclass
class FileEvidence:
    """Bukti dari sebuah file yang berhasil dibaca."""
    path: str
    content: str              # Isi file (mungkin dipotong jika terlalu panjang)
    size_bytes: int = 0
    truncated: bool = False


@dataclass
class SymbolEvidence:
    """Bukti dari sebuah simbol kode (class/function/method)."""
    name: str
    type: str                 # "class", "function", "method"
    file: str
    start_line: int
    end_line: int
    code: str                 # Potongan kode yang relevan


@dataclass
class SearchEvidence:
    """Hasil pencarian teks di seluruh codebase."""
    query: str
    matches: List[Dict[str, Any]] = field(default_factory=list)  # {file, line, content}
    total_matches: int = 0


@dataclass
class GitEvidence:
    """Bukti dari repository Git."""
    status: Optional[str] = None          # git status output
    diff_summary: Optional[str] = None    # git diff --stat
    diff_full: Optional[str] = None       # git diff (content)
    current_branch: Optional[str] = None
    recent_commits: Optional[str] = None  # git log --oneline -10


@dataclass
class EvidenceBundle:
    """
    Paket bukti terstruktur yang dihasilkan oleh KnowledgeOrchestrator.
    
    Ini adalah satu-satunya antarmuka antara Knowledge Layer dan 
    Reasoning/Planning Layer. Mereka tidak boleh tahu tool apa yang dipakai.
    """
    # Metadata
    needs_requested: List[str] = field(default_factory=list)
    needs_satisfied: List[str] = field(default_factory=list)
    needs_failed: List[str] = field(default_factory=list)
    tool_calls_used: int = 0
    tool_budget: int = 5

    # Konten Evidence
    git: GitEvidence = field(default_factory=GitEvidence)
    files: List[FileEvidence] = field(default_factory=list)
    symbols: List[SymbolEvidence] = field(default_factory=list)
    searches: List[SearchEvidence] = field(default_factory=list)

    def is_sufficient(self) -> bool:
        """Apakah setidaknya satu Need berhasil dipenuhi?"""
        return len(self.needs_satisfied) > 0

    def has_gap(self) -> bool:
        """Apakah ada Need yang gagal dipenuhi? (Evidence Gap)"""
        return len(self.needs_failed) > 0

    def to_context_text(self) -> str:
        """
        Format EvidenceBundle menjadi teks ringkasan untuk disuntikkan
        ke dalam prompt Reasoning Engine dan Planning Engine.
        """
        lines = ["=== EVIDENCE BUNDLE ==="]

        if self.git.current_branch:
            lines.append(f"\n[Git] Branch: {self.git.current_branch}")
        if self.git.status:
            lines.append(f"\n[Git Status]\n{self.git.status[:800]}")
        if self.git.diff_summary:
            lines.append(f"\n[Git Diff Summary]\n{self.git.diff_summary[:600]}")
        if self.git.diff_full:
            lines.append(f"\n[Git Diff]\n{self.git.diff_full[:2000]}")

        for sym in self.symbols:
            lines.append(f"\n[Symbol: {sym.name} ({sym.type})] @ {sym.file}:{sym.start_line}-{sym.end_line}")
            lines.append(sym.code[:1000])

        for f in self.files:
            trunc_note = " [TRUNCATED]" if f.truncated else ""
            lines.append(f"\n[File: {f.path}]{trunc_note}")
            lines.append(f.content[:3000])

        for s in self.searches:
            lines.append(f"\n[Search: '{s.query}'] — {s.total_matches} matches")
            for m in s.matches[:5]:
                lines.append(f"  {m.get('file','')}:{m.get('line','')} → {m.get('content','')[:100]}")

        if self.needs_failed:
            lines.append(f"\n[⚠ Evidence Gaps] Could not satisfy: {', '.join(self.needs_failed)}")

        lines.append(f"\n[Tool Budget] Used {self.tool_calls_used}/{self.tool_budget} calls")
        return "\n".join(lines)
