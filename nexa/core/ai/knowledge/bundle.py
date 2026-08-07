"""
ToolBundle — Pemetaan Deterministik Need → Kumpulan Tool

Setiap Need dipetakan ke satu ToolBundle yang berisi daftar
nama tool yang harus dijalankan secara bersamaan (satu bundle = sekali jalan).

Tidak ada LLM yang memilih tool. Semua deterministik.

Filosofi: "Need.REPOSITORY_STATUS selalu berarti: jalankan git_status,
           git_diff_stat, dan git_current_branch. Tidak ada negosiasi."
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from nexa.core.ai.knowledge.need import Need


@dataclass
class ToolBundle:
    """
    Satu bundle = satu Need = beberapa tool dijalankan sekaligus.
    Setiap tool di dalam bundle hanya dihitung 1 kali dari Tool Budget.
    (Bukan per-tool, tapi per-bundle).
    """
    name: str
    tool_names: List[str]
    description: str = ""
    budget_cost: int = 1  # Berapa unit budget yang dipakai oleh bundle ini


# ===================================================================
# REGISTRY BUNDLE — Peta lengkap Need → ToolBundle
# ===================================================================

BUNDLE_REGISTRY: Dict[Need, ToolBundle] = {

    # --- Git ---
    Need.REPOSITORY_STATUS: ToolBundle(
        name="Git Repository Status",
        description="Mengambil status repository, branch aktif, dan ringkasan perubahan",
        tool_names=["git_status", "git_current_branch"],
        budget_cost=1,
    ),
    Need.CODE_DIFF: ToolBundle(
        name="Code Diff Analysis",
        description="Mengambil diff lengkap dan statistik perubahan",
        tool_names=["git_diff"],
        budget_cost=1,
    ),
    Need.GIT_HISTORY: ToolBundle(
        name="Git History",
        description="Mengambil riwayat commit terbaru",
        tool_names=["git_log"],
        budget_cost=1,
    ),
    Need.CURRENT_BRANCH: ToolBundle(
        name="Current Branch",
        description="Mengambil nama branch Git yang aktif",
        tool_names=["git_current_branch"],
        budget_cost=1,
    ),

    # --- File System ---
    Need.FILE_CONTENT: ToolBundle(
        name="File Content Reader",
        description="Membaca isi file dari filesystem",
        tool_names=["file_read"],
        budget_cost=1,
    ),
    Need.FILE_LOOKUP: ToolBundle(
        name="File Lookup",
        description="Mencari file berdasarkan nama atau ekstensi",
        tool_names=["file_lookup"],
        budget_cost=1,
    ),
    Need.PROJECT_STRUCTURE: ToolBundle(
        name="Project Structure",
        description="Mendapatkan gambaran struktur direktori proyek",
        tool_names=["file_tree"],
        budget_cost=1,
    ),

    # --- Code Intelligence ---
    Need.SYMBOL_DEFINITION: ToolBundle(
        name="Symbol Definition",
        description="Mencari definisi class, function, atau method di AST index",
        tool_names=["read_symbol"],
        budget_cost=1,
    ),
    Need.CONTENT_SEARCH: ToolBundle(
        name="Content Search",
        description="Pencarian teks/pattern di seluruh codebase",
        tool_names=["content_search"],
        budget_cost=1,
    ),

    # --- Frontend / Template ---
    Need.TEMPLATE_LOOKUP: ToolBundle(
        name="Template Lookup",
        description="Mencari file template HTML berdasarkan nama atau path",
        tool_names=["file_lookup", "content_search"],
        budget_cost=1,
    ),
    Need.CSS_INSPECTION: ToolBundle(
        name="CSS Class Inspection",
        description="Mencari penggunaan class CSS di template dan stylesheet",
        tool_names=["content_search"],
        budget_cost=1,
    ),
    Need.STATIC_ASSETS: ToolBundle(
        name="Static Assets Lookup",
        description="Mencari file CSS, JS, atau gambar di direktori static",
        tool_names=["file_lookup"],
        budget_cost=1,
    ),

    # --- Database / Model ---
    Need.MODEL_DEFINITION: ToolBundle(
        name="Model Definition",
        description="Mencari definisi model database dari AST index",
        tool_names=["read_symbol", "file_lookup"],
        budget_cost=1,
    ),
    Need.MIGRATION_STATUS: ToolBundle(
        name="Migration Status",
        description="Memeriksa status dan file migrasi",
        tool_names=["file_lookup", "content_search"],
        budget_cost=1,
    ),

    # --- General ---
    Need.PROJECT_FACTS: ToolBundle(
        name="Project Facts",
        description="Mengumpulkan fakta umum tentang proyek (bahasa, framework, dsb)",
        tool_names=["file_lookup"],
        budget_cost=1,
    ),
}


def get_bundle(need: Need) -> Optional[ToolBundle]:
    """Ambil ToolBundle untuk sebuah Need. Returns None jika tidak ada mapping."""
    return BUNDLE_REGISTRY.get(need)


def get_bundles(needs: List[Need]) -> List[tuple]:
    """
    Ambil semua ToolBundle untuk daftar Need.
    Returns list of (Need, ToolBundle) tuple.
    Deduplicates tool_names yang sama antar bundle.
    """
    result = []
    seen_tools = set()
    for need in needs:
        bundle = get_bundle(need)
        if bundle:
            # Filter tool yang sudah akan dijalankan bundle sebelumnya
            unique_tools = [t for t in bundle.tool_names if t not in seen_tools]
            seen_tools.update(bundle.tool_names)
            if unique_tools:
                result.append((need, bundle, unique_tools))
    return result
