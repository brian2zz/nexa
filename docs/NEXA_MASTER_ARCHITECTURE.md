# 🧠 NEXA AI - Master Architecture Document

Dokumen ini adalah "Peta Navigasi" utama untuk memahami anatomi keseluruhan dari **Nexa Framework**. Di sini dijelaskan bagaimana lapisan murni tanpa-AI (Phase 1) menyatu dengan kecerdasan kognitif (Phase 2), penyaring konteks, hingga lengan robotik eksekusi (Phase 3).

## 📊 Anatomi Fase (The Phases)

### 🧱 Phase 1: Foundation Engine (Deterministik, Non-AI)
Lapisan akar yang paling cepat dan kaku. Bertugas mendeteksi struktur proyek, memindai ratusan file dalam hitungan milidetik, menganalisis bahasa, dan menyimpannya ke dalam SQLite lokal (`nexa_project.db`). 
*Komponen utama: CLI Dispatcher, Project Detector, File Scanner, Tree Engine, Static Analyzer.*

### 🤖 Phase 2: Cognitive Engine (Sistem Pemikir AI)
Otak cerdas yang menghubungkan proyek lokal Anda dengan LLM raksasa (seperti Groq, DeepSeek). 
*Komponen utama: Tri-Memory System (Chat, Facts, Pins), Knowledge Engine (Dependency Graph), Analyzer, dan AI Planner (Blueprint Generator).*

### 🛠️ Phase 3: Autonomous Scaffolding Layer (Sistem Pengeksekusi)
"Tangan" Nexa yang mampu menulis ribuan baris kode ke *harddisk* tanpa merusaknya. 
✔ 3.0 Scaffolding Engine (CLI Generative Modules)
✔ 3.1 Context Resolver Engine (Deterministic Token Management)
✔ 3.2 AI Transformation Engine (Pure AI Transformation & Retry Policy)
- 3.3 Patch Engine (Smart File Writer)
- 3.4 Verification Engine (Auto-Test)

---

## ⚙️ Aliran Eksekusi (Lifecycle of a Request)

Bagaimana tepatnya sebuah perintah sederhana dari pengguna diproses dari awal hingga berubah menjadi kode fisik? Berikut adalah siklus hidup (*Life Cycle*) dari perintah sakti **`nexa create`** atau **`/plan`**:

```mermaid
graph TD
    A([User Input / Prompt]) --> B{Smart Intent Router}
    
    %% Intent Branching
    B -- "CHAT" --> C[Prompt Engine]
    B -- "PLAN" --> D[AI Planner Engine]
    
    %% Planning Phase
    D --> E[Tri-Memory System]
    E -.-> |Project Facts| D
    E -.-> |Pinned Rules| D
    E -.-> |Chat History| D
    
    D --> F[LLM Provider]
    F --> G[JSON Blueprint]
    G --> H{Execution Plan Validator}
    
    H -- "Gagal" --> D
    H -- "Valid" --> I[Markdown Blueprint & Recommendations]
    
    %% Execution Phase
    I --> J{User Approval (Y/n)}
    J -- "No" --> A
    J -- "Yes" --> K[Context Resolver Engine]
    
    %% Context Resolving
    K --> L[Knowledge Engine / Dependency Graph]
    L --> M[Snippet Extractors]
    M --> N[Context Optimizer]
    N --> O((ContextBundle))
    
    %% Generation
    O --> P[AI Generator]
    P --> Q[LLM Provider]
    Q --> R[Raw Code Block]
    
    %% Physical Write
    R --> S[AI Executor / Builder]
    S --> T[(Local File System / Harddisk)]
```

## 🧩 Penjelasan Jembatan Krusial (The Bridges)

### 1. Jembatan Phase 2 (Planner) ke Phase 3 (Executor)
Planner tidak menulis kode. Ia murni menghasilkan **Execution Plan JSON** kaku yang berisi: `files_to_create`, `files_to_modify`, `execution_steps`. 
JSON ini kemudian di-*passing* secara murni (*by value*) ke dalam **AI Executor**. Ini berarti *Executor* tidak perlu tahu LLM mana yang dipakai; ia hanya perlu membaca objek JSON untuk membuat folder (menggunakan perintah bawaan OS) dan menembak *Generator* untuk mengisi *source code*-nya.

### 2. Peran Context Resolver (Phase 3.1)
Sebelum `AIGenerator` menulis fungsi yang diminta oleh Planner, ia harus tahu "kode apa saja yang sudah ada di sekitar sana". 
Daripada mengirim seluruh isi proyek ke LLM (yang bisa menghabiskan 120.000 token), **Context Resolver Engine** memotong kode menjadi ukuran gigitan (*bite-sized snippets*). 
1. Ia menggunakan *Language Strategy* (`php.py`, `python.py`).
2. Ia menerapkan *Fallback Pipeline* (Regex -> Window -> Full File).
3. Hasilnya adalah `ContextBundle` super padat yang disuntikkan ke dalam *Prompt Engine* si *Generator*.

### 3. Mengapa Arsitektur Ini Tahan Banting?
Karena Nexa mengadopsi prinsip **Single Responsibility Principle (SRP)** yang ekstrem di level makro:
- `Scanner` murni membaca folder.
- `Context Resolver` murni memotong teks.
- `Planner` murni membuat rencana JSON.
- `Generator` murni memuntahkan blok kode markdown.
- `Executor` murni menyimpan file ke *disk*.

Jika esok hari kita menyambungkan Nexa ke **Telegram Agent** atau **VSCode Extension** (Phase 4), kita tidak perlu menyentuh otak AI-nya sama sekali; kita hanya perlu mengganti lapisan *Interface*-nya!
