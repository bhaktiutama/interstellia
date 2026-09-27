# Rencana: tata letak menu, layar mulai, dan pilihan bahasa

Status: rencana, belum dikerjakan. Berlaku untuk seluruh aplikasi, contoh utama Copper Corn Station.

## Ringkasan

- Panel kontrol Copper Corn Station diubah dari daftar lipat yang memanjang ke bawah menjadi panel bertab: satu kelompok tampil sekaligus, tanpa gulir panjang.
- Saat dibuka, halaman menampilkan layar muat dengan progres lalu tombol Mulai. Bantuan tidak lagi tampil otomatis; dibuka lewat tombol ? atau F1 sebagai jendela bertab.
- Empat bahasa: Indonesia (awal), English, 日本語, 中文 (简体). Pilihan disimpan dan berlaku di menu utama, Copper Corn Station, dan Gargantua.

## Masalah sekarang

| Bagian | Kondisi | Akibat |
| --- | --- | --- |
| Panel kontrol (kanan atas) | 6 kelompok `<details>`, 3 terbuka sejak awal, 35 tombol dan slider berderet ke bawah | Harus gulir panjang, bagian Grafik dan Audio di paling bawah sulit dicapai, menutupi layar |
| Layar mulai | Kartu bantuan 25 baris tombol + deskripsi tahap yang panjang muncul setiap kali dibuka | Pengguna harus gulir sampai tombol Mulai; saat masih memuat, tidak ada tanda progres |
| Proses muat | Seluruh stasiun dibangun sekaligus dalam satu blok skrip (sekitar 6-7 s di sandbox) | Halaman tampak beku tanpa keterangan |
| Bahasa | Semua teks UI dalam bahasa Indonesia, ditulis langsung di HTML dan di sekitar 40 tempat di JS | Tidak bisa diganti bahasa |

## A. Panel kontrol bertab

| Tab | Isi (dari panel sekarang) |
| --- | --- |
| Lokasi | Tombol 1-9, lift, kamera luar, dalam grid 2 kolom yang padat |
| Waktu | Slider jam, kecepatan waktu, orbit Saturnus, cuaca |
| Fisika | Slider lempar dan jatuh, tombol Lempar/Jatuhkan, hasil dan tabel |
| Foto dan tur | Mode foto, tur sinematik |
| Grafik | Preset, vegetasi, efek layar, sunrays, daun, pejalan kaki, burung, bayangan |
| Suara | Suara, musik, pilih file musik |
| Pengaturan | Bahasa, info versi dan tahap, tombol bantuan |

Rancangan:

| Item | Desktop | Ponsel (lebar < 640 px) |
| --- | --- | --- |
| Letak | Kanan atas, lebar 300 px | Lembar bawah (bottom sheet) setinggi maks 55% layar |
| Tab | Baris ikon + label pendek di atas isi | Baris ikon di bawah, isi di atasnya |
| Tinggi | Maks 60% layar, gulir hanya di dalam tab bila perlu | Sama |
| Buka/tutup | Klik judul panel, dan tombol baru ` (backtick) | Tombol Uji yang sudah ada |
| Ingat tab terakhir | localStorage | localStorage |

Tambahan kecil:
- HUD kiri atas punya mode ringkas (jam, zona, FPS saja) dan mode lengkap; klik judul HUD untuk berganti. Semua isi HUD tetap ada.
- Pesan hasil (labResult) dipindah menjadi notifikasi singkat di bawah tengah (hilang sendiri 4 s), sehingga tetap terlihat walau tab lain yang terbuka. Hasil lempar bola tetap tercatat di tab Fisika.

## B. Layar mulai dan bantuan

Alur baru:

| Langkah | Tampilan |
| --- | --- |
| 1. Memuat | Judul, garis progres, nama tahap yang sedang dimuat (tanah, kota, vegetasi, lalu lintas, burung, shader), pilihan bahasa di pojok |
| 2. Siap | Garis progres diganti tombol Mulai besar, pilihan preset grafik (Ultra sampai Hemat) dan bahasa, tautan kecil "Kontrol dasar" dan "Kembali ke menu utama" |
| 3. Main | Tidak ada bantuan otomatis. Petunjuk 1 baris muncul 6 s: "WASD berjalan, mouse melihat, ? bantuan" |
| Bantuan (? atau F1) | Jendela bertab: Dasar, Transportasi, Kamera dan foto, Waktu dan cuaca, Grafik, Pesawat. Tiap tab pendek, tanpa gulir di desktop |

Cara membuat progres muat nyata:
- Skrip sudah berupa modul, jadi bisa diberi `await` di tingkat atas. Di antara blok pembangunan besar (sekitar 10 titik) disisipkan jeda satu frame agar layar sempat menggambar progres. Urutan kode tidak berubah.
- Shader dikompilasi sebelum tombol Mulai aktif (`renderer.compileAsync`), sehingga tidak ada patah-patah pada detik pertama. Perlu diuji di M1.
- Bobot tiap tahap diukur sekali, disimpan sebagai konstanta, supaya garis progres bergerak merata.
- Deskripsi riwayat tahap yang panjang dipindah ke tab Pengaturan (info versi).

## C. Pilihan bahasa

| Kode | Bahasa | Catatan |
| --- | --- | --- |
| id | Indonesia | Bahasa sumber dan awal |
| en | English | |
| ja | 日本語 | Istilah fisika: コリオリの力, 人工重力 |
| zh | 中文 (简体) | Asumsi: Mandarin aksara sederhana. Istilah: 科里奥利力, 人工重力 |

Cara kerja:
- Satu kamus per halaman: `I18N = { id: {...}, en: {...}, ja: {...}, zh: {...} }` dan fungsi `t('kunci', {nilai})`. Teks statis di HTML diberi atribut `data-i18n`, diisi ulang saat bahasa diganti tanpa memuat ulang halaman.
- Teks yang dibuat di JS (pesan panel, prompt aksi, plakat, keterangan tur, label tombol yang berubah) memakai `t()`.
- Angka memakai `Intl.NumberFormat` sesuai bahasa (id: 1.000,5 · en: 1,000.5 · ja/zh: 1,000.5). Satuan tetap metrik.
- Pilihan disimpan di localStorage `lazarus.lang`. Menu utama juga meneruskan `?lang=xx` ke experience, karena saat dibuka sebagai file lokal (file://) perilaku localStorage berbeda antar browser. Awal: bahasa browser bila salah satu dari empat, selain itu Indonesia.
- Huruf: daftar font ditambah cadangan CJK dari sistem (Hiragino Sans, Yu Gothic, PingFang SC, Microsoft YaHei, Noto Sans CJK). Tidak mengunduh font besar.
- Tata letak diuji untuk teks Inggris (lebih panjang) dan CJK (lebih pendek tapi lebih tinggi).

Cakupan teks (perkiraan, jumlah pasti dihitung saat ekstraksi):

| Halaman | Perkiraan jumlah teks |
| --- | --- |
| Menu utama | 15 |
| Copper Corn Station: panel, HUD, bantuan, foto, tur | 150-200 |
| Copper Corn Station: pesan, prompt aksi, plakat, papan terminal | 100-150 |
| Gargantua | 15-20 |

Yang tidak diterjemahkan: komentar kode dan dokumen (tetap bahasa Indonesia sesuai aturan kerja), nama tempat orisinal (Copper Corn Station, Kestrel KS-07), tulisan di dalam dunia 3D seperti papan nama halte dan plakat gedung (tekstur kanvas; bisa menyusul sebagai tahap terpisah).

Kualitas terjemahan: teks Inggris, Jepang, dan Mandarin dibuat oleh Claude. Keterangan fisika (tur, plakat air mancur) sebaiknya dibaca ulang oleh penutur asli; daftar teks per bahasa akan disiapkan dalam satu tabel agar mudah diperiksa.

## Urutan kerja

| Tahap | Isi | Biaya | Uji |
| --- | --- | --- | --- |
| M1 | Layar muat dengan progres, tombol Mulai, bantuan tidak otomatis, jendela bantuan bertab | Rendah | Halaman termuat, progres naik sampai 100%, tombol Mulai muncul, bantuan tertutup |
| M2 | Panel kontrol bertab (desktop dan lembar bawah ponsel), HUD ringkas, notifikasi | Sedang | Semua tombol lama masih ada dan berfungsi (uji lama tetap lulus), tab berpindah, tidak ada gulir halaman |
| M3 | Infrastruktur bahasa dan ekstraksi semua teks, Indonesia + English | Sedang | Tidak ada kunci kosong, ganti bahasa tanpa memuat ulang, tidak ada teks meluber |
| M4 | 日本語 dan 中文, font cadangan CJK, menu utama dan Gargantua | Rendah-sedang | Sama dengan M3 untuk 4 bahasa |

Uji otomatis baru `tools/uji_menu_bahasa.py`: progres dan tombol Mulai, semua tab panel, kelengkapan kamus (setiap kunci ada di 4 bahasa), elemen dengan teks lebih lebar dari wadahnya per bahasa. Skrip uji lama yang mencari teks Indonesia akan dipastikan tetap lulus (bahasa awal di uji = id).

## Keputusan yang perlu dikonfirmasi

| No | Pertanyaan | Usulan awal |
| --- | --- | --- |
| 1 | "Menu yang ke bawah terus" = Panel kontrol di kanan atas Copper Corn Station (dan kartu bantuan)? | Ya, keduanya |
| 2 | Mandarin: aksara sederhana (简体) atau tradisional (繁體)? | Sederhana |
| 3 | Pilih preset grafik di layar mulai? | Ya, dengan preset terakhir sudah terpilih |
| 4 | Aturan CLAUDE.md "bahasa Indonesia untuk teks UI" diubah menjadi "Indonesia sebagai bahasa sumber, UI 4 bahasa lewat kamus" | Ya, diubah saat M3 |

## Risiko

- Menyisipkan `await` di skrip pembangunan: fungsi yang dipanggil sebelum tombol Mulai (event, `requestAnimationFrame`) harus menunggu dunia selesai. Loop `frame` baru dimulai setelah muat selesai.
- Ekstraksi ratusan teks bisa membuat teks lama berubah tanpa sengaja. Mitigasi: kamus Indonesia dibuat dari teks yang ada apa adanya, dan uji lama dijalankan setelah tiap tahap.
- Font CJK sistem berbeda antar perangkat (Windows vs macOS); ukuran baris diberi ruang lebih.
