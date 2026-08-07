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
from nexa.core.ai.knowledge.orchestrator import KnowledgeOrchestrator, CapabilityResolver

__all__ = ["Need", "EvidenceBundle", "KnowledgeOrchestrator", "CapabilityResolver"]
