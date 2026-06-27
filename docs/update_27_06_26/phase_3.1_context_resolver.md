# Phase 3.1 - Context Resolver Engine (Task-Aware)

Sebagai perlindungan absolut terhadap pemborosan memori (Token), Nexa kini dipersenjatai dengan sebuah filter deterministik kaku bernama **Context Resolver Engine**. Berbeda dengan komponen lain, modul ini murni berbasis aturan ketat (*Rule-Based*) dan sama sekali tidak melibatkan "Tebakan AI".

## Arsitektur Anti-Kebocoran Token
Mesin ini mencegah Nexa menelan *file* berukuran raksasa secara utuh dengan cara menerapkan **Fallback Pipeline (Penanganan Ekstrem 4 Lapis)**:

1. **Level 1 (Regex murni):** Menangkap struktur *Class/Function* yang tepat sasaran (Tingkat akurasi: 95%).
2. **Level 2 (Class/Function Detector):** Algoritma pembedah blok khusus (Tingkat akurasi: 85%).
3. **Level 3 (Keyword Window):** Jika gagal dibedah, sistem hanya akan memotong 100 baris sebelum dan sesudah area kode target (Tingkat akurasi: 55%).
4. **Level 4 (Full File):** Penggunaan senjata terakhir. Sistem HANYA mengizinkan ini jika *file* tersebut panjangnya kurang dari 800 baris. Jika lebih panjang dari itu, sistem menolak untuk mencegah '*Context Limit Exceeded*'.

## Fitur Unggulan V2
1. **Abstraksi Token (Future-Proof):** Menggunakan `estimators/base.py` sebagai kerangka, saat ini ditopang oleh `SimpleTokenEstimator` (1 Token = 4 Karakter). Kelak, arsitektur ini siap dipasangi *tokenizer* kelas berat (`tiktoken` / `llama`) tanpa merombak sistem utama.
2. **Language Strategy Khusus:** Strategi pemotongan token dipisah ke dalam modul per-bahasa (`extractors/php.py`, `extractors/python.py`, dll). Karena cara memotong kelas PHP berbeda jauh dengan cara memotong fungsi Python.
3. **Task-Aware Resolver:** Otak filter ini mengerti jenis tugas Anda:
   - Jika meminta `explain`, ia menyempitkan radar fokusnya (tanpa perlu melihat pohon *dependency*).
   - Jika Anda memerintahkan pembuatan fitur (via `/plan`), ia membuka radar strukturnya, hanya mengambil daftar *import*, deklarasi kelas, nama fungsi tanpa memedulikan isi dari fungsinya!

## Kualitas Terukur
Output dari mesin ini (disebut **Context Bundle**) kini menyertakan "Kartu Laporan" (*Quality Metrics*). 
Contoh:
```json
{
  "estimated_tokens": 1250,
  "compression_ratio": 89.2,
  "selection_method": "regex",
  "fallback_level": 1,
  "confidence": 0.95
}
```
Metrik ini membantu Sang Orketrator Utama (Nexa) untuk menyadari seberapa akurat konteks yang sedang ia hadapi sebelum mengirimkannya ke LLM (*Groq/DeepSeek*).

## 4. Demonstrasi di Interactive Shell (`nexa ai`)
Di dalam ekosistem terminal kita, Anda dapat merasakan langsung kehebatan mesin ini. Saat Anda meminta AI menjelaskan sebuah fungsi (misal: `"Jelaskan fungsi login() di @AuthController.php"`):
1. **Pencegatan**: *Intent Router* (Phase 2.13) menangkapnya sebagai *task* `"explain"`.
2. **Pemotongan**: *Context Resolver* membaca *file* tersebut. Karena ukuran *file*-nya mungkin besar, ia memotong dan **hanya mengekstrak fungsi `login()`** tanpa membawa sisa file (menghemat ratusan baris token).
3. **Hasil**: AI merespons jauh lebih cepat (karena yang dibaca sedikit), biaya token lebih hemat, dan tidak ada lagi fenomena AI melantur (*hallucinate*) karena bingung melihat seluruh isi *file*.
