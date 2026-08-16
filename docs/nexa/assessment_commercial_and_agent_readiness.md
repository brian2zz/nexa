# 📋 Asesmen Komprehensif: Kesiapan Komersial & Kapabilitas Agent — Nexa Framework

> **Status:** DOKUMENTASI SAJA — **tidak dieksekusi**. Dokumen ini hanya mencatat hasil audit, solusi yang disarankan, dan dampaknya.
> **Tanggal:** 16 Agustus 2026
> **Metode:** Inspeksi langsung terhadap kode (bukan asumsi), setiap klaim disertai referensi `file:line`.
> **Cakupan:** (A) Kesiapan komersial, (B) Kesiapan fitur, (C) Arsitektur / flow / framework output / ekosistem.
> **Versi teraudit:** v1.0.0 (commit HEAD, working tree berisi kerja Fase 6 yang belum di-commit).

---

## 0. Ringkasan Eksekutif

| Dimensi | Skor | Verdict |
| :--- | :---: | :--- |
| **Arsitektur & keamanan eksekusi** | 🟢 9/10 | Kuat; approval gate + rollback + verification adalah nilai jual |
| **Framework yang dihasilkan** (Django/Flutter/PHP) | 🟢 8/10 | Diferensiasi asli; tapi ada placeholder logic & bahasa campuran |
| **Kesiapan komersial** (legal/CI/rilis) | 🟠 5/10 | Kunci API plaintext, CI minim, tidak ada pipeline rilis |
| **Kapabilitas agent generalis** (vs opencode/Cursor) | 🟠 6–7/10 | Loop ada tapi belum closed-loop; ekosistem hampir semua stub |
| **Ekosistem** (MCP/skills/variants/provider/subagents) | 🔴 2/10 | Titik terlemah — MCP & skills nyata belum ada |

**Kesimpulan dua-lapis:**
1. Sebagai **agent scaffolding full-stack** (Django/Flutter/PHP): sudah **siap & mumpuni** — ini produk yang bisa dijual sekarang.
2. Sebagai **AI coding assistant generalis** (pesaing opencode/Cursor/Claude Code): **belum, ±65–70%** — hambatan terbesar ada di **ekosistem (MCP/skills)**, **loop yang belum self-repair**, dan **hasil generate yang berisi placeholder**.

---

## 1. Metodologi & Cakupan

Audit dilakukan dengan membaca langsung: CLI registry, agent loop, tool registry, pipeline eksekusi, generator, template, provider, konfigurasi, CI, dan test suite. Semua temuan diberi bukti `file:line`. Tidak ada perbaikan yang dieksekusi dalam dokumen ini; solusi ditulis sebagai rekomendasi.

---

# Bagian A — Kesiapan Komersial

## A.1 Keamanan Eksekusi (RCE/Sandbox) — 🔴 KRITIS

### Masalah
Tool `run_bash_command` mengeksekusi perintah yang dihasilkan LLM dengan `shell=True` secara penuh:

- `nexa/core/agent/tools/terminal.py:20-24` — `subprocess.run(command, shell=True, cwd=self.workspace_path, ...)`; LLM mengendalikan `command` tanpa sandbox, tanpa whitelist, tanpa filter.
- Pola `shell=True` tersebar luas: `slash_commands.py:143,335`, `django/build.py:19,69`, `django/install.py:29`, `django/run.py:16,49,55,166,170`, `pipeline/execution/runner.py:10`, `pipeline/execution/parser.py:10`, `ui/app.py:224,295`.
- Approval gate ada (`BeforeApproval` → `ApprovalGranted`), tapi di jalur `AILoopEngine` hanya `run_bash_command`/`write_file`/`edit_file_content` yang butuh approval; **tool lain auto-eksekusi** (`core/ai/agent_loop.py:254-265`).

### Solusi
1. Permission granular per tool: `allow/ask/deny` (evolusi dari satu flag `read_only`).
2. Sandbox bash: whitelist command (mis. `pytest`, `git`, `python`, `flutter`, `npm`), timeout keras, **truncate output** (mencegah ledakan token konteks).
3. Jika dijual sebagai SaaS/hosted: jalankan agent di container/sandbox (Firecracker/containerd), tanpa akses host, tanpa variabel env rahasia.

### Imbas jika dibiarkan
- **Sebagai CLI lokal**: risiko terbatas (pengguna mengeksekusi komandonya sendiri), namun LLM bisa memicu `rm -rf`, `git reset --hard`, atau unduh malware.
- **Jika dijual sebagai service/multi-tenant**: **RCE total** — satu prompt berbahaya = eksekusi kode arbitrer di server. Ini mematikan opsi SaaS dan bisa menimbulkan kerugian finansial & hukum.

---

## A.2 Penyimpanan Kredensial — 🔴 TINGGI

### Masalah
API key disimpan **plaintext** di `~/.nexa/config.json`:

- `nexa/config/__init__.py:7` — `_config_file = Path.home() / ".nexa" / "config.json"`.
- `:31-34` — `json.dump(cls._store, f, indent=4)` tanpa enkripsi dan **tanpa permission 0600** (Windows/Unix default umask).
- Kunci dipakai provider: `deepseek.py:9-20`, `gemini.py:10-20`.

### Solusi
1. Set permission file 0600 (Unix) / ACL terbatas (Windows).
2. Dukungan env var sebagai prioritas (sudah ada sebagian: `DEEPSEEK_API_KEY`, `GEMINI_API_KEY`); tambahkan `.env` loader (`.env` di `.gitignore`).
3. Opsional: enkripsi dengan keyring OS (Windows Credential Manager / macOS Keychain / libsecret).

### Imbas jika dibiarkan
- File `config.json` bisa terbaca proses lain / backup / sinkronisasi cloud (OneDrive/Dropbox) → **bocornya kunci API pengguna** = tagihan LLM tak terkendali & penyalahgunaan akun.
- Reputasi produk hancur bila ada laporan "API key saya dicuri".

---

## A.3 Legal & Lisensi — 🟠 SEDANG

### Masalah
- `LICENSE` = **MIT**, copyright **"Nexa Team"** — tidak ada badan hukum (perorangan/PT), tanpa kapan/tanggal yang sah untuk klaim komersial.
- Tidak ada **CLA** (Contributor License Agreement) → kontributor bisa mencabut hak lisensi di kemudian hari.
- Tidak ada **EULA / Terms** untuk distribusi komersial (bila produk dibundel ke vendor/enterprise).
- Tidak ada audit lisensi dependensi pihak ketiga (textual, click, openai, groq, dll.) — semuanya permissive (MIT/Apache/BSD), jadi ini lebih ke kelengkapan, bukan pelanggaran.

### Solusi
1. Tentukan **model bisnis** dulu: OSS penuh vs **open-core** (fitur Pro = lisensi komersial). Ini satu-satunya keputusan yang mengunci arah A.1–A.7.
2. Ganti copyright ke entitas legal; tambahkan `NOTICE`/`SECURITY.md`.
3. Siapkan CLA sederhana untuk contributor.

### Imbas jika dibiarkan
- Tanpa entitas & model lisensi: **tidak bisa menjual lisensi enterprise/SaaS** secara sah, dan rawan sengketa kontribusi.
- MIT memungkinkan pesaing **menyalin dan menjual** produk Anda tanpa royalti.

---

## A.4 Kualitas & CI/CD — 🟠 SEDANG

### Masalah
- CI sangat minimal: `.github/workflows/ci.yml:14-27` — hanya `pytest` di **Ubuntu + Python 3.11**. Tanpa lint, type-check, coverage threshold, scan kerentanan (`pip-audit`/`bandit`), tanpa matrix OS (TUI Textual & shell tools sangat OS-dependent; hanya teruji Windows manual).
- Test: **94 pass** tapi tanpa target coverage; titik lemah: pipeline execution engine (0 test dedicated), transformation engine, provider (2 file), TUI (2 file).
- Dependensi **longgar** (`pyproject.toml:14-25`, semua `>=`) tanpa lockfile → build tidak reproducible.
- Tidak ada linter/formatter (ruff/black) terkonfigurasi di CI.

### Solusi
1. CI: matrix `windows-latest` + `ubuntu-latest` + `macos-latest`, Python 3.11–3.13.
2. Tambah: `ruff` (lint), `mypy` (type-check), `coverage` dengan threshold (mis. 60–70%), `pip-audit`/`bandit` (security scan).
3. Lockfile (`pip-tools`/`uv`) untuk reproduktibilitas; pin versi minimum yang benar.

### Imbas jika dibiarkan
- Bug TUI/kode silang-platform muncul saat pengguna (bukan hanya Anda) memakai di Windows/Mac → **churn & ticket support**.
- Tanpa scan keamanan, CVE di dependency tidak terdeteksi → insiden di produksi.
- Build "berhasil di mesin saya" gagal di mesin lain → kepercayaan produk turun.

---

## A.5 Packaging, Versi & Rilis — 🟠 SEDANG

### Masalah
- Versi `1.0.0` statis; tidak ada pipeline **PyPI/ruang rilis/GitHub Release** otomatis, tidak ada tag + changelog-driven version bump, tidak ada signing.
- `nexa update` = `pip install --force-reinstall git+https://github.com/brian2zz/nexa.git` (`nexa/cli.py:39-46`, README:43) — **tanpa pinning/checksum** (supply chain), dan nama repo hardcode (`brian2zz/nexa`) yang saat ini berbeda dengan URL resmi.
- Terdapat 3 direktori `*.egg-info` di root (`nexa.egg-info/`, `nexa_cli.egg-info/`, `nexa_framework.egg-info/`) — walaupun sudah di-`.gitignore`, ini indikasi 3 nama paket berbeda pernah dipakai; `pyproject.toml` kini menamai `nexa-cli`. Konsistensi nama paket penting.
- `MANIFEST.in` sudah cover template (`*.tpl`, `php_skeleton`, `SKILL.md`) tapi **belum pernah diverifikasi wheel utuh** (instal bersih + smoke test).

### Solusi
1. Pipeline rilis: bump versi → build wheel/sdist → upload PyPI + GitHub Release (dengan changelog + tag) → smoke test install bersih.
2. Perbaiki `nexa update` untuk memakai index resmi (bukan git+URL) atau minimal pin `@tag`.
3. Hapus artefak `*.egg-info` lama; uji wheel sekali.

### Imbas jika dibiarkan
- **Supply chain attack**: jika repo GitHub dikompromikan, `nexa update` langsung mengeksekusi kode jahat — kepercayaan pengguna hilang.
- Rilis manual rawan melupakan step → versi rusak beredar.

---

## A.6 Observability & Support — 🟡 RENDAH–SEDANG

### Masalah
- Event bus sudah kaya (`AgentLoopIteration`, `ToolCalled`, `TokenUsage`, `ExecutionFailed`, `Timeline`) — **fondasi observability ada**.
- Belum ada: structured logging server-side, tracing lintas tool, crash reporting opt-in, metrik error per command.
- Tidak ada telemetry → **tidak tahu siapa pengguna, di mana mereka gagal**.

### Solusi
1. Opt-in telemetry (usage, error rate, command populer) + `privacy policy`.
2. Crash report opt-in (snippet + stack trace) untuk prioritas bugfix.
3. Dashboard usage sederhana (tokens, sessions, provider) berbasis event `TokenUsage`.

### Imbas jika dibiarkan
- Keputusan produk dibuat "kebutaan" (tidak tahu fitur mana yang dipakai/gagal) → salah alokasi sumber daya.
- Bug yang jarang terjadi tidak pernah terlaporkan → persepsi "produk rapuh".

---

## A.7 Model Bisnis — 🟠 SEDANG (keputusan pemicu)

### Masalah
Belum ada keputusan: **OSS penuh, open-core (Pro berbayar), atau SaaS hosted**. Semua rekomendasi di A.1–A.6 bergantung pada pilihan ini.

### Solusi
Buat keputusan eksplisit sebelum komersialisasi. Peta kemungkinan:
- **CLI developer tool** (open-core): butuh lisensi ganda, support tier, rilis stabil, dokumentasi.
- **SaaS hosted agent**: butuh sandbox (A.1), multi-tenancy, audit log, SSRF protection, billing, auth, monitoring.

### Imbas jika dibiarkan
- Tanpa keputusan, semua kerja komersialisasi berjalan ke arah yang salah / terbuang.

---

# Bagian B — Kesiapan Fitur (Standar AI Coding Assistant Modern)

## B.1 MCP (Model Context Protocol) — 🔴 KRITIS (Stub)

### Masalah
`/mcps` hanya **membaca `mcp_config.json` dan mencetak daftar server** — tidak menjalankan server, tidak mengekspos tool-nya ke agent:

- `nexa/commands/ai/slash_commands.py:476-495` — baca file + `print`, bahkan mencetak "Status: MCP Plugin Engine Ready (Standard Spec v1.0)" padahal **tidak ada engine-nya**.
- Help metadata `slash_commands.py:54` jujur menandai "(Stub: Roadmap feature)".

### Solusi
1. Implementasi client MCP (stdio transport): spawn `command` dari `mcpServers`, handshake `initialize`, list tools, dan **register tool-nya ke `ToolRegistry`**.
2. Tool MCP diberi metadata `read_only` sesuai capability; approval gate tetap berlaku untuk tool berbahaya.
3. Cache alat & sesi per workspace; handle reconnect.

### Imbas jika dibiarkan
- **MCP adalah ekosistem ekstensi utama opencode/Cursor/Claude Code.** Tanpa MCP nyata, Nexa tidak bisa memakai ribuan server MCP publik (database, browser, Slack, dll.) → **kalah telak dalam adopsi developer** dan daya tarik komersial menurun drastis.

---

## B.2 Skills — 🟠 TINGGI (Display-only)

### Masalah
- `/skills` hanya **menampilkan daftar folder skill** (`slash_commands.py:437-455`); isi `SKILL.md` **tidak pernah di-load ke prompt LLM**.
- Satu-satunya inject skill adalah "caveman mode" (`core/ai/cognitive/engine.py:41-49`).
- `nexa/core/ai/caveman/SKILL.md` ada tapi tidak termanfaatkan secara umum.

### Solusi
1. Bangun **skill loader**: scan `./skills/*/SKILL.md` (project) + global, parse frontmatter (name, description), simpan registry.
2. **Inject otomatis** skill relevan ke `enhanced_sys_prompt` di `shell.py:883-894` (dan ke `AILoopEngine._build_system_prompt`).
3. Sediakan `SKILL.md` format kompatibel opencode/Antigravity agar bisa impor skill publik.

### Imbas jika dibiarkan
- Skill adalah pembeda agent modern; tanpa ini, pengguna tidak bisa menyesuaikan perilaku agent per-proyek → fitur ini "ada di help tapi bohong" = **kepercayaan terkikis** dan daya saing turun.

---

## B.3 Variants (Model) — 🟠 SEDANG (Hardcode)

### Masalah
`/variants` (`slash_commands.py:456-474`) mencetak **list hardcode** yang sudah usang (mis. `deepseek-coder`, `gemini-1.5-pro-latest`) — tidak diambil dari provider nyata dan **tidak ada failover** antar model.

### Solusi
1. Ambil daftar model dari provider yang mendukung (Ollama `/api/tags`, OpenAI-compatible `/v1/models`).
2. Auto-failover: saat 429/timeout, coba provider/model cadangan (sekarang 429 hanya menampilkan pesan di `shell.py:729,862,930`).

### Imbas jika dibiarkan
- Daftar model salah/usang → pengguna memilih model yang tidak ada → error.
- Tanpa failover, jam sibuk provider = agent mati total → kesan tidak reliable.

---

## B.4 Provider — 🟠 SEDANG

### Masalah
- Provider tersedia: ollama, deepseek, groq, gemini, mock. **Tidak ada `openai.py`** padahal `openai>=1.0.0` menjadi dependency (`pyproject.toml:22`). Groq/DeepSeek memakai SDK openai-compatible? — perlu dikonfirmasi; sebaiknya ada provider OpenAI baku.
- Tidak ada provider Azure/Anthropic/Claude.

### Solusi
1. Implementasi `OpenAIProvider` (dan sebaiknya `AnthropicProvider`) pada arsitektur `providers/base.py`.
2. Satu `ProviderFactory` dengan registry + auto-failover (lihat B.3).

### Imbas jika dibiarkan
- Pengguna enterprise banyak memakai OpenAI/Claude — tanpa ini segmen pasar hilang.

---

## B.5 Integrasi Editor / API / Web — 🟠 TINGGI

### Masalah
- Tidak ada integrasi IDE (VS Code/JetBrains extension).
- Tidak ada **headless API server** (`nexa serve`), tidak ada web dashboard untuk session/usage.
- Agent bekerja dari TUI/terminal saja.

### Solusi
1. Fase-1 ringan: `nexa serve` (FastAPI/uvicorn) mengekspos endpoint `POST /chat`, `GET /sessions`, `GET /usage`; reuse `NexaAgentRuntime`.
2. Fase-2: VS Code extension memanggil API; web dashboard read-only.

### Imbas jika dibiarkan
- Mayoritas developer tools modern dijual lewat editor; tanpa ini, Nexa hanya dipakai hardcore CLI → pasar kecil, sulit monetisasi.

---

## B.6 Subagents / Delegasi Paralel — 🟠 SEDANG

### Masalah
`manage_tasks` (`tools/tasks.py`) hanya todo list in-memory. Tidak ada delegasi ke sub-agent dengan konteks terpisah (paralelisme untuk tugas besar).

### Solusi
1. Desain `SubagentEngine`: spawn engine agent dengan konteks/tujuan terpisah, gabung hasil.
2. Tool `delegate_task(goal, context)` + aggregasi hasil ke loop utama.

### Imbas jika dibiarkan
- Tugas besar (refactor multi-file) jadi lambat & konteks penuh → pengalaman buruk vs opencode yang punya subagents.

---

## B.7 Cost Control & Usage Tracking — 🟡 RENDAH–SEDANG

### Masalah
Event `TokenUsage` ada (`agent/loop.py:100-112`), tapi belum ada budget cap per-session dan dashboard usage.

### Solusi
1. `Config` key `agent.max_tokens_per_session` → hentikan/konfirmasi saat tercapai.
2. Rekap usage per session di `/status` (sudah ada perkiraan kasar di `handle_context`, `slash_commands.py:353-371`).

### Imbas jika dibiarkan
- Pengguna membayar token tak terkendali di SaaS → churn karena "mahal".

---

## B.8 Multimodal — 🟡 RENDAH

### Masalah
Hanya teks; tidak ada upload gambar di chat (opencode mendukung).

### Solusi
Gunakan provider yang mendukung vision (Gemini/OpenAI gpt-4o) + tipe message `image_url`.

### Imbas jika dibiarkan
- Pengguna tidak bisa "screenshot bug → minta perbaikan" — fitur yang sangat dihargai.

---

## B.9 Share / Cloud — 🟡 RENDAH

### Masalah
`/share` = **export lokal** (`slash_commands.py:345-347`, eksplisit "Online cloud sharing is not enabled"); `/unshare` hanya info (`:349-351`).

### Solusi
Untuk open-core: cukup. Untuk SaaS: cloud sync + share link + permission.

### Imbas jika dibiarkan
- Tidak ada kolaborasi tim antar mesin → feature parity dengan opencode (yang juga masih terbatas di area ini) tidak kritis, tapi jadi pembeda bila dibangun.

---

# Bagian C — Arsitektur, Flow, Framework Output, Ekosistem

## C.1 Arsitektur — 🟢 Kuat, dengan 2 cacat struktural

### Yang benar (nilai jual)
- Lapisan terpisah sangat bersih: **Phase 1 deterministik** (scanner/tree/static analyzer) → **Phase 2 kognitif** (tri-memory, knowledge graph, planner) → **Phase 3 eksekusi** (context resolver → generator → patch → verify → rollback). Sesuai dokumen `docs/NEXA_MASTER_ARCHITECTURE.md` dan kode.
- Keamanan eksekusi matang: `BeforeApproval` gate, rollback backup/git (`pipeline/rollback/*`), verification (`pipeline/verification.py`), patch dengan search-replace + syntax validation (`pipeline/patch.py:33-97`), path-traversal guard (`tools/filesystem.py:11-16`).
- Event-driven (`PipelineBus`) dengan middleware + `TokenUsage`/`AgentLoopIteration` → fondasi observability.

### Masalah 1: Duplikasi dua engine loop
- `core/agent/loop.py` (`AgentLoop`) dipakai jalur **chat** (`shell.py:916`).
- `core/ai/agent_loop.py` (`AILoopEngine`) dipakai jalur **plan** (`shell.py:806`).
- Logika loop (iterasi, tool call, approval, parsing) **ditulis dua kali** → risiko drift & bug tidak konsisten.

### Solusi 1
Satukan ke satu `LoopEngine` abstrak dengan dua *mode* (PLAN/BUILD) dan satu implementasi tool-invocation + approval; `AILoopEngine` jadi subclass/wrapper yang menambahkan parsing `PlanningResult`.

### Imbas jika dibiarkan
- Perbaikan satu loop tidak otomatis memperbaiki loop lain → bug perilaku berbeda di chat vs plan; biaya maintenance ganda.

### Masalah 2: Artefak build di workspace
- `nexa.egg-info/`, `nexa_cli.egg-info/`, `nexa_framework.egg-info/` di root (sudah di-`.gitignore`, tapi mengotori dev & menandakan 3 identitas paket pernah dipakai).

### Solusi 2
Hapus direktori egg-info; pastikan hanya `nexa-cli` satu-satunya identitas paket (lihat A.5).

### Imbas jika dibiarkan
- Kebingungan identitas paket; artefak bisa ke-commit secara tidak sengaja → repo bengkak.

---

## C.2 Flow — 🟠 Berfungsi, tapi belum closed-loop self-repair

### Alur nyata (terverifikasi `shell.py:708-866`)
`IntentClassifier (LLM)` → `ContextResolver` (`ContextProviderRegistry`) → `ClarificationGate` → `AILoopEngine` (tool loop) → `PlannerReport` → **PLAN mode** (read-only, `:829-835`) atau **`BeforeApproval`** → `ApprovalUI` → `ExecutionTransaction` (`runtime.py:63-107`).

### Masalah
1. **Belum closed-loop untuk eksekusi**: plan → approve → execute berjalan linier; **hasil eksekusi (gagal test/verifikasi) tidak otomatis diumpankan balik ke LLM untuk self-repair**. Agent tidak "baca error → perbaiki → ulang" secara otomatis.
2. Di jalur chat (`AgentLoop`), mode BUILD kini punya tool write/bash (Fase 6), tapi tidak ada gerbang approval otomatis per-tool di jalur itu — bergantung mode saja.

### Solusi
1. Tambah **repair loop**: setelah `ExecutionTransaction`, baca `verification` result; jika gagal → inject hasil (stderr/exit code) ke loop → LLM memperbaiki plan/patch → ulang (dengan batas iterasi).
2. Di chat BUILD: approval gate per tool write (reuse pola `ai/agent_loop.py:150-253`) agar BUILD tidak serta-merta tanpa konfirmasi.

### Imbas jika dibiarkan
- Agent tidak bisa menyelesaikan tugas multi-langkah yang butuh iterasi perbaikan → pengguna harus bolak-balik manual → kesan "kurang cerdas" vs kompetitor.

---

## C.3 Framework yang Dihasilkan — 🟢 Kuat, 3 cacat

### Yang benar
- 44 template `.tpl` (api/app/crud/project/scaffold/shared) dengan DSL custom (`[loop:fields]`, `{{ model_name.lower() }}`), schema-driven (`nexa.yaml`), multi-tenant aware, self-healing, atomic rollback. **Ini diferensiasi utama Nexa.**

### Masalah 1: Placeholder bisnis-logic di hasil generate
`core/pipeline/project_pipeline.py:119,124` menulis middleware dengan **komentar kosong**:
```python
class TenantMiddleware: ... # Logic to extract tenant from URL
class ActivityLogMiddleware: ... # Logic to log user activity
```
Artinya hasil "SaaS/ERP" punya **stub**, bukan implementasi berfungsi.

### Solusi 1
- Untuk tiap placeholder: tulis implementasi nyata (tenant dari subdomain/header, activity log ke tabel `activity_log`) ATAU pindah ke fitur eksplisit "generate stub" dengan README peringatan.

### Imbas jika dibiarkan
- Pelanggan generate "ERP/SaaS" tapi fitur inti (tenant/audit) tidak jalan → **retur/demo gagal, kredibilitas hilang**.

### Masalah 2: Bahasa campuran di frontend hasil generate
Template berisi teks Indonesia (mis. `Formulir Pembuatan`, `Zona enkapsulasi pengisian atribut database secara aman` di `templates/crud/form.tpl`).

### Solusi 2
Gunakan bahasa Inggris sebagai default + i18n (konfigurasi `locale` di `nexa.yaml`).

### Imbas jika dibiarkan
- Output terlihat "amateur/regional" untuk pasar global → sulit dijual internasional.

### Masalah 3: php_skeleton minimal
Hanya 20 file di-commit (`nexa/templates/php_skeleton`), sebagian besar struktur skeleton, belum sepadan dengan kualitas Django/Flutter.

### Solusi 3
Lengkapi skeleton PHP (auth, routing, migration runner) atau turunkan klaim fitur PHP di README.

### Imbas jika dibiarkan
- Janji README "NexaPHP" > kenyataan → overpromise, kekecewaan.

---

## C.4 Ekosistem — 🔴 Titik Terlemah (ringkas, detail di Bagian B)
| Komponen | Kondisi | Imbas |
| :--- | :--- | :--- |
| MCP | Stub (`slash_commands.py:476-495`) | Kehilangan ekosistem server MCP publik |
| Skills | Display-only (`:437-455`) | Tidak bisa kustomisasi perilaku per-proyek |
| Variants | Hardcode (`:456-474`) | Daftar usang, tanpa failover |
| Provider | Tanpa OpenAI/Anthropic | Pasar enterprise hilang |
| Subagents | Tidak ada | Tugas besar lambat |
| Template i18n | Campur bahasa | Output tidak global-ready |

---

# Bagian D — Prioritas yang Disarankan (BELUM dieksekusi)

Urutan berdampak maksimal dengan effort minimal:

| # | Item | Effort | Imbas jika dikerjakan | Imbas jika diabaikan |
| :---: | :--- | :--- | :--- | :--- |
| 1 | **Real-injeksi skills + MCP client nyata** (B.1, B.2) | Sedang | Paritas ekosistem opencode; adopsi melonjak | Kalah saing ekosistem |
| 2 | **Closed-loop self-repair** (C.2) | Besar | Agent benar-benar otonom multi-langkah | Persepsi "kurang cerdas" |
| 3 | **Hilangkan placeholder generator + i18n** (C.3) | Sedang | Output enterprise-grade | Demo gagal, kredibilitas turun |
| 4 | **Hapus duplikasi dua loop** (C.1) | Sedang | Maintenance lebih murah, konsisten | Bug drift dua jalur |
| 5 | **Keamanan eksekusi granular + SSRF** (A.1) | Sedang | Membuka opsi SaaS | RCE/SSRF di lingkungan terkelola |
| 6 | **CI quality gates + coverage** (A.4) | Kecil | Kualitas terjamin tiap PR | Bug cross-OS muncul |
| 7 | **Pipeline rilis + update aman** (A.5) | Kecil | Distribusi profesional | Risiko supply chain |
| 8 | **`nexa serve` (API headless)** (B.5) | Sedang | Dasar SaaS & integrasi editor | Pasar CLI saja |

**Catatan penting:** item #1 dan #2 adalah "pembeda besar"; item #5 dan #7 adalah "pengaman" sebelum komersial. Item #6 adalah "disiplin" paling murah yang mencegah semua regresi.

---

## Lampiran — Peta Referensi Kode

| Area | Lokasi |
| :--- | :--- |
| Bash tool (RCE) | `nexa/core/agent/tools/terminal.py:20-24` |
| Pola `shell=True` lain | `commands/ai/slash_commands.py:143,335`; `commands/django/{build,install,run}.py`; `core/pipeline/execution/runner.py:10`; `ui/app.py:224,295` |
| Approval auto-execute | `core/ai/agent_loop.py:150-265` |
| Penyimpanan kunci | `nexa/config/__init__.py:7,31-34`; `providers/{deepseek,gemini}.py` |
| CI | `.github/workflows/ci.yml:14-27` |
| Deps longgar | `pyproject.toml:14-25` |
| Update (supply chain) | `nexa/cli.py:39-46`; `README.md:43` |
| MCP stub | `commands/ai/slash_commands.py:476-495` |
| Skills display-only | `commands/ai/slash_commands.py:437-455`; `core/ai/cognitive/engine.py:41-49` |
| Variants hardcode | `commands/ai/slash_commands.py:456-474` |
| Share lokal | `commands/ai/slash_commands.py:345-351` |
| Compact manual | `commands/ai/slash_commands.py:373` |
| 429 tanpa failover | `commands/ai/shell.py:729,862,930` |
| Duplikasi loop | `core/agent/loop.py` vs `core/ai/agent_loop.py`; pemakaian `shell.py:806,916` |
| Placeholder middleware | `core/pipeline/project_pipeline.py:119,124` |
| Template bahasa campur | `nexa/templates/crud/form.tpl` |
| php_skeleton minimal | `nexa/templates/php_skeleton` (20 file) |
| Tool registry (21 tool) | `core/agent/runtime.py:48-58`; `tools/{execution_tools,web}.py` |
| Approval → ExecutionTransaction | `core/agent/runtime.py:63-107` |

---

*Dokumen ini murni catatan audit & rekomendasi. Tidak ada perubahan kode yang dieksekusi akibat dokumen ini.*
