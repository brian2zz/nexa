# Nexa AI Prompting Guide: Generating Modules with DSL Spec

Dokumen ini menjelaskan cara menggunakan **Nexa DSL Specification** untuk memerintahkan AI (ChatGPT/Claude/Gemini) agar menghasilkan modul Nexa yang sempurna.

---

## 1. The "Base Context" Prompt
Gunakan prompt ini sebagai pembuka saat Anda berdiskusi dengan AI tentang Nexa:

> "Saya sedang mengembangkan proyek menggunakan **Nexa Framework**. Nexa adalah schema-driven engine yang menggunakan YAML sebagai spesifikasi DSL. Berikut adalah spesifikasi teknisnya: [Tempel isi docs/dsl_spec.md di sini]. Tolong pahami aturan penamaan, tipe data, dan struktur CRUD-nya."

---

## 2. Example Task: Generating a Complex Module
Setelah AI memahami spek tersebut, Anda bisa memberikan perintah seperti ini:

> "Buatlah skema `nexa.yaml` untuk modul **Inventory Management**. Aturannya:
> 1. Ada model `Warehouse` (name, location).
> 2. Ada model `StockItem` (product_id, quantity, warehouse_id sebagai foreignkey).
> 3. Aktifkan CRUD untuk keduanya.
> 4. Di `StockItem`, buat tabel agar bisa di-search berdasarkan `product_id` dan di-sort berdasarkan `quantity`.
> 5. Gunakan tipe data yang sesuai dengan Nexa DSL Spec."

---

## 3. How AI Interprets the Spec (Internal Logic)
Dengan membaca **Nexa DSL Spec**, AI akan secara otomatis melakukan hal berikut:

1. **Mapping Database**: Ia tahu bahwa `foreignkey` akan diterjemahkan menjadi `ForeignKey` di Django dan `select` di Frontend.
2. **Deterministic Naming**: Ia akan memberi tahu Anda bahwa file yang dihasilkan nantinya adalah `stock_item.py` (Backend) dan `StockItemList.vue` (Frontend).
3. **Registry Awareness**: Ia akan menyarankan Anda untuk mengecek log generator `api.backend_service` dan `crud.list_page` untuk memverifikasi hasilnya.

---

## 4. Prompt for Custom Generators
Anda bahkan bisa meminta AI membuatkan Generator baru:

> "Berdasarkan Nexa DSL Spec, buatkan saya sebuah Generator Python baru dengan kategori `extension`. Tujuannya adalah men-generate file **PDF Report Template** untuk setiap model yang memiliki metadata `report: true`. Gunakan decorator `@nexa_generator` dengan prioritas `PRIORITY_EXTENSION + 100`."

---

## Kesimpulan
Nexa DSL Spec mengubah AI dari sekadar "chatbot" menjadi **Arsitek Nexa**. Ini akan mempercepat development Anda hingga 10x lipat karena AI tidak perlu lagi menebak-nebak struktur folder atau nama variabel.
