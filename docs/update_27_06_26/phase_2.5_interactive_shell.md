# Phase 2.5 - Nexa Interactive AI Shell (REPL)

Fase ini meningkatkan secara drastis kualitas pengalaman pengembang (*Developer Experience*) dengan memberikan lingkungan antar-muka berbasis terminal (*Shell*).

## Apa yang sudah bisa dilakukan Nexa?
1. **Interactive Shell (`nexa ai`)**: REPL (*Read-Eval-Print Loop*) khusus yang menyulap layar terminal Anda menjadi mode asisten cerdas `Nexa>`.
2. **Persistent Config Manager**: Semua setelan konfigurasi (Model default, Provider aktif, dan API Key) secara otomatis disimpan di dalam disk lokal Anda (`~/.nexa/config.json`). Anda cukup menyetelnya sekali selamanya untuk semua proyek Anda.
3. **Advanced Prompt Toolkit**: Pemasangan modul tingkat lanjut yang memberikan dukungan fitur super canggih:
   - **Dropdown Autocomplete**: Saat pengguna mengetikkan tanda garis miring (`/`), daftar perintah (seperti `/status`, `/set-model`) akan muncul dalam kotak *dropdown* (*suggested menu*). Dapat di navigasi memakai `Tab` atau panah *keyboard*.
   - **Command History**: Pengguna dapat menggunakan tombol *Panah Atas* dan *Panah Bawah* untuk memanggil ulang perintah-perintah lama yang sebelumnya pernah dieksekusi.
4. **Smart Handling (DeepSeek Ready)**: Apabila Anda pindah ke provider *cloud* (*DeepSeek*) memakai `/select-provider deepseek`, sistem otomatis akan mendeteksi apakah `API_KEY` sudah terdaftar atau belum. Jika kosong, sistem otomatis masuk ke mode pengisian sandi aman (*hidden masking*) yang membimbing *user*.
5. **Threaded UI Spinner**: Animasi `[ \ ]` multi-thread yang akan terus berputar ketika AI bekerja sehingga layar tidak "*hang*" dan *UX* menjadi lebih premium.
