from .schema import PlanningResult, ExecutionPlan, ExecutionStageNode, IntentNode

class PipelineBuilder:
    """
    Translates a PlanningResult (Domain Model) into an ExecutionPlan (Pipeline Model).
    """
    def build(self, result: PlanningResult) -> ExecutionPlan:
        # Map WorkItems to ExecutionStages/Intents
        stages = []
        import os
        
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
            
        # Extract YAML schema from summary if present
        yaml_content = ""
        if result.summary and "```yaml" in result.summary:
            try:
                parts = result.summary.split("```yaml")
                if len(parts) > 1:
                    yaml_content = parts[1].split("```")[0].strip()
            except Exception:
                pass

        # 2. Transformation Stage
        transform_intents = []
        commands_to_run = []

        for work in result.work_items:
            work_text = (work.title + " " + work.description + " " + work.objective).lower()
            if "nexa php generate" in work_text or "generate" in work_text:
                commands_to_run.append("nexa php generate nexa.yaml")
            if "makemigrations" in work_text or "migrate" in work_text:
                commands_to_run.append("php bin/nexa migrate")

            for file_path in work.affected_files:
                # If it's a directory (e.g. app/, database/, routes/), skip file transformation
                if file_path.endswith("/") or file_path.strip() in ["app", "apps", "database", "routes"]:
                    continue

                abs_f = file_path if os.path.isabs(file_path) else os.path.join(".", file_path)
                file_action = "MODIFY" if os.path.exists(abs_f) else "CREATE"

                params = {"target": file_path}
                if file_path.endswith("nexa.yaml") and yaml_content:
                    params["content"] = yaml_content

                transform_intents.append(IntentNode(
                    action=file_action,
                    parameters=params,
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
        for cmd in commands_to_run:
            if not any(ci.parameters.get("target") == cmd for ci in command_intents):
                command_intents.append(IntentNode(
                    action="COMMAND",
                    parameters={"target": cmd},
                    description=f"Execute scaffolding command: {cmd}"
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
