# Rencana Perbaikan: C.4 AST Patch Engine & Unified Diff

*Status: Artefact Perencanaan — 07 Agustus 2026*

Dokumen ini adalah rencana untuk menuntaskan **C.4 (AST Patch Engine & Unified
Diff)** Phase 5. Berisi audit kesenjangan, keputusan arsitektur, langkah
eksekusi, desain akhir, dan status tracking.

---

## 1. Ringkasan Kesenjangan

Blueprint (`docs/architecture/phase_5_semantic_cognitive_engine.md:56-59`)
menuntut tiga hal:
1. LLM hanya mengembalikan **Unified Diff** (`@@ -a,b +c,d @@`).
2. **AST Patch Engine** memvalidasi diff secara sintaksis.
3. Merajut kembali file **secara persis** sehingga kode tidak patah.

Verifikasi kode aktual menemukan: **logika engine sudah benar, tetapi tidak
terhubung ke pipeline produksi.**

| # | Kesenjangan | Keparahan | Bukti |
| :-: | :--- | :--- | :--- |
| G-1 | Dua sistem patch paralel — produksi memakai `pipeline/patch.py` (lama) | 🔴 Tinggi | `pipeline/transaction.py:5,31` |
| G-2 | `ai/patching/engine.py` (yang punya C.4) tidak punya pemanggil produksi | 🔴 Tinggi | 0 import selain dirinya sendiri & test |
| G-3 | Test golden hanya menguji Aider-style `<<<< ==== >>>>`; jalur Unified Diff & AST-reject tidak diuji | 🟠 Sedang | `tests/golden/patching/test_patch_engine.py` |
| G-4 | `ai/transformation/processor.py` tidak punya mode diff khusus | 🟡 Rendah | `processor.py:8-33` |

**Inti masalah:** C.4 aktif hanya saat test; saat eksekusi nyata (`ExecutionTransaction`)
sistem lama (SEARCH/REPLACE tanpa Unified Diff & tanpa AST validation) yang berjalan.

---

## 2. Bukti Kode (Apa yang Sudah Ada dan Benar)

Logika C.4 di `nexa/core/ai/patching/engine.py` **sudah sesuai blueprint**:

| Aspek | Status | Lokasi |
| :--- | :--- | :--- |
| Parser Unified Diff header | ✅ | `engine.py:94` — regex `@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@` |
| Re-weave persis berbasis line | ✅ | `engine.py:106-138` — sort hunk descending, strict line-slice match |
| Fallback aman | ✅ | `engine.py:140-168` — naive replace + warning |
| Validasi AST | ✅ | `engine.py:199-211` — `ast.parse`, patch `.py` invalid ditolak |
| Path-traversal guard | ✅ | `engine.py:21-30` |
| RiskAnalyzer | ✅ | `engine.py:233-234` |

**Terverifikasi manual (in-memory, read-only):**
- Single hunk: `def login(): print(1); print(2); return True` → `@@ -1,3 +1,3 @@` → hasil `print(3)` benar, AST valid. ✅
- Multi hunk (urutan header naik): `@@ -2,1 ... @@` lalu `@@ -8,1 ... @@` → keduanya diterapkan benar berkat sort descending. ✅

---

## 3. Apa yang Dibentarkan

### 3.1 Integrasi pipeline (G-1, G-2)

**Keputusan arsitektur: OPSI A — Migrasi penuh ke satu sumber kebenaran.**

| Opsi | Deskripsi | Keputusan |
| :--- | :--- | :--- |
| A. Migrasi penuh | `transaction.py` pakai `ai/patching/engine.py`; `pipeline/patch.py` deprecated | ✅ **Dipilih** |
| B. Delegasi | `pipeline/patch.py` memanggil `ai/patching/engine.py` di dalam `calculate()` | ❌ Masih duplikasi |
| C. Wire di level planner | `AIPlannerEngine`/`ExecutionEngine` langsung pakai engine baru | ❌ Lewati `ExecutionTransaction` |

**Alasan pilih A:**
1. Satu engine patch → tidak ada risiko drift antar dua implementasi.
2. Seluruh kekayaan C.4 (Unified Diff + AST validation + RiskAnalyzer) tersedia
   di jalur produksi, bukan hanya test.
3. `PatchApplier`, `BackupRollbackStrategy`, `VerificationPipeline` tidak berubah
   — hanya sumber `PatchResult` yang diganti.

**Peta konversi yang diperlukan:**

| Dari (`pipeline`) | Ke (`ai/patching`) |
| :--- | :--- |
| `TransformationResult(raw_code, step)` | `PatchRequest(transformation_result={"generated_code": raw_code}, repository_root, target_files=[step["target"]])` |
| `pipeline.patch.PatchResult` (target, action, content) | konversi `PatchObject` → `PatchResult` agar `PatchApplier` tetap berfungsi |

**Titik perubahan:**
- `nexa/core/pipeline/transaction.py:31` — ganti `self.patch_engine = pipeline.patch.PatchEngine()` → `ai.patching.engine.PatchEngine()`.
- `nexa/core/pipeline/transaction.py:44` — adaptasi pemanggilan `calculate()` → `calculate_patch()` dan konversi hasil.

### 3.2 Test golden Unified Diff (G-3)

Tambah ke `tests/golden/patching/test_patch_engine.py`:

1. `test_golden_unified_diff_single_hunk`
   - File awal `login.py`, satu hunk `@@ -1,3 +1,3 @@`.
   - Asersi: `result.success=True`, 1 patch, `new_content` tepat, `ast.parse` valid.
2. `test_golden_unified_diff_multi_hunk`
   - Dua hunk dengan urutan header naik (`@@ -2,1 @@` lalu `@@ -8,1 @@`).
   - Asersi: kedua perubahan hadir (bukti sort descending bekerja).
3. `test_golden_unified_diff_ast_reject`
   - Hunk menghasilkan `.py` invalid (mis. `def :` atau bracket tak seimbang).
   - Asersi: `patches` kosong, `success=False`, warning berisi "AST Validation Error".
4. `test_golden_unified_diff_fallback`
   - Hunk dengan whitespace tidak persis (mis. indent berbeda).
   - Asersi: fallback jalan, warning "whitespace relaxation", hasil tetap ada.

### 3.3 (Opsional) Mode diff di ResponseProcessor (G-4)

`nexa/core/ai/transformation/processor.py`:
- Jika `raw_response` mengandung pola `@@ -` + baris `+`/`-`, set
  `TransformationMode.DIFF` → kirim raw sebagai `generated_code` tanpa
  ekstraksi markdown block.
- Tujuan: mengizinkan LLM mengembalikan Unified Diff langsung dari
  `TransformationEngine`, bukan hanya SEARCH/REPLACE.

---

## 4. Seharusnya Seperti Apa (Desain Final)

```
ExecutionTransaction
   └─ ai/patching/engine.py      (SINGLE PatchEngine)
        ├─ Parser Unified Diff header        ✅
        ├─ Re-weave berbasis line + fallback ✅
        ├─ Validasi AST (.py)                ✅
        ├─ RiskAnalyzer                      ✅
        └─ Aider-style (legacy)              ✅ (tetap didukung)
   └─ pipeline.patch.PatchApplier (unchanged)
   └─ rollback.backup.BackupRollbackStrategy (unchanged)
   └─ verification.VerificationPipeline     (unchanged)
```

Aturan:
- **Tidak ada lagi dua `PatchEngine`.** `pipeline/patch.py` deprecated.
- Semua jalur MODIFY didukung: Aider-style (legacy), Unified Diff, full-file replacement.
- Patch `.py` yang invalid sintaks **selalu ditolak sebelum menyentuh filesystem**
  (validasi AST di `ai/patching/engine.py:199-211`).

---

## 5. Matriks Prioritas

| Prioritas | Item | Effort | Blocker |
| :-: | :--- | :--- | :--- |
| P0 | 3.1 Integrasi pipeline (migrasi ke `ai/patching/engine.py`) | Sedang | Ya — wajib agar C.4 aktif |
| P1 | 3.2 Test golden Unified Diff (4 kasus) | Kecil | Tidak |
| P2 | 3.3 Mode diff ResponseProcessor | Kecil | Tidak |
| P2 | Sinkronisasi `phase_5_completion_plan.md` (C.4 status) | Kecil | Tidak |

---

## 6. Verifikasi

1. Test golden baru (4 kasus) lulus.
2. Suite penuh: `py -m pytest tests -q` → 24+ tetap hijau.
3. Smoke test: `ExecutionTransaction` memakai `ai/patching/engine.py` — jalankan
   skenario MODIFY sederhana dan pastikan rollback/verifikasi masih jalan.
4. Semua jalur import tetap aman (regresi import-order tetap lulus).

---

## 7. Status Tracking

| Item | Status |
| :--- | :--- |
| Audit C.4 vs blueprint | ✅ 07 Agustus 2026 |
| Keputusan arsitektur (Opsi A — migrasi penuh) | ✅ Diputuskan |
| 3.1 Integrasi pipeline | ⏳ Belum |
| 3.2 Test golden Unified Diff (4 kasus) | ⏳ Belum |
| 3.3 Mode diff ResponseProcessor | ⏳ Opsional |
| Verifikasi suite + smoke test | ⏳ Belum |

---

## 8. Referensi Terkait

- `docs/architecture/phase_5_semantic_cognitive_engine.md:56-59` — spesifikasi blueprint.
- `docs/update_07_08_26/phase_5_completion_plan.md` — rencana induk Phase 5 (C.4).
- `docs/update_07_08_26/review_tahap_b_c_phase5.md:77` — review status C.4.
- `nexa/core/ai/patching/engine.py` — engine C.4 (logika sudah benar).
- `nexa/core/pipeline/transaction.py` — titik integrasi.
- `nexa/core/pipeline/patch.py` — engine lama yang akan deprecated.
