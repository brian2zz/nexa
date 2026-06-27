from typing import Dict, List
from .models import IntentContext

class IntentEngine:
    """
    Translates raw user goals into intent domains and keywords.
    """
    DOMAINS = {
        "authentication": ["login", "register", "auth", "jwt", "session", "signin", "signup"],
        "workspace": ["workspace", "team", "organization", "org", "member", "invite"],
        "database": ["db", "sql", "migration", "schema", "model", "repository"],
        "ui": ["component", "layout", "theme", "render", "view", "page", "widget"]
    }

    def analyze(self, goal: str) -> IntentContext:
        goal_lower = goal.lower()
        words = goal_lower.split()
        
        selected_domain = "general"
        keywords = set(words)
        
        for domain, domain_keywords in self.DOMAINS.items():
            for kw in domain_keywords:
                if kw in goal_lower:
                    selected_domain = domain
                    keywords.update(domain_keywords)
                    break
            if selected_domain != "general":
                break
                
        return IntentContext(domain=selected_domain, keywords=list(keywords))
