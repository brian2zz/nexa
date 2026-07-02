from .schema import PlanningResult, ExecutionPlan, ExecutionStageNode, IntentNode

class PipelineBuilder:
    """
    Translates a PlanningResult (Domain Model) into an ExecutionPlan (Pipeline Model).
    """
    def build(self, result: PlanningResult) -> ExecutionPlan:
        # Map WorkItems to ExecutionStages/Intents
        stages = []
        
        # 1. Preparation Stage (if needed based on constraints)
        prep_intents = []
        for constraint in result.constraints:
            prep_intents.append(IntentNode(
                action="ASSERT_CONSTRAINT",
                parameters={"constraint": constraint},
                description=f"Ensure: {constraint}"
            ))
        
        if prep_intents:
            stages.append(ExecutionStageNode(name="Preparation", intents=prep_intents))
            
        # 2. Transformation Stage
        transform_intents = []
        for work in result.work_items:
            for file_path in work.affected_files:
                transform_intents.append(IntentNode(
                    action="MODIFY",
                    parameters={
                        "target": file_path
                    },
                    description=f"Task: {work.title}\nObjective: {work.objective}\nDetails: {work.description}"
                ))
            
        if transform_intents:
            stages.append(ExecutionStageNode(name="Transformation", intents=transform_intents))
            
        # 2.5 Command Execution Stage
        command_intents = []
        if hasattr(result.affected_components, 'commands') and result.affected_components.commands:
            for cmd in result.affected_components.commands:
                command_intents.append(IntentNode(
                    action="COMMAND",
                    parameters={
                        "target": cmd
                    },
                    description=f"Execute terminal command: {cmd}"
                ))
                
        if command_intents:
            stages.append(ExecutionStageNode(name="Commands", intents=command_intents))
            
            
        # 3. Verification Stage
        verification_intents = []
        for ac in result.acceptance_criteria:
            verification_intents.append(IntentNode(
                action="VERIFY",
                parameters={
                    "priority": ac.priority,
                    "method": ac.verification_method
                },
                description=ac.description
            ))
            
        if verification_intents:
            stages.append(ExecutionStageNode(name="Verification", intents=verification_intents))
            
        # Combine all files
        all_files = result.affected_files
        
        # Build legacy ExecutionPlan
        return ExecutionPlan(
            goal=result.goal,
            summary=result.summary,
            complexity="Medium", # Mapped from confidence/risk if needed
            estimated_time="Unknown",
            affected_modules=result.affected_components.models + result.affected_components.services,
            affected_files=all_files,
            files_to_create=[],
            files_to_modify=all_files,
            dependencies=[],
            stages=stages,
            verification_steps=[ac.description for ac in result.acceptance_criteria],
            warnings=[f"RISK ({r.category}): {r.mitigation}" for r in result.risk_analysis],
            recommendations=result.constraints,
            rollback_strategy="Auto-backup before Transformation",
            confidence=result.confidence.score,
            provider_metadata=result.provider_metadata
        )
