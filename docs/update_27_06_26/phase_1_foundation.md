# Phase 1 — Foundation Engine (Selesai)

**Tujuan:** Membangun fondasi Nexa yang murni deterministik, berjalan sangat cepat tanpa campur tangan AI (LLM). Fase ini berfokus pada pengenalan lingkungan (*Environment*), pemindaian (*Scanning*), dan penyimpanan data lokal (*Local Storage*).

## 1.1 CLI Framework
Kerangka antarmuka pengguna berbasis terminal (Command Line Interface).
- `nexa` (Perintah dasar)
- **Command Registry**: Pendaftaran perintah secara dinamis.
- **CLI Dispatcher**: Pengarah perintah ke modul yang tepat.
- **Plugin Command**: Arsitektur yang mendukung modul tambahan.

## 1.2 Project Detection
Mesin pendeteksi identitas proyek secara otomatis (Detektor Cerdas).
- **Detector**: Menganalisis *root folder*.
- **Framework Detection**: Mampu mengenali lebih dari 10 arsitektur (Django, Flutter, NexaPHP, Laravel, CodeIgniter, React, Vue, Angular, Node, Generic PHP, Generic Python).

## 1.3 Scanner Engine
- **File Scanner**: Mengumpulkan daftar file di seluruh proyek.
- **Ignore Rules**: Menghormati `.gitignore` dan aturan pengecualian (seperti folder `vendor`, `node_modules`).
- **Framework Adapter**: Menyesuaikan cara *scanning* berdasarkan kerangka kerja (contoh: mengutamakan `lib/` di Flutter).
- **Priority File Scanner**: Mendeteksi file-file vital (seperti `composer.json`, `package.json`, `manage.py`).

## 1.4 Memory Layer
Lapisan penyimpanan lokal murni tanpa bergantung pada *cloud*.
- **SQLite**: Database relasional lokal (`nexa_project.db`).
- **Project Storage**: Menyimpan meta-data proyek.
- **File Storage**: Mengindeks daftar file dan metadata file.
- **Analysis Cache**: Menyimpan hasil *scan* agar eksekusi berikutnya berkecepatan kilat.

## 1.5 Tree Engine
`nexa tree`
- **Pretty Tree**: Mencetak hierarki struktur direktori yang indah dan mudah dibaca di terminal.
- **Framework-aware Tree**: Struktur *tree* yang diurutkan berdasarkan pentingnya file pada suatu kerangka kerja.
- **Important Files**: Menyoroti file-file kritis dengan warna yang berbeda.

## 1.6 Static Analyzer
Sistem analisis statis murni, mendiagnosis proyek tanpa mengirimkan satu *byte* pun ke LLM.
- **Statistics**: Menghitung jumlah file, rasio bahasa pemrograman.
- **Architecture Detection**: Mendeteksi pola arsitektur (MVC, Clean Architecture).
- **Warnings**: Memberi peringatan keamanan dasar atau kejanggalan struktur.
- **Health Score**: Memberi nilai kesehatan struktur proyek secara keseluruhan.

---

### Output Keseluruhan Phase 1
Aliran eksekusi murni deterministik:
**`nexa scan`** ➡️ **`Project Detected`** ➡️ **`SQLite`** ➡️ **`Tree`** ➡️ **`Static Analysis`**
