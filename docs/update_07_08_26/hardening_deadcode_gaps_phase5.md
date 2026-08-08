# Rencana: Hardening, Dead Code, & Gap Kecil Phase 5

*Status: Artefact Perencanaan — 07 Agustus 2026*

Dokumen ini adalah rencana pembersihan pasca-Phase 5 yang tidak menambah fitur
baru, tapi menghilangkan risiko keamanan nyata, dead code, dan gap kecil yang
ditemukan selama verifikasi C.1–C.4. Berisi audit, keputusan, langkah eksekusi,
dan status tracking.

---

## 1. Ringkasan

Tiga area:
- **Opsi 1 — Hardening Keamanan** (`GitTool.execute` shell injection;
  `SearchTool` Windows-only).
- **Opsi 2 — Dead code / duplikasi** (`pipeline/patch.py` deprecated setelah
  migrasi C.4; audit file mati).
- **Opsi 4 — Gap kecil** (race condition scan; test coverage Semantic Cache).

---

## 2. Opsi 1 — Hardening Keamanan

### 2.1 BUG-H1: `GitTool.execute()` → `shell=True` (CRITICAL)

**Lokasi:** `nexa/core/agent/tools/knowledge/git.py:80-100`
**Risiko:** command injection. Tool di-register ke LLM (`git.py:195`), jadi LLM
atau attacker yang mengendalikan prompt bisa menyuntikkan perintah arbitrer.
Guard saat ini hanya `command.startswith("git")` — lemah.

```python
def execute(self, command: str) -> str:
    if not command.startswith("git"):
        return "Error: Only git commands are allowed."
    result = subprocess.run(command, ..., shell=True)   # ⚠️ shell=True
```

**Fix:**
```python
import shlex
def execute(self, command: str) -> str:
    try:
        args = shlex.split(command)
    except ValueError:
        return "Error: Could not parse command."
    if not args or args[0] != "git":
        return "Error: Only git commands are allowed."
    allowed = {"status", "diff", "log", "blame", "branch", "rev-parse",
               "show", "remote", "tag", "stash", "ls-files"}
    if len(args) >= 2 and args[1] in allowed:
        result = subprocess.run(args, ..., shell=False)  # ✅ no shell
        ...
    return "Error: Command not in allowed list."
```

**Aturan:**
- `shell=False` selalu untuk input dari LLM.
- Whitelist subcommand Git read-only (tidak termasuk `push`/`reset`/`clean`).
- Parsing argv memakai `shlex.split`; jika gagal → tolak.

### 2.2 BUG-H2: `SearchTool.text()` → `findstr` Windows-only (HIGH)

**Lokasi:** `nexa/core/agent/tools/knowledge/search.py:17-19`
**Risiko:** crash/blank di Linux/macOS; limitasi pattern.
**Fix:** backend portabel bertingkat:
1. `rg` tersedia → `["rg", "-n", "-i", query, path]`.
2. `grep` tersedia → `["grep", "-rn", "-i", query, path]`.
3. Fallback Python murni: `os.walk` + substring scan (`errors='replace'`),
   batasi 50 hasil, ignore `ignore_dirs` (sama seperti indexer).

---

## 3. Opsi 2 — Dead Code / Duplikasi

### 3.1 BUG-D1: `pipeline/patch.py` deprecated tapi masih ada

**Kondisi:** setelah migrasi C.4, `PatchEngine.calculate()` di
`pipeline/patch.py:26` **tidak dipakai siapa pun**. Namun **`PatchApplier` dan
`PatchResult` (OldPatchResult) masih dipakai** untuk CREATE/DELETE/COMMAND
(`transaction.py:5,34`).

**Keputusan: A — hapus class `PatchEngine` dari `pipeline/patch.py`**; biarkan
`PatchApplier` + `PatchResult`. Tambah test bahwa tidak ada import
`pipeline.patch.PatchEngine` tersisa.

### 3.2 BUG-D2: Audit file mati lain

- `cognitive/engines/acquisition.py` → **sudah dihapus** ✅
- Audit lanjutan: cari modul `.py` di `nexa/` dengan 0 import (dead code).

---

## 4. Opsi 4 — Gap Kecil

### 4.1 BUG-G1: Race condition `scan_workspace(async_scan=True)`

**Lokasi:** `file.py:14` + `indexer.py:82-87`
**Masalah:** `read_symbol`/`find` bisa dipanggil **sebelum** thread scan selesai
→ hasil kosong/miss. Test golden mengakali dengan `_do_scan()` sinkron dulu.

**Fix:** tambah `_scan_done` Event + `wait_for_scan()` di `WorkspaceIndexer`;
`FileTool.read_symbol`/`find` memanggil `wait_for_scan()` di awal.

### 4.2 BUG-G2: Semantic Cache hit-rate belum teruji

**Kondisi:** C.2 diimplementasikan & di-wire, belum ada test yang membuktikan
query kedua memakai cache (tidak re-parse).

**Test:** pakai `SQLiteCache` temp; `RegexSummarizer.summarize()` dua kali konten
sama → `set` hanya 1x (kedua = hit). Plus test persisten antar dua instans.

---

## 5. Prioritas & Urutan Eksekusi

| Prioritas | Item | Effort | Blocker |
| :-: | :--- | :--- | :--- |
| P0 | BUG-H1 Git `shell=True` | Kecil | Ya (keamanan) |
| P0 | BUG-H2 SearchTool `findstr` | Kecil | Ya (portabilitas) |
| P1 | BUG-G1 Race scan | Kecil | Tidak |
| P1 | BUG-G2 Cache hit-rate test | Kecil | Tidak |
| P2 | BUG-D1 hapus `pipeline.patch.PatchEngine` | Kecil | Tidak |
| P2 | BUG-D2 audit dead code | Sedang | Tidak |

---

## 6. Verifikasi

1. Test baru (H1/H2/G1/G2/D1) lulus.
2. Suite penuh: `py -m pytest tests -q` → 31+ tetap hijau.
3. Smoke test: `FileTool` pada workspace temp → `read_symbol` langsung
   (tanpa prescan) berhasil.
4. Import-order regression tetap lulus.

---

## 7. Status Tracking

| Item | Status |
| :--- | :--- |
| Audit keamanan & dead code | ✅ 07 Agustus 2026 |
| BUG-H1 (Git shell) | ✅ Selesai |
| BUG-H2 (SearchTool portabel) | ✅ Selesai |
| BUG-G1 (race scan) | ✅ Selesai |
| BUG-G2 (cache test) | ✅ Selesai |
| BUG-D1 (hapus legacy PatchEngine) | ✅ Selesai |
| BUG-D2 (audit dead code) | ✅ Selesai |

---

## 8. Referensi Terkait

- `nexa/core/agent/tools/knowledge/git.py:80-100` — `shell=True`.
- `nexa/core/agent/tools/knowledge/search.py:11-28` — `findstr`.
- `nexa/core/agent/tools/knowledge/file.py:14` — `async_scan=True`.
- `nexa/core/agent/indexer.py:78-87` — `scan_workspace`/`_do_scan`.
- `nexa/core/pipeline/patch.py:21-42` — `PatchEngine` legacy.
- `nexa/core/pipeline/transaction.py:5,34` — pemakai `PatchApplier`/`OldPatchResult`.
- `docs/update_07_08_26/fix_c4_ast_patch_unified_diff.md` — migrasi C.4 (asal duplikasi).
