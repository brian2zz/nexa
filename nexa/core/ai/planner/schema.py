from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class RiskItem:
    category: str
    probability: str
    impact: str
    mitigation: str

@dataclass
class ConfidenceAssessment:
    level: str
    score: int
    reason: str
    missing_information: str

@dataclass
class AcceptanceCriterion:
    description: str
    priority: str
    verification_method: str

@dataclass
class AffectedComponents:
    models: List[str] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    commands: List[str] = field(default_factory=list)
    tests: List[str] = field(default_factory=list)
    docs: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)

@dataclass
class WorkItem:
    title: str
    description: str
    objective: str
    affected_files: List[str] = field(default_factory=list)

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
class PlanningResult:
    goal: str
    summary: str
    objective: str
    constraints: List[str] = field(default_factory=list)
    affected_components: AffectedComponents = field(default_factory=AffectedComponents)
    work_items: List[WorkItem] = field(default_factory=list)
    acceptance_criteria: List[AcceptanceCriterion] = field(default_factory=list)
    risk_analysis: List[RiskItem] = field(default_factory=list)
    clarifications: List[str] = field(default_factory=list)
    confidence: ConfidenceAssessment = field(default_factory=lambda: ConfidenceAssessment("LOW", 0, "", ""))
    provider_metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def affected_files(self) -> List[str]:
        files = set(self.affected_components.files)
        for w in self.work_items:
            files.update(w.affected_files)
        return list(files)

    @classmethod
    def from_dict(cls, data: dict):
        ac_data = data.get('affected_components', {})
        affected_components = AffectedComponents(
            models=ac_data.get('models', []),
            services=ac_data.get('services', []),
            commands=ac_data.get('commands', []),
            tests=ac_data.get('tests', []),
            docs=ac_data.get('docs', []),
            files=ac_data.get('files', [])
        )
        
        work_items = []
        for w in data.get('work_items', []):
            work_items.append(WorkItem(
                title=w.get('title', ''),
                description=w.get('description', ''),
                affected_files=w.get('affected_files', []),
                objective=w.get('objective', '')
            ))
            
        acceptance_criteria = []
        for a in data.get('acceptance_criteria', []):
            acceptance_criteria.append(AcceptanceCriterion(
                description=a.get('description', ''),
                priority=a.get('priority', 'MUST'),
                verification_method=a.get('verification_method', '')
            ))
            
        risk_analysis = []
        for r in data.get('risk_analysis', []):
            risk_analysis.append(RiskItem(
                category=r.get('category', ''),
                probability=r.get('probability', 'LOW'),
                impact=r.get('impact', 'LOW'),
                mitigation=r.get('mitigation', '')
            ))
            
        conf_data = data.get('confidence', {})
        confidence = ConfidenceAssessment(
            level=conf_data.get('level', 'LOW'),
            score=conf_data.get('score', 0),
            reason=conf_data.get('reason', ''),
            missing_information=conf_data.get('missing_information', '')
        )
        
        return cls(
            goal=data.get('goal', ''),
            summary=data.get('summary', ''),
            objective=data.get('objective', ''),
            constraints=data.get('constraints', []),
            affected_components=affected_components,
            work_items=work_items,
            acceptance_criteria=acceptance_criteria,
            risk_analysis=risk_analysis,
            clarifications=data.get('clarifications', []),
            confidence=confidence,
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
