from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class RegistryEntry:
    key: str
    value: Any
    category: str = "general"
    target: str = "any"
    priority: int = 100
    metadata: Dict[str, Any] = field(default_factory=dict)

class BaseRegistry:
    def __init__(self, name: str):
        self.name = name
        self._registry: Dict[str, RegistryEntry] = {}
        # Grouped index for faster filtering
        self._by_category: Dict[str, List[RegistryEntry]] = {}

    def register(self, key: str, value: Any, category: str = "general", 
                 target: str = "any", priority: int = 100, metadata: Optional[Dict[str, Any]] = None):
        """
        Registers a new component. Raises ValueError if key already exists.
        """
        if key in self._registry:
            raise ValueError(f"[{self.name} Registry] Collision: Key '{key}' is already registered.")

        entry = RegistryEntry(
            key=key,
            value=value,
            category=category,
            target=target,
            priority=priority,
            metadata=metadata or {}
        )
        
        # Save to main registry
        self._registry[key] = entry
        
        # Update grouped index
        if category not in self._by_category:
            self._by_category[category] = []
        self._by_category[category].append(entry)
        
        # Sort index by priority
        self._by_category[category].sort(key=lambda x: x.priority)

    def get(self, key: str) -> Optional[Any]:
        entry = self._registry.get(key)
        return entry.value if entry else None

    def list_all(self, sort_by_priority: bool = True) -> List[RegistryEntry]:
        entries = list(self._registry.values())
        if sort_by_priority:
            entries.sort(key=lambda x: x.priority)
        return entries

    def filter(self, category: Optional[str] = None, 
               target: Optional[str] = None, 
               metadata_filter: Optional[Dict[str, Any]] = None) -> List[RegistryEntry]:
        """
        Filters entries with optimized category lookup and metadata matching.
        """
        # Start with category index if available, else all entries
        candidates = self._by_category.get(category) if category else list(self._registry.values())
        if not candidates:
            return []

        results = []
        for entry in candidates:
            # Filter by Target
            if target and entry.target != target:
                continue
                
            # Filter by Metadata
            if metadata_filter:
                match = True
                for k, v in metadata_filter.items():
                    if entry.metadata.get(k) != v:
                        match = False
                        break
                if not match:
                    continue
            
            results.append(entry)
        
        # Ensure results are sorted (category index is already sorted)
        if not category:
            results.sort(key=lambda x: x.priority)
            
        return results
