# Nexa AI Framework & Enterprise Scaffolding Engine 🚀

<div align="center">

**Nexa** adalah *Autonomous AI Coding Assistant* dan *Full-Stack Enterprise Framework Engine* mutakhir. Dirancang dengan standar **Google Antigravity & OpenCode**, Nexa menyintesis arsitektur perangkat lunak berskala *Enterprise* mulai dari perancangan cetak biru (*Architectural Blueprint*), *Scaffolding MVC*, migrasi basis data, hingga eksekusi aman dengan *AST Patching* dan *Auto-Rollback*.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Framework Parity](https://img.shields.io/badge/Parity-Antigravity%20%7C%20OpenCode-cyan.svg)](#)

</div>

---

## 🌟 Fitur & Keunggulan Utama Nexa Terbaru

### 🧠 1. Perancangan Arsitektur Otonom (*Antigravity Blueprint Format*)
- **Domain Entity Modeling**: Cukup beri instruksi alami (misal: *"Tolong buatkan project catatan keuangan menggunakan nexa php"*), Nexa AI akan menganalisis kebutuhan bisnis dan merancang entitas relasi pangkalan data yang optimal (`Transaction`, `Income`, `Expense`, `Category`, `Account`, `Budget`).
- **Tabel Skema Terstruktur**: Memaparkan tabel relasi field data, tipe data, serta *foreign keys* sebelum dieksekusi.
- **Skema Deklaratif Standar**: Otomatis menghasilkan dan memvalidasi konfigurasi `nexa.yaml` siap pakai.

---

### ⚡ 2. Generator Mandiri & Workspace Bersih (*Clean Workspace & Auto-Cleanup*)
- **Auto-Bootstrap Sub-Project**: Menjalankan generator dari folder induk mana saja (misal `G:\project code`) akan **otomatis membuat folder proyek mandiri** lengkap:
  - `apps/` *(Modular Domain Apps, Models, Controllers, Routes)*
  - `public/index.php` *(Entrypoint Web Application)*
  - `database/` *(SQLite / MySQL Migrations)*
  - `.env` & `bin/nexa`
- **Zero-Garbage Auto-Cleanup**: File skema `nexa.yaml` sementara yang ada di folder induk **langsung otomatis dihapus setelah proyek selesai digenerate**, sehingga ruang kerja Anda tetap 100% bersih tanpa sampah file konfigurasi.
- **Tanpa Duplikasi**: Di dalam subfolder proyek yang baru dibuat tidak ditaruh file YAML duplikat karena seluruh arsitektur telah berubah menjadi kode PHP murni.

---

### 🔬 3. Protokol Kueri & Analisis Data (*Scratch Script & Self-Cleanup*)
- **Scratch Query Scripting**: Untuk kebutuhan analisis data kompleks, inspeksi database, atau pencarian pattern kode mendalam, Nexa menulis skrip kalkulasi sementara (misal `query_temp.py`).
- **Eksekusi Mandiri & Auto-Delete**: Nexa menjalankan skrip di background terminal, mengambil output data aktual, dan **seketika menghapus skrip sementara tersebut** menggunakan `delete_file`.
- **Laporan Komprehensif**: Hasil analisis disajikan dalam format tabel Markdown yang rapi dan informatif kepada pengguna.

---

### 📋 4. Laporan Walkthrough Lengkap (*Antigravity Walkthrough Report*)
Setiap kali transaksi perubahan kode selesai diterapkan (*Committed*), Nexa langsung menampilkan ringkasan **Walkthrough**:
- 🎯 **Sasaran / Goal**: Tujuan pengerjaan proyek.
- 📁 **Daftar File & Direktori**: Rincian file yang dibuat (`CREATE`), dimodifikasi (`MODIFY`), atau dihapus (`DELETE`) lengkap beserta deskripsi perannya.
- ⚡ **Perintah Terminal yang Dijalankan**: Daftar instruksi generator yang telah dieksekusi.
- 💡 **Panduan Menjalankan**: Blok perintah cepat (misal `cd catatan_keuangan && nexa php run`) dan URL browser lokal.

---

### 🛡️ 5. Mesin Transaksi Aman & Pemulihan Mandiri (*Self-Healing Auto-Recovery*)
- **Event-Driven Architecture (EDA)**: Menggunakan bus *Publish-Subscribe* terpusat untuk komunikasi real-time antar subsistem.
- **Atomic Rollback Strategy**: Jika terjadi kendala saat eksekusi perintah terminal atau penerapan patch, sistem otomatis membatalkan perubahan dan mengembalikan workspace ke kondisi semula yang stabil.
- **Self-Healing Auto-Recovery**: AI secara mandiri mendeteksi kegagalan, menganalisis penyebab error, memperbaiki rencana eksekusi, dan meminta persetujuan baru dari pengguna.

---

### 🖥️ 6. Antarmuka TUI Interaktif Modern (*Terminal User Interface*)
- **Live Status & Token Tracker**: Memantau penggunaan token (Prompt, Completion, Total) serta estimasi biaya ($ USD) secara real-time.
- **Process Activity Monitor**: Menampilkan tahapan eksekusi aktif (*Agent Loop, Patch, Verifying, Success*).
- **Interactive Modals**: Dialog Approval dengan format Markdown dan *bash blocks*, popup klarifikasi multi-opsi, dan modal input API Key yang dapat dibatalkan dengan tombol **`ESC`**.
- **Mode Switching (Tab)**: Beralih instan antara mode **PLAN** (analisis/read-only) dan **BUILD** (eksekusi/menulis kode).
- **Papan Klip Aman**: Dilengkapi *debounce cooldown* untuk mencegah duplikasi paste.

---

## 📥 Cara Instalasi

Pasang Nexa CLI ke environment Python Anda:

```bash
git clone https://github.com/brian2zz/nexa.git
cd nexa
pip install -e .
```

Verifikasi instalasi dengan menjalankan:
```bash
nexa help
```

Untuk masuk ke antarmuka AI interaktif, cukup ketik:
```bash
nexa
```
*(atau `nexa ai shell`)*

---

## 🚀 Panduan Penggunaan Cepat

### 1. Masuk ke Nexa AI Shell
```bash
nexa
```

### 2. Hubungkan AI Provider & Masukkan API Key
Tekan **`Ctrl + K`** lalu pilih **`/connect`** (atau ketik `/connect`), lalu pilih provider AI Anda (misalnya DeepSeek, Gemini, Groq, atau Ollama lokal).

### 3. Buat Proyek Baru
Ketik permintaan Anda secara alami di dalam chat:
```text
Tolong buatkan project catatan keuangan menggunakan nexa php
```
Nexa akan:
1. Menyelidiki workspace Anda.
2. Memaparkan **Cetak Biru Arsitektur & Skema Database**.
3. Meminta persetujuan eksekusi (*Approval Dialog*).
4. Men-generate seluruh file model, controller, routes, dan migrasi database ke dalam folder `catatan_keuangan/`.
5. Membersihkan file YAML sementara secara otomatis.
6. Menampilkan **Laporan Walkthrough Hasil Eksekusi**.

### 4. Jalankan Aplikasi
```bash
cd catatan_keuangan
nexa php run
```
Buka peramban di `http://127.0.0.1:8000`.

---

## 📖 Direktori Lengkap Perintah Nexa CLI

### 🐘 Nexa PHP Framework (`nexa php <command>`)
| Perintah | Deskripsi / Peran |
| :--- | :--- |
| `nexa php new <name> [--frontend=vue\|react]` | Inisialisasi struktur proyek NexaPHP lengkap |
| `nexa php generate [nexa.yaml]` | Scaffold MVC Models, Controllers, Views, dan migrasi dari skema |
| `nexa php make:module <name> [--enterprise]` | Membuat modul domain baru di `apps/<name>/` |
| `nexa php make:model <Name> <App>` | Membuat entitas Doctrine ORM Model baru |
| `nexa php make:migration <name>` | Memindai entitas dan membuat berkas migrasi database |
| `php bin/nexa migrate` | Menerapkan migrasi ke database aktif (SQLite / MySQL) |
| `nexa php run` | Menjalankan server lokal di `http://127.0.0.1:8000` |

---

### 📱 Nexa Flutter Mobile (`nexa flutter <command>`)
| Perintah | Deskripsi / Peran |
| :--- | :--- |
| `nexa flutter new <name>` | Inisialisasi proyek Flutter Clean Architecture & Riverpod |
| `nexa flutter create-module <name>` | Scaffold modul fitur baru dengan auto-routing GoRouter |
| `nexa flutter gen-model <json_file>` | Konversi JSON menjadi Dart Data Model null-safe |
| `nexa flutter run` | Menjalankan aplikasi mobile secara interaktif dengan live hot-reload |
| `nexa flutter doctor` | Mendiagnosis kesehatan SDK Flutter dan dependensi proyek |

---

### 🗄️ Nexa Django REST Framework (`nexa django <command>`)
| Perintah | Deskripsi / Peran |
| :--- | :--- |
| `nexa django new <name>` | Inisialisasi proyek modular Django Enterprise baru |
| `nexa django startapp <name>` | Menyiapkan modul domain aplikasi baru |
| `nexa django make:api <app> <model>` | Mensintesis Serializer, ViewSet, dan rute REST API |
| `nexa django run` | Menjalankan server Django dan Vite frontend secara serentak |
| `nexa django doctor` | Memeriksa kesehatan environment Django & Node.js |

---

### 🤖 Nexa AI Interactive Slash Commands
Gunakan perintah ini di dalam sesi interaktif `nexa`:

| Kategori | Perintah | Deskripsi |
| :--- | :--- | :--- |
| **General** | `/help` | Menampilkan ringkasan direktori bantuan dan keyboard shortcuts |
| | `/commands` | Menampilkan seluruh sub-perintah CLI yang terdaftar |
| | `/editor` | Membuka Notepad / VS Code untuk menulis prompt panjang |
| | `/exit` *(alias: `/quit`, `/q`)* | Keluar dari sesi interaktif Nexa |
| **Project** | `/plan <goal>` | Membuat rencana arsitektur terstruktur untuk suatu tujuan |
| | `/todos` | Mengelola checklist tugas proyek (`list`, `add`, `done`, `remove`) |
| | `/context` | Menampilkan statistik penggunaan token dan konteks sesi |
| **Config** | `/connect` | Wizard pemilihan provider AI dan pengaturan API Key |
| | `/select-provider` | Mengganti AI Provider aktif (`deepseek`, `gemini`, `groq`, `ollama`) |
| | `/models` / `/set-model` | Memilih model AI yang aktif |
| | `/set-api-key` | Memasukkan atau memperbarui API Key |
| | `/mode` | Beralih antara mode **PLAN** dan **BUILD** |
| | `/themes` | Mengganti tema warna antarmuka TUI |
| **Session** | `/new` *(alias: `/clear`)* | Memulai sesi percakapan baru yang bersih |
| | `/sessions` / `/load` | Melihat daftar atau memuat kembali riwayat percakapan lama |
| | `/rename <name>` | Mengubah nama sesi percakapan aktif |
| | `/copy` | Menyalin jawaban AI terakhir ke clipboard sistem |
| | `/export` | Mengekspor riwayat percakapan ke berkas Markdown |
| **Rollback** | `/undo` | Membatalkan pesan terakhir dan me-restore file dari backup |
| | `/redo` | Menerapkan kembali state yang telah di-undo |

---

### ⌨️ Keyboard Shortcuts
- **`Ctrl + K`** : Membuka *Command Palette* pencarian cepat.
- **`Tab`** : Toggle Mode (**PLAN** ⇄ **BUILD**).
- **`Ctrl + V` / Klik Kanan** : Menempel teks dari clipboard.
- **`Ctrl + Y`** : Menyalin respons AI terakhir.
- **`ESC`** : Menutup modal popup aktif atau membatalkan dialog.

---

## 🤝 Kontribusi & Lisensi

Nexa dirancang dengan arsitektur terbuka dan modular. Kontribusi berupa *Bug Reports*, *Feature Requests*, dan *Pull Requests* sangat dipersilakan!

Lisensi: [MIT License](LICENSE)

---
<div align="center">
<b>Nexa Framework</b> — <i>Autonomous Intelligence, Clean Architecture, and Precision Scaffolding.</i> 💎
</div>
