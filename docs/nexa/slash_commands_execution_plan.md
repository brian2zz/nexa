# 🗺️ Planning Eksekusi: Menuntaskan Slash Commands Nexa

> **Status:** RENCANA — **jangan dieksekusi** sebelum disetujui baris per baris.
> **Tanggal:** 14 Agustus 2026
> **Cara pakai dokumen ini:** kerjakan fase secara urut. Setiap fase punya bagian *"Harus Apa"* (tujuan), *"Cara"* (langkah + file:line + kode), *"Kriteria Selesai"*, dan *"Test"*.
> **Rujukan:** `.opencode/plans/slash_commands_audit_and_roadmap.md`, `docs/nexa/slash_commands_opencode_plan.md`, `docs/nexa/slash_commands_opencode_fix_plan.md`

---

## 1. Ringkasan Singkat (1 menit)

Kerja slash command ala opencode sudah **~95% selesai** dan sudah di-commit sebagian (`fabada8`, `799f3ab`). Yang tersisa adalah pekerjaan **pembersihan & penguatan** agar arsitekturnya rapi, aman dari regresi, lalu **menyambungkan ke TUI** dan **mengganti stub dengan fitur nyata**. Urutannya:

**A. Registry dispatch** → **B. Hapus dead code** → **C. Persist redo** → **D. Commit** → **E. TUI wiring** → **F. Stub→nyata** → **G. Gap opencode**.

Tidak ada perubahan kode besar — semuanya refactor bertahap dengan test hijau di tiap fase.

---

## 2. Peta Status Saat Ini (sudah selesai — JANGAN diubah ulang)

| Item | Lokasi | Status |
| :--- | :--- | :--- |
| Handler `SlashCommandHandler` (22 method) | `nexa/commands/ai/slash_commands.py` | ✅ |
| Dispatch command (14 command + stub + normalisasi `/sessions`) | `nexa/commands/ai/shell.py:209-247` | ✅ |
| Alias `/q /new /summarize /resume /continue` | `slash_commands.py:55-62` | ✅ |
| Completer 40+ command | `shell.py:117-176` | ✅ |
| `/editor` (handler + dispatch + test) | `slash_commands.py:136`, `shell.py:215`, `test:125` | ✅ |
| `/redo` (undo push → redo restore) | `slash_commands.py:433-471` | ✅ |
| `/copy` (clipboard) | `slash_commands.py:335`, `shell.py:227` | ✅ |
| `get_last_message` / `delete_last_message` / `rename_session` | `memory/core.py:138,150,164` | ✅ |
| `/mode [PLAN|BUILD]` + TAB toggle di TUI | `slash_commands.py:274`, `shell.py:219`, `ui/app.py:238` | ✅ |
| Test slash commands (7 fungsi) | `tests/core/test_slash_commands.py` | ✅ |
| Dokumen planning | `docs/nexa/` + `.opencode/plans/` | ✅ |

---

## 3. Fase A — Registry Dispatch (Ganti rantai `if/elif`)

### Harus Apa
Mengganti blok `if/elif` di `command_handler` (sekarang 14+ branch) dengan **satu dict registry**, sehingga menambah command = mengubah 1 tempat, dan bug "dead mapping" seperti `/editor` dulu bisa **terdeteksi otomatis oleh test**.

### Cara
**A1.** Di `nexa/commands/ai/slash_commands.py` tambah dict (setelah `SLASH_ALIASES`, baris ~62):
```python
SLASH_DISPATCH = {
    "/connect":  ("handle_connect",  8),
    "/models":   ("handle_models",   7),
    "/init":     ("handle_init",     5),
    "/editor":   ("handle_editor",   7),
    "/themes":   ("handle_themes",   7),
    "/mode":     ("handle_mode",     5),
    "/rename":   ("handle_rename",   7),
    "/export":   ("handle_export",   7),
    "/copy":     ("handle_copy",     5),
    "/compact":  ("handle_compact",  8),
    "/share":    ("handle_share",    6),
    "/unshare":  ("handle_unshare",  8),
    "/context":  ("handle_context",  8),
    "/agents":   ("handle_agents",   7),
    "/undo":     ("handle_undo",     5),
    "/redo":     ("handle_redo",     5),
}
# nilai = (nama_method_handler, panjang_prefix_command)
```

**A2.** Di `shell.py`, ganti `shell.py:209-244` (blok `if first_word == ...`) dengan:
```python
from nexa.commands.ai.slash_commands import SLASH_METADATA, SLASH_ALIASES, SLASH_DISPATCH, SlashCommandHandler

# ... di dalam command_handler, setelah alias resolve:
entry = SLASH_DISPATCH.get(first_word)
if entry:
    handler_name, prefix_len = entry
    handler = getattr(slash_handler, handler_name)
    return handler(clean_cmd[prefix_len:].strip(), last_ai_response)

if first_word == "/details" or first_word == "/thinking":
    return slash_handler.handle_details(clean_cmd[len(first_word):].strip(), last_ai_response)
if first_word in ["/skills", "/variants", "/mcps", "/timeline"]:
    return slash_handler.handle_stub(first_word[1:])
if clean_cmd.lower().startswith("/sessions"):
    clean_cmd = "/session" + clean_cmd[9:]   # normalisasi ke chain lama
```

**A3.** Pastikan import di `shell.py` disesuaikan (tambahkan `SLASH_DISPATCH`).

### Test
Di `tests/core/test_slash_commands.py` tambah **validasi integritas**:
```python
def test_dispatch_integrity():
    # setiap command di metadata (kecuali alias/stub/old-chain) harus punya handler nyata
    from nexa.commands.ai.slash_commands import SLASH_METADATA, SLASH_DISPATCH, SlashCommandHandler
    ignored = {"/help", "/status", "/exit", "/commands", "/q", "/quit", "/new", "/clear",
               "/history", "/load", "/session", "/sessions", "/select-provider", "/set-model",
               "/set-api-key", "/dir", "/explain", "/plan", "/facts", "/pin", "/pins",
               "/unpin", "/clearpins", "/details", "/thinking", "/summarize", "/resume",
               "/continue", "/skills", "/variants", "/mcps", "/timeline"}
    for cmd, _, _ in SLASH_METADATA:
        if cmd in ignored:
            continue
        assert cmd in SLASH_DISPATCH, f"{cmd} ada di help tapi tidak di dispatch!"
        handler_name, _ = SLASH_DISPATCH[cmd]
        assert hasattr(SlashCommandHandler, handler_name), f"{cmd} -> handler {handler_name} tidak ada!"
```
Test ini **otomatis menangkap** kejadian `/editor`-dulu di masa depan.

### Kriteria Selesai
- `command_handler` tidak lagi punya rantai `if/elif` untuk command baru.
- Semua command berfungsi sama seperti sekarang (uji manual: `/models`, `/editor`, `/undo`, `/redo`, `/copy`).
- `pytest tests -q` hijau.

---

## 4. Fase B — Hapus Dead Code (4 handler duplikat)

### Harus Apa
`handle_help`, `handle_status`, `handle_commands`, `handle_exit` di `slash_commands.py:74-134` **tidak pernah dipanggil** — chain lama (`print_help`, `show_status`, blok `/commands`, `/exit`) yang menangani. Hapus duplikasi agar ada satu sumber kebenaran.

### Cara (rekomendasi: OPSI A — hapus)
**B1.** Hapus 4 method tersebut dari `SlashCommandHandler` (`slash_commands.py:74-134`).
**B2.** Verifikasi tidak ada pemanggilan: grep `handle_help|handle_status|handle_commands|handle_exit` → harus 0 hasil di luar definisi.
**B3.** (Opsional penguatan) Pindahkan logika `print_help()` (`shell.py:6-30`) agar membaca `SLASH_METADATA` (sudah demikian) — tidak ada perubahan.

> Alternatif OPSI B (wire ke class): hanya pilih jika kamu ingin semua `/help` dst dikelola class. Lebih banyak perubahan; tidak direkomendasikan sekarang.

### Test
`test_slash_handler_execution` yang memanggil `handle_help/handle_status` harus **disesuaikan**: ganti dengan assert bahwa `command_handler("/help")` mencetak konten benar (cukup via `capsys`), bukan memanggil method class.

### Kriteria Selesai
- Tidak ada method class yang mati.
- `/help`, `/status`, `/commands`, `/exit` tetap jalan (via chain lama).

---

## 5. Fase C — Persist Redo Stack (P3)

### Harus Apa
`_redo_stack` saat ini hanya di memori (class attribute, `slash_commands.py:388`) — hilang saat proses tutup. Buat persist ke `.nexa/undo_stack.json` agar undo/redo bertahan antar-sesi.

### Cara
**C1.** Inisialisasi di `__init__` (`slash_commands.py:66`):
```python
import json
self._redo_stack: List[Dict[str, Any]] = []
self._undo_file = os.path.join(self.cwd, ".nexa", "undo_stack.json")
self._load_redo_stack()
```
**C2.** Tambah helper privat:
```python
def _load_redo_stack(self):
    try:
        if os.path.exists(self._undo_file):
            with open(self._undo_file, "r", encoding="utf-8") as f:
                self._redo_stack = json.load(f)
    except Exception:
        self._redo_stack = []

def _save_redo_stack(self):
    try:
        os.makedirs(os.path.dirname(self._undo_file), exist_ok=True)
        with open(self._undo_file, "w", encoding="utf-8") as f:
            json.dump(self._redo_stack[-20:], f)   # batas 20 item
    except Exception:
        pass
```
**C3.** Panggil `self._save_redo_stack()` di akhir `handle_undo` (setelah push, `slash_commands.py:440`) dan di akhir `handle_redo` (setelah pop, `slash_commands.py:463`).
**C4.** **Hapus** class attribute `_redo_stack` di `slash_commands.py:388`.

### Test
`test_undo_and_redo_flow` (`tests/core/test_slash_commands.py:101`) ditambah: setelah undo, file `.nexa/undo_stack.json` ada; instance baru `SlashCommandHandler` bisa load stack lama dan `/redo` memulihkan pesan.

### Kriteria Selesai
- Undo → tutup shell → buka shell → `/redo` berhasil memulihkan pesan.

---

## 6. Fase D — Commit Batch

### Harus Apa
Mengunci pekerjaan yang sudah benar (Fase A–C + perubahan yang sudah ada) ke dalam commit rapi. **Pastikan tidak meng-commit file yang tidak perlu.**

### Cara
**D1.** `git status` → pastikan hanya: `shell.py`, `slash_commands.py`, `memory/core.py`, `test_slash_commands.py`, `ui/app.py`, `ui/**` (jika Fase E belum), dan dokumen `docs/nexa/`, `.opencode/plans/`.
**D2.** `git add` file spesifik (jangan `git add -A` tanpa seleksi).
**D3.** Commit dengan pesan sesuai gaya repo (lihat `git log --oneline`):
`refactor(ai): replace if/elif slash dispatch with registry + remove dead code + persist redo stack`
**D4.** Jangan push kecuali diminta.

### Kriteria Selesai
- `git status` bersih dari file kerja yang tidak disengaja.
- Riwayat log konsisten.

---

## 7. Fase E — TUI Wiring (`/themes`, `/details`, `/thinking`)

### Harus Apa
Di shell terminal, `/themes` hanya set `Config.ui.theme`. Di TUI (`nexa/ui/app.py`), setelan itu **belum diterapkan**. Sambungkan agar:
- `/themes <nama>` mengubah tema Textual langsung (live).
- `/details` & `/thinking` benar-benar mengubah tampilan reasoning.
- `/themes`/`/details`/`/thinking` ditambahkan ke command palette.

### Cara (berdasarkan struktur `ui/app.py` yang sudah diverifikasi)
**E1.** Command palette (`ui/app.py:79-105`) tambahkan entri:
```python
("/themes", "Switch UI theme"),
("/details", "Toggle reasoning detail"),
("/thinking", "Toggle reasoning visibility"),
```
**E2.** Di `handle_palette_result` (`ui/app.py:455-471`), tambahkan routing ke handler `SlashCommandHandler` (sama seperti `/set-model`, dst). `needs_args`/`needs_modal` (`ui/app.py:458-459`) bisa diabaikan karena command ini cukup `InputModal` sederhana.
**E3.** Terapkan tema: di `on_mount` / saat `/themes` dipanggil, baca `Config.get("ui.theme")` → panggil `self.theme = <nama>` (Textual mendukung `app.theme`); tambahkan refresh `palette.py` bila perlu.
**E4.** Reasoning toggle: cari tempat render streaming/thinking (kemungkinan `ui/widgets/chat_message.py`) → bungkus blok reasoning dengan `if Config.get("ui.show_reasoning", True):`.

### Test
- `tests/core/ui/test_app_ui.py` (sudah ada pola test TUI): tambah test bahwa memanggil `/themes nord` mengubah `app.theme`, dan `/details` mengubah config.
- Pastikan tidak merusak `action_toggle_mode` (`ui/app.py:238`).

### Kriteria Selesai
- Di TUI: `/themes nord` → UI berganti tema; `/details` → reasoning muncul/hilang; TAB mode tetap jalan.

---

## 8. Fase F — Ganti Stub dengan Fitur Nyata

### Harus Apa
`/skills`, `/variants`, `/mcps`, `/timeline` masih stub (`slash_commands.py:429-431`). Implementasikan secara bertahap, prioritas **`/timeline`** dulu (paling mudah, data sudah ada di `PipelineBus`).

### Cara (prioritas berurutan)
**F1. `/timeline`** — baca riwayat event dari `PipelineBus` (`runtime.bus`, lihat `nexa/core/events/bus.py`): tampilkan N event terakhir (nama event, waktu, session). Handler `handle_timeline(args)` baru → tambah ke `SLASH_DISPATCH`.
**F2. `/mcps`** — eksplorasi apakah `nexa/core/agent/tools/` sudah mendukung tool server (lihat `tools/registry.py`). Jika ada plugin/tool eksternal, `/mcps list` menampilkannya; `add/remove` menunda.
**F3. `/skills`** — scaffold: buat folder `nexa/skills/` + format skill YAML/JSON sederhana; `/skills list` membaca folder; `/skills load <name>` memuat.
**F4. `/variants`** — tampilkan varian model aktif dari `Config` (`provider.model` + alternatif dari `list_models()`); `/variants <name>` set alias model.

### Test
Test handler baru: `/timeline` mengembalikan daftar event (mock bus); `/skills list` menemukan folder; dst.

### Kriteria Selesai
- Tidak ada lagi pesan "planned roadmap capability" untuk 4 command tersebut (kecuali yang memang belum layak — tandai di help sebagai "experimental").

---

## 9. Fase G — Gap Analysis opencode

### Harus Apa
Jadikan `docs/gap_analysis_opencode.md` sebagai **checklist** dan kerjakan item tersisa.

### Cara
**G1.** Baca `docs/gap_analysis_opencode.md`, tandai item yang sudah tuntas (slash commands, mode, editor, copy, dll).
**G2.** Untuk item tersisa: buat sub-item baru di dokumen ini (atau dokumen follow-up) dengan format fase yang sama (Harus Apa/Cara/Kriteria).
**G3.** Prioritaskan item yang berdampak langsung pada alur kerja (mis. `@file`/`@directory` resolution, auto-scaffold, knowledge engine).

### Kriteria Selesai
- Dokumen gap menjadi checklist tercentang; semua item punya status jelas (done / planned / deferred).

---

## 10. Urutan Kerja & Dependensi

| Urutan | Fase | Dependensi | Estimasi |
| :---: | :--- | :--- | :--- |
| 1 | A (Registry) | — | Kecil |
| 2 | B (Dead code) | A (agar dispatch konsisten) | Kecil |
| 3 | C (Persist redo) | A | Kecil |
| 4 | D (Commit) | A–C | — |
| 5 | E (TUI wiring) | D (bekerja dari base bersih) | Sedang |
| 6 | F (Stub→nyata) | E | Besar |
| 7 | G (Gap opencode) | F (atau paralel) | Bervariasi |

**Aturan emas:** selesaikan A–D dulu. Jangan mulai E/F sebelum commit A–D, agar ada titik kembali yang aman.

---

## 11. Keputusan yang Harus Kamu Ambil

1. **B (dead code):** hapus (Opsi A) atau wire (Opsi B)? → **Rekomendasi: A (hapus)**.
2. **C (redo persist):** kerjakan sekarang atau tunda? → **Rekomendasi: kerjakan** (murah, ~15 baris).
3. **E (TUI):** apakah `/themes` perlu live-apply tema atau cukup set config dulu? → **Rekomendasi: live-apply**.
4. **F (stub):** urut `/timeline → /mcps → /skills → /variants` disetujui? → **Rekomendasi: ya**, `/timeline` paling murah.
5. **Commit:** apakah commit Fase A–D **tanpa push**? → **Rekomendasi: ya**.

---

## 12. Risiko & Mitigasi

| Risiko | Mitigasi |
| :--- | :--- |
| Registry salah hitung prefix → command ke-trim salah | Test integritas + uji manual tiap command |
| Hapus dead code → ada pemanggil tersembunyi | Grep sebelum hapus (Fase B2) |
| Redo file JSON korup | `try/except` pada load/save + fallback `[]` |
| TUI wiring merusak mode/TAB | Test `action_toggle_mode` tetap hijau |
| Stub→nyata butuh MCP/plugin yang belum ada | Prioritaskan `/timeline`; `/mcps` tunda bila infrastruktur belum siap |

---

*Dokumen ini adalah rencana eksekusi. **Jangan dieksekusi** sampai kamu menyetujui bagian yang relevan.*