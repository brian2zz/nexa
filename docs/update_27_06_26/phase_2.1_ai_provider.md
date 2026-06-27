# Phase 2.1 - AI Provider Layer

Fase ini meletakkan fondasi infrastruktur Nexa untuk berkomunikasi dengan model AI (Large Language Models), tanpa terikat (*vendor-lock*) pada satu perusahaan saja.

## Apa yang sudah bisa dilakukan Nexa?
1. **Multi-Provider Support**: Nexa kini memiliki arsitektur `ProviderFactory` yang mendaftarkan berbagai agen penyedia AI.
2. **Ollama Integration**: Dukungan *native* untuk **Ollama** lokal (`OllamaProvider`). Seluruh analisis kode kini diproses di komputer lokal user tanpa membocorkan kode ke server publik (dengan menggunakan model *open-source* seperti `llama3` atau `qwen3:14b`).
3. **DeepSeek Integration**: Tersedia juga **DeepSeekProvider** bagi pengguna yang ingin memproses kode berat via *cloud API* (jauh lebih cepat dan kuat jika spesifikasi laptop pengguna rendah).
4. **Resiliency**: Jika Ollama tidak menyala, atau model yang diminta tidak ada, Nexa tidak akan *crash*, melainkan memunculkan instruksi jelas kepada pengguna (misalnya `"Please pull it first using 'ollama pull qwen'"`).
