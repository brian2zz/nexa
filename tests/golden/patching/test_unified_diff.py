import os
import pytest
from nexa.core.models.dto.patch import PatchRequest
from nexa.core.ai.patching.engine import PatchEngine

@pytest.fixture
def temp_workspace(tmp_path):
    sample_code = """def hello():
    print("Hello, world!")

def calculate(a, b):
    # This is a comment
    result = a + b
    return result

if __name__ == "__main__":
    hello()
    print(calculate(2, 3))
"""
    file_path = tmp_path / "app.py"
    file_path.write_text(sample_code, encoding="utf-8")
    return str(tmp_path)

def test_unified_diff_precision_applier(temp_workspace):
    # Test our new line-number based unified diff logic
    patch_engine = PatchEngine(bus=None)
    
    # Let's generate a diff that changes calculate and changes hello
    diff = """
@@ -1,5 +1,5 @@
 def hello():
-    print("Hello, world!")
+    print("Hello, precise patch!")

 def calculate(a, b):
@@ -4,4 +4,3 @@
 def calculate(a, b):
-    # This is a comment
-    result = a + b
-    return result
+    # Updated comment
+    return a * b
"""

    request = PatchRequest(
        transformation_result={"generated_code": diff},
        repository_root=temp_workspace,
        target_files=["app.py"]
    )
    
    result = patch_engine.calculate_patch(request)
    assert result.success
    assert len(result.patches) == 1
    
    patch = result.patches[0]
    new_content = patch.new_content
    
    assert 'print("Hello, precise patch!")' in new_content
    assert 'return a * b' in new_content
    assert '# This is a comment' not in new_content
    assert 'print("Hello, world!")' not in new_content
    
    if any("Fallback triggered" in w for w in result.warnings):
        print("WARNINGS:", result.warnings)
    assert not any("Fallback triggered" in w for w in result.warnings)
    
def test_unified_diff_fallback(temp_workspace):
    patch_engine = PatchEngine(bus=None)
    # Give a diff with wrong line numbers, which will trigger fallback
    diff = """
@@ -99,5 +99,5 @@
 def hello():
-    print("Hello, world!")
+    print("Hello, fallback!")
"""

    request = PatchRequest(
        transformation_result={"generated_code": diff},
        repository_root=temp_workspace,
        target_files=["app.py"]
    )
    
    result = patch_engine.calculate_patch(request)
    assert result.success
    assert len(result.patches) == 1
    
    patch = result.patches[0]
    new_content = patch.new_content
    
    assert 'print("Hello, fallback!")' in new_content
    assert 'print("Hello, world!")' not in new_content
    
    # Check that fallback was indeed triggered
    assert any("Fallback triggered" in w for w in result.warnings)
