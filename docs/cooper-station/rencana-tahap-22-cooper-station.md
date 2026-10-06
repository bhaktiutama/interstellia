# Rencana Tahap 22 Copper Corn Station: keragaman kota (pusat terasa padat dan hidup)

Per 6 Oktober 2026 · Bhakti

## Ringkasan

- Masalah: pusat kota terasa kosong di sekitar gedung tinggi. Penyebabnya bukan tinggi gedung, tapi lantai dasar: tiap blok menara = satu podium 2 lantai seragam (warna dan etalase sama) di tengah blok dengan pelataran kosong di sekeliling, tanpa dinding jalan yang menerus, tanpa detail menonjol, dan jalan lokal tanpa orang, perabot, atau mobil parkir.
- Acuan: foto pusat New York (dinding jalan bata dan batu menerus, toko berpapan nama di lantai dasar, tangga darurat besi, AC jendela, lis atap, pohon jalan, mobil parkir, orang rapat).
- Isi: 22a fasad klasik (bata, batu, lis), 22b tata blok pusat (dinding jalan kavling sempit, menara batu bertingkat), 22c detail 3D lantai dasar dan fasad, 22d isi jalan lokal (mobil parkir, orang, perabot). Uji otomatis dijalankan bersama test suite setelah V5 (permintaan pemilik).

Urutan kerja: 1) 22a + 22b (satu langkah, fasad tanpa tata blok tidak terlihat), 2) 22c, 3) 22d (ketiganya selesai, menunggu uji pemilik), 4) 22e bersama test suite setelah V5, lalu lanjut V2 rencana realisme visual.

## Penyebab di kode (terukur dari kode, bukan perkiraan)

| Keluhan | Penyebab | Lokasi (cari nama) |
| --- | --- | --- |
| Kosong di sekitar gedung tinggi | Blok pusat (sel 241,7 x 250 m dibagi 4 x 4, blok sekitar 46 m) = podium `w = bw x 0,7-0,9` di tengah + menara di atasnya. Celah 2,3-7 m tiap sisi + 2 m tepi blok, jadi muka jalan mundur dan podium cuma 7-10 m | loop isi blok kota, cabang `cls === 'pusat'` |
| Lantai dasar seragam | Semua podium gaya 11 dengan etalase modul 2,6 m dan pita gelap yang sama; warna dari 6 warna `COLS.mid` | `BUILD_FS` bagian "lantai dasar: etalase kaca" |
| Menara mirip semua | Menara memakai warna `COLS.tower` = gaya 1 kaca (variasi 21d hanya ukuran kaca dan warna) | `building()` (gaya dari warna) |
| Jalan lokal sepi | Perabot (`FURN`), pohon jalan, kafe, dan rute pejalan kaki hanya di arteri dan plaza; jalan lokal hanya hidran di simpang | `FURN` langkah 1-4, `PEDS` langkah 1-2, `VIBE` kafe |
| Tidak ada mobil parkir | `TRAFFIC` hanya mobil bergerak di arteri dan boulevard | `TRAFFIC` |

## Langkah

| Langkah | Isi | Effort | Model | Thinking | File / fungsi |
| --- | --- | --- | --- | --- | --- |
| 22a | Fasad klasik di shader: gaya 12 bata (walk-up: bata per buah, nat terang, noda turun, jendela tegak berambang batu, palang jendela sorong, deret toko berpapan nama berhuruf, papan menyala malam), gaya 13 batu (batu potong, spandrel gelap = garis tegak art deco, lobi 5 m), gaya 14 lis atap (kotak tipis menonjol 0,45 m) | High | Opus 5.5 | high | `BUILD_FS` (parameter gaya, bahan, ambang, toko, pita), peralatan atap |
| 22b | Tata blok pusat: 70% blok menara jadi dinding jalan (kavling 6-26 m menempel di tepi blok, 3-15 lantai, campuran bata 50%, batu 18%, apartemen 16%, kantor 10%, toko 6%), menara turun ke tanah (puncak sama); 35% menara di atas 45 m jadi batu bertingkat mundur; 35% gedung berjajar pusat jadi kantor batu; 40% deret menengah jadi bata. Generator acak sendiri, bangunan baru di akhir daftar | High | Opus 5.5 | high | `RAGAM`, `ragamWall()`, `ragamTower()`, `ragamCornice()`, `BUILD_LATE`, `building()` |
| 22c | Detail 3D dekat pemain (LOD radius seperti `FURN`): kanopi kain di atas toko, papan nama menonjol, tangga darurat besi di muka bata, AC jendela, tangki air kayu sudah ada | Medium | Sonnet 5.5 | medium | blok baru setelah `FURN`, data muka jalan dari `ragamWall()` |
| 22d | Isi jalan lokal pusat dan menengah: mobil parkir statis di tepi jalan lokal, rute pejalan kaki di trotoar jalan lokal, tempat sampah, rak sepeda, pot | Medium (pejalan kaki: High) | Sonnet 5.5 / Opus 5.5 | medium / high | `FURN`, `PEDS` (generator acak sendiri di akhir), mobil parkir InstancedMesh baru |
| 22e | Uji `tools/uji_keragaman.py`: kavling tidak menimpa jalan, trotoar, kafe, atau halte; `?ragam=0` identik dengan sebelum 22; tanpa nilai tidak valid siang dan malam; jumlah draw call dan segitiga bayangan | Medium | Sonnet 5.5 | medium | `tools/` (dijalankan bersama test suite setelah V5) |

## 22a + 22b: aturan yang dijaga

| Aturan | Cara |
| --- | --- |
| Urutan acak kota lama tidak bergeser | Semua pilihan baru dari `r22()` (generator sendiri). Cabang podium menghitung angka lama dalam urutan yang sama (warna, tinggi podium, warna podium, tinggi menara, posisi dan ukuran menara) |
| Peralatan atap gedung lama tetap | Bangunan baru dicatat di `BUILD_LATE` dan masuk `BUILD` sesudah semua bangunan lama. Menara yang turun ke tanah dan tingkat dasar menara batu tetap di urutan lama dengan lebar, dalam, dan puncak sama. Podium lama (gaya 11) memang dilewati peralatan atap. Deret yang diganti bata tetap memakai angka acak tangki air kayu (gaya 12 ikut gaya 2) |
| Perbandingan | `?ragam=0` = kota persis seperti sebelum tahap 22 |
| Kafe dan pejalan kaki arteri | Muka arteri mundur 3,6 m (kafe 18,6 m dari as arteri, pejalan kaki 14,3-16,3 m, tepi blok 17 m, kavling mulai 20,6 m) |
| Jalan lokal | Kavling tepat di tepi blok: 7 m dari as jalan lokal (trotoar sampai 6,5 m, hidran 5,8 m), dinding ke dinding 14 m |
| Menara dan kavling | Kavling yang menghadap menara dipendekkan sampai menyentuh menara + 0,6 m (tanpa muka sebidang, tanpa z-fighting); bila sisa < 4 m, menara langsung menghadap jalan |
| Lis atap | Kotak 0,9 m lebih lebar, 0,7 m tinggi, puncak 0,15 m di atas atap (tidak sebidang dengan atap). Tidak masuk peta, tidak berkolider, tanpa peralatan atap |
| Tingkat atas menara batu | Shader membaca tinggi dunia (`1000 - length(vW.xy)`): tingkat yang tidak berdiri di tanah tidak memakai lobi; lampu penanda atap > 90 m memakai tinggi dunia |

## Hasil 22a-22d (terukur di sandbox SwiftShader, preset Tinggi)

| Item | Sebelum | Sesudah |
| --- | --- | --- |
| Blok menara pusat jadi dinding jalan | 0 | 46 blok, 500 kavling |
| Menara batu bertingkat mundur | 0 | 22 |
| Gedung lama diganti gaya (deret bata, kantor batu) | 0 | 318 |
| Lis atap | 0 | 723 |
| Instance gedung `flat` | 8.037 | 9.258 (satu InstancedMesh, draw call tidak bertambah) |
| Bangunan di peta (`houseList`) | 16.692 | 17.192 |
| Muka bata dengan detail 3D | 0 | 545 muka: 1.467 lantai tangga darurat + 294 tangga turun, 1.603 AC, 1.102 kanopi, 165 papan nama menonjol |
| Mobil parkir jalan lokal | 0 | 4.814 (berkolider) |
| Collider | 44.685 | 50.018 |
| Rute / orang (`PEDS.list`) | 13.102 | 14.181 (+1.079 di trotoar jalan lokal) |
| Meja kafe trotoar | 69 | 88 (podium lama dulu menghalangi sebagian deret; urutan acak kafe ikut bergeser) |
| Perabot lama (`FURN`: bangku, tong, pot, hidran, lampu lalu lintas, zebra) | 23.190 instance | sama persis (dicek per posisi) |
| Pohon | 15.032 | 15.032 |

Cek `?ragam=0` terhadap commit sebelum tahap 22 (98b6257): daftar bangunan semua tipe, collider, pohon, jumlah orang, perabot, dan matriks peralatan atap identik (hash sama).

Perbaikan selama kerja: mobil parkir pertama mulai 18 m dari as arteri dan menutup 14 deret kafe di mulut jalan lokal; kini mulai 24 m (12 m dari tepi arteri).

## Biaya (perkiraan, belum diukur di GTX 1060 / M1)

- Instance gedung naik (kavling + lis). Semua satu InstancedMesh `flat` yang sudah ada, jadi draw call tidak bertambah. Pass bayangan memakai `SHP` (hanya instance di kotak kamera bayangan).
- Shader: cabang gaya 12 / 13 / 14 setara gaya lain (beberapa `band` dan `hash1` tambahan per piksel di lantai dasar).
- Detail 3D dan mobil parkir hanya dikirim dalam radius (tangga darurat 170 m, kanopi 220 m, AC 110 m, mobil parkir 260 m) lewat `updateFurniture()` (tiap pindah 20 m), 9 draw call baru. Kaca/roda mobil parkir tanpa bayangan; badan mobil, tangga darurat, kanopi, AC ikut pass bayangan.
- Pejalan kaki +8% rute (simulasi CPU orang jauh bergiliran 1 dari 10 per frame, seperti sebelumnya).
- Uji 22e mengukur FPS dan segitiga bayangan; angka GPU nyata tetap perlu dicek pemilik di GTX 1060 dan M1.

## Catatan

- Gaya New York generik (bata, batu, tangga darurat, tangki air kayu, lis atap) bukan desain film.
- Plaza alun-alun New York, menara ikon, pasar, balai, dan fasilitas lain tidak diubah (blok fasilitas dilewati sebelum cabang pusat).

## 22f: menara kaca di atas atap gedung rendah (permintaan pemilik)

Tujuan: mengembalikan 31 gedung kaca yang berkurang di 22b tanpa mengubah satu pun bangunan yang sudah ada. Effort Medium, Opus 5.5, high (menyentuh `BUILD_FS`).

| Aturan | Cara |
| --- | --- |
| Tidak mengubah bangunan lama | Menara hanya ditambahkan di akhir `BUILD.flat` (sesudah `BUILD_LATE`), generator acak sendiri, berdiri di atas atap (tanpa collider, tidak masuk peta) |
| Peralatan atap lama tetap | Menara 22f ditandai `e[11]`, dilewati loop peralatan biasa; ruang mesin dan unit atapnya dibuat sesudah cerobong rumah dengan generator sendiri |
| Atap yang dipakai | Atap datar puncak <= 30 m, sisi terpendek >= 16 m, gaya 0 / 2 / 11 / 12 / 13, kepadatan > 0,62, bukan fasilitas, tidak ada tingkat atau menara lain di atasnya |
| Tidak menembus | Menara tidak memotong gedung lain yang lebih tinggi dari dasarnya dan berjarak >= 6 m dari menara > 45 m lain |
| Lis atap | Di atas gedung bata / batu dasar menara +0,2 m (puncak lis +0,15 m) |
| Tinggi | Rumus menara lama: dekat CBD 60-150 m x (1 - 0,45 x jarak / 380), di luar CBD 45-85 m |
| Lobi | Lantai bawah menara kaca menyala sebagai lobi hanya bila dasarnya < 12 m dari tanah (menara lama di podium 8 m tetap) |
| Perbandingan | `?kaca=0` = kondisi tahap 22 sebelum 22f |

Hasil (sandbox): 92 atap memenuhi syarat, 31 menara dibangun (semua puncak > 45 m). Gedung kaca 77 menjadi 108 (sama dengan sebelum tahap 22), puncak > 45 m 57 menjadi 88. Dicek terhadap `?kaca=0`: 9.258 bangunan lama, 17.192 bangunan peta, 50.018 collider, dan 15.004 instance peralatan atap lama identik (hash sama).
