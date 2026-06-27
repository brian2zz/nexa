# Phase 3 - Autonomous Scaffolding Layer (The Executor)

Phase 3 adalah fase di mana Nexa berevolusi dari sekadar pemberi saran menjadi **Pembuat Nyata** (*Autonomous Builder*). Komponen ini berpusat di direktori `nexa/core/ai/executor/`.

## 1. AI Executor (`builder.py` & `generator.py`)
Mesin yang menerjemahkan *Execution Plan* (dari Phase 2.12) menjadi barisan *source code* secara fisik.
- **`AIGenerator`**: Dipanggil pada setiap langkah pembuatan file. Ia dikhususkan untuk menghasilkan *raw code block* murni tanpa penjelasan basa-basi (berdasarkan panduan *Project Facts* dan *Pinned Memory*).
- **`AIExecutor`**: Mengkoordinasikan pembuatan *folder* (`os.makedirs`), memanggil *Generator*, lalu menyimpan file tersebut (`f.write`) sambil menampilkannya di terminal dengan animasi berputar yang elegan.

## 2. Perintah Pembuatan Proyek Baru (`nexa create`)
Perintah global `nexa create "<Deskripsi>"` telah diaktifkan untuk *scaffolding* (membuat proyek dari nol). 
Karena sangat berisiko jika AI salah menebak, perintah ini dirancang super sopan:
1. **Interactive Inquirer**: Jika Anda tidak menyebutkan *framework*, terminal akan bertanya: `[?] Framework apa yang ingin Anda gunakan? (1. NexaPHP, 2. Django, 3. Flutter)`.
2. **Review Tembok Terakhir**: Sebelum menuliskan ratusan baris kode ke *harddisk*, AI akan mencetak rencananya (beserta **💡 AI Recommendations**) dan bertanya: `[?] Eksekusi rencana ini dan bangun file fisiknya? (Y/n)`.

## 3. Fitur Smart Commands (`/commands`)
Di dalam *Interactive Shell* (`nexa ai`), fitur ajaib `/commands` telah ditambahkan.
Nexa akan menggunakan `ProjectDetector` (Phase 2.9) untuk mengetahui Anda sedang berada di dalam ekosistem apa. 
- Berada di **Django**? Ia akan memunculkan daftar perintah `django` (seperti `run, new, startapp, dev`).
- Berada di **NexaPHP**? Ia akan menyuguhkan `make:module, make:model`.
Ini adalah *Context-Aware Help Menu* tercanggih yang membuat Anda tidak perlu menghafal baris perintah!
