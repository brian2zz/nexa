from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class IntentNode:
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    description: str = ""

@dataclass
class ExecutionStageNode:
    name: str
    intents: List[IntentNode] = field(default_factory=list)

@dataclass
class ExecutionPlan:
    goal: str
    summary: str
    complexity: str
    estimated_time: str
    affected_modules: List[str]
    affected_files: List[str]
    files_to_create: List[str]
    files_to_modify: List[str]
    dependencies: List[str]
    
    stages: List[ExecutionStageNode] = field(default_factory=list)
    
    verification_steps: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    rollback_strategy: str = ""
    confidence: int = 0
    provider_metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: dict):
        stages = []
        for stage_data in data.get('stages', []):
            intents = []
            for intent_data in stage_data.get('intents', []):
                intents.append(IntentNode(
                    action=intent_data.get('action', 'unknown'),
                    parameters=intent_data.get('parameters', {}),
                    description=intent_data.get('description', '')
                ))
            stages.append(ExecutionStageNode(
                name=stage_data.get('name', 'Unknown Stage'),
                intents=intents
            ))
            
        return cls(
            goal=data.get('goal', ''),
            summary=data.get('summary', ''),
            complexity=data.get('complexity', 'unknown'),
            estimated_time=data.get('estimated_time', 'unknown'),
            affected_modules=data.get('affected_modules', []),
            affected_files=data.get('affected_files', []),
            files_to_create=data.get('files_to_create', []),
            files_to_modify=data.get('files_to_modify', []),
            dependencies=data.get('dependencies', []),
            stages=stages,
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
