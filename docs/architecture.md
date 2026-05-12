# Nexa Framework Enterprise Architecture: The Full-Stack SaaS Engine

## 1. Core Philosophy: Schema-Driven Orchestration
Nexa beroperasi dengan prinsip **Single Source of Truth**. Seluruh infrastruktur aplikasi tingkat *Enterprise* (Backend & Frontend) didefinisikan secara komprehensif melalui satu file deklaratif: `nexa.yaml`.

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
- **Frontend**: Vue 3 (Composition API), Pinia, Vite.
- **Orchestration**: Nexa Engine (Python).
