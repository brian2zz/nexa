# Phase 2.3 - Knowledge Engine & Caveman Skills

Fase ini melahirkan "Mesin Akal Sehat Lokal" (Non-AI) yang sangat masif, berfungsi untuk memilah ratusan file proyek (agar token tidak jebol saat dikirim ke AI).

## Apa yang sudah bisa dilakukan Nexa?
1. **Caveman Skills (`skill.md`)**: Sistem instruksi prasejarah sederhana agar struktur data *prompt* menjadi luar biasa ringkas dan menghemat biaya ribuan Token.
2. **Intent Engine**: Saat user meminta `"Analisis fitur otentikasi"`, mesin ini otomatis menterjemahkannya menjadi domain pencarian file spesifik (berisi kata kunci: *jwt, login, register, auth*).
3. **Dependency Graph Parser**: File tidak dikirim secara acak. Nexa membuat graf relasi (misalnya `Controller -> Service -> Repository`).
4. **Scorer & Ranker**: Setiap file diberi skor "Relevansi" (0-100) berdasarkan kemiripannya dengan niat (*intent*) pengguna dan posisinya dalam arsitektur proyek.
5. **BaseOptimizer**: Fitur pemangkasan (*cutoff*) agar jika proyek berjumlah 200 file, hanya 9 file paling relevan saja yang ditarik untuk diproses AI (Kompresi bisa mencapai > 90%).
6. **Metrics Generator**: Menghasilkan data analitik berupa angka statistik, waktu eksekusi (biasanya < 1 milidetik), dan jumlah file yang dikompresi.
