from typing import List, Set
from .models import IntentContext

class IntentMatcher:
    """
    Expands IntentContext into a comprehensive set of matching tokens for the Selector.
    """
    def match(self, intent: IntentContext) -> List[str]:
        # Just use the keywords from the Intent Engine
        # Future: could add synonym expansion or specific project aliases here
        return list(set(intent.keywords))
