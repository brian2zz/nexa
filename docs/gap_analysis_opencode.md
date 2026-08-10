# Gap Analysis: Nexa AI Agent vs opencode

**Tanggal**: 09 Agustus 2026
**Tujuan**: Evaluasi kesenjangan fitur antara agent AI Nexa (`nexa ai`) dan opencode sebagai alat pembanding *state-of-the-art* untuk terminal-based software engineering agent.
**Status**: Dokumentasi evaluasi — belum ada implementasi.

---

## 1. Ringkasan

Nexa memiliki **fondasi yang kuat** dan tumpang tindih secara konseptual dengan opencode di beberapa area inti (TUI, multi-provider LLM, gate persetujuan, manajemen sesi, dan pipeline eksekusi ber-trasaksi). Namun, ada **dua gap kritis** yang membedakan keduanya:

1. **Nexa tidak memiliki loop agent iteratif** — pipeline-nya linear (`intent → plan → approval → execute → selesai`), sedangkan opencode beroperasi sebagai loop otonom yang memanggil tool, membaca hasil, lalu memutuskan langkah berikutnya.
2. **Tool agent Nexa read-only** — jembatan menuju penulisan file (`submit_execution_plan`) masih berupa *stub*, sehingga agent tidak dapat benar-benar menyelesaikan tugas modifikasi file secara mandiri.

Kesimpulan: **Nexa belum seperti opencode**, tetapi gap tersebut dapat ditutup bertahap (lihat §5).

---

## 2. Matriks Fitur

| Fitur | Status | Lokasi | Keterangan |
| :--- | :---: | :--- | :--- |
| **TUI interaktif** (Textual) | ✅ | `nexa/ui/app.py` | Transcript, prompt-input, status panel, command palette. |
| **Multi-provider LLM** | ✅ | `nexa/core/ai/providers/` | Ollama, DeepSeek, Groq, Gemini, Mock + factory. |
| **Approval gate** sebelum eksekusi | ✅ | `nexa/core/approval/engine.py`, `nexa/ui/screens/approval.py` | Event `BeforeApproval` → modal → `ApprovalGranted/Rejected`. |
| **Clarification gate** untuk goal ambigu | ✅ | `nexa/core/ai/cognitive/engines/clarification.py`, `nexa/ui/screens/clarification.py` | Modal TUI + fallback terminal. |
| **Session management & recovery** | ✅ | `nexa/core/ai/memory/core.py`, `nexa/core/agent/session.py` | Chat history SQLite, `/session`, `SessionRecoveryManager`. |
| **Execution pipeline ber-trasaksi** | ✅ | `nexa/core/pipeline/transaction.py` | Transform → patch → backup → verifikasi → commit/rollback atomic. |
| **Memory** (facts, pins, rolling window) | ✅ | `nexa/core/ai/memory/` | Facts, pinned memory, chat context. |
| **Observability / usage tracking** | ✅ | `nexa/core/observability/` | Token usage per sesi, audit, metrics. |
| **Loop agent iteratif** (LLM→tool→hasil→lanjut) | ❌ | `nexa/commands/ai/shell.py:600-724` | Pipeline linear; sekali jalan, tidak beradaptasi terhadap hasil tool. |
| **Write / Edit tools** untuk LLM | ❌ | `nexa/core/agent/tools/pipeline.py:15` | `submit_execution_plan` masih *stub* (belum publish `ExecutionPlanSubmitted`). |
| **Bash tool** yang dipanggil LLM | ⚠️ | `nexa/core/pipeline/execution/runner.py` | `TerminalRunner` ada tapi hanya internal transaksi, bukan tool agent. |
| **Glob / file-find tool** | ⚠️ | `nexa/core/agent/tools/knowledge/file.py:24` | `FileTool.find` ada; belum diintegrasikan sebagai tool loop agent. |
| **Grep / text-search tool** | ⚠️ | `nexa/core/agent/tools/knowledge/search.py:12` | `SearchTool.text` ada; belum dipakai loop agent. |
| **Web fetch / web search** | ❌ | — | Tidak ada tool untuk mengambil informasi dari web. |
| **Subagents / Task tool** | ❌ | — | Tidak ada delegasi tugas ke agent paralel. |
| **Todo list tool** | ⚠️ | `nexa/ui/widgets/status_panel.py` | Status panel *menampilkan* todos dari plan, tapi LLM tidak bisa membuat/update todo. |
| **Skills / Plugins / MCP** | ❌ | — | Tidak ada sistem ekstensi (workflow/instruksi khusus). |
| **Permission rules granular** (allow/ask/deny per tool) | ⚠️ | `nexa/core/approval/` | Hanya 1 gate approval level-plan; belum per-tool/perintah. |
| **Plan mode** (read-only + proposal) | ❌ | — | Tidak ada mode eksplorasi tanpa eksekusi. |
| **AGENTS.md** (baca instruksi proyek) | ❌ | — | Belum ada pembacaan file instruksi per proyek. |
| **LSP / semantic index real-time** | ⚠️ | `nexa/core/agent/indexer.py` | `WorkspaceIndexer` (AST) ada; belum terhubung ke loop agent. |

Legend: ✅ ada & berfungsi · ⚠️ ada parsial / belum terintegrasi · ❌ tidak ada.

---

## 3. Arsitektur Pipeline Saat Ini

```
User Input
   │
   ▼
Intent Classifier (PLAN / CHAT)
   │
   ▼
Clarification Gate ──→ (jika ambigu: tanya user)
   │
   ▼
Planner (AIPlannerEngine) ──→ report + plan
   │
   ├── tidak ada work items → jawab/investigasi saja (Search & Answer)
   │
   └── ada work items → BeforeApproval event
             │
             ▼
      Approval Modal (TUI) ──→ ApprovalGranted
             │
             ▼
   handle_approval_granted → ExecutionTransaction
             │
             ▼
      transform → patch → backup → execute → verify → commit/rollback
```

Karakteristik: **satu arah, tanpa umpan balik.** LLM hanya merencanakan; eksekusi dilakukan oleh mesin deterministik di luar loop LLM. Hasil eksekusi tidak dikembalikan ke LLM untuk iterasi berikutnya.

---

## 4. Gap Kritis

### 4.1 Gap #1 — Tidak Ada Loop Agent Iteratif
opencode berjalan sebagai *agent loop*: LLM menghasilkan panggilan tool → tool dieksekusi → hasil disuntikkan kembali ke konteks → LLM memutuskan langkah berikutnya → berulang hingga tugas selesai.

Nexa saat ini: satu siklus `plan → approval → execute` lalu kembali ke prompt. Konsekuensi:
- Tidak bisa melakukan investigasi bertahap (baca file → cari symbol → coba → perbaiki).
- Tidak bisa memperbaiki sendiri jika eksekusi gagal secara iteratif (hanya ada *satu* jalur auto-recovery via `PlannerContext` di `runtime.py:81-125`).

### 4.2 Gap #2 — Tool Agent Read-Only (Jembatan Eksekusi Stub)
- Semua tool yang terdaftar di `NexaAgentRuntime.tools` bersifat **read-only** (file find/read, search, git).
- Satu-satunya tool "write" adalah `submit_execution_plan` di `pipeline.py`, yang hanya memvalidasi JSON dan mengembalikan `"SUCCESS"` — **tidak** mem-publish `ExecutionPlanSubmitted` dan **tidak** memicu eksekusi apa pun (baris 15-16 masih komentar).

### 4.3 Gap #3 — Belum Ada Ekosistem Ekstensi
Skills, plugins, MCP servers, permission rules granular, subagents, dan pembacaan AGENTS.md semuanya belum ada. Ini adalah diferensiator utama opencode untuk penggunaan produktif lintas proyek.

---

## 5. Peta Jalan Rekomendasi (Konsep — Belum Diimplementasikan)

Urutan disusun dari dampak tertinggi / ketergantungan terendah:

1. **Agent Loop Iteratif** (menutup Gap #1)
   - Perkenalkan loop `while` yang mengizinkan LLM memanggil tool berulang kali.
   - Alirkan hasil tool kembali ke konteks LLM.
   - Posisikan `BeforeApproval` sebagai *salah satu* tool/gerbang di dalam loop, bukan akhir pipeline.

2. **Write/Edit + Bash Tools Nyata** (menutup Gap #2)
   - Aktifkan `submit_execution_plan` → publish `ExecutionPlanSubmitted` → `ExecutionTransaction`.
   - Ekspos `TerminalRunner` sebagai tool `bash` dengan sandbox & timeout.
   - Tambahkan tool `glob`, `grep`, `read`, `write`, `edit` yang dipanggil dari loop agent.

3. **Todo Tool** — izinkan LLM membuat/memperbarui todo; status panel mengikuti.

4. **Permission Rules Granular** — pola allow/ask/deny per tool/perintah, bukan hanya 1 gate plan-level.

5. **AGENTS.md & Plan Mode** — baca instruksi proyek; sediakan mode eksplorasi read-only.

6. **Skills / Plugins / MCP** — sistem ekstensi untuk workflow khusus dan server eksternal.

7. **Subagents / Task tool** — delegasi paralel untuk tugas besar.

8. **Web fetch / search** — tool pengambilan informasi eksternal.

---

## 6. Referensi File Kunci

| File | Peran |
| :--- | :--- |
| `nexa/commands/ai/shell.py` | Handler perintah interaktif, intent classifier, clarification gate, trigger approval. |
| `nexa/core/agent/runtime.py` | `NexaAgentRuntime`: tool registry, subscriber approval/recovery/revision, session. |
| `nexa/core/agent/tools/pipeline.py` | `submit_execution_plan` (stub) — jembatan LLM → pipeline. |
| `nexa/core/agent/tools/knowledge/file.py` | `FileTool` (read-only: find/read/symbol/tree/metadata). |
| `nexa/core/agent/tools/knowledge/search.py` | `SearchTool` (text/symbol search). |
| `nexa/core/agent/tools/knowledge/git.py` | `GitTool` (status/diff/log/execute whitelist). |
| `nexa/core/approval/engine.py` | `ApprovalEngine` — gatekeeper event-driven. |
| `nexa/core/pipeline/transaction.py` | `ExecutionTransaction` — orkestrasi eksekusi atomic. |
| `nexa/core/pipeline/execution/runner.py` | `TerminalRunner` — eksekusi subprocess aman. |
| `nexa/ui/app.py` | `NexaApp` — TUI Textual, event bus → UI. |
| `nexa/ui/screens/approval.py`, `clarification.py` | Modal approval & klarifikasi. |
