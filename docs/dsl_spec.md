# Nexa DSL Specification (v3.0)

Dokumen ini adalah spesifikasi teknis resmi untuk **Nexa Language**. Semua generator dan validator Nexa harus mematuhi standar ini untuk menjamin determinisme sistem.

---

## 1. Project Schema Spec
Struktur utama `nexa.yaml`.

| Key | Type | Description |
| :--- | :--- | :--- |
| `project` | `string` | Nama unik proyek (Slug-style). |
| `apps` | `list` | Daftar modul aplikasi dalam proyek. |

---

## 2. App Specification
Definisi modul/aplikasi dalam proyek.

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `name` | `string` | Nama aplikasi (snake_case). |
| `main` | `boolean` | Jika `true`, aplikasi ini akan menjadi dashboard utama (`/`). |
| `models` | `list` | Daftar model di dalam aplikasi ini. |

> [!TIP]
> Jika tidak ada aplikasi yang ditandai `main: true`, Nexa secara otomatis akan memilih aplikasi pertama di daftar YAML sebagai entry point utama proyek.

---

## 3. Model Schema Spec
Mendefinisikan entitas data dan perilaku UI.

| Key | Type | Description |
| :--- | :--- | :--- |
| `name` | `string` | Nama Model (PascalCase saat di-generate). |
| `crud` | `bool | object` | Konfigurasi otomatisasi UI. |
| `fields` | `list` | Daftar atribut model. |

### CRUD Configuration
```yaml
crud:
  enabled: true
  table:
    searchable: [title]   # Field yang muncul di bar pencarian
    sortable: [price]     # Field yang bisa diurutkan
    columns: [id, title]  # Kolom yang ditampilkan di tabel
  form:
    layout: default       # default | tabs | sections
```

---

## 3. Field Types Spec
Tipe data yang didukung oleh Nexa Translator.

| Type | Django Equivalent | Frontend Input |
| :--- | :--- | :--- |
| `string` | `CharField` | `text` |
| `text` | `TextField` | `textarea` |
| `int` / `integer`| `IntegerField` | `number` |
| `float` | `FloatField` | `number` |
| `decimal` | `DecimalField` | `number` |
| `bool` / `boolean`| `BooleanField` | `checkbox` |
| `date` | `DateField` | `date` |
| `datetime` | `DateTimeField` | `datetime-local` |
| `foreignkey` | `ForeignKey` | `select` (Async) |
| `manytomany` | `ManyToManyField` | `multi-select` |
| `onetoone` | `OneToOneField` | `select` |

### Relationship Options
Untuk tipe relasi (`foreignkey`, `onetoone`, `manytomany`), Anda dapat menambahkan:
*   **`to`**: Target Model (Format: `ModelName` atau `app.ModelName`).
*   **`on_delete`**: Kebijakan penghapusan (`CASCADE`, `SET_NULL`, `PROTECT`). Default: `CASCADE`.
    *   *Catatan: Nexa otomatis menambahkan `null=True` jika Anda memilih `SET_NULL`.*
*   **`related_name`**: Nama unik untuk akses balik (reverse accessor) dari model target. 
    *   *Wajib diisi jika ada lebih dari satu field yang merujuk ke model yang sama.*

---

## 4. Universal Dynamic Architecture (SaaS Ready)
Nexa secara otomatis membangun fondasi yang mendukung Multi-Tenancy namun tetap fleksibel untuk aplikasi tunggal.

### Hybrid Routing Pattern
Setiap aplikasi yang di-generate mendukung dua pola URL sekaligus:
1.  **Direct Path**: `/app-name/` (Untuk akses internal/admin).
2.  **Tenant Path**: `/<tenant_slug>/app-name/` (Untuk isolasi data pelanggan/SaaS).

### Core Foundation (`apps.home`)
Nexa secara otomatis menyertakan aplikasi `home` sebagai pusat kontrol yang berisi:
*   **Tenant Middleware**: Deteksi otomatis konteks bisnis dari URL.
*   **Activity Middleware**: Audit trail otomatis untuk setiap aktivitas user.

---

## 5. Generator Lifecycle
Urutan eksekusi (Priority System).

1. **PRIORITY_CORE - 50** (`project.shared_ui`): Menyiapkan library UI global.
2. **PRIORITY_CORE - 10** (`scaffold.app_entry`): Menyiapkan `index.html` dan `main.js`.
3. **PRIORITY_CORE + 1** (`api.model`): Membangun database schema.
4. **PRIORITY_CORE + 15** (`api.backend_service`): Membangun logic layer.
5. **PRIORITY_CORE + 20** (`api.serializer`): Membangun data transformer.
6. **PRIORITY_CORE + 30** (`api.view`): Membangun controller.
7. **PRIORITY_EXTENSION** (`crud.*`): Membangun frontend UI components.

---

## 5. Deterministic Naming Conventions
| Context | Pattern | Example |
| :--- | :--- | :--- |
| Backend Class | `PascalCase` | `ProductService` |
| Backend File | `snake_case` | `product_service.py` |
| Frontend Component| `PascalCase` | `ProductList.vue` |
| Frontend Service | `camelCase` | `productService.js` |
| API Route | `plural-kebab` | `/api/v1/products/` |
| Frontend Route | `plural-kebab` | `/products/` |
