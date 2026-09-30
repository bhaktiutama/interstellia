# Rencana M3 Millar's World: Shuttle KS-07 dan Misi Suar

Per 30 September 2026 · Status: M3a selesai (lihat "Status M3a"), berikutnya M3b

## Ringkasan

- M3 memberi alur permainan: tiba di samping shuttle KS-07 yang mendarat di air, menjelajah, lalu naik dan lepas landas sebelum gelombang raksasa tiba.
- Shuttle memakai modul bersama pertama `shared/kestrel.js` (geometri sama persis dengan Copper Corn Station), ditambah kaki pendarat.
- Desain shuttle akan diganti ke KS-07 v2b (kotak, simetris, dua tingkat): konsep di `docs/app/konsep-ks07-v2.md`, menunggu persetujuan. M3b dikerjakan setelah model v2 terpasang.
- Dibagi 3 tahap: M3a shuttle mendarat, M3b naik dan terbang, M3c misi suar. Pandangan orbit dan sinematik kedatangan tetap di M4.

## Tahapan

| Tahap | Isi | Yang diuji pemilik |
| --- | --- | --- |
| M3a Shuttle mendarat | Modul bersama `shared/kestrel.js` (Copper ikut memakainya, geometri identik), KS-07 berdiri di air dangkal di samping titik awal dengan kaki pendarat tiga titik bertapak lebar, perut sekitar 1,5 m di atas muka air rata-rata (bisa berjalan di bawahnya, sisa 0,6 m di atas mata), shading seperti laut (langit mendung, pantulan langit, bagian basah lebih gelap, kabut), lampu navigasi dan strobo, riak di kaki, kaki menahan pemain, jarak di HUD | Tampilan shuttle di bawah langit mendung, skala terhadap pemain |
| M3b Naik dan terbang | E di dekat pintu samping = naik (tombol aksi Copper). Kokpit dari Copper dipindah ke modul bersama. Lepas landas vertikal (mesin angkat, semburan air dan kabut di bawah perut, suara mesin), lalu terbang dengan tombol pesawat Copper (W/S, A/D, R/F, Z/C, mouse, Shift, X, V, E, L). Mendarat lagi di air (kaki keluar, E). Bila gelombang tiba saat shuttle masih di air: tersapu seperti pemain. Lolos di atas puncak gelombang = "selamat", catat waktu di luar yang terpakai | Rasa lepas landas, kendali terbang, ketegangan balapan dengan gelombang |
| M3c Misi suar | Suar pendarat misi sebelumnya (desain orisinal: tiang pelampung, lampu berkedip, kotak data) 1-2 km dari titik awal. Penanda arah dan jarak di HUD, E ambil kotak data, kembali ke shuttle dan lepas landas. Skor = tahun di luar yang terpakai (makin sedikit makin baik). Bisa dimatikan di panel (mode jelajah) | Tujuan permainan, keterbacaan penanda |
| M4 (konsep) | Pandangan orbit, sinematik kedatangan, penyelarasan dengan menu | Keseluruhan |

## Keputusan (dipakai pilihan yang disarankan, masih bisa diganti)

| No | Pertanyaan | Pilihan | Dipakai |
| --- | --- | --- | --- |
| 1 | Titik awal | a. Di samping shuttle (konsep, disarankan) · b. Di dalam kokpit | a |
| 2 | Tersapu saat shuttle belum lepas landas | a. Kembali ke titik awal dengan penalti waktu, shuttle ikut kembali (disarankan) · b. Misi gagal, mulai ulang | a |
| 3 | Kokpit | a. Kokpit Copper dipindah ke modul bersama (disarankan) · b. Kokpit baru khusus Millar | a |
| 4 | Setelah lepas landas | a. Terbang bebas rendah sampai sekitar 3 km, orbit menyusul di M4 (disarankan) · b. Langsung sinematik ke orbit | a |
| 5 | Misi suar | a. Masuk di M3c, bisa dimatikan (disarankan) · b. Murni menjelajah | a |

## Catatan teknis

| Hal | Keputusan |
| --- | --- |
| Modul bersama | Skrip biasa (bukan modul ES) yang memasang `window.KESTREL`, dimuat dengan `<script src="../../shared/kestrel.js">` sebelum skrip modul. Modul ES tidak bisa diimpor dari file:// (aturan CORS peramban), jadi pola ini sama dengan aset motor Copper |
| Identitas geometri | Sidik jari atribut (posisi, normal, warna, indeks) badan, bagian, dan cahaya mesin sama persis sebelum dan sesudah pemindahan; diuji di `tools/uji_millar.py` dengan angka dari Copper |
| Material di Millar | Shader sendiri (bukan MeshLambert) agar cahaya, kabut, dan lengkung planet sama dengan laut |
| Tabrakan | M3a hanya kaki (lingkaran tapak + 0,3 m). Badan cukup tinggi untuk dilewati |

## Risiko

| Risiko | Penanganan |
| --- | --- |
| Shuttle terlalu terang atau terlalu putih di bawah langit mendung | Shading dari `uAmb` suasana; pemilik menilai visual, angka mudah disetel di `shipMat` |
| Kokpit Copper bergantung pada kode Copper (layar, suara) | Dipindah bertahap seperti geometri: sidik jari sebelum dan sesudah |
| Fisika terbang di 1,3 g | Percepatan mesin angkat dihitung dari 1,3 g (bukan angka Copper di orbit) |

## Status M3a

Selesai 30 September 2026.

| Bagian | Isi |
| --- | --- |
| Modul bersama | `shared/kestrel.js`: `KESTREL.build(THREE)` (geometri shuttle, sama persis dengan Copper tahap 11d), `KESTREL.gear(THREE, padDrop)` (kaki pendarat), `mergeColored`, profil `W` / `HT` / `HB` |
| Copper | `SHUTTLE = window.KESTREL.build(THREE)`; sidik jari 8 mesh shuttle pemain dan AI sama persis sebelum dan sesudah, uji spaceport lulus (pintu, gerbang B1, lepas sandar, sandar otomatis) |
| Posisi | 30 m dari titik awal, 60 derajat ke kanan dari arah pandang awal (ekor terlihat di tepi kanan, arah datang gelombang tetap terbuka) |
| Kaki pendarat | Hidung + dua utama, tabung atas, batang teleskop krom, kerah kuning, penopang diagonal, tapak lebar 1,5 m; tapak tertinggi menyentuh dasar laut |
| Shading | Langit mendung dari atas, pantulan laut dari bawah, pantulan cubemap langit dengan Fresnel, jendela kokpit mengilap, bagian dekat muka air lebih gelap dan basah, kabut, ikut lengkung planet |
| Lampu | Merah (kiri), hijau (kanan), strobo putih berkedip tiap 1,3 s |
| Air | Riak dan buih kecil di kaki tiap 0,6-0,9 s bila di dekat pemain |
| HUD | Baris "Shuttle KS-07" (jarak) |

Perbaikan lama yang ditemukan saat pengecekan: cincin laut jauh (70 m sampai cakrawala) punya urutan segitiga terbalik sejak R1, sehingga dibuang backface culling. Dari tampilan jalan kaki hampir tidak terlihat (yang tampak adalah langit di bawah cakrawala), tetapi dari drone laut hanya berupa lingkaran 70 m. Kini laut jauh tergambar sampai cakrawala.

Uji: `tools/uji_millar.py` kini 50 pemeriksaan, semua lulus, termasuk: sidik jari geometri KS-07 sama dengan Copper, celah tapak ke dasar laut 0,00-0,04 m, perut 1,55 m di atas muka air rata-rata (mata 0,95 m), pemain yang berjalan ke kaki tertahan di 1,07 m dari pusat tapak (batas 1,05 m), normal laut jauh ke atas, render dengan shuttle di layar tanpa nilai tidak valid atau titik menyala. Copper: `tools/uji_spaceport.py` lulus tanpa error.

Belum: gelombang raksasa melewati shuttle tanpa efek (shuttle tertutup dinding air lalu tampak lagi); ditangani di M3b bersama lepas landas.

Berikutnya M3b: naik (E), kokpit bersama, lepas landas dan terbang, balapan dengan gelombang.
