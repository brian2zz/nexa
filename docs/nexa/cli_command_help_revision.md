# 🧭 Konsep Revisi Command & Help CLI — Nexa

> **Status:** Rencana (belum dieksekusi)
> **Tanggal:** 12 Agustus 2026
> **File terkait:** `nexa/cli.py`, `nexa/commands/**`

---

## 1. Latar Belakang

Analisis CLI `nexa` menemukan 5 masalah struktural pada sistem perintah & help:

1. **`nexa help` / `nexa --help` / `nexa -h` justru CRASH**, bukan menampilkan help.
   - Tidak ada dispatch untuk `help | --help | -h` di `cli.py`.
   - Error path memuat karakter `❌` → pada Windows (cp1252) memicu `UnicodeEncodeError`.
   - Akar masalah: `cli.py` tidak melakukan `sys.stdout.reconfigure('utf-8')`.

2. **Help root (tanpa argumen) sudah usang**.
   - Hanya menampilkan grup `django` & `flutter`.
   - Tidak menampilkan: grup `php`, perintah AI, `update`, `version`.

3. **Ada mapping rusak (dead entry)**.
   - `nexa django sync` → menunjuk `nexa.commands.django.sync` yang **sudah dihapus** → `ImportError` saat dijalankan.
   - Alias redundan: `nexa php make:migrate` dan `nexa php migrate` → module yang sama.

4. **Help grup tidak konsisten & tanpa deskripsi**.
   - `nexa django/flutter/php` hanya mencetak nama subcommand.
   - `nexa ai` bukan grup — langsung membuka shell, sehingga perintah AI tidak bisa di-list.
   - Konsep campur aduk: `nexa plan` (top-level) vs `nexa django generate` (namespaced).

5. **README tidak sinkron** dengan command yang sebenarnya ada.

---

## 2. Keputusan Desain (sudah dikonfirmasi)

| Keputusan | Pilihan |
| :--- | :--- |
| Namespace perintah AI | **Pindah ke grup `nexa ai <sub>`** — seragam dengan grup lain |
| `nexa django sync` | **Hapus dari registry** (module sudah dihapus) |
| Scope tambahan | **Help + registry saja** — `nexa config` / `nexa list` ditunda |

---

## 3. Konsep Baru — Registry Command (Satu Sumber Kebenaran)

Ganti 4 dict hardcoded di `cli.py` dengan **satu registry data-driven** di modul baru `nexa/commands/registry.py`.

### 3.1 Struktur Registry

```python
GROUPS = {
  "django":  [ {module, usage, description}, ... ],
  "flutter": [ {module, usage, description}, ... ],
  "php":     [ {module, usage, description}, ... ],
  "ai":      [ {module, usage, description}, ... ],
}
```

Tiap command berisi:
- `name` — nama perintah
- `module` — path modul handler (`handle(args)`)
- `usage` — sintaks pemakaian
- `description` — deskripsi singkat
- `hidden` — opsional (sembunyikan dari help)

### 3.2 Daftar Command Final per Grup

**🟡 Grup `django`** (penuh): `new · startapp · generate · make:api · build · install · run · doctor · inspect · dev`
→ `sync` **dihapus**.

**🟦 Grup `flutter`** (penuh): `new · create-module · gen-model · generate · run · doctor`.

**🐘 Grup `php`** (penuh): `new · make:module · make:model · generate · make:migration · migrate · install · run`
→ alias `make:migrate` **dihapus** (kanonik: `migrate`).

**🤖 Grup `ai`** (baru): `shell · scan · tree · analyze · plan · create · explain · ask`.

**🌐 Top-level tetap**: `update` · `version` (alias `-v`/`--version`) · `help`/`-h`/`--help`.
**Auto-detect shorthands** (didokumentasikan): perintah diarahkan sesuai tipe project (mis. `nexa run`, `nexa new`, `nexa generate`) — behavior lama dipertahankan.

### 3.3 Surface Help yang Konsisten

| Input | Output |
| :--- | :--- |
| `nexa` · `nexa help` · `nexa -h` · `nexa --help` | Root help: grup + command top-level + contoh penggunaan |
| `nexa help <cmd>` | Deskripsi + usage untuk satu command |
| `nexa help <group>` | Help grup lengkap |
| `nexa django -h` · `nexa django help` | Help grup: usage + deskripsi tiap subcommand |
| `nexa ai` (tanpa argumen) | Help grup `ai` (konsisten dengan grup lain) |
| `nexa ai shell` | Memasuki interactive shell |
| `nexa -v` / `--version`/`version` | Menampilkan versi |

---

## 4. Rencana Implementasi

### Langkah 1 — Modul baru `nexa/commands/registry.py`
- Definisi `GROUPS` + top-level metadata lengkap (usage & deskripsi tiap command).
- Helper render: `render_root_help()`, `render_group_help(group)`, `render_command_help(name)`.
- Fungsi validasi integritas: setiap `module` di `GROUPS` harus dapat di-import (mencegah mapping mati seperti `django sync`).

### Langkah 2 — Refactor `nexa/cli.py`
- Tambah `sys.stdout.reconfigure(encoding='utf-8')` di awal `main()` → hilangkan crash `UnicodeEncodeError` di seluruh command.
- Dispatch baca dari `registry` (ganti 4 dict hardcoded).
- Handler `help | -h | --help` di semua level.
- Pindahkan perintah AI ke grup `nexa ai <sub>`; **hapus alias top-level** (`nexa scan/tree/plan/create/explain/ask/ai`).
- Perbaiki gap fallback `nexa php <unknown>` → native `artisan` (bukan sekadar "Unknown").
- Pecah `main()` → `main()` + `dispatch(args)` agar mudah ditest.

### Langkah 3 — Penyesuaian handler AI (minimal)
- `nexa ai plan/create/scan/tree/ask/shell` menampilkan usage saat tanpa argumen.
- `-h/--help` per-command diizinkan (argparse / usage print). Tanpa kewajiban flag baru di semua handler. *(follow-up)*

### Langkah 4 — Dokumentasi
- `README.md`: update tabel command — tambah grup `ai`, hapus `django sync`, catat perintah AI namespaced.
- `CHANGELOG.md`: entri "Changed: CLI help & command structure".

### Langkah 5 — Test
- File baru: `tests/core/test_cli_registry.py`
- Verifikasi: semua `module` di registry ter-import tanpa error; `main(["help"])`, `main(["-h"])`, `main(["django","-h"])`, `main(["ai","-h"])`, `main(["ai","scan"])` → exit 0 + stdout memuat konten benar (tanpa crash encoding).

### Langkah 6 — Verifikasi akhir
- `py -3.14 -m nexa.cli help` · `--help` · `django -h` · `ai -h` · `ai scan`
- `pytest tests -q` → semua hijau
- Pastikan `nexa update` & `--version` tidak terganggu.

---

## 5. Breaking Changes (harus diperhatikan)

| Sebelum | Sesudah |
| :--- | :--- |
| `nexa scan` | `nexa ai scan` |
| `nexa plan` | `nexa ai plan` |
| `nexa create` | `nexa ai create` |
| `nexa explain` | `nexa ai explain` |
| `nexa ask` | `nexa ai ask` |
| `nexa ai` (langsung shell) | `nexa ai shell`; `nexa ai` → help grup |
| `nexa django sync` | **Dihapus** |
| `nexa php make:migrate` | `nexa php migrate` |

> Semua perubahan ini akan ditandai jelas di help root, README, dan CHANGELOG.

---

*Dokumen ini adalah rencana eksekusi. Eksekusi dilakukan hanya setelah persetujuan pengguna.*