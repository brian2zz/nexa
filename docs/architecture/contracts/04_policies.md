# Master Policies (Enterprise Guardrails)

Komponen-komponen Nexa beroperasi di bawah aturan-aturan ketat (Policies). Jika sebuah DTO atau eksekusi internal melanggar satu saja dari kebijakan di bawah ini, *engine* wajib melempar *exception* yang akan diubah menjadi status `FAILED`.

---

## 1. Logging Policy
Sistem terdistribusi membutuhkan *log* yang seragam.
- **Standar Level:** Semua *engine* **wajib** menggunakan level log standar: `DEBUG`, `INFO`, `WARNING`, `ERROR`.
- **Unified Formatting:** Format log harus terstruktur (lebih disarankan *Structured JSON Logging*) yang menyertakan `session_id`, `engine_name`, dan `timestamp`. Tidak boleh menggunakan perintah `print()` biasa.

## 2. Audit Policy
Nexa memanipulasi *file system* pengguna. Jejak ini harus bisa dipertanggungjawabkan.
- **Mandatory Audit Trail:** Setiap perubahan file fisik (Create/Modify/Delete) **wajib** menghasilkan *Audit Trail*. Catatan ini harus menyimpan informasi: Waktu eksekusi, path file, operasi, dan siapa yang menyetujui (Approved By).

## 3. Observability Policy
Untuk keperluan *dashboard* dan pemantauan performa.
- **Mandatory Metrics:** Setiap *Engine* **wajib** mengirimkan metrik eksekusi ke *Event Bus*. Metrik ini minimal berisi: `duration` (lama eksekusi), `status` (berhasil/gagal), `engine_name`, dan `session_id`.

## 4. Resource Policy
Mencegah AI "menggila" dan menghabiskan *resource* atau memori secara destruktif.
- **Transformation Limits:** `TransformationEngine` memiliki batasan keras maksimal `20.000 tokens` per transaksi.
- **Patch Limits:** `PatchEngine` hanya diizinkan memodifikasi maksimal `500 files` dalam satu kali `ExecutionPlan`. Jika AI meminta generasi 10.000 file, sistem harus langsung menolak (*Fail Fast*).

## 5. Plugin Policy
Aturan ketat bagi ekstensi seperti Telegram, VSCode, atau Remote Agent.
- **Read-Only DTO:** Plugin **dilarang keras** mengubah, memanipulasi, atau memutilasi properti dari objek DTO (Contract) resmi milik Nexa. Plugin hanya bertindak sebagai *Observer* atau mengonsumsi data yang sudah ada.

## 6. Exception Policy
Mencegah *error* yang ambigu dan tidak bisa dilacak.
- **No Generic Exceptions:** *Developer* **dilarang keras** menggunakan `raise Exception("error")`.
- **Specific Errors:** Semua *error* harus menggunakan hirarki eksepsi bawaan Nexa, contohnya:
  - `ValidationError`
  - `TransformationError`
  - `PatchError`
  - `ApprovalError`
  - `ExecutionError`
  - `VerificationError`

## 7. AI Policy (Zero Trust LLM)
Aturan terpenting dalam arsitektur AI yang mencegah eksekusi buta (*blind execution*).
- **Never Trust LLM:** Output dari LLM (berupa *string* murni) **tidak pernah dipercaya**. 
- **Strict Pipeline:** Alur eksekusi wajib melalui tahap: 
  `LLM Output` ➡️ `Validate` ➡️ `Normalize` ➡️ `Process` ➡️ `Contract (DTO)` ➡️ `Engine`.
- **No Direct I/O:** LLM **dilarang keras** menyentuh *filesystem* secara langsung dalam kondisi apa pun.

## 8. Thread Safety Policy
Nexa dirancang untuk dieksekusi secara asinkron atau paralel (misal via *Remote Agent* atau *Web*).
- **Concurrency Ready:** Semua operasi yang membaca atau mengubah *state global* wajib *Thread-Safe*.
- **No Shared Mutable State:** Sebisa mungkin hindari variabel global yang dapat dimodifikasi oleh beberapa sesi secara bersamaan.

## 9. Cache Policy
Pengelolaan *cache* untuk efisiensi vs integritas data.
- **Context Caching:** `Knowledge Engine` **diperbolehkan** melakukan *caching* terhadap `ContextBundle` yang berat (seperti parsing *dependency graph*).
- **No Output Caching:** `TransformationEngine` **dilarang keras** melakukan *cache* terhadap `generated_code`. Setiap eksekusi transformasi LLM harus murni dieksekusi secara *real-time* untuk menjamin akurasi sesuai instruksi terkini.

## 10. Transaction Policy (Atomic Execution)
Mencegah *state* proyek pengguna rusak atau tertinggal setengah jalan (*partial corruption*).
- **Atomic Operations:** Eksekusi fisik I/O wajib bersifat *Atomic*.
- **All or Nothing:** Jika `PatchEngine` ditugaskan memodifikasi 10 file, dan file ke-9 mengalami kegagalan (*Permission Denied*), maka ke-8 file sebelumnya **wajib** melalui proses `ROLLBACK`. Tidak boleh ada eksekusi yang setengah jadi.
