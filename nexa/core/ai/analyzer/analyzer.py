from typing import Any, Optional
import time

from nexa.core.ai.knowledge.models import ScannerResult, AnalyzerResult as StaticAnalyzerResult
from nexa.core.ai.knowledge.engine import KnowledgeEngine
from nexa.core.ai.prompt.context import PromptContext
from nexa.core.ai.prompt.engine import PromptEngine

from .schema import AnalysisResult, AnalysisSession, ProviderMetadata
from .response_parser import ResponseParser
from .merger import Merger
from .history import HistoryManager
from .formatter import OutputFormatter

class AIAnalyzer:
    """
    Orchestration layer. Does not know about specific providers (Ollama, etc).
    Only knows: provider.generate(messages)
    """
    def __init__(self, provider: Any):
        self.provider = provider
        self.knowledge_engine = KnowledgeEngine()
        self.prompt_engine = PromptEngine()
        self.parser = ResponseParser()
        self.merger = Merger()
        self.formatter = OutputFormatter()

    def analyze(self, 
                goal: str, 
                scanner_result: ScannerResult, 
                static_result: StaticAnalyzerResult, 
                max_retries: int = 2) -> AnalysisResult:
        
        project_root = scanner_result.project_root or "."
        self.history_manager = HistoryManager(project_root)
        
        # 1. Knowledge Engine
        k_context = self.knowledge_engine.build(
            goal=goal, 
            task="analyze", 
            scanner_result=scanner_result, 
            analyzer_result=static_result
        )
        
        # 2. Prompt Engine
        # Map KnowledgeContext to PromptContext
        p_context = PromptContext(
            task="analyze",
            goal=goal,
            framework=k_context.framework,
            language=k_context.language,
            statistics={
                "project_files": k_context.metrics.project_files,
                "selected_files": k_context.metrics.selected_files,
                "compression_ratio": k_context.metrics.compression_ratio
            },
            selected_files=[{"path": f.path, "content": f.content} for f in k_context.selected_files]
        )
        prompt_messages = self.prompt_engine.create_messages(p_context)
        
        # 3. Provider loop with Retry Policy
        messages = prompt_messages.messages
        attempts = 0
        parsed_json = {}
        raw_resp = ""
        success = False
        error_msg = ""
        
        start_time = time.time()
        
        while attempts <= max_retries:
            try:
                raw_resp_data = self.provider.generate(messages)
                raw_resp = raw_resp_data.get("content", "") if isinstance(raw_resp_data, dict) else str(raw_resp_data)
            except Exception as e:
                return AnalysisResult(
                    success=False,
                    errors=[f"Provider Error: {str(e)}"],
                    raw_response=""
                )
            
            is_valid, parsed, err = self.parser.parse(raw_resp)
            if is_valid:
                parsed_json = parsed
                success = True
                break
            else:
                attempts += 1
                error_msg = err
                if attempts <= max_retries:
                    # Inject retry prompt
                    messages.append({"role": "assistant", "content": raw_resp})
                    messages.append({"role": "user", "content": "The previous response was not valid JSON. Return ONLY valid JSON, do not use markdown or conversational text."})
        
        latency = time.time() - start_time
        
        if not success:
            return AnalysisResult(
                success=False, 
                errors=[f"Failed to parse JSON after {max_retries} retries. Last error: {error_msg}"],
                raw_response=raw_resp
            )
            
        # 4. Extract Provider Metadata
        # We rely on the provider having standard properties or we mock it
        p_meta = ProviderMetadata(
            name=getattr(self.provider, 'name', 'GenericProvider'),
            model=getattr(self.provider, 'model', 'unknown'),
            latency_sec=latency,
            estimated_tokens=prompt_messages.estimated_tokens
        )
            
        # 5. Merger
        # Pass static data, knowledge, AI JSON, and provider metadata
        report = self.merger.merge(
            static_data={"architecture_score": 8, "maintainability_score": 7}, # Mocked static data for now
            knowledge_context=k_context,
            ai_parsed_json=parsed_json,
            provider_metadata=p_meta
        )
        
        # 6. Session & History
        session = AnalysisSession(
            report=report,
            knowledge_context=k_context,
            prompt_messages=messages,
            provider_metadata=p_meta,
            raw_response=raw_resp
        )
        
        history_file = self.history_manager.save(session)
        
        return AnalysisResult(
            success=True,
            report=report,
            raw_response=raw_resp,
            warnings=[f"Session saved to {history_file}"]
        )
