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

if __name__ == '__main__':
    unittest.main()
