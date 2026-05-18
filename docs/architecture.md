# Nexa Framework Enterprise Architecture: The Full-Stack SaaS Engine

## 1. Core Philosophy: Schema-Driven Orchestration
Nexa beroperasi dengan prinsip **Single Source of Truth**. Seluruh infrastruktur aplikasi tingkat *Enterprise*—mencakup **Backend (Django REST)**, **Web Frontend (Vue 3 SPA)**, dan **Mobile Frontend (Flutter Clean Architecture)**—didefinisikan dan disinkronkan secara komprehensif melalui skema deklaratif berkas `nexa.yaml` maupun utilitas CLI modular Nexa.

---

## 2. Peningkatan Arsitektur Generasi Klien (Staged Workspace)
Sistem antarmuka CRUD mandiri kita tidak lagi sekadar formulir kaku, melainkan ruang kerja basis data interaktif (*Real-Time Dynamic Spreadsheet*) yang mengadopsi arsitektur klien premium:
- **Offline Client-Side Staging**: Penambahan, pengeditan, dan penghapusan data ditampung secara lokal di memori peramban dengan pemetaan warna visual (Hijau, Kuning, Merah).
- **Hibrida Kunci Primer**: Kolom identitas mendukung masukan manual opsional yang secara otomatis mendelegasikan sekuens *Auto-Increment* bawaan ORM jika dikosongkan.
- **Isolasi Aksi Navigasi**: Navigasi menggunakan impor dinamis malas (*lazy loading*) dan rute bernama (*named routing*) untuk mencegah *deadlock* memori pada Single Page Application.

---

## 3. Execution Flow (The Lifecycle)
Alur orkestrasi Nexa dibagi menjadi 6 tahap kritis yang tangguh (*resilient*):

1. **Pre-Flight Snapshot**: Menyimpan status ruang kerja file/direktori saat ini untuk kapabilitas *Atomic Rollback*.
2. **Loader (YAML to Objects)**: Mengonversi YAML mentah menjadi `ProjectSchema` yang memiliki tipe data kuat.
3. **Validator (Integrity Check)**: Memastikan tidak ada relasi yang rusak. Jika tidak valid, akan memicu otomatis *Rollback* mengembalikan ruang kerja bersih.
4. **Pipeline Orchestrator**: Mesin utama yang membagi tugas dan memiliki fungsi **Self-Healing** (otomatis melakukan inisialisasi Django project jika direktori `config` hilang):
   - **Project Level**: Membangun fondasi global (Shared UI, Config).
   - **App Level**: Menyiapkan scaffolding aplikasi (Vite Entry points).
   - **Model Level**: Menjalankan generator spesifik untuk setiap entitas data dengan jembatan keamanan otomatis (CSRF & DRF results unboxing).
5. **Registry System (Discovery)**: Nexa secara otomatis menemukan generator menggunakan decorator `@nexa_generator`.
6. **Generators (Code Synthesis)**: Menggunakan engine `.tpl` untuk mensintesis kode Django dan Vue 3. Jika gagal/exception, semua folder baru di-revert bersih.

---

## 4. Generated Directory Architecture (SaaS Aligned)
Struktur folder yang dihasilkan Nexa dirancang untuk skalabilitas SaaS:

```text
/
├── config/                  # Django Settings & Global URLS
├── shared/
│   └── ui/                  # Shared UI Library (Alias: @ui)
├── apps/
│   ├── home/                # Core SaaS Gateway SPA & Control Center
│   └── [app_name]/          # Independent Business Module
│       ├── models/          # Django Models
│       ├── serializers/     # DRF Serializers
│       ├── views/           # Controllers
│       ├── services/        # Backend Client Logic (Axios Configured)
│       ├── middleware/      # App-specific middleware
│       ├── templates/       # Django-Vue Bridge Templates
│       └── frontend/        # Vue 3 Frontend Root
└── nexa.yaml                # The Master Schema
```

---

## 5. Multi-Tenant Ready (Hybrid Routing)
Arsitektur Nexa mendukung **Dynamic Tenancy** secara out-of-the-box:
- **Automatic Context**: Middleware di aplikasi `home` mendeteksi tenant dari URL tanpa perlu mengubah logika di aplikasi bisnis.
- **Absolute Path Protection**: Rute dasar layanan disinkronkan ke hierarki awalan API Django untuk menghindari bentrokan sapu jagat rute antarmuka klien.

---

## 6. Technology Stack
- **Backend**: Python, Django, Django REST Framework (DRF) dengan *AllowAny* kalibrasi *scaffolding*.
- **Web Frontend**: Vue 3 (Composition API), Pinia, Vite.
- **Mobile Frontend**: Dart, Flutter SDK, Riverpod State Management, GoRouter, Dio.
- **Orchestration**: Nexa Engine (Python).

---

## 7. Mobile Architecture: Clean Architecture & DDD

Aplikasi seluler yang dihasilkan oleh mesin **Nexa Flutter Engine** menggunakan struktur arsitektur bersih (*Clean Architecture*) terstandarisasi yang sangat modular berbasis Domain-Driven Design (DDD). Setiap modul bisnis di bawah `lib/modules/` dipisahkan menjadi beberapa lapisan pelindung terisolasi:

```text
lib/modules/[module_name]/
├── presentation/
│   ├── routes.dart          # Rute GoRouter modular yang terinjeksi otomatis ke router pusat
│   └── [module]_page.dart   # UI menggunakan Riverpod ConsumerWidget untuk responsivitas state
├── application/
│   └── [module]_provider.dart # State Management menggunakan Riverpod StateNotifier & State class
└── data/
    ├── models/
    │   └── [module]_model.dart # Dart Model dengan null-safety & konversi JSON cerdas
    └── repository/
        └── [module]_repository.dart # Komunikasi data terisolasi menggunakan HttpService (Dio-based)
```

### 🛠️ Integrasi Alur Sinkronisasi & Metaprogramming Rute
* **Dynamic Route Injection**: Ketika modul seluler baru dibuat via CLI, generator Nexa akan membedah berkas `lib/core/router/app_router.dart`, mendeteksi jangkar komentar `// [NEXA_ROUTE_IMPORTS]` serta `// [NEXA_ROUTES_ARRAY]`, lalu **menginjeksi rute modul baru secara dinamis** tanpa campur tangan manual.
* **Auto-Fallback Engine**: Semua perintah CLI native Flutter yang dijalankan melalui `nexa flutter` (seperti `run`, `build`, `clean`) akan secara otomatis dialirkan langsung ke native Flutter SDK dengan fungsionalitas monitoring konsol interaktif.

