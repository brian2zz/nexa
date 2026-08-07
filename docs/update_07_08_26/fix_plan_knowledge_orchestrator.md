# Update 07 Agustus 2026: Rencana Perbaikan KnowledgeOrchestrator (WIP → Stable)

Dokumen ini adalah rencana eksekusi (*planning*) untuk menuntaskan pekerjaan WIP
commit `bc7d725` (*feat(ai): WIP implement KnowledgeOrchestrator and integrate cognitive engines*)
menjadi implementasi yang stabil, terverifikasi, dan siap di-push.

---

## 1. Latar Belakang

Commit `bc7d725` mengintegrasikan **Cognitive Pipeline** baru ke dalam `AIPlannerEngine`:

```
IntentResolver → Need[] → KnowledgeOrchestrator (evidence) → Hypothesis → Reasoning → Planning
```

Pipeline ini berjalan end-to-end (terverifikasi manual), namun masih berstatus **WIP** dan
belum diamankan oleh test yang benar-benar mengeksekusi tool sungguhan. Analisis menemukan
beberapa bug nyata yang **tidak tertangkap** oleh test suite yang ada.

## 2. Temuan Bug

### Bug 1: Tool dipanggil tapi tidak pernah didaftarkan (pasti gagal)

`KnowledgeOrchestrator._call_tool` (`nexa/core/ai/knowledge/orchestrator.py`) memanggil:

| Tool yang dipanggil | Status Registrasi |
| :--- | :--- |
| `file_lookup` | ✅ terdaftar |
| `file_read` | ✅ terdaftar |
| `read_symbol` | ✅ terdaftar |
| `content_search` | ✅ terdaftar |
| `git_status` | ✅ terdaftar |
| `git_diff` | ✅ terdaftar |
| `git_execute` | ✅ terdaftar |
| **`git_current_branch`** | ❌ **tidak terdaftar** |
| **`git_log`** | ❌ **tidak terdaftar** |
| **`file_tree`** | ❌ **tidak terdaftar** |

**Dampak terukur (verifikasi manual):**

```
satisfied: ['repository_status']
failed:    ['project_structure', 'git_history']
git status set: True
```

- `Need.PROJECT_STRUCTURE` → selalu gagal (tool `file_tree` hilang).
- `Need.GIT_HISTORY` → selalu gagal (tool `git_log` hilang).
- `Need.CURRENT_BRANCH` → selalu gagal (tool `git_current_branch` hilang).
- `Need.REPOSITORY_STATUS` → sukses sebagian (branch tidak pernah terisi).

**Akar masalah:** `nexa/core/agent/tools/knowledge/git.py` hanya meregistrasi
`git_status`, `git_diff`, `git_execute`. `nexa/core/agent/tools/knowledge/file.py`
tidak meregistrasi `file_tree` (metode `FileTool.tree()` sebenarnya sudah ada).

### Bug 2: Import mati (jejak WIP)

`nexa/core/ai/knowledge/orchestrator.py:56` melakukan:

```python
from nexa.core.agent.tools.git import register_git_tools
```

Modul `nexa.core.agent.tools.git` **tidak ada** (hanya `nexa.core.agent.tools.knowledge.git`).
Import ini tersembunyi oleh `try/except ImportError`, namun harus dibersihkan karena
mengacaukan kejelasan alur registrasi.

### Bug 3: Gap test (kenapa Bug 1 lolos)

Seluruh test yang ada (21 test) **mem-mock `ToolRegistry`**, sehingga tidak ada satu pun
test yang menjalankan `KnowledgeOrchestrator.gather()` dengan tool sungguhan. Akibatnya
tool yang tidak terdaftar tidak pernah terdeteksi.

## 3. Rencana Perbaikan

### Langkah 1 — Perbaiki registrasi tool

1. **`nexa/core/agent/tools/knowledge/git.py`**
   - Tambahkan tool `git_current_branch` (fungsi `GitTool.current_branch()` sudah ada).
   - Tambahkan tool `git_log` (baru, jalankan `git log --oneline -10`).
2. **`nexa/core/agent/tools/knowledge/file.py`**
   - Registrasi tool `file_tree` → `FileTool.tree`.
3. **`nexa/core/ai/knowledge/orchestrator.py`**
   - Hapus `_register_git_tools()` dan import mati `nexa.core.agent.tools.git`.
   - Pastikan pemanggilan `file_tree` konsisten (`registry.execute("file_tree", {"path": ...})`).
   - Rapikan bundle `PROJECT_FACTS` yang saat ini memakai `file_lookup` tanpa hint
     (rentan gagal).

### Langkah 2 — Tambah integration test (tool sungguhan)

Buat `tests/core/ai/knowledge/test_orchestrator_integration.py`:

- Setup temp workspace berisi `login.html` + inisialisasi git repo mini.
- Test `gather()` nyata untuk: `TEMPLATE_LOOKUP`, `FILE_CONTENT`, `PROJECT_STRUCTURE`,
  `REPOSITORY_STATUS`, `CURRENT_BRANCH`, `GIT_HISTORY`.
- Assert `needs_satisfied` berisi kebutuhan yang seharusnya sukses, dan
  `needs_failed` tidak berisi kebutuhan yang seharusnya sukses.

### Langkah 3 — Verifikasi

```bash
py -m pytest tests -q
```

Target: seluruh test (21 existing + test baru) hijau.

### Langkah 4 — Tuntaskan WIP & commit

- Commit: fix registrasi tool + integration test + `pytest.ini` + `tests/core/ai/`
  (masih untracked).
- Pekerjaan `bc7d725` dianggap selesai (label WIP dicabut setelah test hijau).

### Langkah 5 — (Opsional) Push

Push 5 commit (3 local + 2 baru) ke `origin/main`.

## 4. Di Luar Scope Rencana Ini

Hal-hal berikut **tidak** disentuh pada iterasi ini (bisa dijadwalkan terpisah):

- Penataan ulang dokumen `docs/` agar sinkron dengan status implementasi.
- `GitTool.execute()` menggunakan `shell=True` (potensi risiko keamanan).
- `SearchTool.text()` menggunakan `findstr` (Windows-only, belum cross-platform).
- Pembersihan `mock_project/.nexa/` yang masih ter-track di git.

## 5. Status

| Item | Status |
| :--- | :--- |
| Rencana disusun | ✅ 07 Agustus 2026 |
| Langkah 1: fix registrasi tool | ✅ Selesai |
| Langkah 2: integration test | ✅ Selesai |
| Langkah 3: verifikasi test | ✅ Selesai |
| Langkah 4: commit | ✅ Selesai |
| Langkah 5: push | ⏳ Menunggu User |
