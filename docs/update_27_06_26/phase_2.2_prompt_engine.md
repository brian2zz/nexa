# Phase 2.2 - Prompt Engine

Fase ini mengelola *Context-Aware Prompts* agar AI bisa memahami proyek secara kontekstual tanpa perlu diinstruksikan ulang oleh pengguna secara manual.

## Apa yang sudah bisa dilakukan Nexa?
1. **Dynamic Templating (`PromptBuilder`)**: Nexa dapat secara otomatis meracik pesan sistem (*System Prompt*) dan pesan pengguna (*User Prompt*) secara dinamis sesuai bahasa pemrograman (Python/PHP/Flutter).
2. **Strict JSON Constraint**: Mesin memaksa (*hard-coded rule*) agar setiap respons AI **wajib** dikembalikan dalam format JSON Murni (bukan format perbincangan *chatbot*), agar bisa dibaca oleh sistem internal Nexa (via `ResponseParser`).
3. **Penyisipan Otomatis Kode**: Kode *source* dari proyek yang ditargetkan diinjeksi (*embed*) secara halus ke dalam *prompt*, sehingga AI bisa membaca kodenya dan mendeteksi kelemahan keamanan atau *technical debt*.
