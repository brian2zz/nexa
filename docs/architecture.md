# Nexa Framework V3 Architecture: The Full-Stack SaaS Engine

## 1. Core Philosophy: Schema-Driven Orchestration
Nexa beroperasi dengan prinsip **Single Source of Truth**. Seluruh infrastruktur aplikasi (Backend & Frontend) didefinisikan melalui satu file deklaratif: `nexa.yaml`.

---

## 2. Execution Flow (The Lifecycle)
Alur orkestrasi Nexa dibagi menjadi 5 tahap kritis:

1. **Loader (YAML to Objects)**: Mengonversi YAML mentah menjadi `ProjectSchema` yang memiliki tipe data kuat.
2. **Validator (Integrity Check)**: Memastikan tidak ada relasi yang rusak (missing foreign keys).
3. **Pipeline Orchestrator**: Mesin utama yang membagi tugas menjadi 3 level:
   - **Project Level**: Membangun fondasi global (Shared UI, Config).
   - **App Level**: Menyiapkan scaffolding aplikasi (Vite Entry points).
   - **Model Level**: Menjalankan generator spesifik untuk setiap entitas data.
4. **Registry System (Discovery)**: Nexa secara otomatis menemukan generator menggunakan decorator `@nexa_generator`.
5. **Generators (Code Synthesis)**: Menggunakan engine `.tpl` untuk mensintesis kode Django dan Vue 3.

---

## 3. Generated Directory Architecture (SaaS Aligned)
Struktur folder yang dihasilkan Nexa dirancang untuk skalabilitas SaaS:

```text
/
├── config/                  # Django Settings & Global URLS
├── shared/
│   └── ui/                  # Shared UI Library (Alias: @ui)
├── apps/
│   ├── home/                # Core SaaS Module (Middleware & Control Center)
│   └── [app_name]/          # Independent Business Module
│       ├── models/          # Django Models
│       ├── serializers/     # DRF Serializers
│       ├── views/           # Controllers
│       ├── services/        # Backend Logic (Service Layer)
│       ├── middleware/      # App-specific middleware
│       ├── templates/       # Django-Vue Bridge Templates
│       └── frontend/        # Vue 3 Frontend Root
└── nexa.yaml                # The Master Schema
```

---

## 4. Multi-Tenant Ready (Hybrid Routing)
Arsitektur Nexa mendukung **Dynamic Tenancy** secara out-of-the-box:
- **Automatic Context**: Middleware di aplikasi `home` mendeteksi tenant dari URL tanpa perlu mengubah logika di aplikasi bisnis.
- **Unified Codebase**: Kode yang sama menangani `/inventory/` (Internal) dan `/customer-1/inventory/` (SaaS).

---

## 5. Technology Stack
- **Backend**: Python, Django, Django Rest Framework (DRF).
- **Frontend**: Vue 3 (Composition API), Pinia, Vite.
- **Orchestration**: Nexa Engine (Python).
