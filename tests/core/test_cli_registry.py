import importlib
import pytest
from nexa.commands.registry import GROUPS

def test_registry_modules_can_be_imported():
    """Memastikan bahwa semua modul di dalam registry CLI valid dan tidak ada yang mati."""
    failed_imports = []
    
    for group, commands in GROUPS.items():
        for cmd in commands:
            module_name = cmd.get("module")
            if not module_name:
                continue
                
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                failed_imports.append(f"{group} -> {cmd['name']} ({module_name}): {e}")
                
    assert not failed_imports, f"Beberapa modul registry gagal dimuat:\n" + "\n".join(failed_imports)
