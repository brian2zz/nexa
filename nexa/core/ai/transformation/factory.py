from .models import TransformationMode
from .prompts.base import BasePromptBuilder
from .prompts.generator import GeneratorPromptBuilder
from .prompts.modifier import ModifierPromptBuilder
from .prompts.repair import RepairPromptBuilder
from .prompts.analyzer import AnalyzerPromptBuilder

class PromptFactory:
    """
    Decouples the Engine from the specific prompt implementations.
    """
    @staticmethod
    def get_builder(mode: TransformationMode) -> BasePromptBuilder:
        if mode == TransformationMode.GENERATE:
            return GeneratorPromptBuilder()
            
        elif mode in [TransformationMode.MODIFY, TransformationMode.REFACTOR, TransformationMode.OPTIMIZE]:
            return ModifierPromptBuilder()
            
        elif mode == TransformationMode.REPAIR:
            return RepairPromptBuilder()
            
        elif mode in [TransformationMode.EXPLAIN, TransformationMode.SUMMARIZE, TransformationMode.TRANSLATE]:
            return AnalyzerPromptBuilder()
            
        return ModifierPromptBuilder() # fallback
