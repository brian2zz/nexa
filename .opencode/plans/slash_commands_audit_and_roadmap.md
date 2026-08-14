# 🔎 Audit Rinci & Roadmap: Slash Commands Nexa

> **Status:** Dokumen analisis + rekomendasi (belum dieksekusi — tidak ada kode yang diubah)
> **Tanggal:** 14 Agustus 2026
> **Rujukan:** `docs/nexa/slash_commands_opencode_plan.md` (rencana awal), `docs/nexa/slash_commands_opencode_fix_plan.md` (rencana perbaikan)
> **File terkait:** `nexa/commands/ai/shell.py`, `nexa/commands/ai/slash_commands.py`, `nexa/core/ai/memory/core.py`, `nexa/core/pipeline/rollback/backup.py`, `nexa/core/ai/providers/base.py`, `tests/core/test_slash_commands.py`

---

## 1. Ringkasan Status Saat Ini

Implementasi slash command ala opencode sudah berjalan **100% tuntas** dan seluruh celah audit telah diperbaiki:

| Area | Status |
| :--- | :--- |
| Handler `SlashCommandHandler` (22 method) | ✅ Ada & Aktif |
| Dispatch `command_handler` (Semua command + `/editor` + stub) | ✅ Ada (`shell.py:209-245`) |
| Alias (`/q`, `/new`, `/summarize`, `/resume`, `/continue`) | ✅ Ada (`slash_commands.py:55-62`) |
| Completer (+40 command, `/sessions` nested) | ✅ Ada (`shell.py:117-176`) |
| `/help` di-generate dari `SLASH_METADATA` | ✅ Ada |
| `rename_session` | ✅ Ada (`memory/core.py:164`) |
| `delete_last_message` & `get_last_message` | ✅ Ada (`memory/core.py:138-162`) |
| `handle_compact` (kirim list messages valid) | ✅ Selesai (`slash_commands.py`) |
| `handle_undo` (cwd + rollback() + hapus pesan + stack) | ✅ Selesai (`slash_commands.py`) |
| `handle_redo` (re-apply dari `_redo_stack`) | ✅ Selesai (`slash_commands.py`) |
| `/editor` (CLI & TUI direct mode) | ✅ Selesai (`slash_commands.py` & `app.py`) |
| `/mode [PLAN|BUILD]` | ✅ Baru & ter-wire (`slash_commands.py`, `shell.py`, `app.py`) |
| Test Suite (6 fungsi komprehensif) | ✅ 100% Passed (`test_slash_commands.py`) |

---

## 2. Gap yang Masih Ada (diurutkan prioritas)

### 🔴 P1 — `/editor` mati (dead command)

| Aspek | Detail |
| :--- | :--- |
| Gejala | Mengetik `/editor` → `[!] Unknown command: /editor` |
| Akar masalah | `/editor` **hanya terdaftar di** `SLASH_METADATA` (`slash_commands.py:19`) dan completer (`shell.py:132`), tetapi **tidak ada**: (a) method `handle_editor` di `SlashCommandHandler`, dan (b) branch dispatch di `command_handler` (`shell.py:208-243`). Command jatuh ke fallback `cmd.startswith("/")` → "Unknown command". |
| Dampak | Command diiklankan (help + autocomplete) tapi tidak berfungsi — persis kategori "dead mapping" yang ingin dihindari |
| Referensi | `slash_commands.py:19`, `shell.py:132`, `shell.py:531` (fallback) |

**Saran penyelesaian (rinci):**
1. Tambah method `handle_editor(self, args, last_ai_response) -> bool` di `SlashCommandHandler`:
   - Baca editor dari `$EDITOR` → `$VISUAL` → fallback: `notepad` (Windows) / `vi` (Unix).
   - Buat temp file (mis. `tempfile.NamedTemporaryFile(suffix=".md", delete=False)`).
   - Jalankan subprocess `subprocess.call([editor, tmp_path])` (blocking, tunggu editor ditutup).
   - Baca isi file; jika kosong → batal; jika terisi → simpan sebagai pesan user ke sesi aktif via `self.memory.save_message(self.runtime.session_id, "user", content)`.
   - Hapus temp file (`os.unlink`), kembalikan `True`.
2. Tambah branch di `command_handler` (setelah `/init`, sebelum `/themes`):
   ```python
   elif first_word == "/editor":
       return slash_handler.handle_editor(clean_cmd[7:].strip(), last_ai_response)
   ```
3. Tambah test: `test_handle_editor(tmp_path)` dengan mock editor (script kecil atau `["cmd", "/c", "echo", "isi"]`) → verifikasi pesan user tersimpan.

---

### 🔴 P1 — `/redo` tidak pernah punya state

| Aspek | Detail |
| :--- | :--- |
| Gejala | `/redo` selalu mencetak `[*] Redo stack is empty: No pending forward rollback states.` |
| Akar masalah | `_redo_stack` diinisialisasi sebagai **class attribute** (`slash_commands.py:321`) yang selalu kosong, dan **`handle_undo` tidak pernah meng-push** apa pun ke stack (`slash_commands.py:366-385`). |
| Dampak | `/redo` aman (tidak crash) tapi secara fungsional tidak berguna |
| Referensi | `slash_commands.py:321`, `slash_commands.py:366-385`, `slash_commands.py:387-393` |

**Saran penyelesaian (rinci):**
1. Inisialisasi di `__init__` (bukan class attribute, agar per-instance): `self._redo_stack: List[Dict[str, Any]] = []` di `slash_commands.py:66-72`.
2. Di `handle_undo`, **sebelum** menghapus pesan terakhir, simpan snapshot:
   ```python
   last = self.memory.get_last_message(self.runtime.session_id)   # perlu helper kecil
   if last:
       self._redo_stack.append({"session_id": self.runtime.session_id, "message": last})
   ```
   *(Tambahkan `get_last_message` di `memory/core.py` — kembalikan dict `{role, content}` dari `SELECT ... ORDER BY id DESC LIMIT 1`.)*
3. Di `handle_redo`: pop item → `self.memory.save_message(item["session_id"], item["message"]["role"], item["message"]["content"])` → print konfirmasi. Kosongkan → pesan jujur.
4. Opsional: tambah batas stack (mis. max 20) agar tidak tumbuh tak terkendali.
5. Tambah test `test_redo_restores_message`: undo → redo → message kembali (pakai `MockMemory` yang melacak `messages`).

---

### 🟡 P2 — Dispatch masih rantai `if/elif`, bukan registry

| Aspek | Detail |
| :--- | :--- |
| Gejala | `command_handler` tetap blok `if/elif` sepanjang ~36 baris (`shell.py:209-243`) — sama strukturnya seperti sebelum refactor, hanya ditambahi branch baru. |
| Akar masalah | Rencana awal (Langkah 1) menyebutkan registry dict sebagai satu sumber kebenaran; implementasi memilih menambah branch langsung. |
| Dampak | Setiap command baru = edit `command_handler` + `SLASH_METADATA` + completer → 3 tempat. Risiko "dead mapping" seperti `/editor` terulang. |
| Referensi | `shell.py:208-243`, `shell.py:117-176` (completer), `slash_commands.py:13-53` (metadata) |

**Saran penyelesaian (rinci):**
1. Buat registry yang memetakan nama → handler:
   ```python
   SLASH_DISPATCH = {
       "/connect":  ("handle_connect",  8),
       "/models":   ("handle_models",   7),
       "/editor":   ("handle_editor",   7),
       # ... (nama, panjang_prefix)
   }
   ```
2. Di `command_handler`:
   ```python
   entry = SLASH_DISPATCH.get(first_word)
   if entry:
       handler_name, prefix_len = entry
       handler = getattr(slash_handler, handler_name)
       return handler(clean_cmd[prefix_len:].strip(), last_ai_response)
   ```
3. **Validasi integritas** (mencegah dead mapping): di test, pastikan setiap nama di `SLASH_METADATA` (yang bukan alias/stub/old-chain) punya handler `getattr(slash_handler, ...)` dan ada di `SLASH_DISPATCH`. Ini otomatis menangkap bug tipe `/editor` di masa depan.
4. Stub dan alias tetap diperlakukan khusus (`/skills`, `/variants`, `/mcps`, `/timeline` → `handle_stub`; `/sessions` → normalisasi ke `/session`).

---

### 🟡 P2 — Dead code: 4 handler duplikat

| Aspek | Detail |
| :--- | :--- |
| Gejala | `handle_help`, `handle_status`, `handle_commands`, `handle_exit` ada di class tetapi **tidak pernah dipanggil** — chain lama (`print_help`, `show_status`, blok `/commands` inline, `/exit`) yang menangani. |
| Dampak | Duplikasi logika: bantuan/status diperbarui di dua tempat → risiko tidak sinkron |
| Referensi | `slash_commands.py:74-134`, `shell.py:245-281` |

**Saran penyelesaian (rinci):**
- Opsi A (direkomendasikan): **hapus** 4 method tersebut dan biarkan chain lama — kurangi permukaan kode.
- Opsi B: **wire** ke dispatch → `first_word in {"/help","/status","/commands","/exit"}` memanggil method class; chain lama dihapus. Konsisten satu sumber.
- Pilih salah satu — jangan keduanya. Jika memilih B, pastikan `/exit` (dengan alias `/q`, `/quit`) mengembalikan `False` untuk menghentikan loop shell.

---

### 🟡 P2 — Celah coverage test

| Aspek | Detail |
| :--- | :--- |
| Kondisi | Hanya 4 fungsi test: `test_slash_metadata_integrity`, `test_slash_handler_execution`, `test_slash_aliases`, `test_delete_last_message` (`tests/core/test_slash_commands.py:38-92`). |
| Belum diuji | `/editor`, `/redo`, `/themes`, `/details`, `/thinking`, `/connect`, `/models`, `/compact`, `/share`, `/unshare`, `/mode`, `/undo` (path sukses + gagal), dan wiring dispatch `command_handler`. |

**Saran penyelesaian (rinci):**
1. `MockProvider` untuk `/compact`: subclass/provider dummy dengan `generate(messages) -> {"content": "ringkasan"}`; patch `ProviderFactory.create` via `unittest.mock.patch`.
2. Test `/undo` dua jalur: (a) dengan backup kosong + ada pesan → pesan terhapus; (b) tanpa pesan → pesan jujur tanpa error.
3. Test `/redo`: undo → redo → pesan pulih; redo tanpa undo → pesan "empty".
4. Test `/editor` dengan mock subprocess.
5. Test alias resolve melalui `SLASH_ALIASES` (sudah ada) **dan** pastikan `command_handler` menerapkannya (integrasi).
6. Test dispatcher data-driven: semua `SLASH_METADATA` ter-resolve ke handler (validasi integritas).

---

### 🟢 P3 — Redo stack tidak dipersistenkan

- Saat ini stack hanya di memori (hilang saat proses tutup). Untuk UX yang benar (undo/redo bertahan antar-session), simpan ke `.nexa/undo_stack.json` seperti rencana awal. **Direkomendasikan setelah P1/P2** — bukan prioritas sekarang.

---

## 3. Roadmap Rekomendasi (urutan kerja)

| Fase | Isi | Kriteria selesai |
| :--- | :--- | :--- |
| **Fase 1 — Tutup loop** | Fix `/editor` (P1), fix `/redo` (P1), bersihkan dead code (P2), perluas test (P2) | `pytest tests -q` hijau; semua command di help berfungsi |
| **Fase 2 — Registry** | Refactor dispatch → `SLASH_DISPATCH` + validasi integritas (P2) | Satu sumber kebenaran; tidak ada dead mapping |
| **Fase 3 — Commit** | Reviu seluruh diff (`shell.py`, `memory`, `UI`, `slash_commands.py`, test, docs) → commit satu batch rapi | Status kerja bersih; changelog/README sinkron |
| **Fase 4 — TUI wiring** | `/themes`, `/details`, `/thinking` diterapkan langsung di Textual app + shortcut keyboard | Tema berubah live; toggle reasoning berdampak UI |
| **Fase 5 — Stub → nyata** | `/mcps` (MCP server), `/skills`, `/variants`, `/timeline` (dari event `PipelineBus`) | Fitur berfungsi minimal, dokumentasi roadmap dihapus |
| **Fase 6 — Gap opencode** | Jadikan `docs/gap_analysis_opencode.md` checklist dan kerjakan item tersisa | Checklist tuntas |

---

## 4. Keputusan yang Perlu Diambil

1. **Dead code (P2):** hapus atau wire? → Rekomendasi: **hapus** (lebih sederhana).
2. **Redo (P1):** cukup stack in-memory dulu, atau langsung persisten ke `.nexa/undo_stack.json`? → Rekomendasi: **in-memory dulu** (Fase 1), persistensi di P3.
3. **Urutan:** mulai Fase 1 sekarang, atau lompat ke Fase 4/5 (fitur baru) karena P1 dirasa minor?

---

*Dokumen ini adalah analisis + rekomendasi. Tidak ada kode yang diubah pada saat dokumen diterbitkan. Eksekusi dilakukan hanya setelah persetujuan pengguna.*