# Architecture Constraints & Boundaries

Dokumen ini adalah "Kawat Berduri" (*Guardrails*) yang menjaga arsitektur Nexa agar tidak rusak oleh *Spaghetti Code*. Setiap kali Anda melakukan *Pull Request* (PR) atau menambahkan fitur baru, pengulas kode (*Code Reviewer*) akan mengacu pada dokumen ini. 

Jika kode Anda melanggar konvensi di bawah ini, kode tersebut **pasti ditolak**.

---

## 1. Engine & DTO Ownership
Prinsip utamanya adalah **Tanggung Jawab Tunggal**. Sebuah *Engine* bertugas meramu spesifik *Data Transfer Object* (DTO). *Engine* lain hanya berhak membacanya, bukan menciptakannya.

| Engine | Ownership (Hanya Engine ini yang Boleh Membuat DTO) |
|---|---|
| **Planner Engine** | `ExecutionPlan` |
| **Transformation Engine** | `TransformationResult` |
| **Patch Engine** | `PatchResult`, `PatchObject` |
| **Approval Engine** | `ApprovalResult` |
| **Execution Engine** | `ExecutionResult`, `AuditTrail` |
| **Verification Engine** | `VerificationResult` |

**❌ Anti-Pattern:**
*Planner Engine* memutuskan secara manual untuk mem- *bypass* *Transformation*, lalu membuat objek `PatchResult` dan mengirimkannya ke eksekutor. Ini sangat dilarang!

---

## 2. Event Ownership
Sama seperti DTO, *Event Bus* memiliki tuan rumahnya masing-masing. Jangan memancarkan (*publish*) *event* yang bukan milik *Engine* Anda.

| Engine | Wajib Memancarkan (Publish) Event |
|---|---|
| **Planner Engine** | `SessionStarted`, `BeforeTransformation` |
| **Transformation Engine** | `AfterTransformation`, `TransformationFailed`, `RetryStarted` |
| **Patch Engine** | `BeforePatch`, `AfterPatch`, `PatchFailed` |
| **Approval Engine** | `BeforeApproval`, `AfterApproval` |
| **Execution Engine** | `BeforeExecution`, `AfterExecution`, `RollbackStarted`, `RollbackCompleted` |
| **Verification Engine**| `VerificationCompleted`, `VerificationFailed`, `SessionCompleted` |

---

## 3. Allowed vs Forbidden Imports (Dependency Rules)
Untuk mengunci hierarki *Clean Architecture*, blokade *import* Python dibakukan.

### 🟢 Allowed Dependencies (Sangat Diizinkan)
- `Planner` boleh mengimpor `nexa.core.contracts` dan `nexa.core.knowledge`.
- `Transformation` boleh mengimpor `nexa.core.contracts` dan `nexa.core.providers`.
- `Patch` boleh mengimpor `nexa.core.contracts` dan library standar OS/Filesystem.
- `Execution` boleh mengimpor `nexa.core.contracts` dan `nexa.core.patching`.

### 🔴 Forbidden Dependencies (Haram Hukumnya)
- `Patch Engine` **TIDAK BOLEH** mengimpor modul `Planner` (Hanya boleh baca `TransformationResult`).
- `Transformation Engine` **TIDAK BOLEH** memanggil sintaks file I/O (`open()`, `os.write()`).
- `Planner Engine` **TIDAK BOLEH** mengimpor/mengetahui eksistensi `PatchEngine`.
- Semua *Core Engine* (`nexa/core/ai/*`) **TIDAK BOLEH** mengimpor implementasi spesifik dari `nexa/commands/*` (Layer CLI/UI). Core harus tetap buta (*blind*) terhadap *interface* yang memanggilnya.

---

## 4. Layer Rules
Nexa dibagi menjadi 4 layer ketat. Arus dependensi *import* Python (arah panah) **hanya boleh** bergerak ke bawah, dari luar ke dalam.

`Layer 1 (UI/CLI/Plugins) ➡️ Layer 2 (Core Engines) ➡️ Layer 3 (Contracts) ➡️ Layer 4 (Infrastructure/LLM)`

**Aturan Penalti:** Jika `Layer 3 (Contracts)` ketahuan mengimpor *library* spesifik dari `Layer 1 (CLI)`, hal itu disebut **Circular Dependency** dan merupakan *fatal architecture violation*.

---

## 5. Naming & Package Convention

Keseragaman nama mempercepat pemahaman *developer* baru.

### Class Naming
- Semua *Engine* wajib memiliki sufiks `Engine` (contoh: `TransformationEngine`, bukan `Transformer` atau `TransformManager`).
- Semua *DTO Contract* wajib memiliki sufiks `Result`, `Request`, atau `Plan` (contoh: `PatchResult`, bukan `PatchData`).
- Semua Eksepsi (*Exception*) wajib bersufiks `Error` (contoh: `TransformationError`, bukan `TransformationException`).

### Package Convention
Struktur *file/module* Python harus dipisahkan berdasarkan ranahnya.
```python
nexa.core.ai.transformation
├── engine.py       # (Wajib) Logika utama TransformationEngine
├── models.py       # (Wajib) Definisi TransformationRequest & TransformationResult
├── strategies/     # (Opsional) Implementasi Strategy Pattern spesifik
└── exceptions.py   # (Opsional) Custom Error (TransformationError)
```

Segala impor yang menyeberang antar *engine* hanya boleh merujuk ke file `models.py` (tempat bersemayamnya *Contract*), bukan langsung mengimpor metode internal dari file `engine.py` milik tetangganya.
