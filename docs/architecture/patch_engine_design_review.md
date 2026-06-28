# Patch Engine Design Review

**Status:** Proposed untuk Phase 3.3  
**Tujuan:** Mengonversi *TransformationResult* (keluaran LLM) menjadi *PatchResult* murni yang deterministik dan siap dieksekusi, tanpa menggunakan AI.

---

## 1. Core Concept (I/O Flow)

Patch Engine bertindak sebagai jembatan yang 100% deterministik. Ia mengambil blok kode dari LLM, membandingkannya dengan file asli di *disk*, dan merumuskan instruksi *diff/replace* yang pasti.

```mermaid
graph TD
    classDef input fill:#2b6cb0,color:#fff,stroke:#1a365d,stroke-width:2px;
    classDef output fill:#276749,color:#fff,stroke:#22543d,stroke-width:2px;
    classDef core fill:#e2e8f0,stroke:#4a5568,stroke-width:2px;

    TR[TransformationResult<br/>(Dari LLM)]:::input
    CF[(Current File di Disk)]:::input
    
    PE[Patch Engine<br/>- Search & Replace<br/>- Diff Calculation<br/>- Hash Check]:::core
    
    PR[PatchResult<br/>List of PatchObjects]:::output

    TR --> PE
    CF --> PE
    PE --> PR
```

---

## 2. Tanggung Jawab (Single Responsibility)

Sesuai dengan *Golden Rules*, Patch Engine **hanya** bertugas untuk mengalkulasi *patch*.
- **YANG DILAKUKAN:** Mencari posisi blok kode yang harus diganti (Search), menghitung perbedaan (*diff*), dan meramal *hash* file masa depan (*New Hash*).
- **YANG TIDAK DILAKUKAN:** Menulis langsung ke *file system*. Eksekusi fisik adalah tugas `ExecutionEngine`.

---

## 3. Algoritma Internal (Deterministic)

Karena *Patch Engine* dilarang menggunakan AI (ADR-005), algoritma pendekatannya adalah sebagai berikut:

### a. Unified Diff Parsing (Prioritas Utama)
Jika LLM mengembalikan format standar `diff` (menggunakan `+` dan `-`), *Engine* mem- *parse* blok tersebut secara ketat, mencocokkan garis konteks, dan menghitung `new_content`.

### b. Search and Replace (Aider Style)
Jika LLM mengembalikan blok penanda *Search/Replace* seperti:
```python
<<<<
def old_function():
    pass
====
def new_function():
    return True
>>>>
```
*Engine* akan melakukan *exact string matching* (atau berbasis AST) terhadap isi file lokal `CF` untuk mencari blok `<<<<` dan menggantinya dengan blok `====`.

---

## 4. Risk Assessment (PatchAnalysis)

Ini adalah fitur cerdas untuk melindungi ekosistem pengguna. Setelah mengalkulasi *patch*, *Patch Engine* wajib melakukan asesmen risiko heuristik terhadap modifikasi tersebut.

**Tingkat Risiko (Risk Level):**
- **LOW:** Perubahan kosmetik atau aman (misal: memodifikasi `README.md`, menambahkan *comment*, mengubah CSS).
- **MEDIUM:** Memodifikasi logika aplikasi standar.
- **HIGH:** Menyentuh komponen kritikal (misal: file migrasi *database*, skrip *deployment*, konfigurasi *environment*).
- **CRITICAL:** Penghapusan (*deletion*) secara massal (contoh: menghapus 100 file sekaligus).

Jika sebuah *patch* masuk kategori HIGH/CRITICAL, *Approval Engine* akan menolak mode Otonom (*Autonomous Bypass*) dan memaksa intervensi manusia (⚠ **High Risk Patch: Requires Manual Approval**).

---

## 5. Struktur Output (Contract)

Setelah memproses *input* dan menilai risiko, *Patch Engine* diwajibkan menghasilkan kontrak `PatchResult`.

```json
{
  "success": true,
  "status": "SUCCESS",
  "analysis": {
    "risk_level": "HIGH",
    "risk_factors": ["Memodifikasi file skema database (models.py)"],
    "needs_human_approval": true
  },
  "patches": [
    {
      "path": "/src/main.py",
      "operation": "MODIFY",
      "old_hash": "a1b2c3d4...",
      "new_hash": "f9e8d7c6...",
      "old_content": "def run():\n    pass",
      "new_content": "def run():\n    print('Hello')",
      "diff": "@@ -1,2 +1,2 @@\n-def run():\n-    pass\n+def run():\n+    print('Hello')"
    }
  ],
  "additions": 1,
  "deletions": 1,
  "summary": "Berhasil mengalkulasi perubahan untuk main.py"
}
```

---

## 5. Failure Scenarios (Fail Fast)

Sesuai *Policies*, Patch Engine harus gagal dengan anggun (*Graceful Failure*) jika:
1. **Target Not Found:** Blok kode yang ingin diganti (*old_content*) tidak dapat ditemukan secara akurat di dalam file asli.
2. **Permission Denied:** Path yang dituju berada di luar batas repositori (*Sandbox Boundary Violation*).

Dalam kasus tersebut, *Patch Engine* akan melempar `PatchError`, merubah status `PatchResult` menjadi `FAILED`, dan memicu *Event* `PatchFailed`.
