# Nexa Framework Enterprise SaaS & ERP Engine 🚀

**Nexa** adalah framework *full-stack* mutakhir yang didesain untuk menyintesis seluruh arsitektur aplikasi berskala *Enterprise* (SaaS & ERP) dari satu sumber kebenaran (*Single Source of Truth*) menggunakan **Django REST Framework** (Backend) dan **Vue.js 3 / Composition API** (Frontend).

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
nexa new nexa-enterprise
cd nexa-enterprise
```

### 2. Membangun Seluruh Ekosistem via Skema (*Schema-Driven*)
Siapkan berkas deklaratif Anda (misal: `nexa.yaml`), lalu jalankan sintesis mandiri:
```bash
nexa generate nexa.yaml
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

| Perintah | Fungsi / Peran |
| :--- | :--- |
| `nexa new [name]` | Menciptakan direktori proyek ekosistem Nexa baru. |
| `nexa generate [file.yaml]` | Mensintesis cetak biru *Backend* & *Frontend* secara menyeluruh. |
| `nexa run` | Mengorkestrasi server Django dan Vite dev server serentak. |
| `nexa startapp [name]` | Menyiapkan struktur fondasi modul bisnis baru. |
| `nexa make:api [app] [model]` | Mensintesis *Serializer*, *ViewSet*, dan *Frontend Service*. |
| `nexa build` | Membangun bundel produksi aset statis terpadu. |
| `nexa install` | Mengeksekusi penyiapan modul Node.js di tingkat *root*. |

---

## 🤝 Kontribusi & Dukungan

Nexa didesain untuk terus berkembang bersama komunitas pengembang *Enterprise*. Silakan *fork* repositori ini dan ajukan *Pull Request* inovatif Anda!

---
**Nexa Framework** — *Architected with absolute precision and premium aesthetics.* 💎
