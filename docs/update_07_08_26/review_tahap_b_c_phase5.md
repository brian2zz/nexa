# Review Commit Tahap B & C Phase 5 (720ac58, e6ec9b7)

*Status: Artefact Review — 07 Agustus 2026*

Review pasca-implementasi untuk dua commit besar Phase 5 Cognitive Layer:
- `720ac58` — refactor orde pipeline sesuai blueprint (Tahap A-sisa & Tahap B)
- `e6ec9b7` — aktivasi Knowledge Graph, Semantic Cache, Dynamic Tools, Unified Diff (Tahap C)

---

## 1. Ringkasan Eksekutif

Tahap B (orde pipeline) dan sebagian Tahap C berhasil diimplementasikan dengan benar.
Namun ditemukan **1 bug regresi kritis** yang membuat jalur `PLAN` crash total,
serta **ketidaksesuaian antara judul commit dan realita implementasi**
(khususnya klaim "Knowledge Graph" dan "Semantic Cache").

---

## 2. Yang Sudah Benar (Terverifikasi)

| Item | Status | Bukti |
| :--- | :--- | :--- |
| Orde pipeline sesuai blueprint (Hypothesis → Acquisition) | ✅ | `planner/engine.py` — STEP 2 Hypothesis, STEP 3 Gather |
| `search_targets` dari hipotesis memandu `gather()` | ✅ | `engines/hypothesis.py` prompt baru; `engine.py` mengekstrak `hypothesis_hints` |
| BUG-1: `return False` → `break` di `shell.py` | ✅ | `commands/ai/shell.py:527,529,544` |
| BUG-2: print Unicode → ASCII | ✅ | `engine.py`, `orchestrator.py`, `formatter.py`, `interactive.py` |
| `acquisition.py` (dead code) dihapus | ✅ | file tidak lagi ada |
| `SearchTarget` didefinisikan | ✅ | `cognitive/schema.py:6` |
| Dynamic Tools (C.3) aktif | ✅ | `engine.py:152` — `get_schemas_by_capabilities` dipanggil, diteruskan sebagai `active_schemas` |
| Unified Diff applier (C.4) | ✅ | `patching/engine.py:84+` — naive hunk applier |
| Object-Oriented Tooling: `read_symbol` + `summary`/`dependencies` | ✅ | `agent/tools/knowledge/file.py:69-73` |

---

## 3. Bug Regresi KRITIS

### BUG-R1: `ImportError` pada jalur PLAN

Commit `720ac58` menghapus `ReasoningResult` dari `cognitive/schema.py`
(sebagai bagian konsolidasi schema duplikat), **tetapi tidak memperbarui import
di `engines/planning.py`**.

**Lokasi:**
- `nexa/core/ai/cognitive/engines/planning.py:3`
  ```python
  from nexa.core.ai.cognitive.schema import ReasoningResult
  ```
- `ReasoningResult` kini HANYA didefinisikan di `engines/reasoning.py:16`.

**Dampak terukur (reproduksi):**
```
ImportError: cannot import name 'ReasoningResult' from 'nexa.core.ai.cognitive.schema'
```
Jalur `PLAN` di shell crash sebelum STEP 1 selesai.

**Kenapa tidak tertangkap test:** seluruh 22 test yang ada hanya menguji komponen
secara terisolasi (unit test), **tidak ada satu pun yang menjalankan
`AIPlannerEngine.plan()` end-to-end** dengan MockProvider. Regresi integrasi
seperti ini lolos tanpa disadari.

**Fix:** ubah import di `planning.py:3` menjadi
`from nexa.core.ai.cognitive.engines.reasoning import ReasoningResult`.

---

## 4. Klaim Commit vs Realita (Tahap C)

Judul commit `e6ec9b7` menyatakan "Knowledge Graph, Semantic Cache, Dynamic Tools,
Unified Diff". Verifikasi terhadap kode menunjukkan sebagian klaim melebihi realita:

| Klaim Judul | Realita | Verdict |
| :--- | :--- | :--- |
| **Knowledge Graph / Call Graph** | ❌ **Tidak diimplementasikan.** `agent/indexer.py` hanya memiliki tabel `files`, `symbols`, `imports`. Tidak ada tabel `call_graph`, `knowledge_graph`, `dependency_graph`. Relasi `CALLS` (`knowledge/models.py:47`) tetap tidak pernah diproduksi. Yang ditambahkan hanya enrich `read_symbol` (bagian Object-Oriented Tooling). | **MISSING** |
| **Semantic Cache** | ⚠️ Parsial. `SQLiteCache` di-wire ke `FileTool.read_symbol` saja (`file.py:15-18`). **Tidak** di-wire ke `KnowledgeOrchestrator` / pipeline planner seperti rencana C.2. | **PARTIAL** |
| **Dynamic Tools (C.3)** | ✅ `get_schemas_by_capabilities` dipanggil di `engine.py:152`. | **DONE** |
| **Unified Diff (C.4)** | ⚠️ Naive hunk applier (regex `@@...@@`, whitespace-relaxed matching). **Belum** validasi AST / re-weave presisi. | **PARTIAL** |

Kesimpulan: dari 4 item yang diklaim, hanya **Dynamic Tools** yang benar-benar
selesai. **Knowledge Graph belum disentuh sama sekali.**

---

## 5. Rekomendasi Tindak Lanjut (Urutan Prioritas)

1. **P0 — Fix BUG-R1**: perbaiki import `ReasoningResult` di `planning.py:3`.
2. **P0 — Tambah integration test**: buat test `AIPlannerEngine.plan()` end-to-end
   dengan MockProvider agar regresi integrasi (seperti BUG-R1) terdeteksi.
   Ini akar masalah: jalur PLAN tidak pernah diuji secara utuh.
3. **P1 — Koreksi artefact `phase_5_completion_plan.md`**: tandai C.1 (Knowledge
   Graph) dan C.2 (Semantic Cache) sebagai **Belum selesai**, bukan selesai.
4. **P1 — Lanjutkan C.1 asli**: implementasi tabel `call_graph`/`knowledge_graph`
   di indexer + parser relasi `CALLS`.
5. **P2 — Lengkapi C.2**: wire `SQLiteCache` ke `KnowledgeOrchestrator`.
6. **P2 — Perkuat C.4**: validasi sintaks AST setelah hunk diterapkan.

---

## 6. Status Tracking

| Item | Status |
| :--- | :--- |
| Review disusun | ✅ 07 Agustus 2026 |
| Fix BUG-R1 (import `planning.py`) | ⏳ Belum |
| Integration test `AIPlannerEngine.plan()` | ⏳ Belum |
| Koreksi artefact planning (C.1/C.2 status) | ⏳ Belum |
| C.1 Knowledge Graph/Call Graph (asli) | ⏳ Belum |
| C.2 Semantic Cache di Orchestrator | ⏳ Belum |
| C.4 Validasi AST pada Unified Diff | ⏳ Belum |
