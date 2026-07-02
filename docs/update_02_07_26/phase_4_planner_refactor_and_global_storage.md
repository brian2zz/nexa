# Update 02 Juli 2026: Arsitektur Planner & Global Storage

## 1. Migrasi Data `.nexa` ke Global AppData
Sebelumnya, Nexa AI membuat dan menyimpan semua _state_ internal (seperti log, backup, memori chat, database execution audit, dan indeks workspace) di dalam direktori `.nexa/` pada setiap *root* proyek. Hal ini menyebabkan `.nexa` tidak sengaja ter-track oleh Git dan mengotori ruang kerja (workspace) proyek.

**Solusi yang Diterapkan:**
- Seluruh *state* Nexa sekarang disimpan secara terpusat di `~/.nexa/projects/<hash_direktori_proyek>/`.
- Mekanisme *hashing* MD5 dari path absolut proyek (`path.py`) digunakan untuk memastikan tidak ada tabrakan (collision) antar proyek.
- File log, *backups*, `workspace.db`, `execution_audit.db`, `agent.db`, dan semua analisis *history* kini diam-diam ditulis di luar *repository* git pengguna.

## 2. Refactor Arsitektur Planner (Software Architect)
Berdasarkan filosofi *Pipeline Sovereignty*, peran *Planner* sebelumnya (yang langsung menghasilkan *patch code* atau ratusan baris kode melalui perintah `content="..."`) dianggap melanggar batas antara fase *Planning* dan *Transformation*. 

**Perubahan Arsitektur:**
1. **Pemisahan Peran:** LLM (Planner) kini hanya bertindak sebagai *Software Architect*. Planner bertugas menganalisis masalah, merumuskan solusi teknis, menilai risiko, dan memecah pekerjaan ke dalam *Work Items*.
2. **Schema `PlanningResult` Baru:**
   - *Planner* tidak lagi mengembalikan `ExecutionPlan` dengan kumpulan `intents` teknis.
   - Output JSON dirombak menjadi `PlanningResult` yang berisi:
     - `objective`: Tujuan utama pengerjaan
     - `constraints`: Batasan teknis yang harus dipatuhi
     - `work_items`: Daftar tugas spesifik beserta file yang terdampak
     - `acceptance_criteria`: Kondisi yang harus terpenuhi agar fitur dianggap sukses
     - `risk_analysis`: Analisis risiko komprehensif (Kategori, Probability, Impact, Mitigation)
     - `confidence`: Penilaian diri (skor 0-100) mengenai tingkat keyakinan AI terhadap rencana tersebut.
3. **Penyajian UI Terminal:** Formatter diperbarui untuk menyajikan `PlanningResult` dalam format poin (bullet) dan list bersarang sehingga *Risk Analysis* dan *Acceptance Criteria* sangat mudah dibaca.
4. **Kelahiran `PipelineBuilder`:** Komponen baru yang menjembatani *Planner* dengan *Execution Engine*. `PipelineBuilder` menerima `PlanningResult` murni dari LLM dan meraciknya menjadi `ExecutionPlan` (*Pipeline Model*) yang dapat dibaca oleh *Transaction/Execution Engine*.

Dengan arsitektur ini, desain dan logika AI benar-benar terisolasi dari mekanisme teknis penerapan *patch/code* (*Transformation Engine*), yang membuat Nexa menjadi asisten cerdas yang sangat berdisiplin secara perangkat lunak.

## 3. Bugfix: Pemetaan Terminal Commands pada Pipeline
Pada implementasi awal `PipelineBuilder`, perintah CLI/Terminal yang dihasilkan Planner (di dalam `affected_components.commands`) diabaikan. Hal ini mengakibatkan aksi seperti `git restore` atau instalasi dependensi (npm/pip) yang disarankan Planner gagal diteruskan ke transaksi eksekutor.
**Solusi:** Menambahkan tahap evaluasi khusus ("Commands") ke dalam `PipelineBuilder`, yang secara otomatis memetakan `commands` menjadi obyek `IntentNode(action="COMMAND")`.

## 4. Bugfix Kritis: Perbaikan Mesin Transformasi (Transformation Engine)
Terdapat sebuah arsitektur lawas yang sangat naif di dalam `TransformationEngine`: Engine tersebut memaksa LLM menghasilkan modifikasi *code* secara buta tanpa membaca isi file aslinya. Akibatnya, LLM hanya mengembalikan sepotong kode parsial, dan *PatchApplier* langsung menimpa (_overwrite_) seluruh file dengan kode parsial tersebut yang berujung pada hilangnya data pengguna.
**Solusi:** 
- `TransformationEngine` sekarang membaca **keseluruhan teks asli dari file** sebelum mengirimkannya ke LLM.
- Menanamkan instruksi mutlak (*system prompt*) yang mewajibkan LLM untuk menuliskan kode secara utuh dan komplit (FULL FILE REWRITE). Mesin tidak lagi diizinkan menggunakan gaya ringkasan atau *diff*.

## 5. Penambahan Sistem Pelacakan: Generic Git Tool
Untuk meningkatkan keandalan investigasi (sebelum merancang eksekusi), Nexa AI kini dibekali fungsi pendelegasian perintah `git_execute`. 
- **Sebelumnya:** Nexa AI hanya mengetahui `git status` dan `git diff` yang dibatasi pada *working tree*.
- **Sekarang:** Melalui fungsi *tool function calling*, AI mampu mengeksekusi instruksi dinamis seperti `git log`, `git show`, `git branch`, hingga `git blame` secara mandiri. Ini memberikan kesadaran versi (*version awareness*) yang luar biasa saat AI menelusuri sumber kesalahan atau dependensi antar komponen (*Software Archeology*).
