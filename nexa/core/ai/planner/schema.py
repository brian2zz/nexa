from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ExecutionStep:
    action: str
    target: str
    description: str

@dataclass
class ExecutionPlan:
    goal: str
    summary: str
    complexity: str
    estimated_time: str
    risk: str
    affected_modules: List[str]
    affected_files: List[str]
    files_to_create: List[str]
    files_to_modify: List[str]
    dependencies: List[str]
    execution_steps: List[ExecutionStep]
    verification_steps: List[str]
    warnings: List[str]
    recommendations: List[str]
    rollback_strategy: str
    confidence: int
    provider_metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: dict):
        steps = [ExecutionStep(**step) if isinstance(step, dict) else ExecutionStep(action="unknown", target="unknown", description=str(step)) for step in data.get('execution_steps', [])]
        return cls(
            goal=data.get('goal', ''),
            summary=data.get('summary', ''),
            complexity=data.get('complexity', 'unknown'),
            estimated_time=data.get('estimated_time', 'unknown'),
            risk=data.get('risk', 'unknown'),
            affected_modules=data.get('affected_modules', []),
            affected_files=data.get('affected_files', []),
            files_to_create=data.get('files_to_create', []),
            files_to_modify=data.get('files_to_modify', []),
            dependencies=data.get('dependencies', []),
            execution_steps=steps,
            verification_steps=data.get('verification_steps', []),
            warnings=data.get('warnings', []),
            recommendations=data.get('recommendations', []),
            rollback_strategy=data.get('rollback_strategy', ''),
            confidence=data.get('confidence', 0),
            provider_metadata=data.get('provider_metadata', {})
        )

@dataclass
class PlannerContext:
    project_path: str
    knowledge_context: str
    project_facts: Dict[str, str]
    pinned_memory: List[Dict[str, Any]]
    conversation_memory: List[Dict[str, str]]
    user_goal: str
