# Blueprint Arsitektur NexaPHP (Edisi Final)
*The Next-Generation Progressive PHP Framework for Enterprise & Modular SaaS*

Cetak biru ini menyintesis semua diskusi kita ke dalam satu panduan definitif tentang bagaimana NexaPHP beroperasi. NexaPHP didesain agar seringan bulu untuk aplikasi statis, namun sekuat tank baja untuk sistem ERP.

---

## 1. Filosofi Inti (Core Paradigm)

1. **Microkernel Architecture:** Inti dari kerangka kerja ini sangat tipis. Segala hal yang tidak penting untuk menangani sebuah *Request* HTTP (seperti ORM atau Queue) dicabut dari inti dan dijadikan Ekstensi (Fitur).
2. **Capability System (Bukan Leveling):** Alih-alih membagi aplikasi menjadi Level 1-3, developer mengaktifkan kemampuan spesifik (*capabilities*) sesuai kebutuhan (Orthogonal Design).
3. **Module Driven Architecture:** Segala bentuk logika bisnis **wajib** diletakkan di dalam folder spesifik domain (`apps/sales/`, `apps/hr/`).
4. **Simple things simple, Complex things possible:** Memaksa arsitektur (seperti *Repository* & *DTO*) hanyalah opsional via CLI, bukan paksaan sistem.

---

## 2. Struktur Aplikasi (Microkernel vs Features)

Pemisahan tegas antara *Engine* (Kernel) dan Ekstensi.

### NexaPHP Core (Wajib & Otomatis Menyala)
Komponen ini selalu hidup dan menjadi tulang punggung kerangka kerja.
- **Router** (Memetakan URL ke Controller/Fungsi)
- **Container / PHP-DI** (Penyuntik ketergantungan/Dependency Injection)
- **Module Loader** (Membaca manifes setiap modul saat *booting*)
- **Service Registry** (Penghubung komunikasi RPC lokal antar-modul)
- **Event Dispatcher** (Penyiap sinyal untuk *side-effects*)
- **CLI Engine** (`nexa php ...`)

### NexaPHP Capabilities / Features (Opt-In / Konfigurasi)
Diaktifkan via `config/features.php`.
```php
return [
    'orm'           => env('FEATURE_ORM', true),    // Doctrine / Eloquent Standalone
    'queue'         => env('FEATURE_QUEUE', false), // Redis / RabbitMQ
    'tenancy'       => env('FEATURE_TENANCY', false),
    'audit_trail'   => env('FEATURE_AUDIT', false),
];
```

---

## 3. Struktur Modul & Manifes (Module Loader)

Setiap modul bisnis berada di dalam folder `apps/`. Agar bisa dihidupkan, modul **wajib** memiliki file Manifes (`module.php`).

```text
project/
└── apps/
    └── inventory/
        ├── Models/
        ├── Controllers/
        └── module.php   <-- Manifes Modul
```

**Isi dari `module.php` (Sebagai Kontrak Dependensi):**
```php
return [
    'name' => 'inventory',
    'version' => '1.0.0',
    // Modul akan GAGAL LOAD jika modul 'auth' dan 'finance' tidak hidup
    'requires' => [
        'auth',
        'finance'
    ],
    // Mendaftarkan fungsi RPC ke Service Registry Global
    'exports' => [
        'inventory.reserve_stock' => \Apps\Inventory\Services\StockService::class . '@reserve',
        'inventory.check_stock'   => \Apps\Inventory\Services\StockService::class . '@check'
    ]
];
```

---

## 4. Pola Komunikasi Antar Modul (Inter-Module Communication)

Ini adalah jantung pencegahan *bug* konsistensi data (*Eventual Consistency*) di sistem ERP terdistribusi.

### A. Transaksi Utama Inti (Gunakan: Service Registry)
Ketika Modul **Sales** memproses pesanan, ia harus mengurangi stok di Modul **Inventory**. Jika gagal potong stok, uang tidak boleh ditarik.
```php
// Di dalam SalesController.php
DB::beginTransaction();
try {
    $order = Order::create([...]);
    
    // RPC Lokal: Sinkron dan berada di satu transaksi database
    Nexa::call('inventory.reserve_stock', [
        'product_id' => $item->id,
        'qty' => $item->qty
    ]);
    
    DB::commit(); // Stok & Order tersimpan bersamaan
} catch (\Exception $e) {
    DB::rollBack(); // Aman! Tidak ada overselling
}
```

### B. Efek Samping / Side Effects (Gunakan: Event Dispatcher)
Hal yang terjadi *setelah* transaksi dijamin sukses, namun tidak krusial terhadap integritas data utama.
```php
// Setelah DB::commit();
NexaEvent::dispatch('sales.order_placed', $order->id);

// Listener di Modul Lain (Bisa dilempar ke Redis Queue):
// - Email Module -> Kirim struk PDF
// - Notification Module -> Push ke aplikasi bos
// - Analytics Module -> Catat performa sales harian
```

---

## 5. Pendekatan Fleksibilitas (CLI Scaffolding)

NexaPHP tidak membebani pembuat web statis/sederhana. Rahasianya ada di CLI.

**Jika membuat Landing Page / Blog:**
```bash
nexa php make:module blog --simple
```
*Hasil:* Hanya membuat folder `Models` dan `Controllers`. Developer mengakses DB murni dari Controller secara kotor dan cepat.

**Jika membuat ERP Akuntansi:**
```bash
nexa php make:module finance --enterprise
```
*Hasil:* Otomatis membuat struktur ketat: `Models`, `Controllers`, `Repositories`, `Services` (untuk logic), `DTOs` (untuk validasi data lintas modul), dan `Events`.

**Jika Menggunakan Pendekatan Schema-Driven:**
```bash
nexa php generate nexa.yaml
```
*Hasil:* Menerjemahkan *blueprint* YAML menjadi file Doctrine Entities, Controllers, Service Registry Exports, dan men-generate *diff migration* secara magis.

---

## 6. Frontend: Single Global SPA

- Frontend menggunakan **Vite** yang diletakkan secara utuh di folder `/frontend` atau `/resources/js`.
- Frontend berinteraksi dengan API yang dihasilkan secara modular.
- Tidak disarankan memecah React/Vue per folder modul `apps/inventory/frontend` karena akan mematikan konsep *Shared State* (Pinia/Redux) dan menyulitkan navigasi pengguna (*SPA Routing*).

---

## Ringkasan Blueprint

NexaPHP mengambil kemudahan konfigurasi dari **Laravel**, ketangguhan dependensi arsitektur dari **Symfony (Microkernel)**, sinkronisasi skema pintar ala **Django**, dan menggabungkannya ke dalam satu paradigma baru: **Module Driven Framework dengan Manajemen Kapabilitas.**
