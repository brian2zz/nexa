# Phase 2.6 - 2.9: Advanced Shell & Context Awareness

Pembaruan ini berfokus pada mengubah Interactive Shell (`nexa ai`) dari sekadar alat *chat* biasa menjadi Agen Cerdas yang mandiri, proaktif, dan sepenuhnya sadar akan struktur lokal *project*.

## Phase 2.6: Explain Mode & Regular Chat
- **`/explain <path>`**: Perintah khusus yang secara otomatis menggunakan `CodeExtractor` untuk mengekstrak rentang baris kode (*snippet*) spesifik, dan meminta AI menjelaskannya.
- **Regular Chat**: Fitur *chat* bebas yang mengizinkan *user* untuk mengobrol dengan asisten tanpa *prefix* perintah apa pun.

## Phase 2.7: Auto-Context Injection (File Mentions)
- Mendukung fitur *tagging* file dengan karakter `@` (misalnya `@config/urls.py` atau `@directory:src/`).
- Shell akan secara otomatis membaca isi file/direktori tersebut dan menyuntikkannya ke dalam *System Prompt* sebelum mengirimkannya ke AI, sehingga pengguna tidak perlu melakukan *copy-paste* secara manual.

## Phase 2.8: Smart Context Auto-Resolver
- **`ModuleResolver`**: Komponen baru (`nexa/core/ai/knowledge/resolver.py`) yang bertugas memindai teks kode dan menerjemahkan modul pihak pertama (misalnya `from .models import User`) menjadi path file lokal asli.
- **Auto-Dependency Crawler**: Jika *user* memberikan *mention* `@file.py`, sistem tidak hanya menarik `file.py`, melainkan menggunakan `DependencyParser` untuk menemukan hingga **maksimal 3 file pendukung lokal**, mengekstrak esensinya menggunakan `RegexSummarizer` (Caveman Skill), dan ikut membungkusnya ke dalam *prompt*.

## Phase 2.8.1: Fuzzy Path Finder
- Mengeliminasi kebutuhan *user* untuk mengetik *path* secara absolut.
- Jika *user* hanya mengetik `@web.py` (namun nama asli adalah `apps/orders/views/web.py`), sistem menggunakan rekursi `os.walk` untuk menebak dan memperbaiki lintasan file tersebut secara kilat (mengabaikan folder berat seperti `.git`).

## Phase 2.9: Global Context Awareness
- Mengintegrasikan `ProjectDetector` (yang awalnya hanya dipakai untuk perintah `nexa analyze`) ke dalam *startup* loop Interactive Shell.
- Kini AI secara bawaan (*by default*) mengetahui *framework*, *language*, dan *path project* tempat ia dijalankan (misalnya: *Django - Python*), bahkan tanpa adanya konteks `@file` sama sekali.

## UI / UX Enhancements
- Teks jawaban dari asisten AI dan *output* dari `/explain` kini dicetak dengan warna **Cyan (\033[96m)** menggunakan standar *ANSI Escape Codes* untuk visibilitas yang jauh lebih baik dibandingkan dengan input pengguna.
- Pembaruan konfigurasi *default provider* (khususnya Groq) beralih dari model *decommissioned* (`llama3-8b-8192`) ke model generasi terbaru yang didukung secara resmi (`llama-3.1-8b-instant`).
