import os
import pkgutil
import importlib
from .base_registry import BaseRegistry, RegistryEntry

# --- Priority Constants ---
PRIORITY_CRITICAL = 0
PRIORITY_CORE = 100
PRIORITY_EXTENSION = 500
PRIORITY_LOW = 1000

# 1. Specialized Registries
class GeneratorRegistry(BaseRegistry):
    def __init__(self):
        super().__init__("Generator")

class TranslatorRegistry(BaseRegistry):
    def __init__(self):
        super().__init__("Translator")

class FieldRegistry(BaseRegistry):
    def __init__(self):
        super().__init__("Field")

# 2. Global Instances
generators = GeneratorRegistry()
translators = TranslatorRegistry()
fields = FieldRegistry()

# 3. Structured Decorators
def nexa_generator(key, category="api", target="any", priority=PRIORITY_CORE, metadata=None):
    def decorator(cls):
        generators.register(
            key=key, 
            value=cls, 
            category=category, 
            target=target, 
            priority=priority, 
            metadata=metadata
        )
        return cls
    return decorator

def nexa_translator(key, category="django", priority=PRIORITY_CORE, metadata=None):
    def decorator(cls):
        translators.register(
            key=key, 
            value=cls, 
            category=category, 
            priority=priority, 
            metadata=metadata
        )
        return cls
    return decorator

# 4. Advanced Discovery System
def autodiscover(package_path, package_name):
    """
    Automatically scans and imports all modules in a given package path
    to trigger registration decorators.
    """
    for _, module_name, is_pkg in pkgutil.walk_packages([package_path], package_name + "."):
        if not is_pkg:
            importlib.import_module(module_name)

def discover_core():
    """
    Discovery for Nexa Core components.
    """
    # Get the absolute path of nexa.core
    import nexa.core as core
    core_path = os.path.dirname(core.__file__)
    
    # Auto-scan core generators
    autodiscover(os.path.join(core_path, 'generators', 'api'), 'nexa.core.generators.api')
    autodiscover(os.path.join(core_path, 'generators', 'crud'), 'nexa.core.generators.crud')
    autodiscover(os.path.join(core_path, 'generators', 'scaffold'), 'nexa.core.generators.scaffold')
    
    # Auto-scan core translators
    autodiscover(os.path.join(core_path, 'schema', 'translators'), 'nexa.core.schema.translators')
