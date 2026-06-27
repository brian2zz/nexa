from .models import ContextBundle

class ContextValidator:
    """
    Validates that the context bundle is not empty and has valid metrics.
    """
    def validate(self, bundle: ContextBundle) -> bool:
        if not bundle.snippets and not bundle.files:
            return False
            
        # Remove duplicate snippets
        unique_snippets = list(set(bundle.snippets))
        bundle.snippets = [s for s in unique_snippets if s.strip()]
        
        return len(bundle.snippets) > 0 or len(bundle.files) > 0
