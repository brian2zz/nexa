# 🛠️ Rencana Perbaikan: Audit Implementasi Slash Commands opencode

> **Status:** Rencana perbaikan (belum dieksekusi — hanya dokumen)
> **Tanggal:** 14 Agustus 2026
> **File terkait:** `nexa/commands/ai/shell.py`, `nexa/commands/ai/slash_commands.py`, `nexa/core/ai/memory/core.py`, `nexa/core/pipeline/rollback/backup.py`, `nexa/core/ai/providers/base.py`, `tests/core/test_slash_commands.py`
> **Rujukan:** `docs/nexa/slash_commands_opencode_plan.md`

---

## 1. Latar Belakang

Rencana awal (lihat `slash_commands_opencode_plan.md`) sudah sebagian besar diimplementasikan oleh session lain: `SlashCommandHandler` baru, dispatch di `command_handler`, completer +35 command, alias (`/q`, `/new`, `/summarize`, `/resume`, `/continue`), method `rename_session`, dan test dasar.

Audit ulang menemukan **3 bug nyata** yang akan crash/malformed saat dijalankan, **1 fitur tidak lengkap**, **dead code**, dan **celah coverage test**.

## 2. Temuan Audit

### 2.1 Bug Kritis

| # | Lokasi | Masalah | Dampak |
| :-- | :--- | :--- | :--- |
| 1 | `slash_commands.py:19`, `shell.py` completer + `print_help` | `/editor` diiklankan (metadata + completer + help) tetapi **tidak ada branch dispatch** di `command_handler` | Ketik `/editor` → `shell.py:531` → `[!] Unknown command: /editor` |
| 2 | `slash_commands.py:343-354` (`handle_undo`) | `BackupRollbackStrategy()` dipanggil tanpa `cwd`; `strategy.rollback(self.cwd)` mengirim argumen ke `rollback()` yang tanpa argumen; tidak menghapus pesan terakhir; tanpa konfirmasi | **TypeError** (konstruktor butuh `cwd` di `backup.py:8`; `rollback()` tak terima argumen di `backup.py:29`) |
| 3 | `slash_commands.py:319` (`handle_compact`) | `provider.generate(prompt)` mengirim **string**, signature `generate(messages: List[Dict[str,str]])` di `base.py:8` | Crash / permintaan LLM tidak valid |

### 2.2 Tidak Lengkap

| # | Lokasi | Masalah |
| :-- | :--- | :--- |
| 4 | `slash_commands.py:356-358` (`handle_redo`) | Placeholder "No pending forward rollback states" — tidak ada state tersimpan untuk di-redo |

### 2.3 Kebersihan Kode

| # | Lokasi | Masalah |
| :-- | :--- | :--- |
| 5 | `slash_commands.py:73-134` | `handle_help`, `handle_status`, `handle_commands`, `handle_exit` **tidak di-wire** di `command_handler` — chain lama (`print_help`, `show_status`, dll.) yang dipakai → duplikasi logika |

### 2.4 Celah Test

`tests/core/test_slash_commands.py` (73 baris) tidak menguji:
- `/undo`, `/redo`, `/compact`, `/themes`, `/details`, `/connect`, `/models`, `/share`, `/unshare`
- Resolusi alias (`/q`, `/new`, `/summarize`, `/resume`, `/continue`)
- Wiring dispatch `command_handler` (khususnya `/editor`)

---

## 3. Rencana Perbaikan

### Langkah 1 — Wire `/editor`
- Tambah branch di `command_handler` (`shell.py`) untuk `/editor`.
- Implementasi `handle_editor(args, last_ai_response)` di `slash_commands.py`:
  - Gunakan `$EDITOR`/`$VISUAL` (fallback `notepad` di Windows, `vi`/`nano` di Unix).
  - Buat temp file, buka editor via subprocess, baca isi, kirim sebagai pesan user.

### Langkah 2 — Perbaiki `handle_undo`
- `BackupRollbackStrategy(cwd=self.cwd)`.
- Panggil `strategy.rollback()` tanpa argumen.
- Hapus pesan terakhir dari memori (tambah method `delete_last_message(session_id)` di `ChatMemoryManager`).
- Minta **konfirmasi pengguna** sebelum revert (sesuai keputusan desain "lokal minimal, tanpa git reset").

### Langkah 3 — Perbaiki `handle_compact`
- Kirim `provider.generate([{"role": "user", "content": prompt}])`.
- Ambil `summary` dari `raw["content"]` bila provider mengembalikan dict.

### Langkah 4 — Implementasi `/redo` minimal
- Simpan snapshot pesan yang dihapus oleh `/undo` di `.nexa/undo_stack.json`.
- `/redo` me-restore pesan tersebut ke sesi aktif.
- Jika kosong: tampilkan pesan jujur "tidak ada aksi untuk di-redo".

### Langkah 5 — Bersihkan dead code
- Wire `handle_help`/`handle_status`/`handle_commands`/`handle_exit` ke dispatch, atau hapus duplikasi (gunakan satu sumber: `print_help` dari `SLASH_METADATA`).

### Langkah 6 — Perluas test
`tests/core/test_slash_commands.py`:
- Test `/undo` (pakai mock memory + tmp backup), `/redo`, `/compact` (mock provider), `/themes`, `/details`, `/connect`, `/models`, `/share`, `/unshare`.
- Test resolusi alias.
- Test wiring `command_handler` `/editor` tanpa crash.

### Langkah 7 — Verifikasi akhir
- `py -3.14 -m pytest tests -q` → semua hijau.
- Manual: `nexa ai` → `/help`, `/editor`, `/undo`, `/redo`, `/compact`, `/models`, `/themes`.
- Pastikan command lama (`/plan`, `/facts`, `/pin`, `/dir`, `/session`) tidak rusak.

---

## 4. Peringatan

| Hal | Catatan |
| :--- | :--- |
| `/undo` | Tetap **tanpa** `git reset --hard`; revert via `BackupRollbackStrategy` + konfirmasi pengguna |
| `/redo` | Minimal (snapshot `.nexa/undo_stack.json`), bukan full forward-rollback pipeline |
| `/editor` | Perilaku bergantung `$EDITOR`; fallback platform disediakan |

---

*Dokumen ini adalah rencana eksekusi. Eksekusi dilakukan hanya setelah persetujuan pengguna.*