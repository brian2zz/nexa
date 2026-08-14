# 🛠️ Planning: Perbaikan Minor Slash Commands (Timeline, Stub, Redo, Test)

> **Status:** RENCANA — **jangan dieksekusi** sampai disetujui.
> **Tanggal:** 14 Agustus 2026
> **Base:** commit `9fd76cc` (tree bersih)
> **Rujukan:** `docs/nexa/slash_commands_execution_plan.md` (plan utama), `.opencode/plans/slash_commands_audit_and_roadmap.md`

---

## 1. Ringkasan (1 menit)

Fase A–C & F besar dari plan utama sudah selesai dan di-commit. Audit ulang menemukan **4 item sisa** yang murni pembersihan kecil:

1. Fix `handle_timeline` (baca field `payload` yang benar).
2. Hapus dead stub branch + `handle_stub`.
3. Hapus class-attribute `_redo_stack` sisa.
4. Tambah test untuk 4 handler baru.

Semua item independen, kecil, dan bisa dikerjakan dalam 1 sesi lalu di-commit bersama.

---

## 2. Detail Item

### Item 1 — Fix `handle_timeline`

**Lokasi:** `nexa/commands/ai/slash_commands.py:412-433`

**Masalah:** `EventContext` (definisi di `nexa/core/models/events.py:9-19`) punya field `payload`, **bukan** `data`. Kode membaca `evt.data` (`:422`) yang selalu `{}`, dan mengecek kunci `input_tokens`/`output_tokens` (`:426`) padahal `UsageTrackingProvider` publish `prompt_tokens`/`completion_tokens` (lihat `nexa/core/observability/usage_tracking.py:52-53`). Akibat: kolom info summary di `/timeline` tidak pernah muncul.

**Cara:**
```python
data = getattr(evt, "payload", None)
if isinstance(data, dict):
    if "prompt_tokens" in data:
        info_summary = f" [tokens: in={data.get('prompt_tokens')}, out={data.get('completion_tokens')}]"
    elif "plan" in data:
        info_summary = " [ExecutionPlan ready]"
    elif "thought" in data:
        info_summary = f" [thought: {str(data.get('thought', ''))[:30]}]"
```

**Verifikasi:** manual `/timeline` setelah interaksi → muncul `[tokens: in=.., out=..]`; `pytest` hijau.

---

### Item 2 — Hapus Dead Stub Branch + `handle_stub`

**Lokasi:**
- `nexa/commands/ai/shell.py:218-219` — branch `elif first_word in ["/skills", "/variants", "/mcps", "/timeline"]: return slash_handler.handle_stub(...)`
- `nexa/commands/ai/slash_commands.py:496-498` — method `handle_stub`

**Alasan:** `/skills`, `/variants`, `/mcps`, `/timeline` sudah masuk `SLASH_DISPATCH` (`slash_commands.py:83-86`) dan ditangani di `shell.py:209-214` lebih dulu → branch stub **tak pernah tercapai** (dead code). `handle_stub` jadi tidak dipanggil siapa pun.

**Cara:**
1. Hapus `shell.py:218-219`.
2. Hapus method `handle_stub` di `slash_commands.py:496-498`.
3. Grep `handle_stub` → pastikan 0 referensi tersisa.

**Verifikasi:** `grep handle_stub` kosong; `pytest` hijau.

---

### Item 3 — Hapus Class-Attribute `_redo_stack` Sisa

**Lokasi:** `nexa/commands/ai/slash_commands.py:371`

**Masalah:** `_redo_stack: List[Dict[str, Any]] = []` masih tersisa di level class. Sudah ada instance attribute `self._redo_stack` di `__init__` (`:97`). Class attr redundan (instance attr menimpa, jadi tidak berbahaya, tapi mengganggu kebersihan).

**Cara:** Hapus baris `:371`. Pastikan `self._redo_stack` tetap di `__init__` (`:97`).

**Verifikasi:** grep `_redo_stack` → hanya muncul di `__init__` (`:97`), `_load_redo_stack`, `_save_redo_stack`, `handle_undo`, `handle_redo`.

---

### Item 4 — Tambah Test Handler Baru

**Lokasi:** `tests/core/test_slash_commands.py`

**Cara — contoh test timeline:**
```python
class MockBus:
    def __init__(self, events):
        self._events = events
    def get_history(self, limit=50):
        return self._events[-limit:]

def test_handle_timeline(tmp_path):
    from nexa.core.models.events import EventContext
    from nexa.core.models.enums import EventPriority
    evt = EventContext(event_name="TokenUsage", timestamp="2026-08-14T00:00:00",
                       source="UsageTrackingProvider", priority=EventPriority.NORMAL,
                       session_id="1", payload={"prompt_tokens": 100, "completion_tokens": 50})
    runtime = MockRuntime()
    runtime.bus = MockBus([evt])
    handler = SlashCommandHandler(runtime, str(tmp_path), MockMemory(), MockFacts(), MockPins(), "django")
    assert handler.handle_timeline("", "") is True   # info summary token muncul
```

**Test lain:**
- `test_handle_skills(tmp_path)` — buat `tmp_path/skills/demo/SKILL.md` → `handle_skills` mencantumkan `demo`.
- `test_handle_variants` — `handle_variants` menampilkan daftar varian (assert `True`).
- `test_handle_mcps(tmp_path)` — buat `mcp_config.json` valid + tanpa file → kedua jalur tidak crash.

**Perhatian:** `MockRuntime` perlu properti `bus` (periksa `MockRuntime` di file test yang sudah ada — tambahkan `self.bus = PipelineBus(...)` bila belum).

**Verifikasi:** `pytest tests/core/test_slash_commands.py -q` hijau.

---

## 3. Urutan & Commit

| Urutan | Item | File |
| :---: | :--- | :--- |
| 1 | Fix timeline payload | `slash_commands.py` |
| 2 | Hapus stub branch + `handle_stub` | `shell.py`, `slash_commands.py` |
| 3 | Hapus class-attr `_redo_stack` | `slash_commands.py` |
| 4 | Tambah test | `tests/core/test_slash_commands.py` |

Setelah selesai:
- `pytest tests -q` → hijau.
- Uji manual: `/timeline`, `/skills`, `/variants`, `/mcps`, `/undo`, `/redo`, `/editor`.
- Commit pesan sesuai gaya repo: `fix(ai): timeline reads payload, remove dead stub path, drop redundant redo stack attr, add handler tests`

---

## 4. Risiko

| Risiko | Mitigasi |
| :--- | :--- |
| Timeline key berbeda di event lain | Gunakan `get()` dengan default; tampilkan apa adanya |
| Menghapus stub branch ternyata masih dipakai | Grep `handle_stub` sebelum hapus |
| Test timeline bergantung event internals | Pakai `EventContext` langsung (deterministik) |

---

*Dokumen ini adalah rencana. Eksekusi dilakukan hanya setelah persetujuan pengguna.*