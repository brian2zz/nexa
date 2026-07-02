import os
import ast
from typing import List, Optional, Tuple
from nexa.core.pipeline.transformation import TransformationResult

class PatchResult:
    def __init__(self, target: str, action: str, content: str = "", command: str = ""):
        self.target = target
        self.action = action
        self.content = content
        self.command = command

class SearchReplaceBlock:
    """
    Represents a single SEARCH/REPLACE block from LLM output.
    """
    def __init__(self, search: str, replace: str):
        self.search = search
        self.replace = replace

class PatchEngine:
    """
    Tugas: Mengubah TransformationResult (kode mentah) menjadi PatchResult yang siap diaplikasikan.
    Mendukung SEARCH/REPLACE blocks dan CREATE actions.
    """
    def calculate(self, transform_results: List[TransformationResult]) -> List[PatchResult]:
        patches = []
        for tr in transform_results:
            action = tr.step.get("action", "").upper()
            target = tr.step.get("target", "")
            
            if action == "CREATE":
                patches.append(PatchResult(target=target, action="CREATE", content=tr.raw_code))
            elif action == "MODIFY":
                # For MODIFY, the raw_code contains SEARCH/REPLACE blocks
                patches.append(PatchResult(target=target, action="MODIFY", content=tr.raw_code))
            elif action == "DELETE":
                patches.append(PatchResult(target=target, action="DELETE"))
            elif action in ["COMMAND", "TERMINAL_COMMAND"]:
                patches.append(PatchResult(target=target, action="COMMAND", command=target))
                
        return patches


class PatchApplier:
    """
    Tugas: Menerapkan ApprovedPatch ke Filesystem.
    Mendukung:
    1. CREATE: Full file write
    2. MODIFY: Parse SEARCH/REPLACE blocks and apply them
    3. DELETE: Remove file
    """
    def __init__(self, cwd: str):
        self.cwd = cwd
        
    def _parse_search_replace_blocks(self, raw_content: str) -> List[SearchReplaceBlock]:
        """
        Parse SEARCH/REPLACE blocks from LLM output.
        Format:
        <<<< SEARCH
        ... original code ...
        ====
        ... new code ...
        >>>> REPLACE
        """
        blocks = []
        
        parts = raw_content.split("<<<< SEARCH")
        for part in parts[1:]:  # skip everything before first SEARCH
            if "====" in part and ">>>> REPLACE" in part:
                search_part, rest = part.split("====", 1)
                replace_part = rest.split(">>>> REPLACE", 1)[0]
                
                # Strip the leading/trailing newline added by the format
                search_str = search_part.strip("\n")
                replace_str = replace_part.strip("\n")
                
                blocks.append(SearchReplaceBlock(search=search_str, replace=replace_str))
                
        return blocks
        
    def _apply_search_replace(self, original: str, blocks: List[SearchReplaceBlock]) -> Tuple[bool, str]:
        """
        Apply SEARCH/REPLACE blocks to original content.
        Returns (success, new_content).
        """
        content = original
        
        for block in blocks:
            if block.search not in content:
                # Fuzzy fallback: try stripping leading/trailing whitespace on each line
                search_stripped = "\n".join(line.rstrip() for line in block.search.split("\n"))
                content_stripped = "\n".join(line.rstrip() for line in content.split("\n"))
                
                if search_stripped in content_stripped:
                    # Apply on the stripped version by finding the index
                    idx = content_stripped.find(search_stripped)
                    content = content[:idx] + block.replace + content[idx + len(search_stripped):]
                else:
                    print(f"[!] SEARCH block not found in file. Block preview: {block.search[:80]!r}")
                    return False, content
            else:
                content = content.replace(block.search, block.replace, 1)
                
        return True, content
        
    def _validate_python_syntax(self, content: str, filepath: str) -> Tuple[bool, str]:
        """
        Validate Python syntax if the file is a .py file.
        """
        if not filepath.endswith(".py"):
            return True, ""
            
        try:
            ast.parse(content)
            return True, ""
        except SyntaxError as e:
            return False, f"SyntaxError: {e}"
        
    def apply(self, patch: PatchResult) -> bool:
        target_path = os.path.join(self.cwd, patch.target)
        
        try:
            if patch.action == "CREATE":
                os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)
                # Validate syntax before writing
                valid, err = self._validate_python_syntax(patch.content, patch.target)
                if not valid:
                    print(f"[!] Syntax error in generated code for {patch.target}: {err}")
                    return False
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(patch.content)
                    
            elif patch.action == "MODIFY":
                # Ensure the file exists before modifying
                if not os.path.exists(target_path):
                    print(f"[!] ERROR: Target file for MODIFY does not exist: {patch.target}. Rejecting patch to prevent hallucinated files.")
                    return False
                    
                # Read original file
                with open(target_path, 'r', encoding='utf-8') as f:
                    original = f.read()
                        
                blocks = self._parse_search_replace_blocks(patch.content)
                
                if not blocks:
                    # No blocks found — fallback to full write ONLY if it's not a hallucinated file
                    print(f"[~] No SEARCH/REPLACE blocks found in {patch.target}. Falling back to full write.")
                    valid, err = self._validate_python_syntax(patch.content, patch.target)
                    if not valid:
                        print(f"[!] Syntax error in fallback write for {patch.target}: {err}")
                        return False
                    with open(target_path, 'w', encoding='utf-8') as f:
                        f.write(patch.content)
                else:
                    success, new_content = self._apply_search_replace(original, blocks)
                    if not success:
                        print(f"[!] SEARCH/REPLACE failed for {patch.target}.")
                        return False
                    valid, err = self._validate_python_syntax(new_content, patch.target)
                    if not valid:
                        print(f"[!] Syntax error after applying patch to {patch.target}: {err}")
                        return False
                    with open(target_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                        
            elif patch.action == "DELETE":
                if os.path.exists(target_path):
                    os.remove(target_path)
                    
            return True
        except Exception as e:
            print(f"[!] Gagal menerapkan patch ke {patch.target}: {e}")
            return False
