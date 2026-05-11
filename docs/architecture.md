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
│   └── [app_name]/          # Independent Business Module
│       ├── models/          # Django Models
│       ├── serializers/     # DRF Serializers
│       ├── views/           # Controllers
│       ├── services/        # Backend Logic (Service Layer)
│       └── frontend/        # Vue 3 Frontend Root
│           ├── index.html   # Multi-entry Vite Point
│           └── src/
│               ├── main.js  # App Initialization
│               └── pages/   # CRUD Views
└── nexa.yaml                # The Master Schema
```

---

## 4. Technology Stack
- **Backend**: Python, Django, Django Rest Framework (DRF).
- **Frontend**: Vue 3 (Composition API), Pinia, Vite.
- **Orchestration**: Nexa Engine (Python).
