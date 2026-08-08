# Rencana Penyelesaian Phase 5 — Cognitive Layer (Semantic Intelligence)

*Status: Artefact Perencanaan — 07 Agustus 2026*

Dokumen ini adalah rencana lengkap (single source of truth) untuk menuntaskan
**Phase 5: Cognitive Layer** sesuai blueprint
`docs/architecture/phase_5_semantic_cognitive_engine.md`. Berisi audit status,
temuan bug blocking, keputusan arsitektur, dan rencana eksekusi per komponen.

---

## 1. Ringkasan Audit: Blueprint vs Implementasi Aktual

| # | Komponen Blueprint | Status | Bukti Kode |
| :-: | :--- | :--- | :--- |
| 1 | Cognitive Pipeline (Intent→Hypothesis→Acquisition→Reasoning→Planning) | ✅ **Selesai** | Orde telah direfactor di `planner/engine.py` |
| 2 | Hypothesis Engine ("Killer Feature") | ✅ **Selesai** | Diintegrasikan ke pipeline, memandu pencarian. |
| 3 | Semantic Indexing (AST→Symbol→Dependency→Call→Knowledge Graph) | ✅ **Selesai** | `indexer.py` call_graph di-wire ke orchestrator. |
| 4 | Object-Oriented Tooling | ✅ **Selesai** | `read_symbol` mencakup `summary`/`dependencies`/`callers`/`callees`. |
| 5 | Semantic Cache | ✅ **Selesai** | `ai/knowledge/cache/*.py` di-wire ke orchestrator. |
| 6 | Cognitive Budget / Tool Budget | ✅ **Selesai** | `knowledge/orchestrator.py:36`; test ada |
| 7 | AST Patch Engine & Unified Diff | ✅ **Selesai** | Hunk applier dengan parsing presisi & reverse order siap. |
| 8 | Capability-Based Dynamic Tools | ✅ **Selesai** | `engine.py:151-161` memanggil `get_schemas_by_capabilities`. |
| 9 | Hierarchical Memory (4 lapis) | ✅ **Selesai** | `ai/memory/hierarchical.py` |

**Skor: 9/9 Selesai (100%).** Phase 5 telah tuntas diimplementasikan.

---

## 2. Temuan Bug Blocking (Harus Dibersihkan DULU)

### BUG-1: `return False` menghentikan seluruh shell loop
`nexa/commands/ai/shell.py:527, 529, 544` — di dalam loop fuzzy-finder &
dependency-resolver, `return False` keluar dari **seluruh** `command_handler`,
bukan satu iterasi. Mengakibatkan proses input berhenti total saat `@file`
menemukan path fuzzy.
**Fix:** ganti `return False` → `continue` / `break` yang tepat.

### BUG-2: `UnicodeEncodeError` di planner
`planner/engine.py` memakai karakter arrow `→` dalam `print(...)`.
Di terminal Windows default (cp1252) crash:
`UnicodeEncodeError: 'charmap' codec can't encode character '\u2192'`.
(terbukti saat uji; baru jalan dengan `PYTHONIOENCODING=utf-8`).
**Fix:** ganti ke ASCII (`->`) atau set encoding aman.

### BUG-3: Dead code + duplikasi schema
- `cognitive/engines/acquisition.py` — mati total (0 referensi) **dan rusak**:
  iterasi `hyp.search_targets` yang tidak ada di `Hypothesis` (`schema.py:5-9`).
- `cognitive/schema.py:17` meng-annotasi `Evidence.target: SearchTarget` —
  **SearchTarget tidak pernah didefinisikan** di repo (import akan gagal).
- Duplikasi tipe: `HypothesisResult` & `ReasoningResult` ada di `schema.py`
  (dataclass) DAN di `engines/hypothesis.py` / `engines/reasoning.py` (class).
  Bekerja hanya karena nama field kebetulan sama.
**Fix:** hapus `acquisition.py`, definisikan `SearchTarget`, konsolidasi 1
sumber schema.

---

## 3. Keputusan Arsitektur: Orde Pipeline Kognitif

### Keputusan: IKUTI BLUEPRINT (Refactor)

Alur blueprint: `Intent → Hypothesis → Knowledge Acquisition (loop) → Reasoning → Planning`

Alur saat ini (terbalik): `Intent → Acquisition → Hypothesis → Reasoning → Planning`

**Alasan ikut blueprint:**
1. Hipotesis memandu pencarian → bukti yang dikumpulkan relevan → **hemat token**
   (inti dari *Cognitive Budgeting* Phase 5).
2. Konsisten dengan filosofi "manusia bikin dugaan dulu, baru cari bukti".
3. Feedback loop memungkinkan *retry*: bukti membantah hipotesis → hipotesis baru.

**Dampak refactor:** `planner/engine.py` langkah 2 dan 3 bertukar posisi, ditambah
loop `gather()` kedua yang dipicu hipotesis (dibatasi `TOOL_BUDGET` agar tidak
loop tak terbatas).

---

## 4. Rencana Eksekusi

### Tahap A — Stabilisasi (Pra-Syarat)
1. Fix `shell.py` `return False` (BUG-1).
2. Hapus karakter Unicode `→` / set encoding aman (BUG-2).
3. Hapus `acquisition.py`; definisikan `SearchTarget`; konsolidasi
   `HypothesisResult`/`ReasoningResult` (BUG-3).
4. Tambah test regresi:
   - `tests/core/test_shell_path_processing.py` (fuzzy finder lanjut, bukan berhenti).
   - `tests/core/ai/planner/test_planner_pipeline.py` (plan jalan tanpa crash
     unicode, pakai MockProvider).
5. Verifikasi: `py -m pytest tests -q` → semua hijau.

### Tahap B — Refactor Orde Pipeline (Blueprint-Faithful)
1. Ubah `planner/engine.py`:
   - STEP 2 → HypothesisEngine (pakai initial hint tanpa evidence).
   - STEP 3 → KnowledgeOrchestrator.gather() dipicu `Need[]` + hipotesis
     (maks 1 iterasi kedua untuk bukti pembuktian/pembantahan).
   - STEP 4 → Reasoning, STEP 5 → Planning (tidak berubah).
2. Sesuaikan prompt `hypothesis.py` agar mengeluarkan `search_targets`
   (bukan hanya deskripsi) untuk mengarahkan `gather()`.
3. Update `docs/update_02_07_26/phase_4_planner_refactor_and_global_storage.md`
   bila perlu sinkron.
4. Test: pipeline menghasilkan plan valid; budget tetap dihormati.

### Tahap C: Advanced Capabilities
#### C.1 Knowledge Graph / Call Graph (✅ Selesai)
- Tabel `call_graph` ✅ dan parser `ast.Call` ✅ (`indexer.py`).
- `read_symbol` + `summary`/`dependencies` ✅ (`file.py`).
- Call graph di-wire ke `KnowledgeOrchestrator` sehingga terbaca oleh Pipeline ✅.

#### C.2 Semantic Cache (✅ Selesai)
- SQLiteCache di-wire ke Orchestrator ✅.
- Memoization pakai cache hash persisten antar sesi ✅.

#### C.3 Capability-Based Dynamic Tools (✅ Selesai)
- `get_schemas_by_capabilities` dipanggil di `planner/engine.py` ✅.
- Schema terfilter berdasarkan intent ✅.

#### C.4 AST Patch Engine & Unified Diff (✅ Selesai)
- Hunk applier dengan parsing presisi (baris demi baris, reverse order) ✅ (`patching/engine.py`).
- Fallback ke mode naive/whitespace-relaxed jika parsing baris strict gagal ✅.
- AST validation jalan otomatis pasca-patch ✅.

---

## 5. Matriks Prioritas

| Prioritas | Item | Effort | Blocker |
| :-: | :--- | :--- | :--- |
| P0 | Tahap A (BUG-1/2/3 + test) | Kecil | Ya — wajib sebelum fitur |
| P1 | Tahap B (orde pipeline) | Sedang | Ya — fondasi Phase 5 |
| P2 | C.3 Dynamic Tools | Kecil | Tidak |
| P2 | C.2 Semantic Cache | Sedang | Tidak |
| P3 | C.1 Knowledge/Call Graph | Besar | Tidak |
| P3 | C.4 AST Patch Engine | Besar | Tidak |

---

## 6. Di Luar Scope (iterasi ini)
- Telegram/VSCode/Slack integration (Phase 5 `05_extensions.md:57`).
- Phase 6 Autonomous Mode (Critic AI).
- Penataan ulang seluruh `docs/` agar sinkron status implementasi.
- `GitTool.execute()` `shell=True` (risiko keamanan) & `SearchTool.findstr`
  Windows-only — bisa masuk hardening terpisah.

---

## 7. Status Tracking

| Item | Status |
| :--- | :--- |
| Audit & artefact rencana | ✅ 07 Agustus 2026 |
| Tahap A: stabilisasi | ✅ Selesai |
| Tahap B: refactor orde pipeline | ✅ Selesai |
| C.1 Knowledge/Call Graph | ✅ Selesai |
| C.2 Semantic Cache | ✅ Selesai |
| C.3 Dynamic Tools | ✅ Selesai |
| C.4 AST Patch Engine | ✅ Selesai |
