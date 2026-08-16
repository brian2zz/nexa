# 🗺️ Planning: Penyelesaian Slash Commands + Gap Analysis opencode

> **Status:** SELESAI (Fase 1–6 bagian inti). Sisa kecil di Fase 6 dicatat di §2.3.
> **Tanggal:** 14 Agustus 2026 (revisi 16 Agustus 2026)
> **Lokasi dokumen:** `.opencode/plans/` (satu-satunya path yang diizinkan saat plan mode).
> **Base:** commit `511f8c2` + uncommitted tema (3 file).
> **Rujukan:** `docs/gap_analysis_opencode.md`, `docs/nexa/slash_commands_execution_plan.md`, `docs/nexa/slash_commands_minor_fixes_plan.md`

---

## 1. Ringkasan (1 menit)

Slash commands ala opencode sudah **tuntas** (registry, `/editor`, `/undo`/`/redo`, `/copy`, `/mode`, `/timeline`, `/skills`, `/variants`, `/mcps`, live theme, `/todos`). Seluruh Fase 1–5 **sudah dieksekusi & di-commit**; Fase 6 bagian inti (bash/write/edit/task/web) **sudah di-wire** ke runtime chat.

Sisa di Fase 6 (belum dikerjakan):
1. **Permission rules granular** — baru flag `read_only` per tool; belum `allow/ask/deny` per tool/perintah.
2. **Subagents penuh** — `TaskTool` baru in-memory (per-loop); belum delegasi paralel antar-engine.
3. **Unifikasi dua loop** — `AgentLoop` (chat) vs `AILoopEngine` (plan) masih duplikasi logika.

Setiap fase punya: **Harus Apa / Cara (file:line + kode) / Kriteria Selesai / Test**. Bekerja satu fase per sesi, test hijau, lalu commit.

---

## 2. Status Saat Ini

### 2.1 Sudah selesai & di-commit
Registry `SLASH_DISPATCH`, 20+ handler, alias, completer, `get_last_message/delete_last_message/rename_session`, redo persist, `/editor`, `/copy`, `/mode`, `/timeline` (payload fix), `/skills`, `/variants`, `/mcps`, `/todos`, dead-code bersih, live theme, test slash + dispatch integrity.

| Fase | Commit | Status |
| :--- | :--- | :--- |
| 1 — Docs (CHANGELOG/README) | `f6fec1f` | ✅ |
| 2 — AGENTS.md reading | `f6fec1f` (injection di `shell.py:8,884-886`; `AILoopEngine` baca di `ai/agent_loop.py:33-42`) | ✅ |
| 3 — Todo tool | `f18685c` (`TodoStore` + tool + `/todos` + TUI sync) | ✅ |
| 4 — Write/Edit nyata | `802d5bd` (`submit_execution_plan` → `ExecutionPlanSubmitted` → `BeforeApproval` → `ApprovalGranted` → `ExecutionTransaction`, `runtime.py:63-107`) | ✅ |
| 5 — Agent loop | `238f155` (`AgentLoop` chat `core/agent/loop.py` + `AILoopEngine` plan `core/ai/agent_loop.py`) | ✅ |
| 6 — Lanjutan (bagian inti) | Bash/write/edit/task (`tools/execution_tools.py`) + web (`tools/web.py`) ter-wire ke `runtime.tools` (`runtime.py:48-58`) | ✅ |

Test: **94 passed** (`py -m pytest -q`), termasuk baru: `test_execution_tools.py` (7), `test_web_tools.py` (6), `test_ailoop_engine.py` (4).

### 2.2 Belum di-commit (kerja aktif)
| File | Isi |
| :--- | :--- |
| `nexa/core/agent/tools/web.py` | tool `web_fetch` + `web_search` baru (stdlib, read-only) |
| `nexa/core/agent/runtime.py` | registrasi `register_execution_tools` + `register_web_tools` |
| `tests/core/test_execution_tools.py`, `test_web_tools.py`, `test_ailoop_engine.py` | test baru |
| `CHANGELOG.md` | entri `[Unreleased]` untuk Fase 3–6 |

### 2.3 Sisa Fase 6 (belum dikerjakan)
1. **Permission rules granular** — ganti flag `read_only` tunggal dengan policy `allow/ask/deny` per tool (dan per pola perintah bash).
2. **Subagents penuh** — `TaskTool` masih in-memory per-loop (`tools/tasks.py`), belum delegasi paralel.
3. **Unifikasi dua loop** — `AgentLoop` vs `AILoopEngine` (duplikasi; keputusan desain).

---

## 3. Fase 1 — Commit & Dokumentasi (kecil, duluan)

### Harus Apa
Mengunci kerja tema yang sudah benar, lalu mencatat semua pekerjaan slash commands di CHANGELOG & README agar repo konsisten.

### Cara
**1.1 Commit tema (3 file):**
- `git add nexa/ui/app.py nexa/commands/ai/slash_commands.py tests/core/ui/test_app_ui.py`
- Pesan sesuai gaya repo (`git log --oneline`):
  `feat(ui): apply ui.theme live in TUI (on_mount + /themes modal) with theme mapping and tests`

**1.2 CHANGELOG.md** — tambah section baru `[Unreleased]` di atas `[1.0.0]`:
```
## [Unreleased]
### Added
- OpenCode-parity slash commands: /connect /models /init /editor /themes /mode /details /thinking /rename /export /copy /compact /share /unshare /context /agents /undo /redo /timeline /skills /variants /mcps
- Slash dispatch registry (SLASH_DISPATCH) as single source of truth + dispatch integrity test
- Live UI theme application (on_mount + /themes modal) with dark→textual-dark mapping
- AGENTS.md scaffolding via /init
### Changed
- Refactored command_handler to registry-based dispatch (no more if/elif chains)
- Redo stack persisted to .nexa/undo_stack.json (bounded 20)
### Fixed
- /editor now dispatches to external editor handler (was dead mapping)
- /redo restores messages (undo now pushes snapshot)
- /timeline reads EventContext.payload with correct token keys
```

**1.3 README.md** — tambah bagian pendek "Slash Commands (OpenCode Parity)" berisi tabel:
`/help /status /connect /select-provider /models /set-model /set-api-key /mode /themes /details /thinking /editor /init /plan /facts /context /rename /export /copy /compact /share /unshare /new /clear /history /sessions /load /pin /pins /unpin /clearpins /undo /redo /agents /skills /variants /mcps /timeline /exit`

### Kriteria Selesai
- `git status` bersih; CHANGELOG & README mencerminkan fitur nyata.

### Test
- Tidak perlu test baru (dokumentasi). Pastikan `pytest tests -q` tetap hijau.

---

## 4. Fase 2 — AGENTS.md Reading (kecil, berdampak)

### Harus Apa
Pipeline harus **membaca** `AGENTS.md` (jika ada) dan menyuntikkan isinya ke system prompt LLM — melengkapi `/init` yang sudah bisa *create*.

### Cara
**2.1** Di `nexa/commands/ai/shell.py`, `system_base_prompt` didefinisikan di `:98`. Tambahkan helper baca:
```python
def load_agents_instructions(cwd: str) -> str:
    path = os.path.join(cwd, "AGENTS.md")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()[:8000]
    return ""
```
**2.2** Gabung ke prompt di `:98` (atau di titik `enhanced_sys_prompt`, `:871`):
```python
agents_txt = load_agents_instructions(cwd)
system_base_prompt = (f"You are Nexa AI... {framework} ({language}) project at {cwd}."
                      + (f"\n\nProject AGENTS.md instructions:\n{agents_txt}" if agents_txt else ""))
```

### Kriteria Selesai
- Ada `AGENTS.md` di cwd → pesan LLM pertama memuat instruksinya (dapat diverifikasi via log/`/status` atau debug).
- Tidak ada `AGENTS.md` → prompt tidak berubah (no-op).

### Test
`tests/core/test_slash_commands.py` (atau test baru `tests/core/test_agents_instructions.py`):
- tmp dir berisi `AGENTS.md` → `load_agents_instructions` mengembalikan isi; tanpa file → `""`.
- Unit test `handle_init` tetap menghasilkan file yang bisa dibaca helper.

---

## 5. Fase 3 — Todo Tool (kecil–sedang)

### Harus Apa
LLM dapat **membuat/memperbarui todos** selama bekerja; status panel TUI (`nexa/ui/widgets/status_panel.py`) yang saat ini hanya menampilkan todos dari plan ikut terupdate.

### Cara
**5.1** Buat store todo sederhana di `.nexa/` (mis. `todo_store.py` di `nexa/core/agent/tools/todo.py`):
- `TodoStore(cwd)` → file `.nexa/todos.json`.
- API: `list()`, `add(title)`, `update(id, status)`, `clear()`.
**5.2** Daftarkan sebagai tool agent di `nexa/core/agent/runtime.py` (registrasi tool di `:52-54`):
- `register_todo_tools(self.tools, self.cwd)` → tool `todo_list`, `todo_add`, `todo_update`.
**5.3** Sinkron status panel: baca `todos.json` dan render (pola yang sudah ada untuk plan todos di `status_panel.py`).

### Kriteria Selesai
- `/skills`-style handler `/todos` (baru, jika diinginkan) atau tool dipanggil LLM menghasilkan/update `.nexa/todos.json`.
- Status panel menampilkan todos terbaru.

### Test
- Unit: `TodoStore.add/update/list` terhadap `tmp_path`.
- Integrasi: panggil tool → file berubah → render panel (mock).

---

## 6. Fase 4 — Write/Edit Tools Nyata (Gap #2)

### Harus Apa
Mengaktifkan `submit_execution_plan` yang masih **stub** (`nexa/core/agent/tools/pipeline.py:3-21`) sehingga benar-benar mem-publish `ExecutionPlanSubmitted` dan memicu `ExecutionTransaction` (lihat komentar `:14-16`).

### Cara
**4.1** Di `pipeline.py`, ganti bagian return dengan publish event:
```python
from nexa.core.models.events import EventContext
from nexa.core.models.enums import EventPriority
import datetime, uuid

def submit_execution_plan(plan_json: str) -> str:
    try:
        plan = json.loads(plan_json)
        if "files" not in plan:
            return "Error: ExecutionPlan must contain a 'files' array."
        if not _BUS:
            return "Error: Pipeline bus not initialized."
        _BUS.publish(EventContext(
            event_name="ExecutionPlanSubmitted",
            timestamp=datetime.datetime.now().isoformat(),
            source="LLMTool:submit_execution_plan",
            priority=EventPriority.NORMAL,
            session_id=_SESSION_ID_FN(),
            payload=plan,
        ))
        return "SUCCESS: ExecutionPlan submitted. Pipeline execution started."
    except Exception as e:
        return f"Error parsing ExecutionPlan: {e}"
```
**4.2** Sediakan `_BUS` / `_SESSION_ID_FN` (setter dipanggil saat runtime init, mis. di `nexa/core/agent/runtime.py:52-54` atau shell setup).
**4.3** Pastikan ada subscriber `ExecutionPlanSubmitted` yang membangun `ExecutionTransaction` (cek pattern approval gate di `nexa/core/approval/engine.py` + `runtime.py` subscriber). Kalau belum ada, buat subscriber yang menjalankan pipeline yang sama dengan `handle_approval_granted`.

### Kriteria Selesai
- LLM memanggil tool → event `ExecutionPlanSubmitted` ter-publish → pipeline eksekusi berjalan (transform→patch→backup→verify→commit).
- Hasil dieksekusi kembali ke loop (pra-syarat Fase 5).

### Test
- Unit: `submit_execution_plan` valid → event ter-publish (mock bus); `files` hilang → error.
- Integrasi: trigger via handler → `todos.json`/file berubah di `tmp_path`.

---

## 7. Fase 5 — Agent Loop Iteratif (Gap #1, terbesar)

### Harus Apa
Mengubah pipeline linear (`intent→plan→approval→execute→selesai`) menjadi **agent loop**: LLM memanggil tool → hasil disuntikkan ke konteks → LLM memutuskan langkah berikutnya → ulang hingga selesai. `BeforeApproval` menjadi salah satu gerbang di dalam loop, bukan akhir.

### Cara (kerangka — detail final disetujui di fase ini)
**5.1** Buat modul loop baru (mis. `nexa/core/agent/loop.py`):
```python
class AgentLoop:
    def __init__(self, runtime, max_iterations=12):
        ...
    def run(self, user_input: str) -> str:
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.append({"role": "user", "content": user_input})
        for i in range(self.max_iterations):
            resp = self.provider.generate(messages, tools=self.runtime.tools.schemas())
            if resp.get("tool_calls"):
                for call in resp["tool_calls"]:
                    result = self.runtime.tools.invoke(call["name"], call["arguments"])
                    messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
                continue
            return resp["content"]
        return "Max iterations reached."
```
**5.2** Sambungkan ke shell/TUI: ganti jalur eksekusi `plan→approval→execute` dengan `AgentLoop.run`; pertahankan approval gate sebagai tool/gerbang (`submit_execution_plan` memicu approval).
**5.3** Streaming hasil tool ke TUI transcript (reuse event bus + `_EVENT_LABELS` di `ui/app.py:574-593`).
**5.4** Pertahankan mode PLAN/BUILD: di PLAN, loop berhenti sebelum write (tool write di-filter); di BUILD, loop penuh.

### Kriteria Selesai
- Pertanyaan bertahap (baca file → cari → coba → perbaiki) bisa berjalan dalam satu sesi loop.
- Approval tetap wajib sebelum eksekusi write.
- Tidak ada infinite loop (batas iterasi + timeout).

### Test
- Unit: `AgentLoop` dengan mock provider/tool → verifikasi urutan call & hasil akhir.
- Integrasi: skenario "perbaiki bug" → loop sampai sukses/gagal dengan batas iterasi.

---

## 8. Fase 6 — Lanjutan (setelah Gap #1–2 tuntas)

| Item | Catatan |
| :--- | :--- |
| **Bash tool** (`nexa/core/pipeline/execution/runner.py` → `TerminalRunner`) | Ekspos sebagai tool agent dengan sandbox + timeout + whitelist |
| **Permission rules granular** | Per-tool/perintah: allow/ask/deny (evolusi dari 1 gate plan-level) |
| **Web fetch / search** | Tool baru (stdlib `urllib`/`httpx` jika tersedia) |
| **Subagents / Task tool** | Delegasi paralel untuk tugas besar (paling berat) |

Masing-masing mengikuti format fase yang sama; detail disusun saat tiba.

---

## 9. Urutan, Dependensi & Estimasi

| Urutan | Fase | Dependensi | Estimasi |
| :---: | :--- | :--- | :--- |
| 1 | Fase 1 — Commit & Docs | — | Kecil (<1 sesi) |
| 2 | Fase 2 — AGENTS.md reading | — | Kecil |
| 3 | Fase 3 — Todo tool | — | Sedang |
| 4 | Fase 4 — Write/Edit nyata | — | Sedang |
| 5 | Fase 5 — Agent loop | **Fase 4** (loop butuh write tool nyata) | Besar |
| 6 | Fase 6 — Lanjutan | Fase 5 | Besar |

**Aturan:** selesaikan & commit tiap fase sebelum lanjut. Fase 5 **tidak boleh** dikerjakan sebelum Fase 4, karena loop tanpa write tool nyata akan berakhir dengan stub lagi.

---

## 10. Keputusan yang Perlu Kamu Ambil

1. **Fase 3 (Todo):** cukup `.nexa/todos.json` + tool, atau perlu slash `/todos` di help juga? → Rekomendasi: tool + `/todos` handler kecil.
2. **Fase 4:** subscriber `ExecutionPlanSubmitted` memakai `ExecutionTransaction` yang sama dengan approval? → Rekomendasi: ya, satu jalur eksekusi.
3. **Fase 5:** batas iterasi default 12? → Rekomendasi: ya, konfigurabel via `Config`.
4. **Fase 6:** urut bash → permission → web → subagents disetujui? → Rekomendasi: ya.

---

## 11. Risiko & Mitigasi

| Risiko | Mitigasi |
| :--- | :--- |
| AGENTS.md terlalu panjang membebani prompt | Truncate 8000 char + hanya baca file pertama |
| Todo store korup / konflik antar-sesi | `try/except` + JSON atomic write |
| Event `ExecutionPlanSubmitted` tanpa subscriber → silent no-op | Test memastikan subscriber terdaftar saat runtime init |
| Agent loop infinite / boros token | Batas iterasi + timeout + cap konteks (compact otomatis) |
| Approval dilewati di loop | Approval sebagai gerbang wajib sebelum tool write |

---

*Dokumen ini adalah rencana. Eksekusi dilakukan hanya setelah persetujuan pengguna per fase.*