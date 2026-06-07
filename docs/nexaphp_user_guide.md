# Panduan Penggunaan NexaPHP

NexaPHP adalah kerangka kerja (framework) modular yang berjalan di atas ekosistem Nexa, dirancang untuk membangun sistem *Enterprise* dan *SaaS* yang cepat dengan kombinasi backend PHP ringan dan frontend Vue.js.

## 1. Instalasi dan Inisialisasi Proyek

Untuk memulai proyek baru dengan NexaPHP, gunakan perintah `new`:

```bash
nexa php new nama_proyek --frontend=vue
```

Perintah di atas akan:
- Membuat folder `nama_proyek` dengan struktur *backend* (PHP) dan *frontend* (Vue.js).
- Menginstal dependensi Composer (`vendor/`) dan NPM (`node_modules/`).
- Menyiapkan konfigurasi `.env`.
- Menyiapkan *Router* Vue dan Antarmuka Admin (Nexa Admin).

Setelah selesai, jalankan peladen (server):

```bash
cd nama_proyek
nexa php run
```

Aplikasi dapat diakses di `http://127.0.0.1:8000`.

---

## 2. Konfigurasi Lingkungan (.env)

Sistem NexaPHP menggunakan variabel lingkungan untuk menyimpan konfigurasi penting seperti kredensial basis data.

Buka file `.env` di direktori proyek Anda:

```env
APP_ENV=local
APP_DEBUG=true
APP_URL=http://127.0.0.1:8000

# Konfigurasi Database (Mendukung sqlite, mysql, pgsql)
DB_CONNECTION=sqlite
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=database.sqlite
DB_USERNAME=root
DB_PASSWORD=
```

Jika Anda ingin beralih ke MySQL, ubah `DB_CONNECTION` menjadi `mysql` dan sesuaikan nama `DB_DATABASE`.

---

## 3. Manajemen Basis Data (Migrasi)

Setelah Anda mendefinisikan model atau tabel baru di sistem, Anda perlu mencetak perubahan struktur tersebut ke dalam bentuk migrasi, lalu menjalankannya.

- **Membuat Migrasi:**
  ```bash
  php bin/nexa makemigrations
  ```
  Ini akan memindai seluruh *Model* Doctrine ORM Anda dan membuat berkas migrasi PHP.

- **Menjalankan Migrasi:**
  ```bash
  php bin/nexa migrate
  ```
  Ini akan mengeksekusi migrasi ke dalam basis data aktif (sesuai `.env`).

---

## 4. Membangun Modul Baru (Manual)

Untuk menciptakan kerangka kerja modul (aplikasi mini) di dalam sistem:

```bash
nexa php make:module inventory
```

Akan terbuat direktori `apps/inventory/` dengan:
- `Models/` (Entitas Basis Data)
- `Controllers/` (Logika Aplikasi)
- `routes/api.php` (Pengaturan Rute API)
- `module.php` (Manifes Modul)

Jika Anda membutuhkan arsitektur berskala besar (Enterprise):
```bash
nexa php make:module inventory --enterprise
```
Sistem akan menambahkan *Repositories*, *Services*, *Events*, dan *DTOs*.

---

## 5. Pembuatan Kode Otomatis (Generator)

Nexa mendukung pembuatan kerangka kerja secara otomatis berdasarkan deklarasi yaml (seperti `nexa.yaml`). Fitur ini (yang saat ini masih dalam fase penyempurnaan) memungkinkan Anda mendefinisikan seluruh Modul beserta propertinya.

```bash
nexa php generate nexa.yaml
```

Ini akan menghasilkan:
- Entitas *Doctrine ORM* di dalam `Models/`
- *Controller* API yang mengembalikan JSON
- (Rencana Masa Depan) Frontend Vue CRUD komponen otomatis.

---

## 6. Nexa Admin Dashboard

NexaPHP menyertakan Antarmuka Admin bawaan bergaya *Enterprise* (berbasis Vue + TailwindCSS) yang tidak akan mengotori direktori proyek (berjalan dalam mode *Stealth*).

- Akses Dasbor Admin di: `http://127.0.0.1:8000/nexa-admin`

Admin ini akan otomatis membaca seluruh skema *Database* dan menyajikannya dalam format antarmuka visual yang modern dan memukau. Semua modul yang Anda bangun dengan `nexa php make:module` (yang memiliki Model) secara ajaib akan muncul di panel administrasi tanpa perlu pengaturan rute manual!
