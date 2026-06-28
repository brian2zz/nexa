from typing import List, Protocol
from nexa.core.models.dto.patch import PatchObject, PatchAnalysis
from nexa.core.models.enums import RiskLevel

class RiskRule(Protocol):
    def evaluate(self, patch: PatchObject) -> int:
        """Returns risk score points for a single patch."""
        ...

class DeleteFileRule:
    def evaluate(self, patch: PatchObject) -> int:
        if patch.operation.name == "DELETE":
            return 30
        return 0

class MigrationFileRule:
    def evaluate(self, patch: PatchObject) -> int:
        if "migrations/" in patch.path or "alembic/" in patch.path:
            return 50
        return 0

class ModelFileRule:
    def evaluate(self, patch: PatchObject) -> int:
        if "models.py" in patch.path or "schema.py" in patch.path:
            return 20
        return 0

class MassiveDeleteRule:
    def evaluate(self, patch: PatchObject) -> int:
        if patch.diff and patch.diff.count("\n-") > 50:
            return 30
        return 0

class RiskAnalyzer:
    def __init__(self):
        self.rules: List[RiskRule] = [
            DeleteFileRule(),
            MigrationFileRule(),
            ModelFileRule(),
            MassiveDeleteRule()
        ]
        
    def analyze(self, patches: List[PatchObject]) -> PatchAnalysis:
        total_score = 0
        factors = []
        
        for patch in patches:
            for rule in self.rules:
                score = rule.evaluate(patch)
                if score > 0:
                    total_score += score
                    factors.append(f"Terpicu rule {rule.__class__.__name__} pada {patch.path} (+{score})")
                    
        # Tentukan Risk Level
        if total_score >= 80:
            level = RiskLevel.CRITICAL
            needs_approval = True
        elif total_score >= 50:
            level = RiskLevel.HIGH
            needs_approval = True
        elif total_score >= 20:
            level = RiskLevel.MEDIUM
            needs_approval = False
        else:
            level = RiskLevel.LOW
            needs_approval = False
            
        return PatchAnalysis(
            risk_level=level,
            risk_score=total_score,
            risk_factors=factors,
            needs_human_approval=needs_approval
        )
