# Review Implementasi Phase 1-3: Agent Loop, Toolset & Ekosistem

**Tanggal**: 09 Agustus 2026
**Status**: Review kode (belum ada perbaikan diterapkan)
**Cakupan**: Implementasi yang baru diterapkan di working tree (belum commit)
**Hasil test**: 51 passed, 4 warnings — **namun tidak meng-cover file baru**, sehingga error fatal di `agent_loop.py` tidak terdeteksi.

---

## 1. Ringkasan

Implementasi mencoba menutup gap vs opencode (lihat `docs/gap_analysis_opencode.md`) dengan memperkenalkan:

- **Agent loop iteratif** — `nexa/core/ai/agent_loop.py` (`AILoopEngine`), menggantikan `AIPlannerEngine` yang linear.
- **Toolset eksekusi** — `nexa/core/agent/tools/terminal.py`, `filesystem.py`, `tasks.py`, `execution_tools.py` (bash, write, edit, list, task management).
- **Integrasi TUI** — modal approval & clarification per-tool, status panel tugas dinamis (`AgentTasksUpdated`).
- **AGENTS.md** — dibaca & disuntikkan ke system prompt agent loop.

Secara arsitektur, arahnya sudah benar (dari pipeline linear → loop otonom). Namun ditemukan **6 bug kritis** yang membuat fitur tidak berjalan, atau berpotensi berbahaya (eksekusi ganda), plus **2 bug medium** dan **1 gap pengujian**.

---

## 2. Hasil Pemeriksaan

### 2.1 Verifikasi Lingkungan

| Pemeriksaan | Hasil |
| :--- | :--- |
| `import nexa.core.ai.agent_loop` | ❌ `ImportError: cannot import name 'PlannerReport' from 'nexa.core.ai.planner.schema'` |
| `import nexa.core.agent.tools.execution_tools` (dsb.) | ✅ OK |
| `py -m pytest tests -q` | 51 passed, 4 warnings (DeprecationWarning sqlite3) |
| Test yang meng-cover file baru | ❌ Tidak ada |

---

## 3. Bug Kritis (harus diperbaiki sebelum fitur aktif)

### B1. ImportError fatal di `AILoopEngine`
- **Lokasi**: `nexa/core/ai/agent_loop.py:11`
- **Masalah**: `from nexa.core.ai.planner.schema import ... PlannerReport ...` — `PlannerReport` didefinisikan di `nexa/core/ai/planner/report.py`, **bukan** di `schema.py`.
- **Dampak**: `import nexa.core.ai.agent_loop` gagal total → seluruh jalur PLAN di shell.py mati saat runtime.
- **Perbaikan**: import dari `nexa.core.ai.planner.report import PlannerReport` (atau dari `nexa.core.ai.planner` yang sudah re-export).

### B2. Nama event clarification/tool tidak konsisten
- **Lokasi**: `agent_loop.py:171` subscribe `"PlanningRevisionRequested"`; `app.py:328` & `runtime.py:183` publish `"PlanRevisionRequested"` (tanpa `-ning-`).
- **Dampak**: user klik "Provide Feedback (C)" di ApprovalModal → event `PlanRevisionRequested` ter-publish, tetapi subscriber agent_loop menunggu `PlanningRevisionRequested` → **tidak pernah terbangun**, loop hang sampai timeout.

### B3. Tombol "No, Abort" menyebabkan hang
- **Lokasi**: `app.py:320-321` (action `"no"` hanya print ke chat, tidak publish event); `agent_loop.py:176-177` hanya subscribe `ApprovalGranted` & `PlanningRevisionRequested`.
- **Dampak**: klik "No" → tidak ada event yang membangunkan `approval_event` → `wait()` menggantung (diperparah B5 tanpa timeout).
- **Perbaikan**: publish `ApprovalRejected` pada action `"no"`; agent_loop subscribe `ApprovalRejected`.

### B4. Eksekusi ganda `ApprovalGranted` (berbahaya)
- **Lokasi**: `runtime.py:127` (`handle_approval_granted` → `ExecutionTransaction`) DAN `agent_loop.py:176` (subscriber yang sama, untuk mengeksekusi tool).
- **Dampak**: keduanya aktif bersamaan di TUI. Klik "Yes" pada modal approval tool → **dua jalur berjalan**:
  1. `agent_loop` mengeksekusi tool (mis. `run_bash_command`).
  2. `runtime.handle_approval_granted` memperlakukan dummy plan (`ExecutionPlan` berisi `CommandStep` tool) sebagai **transaksi filesystem**, memicu `ExecutionTransaction` pada data yang bukan rencana file → salah eksekusi / error.
- **Perbaikan**: beri tanda pada payload `BeforeApproval` (mis. `tool_approval: True`); guard di `runtime.handle_approval_granted` agar mengabaikan approval tool-loop. Alternatif: agent_loop tidak memakai event bus `ApprovalGranted` untuk tool internal.

### B5. `approval_event.wait()` tanpa timeout
- **Lokasi**: `agent_loop.py:189`
- **Dampak**: modal ditutup tanpa jawaban (Escape/exit) → worker thread menggantung selamanya. Ini pola yang sama dengan bug `shell.py` yang sudah diperbaiki sebelumnya.
- **Perbaikan**: `wait(timeout=60)` + treat timeout sebagai "abort".

### B6. Subscribe tanpa `try/finally`
- **Lokasi**: `agent_loop.py:176-191`
- **Dampak**: bila exception terjadi di antara subscribe dan unsubscribe, subscriber `ApprovalGranted`/`PlanRevisionRequested` bocor (menumpuk di bus).
- **Perbaikan**: bungkus dalam `try/finally` (pola yang sama dengan fix `shell.py`).

---

## 4. Bug Medium

### B7. Tidak berfungsi dengan provider mock (default)
- **Lokasi**: `agent_loop.py:_build_system_prompt` (tidak memuat token intent); `mock.py:generate`
- **Dampak**: `MockProvider` memilih intent via deteksi teks (`"planning engine"`, `"nexa ai planner"`). System prompt `AILoopEngine` tidak mengandung token tersebut → mock mengembalikan `{"status":"mocked_success","data":[]}` yang bukan JSON plan → parse selalu gagal. **Fitur tidak dapat dites/dijalankan secara lokal tanpa provider asli.**
- **Perbaikan**: tambahkan token intent di system prompt agent loop, atau perbaiki deteksi `MockProvider` untuk jalur agent-loop.

### B8. Plan hasil loop tidak dirender
- **Lokasi**: `shell.py:671-674`
- **Masalah**: cek `hasattr(report.plan, "to_markdown")` — `PlanningResult` tidak punya method tersebut (hanya `PlannerReport` yang punya). Selalu jatuh ke fallback `"Plan generated successfully."`
- **Perbaikan**: gunakan `PlanFormatter().to_markdown(plan)`.

---

## 5. Gap Pengujian

### B9. Tidak ada test untuk modul baru
File berikut **tidak memiliki test sama sekali**, dan suite saat ini tidak meng-import `agent_loop.py`:
- `nexa/core/ai/agent_loop.py`
- `nexa/core/agent/tools/execution_tools.py`
- `nexa/core/agent/tools/terminal.py`
- `nexa/core/agent/tools/filesystem.py`
- `nexa/core/agent/tools/tasks.py`

Perlu test minimal:
1. Import `agent_loop` berhasil (menangkap B1).
2. Tool `write_file`/`edit_file_content`/`list_directory`/`run_bash_command`/`manage_tasks` berfungsi & path-traversal di-block.
3. Alur modal approval TUI: Yes / No / Comment masing-masing mem-publish event yang benar (menangkap B2-B3).
4. Loop agent dengan mock provider menghasilkan `PlannerReport` sukses (menangkap B7).

---

## 6. Daftar File yang Terlibat

| File | Peran | Status |
| :--- | :--- | :--- |
| `nexa/core/ai/agent_loop.py` | `AILoopEngine` — loop iteratif baru | Baru |
| `nexa/core/agent/tools/terminal.py` | Tool `run_bash_command` | Baru |
| `nexa/core/agent/tools/filesystem.py` | Tool `write_file`, `edit_file_content`, `list_directory` | Baru |
| `nexa/core/agent/tools/tasks.py` | Tool `manage_tasks` | Baru |
| `nexa/core/agent/tools/execution_tools.py` | Registrasi tool eksekusi | Baru |
| `nexa/commands/ai/shell.py` | Ganti `AIPlannerEngine` → `AILoopEngine`; clarification gate TUI | Dimodifikasi |
| `nexa/ui/app.py` | Modal clarification; handler `AgentTasksUpdated`; approval per-tool | Dimodifikasi |
| `nexa/ui/widgets/status_panel.py` | `set_agent_tasks` (checklist dinamis) | Dimodifikasi |
| `tests/core/ui/test_app_ui.py` | Test clarification + status panel | Dimodifikasi |
| `nexa/ui/screens/clarification.py` | `ClarificationModal` | Baru |

---

## 7. Rekomendasi Prioritas Perbaikan

| # | Perbaikan | Prioritas | Menutup |
| :--- | :--- | :---: | :--- |
| 1 | Import `PlannerReport` benar | P0 | B1 |
| 2 | Uniform nama event (`PlanRevisionRequested`) | P0 | B2 |
| 3 | Publish/subscribe `ApprovalRejected` | P0 | B3 |
| 4 | Guard `runtime.handle_approval_granted` utk tool-loop | P0 | B4 |
| 5 | `wait(timeout=60)` + `try/finally` | P0 | B5, B6 |
| 6 | Dukungan provider mock untuk agent loop | P1 | B7 |
| 7 | Render plan via `PlanFormatter` | P1 | B8 |
| 8 | Tambahkan test untuk modul & alur baru | P1 | B9 |

**Catatan**: P0 = fitur tidak berjalan / berbahaya; P1 = kualitas & keterujian.
