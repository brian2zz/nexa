# Phase 2.11 - Persistent Project Facts & Pinned Memory

Sistem memori Nexa AI telah dirombak menjadi **Tri-Memory Architecture**, sebuah desain yang meniru kognisi otak manusia dengan memisahkan tiga jenis ingatan ke dalam *database* `chat_memory.db` secara terstruktur:

## Arsitektur Tri-Memory
1. **Chat Memory (Memori Jangka Pendek)**: Untuk obrolan *rolling window*.
2. **Project Facts (Memori Semantik)**: Fakta teknis mutlak (contoh: *Framework*, Bahasa, *Package Manager*).
3. **Pinned Memory (Memori Episodik/Preferensi)**: Catatan kritis dan aturan gaya *koding* (*Coding Style*) dari *user* yang tidak boleh dilanggar.

## Fitur & Perintah
- **`/facts`**: Menampilkan tabel fakta yang sedang aktif di *project* saat ini.
- **`/facts set <k> <v>`**: Menyimpan fakta baru (misal: `/facts set UI_Framework Tailwind`).
- **`/facts remove <k>`**: Menghapus fakta.
- **`/pin <text>`**: Secara eksplisit mem-*pin* aturan atau instruksi yang harus dipatuhi AI untuk semua obrolan selanjutnya.
- **`/pin`**: (Tanpa argumen) Akan secara ajaib mem-*pin* jawaban/kode terakhir yang dihasilkan oleh AI sebelumnya!
- **`/pins`**, **`/unpin <id>`**, **`/clearpins`**: Manajemen *Pinned Memory*.

## Integrasi *Scanner* Otomatis
Apabila Anda menjalankan `nexa scan`, *Project Facts* seperti `framework` dan `language` akan terisi ke *database* ini secara otomatis (tanpa menimpa preferensi manual yang telah Anda tetapkan).

## Integrasi *System Prompt*
Setiap kali AI berpikir, ketiga lapisan memori ini akan dirajut *(inject)* ke dalam *System Prompt* utama sebelum dikirim ke *LLM Provider*, menjamin AI tidak akan pernah "lupa" akan preferensi sistem Anda.
