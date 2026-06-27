import os
from typing import List, Dict, Any
from .models import ContextBundle
from .loader import SourceLoader
from .optimizer import ContextOptimizer
from .validator import ContextValidator
from .extractors import get_extractor
from .estimators import SimpleTokenEstimator

class ContextResolver:
    """
    Task-Aware Context Resolver Engine.
    Filters down the project files into a high-density ContextBundle.
    """
    def __init__(self):
        self.loader = SourceLoader()
        self.optimizer = ContextOptimizer()
        self.validator = ContextValidator()
        self.estimator = SimpleTokenEstimator()

    def _determine_scope(self, task: str) -> dict:
        """Returns strategy based on task type."""
        task = task.lower()
        if task == "analyze":
            return {"snippet": False, "depth": 1}
        elif task == "explain":
            return {"snippet": True, "depth": 0}
        elif task == "planner":
            return {"snippet": True, "depth": 0, "structural_only": True}
        elif task == "generator":
            return {"snippet": True, "depth": 1}
        elif task == "refactor":
            return {"snippet": True, "depth": 2} # deep
        return {"snippet": True, "depth": 0}

    def resolve(
        self, 
        task: str, 
        goal: str, 
        project_path: str, 
        target_files: List[str], 
        keywords: List[str],
        project_facts: Dict[str, str] = None,
        pinned_memory: List[Dict[str, Any]] = None
    ) -> ContextBundle:
        
        strategy = self._determine_scope(task)
        bundle = ContextBundle(
            goal=goal,
            project_facts=project_facts or {},
            pinned_memory=pinned_memory or [],
            files=target_files
        )
        
        original_tokens = 0
        final_tokens = 0
        
        # 1. Dependency Resolution (Mocked for V1, assuming KnowledgeEngine provides files)
        resolved_files = target_files
        
        # 2. Loading and Extracting
        for f_path in resolved_files:
            code = self.loader.load(project_path, f_path)
            if not code:
                continue
                
            orig_est = self.estimator.estimate(code)
            original_tokens += orig_est
            
            if not strategy["snippet"]:
                # Full file requested (e.g., Analyze)
                optimized = self.optimizer.optimize(code)
                bundle.snippets.append(f"--- File: {f_path} ---\n{optimized}")
                bundle.selection_method = "full_file"
                bundle.confidence = 1.0
                bundle.fallback_level = 4
                final_tokens += self.estimator.estimate(optimized)
            else:
                # Task requires snippet extraction
                _, ext = os.path.splitext(f_path)
                extractor = get_extractor(ext)
                
                snippet, conf, method, fallback = extractor.extract(code, keywords)
                if snippet:
                    optimized = self.optimizer.optimize(snippet)
                    bundle.snippets.append(f"--- Snippet from: {f_path} ---\n{optimized}")
                    bundle.confidence = conf
                    bundle.selection_method = method
                    bundle.fallback_level = fallback
                    final_tokens += self.estimator.estimate(optimized)
                    
        bundle.estimated_tokens = final_tokens
        
        if original_tokens > 0:
            ratio = ((original_tokens - final_tokens) / original_tokens) * 100
            bundle.compression_ratio = round(ratio, 2)
            
        self.validator.validate(bundle)
        return bundle
