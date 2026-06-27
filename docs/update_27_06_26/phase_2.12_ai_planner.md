# Phase 2.12 - AI Planning Engine (Single Source of Truth)

Sistem Perencanaan AI Tingkat Lanjut (*Enterprise Grade*) yang memisahkan tanggung jawab "Sang Pemikir" (*Planner*) dengan "Sang Pekerja" (*Executor*). Modul ini tertanam secara eksklusif di dalam `nexa/core/ai/planner/`.

## Konsep Dasar (Single Responsibility Principle)
Alih-alih langsung memuntahkan barisan kode secara acak, AI sekarang dipaksa untuk menghasilkan **Execution Plan JSON** yang kaku. 
Skema ini (yang divalidasi oleh `validator.py`) berisi daftar lengkap *Affected Modules*, *Files to Create*, *Files to Modify*, hingga *Execution Steps* terperinci. 

Karena *Execution Plan* ini bersifat murni data terstruktur, kelak rancangan ini dapat dieksekusi dengan mulus oleh sistem *Agentic Executor*, Bot Telegram, Ekstensi VSCode, atau antarmuka manapun.

## Dual-Mode Architecture (Mode Cerdas)
Untuk memastikan Nexa tetap gesit dan tidak lambat saat dipakai obrolan santai, kami memisahkan modenya:
- **Mode Konsultan (Cepat)**: Aktif secara *default*. Tidak melibatkan *Planning Engine*.
- **Mode Eksekusi (Struktural)**: Diaktifkan melalui *Command* Aksi.

## Perintah Aksi Baru (`/plan`)
Jika Anda ingin menyuruh AI membuat fitur kompleks atau merombak sistem, gunakan perintah ini di dalam *Interactive Shell*:

```bash
/plan Buatkan saya sebuah form login untuk framework ini menggunakan Bootstrap 5
```

### Alur Kerja (Orchestrator)
1. **Context Compilation**: `AIPlannerEngine` akan mengambil *Project Facts*, *Pinned Memory*, dan *Rolling Chat Memory*.
2. **System Prompt Injection**: Menjejalkan seluruh konteks tersebut ke *LLM Provider* yang dipilih (Groq/DeepSeek).
3. **Structured Validation**: Memastikan AI menjawab dalam blok JSON murni yang sesuai dengan rancangan `ExecutionPlan`. Jika formatnya cacat, validasi digagalkan.
4. **Markdown Formatting**: Mengubah JSON tersebut menjadi laporan cetak biru (*Blueprint*) Markdown yang sangat rapi.

## Fitur Ekstra yang Ditanamkan
1. **Smart Intent Router**: Anda tidak perlu mengetik `/plan` secara eksplisit. Cukup ketik layaknya manusia: *"Buatkan form login"*, dan Nexa secara ajaib akan mendeteksi niat (*intent*) Anda dan langsung melompat ke mode *Planner*.
2. **AI Recommendations**: Setiap *Execution Plan* yang tercetak, akan menyertakan bagian **💡 AI Recommendations**. Di sini AI akan memberi saran keamanan, pola desain, atau tambahan yang mungkin Anda lewatkan sebelum Anda merestui (*Approve*) rencana tersebut.
