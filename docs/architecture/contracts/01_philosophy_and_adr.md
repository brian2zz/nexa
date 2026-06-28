# Filosofi & Architecture Decision Records (ADR)

Dokumen ini adalah **"Kitab Suci"** arsitektur Nexa. Jika Anda ingin mengubah atau menambahkan sesuatu ke dalam inti (*core*) sistem Nexa, Anda harus memastikan bahwa perubahan tersebut selaras dengan filosofi yang tertulis di sini. Jika tidak, desain Anda akan menjadi *Anti-Pattern*.

---

## 1. Golden Rules (10 Commandments Nexa)

Aturan-aturan di bawah ini adalah hukum mutlak yang mengikat seluruh komponen arsitektur Nexa. Tidak ada pengecualian.

1. **Rule 1:** *Engine* hanya memiliki **satu tanggung jawab** (Single Responsibility).
2. **Rule 2:** *Engine* **tidak boleh** mengetahui implementasi *Engine* lain.
3. **Rule 3:** *Engine* hanya menerima komunikasi berupa **Contract** (DTO resmi).
4. **Rule 4:** *Engine* hanya mengembalikan komunikasi berupa **Contract** (DTO resmi).
5. **Rule 5:** *Engine* **tidak boleh** mengubah Contract milik *Engine* lain (*Immutable*).
6. **Rule 6:** Semua komunikasi harus **deterministic** dan dapat diprediksi.
7. **Rule 7:** *Large Language Model (LLM)* **hanya** berada dan dieksekusi di *Transformation Layer*.
8. **Rule 8:** Kesalahan (*Error*) tidak boleh membuat *crash* sistem; harus di-*catch* dan dikonversi menjadi *Event* atau *Result* dengan status `FAILED`.
9. **Rule 9:** *Provider* (Groq, OpenAI, Ollama) dilarang keras bocor hingga ke lapisan inti bisnis (*Core Logic*).
10. **Rule 10:** Setiap modifikasi *File System* harus melewati mekanisme persetujuan (*Approval Engine*).

---

## 2. Filosofi Inti: Immutable Contract

Setiap *Data Transfer Object* (DTO) atau *Result Object* yang menjembatani komunikasi antar *engine* (misalnya dari `Transformation Engine` ke `Patch Engine`) dirancang berlandaskan filosofi **Immutable Contract**.

### Mengapa Immutable? Mengapa Bukan Mutable?
Dalam sistem AI berskala besar, data bergerak ibarat di atas ban berjalan (*conveyor belt*) melalui serangkaian *Pipeline* (Fase 1 hingga Fase 6).

- **Mutable (Bisa diubah):** Jika objek seperti `ExecutionPlan` atau `TransformationResult` bisa diubah di tengah jalan oleh *engine* lain, maka melacak *bug* (observabilitas) menjadi mimpi buruk. Anda tidak akan pernah tahu *engine* mana yang merusak format JSON atau menghapus atribut penting sebelum data itu sampai ke ujung pipa.
- **Immutable (Tidak bisa diubah):** Dengan membuat objek komunikasi ini statis (tidak berubah setelah diinisialisasi), setiap *engine* dipaksa menjadi *pure function* (Fungsi Murni). Mereka menerima data yang mutlak, memprosesnya, dan menghasilkan *objek baru* tanpa pernah mengotori *state* aslinya.

### Tradeoff & Keuntungan
- **Tradeoff:** Penggunaan memori sedikit lebih besar karena sistem harus membuat objek/salinan baru (misal `PatchResult` lahir murni dari olahan `TransformationResult`, bukan memodifikasinya). Hal ini terkadang membuat kode terasa panjang (*boilerplate*).
- **Keuntungan:** Keamanan absolut. Jika terjadi *error* pada tahap *Patching*, *engine* bisa melakukan *Rollback* dengan seketika ke *state* sebelumnya karena objek aslinya (`TransformationResult` dan `ExecutionPlan`) masih utuh tak tersentuh. 

---

## 3. Anti-Pattern

Hindari melakukan kesalahan-kesalahan arsitektur di bawah ini. *Developer* sering kali tergiur untuk mengambil "jalan pintas", namun jalan pintas ini akan merusak modularitas Nexa.

> **❌ Anti-Pattern 1: Planner merangkap Eksekutor**
> ```mermaid
> graph LR
>     Planner -->|Tulis file langsung| FileSystem
> ```
> *Mengapa salah?* Planner hanya bertugas menganalisa dan membuat rencana (`ExecutionPlan`). Menulis *file* adalah tugas `Execution Engine`.

> **❌ Anti-Pattern 2: Kebocoran Provider ke Layer Eksekusi**
> ```mermaid
> graph LR
>     PatchEngine -->|Memanggil Groq API| Provider
> ```
> *Mengapa salah?* Patch Engine harus murni deterministik. AI (halusinasi, ketidakpastian LLM) tidak boleh ada di luar lingkup `Transformation Engine`.

> **❌ Anti-Pattern 3: AI Menulis File Langsung**
> ```mermaid
> graph LR
>     TransformationEngine -->|Menulis kode| FileSystem
> ```
> *Mengapa salah?* Transformation Engine hanya mengubah spesifikasi menjadi kode (*pure transformation*). Penulisan fisik harus melalui jembatan kontrak (`Patch Engine`) yang memvalidasinya.

---

## 4. Architecture Decision Records (ADR)

ADR mendokumentasikan setiap keputusan desain kritis dalam pengembangan Nexa.

### ADR-001: Planner Tidak Boleh Menulis File
- **Status:** Accepted
- **Reason:** Tugas *Planner* murni *decision-making* (menyusun `ExecutionPlan`). Membiarkan *Planner* menulis *file* akan melanggar *Single Responsibility Principle*.
- **Consequences:** Eksekusi penulisan dipindahkan secara absolut ke `Execution Engine`.

### ADR-002: Engine Harus Bersifat Provider Agnostic
- **Status:** Accepted
- **Reason:** Ekosistem AI bergerak cepat (Groq, OpenAI, Llama, DeepSeek). Jika arsitektur terikat pada satu *provider*, sistem menjadi tidak *scalable*.
- **Consequences:** Semua interaksi AI disembunyikan di balik antarmuka abstrak `LLMProvider`.

### ADR-003: Graceful Failure atas Halusinasi LLM
- **Status:** Accepted
- **Reason:** LLM sering mengabaikan instruksi format Markdown/JSON. *Crash* sistem akibat *output* AI yang kotor akan merusak UX.
- **Consequences:** Menerapkan `ResponseProcessor` internal dan *Retry Policy* di `TransformationEngine` sebelum melempar *error*.

### ADR-004: Transformation Engine Tidak Menulis File
- **Status:** Accepted
- **Reason:** Memastikan AI murni bertindak sebagai "Pabrik Kode" (menghasilkan transformasi text-to-text). Interaksi *file system* terlalu berbahaya untuk disatukan dengan proses halusinatif.
- **Consequences:** Eksekusi fisik didelegasikan ke `Patch Engine` dan `Execution Engine`.

### ADR-005: Patch Engine Tidak Menggunakan AI
- **Status:** Accepted
- **Reason:** Proses modifikasi kode (*Patching*) harus 100% *deterministic* (misal: Cari *String A*, ganti dengan *String B*). Tidak boleh ada ruang untuk halusinasi LLM di fase ini.
- **Consequences:** Algoritma internal `PatchEngine` hanya mengandalkan metode klasikal seperti *Search-and-Replace* blok atau *Unified Diff Parser*.

### ADR-006: Approval Selalu Terjadi Sebelum Execution
- **Status:** Accepted
- **Reason:** Sekalipun Nexa dijalankan dalam mode otonom (Autonomous Mode), *approval* (persetujuan) harus tetap menjadi lapisan (*layer*) terpisah yang dilalui oleh data.
- **Consequences:** Otonomi hanya berarti *Approval Engine* menekan "Yes" secara algoritmik, namun pos pemeriksaannya tetap eksis.

### ADR-007: Engine Berkomunikasi Melalui Contract
- **Status:** Accepted
- **Reason:** *Developer* dilarang memanggil `PatchEngine` secara langsung tanpa parameter standar. Contract memaksa standarisasi.
- **Consequences:** Setiap pergerakan antar komponen harus diinisiasi dan direspons menggunakan Data Transfer Object (`TransformationRequest`, `PatchResult`, dll.).

### ADR-008: Provider Tidak Boleh Bocor ke Core
- **Status:** Accepted
- **Reason:** Mencemari kode logika inti dengan *statement* seperti `if provider == "groq"` akan membuat kode menjadi kotor (*spaghetti code*).
- **Consequences:** *Logic provider-specific* harus ditangani secara penuh di kelas turunan di dalam `providers/` folder.

### ADR-009: Event Driven Architecture
- **Status:** Accepted
- **Reason:** Fleksibilitas integrasi. Jika *frontend* CLI, antarmuka web, ekstensi VSCode, Telegram Bot, atau *Remote Agent* ingin mengetahui *progress* sistem, mereka tidak perlu melakukan *polling*.
- **Consequences:** *Engine* hanya perlu melemparkan *event* (`BeforeTransformation`, `AfterPatch`), dan siapapun bisa men-*subscribe* *event* tersebut.
