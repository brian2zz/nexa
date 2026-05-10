# Nexa Framework 🚀

**Nexa** adalah framework full-stack modern yang dirancang untuk mempercepat pengembangan aplikasi SaaS dan ERP menggunakan **Django** (Backend) dan **Vue.js 3** (Frontend).

Nexa menggabungkan kekuatan Django dalam manajemen data dan keamanan dengan fleksibilitas Vue.js dan kecepatan Vite untuk pengalaman pengembangan yang luar biasa.

## ✨ Fitur Utama

-   🏗️ **Project Scaffolding**: Membuat struktur proyek lengkap (Django + Vue + Vite) dalam hitungan detik.
-   🔄 **Integrated Dev Server**: Jalankan server Django dan Vite secara bersamaan dengan satu perintah.
-   📦 **Automated App Generation**: Membuat modul aplikasi baru yang sudah terkonfigurasi dengan router, store, dan API service.
-   🛠️ **Smart API Scaffolding**: Generate Serializer, Viewsets, dan Frontend Service secara otomatis dari satu perintah.
-   🚀 **Unified Build System**: Build aplikasi untuk produksi dengan optimasi aset otomatis.
-   🎨 **Modern Tech Stack**: Mendukung Vue 3, Pinia, Vite, Tailwind CSS, dan Bootstrap.

## 📥 Cara Install

Kamu bisa meng-install Nexa langsung dari GitHub menggunakan `pip`:

```bash
pip install git+https://github.com/USERNAME_KAMU/nexa.git
```

Setelah ter-install, kamu bisa memverifikasi instalasi dengan mengetik:

```bash
nexa
```

## 🚀 Panduan Cepat (Quick Start)

### 1. Membuat Proyek Baru
```bash
nexa new nama_proyek
cd nama_proyek
```

### 2. Meng-install Dependensi
```bash
nexa install
pip install -r requirements.txt
```

### 3. Menjalankan Environment Pengembangan
```bash
nexa run
```
Akses aplikasi kamu di `http://127.0.0.1:8000`.

### 4. Membuat Aplikasi/Modul Baru
```bash
nexa startapp nama_modul
```

### 5. Membuat API Secara Otomatis
```bash
nexa make:api nama_modul NamaModel
```

## 📖 Dokumentasi Perintah

| Perintah | Deskripsi |
| :--- | :--- |
| `nexa new [name]` | Membuat proyek Nexa baru. |
| `nexa run` | Menjalankan Django server dan Vite dev server. |
| `nexa startapp [name]` | Membuat modul aplikasi baru dengan struktur Vue. |
| `nexa make:api [app] [model]` | Generate Serializer, Viewset, dan Frontend Service. |
| `nexa build` | Membangun aset frontend dan mengumpulkan static files. |
| `nexa install` | Menjalankan `npm install` di root proyek. |

## 🛠️ Persyaratan Sistem

-   Python 3.8+
-   Node.js 16+ & npm
-   Django 4.0+

## 🤝 Kontribusi

Kontribusi selalu terbuka! Silakan fork repository ini dan kirimkan Pull Request.

---
Dibuat dengan ❤️ untuk pengembang Indonesia.
