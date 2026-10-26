# Rencana Tahap 32 Copper Corn Station: tekstur jarak dekat (fasad, trotoar, aspal)

Per 26 Oktober 2026 · disusun atas permintaan Bhakti dari 3 foto (gedung dan trotoar, aspal, tembok bata) · status: 32a-32h diterapkan tanpa uji visual (diuji Bhakti); 32i (skrip uji) tidak dibuat atas permintaan, hanya dicek halaman termuat tanpa error dengan dan tanpa `?tekstur=lama`

## Ringkasan

- Masalah utama bukan resolusi tekstur, tetapi semua permukaan terlihat **baru, rata, dan bersih**: tanpa pelapukan, tanpa kedalaman (nat, ambang, lis hanya warna), dan pertemuan bahan terputus tajam (dinding langsung ke rumput, aspal langsung ke trotoar).
- Dua cacat yang jelas dan murah diperbaiki dulu: papan nama toko berisi balok seperti barcode (32b) dan aspal kehijauan di tepi jalan (32c, penyebab sudah ditemukan di kode).
- Semua tetap prosedural di shader (tanpa tekstur foto, tanpa addon), di belakang saklar `?tekstur=lama` yang membuat tampilan identik dengan sebelum tahap 32.

## Temuan dari foto

| Foto | Temuan | Penyebab di kode (`experiences/cooper-station/index.html`) |
| --- | --- | --- |
| 3 Tembok bata | Papan nama toko berisi balok hitam / terang seperti barcode | Pasti: `glyph` di `BUILD_FS` gaya 12 (blok "22a: deret toko") = pita `fract(u / 0.3)` dinyalakan acak per 0,3 m, bukan huruf |
| 2 Aspal | Aspal di dekat tepi rumput berubah kehijauan | Pasti: klasifikasi tanah memakai warna `uLand` (`landCanvas` 2.048 x 2.608, sekitar 3,07 m per piksel) yang disaring bilinear; piksel tepi jalan bercampur rumput, jadi `base` kehijauan dan `asphM` / `vegM` bercampur sepanjang sekitar 3 m |
| 2 Aspal | Tidak ada jejak ban, aus marka, tambalan, retak; butir agregat lemah | Shader tanah blok "jalan dan ladang dari dekat": hanya `grainN(P * 18)`, `vnoise(P / 2.5)`, noda `mdNoiseD`; marka `roadMarks()` sempurna |
| 1 Trotoar | Petak 3 m seragam, sambungan rata, tanpa retak / noda, tanpa gelap di dekat dinding | Blok "15c: trotoar kota" + petak `tid = floor(P / 3.0)` dengan `tv` 0,94-1,06 saja |
| 1 Rumah | Papan dinding tanpa bayangan bawah papan, dinding langsung masuk rumput, jendela tanpa ambang menonjol, pintu persegi gelap | `BUILD_FS` `mat == 1.0` hanya `lines(y, 0.2, 0.012)` gelap 22%; tidak ada plint |
| 3 Bata | Bata dan nat rata, warna per bata sedikit, tanpa noda turun di bawah ambang; kaca etalase hampir hitam; lis datar | `mat == 4.0` (gaya 12 sudah punya warna acak per bata dan noda kecil); `shopM` etalase gelap |
| 1 Tiang | Abu-abu polos tanpa alas | Geometri tiang lampu `LAMP` |

## Prinsip

- Pertahankan yang ada: tampilan jauh (> 60 m) dan semua preset tidak berubah kecuali yang disebut. Detail baru memudar dengan jejak piksel `fp` / `fwU` / `fwY` seperti pola yang sudah ada.
- Detail mahal hanya Ultra dan Tinggi lewat `uL_Detail` (pola V1); perbaikan cacat (32b, 32c) berlaku di semua preset.
- Shader aman untuk M1: tanpa `normalize()` vektor nol, tanpa `pow()` negatif, tanpa `sqrt()` / `asin()` di luar rentang.
- Saklar `?tekstur=lama` (`TEKS.lama`) = define yang mematikan semua cabang baru; uji membandingkan piksel dengan dan tanpa saklar terhadap commit induk.

## Langkah

| Langkah | Isi | File / fungsi | Effort | Model | Thinking |
| --- | --- | --- | --- | --- | --- |
| 32a | Saklar `?tekstur=lama` (define `TEKS_LAMA` di shader tanah dan `BUILD_FS`), titik foto acuan tetap (6 lokasi: rumah foto 1, arteri foto 2, deret bata foto 3, pusat NY, permukiman, boulevard), uji identik dengan induk | `TEKS`, `groundMat`, material gedung, `tools/uji_tekstur.py` baru | Medium | Sonnet 5.5 | medium |
| 32b | Papan nama berhuruf asli: atlas kanvas 1.024 x 256 berisi 32 kata pendek ID + EN (TOKO, ROTI, KOPI, DELI, BAKERY, APOTEK, BOOKS, 24H, nomor gedung), dipilih per toko dari `hb2`; huruf disampel dengan `textureGrad` dan memudar ke rata-rata saat `fwU` besar; neon malam memakai alfa huruf yang sama | `BUILD_FS` blok 22a (`glyph`, `neon`), uniform sampler baru di material gedung, `warmShaders()` | Medium | Sonnet 5.5 | medium |
| 32c | Aspal tanpa rona hijau: tepi jalan dari geometri analitik (lebar arteri `dS` / `dZ`, boulevard, `sidewalkD()` yang sudah ada), bukan dari warna peta; `base` aspal diganti warna aspal tetap di dalam jalan; tepi aspal ke rumput / trotoar tajam satu piksel (`lineAA`), bukan campuran 3 m | Shader tanah: klasifikasi `asphM` / `vegM` / `grayM`, juga jalan `roadZ()` dan `ROAD_DETOURS` | High | Opus 5.5 | high |
| 32d | Aspal hidup: 2 jalur ban gelap per lajur (lebih licin di `mdRough`), marka aus dan berbintik (lebih aus di jalur ban), tambalan persegi gelap, retak halus jarang, tutup saluran bulat di dekat simpang, talang gelap 0,4 m di tepi kerb | Shader tanah blok aspal, `roadMarks()` | Medium | Sonnet 5.5 | medium |
| 32e | Trotoar: lebar petak 1,5-3 m per ruas (hash per blok), sambungan potong yang lebih dalam (gelap + tonjolan `mdG`), retak jarang, noda bundar (permen karet, tetes air), gelap kotor 0,3-0,8 m di sisi dinding dan rumput, kerb dengan sisi tegak palsu (garis terang + bayangan di sisi jalan) | Shader tanah blok 15c, `SIDEWALK_GLSL` (jangan ubah `sidewalkD()` agar JS `SIDEWALK.d` tetap sama) | Medium | Sonnet 5.5 | medium |
| 32f | Pelapukan fasad (semua gaya): kaki dinding gelap dan kotor 0-1,2 m, noda turun di bawah tiap ambang jendela (mengikuti kolom jendela yang sudah dihitung), variasi warna per bata / per papan, nat bata tenggelam dan papan dinding dengan bayangan bawah papan lewat normal palsu dari turunan layar, lumut tipis di sisi teduh dekat tanah, debu di atas lis | `BUILD_FS` setelah warna dinding dasar (`mat` 1 / 3 / 4, gaya 12 dan 13), uniform `uWeather` dari `CONFIG` | High | Opus 5.5 | high (BUILD_FS besar, rawan NaN di M1) |
| 32g | Jendela dan pintu: ambang dan bingkai menonjol (bayangan palsu di bawah ambang dan sisi bingkai menurut arah cahaya `uL_SunDir`), pintu berpanel dengan pegangan, kaca etalase gaya 12 tidak hitam pekat (ruang toko sederhana memakai cara `kI` 14c atau pantulan ngarai 21e), lis dan pita batu dengan bayangan bawah | `BUILD_FS` blok jendela, 14c, 22a | Medium | Sonnet 5.5 | medium |
| 32h | Pertemuan bahan: plint beton 0,4 m di kaki rumah dan gedung (di shader, tanpa geometri), garis rumput ke trotoar dibuat tidak rata (tanah terbuka 0,1-0,3 m), alas tiang lampu (kerucut kecil di geometri `LAMP`) | `BUILD_FS`, shader tanah, rumput `CLIP_AWAY`, geometri tiang | Medium | Sonnet 5.5 | medium |
| 32i | Uji dan ukur: tanpa nilai tidak valid di 5 preset siang / malam / hujan, `?tekstur=lama` identik, papan nama berhuruf (sampel piksel), tidak ada piksel kehijauan di dalam jalan (sampel rona di 6 lokasi), waktu GPU `GPUT` sc sebelum / sesudah, `tools/ukur_muat.py cooper-station --cek` (atlas huruf tanpa program baru di frame pertama) | `tools/uji_tekstur.py`, CLAUDE.md (peta kode, riwayat) | Medium | Sonnet 5.5 | medium |

Urutan kerja: 32a, 32b, 32c (cacat, langsung terlihat), lalu 32d, 32e, 32f, 32g, 32h, lalu 32i. 32f boleh dipecah: 32f-1 kaki dinding dan noda turun (Medium), 32f-2 normal palsu nat dan papan (High).

## Perkiraan biaya

| Item | Perkiraan | Dasar |
| --- | --- | --- |
| Memori | Atlas huruf 1.024 x 256 RGBA dengan mipmap sekitar 1,4 MB | Ukuran tekstur |
| Muat | Tanpa program shader baru (hanya cabang di program yang sudah ada); atlas kanvas di bawah 20 ms | Perkiraan, diukur di 32i |
| Waktu GPU | Belum diketahui. Shader tanah dan `BUILD_FS` mendapat beberapa noise per piksel di bawah 60 m; diukur dengan `GPUT` di 32i dan di GTX 1060 / M1 oleh Bhakti | Tidak bisa diukur bermakna di SwiftShader |

## Keputusan untuk Bhakti

| Pertanyaan | Usulan bawaan |
| --- | --- |
| Seberapa kotor kota? Copper stasiun yang dirawat, jadi pelapukan ringan sampai sedang | Ringan di pusat (mega), sedang di permukiman dan kawasan tani; satu pengali `CONFIG.weather` untuk disetel saat uji |
| Bahasa papan nama | Campur ID dan EN (kota antarbangsa), tanpa merek nyata |
| Pelapukan di Hemat / Rendah | Mati (hanya 32b dan 32c yang berlaku di semua preset) |

## Batasan

- Diagnosis berasal dari 3 foto, satu waktu, satu cuaca. Distrik lain (menara kaca, pasar, tani) belum dilihat dan mungkin punya masalah lain.
- Penyebab 32b dan 32c pasti dari kode; penilaian "rata" dan "bersih" adalah penilaian visual dari foto.
- Hasil akhir dinilai Bhakti di GPU asli; sandbox hanya memeriksa error, nilai tidak valid, dan keidentikan saklar.

## Catatan penerapan (26 Oktober 2026)

| Langkah | Yang dibuat | Nama di kode |
| --- | --- | --- |
| 32a | Saklar `?tekstur=lama` = define `TEKS_LAMA` di shader tanah dan `BUILD_FS`, tanpa peta jalan, atlas, dan alas tiang | `TEKS`, `TEKS_DEF` |
| 32b | Atlas 1.024 x 512 berisi 32 kata, satu kata per toko, huruf 0,5 m; neon malam memakai huruf yang sama | `SIGN`, `BUILD_U.uSignTex`, `glyph` di blok 22a |
| 32c | Kanvas kembaran peta lahan (r = arteri, g = jalan lokal) dari pembungkus `lg.fillRect` / `fill` / `stroke`; tekstur RG8 `uRoadM`; di shader: jarak ke tepi = (cakupan - 0,5) x 3,07 m, dalam jalan = warna aspal tepat, luar jalan = warna lahan dipisahkan dari campuran aspal (gamma 2,2) | `roadCanvas`, `ROADM.fill()`, `rEd`, `rLoc` |
| 32d | Agregat halus, jalur ban dan tetes oli per lajur (arteri dan boulevard dari as, jalan lain dari tepi), tambalan (sel 7 m, 9%), retak, talang 0,45 m, tutup saluran (sel 24 m, 45%), marka aus; jalur ban lebih licin | `laneTracks()`, `boxSD()`, `trk` |
| 32e | Petak 1,5-3 m per wilayah 60 m, rona per petak, noda air, permen karet, retak di 12% petak, kotor di sisi kerb dan sisi dalam | `tS`, blok 32e setelah sambungan beton |
| 32f | Nat bata tenggelam, warna per bata (gaya 8), papan bertumpuk dengan bayangan, plester bercak, noda turun di bawah ambang dan dari atap, kaki dinding kotor (lumut tipis di gedung lama), bercak pudar; kekuatan per gedung `wk` | `wk` di `BUILD_FS` |
| 32g | Ambang menonjol + bayangan (gaya tanpa ambang batu), kaca masuk ke dinding, pintu rumah berpanel 4 + kenop + kusen + 6 warna, pintu toko berkaca, ruang toko di balik etalase (rak berisi barang, lampu malam), bayangan di bawah pita batu | blok 32g |
| 32h | Plint beton 0,45 m, kerb beton 0,3 m di tepi aspal tanpa trotoar, alas dan kerah tiang lampu | blok 32h, `poleGeo` |

Batasan yang diketahui:
- 32d-32h hanya Ultra dan Tinggi (`uL_Detail`); 32b dan 32c berlaku di semua preset.
- Rumput 3D memakai klasifikasi lahannya sendiri, jadi helai rumput masih bisa tumbuh sampai tepi kerb.
- Strip trotoar 1,5 m jalan lokal masih dari peta lahan (lebih kecil dari satu piksel peta), hanya warnanya tidak lagi tercampur aspal.
- Jalur ban pada jalan selain arteri kota hanya satu jalur dekat kerb (jarak dari tepi hanya diketahui sampai 1,5 m).
- Memori tambahan: peta jalan RG8 2.048 x 2.608 sekitar 10,7 MB (+ mipmap sekitar 14 MB), atlas papan nama sekitar 2,8 MB.

## Revisi 1 dari 4 foto Bhakti (26 Oktober 2026)

| No | Masalah di foto | Penyebab | Perbaikan | Nama di kode |
| --- | --- | --- | --- | --- |
| 32j-1 | Nama toko terbalik di sebagian sisi gedung | Koordinat `u` naik ke kanan pengamat hanya di muka +z dan -x | `lx` dikali `sign(n.z)` / `-sign(n.x)` | blok 22a |
| 32j-2 | Isi semua toko mirip toko buku | Satu pola rak untuk semua toko | Isi toko mengikuti kata papan nama: 7 kelas (rak barang, makan, roti, jasa, busana, bunga, bengkel) dan 12 sub (buku, apotek, perkakas, cukur / salon, laundry, bank / pos, optik, sepatu, perhiasan, musik, penjahit); lantai per kelas (ubin catur / kayu dengan bayangan meja untuk tempat makan), lampu plafon | `SHOPK`, `SHOPS`, `shopBack()`, `shopFloor()`, `shopK` / `shopS` / `shopId` |
| 32j-3 | Malam: semua etalase menyala rata dan silau, isi tidak terlihat | Etalase memancar penuh (`shopM`) di atas ruang toko | 40% toko tutup malam dengan pintu gulung (jam tutup berbeda per toko); toko buka diterangi lewat ruangnya, pancaran rata hanya 0,45x dari jauh | `shut`, `shopE` |
| 32k | Halaman rumput di antara rumah kosong dan datar | Tidak ada benda halaman | Depan: beranda beratap (rumah tunggal / besar), undakan beton (rumah deret), batu pijakan, bedeng bunga, pagar kayu putih atau pagar tanaman; belakang: dek kayu, meja dan kursi, payung, panggangan, ayunan, bedeng sayur, trampolin, pagar kayu antar kavling dan belakang. Tidak bertumpuk dengan rumah, garasi, gudang kebun, pohon halaman, air | `TERAS_H` / `TERAS_G` / `TERAS_T` (dicatat di `fillHomes` tanpa angka acak), `TERAS`, `FURN.kinds.t32*` |

Jumlah benda halaman (hasil muat): beranda 4.019, undakan 5.655, batu pijakan 33.555, bedeng bunga 7.346, pagar kayu putih 14.610 ruas, pagar kayu 40.730 ruas, pagar tanaman 10.712 ruas, dek 4.575, meja 3.438, payung 1.857, panggangan 1.556, ayunan 295, bedeng sayur 1.857, trampolin 149. Dikirim ke GPU hanya dalam radius 80-220 m (`updateFurniture()`).

Batasan revisi:
- Benda halaman berlaku di semua preset (tidak ada saklar preset); FPS di GPU asli belum diukur.
- Beranda, pagar, dek, ayunan, trampolin, dan bedeng sayur berkolider (sekitar 80 ribu kolider baru); batu pijakan, bedeng bunga, meja, payung, panggangan tidak.
- Helai rumput 3D bisa menembus batu pijakan setinggi 8 cm.

## Revisi 2 dari 3 foto Bhakti (26 Oktober 2026)

| No | Masalah | Perbaikan |
| --- | --- | --- |
| 1 | Undakan rumah deret menutup pintu; tanaman bedeng terlalu low poly | Undakan dan bedeng bunga dihapus. Teras kini rata tanah (lantai 0,1 m, tanpa anak tangga), beranda juga diturunkan dari 0,35 m ke 0,1 m |
| 2 | Pagar tidak perlu | Semua pagar (kayu putih, kayu tinggi, tanaman) dan bedeng sayur dihapus. Diganti variasi teras depan: beranda beratap 35%, pergola kayu 25%, kanopi pintu 20%, teras terbuka dengan meja 20% (rumah deret: kanopi 60% / teras terbuka 40%) |
| 3 | Kedalaman toko terlihat aneh: isi menembus pilar ke toko sebelah | Ruang toko kini kotak selebar modulnya (dinding samping di batas toko, di balik pilar: `shopU0` / `shopU1`), makin gelap ke belakang, sudut gelap, lantai catur kontras lebih rendah |

Jumlah (hasil muat): beranda 2.014, kanopi 4.569, pergola 1.443, teras terbuka 3.429, batu pijakan 35.269, dek belakang 4.652, meja 4.169, payung 1.929, panggangan 1.644, ayunan 320, trampolin 157. Kolider tinggal di beranda, pergola, dek, ayunan, trampolin.

## Revisi 3 (26 Oktober 2026)

| No | Masalah | Perbaikan | Nama di kode |
| --- | --- | --- | --- |
| 1 | Penyangga kanopi pintu terbalik | Penyangga siku naik dari dinding (1,95 m) ke bawah tepi luar kanopi (2,46 m) | `canopy` |
| 2 | Rumput tumbuh menembus teras, dek, dan batu pijakan | Masker halaman 1 m per piksel dari tapak teras, dek, dan jalur batu pijakan; rumpun rumput 3D di dalamnya dibuang | `YARDM`, `YARD_GLSL` / `yardM()`, `bare()` |
| 3 | Toko yang etalasenya menghadap belakang berdiri di rumput | Pelataran beton 4 m di sekeliling 1.391 gedung bertoko (gaya 1, 2, 11, 12, 13, gaya 0 > 12 m); digambar shader tanah dari masker, tidak di jalan atau air | kanal r `YARDM`, blok 32k di shader tanah |
| 4 | Halaman belakang semua rumput | 50% sisi gedung bertoko yang di depannya kosong (tanpa gedung, jalan, trotoar, air, pohon) jadi lahan parkir aspal 17 m: dua baris petak 2,6 m dengan garis dan penahan roda, lorong 6 m; sisanya tetap rumput. Hasil: 172 lahan, 2.724 petak | kanal g `YARDM`, `TERAS.lots`, `stall` |

Batasan: masker halaman RG8 6.284 x sekitar 2.500 piksel (sekitar 31 MB dengan mipmap).

## Revisi 4 (26 Oktober 2026)

| No | Masalah | Perbaikan | Nama di kode |
| --- | --- | --- | --- |
| 1 | Lahan parkir kosong, mobil semua di tepi jalan | Mobil tepi jalan dalam 150 m dari lahan dipindah ke petak (terdekat dulu, 35-75% petak terisi, 25% masuk mundur). Jumlah mobil tetap 4.814; 1.238 dipindah | `PARKED.moved`, `TERAS.lots[].slots` / `cars` |
| 2 | Lahan parkir di tengah rumput tanpa akses | Jalan masuk aspal 6 m dari lahan ke jalan atau trotoar terdekat (lurus dari tepi jauh atau dari ujung lorong, maks 60 m, tidak menembus gedung, pohon, air, isi halaman). Lahan tanpa jalan masuk tidak dibuat. Hasil: 168 lahan, 2.326 petak, jalan masuk 6-43 m | `drive()`, `TERAS.lots[].drive` |
| 3 | FPS pusat kota 40-50 | Detail aspal dan beton 32d-32e (8-10 noise per piksel) hanya bila jejak piksel < 0,25 m, memudar 0,12-0,25; pelapukan dinding 32f-32h hanya dalam 110 m, memudar 70-110 m; ruang toko tetap memudar lewat jejak piksel | `fD` shader tanah, `wD` `BUILD_FS` |
| 4 | Pernyataan `TERAS.clipN` tertelan komentar | Dipisah ke baris sendiri | blok 32k |
