# Phase 3.2 - AI Transformation Engine (Enterprise Grade)

## Status: Selesai ✅

**Tujuan**: Membangun sebuah *engine* murni (*Pure Transformation*) yang bertindak sebagai "dapur" utama Nexa dalam mengubah *Execution Plan* dan *Context Bundle* menjadi blok kode siap pakai. Engine ini sama sekali tidak menyentuh sistem *file*, tidak meminta *approval*, dan tidak melempar *patch* secara langsung.

---

## 1. Kemampuan (8 Mode Transformasi)
Nexa kini bukan lagi sekadar asisten penjawab (*chatbot*), ia adalah pabrik kode. *AI Transformation Engine* dirancang sebagai *Shapeshifter* yang mampu merubah wujud (*Strategy Pattern*) ke dalam 8 mode operasi:

1. **GENERATE**: Menulis kode atau file baru dari nol (*from scratch*).
2. **MODIFY**: Mengubah bagian tertentu dari kode yang sudah ada.
3. **REFACTOR**: Membersihkan dan menata ulang arsitektur kode lama tanpa mengubah *output* aslinya.
4. **REPAIR**: Menganalisis *stacktrace error* dan memberikan blok kode perbaikannya (*bug fixing*).
5. **OPTIMIZE**: Mengubah kode yang berjalan lambat/boros memori menjadi versi *high-performance*.
6. **TRANSLATE**: Mengonversi kode dari satu bahasa ke bahasa lain (misal: PHP ke Python).
7. **EXPLAIN**: Membaca serangkaian sistem kompleks dan memberikan penjelasan tekstual yang ramah manusia.
8. **SUMMARIZE**: Membuat ringkasan eksekutif atau *docstring* dari sebuah kelas atau modul raksasa.

---

## 2. Arsitektur Komponen

Lokasi Modul: `nexa/core/ai/transformation/`

### A. Data Transfer Object (DTO)
- `TransformationRequest`: Kelas pembungkus untuk menstandarisasi *input*. Berisi `mode`, `execution_plan`, `context_bundle`, `temperature`, dan instruksi tambahan.
- `TransformationResult`: Kelas yang dikembalikan oleh *Engine*. Berisi status `success`, `generated_code`, `explanation`, serta metadata observabilitas.

### B. Prompt Factory & Strategy Pattern
Tidak ada *God Object* (file raksasa) di Nexa. Setiap mode diproses oleh pembangun instruksi (*Prompt Builder*) tersendiri yang dipanggil secara otomatis oleh `PromptFactory`:
- `GeneratorPromptBuilder`
- `ModifierPromptBuilder`
- `RepairPromptBuilder`
- `AnalyzerPromptBuilder`

### C. Response Processor (Parser)
Bertugas sebagai *Regex Ninja* yang mengekstrak blok *markdown* (```python ... ```) dari respons mentah LLM, memisahkan penjelasan manusia, dan melempar *error* internal jika LLM berhalusinasi (misal, merespons tanpa blok kode).

### D. Transformation Engine (Sang Konduktor)
Kelas utama yang menyatukan semua komponen:
- Ia mengusung sifat **Provider Agnostic** (Bisa dicolok menggunakan `OpenAI`, `Groq`, `DeepSeek`, `Ollama`).
- Ia menyuntikkan ketergantungan melalui injeksi (`__init__(self, provider: LLMProvider)`).

---

## 3. Fitur Spesial: Graceful Error Handling & Retry Policy
Nexa tidak mudah menyerah. Jika `ResponseProcessor` mengeluh bahwa format AI berantakan (*Format rusak, tidak ada markdown*), *Engine* **TIDAK AKAN** melempar *Exception* yang merusak program.

Ia akan menangkap kesalahan itu, secara otomatis melakukan iterasi (*Retry Loop*), dan membentak balik si LLM:
> *"System Error from previous attempt: No valid markdown code block found. Please fix the format and try again."*

Ini memastikan *pipeline* tetap berjalan mulus, menjadikan Nexa AI berstandar *Enterprise*.

---

## 4. Alur Kerja (Workflow)
```
Execution Plan & Context 
        ↓
TransformationRequest (DTO)
        ↓
TransformationEngine
        ↓ (Factory)
Prompt Builder yang sesuai (misal: REPAIR)
        ↓
LLMProvider (Groq/Ollama/dll)
        ↓
ResponseProcessor (Ekstrak & Validasi)
        ↓ (Jika format rusak -> Lempar balik ke LLMProvider [Retry])
TransformationResult (Berisi Kode, Penjelasan, & Observabilitas)
```
