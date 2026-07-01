import os
from typing import Tuple, Union

# Facade module for the new Secure Execution Layer
from nexa.core.pipeline.execution.parser import CommandParser
from nexa.core.pipeline.execution.policy import PolicyEngine
from nexa.core.pipeline.execution.risk import RiskAnalyzer
from nexa.core.pipeline.execution.runner import TerminalRunner as NewTerminalRunner
from nexa.core.pipeline.execution.audit import AuditService
from nexa.core.pipeline.execution.models import CommandResult, ExecutionPlan, ExecutionStrategy, CommandRequest

class CommandPolicy:
    """
    Legacy wrapper. This class is kept for backward compatibility, 
    but its logic is now delegated to PolicyEngine.
    """
    @classmethod
    def is_allowed(cls, command: str) -> bool:
        parser = CommandParser()
        success, err, reqs = parser.parse_all(command, os.getcwd())
        if not success or not reqs:
            return False
            
        policy = PolicyEngine()
        for _, req in reqs:
            is_valid, _ = policy.evaluate(req)
            if not is_valid:
                return False
        return True

class TerminalRunner:
    """
    The main entry point for executing terminal commands.
    It orchestrates the Parser, PolicyEngine, RiskAnalyzer, Executor, and Auditor.
    Handles sequential execution of ExecutionPlan Stages and Steps.
    """
    def __init__(self, cwd: str):
        self.cwd = cwd
        self.parser = CommandParser()
        self.policy_engine = PolicyEngine()
        self.risk_analyzer = RiskAnalyzer()
        self.executor = NewTerminalRunner()
        self.auditor = AuditService(self.cwd)
        
    def execute(self, command: str) -> Tuple[bool, str]:
        """
        Legacy string execution. Parses and executes.
        """
        success, err_msg, reqs = self.parser.parse_all(command, self.cwd)
        if not success:
            return False, f"Parser Error: {err_msg}"
            
        total_output = []
        overall_success = True
        
        for operator, req in reqs:
            if operator == "&&" and not overall_success:
                total_output.append(f"\n[!] Skipping '{req.raw_command}' due to previous failure (&&).")
                break
                
            is_valid, policy_err = self.policy_engine.evaluate(req)
            if not is_valid:
                return False, f"Policy Violation: {policy_err}"
                
            self.risk_analyzer.analyze(req)
            result = self.executor.execute(req)
            self.auditor.log(result)
            
            out = result.stdout if result.success else (result.stderr or result.stdout)
            total_output.append(out)
            overall_success = result.success
            
            if not overall_success and operator != ";":
                if operator == "" and len(reqs) > 1:
                    pass
                    
        return overall_success, "\n".join(total_output)

    def execute_plan(self, plan: ExecutionPlan) -> Tuple[bool, str]:
        """
        Executes a structured ExecutionPlan directly.
        This is the new Intent-Based Execution Flow.
        """
        total_output = []
        overall_success = True
        
        for stage in plan.stages:
            total_output.append(f"\n=== Stage: {stage.name} ===")
            
            for step in stage.steps:
                # 1. Policy Evaluation
                # Convert CommandStep to CommandRequest for policy evaluation
                req = CommandRequest(
                    raw_command=step.raw_command,
                    executable=step.executable,
                    args=step.args,
                    cwd=step.cwd,
                    env=step.env,
                    timeout=step.timeout
                )
                
                is_valid, policy_err = self.policy_engine.evaluate(req)
                if not is_valid:
                    total_output.append(f"[!] Policy Violation on {step.id}: {policy_err}")
                    return False, "\n".join(total_output)
                    
                # 2. Risk Evaluation (Ensure it was done)
                self.risk_analyzer.analyze(step)
                
                # 3. Check Conditions (if any)
                if step.condition == "if_previous_success" and not overall_success:
                    total_output.append(f"[~] Skipping Step {step.id} (Condition not met)")
                    continue
                    
                # 4. Execute
                result: CommandResult = self.executor.execute(step)
                
                # 5. Audit
                self.auditor.log(result)
                
                out = result.stdout if result.success else (result.stderr or result.stdout)
                total_output.append(f"--- Output of '{step.raw_command}' ---")
                total_output.append(out)
                
                overall_success = result.success
                
                # 6. Apply Execution Strategy
                if not overall_success:
                    if step.strategy == ExecutionStrategy.STOP_ON_ERROR:
                        total_output.append(f"[!] Stopping execution at Stage '{stage.name}' due to STOP_ON_ERROR strategy.")
                        return False, "\n".join(total_output)
                    elif step.strategy == ExecutionStrategy.CONTINUE_ON_ERROR:
                        total_output.append(f"[!] Step failed, but continuing due to CONTINUE_ON_ERROR strategy.")
                    elif step.strategy == ExecutionStrategy.FALLBACK:
                        total_output.append(f"[!] Step failed. Requesting FALLBACK (Not implemented yet).")
                        return False, "\n".join(total_output)
                        
        return overall_success, "\n".join(total_output)
