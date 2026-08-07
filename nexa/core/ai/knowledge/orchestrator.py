"""
KnowledgeOrchestrator — Satu-satunya Komponen yang Boleh Memanggil Tool

Filosofi Inti:
  - Planner tidak pernah memanggil tool.
  - Reasoning tidak pernah memanggil tool.
  - Hypothesis tidak pernah memanggil tool.
  - HANYA KnowledgeOrchestrator yang boleh memanggil tool.

Alur:
  Need[] ──► CapabilityResolver ──► ToolBundle[]
                                          │
                                    [Tool Budget = 5]
                                          │
                                   Execute Tools
                                          │
                                   EvidenceBundle ──► Reasoning ──► Planning

Tentang Tool Budget:
  Setiap bundle menghabiskan 1 unit budget.
  Jika budget habis, Orchestrator berhenti dan menyerahkan
  evidence yang sudah terkumpul kepada Planner (walaupun tidak lengkap).
  Ini mencegah loop tak terbatas.
"""

import json
from typing import List, Optional
from nexa.core.ai.knowledge.need import Need
from nexa.core.ai.knowledge.bundle import get_bundles
from nexa.core.ai.knowledge.evidence import (
    EvidenceBundle, FileEvidence, SymbolEvidence, SearchEvidence, GitEvidence
)
from nexa.core.agent.tools.registry import ToolRegistry
from nexa.core.agent.tools.knowledge import register_knowledge_tools

TOOL_BUDGET = 5  # Max bundle calls per siklus


class KnowledgeOrchestrator:
    """
    Mengorkestrasi seluruh proses pengumpulan pengetahuan.
    Menerima Need[] → mengeksekusi ToolBundle[] → menghasilkan EvidenceBundle.
    """

    def __init__(self, workspace_path: str, tool_budget: int = TOOL_BUDGET):
        self.workspace_path = workspace_path
        self.tool_budget = tool_budget
        self.registry = ToolRegistry()
        register_knowledge_tools(self.registry, workspace_path)


    def gather(self, needs: List[Need], context_hints: dict = None) -> EvidenceBundle:
        """
        Entry point utama.
        Menerima Need[] dan menghasilkan EvidenceBundle yang terstruktur.
        """
        bundle = EvidenceBundle(
            needs_requested=[n.value for n in needs],
            tool_budget=self.tool_budget
        )

        # Deduplicate dan urutkan bundles
        bundle_plan = get_bundles(needs)
        budget_remaining = self.tool_budget

        for need, tool_bundle, unique_tools in bundle_plan:
            if budget_remaining <= 0:
                print(f"       [Orchestrator] [!] Tool Budget habis ({self.tool_budget}). Berhenti.")
                bundle.needs_failed.append(need.value)
                continue

            # Jalankan semua tool dalam bundle sekaligus
            success = self._execute_bundle(need, unique_tools, bundle, context_hints or {})

            if success:
                bundle.needs_satisfied.append(need.value)
            else:
                bundle.needs_failed.append(need.value)

            bundle.tool_calls_used += tool_bundle.budget_cost
            budget_remaining -= tool_bundle.budget_cost

        return bundle

    def _execute_bundle(self, need: Need, tool_names: List[str], bundle: EvidenceBundle, hints: dict) -> bool:
        """
        Eksekusi satu bundle (kumpulan tool untuk satu Need).
        Menulis hasilnya langsung ke EvidenceBundle.
        Returns True jika setidaknya satu tool berhasil.
        """
        any_success = False

        for tool_name in tool_names:
            try:
                result = self._call_tool(tool_name, need, hints)
                if result and "Error" not in str(result)[:50]:
                    self._write_to_bundle(need, tool_name, result, bundle, hints)
                    any_success = True
            except Exception as e:
                print(f"       [Orchestrator] Tool '{tool_name}' gagal: {e}")

        return any_success

    def _call_tool(self, tool_name: str, need: Need, hints: dict) -> Optional[str]:
        """
        Panggil tool dengan argumen yang dibangun dari Need dan context hints.
        Argumen ditentukan secara DETERMINISTIK berdasarkan Need, bukan LLM.
        """
        # --- Git tools ---
        if tool_name == "git_status":
            return self.registry.execute("git_status", {})
        elif tool_name == "git_current_branch":
            return self.registry.execute("git_current_branch", {})
        elif tool_name == "git_diff":
            return self.registry.execute("git_diff", {"stat_only": False})
        elif tool_name == "git_log":
            return self.registry.execute("git_log", {"limit": 10})

        # --- File tools ---
        elif tool_name == "file_read":
            filepath = hints.get("file_path", hints.get("target_file", ""))
            if not filepath:
                return None
            return self.registry.execute("file_read", {"filepath": filepath})

        elif tool_name == "file_lookup":
            # Untuk template: cari .html, untuk model: cari .py
            if need in (Need.TEMPLATE_LOOKUP, Need.STATIC_ASSETS):
                ext = hints.get("extension", ".html")
                name = hints.get("template_name", hints.get("file_name", ""))
                return self.registry.execute("file_lookup", {"extension": ext, "name": name})
            elif need in (Need.MODEL_DEFINITION, Need.MIGRATION_STATUS):
                return self.registry.execute("file_lookup", {"extension": ".py", "name": hints.get("model_name", "")})
            else:
                name = hints.get("file_name", hints.get("target_file", ""))
                ext = hints.get("extension", "")
                return self.registry.execute("file_lookup", {"name": name, "extension": ext})

        elif tool_name == "file_tree":
            path = hints.get("tree_path", ".")
            return self.registry.execute("file_tree", {"path": path})

        # --- Code intelligence ---
        elif tool_name == "read_symbol":
            symbol = hints.get("symbol_name", hints.get("class_name", hints.get("function_name", "")))
            if not symbol:
                return None
            return self.registry.execute("read_symbol", {"symbol_name": symbol})

        elif tool_name == "content_search":
            query = hints.get("search_query", hints.get("css_class", hints.get("keyword", "")))
            if not query:
                return None
            path = hints.get("search_path", ".")
            return self.registry.execute("content_search", {"query": query, "path": path})

        return None

    def _write_to_bundle(self, need: Need, tool_name: str, result: str, bundle: EvidenceBundle, hints: dict):
        """Tulis hasil tool ke slot yang tepat di EvidenceBundle."""
        # --- Git ---
        if tool_name == "git_status":
            bundle.git.status = str(result)
        elif tool_name == "git_current_branch":
            bundle.git.current_branch = str(result).strip()
        elif tool_name == "git_diff":
            full = str(result)
            bundle.git.diff_full = full
            # Generate summary (first ~500 chars of diff as "summary")
            bundle.git.diff_summary = full[:500] if len(full) > 500 else full
        elif tool_name == "git_log":
            bundle.git.recent_commits = str(result)

        # --- File ---
        elif tool_name == "file_read":
            content = str(result)
            truncated = len(content) > 5000
            bundle.files.append(FileEvidence(
                path=hints.get("file_path", hints.get("target_file", "unknown")),
                content=content[:5000],
                size_bytes=len(content),
                truncated=truncated
            ))

        elif tool_name == "file_lookup":
            # file_lookup mengembalikan JSON list of paths
            try:
                paths = json.loads(result) if isinstance(result, str) else result
                if isinstance(paths, list) and paths:
                    # Ambil file pertama yang relevan dan baca isinya
                    target = paths[0] if isinstance(paths[0], str) else str(paths[0])
                    content = self.registry.execute("file_read", {"filepath": target})
                    if content and "Error" not in str(content)[:50]:
                        truncated = len(content) > 5000
                        bundle.files.append(FileEvidence(
                            path=target,
                            content=str(content)[:5000],
                            size_bytes=len(str(content)),
                            truncated=truncated
                        ))
            except Exception:
                pass

        # --- Code Intelligence ---
        elif tool_name == "read_symbol":
            try:
                data = json.loads(result) if isinstance(result, str) else result
                if isinstance(data, list):
                    for sym in data:
                        bundle.symbols.append(SymbolEvidence(
                            name=sym.get("name", ""),
                            type=sym.get("type", "unknown"),
                            file=sym.get("file", ""),
                            start_line=sym.get("lines", [0, 0])[0],
                            end_line=sym.get("lines", [0, 0])[1],
                            code=sym.get("code", "")[:1500]
                        ))
            except Exception:
                pass

        elif tool_name == "content_search":
            query = hints.get("search_query", hints.get("css_class", hints.get("keyword", "")))
            result_str = str(result)
            # Parse simple line-based results
            matches = []
            for line in result_str.split("\n")[:20]:
                if ":" in line:
                    parts = line.split(":", 2)
                    if len(parts) >= 2:
                        matches.append({
                            "file": parts[0].strip(),
                            "line": parts[1].strip() if len(parts) > 2 else "",
                            "content": parts[-1].strip()
                        })
            bundle.searches.append(SearchEvidence(
                query=query,
                matches=matches,
                total_matches=len(matches)
            ))


class CapabilityResolver:
    """
    Memetakan Need[] ke konteks hints yang diperlukan.
    Dipanggil sebelum KnowledgeOrchestrator.gather() untuk
    memperkaya hints dari user_goal.
    """

    @staticmethod
    def build_hints(user_goal: str, needs: List[Need], project_facts: dict = None) -> dict:
        """
        Ekstrak hints dari user_goal secara deterministik (regex/keyword).
        Hints dipakai oleh tool dalam setiap bundle.
        """
        import re
        hints = {}
        goal_lower = user_goal.lower()

        # File path: deteksi jika ada path di goal/clarification
        path_match = re.search(r'(modules?/[\w/.-]+\.(?:html|py|js|css))', user_goal)
        if path_match:
            hints["file_path"] = path_match.group(1)
            hints["target_file"] = path_match.group(1)

        # Template name hint
        if Need.TEMPLATE_LOOKUP in needs or Need.CSS_INSPECTION in needs:
            hints["extension"] = ".html"
            # Cari nama template dari goal
            tpl_match = re.search(r'\b(\w+\.html)\b', user_goal)
            if tpl_match:
                hints["template_name"] = tpl_match.group(1)

        # CSS class hint
        css_match = re.search(r'\b(btn-\w+|[\w-]+-\w+)\b', user_goal)
        if css_match:
            hints["css_class"] = css_match.group(1)
            hints["search_query"] = css_match.group(1)

        # Symbol/class hint
        sym_match = re.search(r'\b([A-Z][a-zA-Z]+(?:View|Model|Manager|Engine|Service|Controller|Repository))\b', user_goal)
        if sym_match:
            hints["symbol_name"] = sym_match.group(1)

        # Keyword search
        kw_match = re.search(r'\b(?:cari|temukan|search|find)\s+["\']?([^"\']+)["\']?', goal_lower)
        if kw_match:
            hints["keyword"] = kw_match.group(1).strip()
            hints["search_query"] = kw_match.group(1).strip()

        # Dari clarification block [User Clarification]
        if "[User Clarification]" in user_goal:
            clar_section = user_goal.split("[User Clarification]")[1]
            for line in clar_section.strip().split("\n"):
                line = line.strip().lstrip("- ")
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip().lower().replace(" ", "_")
                    val = val.strip()
                    if key == "button_location" or key == "template_path":
                        hints["file_path"] = val
                        hints["target_file"] = val
                    elif key == "color_target":
                        hints["search_query"] = val
                        hints["css_class"] = val
                    elif key == "change_detail":
                        # "dari btn-primary ke btn-success"
                        change_match = re.search(r'(btn-\w+)', val)
                        if change_match:
                            hints["search_query"] = change_match.group(1)

        return hints
