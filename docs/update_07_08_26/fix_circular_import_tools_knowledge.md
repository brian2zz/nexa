# Rencana Perbaikan: Circular Import `agent.tools.knowledge` ↔ `ai.knowledge`

*Status: Artefact Perencanaan — 07 Agustus 2026*

Dokumen ini mendokumentasikan **bug circular import** yang ditemukan saat
verifikasi perubahan working-tree Phase 5 (Tahap C.1/C.2 — Call Graph &
Semantic Cache). Berisi: apa bug-nya, bagaimana mereproduksinya, rantai siklus
yang persis, akar masalah arsitektural, apa yang diperbaiki, dan bagaimana
seharusnya struktur import yang benar.

---

## 1. Ringkasan Bug

**Gejala:**
```
ImportError: cannot import name 'register_knowledge_tools' from partially
initialized module 'nexa.core.agent.tools.knowledge'
(most likely due to a circular import)
```

Muncul saat mengimpor **sisi tools** terlebih dahulu:
```bash
py -X utf8 -c "from nexa.core.agent.tools.knowledge.file import FileTool"
```

**Sifat bug: TIDAK KONSISTEN (bergantung urutan import).**
Berikut sukses tanpa error:
```bash
py -X utf8 -c "import nexa.core.ai.knowledge"                       # OK
py -X utf8 -c "from nexa.core.ai.knowledge.orchestrator import KnowledgeOrchestrator"  # OK
```
Ini karena `knowledge/__init__.py` menjalankan baris 14 (import orchestrator)
**sebelum** ada yang menyentuh sisi tools, sehingga rantai selesai diload dulu.

Tes suite 23/23 tetap hijau **hanya karena tidak ada test yang mengimpor
`file.py`/`tools.knowledge` secara langsung** — bug sedang menunggu ledakan di
jalur mana pun yang kebetulan mengimpor `FileTool` lebih dulu (mis. sesi shell
baru, tool lain, atau test baru).

---

## 2. Reproduksi

```bash
cd "G:\project code\nexa"
$env:PYTHONIOENCODING='utf-8'
py -X utf8 -c "from nexa.core.agent.tools.knowledge.file import FileTool; print('OK')"
```

Hasil:
```
  File "...\nexa\core\agent\tools\knowledge\file.py", line 4, in <module>
    from nexa.core.ai.knowledge.cache.sqlite import SQLiteCache
  File "...\nexa\core\ai\knowledge\__init__.py", line 14, in <module>
    from nexa.core.ai.knowledge.orchestrator import KnowledgeOrchestrator, CapabilityResolver
  File "...\nexa\core\ai\knowledge\orchestrator.py", line 34, in <module>
    from nexa.core.agent.tools.knowledge import register_knowledge_tools
ImportError: cannot import name 'register_knowledge_tools' from partially
initialized module 'nexa.core.agent.tools.knowledge'
```

---

## 3. Rantai Circular Import (Persis)

```
[1] tools/knowledge/__init__.py:1
      from nexa.core.agent.tools.knowledge.file import FileTool
      │
[2]   file.py:4
      from nexa.core.ai.knowledge.cache.sqlite import SQLiteCache
      │
[3]      ← memicu load PACKAGE nexa.core.ai.knowledge
         ai/knowledge/__init__.py:14
         from nexa.core.ai.knowledge.orchestrator import KnowledgeOrchestrator, CapabilityResolver
         │
[4]         orchestrator.py:34
            from nexa.core.agent.tools.knowledge import register_knowledge_tools
            │
            ← tools/knowledge MASIH partially-initialized (belum selesai baris 1)
            → register_knowledge_tools BELUM terdefinisi → ImportError 💥
```

**Pemicu utama:** `ai/knowledge/__init__.py` mengimpor `orchestrator` di
top-level (baris 14), dan `orchestrator.py` mengimpor `agent.tools.knowledge`
di top-level (baris 34). Sementara `file.py` (anak `tools.knowledge`) menarik
balik import ke `ai.knowledge` (baris 4). Siklus antar-package:

```
ai.knowledge ──(import)──► orchestrator ──(import)──► agent.tools.knowledge
      ▲                                                        │
      └──────────(file.py:4 import cache.sqlite)──────────────┘
```

Jika load dimulai dari **sisi kanan** (tools), Python belum selesai mengisi
`tools.knowledge`, lalu `knowledge/__init__.py` menuntut `register_knowledge_tools`
→ crash. Jika dimulai dari **sisi kiri** (ai.knowledge), urutan menang.

---

## 4. Akar Masalah Arsitektural

| Lapisan | Isi | Kewajiban |
| :--- | :--- | :--- |
| `ai.knowledge` (atas) | `orchestrator`, `cache`, `summarizer`, `dependency` | Boleh mengimpor lapisan di bawahnya |
| `agent.tools.knowledge` (bawah) | `FileTool`, `SearchTool`, registry | **TIDAK boleh** mengimpor ke lapisan di atasnya |

Pelanggaran yang terjadi:
1. `file.py:4` — lapisan bawah `agent.tools` mengimpor `ai.knowledge.cache.sqlite`
   (ke arah atas) → inilah yang "menjembatani" siklus.
2. `ai/knowledge/__init__.py:14` — package `__init__` menarik seluruh dependency
   graph (orchestrator → tools) saat module itu sendiri diload. Ini membuat
   package `ai.knowledge` menjadi *bottleneck* yang wajib di-load penuh.
3. `orchestrator.py:34` — impor top-level dari package lain yang berada tepat
   di ujung siklus.

Circular import adalah gejala dari pelanggaran arah dependensi ini.

---

## 5. Apa yang Diperbaiki

Perbaikan bertumpu pada **memutus siklus di sumber** dengan *lazy import*
(impor di dalam method, bukan top-level) dan **membuat package `__init__.py`
tidak menarik dependency graph penuh**.

### 5.1 `nexa/core/agent/tools/knowledge/file.py`

**Sebelum (top-level — penyebab siklus):**
```python
import os
import json
from nexa.core.agent.indexer import WorkspaceIndexer
from nexa.core.ai.knowledge.cache.sqlite import SQLiteCache   # ← baris 4 memicu cycle
from nexa.core.ai.knowledge.summarizer import RegexSummarizer
from nexa.core.ai.knowledge.dependency import DependencyParser

class FileTool:
    def __init__(self, workspace_path: str, cache=None):
        ...
        if cache:
            self.cache = cache
        else:
            db_path = os.path.join(workspace_path, ".nexa_cache.db")
            self.cache = SQLiteCache(db_path=db_path)          # ← pakai di runtime
```

**Sesudah (lazy import hanya saat dibutuhkan):**
```python
import os
import json
from nexa.core.agent.indexer import WorkspaceIndexer

class FileTool:
    def __init__(self, workspace_path: str, cache=None):
        ...
        if cache:
            self.cache = cache
        else:
            from nexa.core.ai.knowledge.cache.sqlite import SQLiteCache
            db_path = os.path.join(workspace_path, ".nexa_cache.db")
            self.cache = SQLiteCache(db_path=db_path)
```

**Alasan:** saat `tools/knowledge/__init__.py` diload, `file.py` tidak lagi
menarik `ai.knowledge` sama sekali. Import `SQLiteCache` baru dieksekusi saat
`FileTool(...)` di-instantiate — yaitu setelah seluruh package selesai diload.
Siklus pada rantai [2]→[3]→[4] terputus.

*(Catatan: `RegexSummarizer` & `DependencyParser` masih top-level — keduanya
tidak memicu siklus karena tidak mengimpor `orchestrator`/`tools`; mereka aman.
Bila ingin benar-benar bersih sesuai prinsip lapisan, ketiganya bisa dipindah
ke lazy, tapi bukan syarat mematikan cycle ini.)*

### 5.2 `nexa/core/ai/knowledge/__init__.py`

**Sebelum:**
```python
from nexa.core.ai.knowledge.need import Need
from nexa.core.ai.knowledge.evidence import EvidenceBundle
from nexa.core.ai.knowledge.orchestrator import KnowledgeOrchestrator, CapabilityResolver

__all__ = ["Need", "EvidenceBundle", "KnowledgeOrchestrator", "CapabilityResolver"]
```

**Sesudah (lazy ekspor via PEP 562 `__getattr__`):**
```python
from nexa.core.ai.knowledge.need import Need
from nexa.core.ai.knowledge.evidence import EvidenceBundle

def __getattr__(name):
    if name in {"KnowledgeOrchestrator", "CapabilityResolver"}:
        from nexa.core.ai.knowledge.orchestrator import (
            KnowledgeOrchestrator, CapabilityResolver
        )
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["Need", "EvidenceBundle", "KnowledgeOrchestrator", "CapabilityResolver"]
```

**Alasan:** mengimpor `nexa.core.ai.knowledge` (atau submodul mana pun seperti
`cache.sqlite`) kini TIDAK lagi memaksa load `orchestrator` (dan dengan
sendirinya `agent.tools.knowledge`). Ekspor tetap tersedia untuk kode pemakai
(`from nexa.core.ai.knowledge import KnowledgeOrchestrator`) tanpa membuat
package `__init__` menjadi bottleneck.

### 5.3 `nexa/core/ai/knowledge/orchestrator.py` (opsional — pengaman lapisan)

**Sebelum:**
```python
from nexa.core.agent.tools.registry import ToolRegistry
from nexa.core.agent.tools.knowledge import register_knowledge_tools
from nexa.core.ai.knowledge.cache.sqlite import SQLiteCache
import os
```

**Sesudah (lazy `register_knowledge_tools` — di dalam `__init__`):**
```python
from nexa.core.agent.tools.registry import ToolRegistry
from nexa.core.ai.knowledge.cache.sqlite import SQLiteCache
import os

class KnowledgeOrchestrator:
    def __init__(self, workspace_path: str, tool_budget: int = TOOL_BUDGET):
        self.workspace_path = workspace_path
        self.tool_budget = tool_budget
        self.registry = ToolRegistry()
        from nexa.core.agent.tools.knowledge import register_knowledge_tools
        db_path = os.path.join(workspace_path, ".nexa_cache.db")
        self.cache = SQLiteCache(db_path=db_path)
        register_knowledge_tools(self.registry, workspace_path, cache=self.cache)
```

**Alasan:** defensif ganda. Dengan 5.1 + 5.2 siklus sudah putus; 5.3 membuat
`orchestrator` tidak lagi membawa dependensi `agent.tools` saat diload,
sehingga `from nexa.core.ai.knowledge.orchestrator import KnowledgeOrchestrator`
berjalan aman dalam urutan import apa pun.

---

## 6. Seharusnya Seperti Apa (Prinsip + Desain Final)

### 6.1 Grafik dependensi yang benar

```
agent.tools.knowledge  (lapisan bawah, tidak mengimpor ke atas)
   file.py ───────────► ai.knowledge.cache / summarizer / dependency
                              (hanya saat instantiate, lazy OK)
                                        │
ai.knowledge ────────► orchestrator ───► agent.tools.knowledge (via runtime)
                                        │
                               (package __init__ ringan: hanya Need & Evidence)
```

Aturan yang ditegakkan:
1. **Tidak ada import top-level yang menyeberang dari `agent.*` ke `ai.*`**
   — kalau mau, harus lazy (di dalam method).
2. **`package/__init__.py` tidak mengimpor objek yang menarik seluruh
   dependency graph.** `ai/knowledge/__init__.py` hanya mengekspor
   `Need`/`EvidenceBundle` secara eager; `KnowledgeOrchestrator` via `__getattr__`.
3. **Arah dependensi satu arah:** `ai.*` boleh memakai `agent.tools.*`; arah
   sebaliknya dilarang. `FileTool` menerima `cache` lewat constructor (injection)
   dari `orchestrator` — bukan mengimpor langsung.

### 6.2 Hasil akhir yang diharapkan

```bash
# Semua jalur import harus sukses, urutan apa pun:
py -X utf8 -c "import nexa.core.ai.knowledge"
py -X utf8 -c "from nexa.core.ai.knowledge import KnowledgeOrchestrator, CapabilityResolver"
py -X utf8 -c "from nexa.core.ai.knowledge.orchestrator import KnowledgeOrchestrator"
py -X utf8 -c "from nexa.core.agent.tools.knowledge import register_knowledge_tools"
py -X utf8 -c "from nexa.core.agent.tools.knowledge.file import FileTool"
py -X utf8 -c "from nexa.core.ai.knowledge.cache.sqlite import SQLiteCache"
```

### 6.3 Test regresi yang harus ditambahkan

`tests/core/agent/tools/knowledge/test_import_order.py` — menguji bahwa
kelima jalur import di atas tidak crash, **dieksekusi sebagai subprocess
terpisah** (urutan `sys.modules` bersih setiap kali) supaya circular import
benar-benar terdeteksi:

```python
import subprocess, sys

CASES = [
    "import nexa.core.ai.knowledge",
    "from nexa.core.ai.knowledge import KnowledgeOrchestrator, CapabilityResolver",
    "from nexa.core.ai.knowledge.orchestrator import KnowledgeOrchestrator",
    "from nexa.core.agent.tools.knowledge import register_knowledge_tools",
    "from nexa.core.agent.tools.knowledge.file import FileTool",
    "from nexa.core.ai.knowledge.cache.sqlite import SQLiteCache",
]

def test_import_orders_do_not_circular_import():
    for stmt in CASES:
        r = subprocess.run(
            [sys.executable, "-X", "utf8", "-c", stmt],
            capture_output=True, text=True,
            cwd=PROJECT_ROOT,
        )
        assert r.returncode == 0, f"{stmt} FAILED:\n{r.stderr}"
```

*(tanpa `-cwd` perlu disesuaikan — versi final memakai path absolut project
dan memastikan `nexa` ada di `PYTHONPATH`.)*

---

## 7. Verifikasi

1. Jalankan test import-order baru di atas.
2. Jalankan suite penuh: `py -m pytest tests -q` → tetap 23+ hijau.
3. Smoke test runtime (Cache + Call Graph + Pipeline) yang sudah dijalankan
   sebelumnya tetap lulus:
   - `KnowledgeOrchestrator.gather()` → `EvidenceBundle`.
   - Call Graph menghasilkan baris (`handler→login`, `login→get_user`, dst).
   - `test_planner_engine_end_to_end` sukses.

---

## 8. Status Tracking

| Item | Status |
| :--- | :--- |
| Identifikasi & reproduksi bug | ✅ 07 Agustus 2026 |
| Root cause & rantai siklus | ✅ Didokumentasikan |
| 5.1 `file.py` lazy import | ⏳ Belum dieksekusi |
| 5.2 `ai/knowledge/__init__.py` lazy `__getattr__` | ⏳ Belum dieksekusi |
| 5.3 `orchestrator.py` lazy `register_knowledge_tools` | ⏳ Opsional |
| Test regresi import-order | ⏳ Belum dieksekusi |
| Verifikasi suite + smoke test | ⏳ Belum |

---

## 9. Referensi Terkait

- `docs/update_07_08_26/phase_5_completion_plan.md` — rencana induk Phase 5
  (Tahap C.1/C.2 yang memicu perubahan working-tree ini).
- `docs/update_07_08_26/review_tahap_b_c_phase5.md` — review Tahap B/C.
- `nexa/core/ai/knowledge/orchestrator.py:34` — import top-level `register_knowledge_tools`.
- `nexa/core/agent/tools/knowledge/file.py:4` — import top-level `SQLiteCache`.
- `nexa/core/ai/knowledge/__init__.py:14` — import top-level `orchestrator`.
