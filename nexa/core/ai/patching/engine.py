import os
import hashlib
import time
import datetime
from typing import Optional, List, Tuple
from nexa.core.models.dto.patch import PatchRequest, PatchResult, PatchObject
from nexa.core.models.enums import Status, Operation
from nexa.core.models.events import EventContext
from nexa.core.events.bus import PipelineBus
from nexa.core.models.enums import EventPriority
from nexa.core.ai.patching.risk_analyzer import RiskAnalyzer

class PatchEngine:
    def __init__(self, bus: Optional[PipelineBus] = None):
        self.risk_analyzer = RiskAnalyzer()
        self.bus = bus

    def _hash_content(self, content: str) -> str:
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _read_file_safe(self, repo_root: str, target_file: str) -> Optional[str]:
        # Memastikan tidak ada Path Traversal
        abs_path = os.path.abspath(os.path.join(repo_root, target_file))
        if not abs_path.startswith(os.path.abspath(repo_root)):
            return None
        
        if os.path.exists(abs_path):
            with open(abs_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def calculate_patch(self, request: PatchRequest, session_id: str = "default_session") -> PatchResult:
        start_time = time.time()
        
        if self.bus:
            self.bus.publish(EventContext(
                event_name="BeforePatch",
                timestamp=datetime.datetime.now().isoformat(),
                source="PatchEngine",
                priority=EventPriority.NORMAL,
                session_id=session_id,
                payload={"target_files": request.target_files}
            ))
            
        generated_code = request.transformation_result.get("generated_code", "")
        patches: List[PatchObject] = []
        warnings = []
        
        # Murni demonstrasi parsing sederhana ala Search & Replace (Aider <<<< ==== >>>>)
        # Pada skenario nyata, ini harus menggunakan Regex atau parser blok yang jauh lebih robus.
        if "<<<<" in generated_code and "====" in generated_code and ">>>>" in generated_code:
            parts = generated_code.split("<<<<")
            for part in parts[1:]:
                if "====" not in part or ">>>>" not in part:
                    continue
                search_block = part.split("====")[0].strip()
                replace_block = part.split("====")[1].split(">>>>")[0].strip()
                
                # Asumsi satu file target (untuk MVP)
                target_file = request.target_files[0] if request.target_files else "unknown.py"
                old_content = self._read_file_safe(request.repository_root, target_file)
                
                if old_content is None:
                    warnings.append(f"File {target_file} tidak ditemukan di repository.")
                    continue
                    
                if search_block not in old_content:
                    warnings.append(f"Blok pencarian tidak ditemukan di {target_file}")
                    continue
                    
                new_content = old_content.replace(search_block, replace_block)
                
                patch_obj = PatchObject(
                    path=target_file,
                    operation=Operation.MODIFY,
                    old_hash=self._hash_content(old_content),
                    new_hash=self._hash_content(new_content),
                    old_content=search_block,
                    new_content=replace_block,
                    diff=f"- {search_block}\n+ {replace_block}",
                    summary="Modify block success"
                )
                patches.append(patch_obj)
        elif "@@ " in generated_code and ("-" in generated_code or "+" in generated_code):
            target_file = request.target_files[0] if request.target_files else "unknown.py"
            old_content = self._read_file_safe(request.repository_root, target_file)
            
            if old_content is None:
                warnings.append(f"File {target_file} tidak ditemukan di repository.")
            else:
                import re
                # Naive unified diff applier for MVP
                blocks = re.split(r"@@.*?@@", generated_code)
                headers = re.findall(r"@@.*?@@", generated_code)
                
                new_content = old_content
                # Sometimes split gives text before the first @@
                start_idx = 1 if len(blocks) > len(headers) else 0
                
                for i in range(len(headers)):
                    hunk_text = blocks[start_idx + i]
                    hunk_lines = hunk_text.split("\n")
                    
                    search_lines = []
                    replace_lines = []
                    
                    for line in hunk_lines:
                        if not line: continue
                        if line.startswith("-"): search_lines.append(line[1:])
                        elif line.startswith("+"): replace_lines.append(line[1:])
                        elif line.startswith(" "): 
                            search_lines.append(line[1:])
                            replace_lines.append(line[1:])
                            
                    search_block = "\n".join(search_lines).strip()
                    replace_block = "\n".join(replace_lines).strip()
                    
                    if search_block and search_block in new_content:
                        new_content = new_content.replace(search_block, replace_block)
                    elif search_block:
                        # Try a looser match (ignore whitespace)
                        new_content = new_content.replace(search_block.replace("\r", ""), replace_block.replace("\r", ""))
                        warnings.append("Hunk matched with whitespace relaxation.")
                
                patch_obj = PatchObject(
                    path=target_file,
                    operation=Operation.MODIFY,
                    old_hash=self._hash_content(old_content),
                    new_hash=self._hash_content(new_content),
                    old_content="[Hunks applied]",
                    new_content=new_content,
                    diff="[Unified Diff Patch Applied]",
                    summary="Unified diff applied"
                )
                patches.append(patch_obj)
        else:
            # Fallback jika hanya mengembalikan full file
            target_file = request.target_files[0] if request.target_files else "unknown.py"
            old_content = self._read_file_safe(request.repository_root, target_file)
            
            if old_content is not None:
                patch_obj = PatchObject(
                    path=target_file,
                    operation=Operation.MODIFY,
                    old_hash=self._hash_content(old_content),
                    new_hash=self._hash_content(generated_code),
                    old_content=old_content,
                    new_content=generated_code,
                    diff="[Full File Replacement]",
                    summary="Full file replacement"
                )
                patches.append(patch_obj)

        # C.4: Validasi AST untuk file Python
        valid_patches = []
        for p in patches:
            if p.path.endswith('.py') and p.new_content:
                try:
                    import ast
                    ast.parse(p.new_content)
                    valid_patches.append(p)
                except SyntaxError as e:
                    warnings.append(f"AST Validation Error on {p.path}: {str(e)}")
            else:
                valid_patches.append(p)
        patches = valid_patches

        if not patches:
            duration = time.time() - start_time
            if self.bus:
                self.bus.publish(EventContext(
                    event_name="PatchFailed",
                    timestamp=datetime.datetime.now().isoformat(),
                    source="PatchEngine",
                    priority=EventPriority.HIGH,
                    session_id=session_id,
                    duration=duration,
                    payload={"warnings": warnings}
                ))
                
            return PatchResult(
                success=False,
                status=Status.FAILED,
                summary="Gagal mengalkulasi patch. Format LLM tidak dikenali.",
                warnings=warnings
            )

        # Hitung risiko menggunakan RiskAnalyzer
        analysis = self.risk_analyzer.analyze(patches)
        
        # Hitung baris additions/deletions kasar
        additions = sum(p.new_content.count('\n') if p.new_content else 0 for p in patches)
        deletions = sum(p.old_content.count('\n') if p.old_content else 0 for p in patches)

        result = PatchResult(
            success=True,
            status=Status.SUCCESS,
            patches=patches,
            analysis=analysis,
            summary=f"Berhasil membuat {len(patches)} patch.",
            additions=additions,
            deletions=deletions,
            warnings=warnings
        )
        
        duration = time.time() - start_time
        
        if self.bus:
            self.bus.publish(EventContext(
                event_name="AfterPatch",
                timestamp=datetime.datetime.now().isoformat(),
                source="PatchEngine",
                priority=EventPriority.NORMAL,
                session_id=session_id,
                duration=duration,
                payload={
                    "additions": additions,
                    "deletions": deletions,
                    "risk_score": analysis.risk_score,
                    "risk_level": analysis.risk_level.value
                }
            ))
        return result
