# Phase 2.4 - AI Analyzer & Orchestrator

Fase ini menyambungkan pipa *Static Analyzer*, *Knowledge Engine*, *Prompt Engine*, dan *AI Provider* menjadi sebuah harmoni kerja yang siap dipanggil.

## Apa yang sudah bisa dilakukan Nexa?
1. **AIAnalyzer Orchestrator**: Modul sentral yang bertindak sebagai "Mandor". CLI cukup memanggil `analyzer.analyze()`, dan modul ini akan mengatur pengiriman data statis (*static result*) dan data dari *scanner*.
2. **Robust Response Parser**: Jika model AI melanggar aturan dan membalas dengan curhat (*"Here is your json:"*) alih-alih mengirim JSON langsung, modul ini (`response_parser.py`) akan menggunakan regex (*Repair Engine*) untuk mengekstrak hanya blok JSON-nya saja.
3. **Smart Retry Loop**: Jika ekstrak JSON benar-benar gagal/rusak, sistem tidak langsung tumbang. Sistem ini akan mengulang permintaan otomatis (*retry*) hingga batas waktu tertentu (mencegah *crash* saat presentasi).
4. **Adapter & Merger**: Standarisasi skema antara mesin lama (V1) dan mesin baru (V2).
5. **Output Formatter**: CLI sekarang mendukung fitur *export report* menjadi bentuk warna *Terminal Text*, format *Markdown* untuk GitHub, maupun raw *JSON*.
6. **Graceful Error Handling (AnalysisResult Object)**: Menghindari *Exception Crash Stack Trace*. Seluruh *error* dibungkus ke dalam objek `AnalysisResult.errors` agar CLI tetap elegan.
