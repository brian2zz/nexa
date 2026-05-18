# Nexa Framework Enterprise SaaS & ERP Engine 🚀

**Nexa** adalah framework *full-stack & cross-platform* mutakhir yang didesain untuk menyintesis seluruh arsitektur aplikasi berskala *Enterprise* (SaaS & ERP) dari satu sumber kebenaran (*Single Source of Truth*) menggunakan **Django REST Framework** (Backend), **Vue.js 3 / Composition API** (Web Frontend), serta **Flutter Clean Architecture & Riverpod** (Mobile Frontend).

---

## ✨ Inovasi & Fitur Unggulan Versi Terbaru

### 📊 1. Ruang Kerja Database Klien Real-Time (*Inline Staged Spreadsheet*)
- **Pemisahan Aksi Mouse Eksklusif**: Klik tunggal (*single click*) murni dioptimalkan untuk seleksi salin (*copy/block text*) tanpa interupsi, sementara klik ganda (*double click*) seketika menyulap sel tabel menjadi kotak masukan (*inline input box*).
- **Client-Side Staged Batch Commits**: Menampung modifikasi pengguna di sisi peramban terlebih dahulu layaknya perangkat lunak *DBeaver* atau *DataGrip*.
  - 🟢 **Baris Hijau (*Staged Add*)**: Baris penambahan baru muncul bercahaya di puncak tabel. Mendukung input *Primary Key* ID opsional dengan *fallback Auto-Increment* pangkalan data otomatis saat dikosongkan.
  - 🟡 **Baris Kuning (*Staged Edit*)**: Menyorot baris yang nilainya dimodifikasi dengan kapabilitas **"↩ Reset"** instan.
  - 🔴 **Baris Merah (*Staged Delete*)**: Menandai rekaman untuk dicoret/dihapus dengan kebebasan **"↩ Restore"** sebelum *commit* permanen.
- **Master Global Commit Toolbar**: Panel kendali bersinar dengan indikator denyut (*pulse animation*) yang merangkum kuantitas baris operasi tertunda untuk dieksekusi secara serentak ke server.

### 🔍 2. DBeaver-Style & Fuzzy Cross-Column Filtering
- Antarmuka pencarian ganda canggih yang mendukung ekspresi kueri kondisional berbasis SQL (misal: `id = 53 and status = 'sukses'`) maupun pencarian teks buram (*fuzzy search*) serbaguna.

### 🛡️ 3. Keamanan & Sinkronisasi Arsitektur Tingkat Tinggi
- **DRF Pagination Bridge**: Pinia *store* dibekali logika *unboxing* cerdas ganda yang otomatis mengurai *array* murni maupun respons berformat `{ results: [...] }` bawaan Django REST Framework.
- **CSRF Token Security Handshake**: Klien Axios dikonfigurasi secara absolut untuk menyelaraskan *cookie* `csrftoken` dengan *header* HTTP `X-CSRFToken` pada seluruh rute `POST, PUT, DELETE`.
- **Absolute Path Alignment**: Seluruh rute layanan klien otomatis terhubung ke *prefix* hierarki pendaftaran URL pangkalan data `/api/v1/[app_name]/[route_name]/` guna menghilangkan pencegatan rute halaman SPA.
- **SPA Deadlock Prevention**: Rute antarmuka *scaffolded* dikonversi sepenuhnya menjadi impor dinamis malas (*lazy dynamic imports*) dan rute bernama (*named routes*) untuk navigasi super mulus tanpa *reload*.

### 📱 4. Orkestrasi Mobile Seluler Terpadu (Nexa Flutter Engine)
- **Clean Architecture & DDD Scaffolding**: Menghasilkan boilerplate proyek seluler modular yang kokoh dengan pemisahan lapisan yang disiplin: `presentation`, `application` (Riverpod State Management), `data/models`, dan `data/repository`.
- **Nexa Interactive Keyboard Runner**: Konsol eksekusi interaktif `nexa flutter run` yang menangani interaksi satu-karakter secara real-time:
  - 🟢 **`c`**: Otomatis mematikan aplikasi, menjalankan `flutter clean` + `flutter pub get`, dan menyalakannya kembali secara dinamis.
  - 🟢 **`s`**: Memicu Hot Restart yang membersihkan dan memuat ulang seluruh state manajemen **Riverpod ProviderScope** instan.
  - 🟢 **`p`**: Mengaktifkan atau menonaktifkan *Performance Overlay* pada layar pengujian.
  - 🟢 **`e`**: Memuat ulang konfigurasi berkas `.env` dan memicu restart cepat.
- **Console Network Monitor (No DevTools)**: Logs HTTP dinamis dari Axios/Dio Interceptor (`GET /api/user -> 200 (120ms)`) dicetak penuh warna secara real-time langsung di terminal tanpa repot membuka Chrome DevTools.
- **JSON-to-Dart AI Schema Generation (`gen-model`)**: Cukup arahkan ke file JSON, Nexa akan mensintesis Dart Model null-safe lengkap dengan serialisasi `fromJson/toJson` serta proteksi *float-double casting* otomatis.

---

## 📥 Cara Instalasi

Anda dapat memasang Nexa langsung melalui repositori GitHub menggunakan manajer paket `pip`:

```bash
pip install git+https://github.com/brian2zz/nexa.git
```

Verifikasi instalasi dengan menjalankan:

```bash
nexa --help
```

---

## 🚀 Panduan Cepat (*Quick Start*)

### 1. Inisialisasi Ruang Kerja Proyek
```bash
nexa django new nexa-enterprise
cd nexa-enterprise
```

### 2. Membangun Seluruh Ekosistem via Skema (*Schema-Driven*)
Siapkan berkas deklaratif Anda (misal: `nexa.yaml`), lalu jalankan sintesis mandiri:
```bash
nexa django generate nexa.yaml
```
> **Catatan**: Mesin Nexa dilengkapi fitur **Self-Healing** (otomatis membuat struktur dasar Django jika hilang) serta **Atomic Auto-Rollback** (mengembalikan kondisi direktori bersih semula jika terjadi anomali sintesis).

### 3. Pemasangan Dependensi & Migrasi Basis Data
```bash
nexa install
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
```

### 4. Menjalankan Server Pengembangan Terpadu
```bash
nexa run
```
Akses dasbor administrator pusat bergaya *glassmorphism* premium di alamat `http://127.0.0.1:8000`.

---

## 📖 Referensi Cepat Perintah CLI

Nexa CLI memisahkan ekosistem perintah secara rapi di bawah kendali `django` dan `flutter`:

### 🗄️ Grup Perintah Django REST & Vue.js 3 (`nexa django <command>`)

| Perintah | Fungsi / Peran |
| :--- | :--- |
| `nexa django new [name]` | Menciptakan direktori proyek ekosistem Nexa baru. |
| `nexa django generate [file.yaml]` | Mensintesis cetak biru *Backend* & *Frontend* secara menyeluruh. |
| `nexa django run` | Mengorkestrasi server Django dan Vite dev server serentak. |
| `nexa django startapp [name]` | Menyiapkan struktur fondasi modul bisnis baru. |
| `nexa django make:api [app] [model]` | Mensintesis *Serializer*, *ViewSet*, dan *Frontend Service*. |
| `nexa django build` | Membangun bundel produksi aset statis terpadu. |
| `nexa django install` | Mengeksekusi penyiapan modul Node.js di tingkat *root*. |
| `nexa django doctor` | Mendiagnosis kesehatan environment backend Django & Node.js. |

### 📱 Grup Perintah Flutter & Mobile (`nexa flutter <command>`)

| Perintah | Fungsi / Peran |
| :--- | :--- |
| `nexa flutter new [name]` | Menginisialisasi proyek Flutter Clean Architecture & Riverpod baru. |
| `nexa flutter create-module [name]` | Mensintesis modul fitur baru dengan auto-routing GoRouter. |
| `nexa flutter gen-model [json_file]` | Mengubah berkas JSON menjadi Dart Class Model null-safe secara instan. |
| `nexa flutter doctor` | Mendiagnosis kesehatan environment SDK Flutter, Dart, & proyek. |
| `nexa flutter run [args]` | Menjalankan aplikasi secara interaktif dengan shortkey `c`, `s`, `p`, `e` & Network Logs. |
| `nexa flutter build [args]` | Membangun rilis produksi (APK, AppBundle, dll.) dengan dukungan penuh variasi flag. |
| `nexa flutter [any_subcommand]` | *Auto-Fallback* cerdas, meneruskan perintah apa saja langsung ke native Flutter CLI. |

---

## 🤝 Kontribusi & Dukungan

Nexa didesain untuk terus berkembang bersama komunitas pengembang *Enterprise*. Silakan *fork* repositori ini dan ajukan *Pull Request* inovatif Anda!

---
**Nexa Framework** — *Architected with absolute precision and premium aesthetics.* 💎
