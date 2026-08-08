import os
import tempfile
import unittest
from nexa.core.models.dto.patch import PatchRequest
from nexa.core.models.enums import RiskLevel, SearchStrategy
from nexa.core.ai.patching.engine import PatchEngine

class TestGoldenPatchEngine(unittest.TestCase):
    def setUp(self):
        self.engine = PatchEngine()
        
    def test_golden_modify_login(self):
        """Test modify blok fungsi menggunakan skenario Aider style <<<< === >>>>"""
        # Setup temporary repository
        with tempfile.TemporaryDirectory() as temp_repo:
            target_file = "login.py"
            abs_path = os.path.join(temp_repo, target_file)
            
            # 1. State Awal (Current File)
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write("def login():\n    return False\n")
                
            # 2. Mock TransformationResult (Dari LLM)
            generated_code = (
                "Berikut adalah update login:\n"
                "<<<<\n"
                "def login():\n"
                "    return False\n"
                "====\n"
                "def login():\n"
                "    return True\n"
                ">>>>\n"
            )
            
            # 3. Eksekusi PatchEngine (The SUT - System Under Test)
            request = PatchRequest(
                transformation_result={"generated_code": generated_code},
                repository_root=temp_repo,
                target_files=[target_file],
                search_strategy=SearchStrategy.EXACT
            )
            
            result = self.engine.calculate_patch(request)
            
            # 4. Golden Assertions
            self.assertTrue(result.success)
            self.assertEqual(len(result.patches), 1)
            
            patch = result.patches[0]
            self.assertEqual(patch.path, target_file)
            self.assertEqual(patch.old_content, "def login():\n    return False")
            self.assertEqual(patch.new_content, "def login():\n    return True")
            
            # Risk Analysis Assertion (Ubah file biasa harusnya LOW)
            self.assertIsNotNone(result.analysis)
            self.assertEqual(result.analysis.risk_level, RiskLevel.LOW)
            self.assertFalse(result.analysis.needs_human_approval)

    def test_golden_modify_models_risk(self):
        """Test spesifik memastikan modifikasi models.py memicu risk rule."""
        with tempfile.TemporaryDirectory() as temp_repo:
            target_file = "models.py" # File sensitif sesuai Rule
            abs_path = os.path.join(temp_repo, target_file)
            
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write("class User:\n    pass\n")
                
            generated_code = (
                "<<<<\nclass User:\n    pass\n====\nclass User:\n    name = str\n>>>>\n"
            )
            
            request = PatchRequest(
                transformation_result={"generated_code": generated_code},
                repository_root=temp_repo,
                target_files=[target_file]
            )
            
            result = self.engine.calculate_patch(request)
            
            self.assertTrue(result.success)
            # Karena memodifikasi models.py, score harus +20 (MEDIUM)
            self.assertEqual(result.analysis.risk_level, RiskLevel.MEDIUM)
            self.assertEqual(result.analysis.risk_score, 20)

    def test_golden_unified_diff_single_hunk(self):
        with tempfile.TemporaryDirectory() as temp_repo:
            target_file = "login.py"
            abs_path = os.path.join(temp_repo, target_file)
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write("def login():\n    print(1)\n    print(2)\n    return True\n")
            
            diff = "@@ -1,4 +1,4 @@\n def login():\n-    print(1)\n-    print(2)\n+    print(3)\n     return True\n"
            req = PatchRequest(transformation_result={"generated_code": diff}, repository_root=temp_repo, target_files=[target_file])
            res = self.engine.calculate_patch(req)
            self.assertTrue(res.success)
            self.assertEqual(len(res.patches), 1)
            self.assertIn("print(3)", res.patches[0].new_content)
            self.assertNotIn("print(1)", res.patches[0].new_content)
            
    def test_golden_unified_diff_multi_hunk(self):
        with tempfile.TemporaryDirectory() as temp_repo:
            target_file = "app.py"
            abs_path = os.path.join(temp_repo, target_file)
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write("def a():\n    pass\n\ndef b():\n    pass\n")
            
            diff = "@@ -1,2 +1,2 @@\n def a():\n-    pass\n+    return 1\n@@ -3,2 +3,2 @@\n def b():\n-    pass\n+    return 2\n"
            req = PatchRequest(transformation_result={"generated_code": diff}, repository_root=temp_repo, target_files=[target_file])
            res = self.engine.calculate_patch(req)
            self.assertTrue(res.success)
            self.assertIn("return 1", res.patches[0].new_content)
            self.assertIn("return 2", res.patches[0].new_content)
            
    def test_golden_unified_diff_ast_reject(self):
        with tempfile.TemporaryDirectory() as temp_repo:
            target_file = "bad.py"
            abs_path = os.path.join(temp_repo, target_file)
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write("def func():\n    pass\n")
            
            diff = "@@ -1,2 +1,2 @@\n def func():\n-    pass\n+    return (\n"
            req = PatchRequest(transformation_result={"generated_code": diff}, repository_root=temp_repo, target_files=[target_file])
            res = self.engine.calculate_patch(req)
            self.assertFalse(res.success)
            self.assertEqual(len(res.patches), 0)
            self.assertTrue(any("AST Validation Error" in w for w in res.warnings))
            
    def test_golden_unified_diff_fallback(self):
        with tempfile.TemporaryDirectory() as temp_repo:
            target_file = "fall.py"
            abs_path = os.path.join(temp_repo, target_file)
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write("def fall():\n    pass\n")
            
            diff = "@@ -99,2 +99,2 @@\n def fall():\n-    pass\n+    return True\n"
            req = PatchRequest(transformation_result={"generated_code": diff}, repository_root=temp_repo, target_files=[target_file])
            res = self.engine.calculate_patch(req)
            self.assertTrue(res.success)
            self.assertIn("return True", res.patches[0].new_content)
            self.assertTrue(any("Fallback triggered" in w for w in res.warnings))

if __name__ == '__main__':
    unittest.main()
