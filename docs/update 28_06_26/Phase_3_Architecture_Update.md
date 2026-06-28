# Walkthrough: Master Contract Implementation

Pekerjaan dokumentasi masif (Master Contract) telah berhasil diselesaikan secara bertahap dan modular. Seluruh fondasi arsitektur Nexa kini tertuang dengan sangat komprehensif di dalam direktori `docs/architecture/contracts/`.

Berikut adalah ringkasan dari dokumen-dokumen yang telah digenerasi:

## 1. Direktori Pusat
Direktori baru `docs/architecture/contracts/` telah dibuat untuk menjadi *"Single Source of Truth"* bagi seluruh pengembang *Core Engine*, *Plugin*, maupun antarmuka eksternal di masa depan.

## 2. File Spesifikasi
Total ada 7 file utama (pilar) yang saling terhubung yang telah ditulis sesuai dengan *feedback* dan struktur *Enterprise* yang telah disetujui:

### `00_README.md`
- Titik masuk (*entry point*) untuk orientasi.
- Menjelaskan arti dan pentingnya *Contract* serta memberikan urutan membaca yang benar (*Learning Path*).
- Memperkenalkan konsep klasifikasi **Contract Level** (`Stable`, `Experimental`, `Internal`, `Deprecated`).

### `01_philosophy_and_adr.md`
- **10 Commandments Nexa:** (*Golden Rules*) seperti larangan mutlak kebocoran *Provider* ke *Core Logic*.
- Penjabaran dalam mengapa kita memilih desain *Immutable Contract*.
- Visualisasi **Anti-Pattern** menggunakan diagram panah merah (❌) untuk kesalahan-kesalahan umum (seperti *Planner* menulis *file* langsung).
- Kumpulan **ADR (Architecture Decision Records)** lengkap dengan Status, Reason, dan Consequences (ADR-001 hingga ADR-009).

### `02_core_objects.md`
- Dokumentasi API terlengkap untuk setiap *Data Transfer Object* (DTO) resmi, seperti `ExecutionPlan`, `TransformationResult`, `PatchResult`, hingga `VerificationResult`.
- Setiap objek kini didokumentasikan berdasarkan Purpose, Lifecycle, Fields, Validation Rules, JSON Example, dan Future Extensions.

### `03_state_and_events.md`
- Memetakan arsitektur *asynchronous* melalui **Trifecta Diagram** (dengan *Mermaid*):
  - *Sequence Diagram:* Alur DTO antar-engine secara kronologis.
  - *Activity Diagram:* Titik keputusan dan percabangan (*Decision Points* & *Retry Loops*).
  - *State Diagram:* Kondisi siklus hidup operasional (`PENDING`, `RUNNING`, `ROLLED_BACK`).
- Tabel *Payload* **Event Bus** resmi (`BeforeTransformation`, `AfterPatch`, dll.).

### `04_policies.md`
- Mendefinisikan aturan keras (*hard rules*) mengenai:
  - *Validation Policy* (Strict typing & Absolute Paths)
  - *Retry & Backoff Policy* (Eksponensial & maksimal 3 retries)
  - *Security Policy* (Boundary Sandbox & Secret Scrubbing)
  - *Serialization Policy* (JSON Murni tanpa objek referensial Python)
  - *Performance Policy* (Zero Copy Parsing)
  - *Compatibility Policy*

### `05_extensions.md`
- Spesifikasi desain untuk *Phase 4 (Remote Agent)* dengan WebSockets.
- Spesifikasi *Phase 5 (Telegram Integration)* yang bekerja cukup dengan men-*subscribe* `BeforeApproval` event.
- Kerangka pikiran awal untuk *Phase 6 (Autonomous Mode)* menggunakan *Critic AI* menggantikan *user approval*.

### `06_reference_architecture.md`
- Satu file khusus yang dirancang untuk visualisasi. Memuat *Full Pipeline Diagram (Macro View)*, diagram lapisan *Clean Architecture*, dan peta direktori *folder* Nexa (*Folder Structure*).

---

## 3. Phase 3.3: Patch Engine Implementation (Kode Python)
Teori di atas telah dieksekusi menjadi sistem *backend* nyata tanpa halusinasi AI.

### Model Sentralisasi (`nexa.core.models`)
Sesuai arahan arsitektur, seluruh DTO dan *Contract* kini didefinisikan menggunakan standar `@dataclass` Python (tanpa dependensi berat Pydantic).
- **`enums.py`**: Mengunci tipe standar operasional (Status, Operation, RiskLevel, SearchStrategy, PatchStrategy).
- **`events.py`**: Memperkenalkan pembungkus DTO `EventContext` dan *interface* komunikasi `EventPublisher`.
- **`dto/patch.py`**: DTO absolut yang mengatur *input* (`PatchRequest`) dan output (`PatchResult`, `PatchObject`, `PatchAnalysis`). File lama di folder `patching/models.py` telah dihapus untuk menghindari redundansi.

### Rule-Based Risk Analyzer
Pemeriksaan risiko otomatis kini tidak lagi di- *hardcode*, melainkan mematuhi *Rule-Based Architecture* (`nexa/core/ai/patching/risk_analyzer.py`):
- `DeleteFileRule` (+30 risk score)
- `MigrationFileRule` (+50 risk score)
- `ModelFileRule` (+20 risk score)
- `MassiveDeleteRule` (+30 risk score)
Setiap nilai ini digabungkan secara dinamis untuk menentukan level risiko (LOW hingga CRITICAL).

### Patch Engine Core
Otak utilitas `nexa/core/ai/patching/engine.py` telah sukses ditulis:
- Murni deterministik. Melakukan pencarian blok teks (*Search*) dan substitusi (*Replace*) tanpa bergantung lagi ke LLM API.
- Menghasilkan status, daftar modifikasi (`PatchObject`), metrik peringatan (*warnings*), dan asesmen risiko secara *real-time*.

### Unit & Golden Testing
Eksekusi di atas diamankan oleh pengujian regresi tangguh bernama **Golden Test** (`tests/golden/patching/test_patch_engine.py`):
- Memeriksa struktur manipulasi *dummy* (seperti pengubahan fungsionalitas `login()` secara sukses dengan deteksi level *LOW*).
- Memeriksa injeksi modifikasi pada file kritikal (seperti menyentuh *models.py* secara otomatis memicu skenario bahaya/skor +20, *MEDIUM*).
- **Status Uji Coba: LULUS (OK).**

---

## 4. Phase 3.35: Core Infrastructure (Sprint 1)
Sistem Nexa resmi beralih dari aplikasi mandiri tunggal menjadi **Sistem Terdistribusi Berbasis Event**. Semua komponen infrastruktur yang dirancang di `08_infrastructure_layer.md` kini aktif dalam wujud Python murni.

### PipelineBus (Execution Spine)
- **`nexa/core/events/bus.py`**: Menggantikan `EventManager` dengan `PipelineBus` tangguh yang dioperasikan oleh `ThreadPoolExecutor`. Mendukung pola pencegatan `Middleware` dengan proteksi eksepsi otomatis (isolasi *subscriber crash*).
- **`nexa/core/events/middleware.py`**: Kelas abstraksi *object-oriented* yang siap mencegat rute pesan, dan sanggup melempar `PropagateHalted` untuk menghentikan aliran jika ada bahaya (*Short-Circuit* keamanan).
- Diuji sukses dengan unit test (`tests/core/test_pipeline_bus.py`).

### Storage & Observability
- **`nexa/core/storage/base.py` & `jsonl.py`**: Sistem `StorageBackend` buta tipe, siap dialihkan ke *PostgreSQL* di masa depan.
- **`nexa/core/observability/metrics.py`**: Agen pintar yang otomatis menempel ke `PipelineBus` untuk merekam performa mesin (Durasi, CPU, Token).
- **`nexa/core/observability/audit.py`**: Sistem kotak hitam (*Black Box*) penangkap setiap kejadian Modifikasi/Hapus file dan kejadian *Rollback*.

### Plugin SDK
- **`nexa/plugin/base.py`**: Cetak biru `NexaPlugin` yang memaksa pembuat ekstensi pihak ketiga (Telegram/VSCode) mematuhi *Lifecycle* inisialisasi yang teratur.

---

## 5. Phase 3.35 - Sprint 2: Refactoring Legacy Engines
Nexa melakukan perombakan massal agar mesin (*Engines*) lama mendukung `PipelineBus` secara *native*, menghubungkan mereka ke tulang punggung infrastruktur Nexa.

### AIPlannerEngine
- **Lokasi**: `nexa/core/ai/planner/engine.py`
- Menginjeksi `PipelineBus`.
- Memancarkan `BeforePlanning`, `AfterPlanning`, dan `PlanningFailed`.

### TransformationEngine
- **Lokasi**: `nexa/core/ai/transformation/engine.py`
- Menginjeksi `PipelineBus`.
- Memancarkan `BeforeTransformation`, `AfterTransformation`, dan `TransformationFailed`.
- Mampu memancarkan `RetryStarted` jika LLM berhalusinasi, sehingga Nexa bisa mendeteksi frekuensi halusinasi LLM (*Observability Metrics*).

### PatchEngine
- **Lokasi**: `nexa/core/ai/patching/engine.py`
- Menggantikan parameter *mock* `EventPublisher` ke `PipelineBus` murni tanpa merusak pengujian (*backward compatible* dengan inisialisasi `bus=None`).
- Memancarkan `BeforePatch`, `AfterPatch` (beserta skor risiko deterministik), dan `PatchFailed`.
- Uji Coba *Golden Test* berhasil berjalan tanpa hambatan dengan 5 pengujian (100% OK).

---

## 6. Phase 3.4 - Sprint 3: Approval Engine
Approval Engine beroperasi murni sebagai *Gatekeeper* yang sepenuhnya buta terhadap antarmuka pengguna (Agnostik-UI). Ia tidak tahu menahu apakah ia sedang di-*approve* oleh manusia via Terminal, via Telegram, atau via agen AI (*Critic*).

### Arsitektur Blok-Sinyal (Block & Wait)
- **Lokasi**: `nexa/core/approval/engine.py`
- Engine ini merilis event `BeforeApproval` via PipelineBus dan langsung membekukan (*block*) jalur eksekusinya menggunakan mekanisme `threading.Event`.
- PipelineBus (dalam *thread* lain) menunggu masuknya balasan berupa event `ApprovalGranted` atau `ApprovalRejected`.
- Ketika masuk, Engine "terbangun" (unblocked) dan merilis `AfterApproval` sebelum mengembalikan `ApprovalResult`.
- Dilengkapi dengan *timeout mechanism* (misalnya menolak otomatis setelah 10 menit jika tidak ada jawaban dari antarmuka apa pun).
- **Hasil Unit Test (`test_approval_engine.py`)**: LULUS 100% untuk skenario Setuju, Tolak, maupun Habis Waktu (Timeout) dengan bantuan simulasi bot asinkron (`MockTelegramSubscriber`).

---

## 7. Phase 3.5 - Sprint 4: Execution Engine (The Atomic Writer)
Di sinilah Nexa menyentuh dunia nyata (*Filesystem*). Berbeda dengan *Engine* lainnya yang memakai AI, mesin ini 100% Deterministik. Ia mengimplementasikan transaksi *Database-Style* (*Atomic: All-or-Nothing*).

### BackupManager (Sistem Pencadangan Kebal Bencana)
- **Lokasi**: `nexa/core/execution/backup.py`
- Menyimpan cadangan *fisik* di dalam folder `.nexa/backups/[SESSION_ID]_[TIMESTAMP]`.
- Dilengkapi dengan *manifest.json* yang mencatat metadata (path, hash, timestamp) setiap file yang diubah.
- Mendukung siklus transaksional: `create_session()`, `backup()`, `restore()`, dan `commit()`.

### ExecutionEngine (Logika Transaksi Atomic)
- **Lokasi**: `nexa/core/execution/engine.py`
- **Alur Kerja**: Backup -> Write -> Verify Hash -> Commit / Rollback.
- Jika semua proses berjalan lancar, *file* akan disimpan, dan transaksi di-*commit*. Event `AfterExecution` disiarkan.
- **Rollback Otomatis**: Jika dalam transaksi yang berisi (misalnya) 5 file, ada 1 file yang gagal diverifikasi (*hash mismatch* karena interupsi pengguna lain/proses tersembunyi), mesin secara radikal membatalkan *semuanya*. Ia otomatis memanggil `BackupManager.restore()` untuk mengembalikan kode proyek Anda ke hitungan milidetik sebelum eksekusi terjadi.
- Memancarkan event krusial ke *PipelineBus*: `BeforeExecution`, `ExecutionFailed`, `RollbackStarted`, dan `RollbackCompleted` (Sangat bernilai untuk *Audit Service*).
- **Hasil Unit Test (`test_execution_engine.py`)**: LULUS 100%. Simulasi injeksi kegagalan hash (*Wrong Hash Prediction*) dengan sempurna memicu aktivasi Rollback, dan mengembalikan file percobaan tepat ke kondisi awalnya.

---

## 8. Phase 3.6 - Sprint 5: Verification Engine (Sang Dewan Juri)
Tahapan final dari seluruh siklus. Setelah file ditulis oleh *Execution Engine*, *Verification Engine* mengambil alih kendali (Tanpa LLM, menggunakan sub-proses independen).

### Mekanisme Kiamat Tertunda (Delayed Rollback)
- **Lokasi**: `nexa/core/verification/engine.py` & `nexa/core/execution/engine.py`
- *Verification Engine* bertugas memanggil `py_compile` dan `unittest` untuk memvalidasi *syntax* dan logika *test*.
- Jika terdeteksi ada kerusakan (misalnya *SyntaxError* karena *Patch Engine* salah menaruh spasi/titik dua), *Verification Engine* TIDAK perlu tahu cara melakukan *Rollback*.
- Ia cukup meneriakkan event `VerificationFailed` ke *PipelineBus*.
- Secara gaib dan *decoupled*, *Execution Engine* yang telah saya program untuk "mendengarkan" frekuensi ini, akan langsung bangun dan memicu metode `_do_rollback()`. File yang rusak akan dihapus dan dipulihkan ke wujud aslinya dari folder `.nexa/backups/`.
- **Hasil Unit Test (`test_verification_engine.py`)**: LULUS 100%. Saya mensimulasikan kode `def hello()\n` (tanpa titik dua) yang sengaja diloloskan ke sistem. *Verification Engine* mendeteksi `SyntaxError`, melemparkan *event*, dan *PipelineBus* secara asinkron memicu *Rollback* di *Execution Engine* yang seketika membalikkan file tersebut menjadi utuh kembali. Luar biasa!

## Kesimpulan Akhir
Dengan lahirnya dokumen-dokumen dan implementasi konkret kelima *Sprint* ini, Nexa secara resmi tidak lagi hanya bertindak sebagai skrip Python biasa. Nexa telah berevolusi menjadi sebuah **Platform Autonomous AI Architectures** (*Execution Spine*) yang mengedepankan isolasi (*Decoupling*), *Event-Driven Communication*, serta *Filesystem Safety* tingkat militer (ACID-like). Infrastruktur pamungkas ini telah siap 100% untuk menopang Fase ke-4: CLI & Telegram Agent di kemudian hari.
