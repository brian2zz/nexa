# Nexa AI - Master Contract

Selamat datang di direktori spesifikasi arsitektur internal **Nexa AI**. 

Jika Anda adalah *developer* baru, kontributor *open source*, atau *maintainer* sistem ini, **BERHENTI SEJENAK**. Bacalah dokumen ini sebelum Anda melihat atau menulis satu baris kode pun di dalam *core engine* Nexa.

---

## 1. Apa itu Master Contract?

**Master Contract** bukanlah sekadar dokumentasi atau buku panduan biasa. Ini adalah **perjanjian hukum (secara arsitektur)** yang mengikat seluruh komponen dan *engine* di dalam Nexa. 

Nexa dirancang sebagai sebuah *Platform* yang modular. Setiap fase dan *engine* (*Planner*, *Transformation Engine*, *Patch Engine*, *Approval Engine*) hidup sebagai entitas yang mandiri. Mereka tidak saling mengetahui bagaimana cara kerja internal satu sama lain. Mereka **hanya** berkomunikasi melalui bahasa universal yang disepakati bersama. 

Bahasa universal inilah yang disebut sebagai **Contract**.

## 2. Kenapa Contract Ini Dibuat?

Dalam sistem kecerdasan buatan (*AI*) yang terus berevolusi menuju otonomi (Phase 6: *Autonomous Software Engineer*), kekacauan sangat mudah terjadi jika:
- Sebuah *engine* tiba-tiba mengubah format *output*-nya.
- Modul *plugin* eksternal bingung harus mengirim data dalam bentuk apa.
- Terjadi *breaking changes* setiap kali ada pembaruan pada *Prompt Strategy*.

Oleh karena itu, Master Contract ini menjamin **Stabilitas**, **Keseragaman (Consistency)**, dan **Kompabilitas Mundur (Backward Compatibility)**. Jika sebuah komponen mematuhi Contract, maka dijamin komponen tersebut bisa terhubung mulus dengan seluruh ekosistem Nexa, apa pun versi model LLM (Llama, GPT, DeepSeek) atau *provider* yang sedang dipakai.

---

## 3. Cara Membaca Contract

Setiap *file* di dalam direktori ini memiliki peruntukannya masing-masing. Dokumen ditulis dengan standar keinsinyuran (*Software Engineering*) yang ketat. 

Beberapa poin penting saat membaca:
- **Contract Level:** Beberapa objek akan ditandai dengan stabilitasnya, seperti:
  - `[Stable]` - Kontrak final, perubahan harus melalui proses *versioning* ketat.
  - `[Experimental]` - Masih diuji coba, bisa berubah sewaktu-waktu.
  - `[Internal]` - Hanya boleh digunakan oleh *core engine* tertentu, bukan untuk *plugin*.
  - `[Deprecated]` - Jangan digunakan lagi, sedang dalam masa transisi untuk dihapus.
- Segala spesifikasi JSON atau representasi *Dataclass* yang ada di sini bersifat absolut.

---

## 4. Urutan Membaca (Learning Path)

Agar tidak tersesat, ikutilah urutan membaca *Kitab Suci Nexa* berikut ini:

1. **`01_philosophy_and_adr.md`**  
   Pahami *mindset* sistem ini. Temukan jawaban "Mengapa Nexa dibangun seperti ini?" beserta catatan keputusan (*Architecture Decision Record / ADR*).
2. **`02_core_objects.md`**  
   Kamus utama Anda. Berisi definisi API secara mendetail dari setiap *Data Transfer Object (DTO)* yang lalu-lalang di dalam sistem (misal: `ExecutionPlan`, `PatchResult`).
3. **`03_state_and_events.md`**  
   Pelajari bagaimana siklus hidup (*Lifecycle*) terjadi melalui *State Machine* dan *Event Bus*, serta lihat *Sequence Diagram* untuk interaksi waktu nyata (*real-time*).
4. **`04_policies.md`**  
   Pahami aturan ketat mengenai Validasi, Ketahanan (*Retry Policy*), dan Keamanan sebelum Anda memprogram sebuah modul baru.
5. **`05_extensions.md`**  
   (Fase Lanjutan) Bagaimana cara menghubungkan Nexa dengan Telegram, *Remote Agent*, atau *plugin* dari pihak ketiga.
6. **`06_reference_architecture.md`**  
   Pusat referensi visual. Jika Anda tersesat dan hanya ingin melihat gambar skema sistem utuhnya (UML, *Dependency Graph*), buka file ini.

---

## 5. Hubungan dengan Phase 3

Dokumen Master Contract ini dilahirkan pada **Phase 3 (Enterprise Transformation & Patching)**. 
Pada fase inilah Nexa bertransformasi dari asisten obrolan biasa menjadi "Pabrik Kode" (*Code Factory*). 

Mulai Phase 3, seluruh hasil *output* AI (melalui *Transformation Engine*) akan langsung diterapkan secara otomatis ke dalam *file system* lokal (melalui *Patch Engine*). Karena risiko kerusakan sistem menjadi sangat tinggi akibat intervensi AI langsung ke file, Master Contract ini didirikan sebagai "Tembok Pelindung" (*Guardrails*). 

Setiap potongan kode yang digenerasi oleh AI wajib tervalidasi dan dibungkus kuat-kuat oleh *Contract* sebelum dieksekusi ke *disk* Anda.
