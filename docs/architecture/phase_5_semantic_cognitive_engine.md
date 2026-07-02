# Phase 5: Cognitive Layer Blueprint (Semantic Intelligence)

Dokumen ini memuat cetak biru (*blueprint*) lompatan arsitektur terbesar untuk Nexa AI. Alih-alih hanya beroperasi sebagai generator teks atau sekadar "AI Coding Assistant", Phase 5 akan mengubah Nexa menjadi **Cognitive Software Engineering Platform**. Arsitektur ini tidak dirancang untuk membuat *prompt* yang lebih panjang, melainkan membuat sistem di sekitar LLM menjadi lebih cerdas, independen dari model tertentu, dan jauh lebih hemat token (Cognitive Budgeting).

---

## 🚀 The Ultimate Cognitive Pipeline
Alur eksekusi Nexa akan berevolusi dari sekadar `Knowledge ➔ Planner ➔ Transformation` menjadi arsitektur kognitif yang menyerupai cara berpikir *Software Engineer* Senior manusia.

**Alur Baru:**
`User Intent` ➔ `Hypothesis Engine` ➔ `Knowledge Acquisition` ➔ `Reasoning Layer` ➔ `Planning Layer` ➔ `Transformation Layer` ➔ `Authority Layer`

### 1. Hypothesis Engine (Killer Feature)
Manusia tidak pernah langsung menelusuri seluruh *codebase* secara buta. Manusia membuat hipotesis terlebih dahulu.
- **Konsep:** Sebelum mencari data, mesin merumuskan kemungkinan (*Hipotesis A: Backend tidak mengirim total*, *Hipotesis B: Frontend salah parsing*).
- **Eksekusi:** *Knowledge Acquisition* kemudian beroperasi HANYA untuk mencari bukti-bukti (mengumpulkan data) yang relevan guna membuktikan atau membantah hipotesis-hipotesis tersebut, menghemat *token budget* secara drastis.

### 2. Reasoning Layer & Evidence Layer
- **Reasoning Layer:** Memisahkan secara tegas antara menyimpulkan masalah (Reasoning) dan menyusun langkah perbaikan (Planning). Mesin harus tahu persis **"Kenapa ini rusak?"** sebelum merancang **"Bagaimana cara memperbaikinya?"**.
- **Evidence Layer:** Setiap *Root Cause* yang ditemukan di *Reasoning Layer* **wajib** memiliki jejak bukti (*Evidence Trail*). 
  - *Contoh:* Bukti: `supplierView.py (line 82)` ➔ `requestAjax()` ➔ `return response.data`.

---

## 🧠 Semantic Indexing & Knowledge Graph
Mengirimkan teks mentah (file ribuan baris) ke LLM sangat mahal dan tidak efisien (*Context Explosion*). 

### 1. Dari File menuju Semantic Object (AST)
Database SQLite Nexa tidak lagi menyimpan nama file, melainkan dirombak total menjadi **Knowledge Graph**:
`AST` ➔ `Symbol Graph` ➔ `Dependency Graph` ➔ `Call Graph` ➔ `Knowledge Graph (Business Concepts)`
- **Call Graph:** Nexa mengetahui relasi bahwa `SupplierView` memanggil `requestAjax` yang kemudian memanggil `fetch`.
- **Business Concepts:** Nexa memahami bahwa `Supplier`, `Purchase`, `Stock`, dan `Warehouse` saling berhubungan dalam domain bisnis, meskipun berada di file yang benar-benar berbeda.

### 2. Object-Oriented Tooling
Saat LLM memanggil *tool* pembaca kode, ia tidak mendapat kembalian rentetan teks, melainkan objek JSON kaya metadata:
```json
{
  "type": "function",
  "name": "update_supplier",
  "file": "supplierView.py",
  "lines": [82, 146],
  "summary": "...",
  "dependencies": ["requestAjax", "Supplier"]
}
```
LLM bernalar menggunakan objek semantik ini terlebih dahulu, dan baru membaca kode sumber jika sangat diperlukan.

### 3. Semantic Cache & Cognitive Budget
- **Semantic Cache:** Jika Planner menanyakan "Apa fungsi requestAjax?", SQLite akan langsung memberikan jawaban dari *cache* hasil *reasoning* sebelumnya, tanpa perlu parsing ulang.
- **Cognitive Budget:** Menggantikan konsep "Token Budget". Planner hanya diizinkan menarik sejumlah objek kognitif secara bertahap (misal: max 10 Knowledge Objects per siklus), memaksa *reasoning* yang lebih terarah dan irit.

---

## ⚙️ Transformation & Memory Layer

### 1. AST Patch Engine & Unified Diff
Modifikasi kode secara membabi buta (*Full File Rewrite*) akan ditinggalkan karena memakan Output Token yang sangat mahal dan lambat.
- LLM hanya mengembalikan instruksi **Unified Diff** (`@@ -123,7 +123,9 @@`).
- Nexa memiliki **AST Patch Engine** yang akan memvalidasi *diff* secara sintaksis dan merajut kembali file tersebut secara persis, memastikan kode tidak patah.

### 2. Capability-Based Dynamic Tools
Pengiriman seluruh kamus fungsi/tools ke LLM secara penuh sangat boros.
- *Tool Set* disediakan secara dinamis berdasarkan **Capability** dari intensi saat itu. Jika Intent adalah "Buat commit", maka AI hanya dibekali *Capability Git*, membuang ratusan baris *System Prompt* yang tidak perlu.

### 3. Hierarchical Memory
Menggantikan sistem memori linier dengan memori otak berjenjang:
1. **Conversation:** Obrolan pengguna real-time.
2. **Working Memory:** Detail fungsi dan hipotesis jangka pendek yang dikosongkan setelah *task* beres.
3. **Session Memory:** Rekam jejak *problem-solving* sepanjang sesi aktif.
4. **Long Term Memory:** Aturan arsitektur *project* dan gaya pengkodean (*style*) yang ditarik sebagai fondasi permanen.

---
*Roadmap Evolusi Nexa AI:*
`Phase 1: Foundation ➔ Phase 2: Thinking ➔ Phase 3: Authority ➔ Phase 4: Agent ➔ Phase 5: Cognitive Layer ➔ Phase 6: Autonomous Software Engineer`
