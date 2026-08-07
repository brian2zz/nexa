"""
Need — Deklarasi Kebutuhan Semantik Nexa AI

Need adalah unit kebutuhan yang paling fundamental.
IntentResolver menghasilkan Need[], bukan tools.
CapabilityResolver memetakan Need ke ToolBundle.

Filosofi: "Planner berkata: Saya butuh REPOSITORY_STATUS.
           Knowledge Orchestrator yang tahu cara mendapatkannya."
"""

from enum import Enum, auto


class Need(str, Enum):
    """
    Semua kebutuhan semantik yang bisa dimiliki oleh sebuah Intent.
    Bersifat deklaratif — tidak menyebut nama tool satupun.
    """

    # --- Git / Version Control ---
    REPOSITORY_STATUS   = "repository_status"    # Status repo: staged, unstaged, untracked
    CODE_DIFF           = "code_diff"             # Diff perubahan kode
    GIT_HISTORY         = "git_history"           # Riwayat commit
    CURRENT_BRANCH      = "current_branch"        # Nama branch aktif

    # --- File System ---
    FILE_CONTENT        = "file_content"          # Isi lengkap sebuah file
    FILE_LOOKUP         = "file_lookup"           # Cari file berdasarkan nama/ekstensi
    PROJECT_STRUCTURE   = "project_structure"     # Struktur folder/direktori proyek

    # --- Code Intelligence ---
    SYMBOL_DEFINITION   = "symbol_definition"     # Definisi class/function/method
    CONTENT_SEARCH      = "content_search"        # Pencarian teks di seluruh codebase

    # --- Frontend / Template ---
    TEMPLATE_LOOKUP     = "template_lookup"       # Cari template HTML/Jinja
    CSS_INSPECTION      = "css_inspection"        # Inspeksi penggunaan CSS class
    STATIC_ASSETS       = "static_assets"         # Cari file CSS/JS/gambar

    # --- Database / Model ---
    MODEL_DEFINITION    = "model_definition"      # Definisi model database
    MIGRATION_STATUS    = "migration_status"      # Status migrasi Django/Laravel

    # --- General ---
    PROJECT_FACTS       = "project_facts"         # Fakta proyek (bahasa, framework, dsb)
