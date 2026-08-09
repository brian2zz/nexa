# Rencana Implementasi: StatusPanel Kanan (Versi, Token Spent, Todo, Proses) + Full Percakapan Kiri

*Status: Artefact Perencanaan untuk implementasi oleh agent lain (antigravity) — 09 Agustus 2026*

Dokumen ini adalah **rencana implementasi lengkap** untuk mengubah layout TUI `nexa ai`:

- **Panel kiri**: full percakapan (transkrip user + AI) — sudah ada, hanya penyesuaian layout.
- **Panel kanan (baru)**: panel status **selalu terlihat tanpa toggle** yang menampilkan:
  1. Info: versi Nexa, path project, provider, model, session ID.
  2. Context/Token spent: prompt tokens, completion tokens, total, estimasi biaya.
  3. Todo: daftar `work_items` dari Execution Plan (checklist).
  4. Proses yang dijalankan: log pipeline (Planning → Patch → Execution → Verification → Transformation).
- **Fitur konseptual**: "mengajukan pertanyaan ke Nexa supaya result lebih baik" — dirancang sebagai konsep terpisah (bagian 8), hanya dokumentasi.

Tujuan dokumen ini: agent lain (antigravity) dapat menerapkan seluruh perubahan **tanpa menebak-nebak**.

---

## 1. Ringkasan Perubahan (High-Level)

| # | File | Aksi |
| :- | :--- | :--- |
| 1 | `nexa/ui/widgets/status_panel.py` | **BARU** — widget `StatusPanel` |
| 2 | `nexa/ui/widgets/tool_panel.py` | Diganti/diarsipkan — fitur log tool dipindah ke `StatusPanel` |
| 3 | `nexa/ui/app.py` | Layout baru, handler event baru, token tracking |
| 4 | `nexa/commands/ai/shell.py` | Patch `ProviderFactory.create` agar mem-publish `TokenUsage` |
| 5 | `nexa/core/observability/usage_tracking.py` | **BARU** — wrapper provider `UsageTrackingProvider` |

Tidak ada perubahan di `nexa/core/ai/planner/*`, `nexa/core/events/bus.py`, `nexa/ui/bridge.py` — mereka sudah mendukung kebutuhan ini.

---

## 2. Desain UI

### 2.1 Layout Baru

```
┌────────────────────────────────────────────────────────────┐
│ Header (Textual default)                                    │
├───────────────────────────────────┬─────────────────────────┤
│                                   │  ┌───────────────────┐  │
│                                   │  │ 🖥 Nexa Status     │  │
│   #transcript (kiri)              │  │ Version: 1.0.0    │  │
│   ┌─────────────────────────────┐ │  │ Path: G:\...\nexa │  │
│   │ 🧑 User                     │ │  │ Provider: deepseek│  │
│   │ ...                         │ │  │ Model: deepseek-  │  │
│   │ 🤖 Nexa                     │ │  │        coder      │  │
│   │ ...                         │ │  ├───────────────────┤  │
│   │ [💭 Processes collapsible]  │ │  │ 📊 Context/Token  │  │
│   └─────────────────────────────┘ │  │ Prompt: 1,234     │  │
│   width: 1fr, scrollable           │  │ Output: 567       │  │
│                                   │  │ Total: 1,801      │  │
│                                   │  │ Cost: ~$0.0012    │  │
│                                   │  ├───────────────────┤  │
│                                   │  │ 📋 Todo           │  │
│                                   │  │ ☐ Fix button      │  │
│                                   │  │ ☐ Update style    │  │
│                                   │  ├───────────────────┤  │
│                                   │  │ ⚙ Proses          │  │
│                                   │  │ ✅ Planning       │  │
│                                   │  │ ⏳ Patch...       │  │
│                                   │  └───────────────────┘  │
│                                   │  #status-panel (kanan)   │
│                                   │  width: 40              │
├───────────────────────────────────┴─────────────────────────┤
│ StatusBar                                                    │
│ Input (dock bottom)                                          │
└────────────────────────────────────────────────────────────┘
```

### 2.2 Binding Keys

Hapus binding `f` (`toggle_tools`) karena panel kanan sekarang permanen.
Pertahankan: `ctrl+c` quit, `ctrl+k` palette, `pageup`/`pagedown` scroll transcript.

### 2.3 CSS di `NexaApp`

```css
#transcript {
    width: 1fr;
    height: 1fr;
    padding: 1;
    border: solid $surface;
}
#status-panel {
    width: 40;
    height: 1fr;
    border-left: solid $primary;
    background: $surface;
}
```

---

## 3. Data Flow (Arsitektur)

```
[worker thread: command_handler]                  [Textual main thread]
  provider.generate(messages)                          #transcript (kiri)
        │                                              ChatMessage user/ai
        ▼
  UsageTrackingProvider._report_usage()
        │ bus.publish_async(EventContext("TokenUsage",
        │   payload={prompt_tokens, completion_tokens}))
        ▼
  PipelineBus ──► Bridge.subscribe(bus, "*", app)
                      │ app.post_message(BusMessage(ctx))
                      ▼
              NexaApp.on_bus_message(ctx)
                      ├── "TokenUsage"  → status_panel.update_tokens(p, c)
                      ├── "AfterPlanning"/"BeforeApproval"
                      │                   → status_panel.set_todos(plan)
                      ├── "BeforePatch"/"AfterPatch"/"BeforeExecution"/
                      │   "AfterExecution"/... → status_panel.add_process(...)
                      └── "ToolCalled"  → status_panel.add_process(...)

  Planner engines mem-publish BeforePlanning/AfterPlanning/dll (sudah ada,
  tidak perlu diubah). Yang baru: hanya event "TokenUsage".
```

---

## 4. Spesifikasi File 1 — `nexa/ui/widgets/status_panel.py` (BARU)

Widget turunan `VerticalScroll` (dari `textual.containers`). Semua update melalui method
publik; dipanggil dari `NexaApp` pada thread main (lewat `call_from_thread` saat perlu).

### 4.1 Struktur (compose)

```python
class StatusPanel(VerticalScroll):
    DEFAULT_CSS = """
    StatusPanel {
        background: $surface;
        padding: 0 1;
    }
    .status-header {
        text-style: bold;
        color: $accent;
        padding-bottom: 1;
        border-bottom: solid $primary;
    }
    .status-section {
        text-style: bold;
        color: $text;
        margin-top: 1;
    }
    .status-info {
        color: $text-muted;
    }
    .status-todo-done {
        color: $success;
    }
    .status-todo-pending {
        color: $text;
    }
    """
```

- `compose()` yield:
  1. `Static("🖥 Nexa Status", classes="status-header", id="status-header")`
  2. `Static("", classes="status-info", id="status-info")` — versi/path/provider/model/session
  3. `Static("📊 Context & Token", classes="status-section")`
  4. `Static("Prompt: 0 · Output: 0 · Total: 0", id="status-tokens")`
  5. `Static("Cost: $0.0000", id="status-cost")`
  6. `Static("📋 Todo", classes="status-section")`
  7. `VerticalScroll(id="status-todo-list", classes="status-info")`
  8. `Static("⚙ Proses", classes="status-section")`
  9. `RichLog(id="status-process-log", wrap=True, highlight=True)`

### 4.2 Method Publik

```python
def set_info(self, *, version: str, project_path: str,
             provider: str, model: str, session_id):
    """Isi blok info."""
    self.query_one("#status-info").update(
        f"Version : {version}\n"
        f"Path    : {project_path}\n"
        f"Provider: {provider}\n"
        f"Model   : {model}\n"
        f"Session : {session_id}"
    )

def update_tokens(self, prompt_tokens: int, completion_tokens: int):
    """Akumulasi token per sesi lalu re-render."""
    self._prompt_total += prompt_tokens
    self._completion_total += completion_tokens
    total = self._prompt_total + self._completion_total
    self.query_one("#status-tokens").update(
        f"Prompt: {self._prompt_total:,} · Output: {self._completion_total:,} · Total: {total:,}")
    self.query_one("#status-cost").update(f"Cost: {self.estimate_cost():.4f} USD")

def estimate_cost(self) -> float:
    """Estimasi biaya. Ollama = $0. Tabel harga pada §7."""
    return (
        self._prompt_total * self.PROMPT_RATE
        + self._completion_total * self.COMPLETION_RATE
    ) / 1_000_000  # rate per million tokens

def set_todos(self, work_items):
    """Render checklist todo dari plan. work_items: iterable WorkItem/dict."""
    container = self.query_one("#status-todo-list")
    container.remove_children()
    for i, w in enumerate(work_items, 1):
        title = w.title if hasattr(w, "title") else w.get("title", "")
        affected = getattr(w, "affected_files", []) or w.get("affected_files", [])
        files = ", ".join(affected[:3])
        label = f"☐ [{i}] {title}"
        if files:
            label += f"  ( {files} )"
        container.mount(Static(label, classes="status-todo-pending", id=f"todo-{i}"))

def add_process(self, text: str, status: str = "info"):
    """Tulis satu baris ke log proses. status: info/ok/err/running."""
    icon = {"ok": "✅", "err": "❌", "running": "⏳", "info": "•"}.get(status, "•")
    self.query_one("#status-process-log", RichLog).write(f"{icon} {text}")

def log_tool(self, tool_name: str, status: str = "running"):
    """Kompatibel dengan ToolPanel lama. status: running/success/error."""
    mapping = {"running": "running", "success": "ok", "error": "err"}
    self.add_process(tool_name, mapping.get(status, "info"))
```

### 4.3 Konstanta Rate (per 1M token)

```python
# (input, output) USD per 1M token — default 0 (misal ollama/mock)
PROVIDER_RATES = {
    "deepseek": (0.27, 1.10),   # deepseek-chat (cek harga terbaru saat implementasi)
    "groq":     (0.30, 0.60),
    "ollama":   (0.0, 0.0),
}
PROMPT_RATE, COMPLETION_RATE = PROVIDER_RATES.get("deepseek", (0.0, 0.0))
```

Buat `set_provider_rates(provider: str)` dipanggil dari `set_info` agar rate mengikuti provider aktif.

---

## 5. Spesifikasi File 2 — `nexa/ui/widgets/tool_panel.py` (diganti)

Opsi: (a) hapus file & import, atau (b) jadikan `ToolPanel = StatusPanel` alias.
Rekomendasi **(a) hapus** dan pindahkan fungsionalitas `log_tool` ke `StatusPanel.log_tool` (tetap dipanggil dari `on_bus_message`). Pastikan tidak ada import `tool_panel` tersisa selain di `nexa/ui/app.py`.

---

## 6. Spesifikasi File 3 — `nexa/ui/app.py` (UPDATE)

### 6.1 Import

```python
from nexa.ui.widgets.status_panel import StatusPanel
# hapus: from nexa.ui.widgets.tool_panel import ToolPanel
from nexa import __version__ as NEXA_VERSION
from nexa.config import Config
```

### 6.2 `compose()`

```python
def compose(self) -> ComposeResult:
    yield Header()
    with Horizontal():
        with VerticalScroll(id="transcript"):
            pass
        yield self.status_panel          # ← StatusPanel(id="status-panel")
    self.status_bar = StatusBar()
    yield self.status_bar
    yield Input(placeholder="Nexa> _", id="prompt-input")
```

`__init__`: ganti `self.tool_panel = ToolPanel(id="tool-panel")` dengan
`self.status_panel = StatusPanel(id="status-panel")`.

### 6.3 `on_mount()` — isi info panel

```python
def on_mount(self):
    self.query_one("#prompt-input").focus()
    Bridge.subscribe(self.runtime.bus, "*", self)

    provider = Config.get("provider", "mock")
    model = Config.get(f"{provider}.model", "unknown")
    self.status_panel.set_info(
        version=NEXA_VERSION,
        project_path=self.runtime.cwd,
        provider=provider,
        model=model,
        session_id=self.runtime.session_id,
    )
    self.status_panel.set_provider_rates(provider)

    self.original_stdout = sys.stdout
    sys.stdout = RedirectedStdout(self)
    self.current_ai_msg = None
    self.print_to_chat("Welcome to Nexa AI Interactive Shell (TUI).\nType /help for available commands or /exit to quit.", role="ai")
```

### 6.4 BINDINGS — hapus toggle

```python
BINDINGS = [
    ("ctrl+c", "quit", "Quit"),
    ("ctrl+k", "palette", "Command Palette"),
    ("pageup", "scroll_transcript_up", "Scroll Up"),
    ("pagedown", "scroll_transcript_down", "Scroll Down"),
]
# HAPUS method action_toggle_tools()
```

### 6.5 `on_bus_message()` — handler event baru

Tambahkan cabang baru di `on_bus_message` (jangan hapus cabang `ToolCalled`/`BeforeApproval` yang ada):

```python
def on_bus_message(self, message: BusMessage):
    ctx = message.event_context
    payload = ctx.payload or {}

    if ctx.event_name == "TokenUsage":
        p = payload.get("prompt_tokens", 0) or 0
        c = payload.get("completion_tokens", 0) or 0
        self.status_panel.update_tokens(p, c)
        return

    if ctx.event_name in ("BeforePlanning", "AfterPlanning", "PlanningFailed",
                          "BeforePatch", "AfterPatch", "PatchFailed",
                          "BeforeExecution", "AfterExecution", "ExecutionFailed",
                          "BeforeVerification", "AfterVerification",
                          "BeforeTransformation", "AfterTransformation",
                          "RetryStarted", "RollbackStarted", "RollbackCompleted",
                          "RecoverySucceeded", "RecoveryFailed"):
        # konversi event_name → baris teks yang mudah dibaca
        self.status_panel.add_process(self._human_event(ctx), self._status_of(ctx))
        return

    if ctx.event_name == "ToolCalled":
        tool_name = payload.get("tool_name", "unknown")
        status = payload.get("status", "running")
        self.status_panel.log_tool(tool_name, status)
        return

    if ctx.event_name in ("AfterPlanning", "BeforeApproval"):
        plan = payload.get("plan")
        work_items = (getattr(plan, "work_items", [])
                      if not isinstance(plan, dict)
                      else plan.get("work_items", []))
        if work_items:
            self.status_panel.set_todos(work_items)
        # jangan return — BeforeApproval tetap lanjut ke modal approval di bawah

    if ctx.event_name == "BeforeApproval":
        ...  # kode modal approval yang SUDAH ADA, pertahankan aslinya
```

Helper private:

```python
_EVENT_LABELS = {
    "BeforePlanning": ("Planning started", "running"),
    "AfterPlanning":  ("Planning complete", "ok"),
    "PlanningFailed": ("Planning failed", "err"),
    "BeforePatch":    ("Patching started", "running"),
    "AfterPatch":     ("Patch applied", "ok"),
    "PatchFailed":    ("Patch failed", "err"),
    "BeforeExecution":("Execution started", "running"),
    "AfterExecution": ("Execution complete", "ok"),
    "ExecutionFailed":("Execution failed", "err"),
    "BeforeVerification":("Verification started", "running"),
    "AfterVerification": ("Verification complete", "ok"),
    "BeforeTransformation":("Transformation started", "running"),
    "AfterTransformation": ("Transformation complete", "ok"),
    "RetryStarted":   ("Retrying...", "running"),
    "RollbackStarted":("Rollback started", "running"),
    "RollbackCompleted":("Rollback complete", "ok"),
    "RecoverySucceeded":("Recovery complete", "ok"),
    "RecoveryFailed": ("Recovery failed", "err"),
}

def _human_event(self, ctx) -> str:
    label, _ = self._EVENT_LABELS.get(ctx.event_name, (ctx.event_name, "info"))
    return label

def _status_of(self, ctx) -> str:
    _, status = self._EVENT_LABELS.get(ctx.event_name, ("", "info"))
    return status
```

Catatan penting: `on_bus_message` dieksekusi di thread main Textual — aman untuk meng-update widget langsung.

---

## 7. Spesifikasi Token Tracking — `nexa/core/observability/usage_tracking.py` (BARU) + patch di shell.py

### 7.1 Kenapa wrapper di `ProviderFactory`

Semua panggilan `provider.generate()` (intent classifier, chat, explain, dan engine
planner: hypothesis/reasoning/planning) melewati `ProviderFactory.create()`. Dengan
membungkus provider sekali di factory, **semua** token usage tertangkap tanpa mengubah
setiap titik pemanggil.

### 7.2 File baru: `nexa/core/observability/usage_tracking.py`

```python
import datetime
from typing import Callable
from nexa.core.ai.providers.base import LLMProvider
from nexa.core.events.bus import PipelineBus
from nexa.core.models.events import EventContext
from nexa.core.models.enums import EventPriority


class UsageTrackingProvider(LLMProvider):
    """Proxy yang membungkus provider asli dan mem-publish usage token ke bus."""

    def __init__(self, inner: LLMProvider, bus: PipelineBus,
                 session_id_fn: Callable[[], int]):
        self._inner = inner
        self._bus = bus
        self._session_id_fn = session_id_fn

    # --- delegasi ---
    def health(self) -> bool:
        return self._inner.health()

    def list_models(self):
        return self._inner.list_models()

    # --- generate: lapisi dengan pelaporan usage ---
    def generate(self, messages, temperature=0.2, tools=None):
        raw = self._inner.generate(messages, temperature=temperature, tools=tools)
        self._report(raw)
        return raw

    def stream(self, messages, temperature=0.2, tools=None):
        for chunk in self._inner.stream(messages, temperature=temperature, tools=tools):
            yield chunk

    def __getattr__(self, name):
        # pastikan method lain tetap tersedia
        return getattr(self._inner, name)

    def _report(self, raw):
        if not isinstance(raw, dict):
            return
        usage = raw.get("usage") or {}
        prompt = usage.get("prompt_eval_count", 0)
        completion = usage.get("eval_count", 0)
        if not prompt and not completion:
            return
        self._bus.publish_async(EventContext(
            event_name="TokenUsage",
            timestamp=datetime.datetime.now().isoformat(),
            source="UsageTrackingProvider",
            priority=EventPriority.NORMAL,
            session_id=self._session_id_fn(),
            payload={
                "prompt_tokens": prompt,
                "completion_tokens": completion,
            },
        ))
```

Catatan: `publish_async` digunakan agar tidak memblokir worker thread; `PipelineBus`
sudah thread-safe (`ThreadPoolExecutor`).

### 7.3 Patch di `nexa/commands/ai/shell.py` — bagian `handle()`

Lokasi: blok `if sys.stdout.isatty():` (sekitar baris 748–765), **sebelum** `app.run()`.

```python
if sys.stdout.isatty():
    try:
        from nexa.ui.app import NexaApp
        from nexa.core.agent.session import SessionRecoveryManager
        from nexa.core.ai.providers.factory import ProviderFactory
        from nexa.core.observability.usage_tracking import UsageTrackingProvider

        recovery = SessionRecoveryManager(runtime.memory)
        recovered_id = recovery.prompt_recovery(runtime.cwd)
        if recovered_id is not None:
            runtime.session_id = recovered_id
        else:
            runtime.session_id = runtime.memory.create_session(runtime.cwd)

        runtime.enable_tui_mode()

        # --- WRAP provider agar mem-publish TokenUsage (HANYA untuk TUI) ---
        _original_create = ProviderFactory.create.__func__  # classmethod unwrap

        def _tracked_create():
            inner = _original_create(ProviderFactory)      # panggil implementasi asli
            return UsageTrackingProvider(inner, runtime.bus, lambda: runtime.session_id)

        ProviderFactory.create = classmethod(_tracked_create)

        app = NexaApp(command_handler, runtime)
        try:
            app.run()
        finally:
            ProviderFactory.create = classmethod(_original_create)  # restore
            runtime.bus.shutdown(wait=True)
        return
    except Exception as e:
        print(f"[!] Failed to start Textual UI: {e}. Falling back to basic shell.")

runtime.start_loop(get_input, command_handler)
```

> ⚠️ Saat implementasi: pastikan cara mengambil implementasi classmethod asli benar.
> Alternatif yang lebih aman dan sederhana: monkey-patch langsung method instance:
> ```python
> _original_create = ProviderFactory.create
> ProviderFactory.create = classmethod(lambda cls: UsageTrackingProvider(
>     _original_create(), runtime.bus, lambda: runtime.session_id))
> ```
> (valid karena `classmethod` tidak terikat ke instance tertentu saat dipanggil lewat cls).

### 7.4 Format usage per provider (referensi)

| Provider | Field prompt | Field completion |
| :--- | :--- | :--- |
| `deepseek.py:57` | `prompt_eval_count` | `eval_count` |
| `groq.py:63` | `prompt_eval_count` | `eval_count` |
| `ollama.py:35` | `prompt_eval_count` | `eval_count` |
| `mock.py:93` | `{}` (tidak ada) | — |

Semua sudah konsisten dengan `_report()` di §7.2.

---

## 8. Konsep: "Mengajukan Pertanyaan ke Nexa supaya Result Lebih Baik" (DOKUMENTASI SAJA)

> Ini adalah **konsep** — diimplementasikan sebagai dokumen desain, bukan kode pada
> iterasi ini, sesuai keputusan user.

### 8.1 Masalah saat ini

`ClarificationEngine.ask_user()` (`nexa/core/ai/cognitive/engines/clarification.py:118`)
memakai `input()` langsung di terminal. Saat dipanggil dari dalam **worker thread TUI**,
`input()` akan memblokir thread worker dan **berpotensi menggantung/hang** UI Textual,
karena stdin dibaca bersamaan oleh Textual.

### 8.2 Desain usulan (masa depan)

1. `ClarificationEngine` tidak lagi memakai `input()`. Ia cukup mem-publish event
   `ClarificationRequested` (payload: daftar `ClarificationQuestion`) dan **menunggu**
   event balasan `ClarificationAnswered` (payload: dict `{key: answer}`).
2. UI TUI menangkap `ClarificationRequested`, menampilkan pertanyaan di panel kiri
   atau modal ringan, mengumpulkan jawaban dari `Input`, lalu mem-publish
   `ClarificationAnswered` → pipeline lanjut dengan `enriched_goal`.
3. Implementasi mekanisme tunggu-jawab dapat memakai `threading.Event` di sisi
   command_handler, atau refactor pipeline agar async.
4. Nilai tambah: user bisa bertanya balik kapan pun (bukan hanya saat klarifikasi)
   dengan memasukkan jawaban/follow-up ke transkrip; AI memakainya untuk memperbaiki
   rencana berikutnya via `conversation_memory` (sudah otomatis tersimpan oleh
   `memory_manager`).

Konsep ini **tidak diimplementasikan sekarang** — hanya didokumentasikan.

---

## 9. Checklist Implementasi (untuk antigravity, urut)

1. Buat `nexa/core/observability/usage_tracking.py` (persis §7.2).
2. Buat `nexa/ui/widgets/status_panel.py` (persis §4).
3. Update `nexa/ui/app.py`:
   - import `StatusPanel`, `NEXA_VERSION`, `Config` (§6.1)
   - `__init__` ganti ToolPanel → StatusPanel (§6.2)
   - `compose()` baru (§6.2)
   - CSS baru: transcript 1fr, status-panel width 40 (§2.3)
   - BINDINGS hapus `f` + hapus `action_toggle_tools` (§6.4)
   - `on_mount` isi info panel (§6.3)
   - `on_bus_message` tambah handler (§6.5)
4. Update `nexa/commands/ai/shell.py` blok TUI: wrap `ProviderFactory.create` + restore
   di `finally` (§7.3).
5. Hapus `nexa/ui/widgets/tool_panel.py` dan semua import-nya (§5).
6. Jalankan verifikasi (§10).

---

## 10. Verifikasi

1. `python -m nexa ai` (atau `nexa ai`) dari root project.
2. Pastikan:
   - Panel kanan tampil permanen (tanpa menekan F), panel kiri penuh.
   - Info menampilkan versi/path/provider/model/session yang benar.
   - Ketik pertanyaan biasa → setelah jawaban AI muncul, angka Prompt/Output di panel
     kanan **bertambah** sesuai usage provider.
   - Ketik perintah yang memicu plan (misal `/plan ...` atau goal yang di-classify PLAN)
     → baris `Planning started`/`Planning complete` + checklist Todo muncul di panel kanan.
   - Jika eksekusi berjalan, log Patch/Execution muncul.
   - `pageup`/`pagedown` tetap scroll transkrip kiri.
   - Exit bersih (`ctrl+c`) tanpa hang, dan `ProviderFactory.create` ter-restore
     (tidak berdampak pada sesi berikutnya).
3. Jalankan test suite yang ada: `python -m pytest tests -q` (pastikan tidak regresi).
   Khususnya tes yang mengimpor `nexa.ui.app` atau `shell`.

---

## 11. Risiko & Catatan

- **`call_from_thread` vs thread**: `on_bus_message` dijalankan di main thread Textual
  (via `Bridge` → `post_message`), jadi aman memanggil widget langsung. Jangan memanggil
  `status_panel` dari worker thread tanpa `call_from_thread`.
- **`ProviderFactory.create` restore**: wajib di `finally`, supaya sesi non-TUI dan
  sesi TUI berikutnya tidak salah wrap.
- **Estimasi cost** adalah perkiraan; rate token berubah, gunakan konstanta yang bisa
  dikonfigurasi. Ollama/mock = $0.
- **`ToolCalled` event** saat ini tidak dipublish dari mana pun (baris
  `nexa/core/agent/tools/pipeline.py:15` ter-comment). Jika ingin log tool muncul,
  aktifkan publish tersebut atau tambahkan publish di titik eksekusi tool.
- **Jangan mengubah** alur `BeforeApproval` yang sudah ada (modal approval) — hanya
  menambah cabang `set_todos` sebelum blok modal.
