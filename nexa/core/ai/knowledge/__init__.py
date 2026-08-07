"""
Nexa Knowledge Layer — Capability-Based Knowledge Acquisition

Package ini adalah satu-satunya lapisan dalam Cognitive Pipeline
yang diizinkan untuk memanggil tools=[] ke LLM atau mengeksekusi
tool terhadap filesystem/git.

Semua layer lain (Hypothesis, Reasoning, Planning) hanya boleh
membaca EvidenceBundle yang dihasilkan oleh package ini.
"""

from nexa.core.ai.knowledge.need import Need
from nexa.core.ai.knowledge.evidence import EvidenceBundle
def __getattr__(name):
    if name in {"KnowledgeOrchestrator", "CapabilityResolver"}:
        import nexa.core.ai.knowledge.orchestrator as _orchestrator
        return getattr(_orchestrator, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["Need", "EvidenceBundle", "KnowledgeOrchestrator", "CapabilityResolver"]
