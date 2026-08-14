# 🧭 Rencana: Semua `/` Command ala opencode di Shell Nexa

> **Status:** Rencana (belum dieksekusi — hanya dokumen)
> **Tanggal:** 14 Agustus 2026
> **File terkait:** `nexa/commands/ai/shell.py`, `nexa/commands/ai/completer.py`, `nexa/commands/ai/slash_commands.py` (baru), `nexa/core/ai/memory/core.py`, `nexa/core/pipeline/rollback/backup.py`, `nexa/core/observability/usage_tracking.py`, `nexa/config/__init__.py`

---

## 1. Latar Belakang

Pengguna meminta agar **semua slash command (`/...`) milik opencode** tersedia di shell `nexa ai` untuk mencapai paritas fitur. Saat ini shell Nexa memiliki 22 command bawaan (`/help`, `/clear`, `/history`, `/load`, `/session`, `/dir`, `/plan`, dll.), tetapi banyak command inti opencode belum ada.

### 1.1 Slash command opencode (17 built-in resmi)

`/connect` · `/compact` (alias `/summarize`) · `/details` · `/editor` · `/exit` (alias `/quit`, `/q`) · `/export` · `/help` · `/init` · `/models` · `/new` (alias `/clear`) · `/redo` · `/sessions` (alias `/resume`, `/continue`) · `/share` · `/themes` · `/thinking` · `/undo` · `/unshare`

### 1.2 Ekstended (versi terbaru opencode)

`/agents` · `/skills` · `/variants` · `/mcps` · `/status` · `/context` · `/timeline` · `/rename`

---

## 2. Keputusan Desain (sudah dikonfirmasi pengguna)

| Keputusan | Pilihan |
| :--- | :--- |
| Cakupan target | **Shell terminal + registry** — flag TUI (`themes/details/thinking`) menjadi setelan config dulu |
| Command butuh backend | **Lokal minimal** — `/share` & `/unshare` dipetakan ke export markdown lokal; `/undo` & `/redo` pakai backup + stack `.nexa` (**tanpa** `git reset --hard`) |
| Daftar extended | **Semua** — `/context` & `/rename` diimplementasikan; `/agents`, `/skills`, `/variants`, `/mcps`, `/timeline` sebagai **stub dengan pesan jelas** |

---

## 3. Peta Status vs Shell Nexa Saat Ini

| opencode | Status di Nexa | Rencana |
| :--- | :--- | :--- |
| `/help` | ✅ ada | tetap |
| `/exit` `/quit` | ✅ ada | + alias `/q` |
| `/new` `/clear` | ⚠️ `/clear` ada | + alias `/new` → `new_chat_session()` |
| `/sessions` | ⚠️ `/session list/enter/delete` ada | + alias `/resume`, `/continue` |
| `/select-provider` + `/set-api-key` | ✅ ada (dasar) | **+ `/connect`** komposit (pilih provider + isi key) |
| `/set-model` | ✅ ada (dasar) | **+ `/models`** (daftar semua model per provider) |
| `/status` | ✅ ada | tetap |
| `/compact` | ❌ belum | **baru** — ringkas percakapan via `load_session_messages` + LLM |
| `/editor` | ❌ belum | **baru** — buka `$EDITOR`/notepad, isi jadi pesan |
| `/export` | ❌ belum | **baru** — tulis percakapan ke `.md` |
| `/init` | ❌ belum | **baru** — wizard pembuatan `AGENTS.md` |
| `/undo` | ❌ belum | **baru** — hapus pesan terakhir + revert file via `BackupRollbackStrategy` |
| `/redo` | ❌ belum | **baru** — restore aksi yang di-undo (stack di `.nexa`) |
| `/themes` | ❌ belum | **baru** — daftar/terapkan tema (config `ui.theme`) |
| `/details` `/thinking` | ❌ belum | **baru** — toggle flag config (`ui.details` / `ui.show_reasoning`) |
| `/share` `/unshare` | ❌ belum | **lokal minimal** — export markdown lokal + catatan "sharing online belum tersedia" |
| `/context` | ❌ belum | **baru** — ringkasan token/usage via `usage_tracking` (event `TokenUsage`) |
| `/rename` | ❌ belum | **baru** — `UPDATE` kolom `name` tabel `sessions` (kolom sudah ada, tanpa migrasi) |
| `/agents` | ❌ belum | **baru** — tampilkan konfigurasi `NexaAgentRuntime` |
| `/skills` `/variants` `/mcps` `/timeline` | ❌ belum | **stub** — pesan jelas "belum didukung di Nexa" |

---

## 4. Referensi Kode Terkait (hasil analisis)

| Modul | Referensi | Peran |
| :--- | :--- | :--- |
| `nexa/commands/ai/shell.py` | `command_handler` baris 174 (rantai `elif`), `print_help` baris 6, `show_status` baris 41, `NestedCompleter.from_nested_dict` baris 128 (`slash_completer`), app start baris 897/907 | Titik masuk utama refactor |
| `nexa/commands/ai/completer.py` | `DynamicModelCompleter` baris 53 (daftar model per provider) | Dipakai ulang oleh `/models`; tambah daftar slash baru |
| `nexa/config/__init__.py` | `Config.get(key, default)` / `Config.set(key, value)` | State `/themes`, `/details`, `/thinking`, `/connect`, `/models` |
| `nexa/core/ai/memory/core.py` | `load_session_messages`, `save_message`, `new_chat_session`, `delete_session`, `set_active_session`; kolom `name` di `sessions` baris 70 | Dasar `/export`, `/compact`, `/undo`, `/rename` |
| `nexa/core/pipeline/rollback/backup.py` | `BackupRollbackStrategy.backup/rollback/commit` | Dasar `/undo` & `/redo` (tanpa git reset) |
| `nexa/core/observability/usage_tracking.py` | `UsageTrackingProvider` mempublish event `TokenUsage` (prompt/completion tokens) ke `PipelineBus` | Dasar `/context` |

---

## 5. Rencana Implementasi

### Langkah 1 — Refactor `command_handler` ke Registry
- Ubah rantai `if/elif` di `shell.py:174` menjadi **dict `SLASH_COMMANDS: {name: handler_fn}`**.
- `NestedCompleter` (baris 128) dan `/help` di-**generate dari registry** — satu sumber kebenaran, autocomplete otomatis lengkap.
- Alias di-resolve lewat pemetaan terpisah (`/q`, `/new`, `/resume`, `/continue`, `/summarize`).

### Langkah 2 — Modul baru `nexa/commands/ai/slash_commands.py`
Handler untuk setiap command baru:

| Command | Implementasi |
| :--- | :--- |
| `/connect` | wizard: pilih provider → input API key (`getpass`) → `Config.set` |
| `/models` | daftar model tiap provider (reuse `DynamicModelCompleter`) + pilih (gabung `/set-model`) |
| `/compact` | `load_session_messages` → LLM ringkas → simpan ringkasan sebagai pesan baru |
| `/editor` | temp file + buka `$EDITOR`/notepad → isi jadi pesan user |
| `/export` | tulis percakapan ke `exports/chat_<ts>.md` (di cwd) |
| `/init` | wizard pembuatan `AGENTS.md` |
| `/undo` | hapus pesan terakhir (DB) + revert file via `.nexa/backups` — **konfirmasi dulu** |
| `/redo` | restore pesan/aksi (stack di `.nexa/undo_stack.json`) |
| `/themes` | daftar tema Textual + set `ui.theme` di config |
| `/details` `/thinking` | toggle `ui.details` / `ui.show_reasoning` di config |
| `/share` `/unshare` | export markdown lokal + catatan sharing online belum tersedia |
| `/rename` | `UPDATE` nama sesi di tabel `sessions` (helper kecil di `chat_memory`) |
| `/context` | ringkasan token/usage dari event `TokenUsage` (`usage_tracking`) |
| `/agents` | tampilkan konfigurasi `NexaAgentRuntime` (nama agent, platform) |
| `/skills` `/variants` `/mcps` `/timeline` | stub: pesan jelas "belum didukung di Nexa" |

### Langkah 3 — Sinkronisasi
- Update `print_help()` — daftar lengkap semua command (di-generate dari registry).
- Update `nexa/commands/ai/completer.py` — daftar slash nama.
- Update README (section `nexa ai shell`) + CHANGELOG.

### Langkah 4 — Test
- File baru: `tests/core/test_slash_commands.py`
- Verifikasi: setiap command punya handler di registry; alias me-resolve benar; `/help`, `/export`, `/context`, `/init` jalan tanpa crash di env test.

### Langkah 5 — Verifikasi Akhir
- `py -3.14 -m nexa.ai shell` (atau entrypoint shell yang digunakan) → jalankan `/help`, `/export`, `/context`, `/init`.
- `pytest tests -q` → semua hijau.
- Pastikan command Nexa lama (`/plan`, `/facts`, `/pin`, `/dir`, dsb.) tidak rusak.

---

## 6. Peringatan Breaking / Perhatian

| Hal | Catatan |
| :--- | :--- |
| Nama `command_handler`/struktur internal | Refactor internal hanya — tidak mengubah entrypoint CLI eksternal |
| `/undo` | Menghapus pesan terakhir & revert file via backup (`.nexa/backups`, **tanpa** `git reset --hard`); **konfirmasi pengguna sebelum revert** |
| `/share`/`/unshare` | Terdengar seperti "sharing online", padahal hanya export lokal — pesan transparan agar tidak membingungkan |
| Command terbaru opencode (variants/mcps/timeline) | Stub jujur, bukan fake — roadmap ke depan |

---

*Dokumen ini adalah rencana eksekusi. Eksekusi dilakukan **hanya** setelah persetujuan pengguna dan tidak ada kode yang diubah saat dokumen ini diterbitkan.*