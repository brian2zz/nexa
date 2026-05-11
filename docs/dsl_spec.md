# Nexa DSL Specification (v3.0)

Dokumen ini adalah spesifikasi teknis resmi untuk **Nexa Language**. Semua generator dan validator Nexa harus mematuhi standar ini untuk menjamin determinisme sistem.

---

## 1. Project Schema Spec
Struktur utama `nexa.yaml`.

| Key | Type | Description |
| :--- | :--- | :--- |
| `project` | `string` | Nama unik proyek (Slug-style). |
| `apps` | `list` | Daftar modul aplikasi dalam proyek. |

### App Definition
Setiap aplikasi didefinisikan sebagai modul independen.
```yaml
- name: accounting
  models: [...]
```

---

## 2. Model Schema Spec
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

---

## 4. Generator Lifecycle
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
