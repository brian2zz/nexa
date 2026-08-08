# Rencana Perbaikan: Review UI Textual + Desain Layout Target

*Status: Artefact Perencanaan — 08 Agustus 2026*

Dokumen ini berisi (A) hasil review kode UI Textual yang sudah ditulis, dan
(B) desain layout multi-zona yang menjadi target akhir. Dokumen ini adalah
**planning saja**; eksekusi dilakukan terpisah setelah keputusan lanjut.

---

## Bagian A — Temuan Review UI

### Status test saat ini
Full test suite: **34 passed, 4 warnings** (hijau). Namun TUI belum benar-benar
dijalankan secara manual — beberapa bug baru muncul saat runtime.

### 🔴 Critical (TUI akan crash / hang saat dijalankan)

| # | Lokasi | Masalah |
| :-: | :--- | :--- |
| C-1 | `nexa/ui/screens/approval.py:58` | `VerticalScroll(..., style="height: 1fr; ...")` → `TypeError: ScrollableContainer.__init__() got an unexpected keyword argument 'style'` (terverifikasi di Textual 8.2.8). Modal approval crash saat `/plan` memicu `BeforeApproval`. |
| C-2 | `nexa/core/agent/workflow/interactive.py:82` + `runtime.py:58` | `ApprovalUI.handle_before_approval` selalu di-subscribe dan memanggil `input()` blocking. Saat TUI aktif, event `BeforeApproval` memicu **dua** handler: ApprovalUI lama (blocking) + modal TUI → double handling / deadlock. |
| C-3 | `nexa/commands/ai/shell.py:747-769` + `app.py:106` | `RedirectedStdout` membajak `sys.stdout` global. Jika Textual crash setelah redirect, stdout tidak dikembalikan → fallback `start_loop` mencetak ke objek mati; `on_unmount` tidak menjamin restore saat crash. |

### 🟠 High (rusak tapi tidak langsung crash)

| # | Lokasi | Masalah |
| :-: | :--- | :--- |
| H-1 | `app.py:14-32,101` | Hijack `sys.stdout` global itu invasive; `Spinner` (`spinner.py:20`) menulis `\r[|]...` tanpa newline → buffer `RedirectedStdout.buffer` tidak pernah flush per-token → streaming tidak smooth dan spinner garbage masuk ke chat. |
| H-2 | `nexa/ui/screens/palette.py:36` | `OptionList` di-populasi string; event mengembalikan `Option`. `str(event.option.prompt)` bisa menghasilkan markup mentah; list statis tidak mendukung parameter (mis. `/set-model foo`). |
| H-3 | `app.py:139-182` | `ctx.payload.get(...)` tanpa guard bila `payload=None` → crash handler event dari bus lain. |
| H-4 | `nexa/ui/widgets/tool_panel.py:22-32` | String concatenation O(n²) dan `scroll_end()` dipanggil tanpa cek widget sudah mount. |

### 🟡 Medium

| # | Lokasi | Masalah |
| :-: | :--- | :--- |
| M-1 | `shell.py:107` | `print(...ID: {runtime.session_id})` dicetak sebelum `start_loop` men-set session → mencetak `None`. (Bug lama.) |
| M-2 | `providers/groq.py`, `deepseek.py`, `ollama.py`, `gemini.py` | `stream()` remote tidak punya test (hanya mock yang teruji). |
| M-3 | `nexa/ui/` | Tidak ada `__init__.py` → `find_packages()` di `setup.py` TIDAK mengikutkan `nexa.ui.*` saat build → setelah `pip install`, UI tidak ada. |
| M-4 | `tests/core/ui/test_bridge.py` | Hanya menguji bridge ke `DummyApp`; tidak ada test `on_bus_message` (routing ToolCalled/BeforeApproval) atau modal. |

### ✅ Yang sudah benar
- `stream()` di `base.py` + 5 provider lengkap; mock teruji (`test_stream_mock.py`).
- `nexa/ui/bridge.py` — pemetaan bus → `post_message` bersih dan thread-safe.
- `shell.py:748` guard `isatty()` + fallback `start_loop`.
- Test bridge hijau.

### Urutan perbaikan yang diusulkan
1. **C-1**: Pindahkan style `VerticalScroll` dari kwarg → blok CSS `#approval-markdown-scroll`.
2. **C-2**: Guard subscribe ApprovalUI di `runtime.py:58` saat mode TUI aktif (flag `tui_mode`).
3. **C-3**: Restructure stdout redirect — redirect di `on_mount`, restore di `finally` pada `app.run()` path; jangan bajak global, pakai callback eksplisit.
4. **H-1**: Ganti `RedirectedStdout` dengan callback eksplisit ke `print_to_chat` + streaming event `AIToken` untuk render smooth.
5. **H-3**: Guard `ctx.payload or {}` di semua handler bus.
6. **M-3**: Tambah `__init__.py` di `nexa/ui/`, `nexa/ui/screens/`, `nexa/ui/widgets/`.
7. **M-2 + M-4**: Tambah test streaming provider remote dan routing `on_bus_message`.

---

## Bagian B — Desain Layout Target (Layout Multi-Zona)

Menggantikan arsitektur 2-zona saat ini (transcript + input) dengan layout
multi-zona **progressive disclosure**:

```
┌──────────────────────────────────────────────────────────┐
│ Header: Nexa — django — main  [Ctrl+K palette]  [F tools]│
├───────────────────────────┬──────────────────────────────┤
│  CHAT (1fr)               │  TOOL PANEL (30%, Tab)       │
│  • user: tambah login     │  • file_lookup     ✅        │
│  • ai: [streaming...]     │  • grep_search     ⏳        │
│  • ai: [diff summary]     │  • evidence 3/5    ✅        │
│                           │  • plan stages     ⏳        │
├───────────────────────────┴──────────────────────────────┤
│ StatusBar: provider/model • session ID • spinner         │
│ Prompt: Nexa> _   [Tab] switch pane  [Enter] send        │
└──────────────────────────────────────────────────────────┘
```

### Zona & perilaku

| Zona | Layout | Default | Isi |
| :--- | :--- | :--- | :--- |
| **Header** | atas, 1 baris | ✅ | Project (framework — branch) + akses cepat palette/tools |
| **Chat** | kiri, `1fr` | ✅ | Transkrip + bubble streaming (`AIToken`) + ringkasan diff |
| **ToolPanel** | kanan, 30%, collapsible | ❌ (via `F`) | Live tool execution, evidence, diff hunks, progress plan — subscribe `ToolCalled` |
| **StatusBar** | bawah, 1 baris | ✅ | provider/model • session ID • spinner state |
| **Prompt** | bawah, 1 baris | ✅ | Input; `Tab` pindah fokus antar-pane |
| **Palette** | overlay `Ctrl+K` | ❌ | Semua `/command` + switch screen |
| **ApprovalModal** | overlay `push_screen` | ❌ | Konfirmasi eksekusi plan (ganti `input()` blocking) |

### Prinsip progressive disclosure
- **User baru** hanya melihat **chat + prompt + status bar** (mirip Nexa sekarang,
  hanya rapi) — tidak membingungkan.
- **Panel kanan opt-in** via tombol `F` — user lanjut bisa buka tools/evidence/plan.
- **Palette `Ctrl+K`** — semua `/command` yang ada di `shell.py:7-29`
  dipertahankan, tidak ada fitur yang hilang.

### Kaitan dengan perbaikan kode (Bagian A)
- **H-1** → streaming token dirender di ChatScreen; ToolPanel menerima event tool
  terpisah; hapus `RedirectedStdout`.
- **C-2** → Approval jadi modal `push_screen`, tidak menyatu ke chat.
- **H-2** → Palette bisa memilih command + meneruskan input lanjutan.

---

## Status Tracking

| Item | Status |
| :--- | :--- |
| Bagian A — review findings | ✅ Dituangkan |
| Bagian B — layout target | ✅ Dituangkan |
| C-1 `style=` crash approval | ✅ **Selesai** — dipindah ke CSS `#approval-markdown-scroll` |
| C-2 double-handling approval | ✅ **Selesai** — `enable_tui_mode()` + `bus.unsubscribe()` |
| C-3 stdout redirect crash fallback | ✅ **Selesai** — ganti hijack global `sys.stdout` → `contextlib.redirect_stdout(ChatStdout)` scoped per-worker (`app.py:128`) |
| H-1 stdout hijack invasive | ✅ **Selesai** — `ChatStdout` + filter spinner `\r`/`[|]` |
| H-2 palette | ✅ **Selesai** — `Option(id=...)` + `event.option.id` |
| H-3 payload None | ✅ **Selesai** — guard `ctx.payload or {}` |
| H-4 tool panel O(n²) | ✅ **Selesai** — `RichLog.write` |
| M-1 session_id None print | ✅ **Selesai** |
| M-2 test streaming provider remote | ✅ **Selesai** — `test_stream_providers.py` (6 test, mocked SSE) |
| M-3 `__init__.py` | ✅ **Selesai** — `ui/`, `ui/screens/`, `ui/widgets/` |
| M-4 test routing `on_bus_message` | ✅ **Selesai** — `test_app_ui.py` (6 headless test) |
| Cleanup duplikat `on_mount` + CSS `#chat-scroll` | ✅ **Selesai** |

### Hasil akhir
- Full test suite: **46 passed, 4 warnings** (naik dari 34; +12 test baru).
- Verifikasi headless TUI: mount, submit, ToolCalled, BeforeApproval→modal, palette, toggle panel — semua lulus.
- Layout multi-zona aktif: chat mengisi, tool panel collapsible via `F`.
