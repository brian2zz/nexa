# Core Objects & Data Models API (Version 1.0)

Selamat datang di direktori objek komunikasi Nexa. Dokumen ini mendefinisikan seluruh struktur *Data Transfer Object* (DTO) resmi yang mengalir di sepanjang pipa eksekusi.

Setiap objek diberikan **Contract Level** (`[Stable]`, `[Experimental]`, `[Internal]`, `[Deprecated]`) dan **Version** (`1.0`, `1.1`). Perubahan penambahan atribut (forward compatibility) di masa depan akan menaikkan versi minor, sementara penghapusan atribut akan menaikkan versi mayor (refactor).

---

## 1. Global Enums
Semua objek di dalam Nexa harus menggunakan enumerasi global yang sama agar selaras.

### Status Enum
Status siklus hidup sebuah operasi.
- `PENDING`: Menunggu dieksekusi.
- `RUNNING`: Sedang dalam proses eksekusi.
- `SUCCESS`: Berhasil penuh.
- `FAILED`: Gagal total.
- `PARTIAL`: Berhasil sebagian (sebagian file gagal di-patch).
- `ROLLED_BACK`: Dibatalkan dan dikembalikan ke versi aslinya.

### Operation Enum
Tindakan spesifik pada level AI maupun Sistem File.
- `GENERATE`: Membuat dari nol.
- `MODIFY`: Mengubah sebagian.
- `DELETE`: Menghapus file/kode.
- `MOVE`: Memindahkan file.
- `RENAME`: Mengubah nama file.
- `OPTIMIZE`: Mempercepat kinerja.
- `REPAIR`: Memperbaiki error.
- `DOCUMENT`: Menambahkan dokumentasi.
- `TRANSLATE`: Mengonversi bahasa pemrograman.
- `EXPLAIN`: Menghasilkan teks penjelasan.

---

## 2. ExecutionPlan
**Contract Level:** `[Stable]` | **Version:** `1.0`

### Purpose
Rencana cetak biru (*blueprint*) spesifik yang dihasilkan oleh *Planner Engine*. Menjadi panduan utama bagi seluruh *engine* di bawahnya.

### Fields
- `id` (UUID) - Identifier unik.
- `session_id` (String) - Identifier sesi percakapan.
- `created_at` (ISO 8601) - Waktu plan dibuat.
- `goal` (String) - Tujuan utama.
- `intent` (Enum: Operation)
- `priority` (String: LOW/MEDIUM/HIGH)
- `complexity` (String: LOW/MEDIUM/HIGH/EXTREME)
- `framework` (String) - Framework spesifik (misal: "Django").
- `language` (String) - Bahasa pemrograman.
- `provider_preference` (String) - Saran LLM (misal: "groq").
- `estimated_tokens` (Int)
- `estimated_duration` (Float)
- `files_to_modify`, `files_to_create`, `files_to_delete` (List[String]) - Absolute paths.
- `execution_steps` (List[String]) - Panduan step-by-step.
- `rollback_strategy` (String)
- `warnings`, `recommendations` (List[String])
- `metadata` (Dict)

### Extension Point
- **Diperbolehkan:** Plugin *boleh* menambahkan `execution_steps` tambahan atau menyisipkan `metadata`.
- **Dilarang:** Plugin *tidak boleh* menghapus atau mengubah `goal` utama.

### JSON Schema (Draft 2020-12)
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ExecutionPlan",
  "type": "object",
  "properties": {
    "id": { "type": "string", "format": "uuid" },
    "goal": { "type": "string" },
    "intent": { "type": "string" },
    "priority": { "type": "string", "enum": ["LOW", "MEDIUM", "HIGH"] }
  },
  "required": ["id", "goal", "intent"]
}
```

---

## 3. TransformationRequest
**Contract Level:** `[Stable]` | **Version:** `1.0`

### Purpose
Objek permohonan ke *Transformation Engine*. Membungkus instruksi, konteks memori, dan konfigurasi ketat bagi Provider LLM.

### Fields
- `id` (UUID)
- `execution_plan` (Object: ExecutionPlan)
- `context_bundle` (Object: ContextBundle)
- `mode` (Enum: Operation)
- `provider_options` (Dict) - Konfigurasi API key, base URL.
- `temperature` (Float)
- `top_p` (Float)
- `max_tokens` (Int)
- `retry_policy` (Object: RetryPolicy)
- `user_instruction` (String)
- `system_override` (String)

### Extension Point
- **Diperbolehkan:** Plugin keamanan *boleh* memanipulasi `provider_options` untuk merotasi API Key.
- **Dilarang:** Plugin *tidak boleh* menghapus `context_bundle`.

---

## 4. TransformationResult
**Contract Level:** `[Stable]` | **Version:** `1.0`

### Purpose
Hasil mutlak dari konversi spesifikasi menjadi blok kode oleh AI.

### Fields
- `success` (Boolean)
- `status` (Enum: Status)
- `operation` (Enum: Operation)
- `generated_files`, `modified_files`, `deleted_files` (List[String])
- `generated_code` (String)
- `explanation`, `summary` (String)
- `confidence` (Float 0.0 - 1.0)
- `estimated_cost` (Float)
- `retry_count` (Int)
- `warnings` (List[String])
- `raw_response` (String)
- `metadata` (Dict)

### Extension Point
- **Diperbolehkan:** Plugin metrik *boleh* menambahkan analitik pada `metadata`.
- **Dilarang:** Plugin *tidak boleh* mengubah isi `generated_code` sama sekali.

---

## 5. PatchResult & PatchObject
**Contract Level:** `[Stable]` | **Version:** `1.0`

### Purpose
Bukti forensik bahwa modifikasi fisik telah berhasil dihitung.

### Fields (PatchObject)
- `path` (String)
- `operation` (Enum: Operation)
- `old_hash` (String) - SHA256 file lama.
- `new_hash` (String) - Prediksi SHA256 file baru.
- `old_content` (String)
- `new_content` (String)
- `diff` (String) - Unified diff.
- `summary` (String)
- `warnings` (List[String])

### Fields (PatchResult)
- `success` (Boolean)
- `status` (Enum: Status)
- `patches` (List[PatchObject])
- `analysis` (Object: PatchAnalysis) - *Risk Assessment*
- `summary` (String)
- `additions`, `deletions` (Int)
- `warnings` (List[String])

### Fields (PatchAnalysis)
*Fitur keamanan tingkat lanjut untuk mendeteksi potensi kerusakan.*
- `risk_level` (Enum: LOW/MEDIUM/HIGH/CRITICAL)
- `risk_factors` (List[String]) - Alasan mengapa dilabeli risiko tersebut (misal: "Menghapus lebih dari 50 baris", "Memodifikasi file migrasi database").
- `needs_human_approval` (Boolean) - Paksaan untuk mematikan mode otonom jika risiko terlalu tinggi.

### Extension Point
- **Diperbolehkan:** Plugin Git *boleh* mengamati `diff` untuk di- *commit* secara otomatis.
- **Dilarang:** Plugin *tidak boleh* mengubah nilai `new_hash`.

---

## 6. ApprovalResult
**Contract Level:** `[Internal]` | **Version:** `1.0`

### Purpose
Keputusan akhir apakah Patch diizinkan dieksekusi secara fisik ke *disk*. Mendukung persetujuan sebagian (*Partial Approval*).

### Fields
- `approved` (Boolean)
- `approved_by` (String) - e.g., "USER", "CRITIC_AI"
- `approved_files` (List[String]) - Daftar path yang disetujui.
- `rejected_files` (List[String]) - Daftar path yang ditolak.
- `comment` (String) - Alasan penolakan.

---

## 7. VerificationResult
**Contract Level:** `[Experimental]` | **Version:** `1.0`

### Purpose
Memastikan kode berjalan sempurna setelah ditulis. Tidak hanya sintaksis, namun meluas ke keamanan dan performa.

### Fields
- `syntax_ok`, `compile_ok`, `tests_passed` (Boolean)
- `coverage` (Float)
- `security_scan` (Dict) - Kerentanan yang terdeteksi (misal: *SQL Injection*).
- `performance_check` (Dict) - Peringatan kebocoran memori (OOM).
- `dependency_check` (Dict) - Peringatan *package* kadaluwarsa.
- `lint_warnings`, `recommendation` (List[String])

---

*(Catatan: Object pelengkap seperti `ContextBundle`, `RetryPolicy`, `Metrics`, `ExecutionRequest`, `ExecutionResult`, `AuditTrail`, dan `EventContext` memiliki skema hierarki dan Extension Point yang serupa dalam rancangan JSON Schema Draf 2020-12).*
