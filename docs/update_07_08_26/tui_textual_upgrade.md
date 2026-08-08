# Rencana Upgrade: TUI Textual untuk Nexa AI Shell (Tanpa WebSocket)

*Status: Artefact Perencanaan — 08 Agustus 2026*

Dokumen ini adalah rencana untuk mengganti loop `PromptSession` line-based pada
`nexa ai` dengan **TUI full-screen ala opencode** memakai Textual. Prinsip utama:
**tanpa WebSocket**, **tanpa dependensi runtime tambahan di sisi user** (textual
masuk `install_requires`), **tanpa kehilangan fitur**, dan extensible untuk
fitur-fitur ke depan.

---

## 1. Latar Belakang & Tujuan

UI `nexa ai` saat ini adalah REPL line-based (`nexa/commands/ai/shell.py:144`)
dengan output `print()` berwarna dan spinner. User menginginkan pengalaman ala
opencode (split pane, streaming, modal approval) tetapi **tetap in-process**:

- ❌ **Tanpa WebSocket** — tidak ada server terpisah (berbeda dari opencode yang
  memakai binary Go + server TS/Bun + WebSocket).
- ✅ **Langsung jalan setelah install** — `pip install nexa` saja, tidak ada
  toolchain eksternal.
- ✅ **UI interaktif yang tidak membingungkan** — progressive disclosure.
- ✅ **Fitur baru mudah masuk** — Textual `Screen` registry + `PipelineBus`
  (sudah ada) sebagai spine event.

### Kenapa Textual (bukan prompt_toolkit full-screen)

| Aspek | prompt_toolkit (sudah terinstall) | Textual |
| :--- | :--- | :--- |
| Model UI | Layout imperatif, render manual | Widget reactive, `App`/`Screen`/`Compose` |
| Worker async | Manual `create_task` | `run_worker` + `post_message` bawaan |
| Tampilan modern | Perlu bangun sendiri | Built-in themes, panels, scroll, focus |
| Dependensi tambahan | 0 | 1 (`textual`) |
| Ekosistem | REPL/line | TUI app penuh |

Keputusan: **Textual** dipilih karena produktivitas pembangunan UI modern jauh
lebih tinggi; `textual>=0.80` hanya satu baris di `install_requires`, pure
Python, wheel siap pakai di Windows/macOS/Linux.

---

## 2. Keputusan Arsitektur

### 2.1 Tanpa WebSocket — kontrak in-process

Blocking call (LLM, planner, indexer) dijalankan lewat `self.run_worker()`
(thread Textual); hasil dikirim balik ke UI via `post_message` (Message Textual)
atau reactive attribute. Komunikasi antar-engine memakai **`PipelineBus` yang
sudah ada** (`nexa/core/events/bus.py:12-87`) — thread-safe, publish dari worker
thread, subscribe dari UI. Tidak ada soket.

```
[Textual App: main thread]   ──run_worker──▶   [Runtime worker thread]
   ChatScreen (chat + prompt)                   bus.publish("AIToken", token)
   ToolPanel (kanan, Tab)   ◄──post_message──   bus.publish("ToolCalled", ...)
   StatusBar (provider/model)                   bus.publish("PlanReady", ...)
   Palette (Ctrl+K)                             bus.publish("BeforeApproval", ...)
```

### 2.2 Prinsip desain UI — progressive disclosure

| Zona | Default | Kapan tampil |
| :--- | :--- | :--- |
| Chat (utama) | ✅ Selalu | Scroll transkrip + streaming |
| Prompt (bawah) | ✅ Selalu | Input baris, `Tab` ganti fokus |
| StatusBar (1 baris) | ✅ Selalu | provider/model/branch/spinner |
| ToolPanel (kanan) | ❌ Collapsible | Tombol `F` / `/tools` |
| PlanScreen | ❌ Push | Saat `/plan` selesai |
| DiffScreen | ❌ Push | Saat hasil patch siap |
| ApprovalModal | ❌ Push | Saat `BeforeApproval` diterima |
| Palette | ❌ Overlay | `Ctrl+K` |

User baru hanya melihat chat + prompt + status bar (mirip Nexa sekarang, hanya
rapi). Panel lanjutan bersifat opt-in — tidak membingungkan.

### 2.3 Backward compatibility

- Semua `/command` di `shell.py:7-29` dipertahankan sebagai command palette.
- Jalur Approval `input()` di `workflow/interactive.py` diganti modal, **tetapi
  fallback ke `input()` lama dipertahankan** bila Textual gagal init (non-TTY).
- `PromptSession` tetap dipakai sebagai fallback terminal legacy (VT tidak
  tersedia).

### 2.4 Struktur direktori baru

```
nexa/ui/
  __init__.py
  app.py              TextualApp — tema, keybindings, screen registry
  bridge.py           PipelineBus ↔ Textual post_message (satu file kecil)
  screens/
    chat.py           ChatScreen — transkrip + streaming bubble
    palette.py        CommandPalette (Ctrl+K)
    plan.py           PlanScreen — render report.to_markdown()
    diff.py           DiffScreen — render unified diff
    approval.py       ApprovalModal — modal Yes/No
  widgets/
    chat_bubble.py    Markdown bubble + kursor streaming
    status_bar.py     provider/model/branch + spinner state
    tool_panel.py     Panel kanan collapsible (tools/evidence)
```

---

## 3. Tahapan Eksekusi

### Tahap 1 — Fondasi bridge bus → UI
- Tambah `"textual>=0.80"` di `setup.py:9-19`.
- Buat `nexa/ui/bridge.py`: `Bridge.subscribe(bus, event_filter, handler)` yang
  memetakan `EventContext` → `app.post_message`.
- Verifikasi: screen statis muncul; subscribe dummy event berhasil.
- Test: `tests/core/ui/test_bridge.py` — bridge tanpa app, pakai `threading.Event`.

### Tahap 2 — Streaming provider
- `providers/base.py:8` tambah `stream(messages, temperature, tools) -> Iterator[str]`
  (callback per token).
- Implement di 5 provider — **re-use** logika `generate()` yang ada:
  - `mock` — yield token dari response JSON.
  - `ollama` — parse `{"response": ...}` per line.
  - `deepseek` / `groq` / `gemini` — SSE `data:` line.
- Verifikasi: token hasil `stream()` menyatu == `content` hasil `generate()`.
- Test: `tests/core/ai/providers/test_stream_mock.py`.

### Tahap 3 — Textual App minimal
- `nexa/ui/app.py`: `TextualApp` + `ChatScreen` + `StatusBar`.
- Refactor `shell.py:747` — `runtime.start_loop(get_input, ...)` diganti
  `app.run()`. Logika `command_handler` (747 baris) dipindah ke handler berbasis
  Message **tanpa mengubah perilaku** (intent classifier, facts/pins injection,
  planner, approval event di `shell.py:620-679` tetap utuh).
- Default: chat atas + prompt bawah + status bar; `F` buka ToolPanel.
- Verifikasi manual: `nexa ai` — `/status`, `/help`, `/select-provider`,
  `@file` context, `/plan` semua jalan di TUI.

### Tahap 4 — Panel tambahan & Approval modal
- `ToolPanel` (kanan, collapsible): subscribe `ToolCalled` — nama tool + status.
- `PlanScreen`: subscribe `PlanReady` → render `report.to_markdown()` (rich
  Markdown di dalam Textual).
- `ApprovalModal`: jalur `BeforeApproval` (`runtime.py:58`) sekarang post ke UI,
  bukan blocking input. Fallback `input()` lama jika Textual gagal init.
- Verifikasi: `/plan` end-to-end — plan muncul di panel, approval Yes/No dari
  modal.

### Tahap 5 — Command palette & polish
- `Palette` (Ctrl+K): semua `/command` shell + screen-switch.
- Streaming render: subscribe `AIToken` → bubble mengetik real-time.
- Fallback non-TTY: auto turun ke `PromptSession` lama.
- DiffScreen: render hasil unified diff (`ai/patching/engine.py`) bila /plan
  menghasilkan patch.

### Tahap 6 — Pembersihan & docs
- Update `docs/update_07_08_26/phase_5_completion_plan.md` — tambah seksi
  "TUI Phase".
- Update `print_help()` `shell.py:6-29` → referensi palette.
- Jalankan full test suite (harus tetap ≥32 passed).

---

## 4. Risiko & Mitigasi

| Risiko | Mitigasi |
| :--- | :--- |
| Textual tidak jalan di terminal legacy Windows | Deteksi VT; fallback `PromptSession` otomatis |
| Refactor `shell.py` (747 baris) merusak perilaku | Tahap 3: pindah handler apa adanya, tanpa rewrite logika |
| Streaming provider menambah kompleksitas API | `stream()` default fallback → `generate()` bila tak didukung |
| Race worker ↔ UI | Semua state via `post_message` / reactive; bridge single-threaded ke event loop Textual |
| Approval jadi async kehilangan kontrol | Modal blocking via `push_screen` + `pop_screen`; timeout policy |

---

## 5. Definisi Selesai

1. `nexa ui`/`nexa ai` menampilkan TUI full-screen (chat + prompt + status bar).
2. `/plan` berakhir di PlanScreen; approval lewat modal; tanpa `input()` blocking
   saat TUI aktif.
3. Streaming token tampil real-time di bubble.
4. Fallback non-TTY bekerja (PromptSession) tanpa error.
5. Full test suite hijau; tidak ada fitur `/command` yang hilang.

---

## 6. Status Tracking

| Tahap | Status |
| :--- | :--- |
| 1. Fondasi bridge | ⬜ Belum |
| 2. Streaming provider | ⬜ Belum |
| 3. Textual App minimal | ⬜ Belum |
| 4. Panel & Approval modal | ⬜ Belum |
| 5. Palette & polish | ⬜ Belum |
| 6. Pembersihan & docs | ⬜ Belum |

*Catatan: dokumen ini adalah planning saja; eksekusi dilakukan terpisah setelah
keputusan lanjut.*
