# Phase 2.10 - Persistent Chat Memory (Sesi Stateful)

Nexa AI kini tidak lagi mengidap amnesia! Modul ini menambahkan kemampuan **Stateful Memory** berbasis sesi untuk `nexa ai`, menyerupai interaksi berkesinambungan seperti ChatGPT.

## Arsitektur Ingatan

1. **SQLite Database (`chat_memory.db`)**
   - Sistem tidak menggunakan file JSON yang berat, melainkan *database* SQLite super ringan yang tertanam di `~/.nexa/chat_memory.db`.
   - Tabel direlasikan secara spesifik dengan **Project Path** tempat `nexa ai` dijalankan (terisolasi per proyek).

2. **Rolling Window (Optimalisasi Token)**
   - Sistem menggunakan teknik *Rolling Window* untuk melindungi memori lokal dari kebocoran (*Memory Leak*).
   - AI hanya memuat **3 sesi tanya-jawab terakhir** secara aktif ke dalam memori untuk menjaga token LLM tetap hemat dan kilat. Pesan-pesan yang lebih tua tetap diamankan di *database*.

3. **Sistem Sesi (Session ID)**
   - Setiap kali `nexa ai` dibuka di dalam *project*, ia akan diam-diam menghasilkan Sesi Baru secara otomatis.
   - Ia tidak akan mencampurkan memori dari sesi hari-hari sebelumnya KECUALI secara eksplisit diminta oleh *user*.

## Perintah Manajemen Ingatan (Time Machine)

Fitur manajemen ingatan ini dapat dikendalikan langsung oleh *user* melalui antarmuka *Shell* `Nexa>` menggunakan perintah sakti berikut:

- **`/history`**
  Menampilkan semua daftar Sesi Percakapan (*Chat Sessions*) yang pernah dilakukan di folder proyek ini pada masa lampau, beserta jumlah pesan dan keterangan waktu.

- **`/load <ID>`**
  Memuat kembali konteks percakapan historis (misalnya `/load 5`) dari masa lalu ke dalam kepala AI secara langsung (berguna untuk melanjutkan obrolan hari kemarin).

- **`/clear`**
  Merupakan tombol *panic/reset*. Perintah ini akan mencuci bersih otak dan ingatan aktif AI, lalu memulai ID Sesi yang sepenuhnya kosong seketika.
