# Rencana Tahap 21 Copper Corn Station: air mancur, kaca rumah Cooper, gedung kaca malam, jendela gedung, kabut pagi

Per 29 September 2026 · Bhakti

## Ringkasan

- **21a air mancur:** orang dan pohon tidak lagi muncul di dalam kolam, pengunjung datang, berdiri atau duduk di bibir kolam, lalu pergi. Semburan diganti kolom air utuh + tetes bulat lembut + percikan di titik jatuh. Permukaan air beriak (dari semburan, angin, hujan), dasar kolam terlihat tembus. Angka fisika Coriolis (5,1 m, 1,37 m, 0,30 m) tidak berubah.
- **21b kaca rumah Cooper:** dari dalam rumah kaca tidak lagi memantulkan seluruh silinder. Yang terpantul hanya ruangan yang redup (lemah), jadi luar terlihat jelas. Dari luar pantulan daratan seberang tetap ada.
- **21c gedung kaca malam:** gedung jauh tidak lagi putih rata. Lampu menyala per lantai dan per blok kantor (tetap bervariasi dari jauh), warna putih dingin kantor vs kuning hangat hunian, banyak kaca gelap, jumlah lampu ikut jam, lampu mahkota di sebagian menara, lampu merah penanda di atap.

- **21d jendela gedung tinggi:** ukuran kaca, tinggi lantai, dan warna berbeda per menara; satu ruangan selebar beberapa jendela sampai satu lantai; ruangan tidak terlihat dari jauh.
- **21e revisi dari foto:** hal yang sama untuk deretan menengah dan podium, kilau diagonal dihapus, kaca memantulkan gedung seberang jalan, kabut pagi.

Urutan kerja: 1) 21a-1 (selesai), 2) 21b (selesai), 3) 21c (selesai), 4) 21d dan 21e (selesai), 5) 21a-2 + 21a-3 (paling besar).

## Penyebab di kode

| Keluhan | Penyebab | Lokasi (cari nama) |
| --- | --- | --- |
| Gambar 1: orang terjebak di kolam | Kelompok mengobrol di plaza (`still({ pose: 1 })`, 2 kelompok per plaza) ditaruh acak di setengah tengah plaza, lalu diam selamanya. `PEDS` dibangun sebelum `FOUNT`, jadi posisi kolam belum diketahui. Blok plaza kecil (dipotong jalan lokal), jadi peluang jatuh di radius kolam 4,8 m cukup besar | `PEDS` langkah 3 "taman dan plaza kota"; `FOUNT` |
| Gambar 1: pohon di tengah kolam (dugaan awal, keliru) | Diukur di 21a-1: tidak ada pohon dalam 10 m dari pusat kolam; pohon di gambar 1 berdiri di belakang kolam. Pohon plaza tetap diberi zona larangan agar tidak terjadi bila tata letak berubah | loop `parkBlocks` di blok pohon ("taman dan plaza kota") |
| Merpati mematuk di dalam air (temuan tambahan) | Titik kawanan merpati = tepat pusat tiap plaza, sama dengan pusat air mancur | `BIRDS`, "tempat merpati" |
| Gambar 1: busa cuma zigzag | 3.600 kotak datar 6 x 6 cm tanpa tepi lembut, alfa rata 0,55, warna rata. Tiap semburan 400 partikel pada satu garis lintasan dengan geser acak kecil (+-6 cm) yang tetap per partikel, jadi terbaca sebagai garis bergerigi, bukan kolom air | `FOUNT` (VS dengan `aJet`) |
| Gambar 1: air diam seperti kaca | Air = `CircleGeometry` datar dengan `specMat` kekasaran 0,05: cermin sempurna `farEnv`, tanpa riak, tanpa dasar kolam, tanpa gerak | `FOUNT`, `water` |
| Gambar 2: kaca dalam rumah memantulkan silinder | `M.glassClear` = `specMat(..., 0.03, 0.06, 0, true)`. `SPEC_GLSL` selalu memantulkan `farEnv` (daratan seberang, sunline, end cap, awan) tanpa melihat sisi mana penonton berdiri. Alfa naik ke 1 mengikuti Fresnel, jadi di sudut miring kaca jadi cermin silinder yang pekat. Kaca = kotak 2 cm dua sisi, jadi pantulan dobel. Tekstur tint abu-biru alfa 0,14 di seluruh panel menambah kabut (persegi pucat di gambar 2) | `COOPER_HOUSE`, fungsi `win()`, `T.glassClear`, `SPEC_GLSL` |
| Gambar 4: gedung kaca malam putih polos | Di `BUILD_FS`, bila satu bay jendela lebih kecil dari beberapa piksel (`ax`, `ay` dari `fwidth`), jendela dirata-ratakan: `on = mix(step(wid, litP), litP, max(ax, ay))`. Dari jauh SEMUA jendela menyala tepat 35% (menara kaca, `litP` 0,35) dengan warna rata, emisi x 1,6. Menara kaca: jendela 92% x 80% = 73,6% muka gedung, bay 1,5 m, jadi rata-rata cepat terjadi. Hasilnya pita terang seragam per lantai; setelah bloom, ACES, dan adaptasi mata malam (`ADAPT.max` 2,2) tampak putih pucat | `BUILD_FS` blok "kaca: interior gelap + pantulan langit" |

## 21a: air mancur

### 21a-1: orang, pohon, merpati (selesai)

Terukur sebelum perbaikan: 5 orang diam di 3,3-5,0 m dari pusat kolam (dinding kolam 4,8 m, jadi di dalam kolam) dan titik kawanan merpati tepat di pusat kolam (0 m). Plaza air mancur 31,4 x 41,2 m. Tidak ada pohon atau perabot dalam 9 m.

| Bagian | Perubahan |
| --- | --- |
| Posisi kolam lebih awal | `FOUNT.s`, `FOUNT.za`, `FOUNT.block` dihitung di blok pohon (rumus sama: plaza pusat kota terdekat ke s 14, za 625), sebelum pohon, pejalan kaki, dan merpati. `FOUNT.h` dan kolam tetap dibangun di bagian air mancur (butuh `TER`). Fungsi bantu `fountDist()`, `fountPush(s, za, r)` |
| Zona larangan | `FOUNT.clear` 7,0 m dari pusat (dinding kolam 4,8 m + jalur 2,2 m) |
| Pohon plaza | Pohon di dalam zona didorong keluar sepanjang garis dari pusat sampai 7,0 m, tidak dibuang (jumlah dan urutan acak sama) |
| Kelompok mengobrol | Pusat kelompok di zona didorong ke 8,5 m. Kelompok kini bergerak (`VIS.groups`): diam mengobrol 3-8 menit, bubar (anggota kembali ke jalur keliling plaza 40-150 s), lalu berkumpul lagi di tempat baru di plaza yang sama (jauh dari kolam, pohon, dan kelompok lain). Yang datang lebih dulu menunggu temannya, berkumpul paling lama 4 menit |
| Pengunjung air mancur (baru) | 8 orang (`VIS.fount`): keliling plaza 30-120 s, jalan lurus ke tepi kolam (5,05 m, dekat arah datang, tidak berebut tempat: jarak busur minimal 0,9 m), berdiri menghadap air atau (1 dari 3) duduk di bibir kolam menghadap keluar (4,5 m, tinggi 0,55 m), 20-90 s, lalu jalan ke titik lain di jalur keliling. Tidak pernah muncul atau hilang tiba-tiba. Kepadatan tetap ikut `pedAct()` (malam lebih sepi) |
| Jalur lurus | `visPathOK()`: tiap 0,7 m dicek tidak masuk lingkaran 5,0 m kolam dan tidak menabrak collider (pohon, perabot); bila gagal, coba titik lain atau tunggu 3 s |
| Merpati | Titik kawanan plaza air mancur digeser 10 m ke sisi -za (plakat di sisi +za). Merpati yang turun didorong menjauh dari kolam dalam 7 m; merpati di tanah tidak pernah di dalam 5,2 m |
| Mesin keadaan | `stepVisit(p, dt)` dipanggil dari `stepPeds()` untuk `kind: 'visit'` ('loop', 'in', 'stay', 'out'); generator acak sendiri `visRnd()` |
| Dunia lain | Tidak berubah: angka acak setup pejalan kaki, pohon, dan merpati tetap. Dicek terhadap main: 15.032 pohon, 11.641 rute pejalan kaki, 10 kawanan merpati lain, 44.685 collider, penampilan 13.094 orang, semua identik. Yang berubah hanya 41 anggota kelompok mengobrol (kini bergerak) dan 8 pengunjung baru |

Hasil `tools/uji_air_mancur.py` (baru, 30 menit simulasi, sandbox SwiftShader):

| Cek | Hasil |
| --- | --- |
| Geser Coriolis 10 m/s dan 6 m/s | 1,372 m dan 0,296 m (tidak berubah) |
| Orang di dalam kolam saat muat | 0 (sebelumnya 5) |
| Pohon dalam 7 m | 0 |
| Titik merpati terdekat | 10,0 m dari pusat kolam (sebelumnya 0 m) |
| Pengunjung air mancur | 8 dari 8 pernah di tepi kolam, 8 pernah duduk |
| Lama di tepi kolam paling lama | 90 s |
| 30 menit: posisi di dalam kolam / nilai tidak valid | 0 / 0 |
| 30 menit: titik jalur lurus di dalam pohon atau benda | 0 |
| Kelompok mengobrol | 16 kelompok: 16 bubar, 16 berkumpul lagi |
| Pusat kelompok terdekat | 8,5 m dari pusat kolam |
| Merpati dikejutkan lalu hinggap lagi | 6 dari 6 terbang, 6 hinggap, 0 di dalam kolam |

Uji lama yang dijalankan ulang, semua lolos tanpa error: `qc_load.py`, `uji_pejalan_kaki.py`, `uji_trotoar.py`, `uji_burung.py`, `uji_hujan.py`, `uji_ladang_foto_tur.py`, `uji_bahasa.py`. Catatan: di uji merpati, kawanan terbang menjauhi kolam (arah pemain), jadi dorongan saat mendarat hanya teruji lewat batas keras 5,2 m.

### 21a-2: semburan

| Lapisan | Isi | Jumlah per preset (Ultra / Tinggi / Sedang / Rendah / Hemat) |
| --- | --- | --- |
| Kolom air | Pita menghadap kamera per semburan, 32 ruas, lintasan dihitung di VS dengan rumus yang sama seperti sekarang (termasuk geser Coriolis `xs`). Lebar mengecil dari nosel lalu melebar di dekat puncak, alur memanjang bergerak (noise), tepi lebih terang (Fresnel), agak tembus. Di dekat puncak kolom pecah (alfa memudar) | 9 pita semua preset |
| Tetes dan buih | Sprite bulat bertepi lembut 8-25 cm (membesar dengan waktu terbang), kecepatan samping acak kecil (kerucut +-0,3 m/s) sehingga saat turun tetes melebar seperti payung, bukan satu garis | 6.000 / 4.500 / 3.600 / 2.400 / 1.500 |
| Percikan | Semburan kecil sprite di titik jatuh + cakram buih putih di air. Titik jatuh ikut bergeser Coriolis (1,37 m semburan tengah, 0,30 m semburan kecil), jadi efek fisikanya kelihatan di air | 600 / 450 / 360 / 240 / 120 |
| Kabut halus | 40 sprite besar sangat tipis di sekitar titik jatuh, terbawa `WIND` | 40 / 40 / 24 / 0 / 0 |
| Cahaya | Tetap `vegLight` (siang terang, malam redup) + kilau pantul sunline / Matahari lewat `farEnv`. Malam: lampu sorot bawah air di nosel (usulan, lihat Keputusan) | |

Angka fisika tetap, dicek ulang:

| Item | Nilai | Derivasi |
| --- | --- | --- |
| Tinggi semburan tengah | 5,10 m | v^2 / 2g = 10^2 / (2 x 9,81) |
| Tinggi semburan kecil | 1,83 m | 6^2 / (2 x 9,81) |
| Geser Coriolis tengah | 1,37 m | (4/3) omega v^3 / g^2 = (4/3) x 0,09905 x 1.000 / 96,24 (`FOUNT.shift10`) |
| Geser Coriolis kecil | 0,30 m | (4/3) x 0,09905 x 216 / 96,24 (`FOUNT.shift6`) |

Teks plakat (`FOUNT_TEXT`), titik tur, dan tombol 9 tidak berubah.

### 21a-3: permukaan air

| Bagian | Isi |
| --- | --- |
| Material | Shader air sendiri (pakai `LIGHT_GLSL`: `stationLight`, `farEnv`, `nightLight`), menggantikan `CircleGeometry` + `specMat` |
| Riak semburan | Cincin menyebar dari 9 titik jatuh, melemah dengan jarak. Panjang gelombang 0,1-0,3 m, kecepatan 0,40-0,68 m/s (gelombang gravitasi c = akar(g lambda / 2 pi), tegangan permukaan diabaikan karena < 3% di panjang ini) |
| Riak angin | Dua lapis noise bergulir, kekuatan dari `WIND` (lebih kasar saat mendung) |
| Riak hujan | Cincin tetes seperti genangan di shader tanah, aktif saat `RAIN` |
| Pantulan | `farEnv` dengan normal beriak + Fresnel Schlick (F0 0,02 air). Pantulan jadi pecah dan bergoyang, bukan cermin |
| Dasar kolam | Dihitung di shader tanpa tekstur layar: sinar dibiaskan ke bidang dasar (kedalaman 0,37 m), pola ubin + kaustik bergerak (terang ikut sunline), warna makin biru-hijau dengan jarak tempuh di air |
| Buih | Putih bernoise di titik jatuh dan kaki nosel |
| Garis basah | Pita gelap di dinding dalam kolam tepat di atas permukaan air |
| Malam | Pantulan lampu jalan dan lampu untaian plaza (`lampPool`), cahaya sorot nosel bila dipilih |
| Suara (usulan) | Desis percikan disintesis, keras dalam 25 m, ikut `AUDIO` |

Aturan GPU tetap: tidak `normalize()` vektor yang bisa nol, tidak `pow()` bilangan negatif, `sqrt()` dijaga (NaN di M1).

## 21b: kaca rumah Cooper (selesai)

Fisika singkat: kaca biasa memantulkan sekitar 4% cahaya saat dilihat tegak lurus (F0 = ((n - 1) / (n + 1))^2 = (0,5 / 2,5)^2 = 0,04 untuk n = 1,5), naik hanya di sudut sangat miring. Dari dalam, yang terpantul adalah ruangan; yang tembus adalah luar. Karena luar siang jauh lebih terang daripada ruangan, pantulan ruangan nyaris tidak terlihat (kesimpulan kualitatif, belum diukur di adegan). Malam kebalikannya: luar gelap, kaca mulai jadi cermin ruangan.

| Bagian | Sekarang | Sesudah |
| --- | --- | --- |
| Geometri kaca | Kotak 2 cm, dua sisi, pantulan dobel | Satu bidang per jendela dengan normal menghadap keluar. `gl_FrontFacing` = penonton di luar; belakang = penonton di dalam (tanpa biaya tambahan) |
| Pantulan dari dalam | `farEnv` (seluruh silinder) | Warna ruangan perkiraan: plester (`T.plaster`) x cahaya ambien dalam rumah x 0,35, F0 0,04 |
| Alfa dari dalam | Naik ke 1 di sudut miring | Dibatasi maksimum 0,35, jadi luar selalu terlihat |
| Pantulan dari luar | `farEnv` | Tetap `farEnv` (benar dari luar), F0 0,06 ke 0,04 |
| Tint kaca | Abu-biru alfa 0,14 | Alfa sekitar 0,04, sedikit hijau di tepi |
| Kisi dan kusen | Ada | Tetap |
| Adaptasi mata | `ADAPT` sudah ada | Di dalam rumah yang lebih redup mata beradaptasi, jadi luar tampak lebih terang (dicek di uji) |

Hanya `M.glassClear` rumah Cooper yang memakai material ini (dicek dengan grep). Kaca terminal dan gedung tidak berubah.

### Hasil 21b

Penyebab utama ternyata lebih parah dari dugaan: kaca lama hampir pejal dari KEDUA sisi (alpha 0,986 tegak lurus, diukur). Kaca transparan dua sisi digambar three.js dalam dua lintasan; di lintasan sisi belakang urutan muka dibalik, jadi shader mengira kaca dilihat dari sudut 90 derajat (Fresnel 1) dan menggambarnya sebagai cermin silinder pejal. Kini sisi penonton ditentukan dari arah kamera terhadap normal keluar.

| Cek (`tools/uji_kaca_cooper.py`, baru) | Sebelum | Sesudah |
| --- | --- | --- |
| Alpha kaca dilihat tegak lurus dari dalam | 0,986 | 0,078 |
| Alpha kaca dilihat tegak lurus dari luar | 0,986 | 0,078 |
| Alpha dari dalam, miring 85 derajat (batas 0,35) | diukur hanya di versi baru | 0,350 |
| Alpha dari luar, miring 85 derajat (pantulan daratan tetap) | diukur hanya di versi baru | 0,666 |
| Nilai tidak valid siang dan malam | | 0 |
| Panel kaca | 22 kotak | 22 bidang (1 mesh) |

Alpha diukur dengan kaca saja (tekstur kisi putih diganti sementara saat uji). Kisi putih tetap pejal. `tools/uji_menara.py`: hitungan panel disesuaikan (6 verteks per bidang, dulu 36 per kotak). Uji lama `qc_load`, `uji_pantulan`, `uji_bahasa` lolos; `uji_menara` lolos kecuali 2 cek jatuhkan bola dari dek yang juga gagal di commit sebelum Tahap 21 (bola belum mendarat dalam batas tunggu 30 s di sandbox SwiftShader yang lambat), jadi bukan dari perubahan ini.


## 21c: gedung kaca malam (selesai)

| Bagian | Isi |
| --- | --- |
| Lampu bertingkat (inti perbaikan) | Hash nyala dihitung di beberapa tingkat: jendela, blok 4 bay (satu kantor), segmen 12 bay, satu lantai penuh. Dari jauh dipakai tingkat terkasar yang selnya masih di atas sekitar 2 piksel (dipilih dari `fwidth`, dicampur halus antar tingkat). Rata-rata tetap `litP`, tetapi pola lantai terang dan gelap tetap terlihat dari jauh, tidak lagi rata |
| Beda per gedung | Faktor 0,3-1,6 dari `vSeed`: ada gedung hampir gelap, ada yang terang penuh |
| Ikut jam | Uniform jam baru di `BUILD_U`. Usulan awal: kantor ramai 18-21, turun ke sekitar 0,1 setelah 23; hunian puncak 19-23, sedikit setelah 01 (angka awal, disetel setelah Bhakti melihat) |
| Warna | Kantor (gaya 0, 1, 8): putih dingin, sebagian putih netral. Hunian (gaya 2, 3, 11): kuning hangat. Sekarang hanya 20% jendela berwarna dingin untuk semua gaya |
| Kaca gelap | Jendela mati tetap gelap dengan pantulan kota redup; rangka dan pelat lantai tidak ikut dirata-ratakan jadi terang |
| Kecerahan | Emisi rata-rata muka gedung diturunkan dan dikalibrasi dengan adaptasi mata malam agar lantai terang tidak menjadi putih jenuh setelah ACES |
| Lantai mesin | Tiap 15-25 lantai satu pita gelap berkisi |
| Lobi | Lantai dasar menara kaca terang |
| Lampu mahkota | Sekitar 30% menara di atas 120 m: 2-6 lantai teratas disorot dari bawah (gradasi). Warna menunggu keputusan (lihat bawah). Desain orisinal, tidak meniru gedung nyata tertentu |
| Lampu penanda atap | Merah berkedip di atap gedung di atas 90 m. Laju usulan 20-60 kedip per menit, mengikuti kisaran lampu penghalang penerbangan intensitas menengah (ICAO Annex 14, tipe B merah); dari ingatan, belum dicek ke dokumen sumber |
| Siang | Tidak berubah (hanya jalur emisi malam yang diganti) |
| Biaya | Beberapa hash tambahan per piksel, hanya di cabang `uNight > 0.01`. Preset Hemat: dua tingkat saja |

Menara ikon `LANDMARK` (221 m, beacon) dan interior jendela dekat (14c) tetap.

### Hasil 21c

| Bagian | Yang dikerjakan |
| --- | --- |
| Nyala bertingkat | Lantai, blok 4 bay, jendela; peluang qF = litB^0,4, qB = litB^0,35, qW = litB^0,25 (hasil kali = litB). Rata-rata per tingkat saat sel lebih kecil dari sekitar 2 piksel |
| Per gedung | litB = litP x faktor jam x (0,3-1,7 dari `vSeed`) |
| Faktor jam (`BUILD_U.uLitT`) | Kantor 1,0 sampai 21.00, turun ke 0,25 pukul 23.30; hunian 1,0 pukul 19-23, turun ke 0,25 pukul 01.30, naik sedikit pagi 05-09. Angka awal, bisa disetel |
| Warna | Kantor (gaya 0, 1, 8): putih netral atau putih dingin per blok. Hunian: kuning hangat, 15% putih kebiruan. Terang per blok 0,75-1,25 |
| Menara kaca | Lantai mesin gelap tiap 14-22 lantai (menara > 60 m), lobi selalu terang |
| Lampu mahkota | 30% menara kaca > 120 m: 12 m teratas disorot dari lis bawah; 1 dari 5 biru atau ungu, sisanya putih hangat |
| Lampu penanda atap | Merah di sudut atap gedung > 90 m, 30 kedip per menit, ukuran minimal sekitar 2 piksel |
| Siang | Tidak berubah (semua suku baru dikali `uNight`) |
| Interior 14c | Lampu ruangan dekat mengikuti pola nyala bertingkat yang sama |

Hasil `tools/uji_gedung_malam.py` (baru): menara kaca tertinggi (142 m) dirender sendirian dari 800 m pukul 23.00.

| Ukuran | Sebelum (main) | Sesudah |
| --- | --- | --- |
| Sebaran terang sepanjang baris (blok menyala / gelap) | 0,05 (rata) | 0,39 |
| Sebaran terang antarbaris (lantai) | 0,31 | 1,73 |
| Terang rata-rata muka gedung | 0,318 | 0,134 (ikut jam: kantor pukul 23.00 sekitar 1/3) |
| Nilai tidak valid | | 0 |
| Siang dengan faktor jam berbeda | | 0 nilai beda |

Sebaran = simpangan baku dibagi rata-rata. Uji lama `qc_load` dan `uji_interior` dijalankan ulang.


## 21d: jendela gedung tinggi (selesai)

Keluhan Bhakti: satu jendela = satu ruangan (terlihat seperti bilik kecil), padahal satu kotak kaca bisa selebar lantai; dari jauh ruangan jarang terlihat; ukuran kaca semua menara sama.

| Bagian | Isi |
| --- | --- |
| Variasi per gedung (gaya 0 dan 1) | Dari `vSeed`: jarak mullion (menara kaca 1,2 / 1,5 / 1,8 / 2,4 / 3,0 / 4,5 m), tinggi lantai (3,6-4,4 m), pola kaca (penuh, pita, berlubang, sirip), lebar mullion, tint kaca (biru, hijau, abu, perunggu), warna rangka |
| Ruangan multi-bay | Satu ruangan = `rm` bay (lebar target 6-14 m), 20-30% gedung lantai terbuka selebar muka. Meja berderet tiap 2,6 m, kisi lampu plafon tiap 3 m, kerai per ruangan, lantai kantor lebih dalam (5-12 m) |
| Jauh | Ruangan memudar di 35-100 m; jauh = kaca pantul + lantai menyala |
| Gaya lain | Tidak berubah (`rm = 1`) |

## 21e: revisi dari foto Bhakti (selesai)

| Foto | Keluhan | Penyebab | Perbaikan |
| --- | --- | --- | --- |
| 1 | Masih ada 1 jendela 1 kamar | 21d hanya gaya 0 dan 1; deretan menengah / apartemen (gaya 2, gedung paling banyak) dan podium (gaya 11) tetap satu bay per ruangan | Variasi dan ruangan multi-bay juga untuk gaya 2 dan 11 |
| 2 | Garis putih diagonal sebagai kilauan tidak meyakinkan | Pita diagonal `sheen` di kaca interior 14c | Dihapus; kaca hanya memakai pantulan utama (`farEnv`) |
| 3 | Kaca memantulkan seluruh silinder padahal ada gedung di depannya (dibaca sebagai pantulan, bukan bayangan cahaya) | `farEnv` tanpa penghalang di kaca dan etalase | Model ngarai kota: sinar pantul yang tiba di muka seberang di bawah atapnya memantulkan gedung itu |
| 4 | Pagi langsung terang | Kabut pagi lama x2,2 hanya sekitar 1 jam | Kabut pagi x5, 05.00-09.30, warna pucat hangat |

| Bagian | Isi |
| --- | --- |
| Gaya 2 | Bay 3,0 / 3,4 / 4,2 / 5,0 m, lantai 3,0-3,5 m, pola berlubang / berlubang lebar / pita, ruangan 6-12 m, 20% lantai terbuka. Isi hunian (lantai kayu, gambar, tirai); modul lebih dari 5,5 m: perabot tiap 3,2 m dan kisi lampu plafon. Balkon berselang per ruangan, bukan per bay |
| Gaya 11 | Bay 2,8 / 3,6 / 4,5 m, lantai 3,6-4,2 m, pola pita lebar / berlubang lebar, ruangan 8-16 m, 40% lantai terbuka, isi kantor |
| Zona lampu | Ruangan lebar dan lantai terbuka dinyalakan per zona sekitar 6 m (ruangan <= 6 m: zona = ruangan, seperti 21d), jadi lantai terbuka tidak menyala rata selebar muka dari jauh. Ditemukan saat `uji_gedung_malam` dijalankan ulang (sebaran sepanjang baris turun ke 0,08 setelah 21d) |
| Pantulan | Gaya 0, 1, 2, 8, 11. Muka seberang 28 m di depan; tinggi gedung seberang `clamp(0,9 H, 12, 60)` x 0,55-1,45 per segmen 28 m, 12% segmen = celah. Warna muka seberang dengan jendela (malam sebagian menyala). Kaca interior 14c, kaca jauh, dan etalase memakai model yang sama (siluet acak 14c lama dihapus). Pembagi dijaga, tanpa `pow` / `sqrt` |
| Kabut pagi | Naik 04.48-06.00, penuh sampai 07.12, hilang 09.30; kerapatan dasar + 4 x dasar (1 km 43%, 2 km 89%); warna dicampur 60% ke pucat hangat; pantulan daratan seberang ikut berkabut. Mendung tetap menghapus kabut pagi; kamera luar tanpa kabut |

### Hasil 21e

| Uji | Hasil |
| --- | --- |
| `qc_load.py` | Tanpa error |
| `uji_kabut_pagi.py` (baru) | 9 dari 9 OK: kerapatan jam 5 / 6 / 6,6 / 8 / 9 / 9,6 = 1,30 / 5,00 / 5,00 / 3,88 / 1,48 / 1,00 x dasar; di luar pagi `uL_FarAvg` sama dengan rumus lama; render jam 6,6 0 nilai tidak valid dari 192.000 |
| `uji_jendela_gedung.py` (diubah) | Variasi: gaya 1 (8 gedung) 8 jarak mullion / 5 tinggi lantai berbeda, gaya 2 (6) 4 / 4, gaya 11 (6) 3 jarak mullion; 150 m interior hidup = mati untuk gaya 0, 1, 2, 11 (0 nilai beda dari 1.179.648); 0 nilai tidak valid dari 4.194.304. Pantulan: kaca lantai 90 m menara > 120 m tidak berubah (0,000); etalase dilihat tegak lurus berubah 1,6-2,5% dari rata-rata gambar (GAGAL ambang 0,05: dilihat tegak lurus bobot pantulan kecil karena Fresnel; uji sudut miring belum dijalankan) |
| `uji_gedung_malam.py` | OK setelah zona lampu: sebaran sepanjang baris 0,34 (batas > 0,25; setelah 21d sempat 0,08), antarbaris 1,57 |
| `uji_interior.py` | OK (kait shader uji disesuaikan dengan baris `kI` 21d): pantulan 15 m 0,11, 60 m 0,55 |
| `uji_kaca_cooper.py`, `uji_pantulan.py` | OK |
| `uji_menara.py` | GAGAL di bola jatuh dari dek ("bola belum mendarat"), dijalankan bersamaan dengan uji lain (CPU berebut); belum dicek apakah juga gagal di main. Bagian lain OK |

Perbandingan dengan versi lama dari git dibuang dari `uji_jendela_gedung.py`: dua halaman tetap berbeda walau jam, putaran sunline, dan awan dibekukan (selisih kontrol satu halaman 0,0115), jadi diganti uji A/B dalam satu halaman (shader dipinjam sementara).

## Uji

| Skrip | Isi |
| --- | --- |
| `tools/uji_air_mancur.py` (baru) | 30 menit simulasi: tidak ada pejalan kaki dalam 5,0 m dari pusat kolam, tidak ada pohon dalam 7,0 m, titik merpati di luar 7,0 m; pengunjung berganti (lebih dari 8 orang berbeda, lama tinggal maksimal 120 s); geser titik jatuh = `FOUNT.shift10` dalam 1%; render siang dan malam tanpa nilai tidak valid |
| `tools/uji_kaca_cooper.py` (baru) | Kamera di dalam rumah menghadap jendela: warna tembus kaca mendekati warna luar tanpa kaca; dari luar pantulan masih ada; tanpa nilai tidak valid |
| `tools/uji_gedung_malam.py` (baru) | Menara kaca jam 23 dari sekitar 800 m: sebaran terang di muka gedung di atas ambang (tidak rata), rata-rata dalam rentang; fraksi jendela menyala mendekati `litP` x faktor jam; render siang sama dengan sebelum perubahan |
| Uji lama yang disentuh | `qc_load.py`, `uji_pejalan_kaki.py`, `uji_trotoar.py`, `uji_burung.py`, `uji_hujan.py` (angka air mancur), `uji_suasana.py`, `uji_interior.py`, `uji_menara.py` (kaca bening rumah Cooper), `uji_bahasa.py` (teks baru lewat `t()` dan `I18N.en`) |

## Keputusan Bhakti

Diputuskan 29 September 2026: semua mengikuti usulan bawaan. Nomor tahap diganti dari 20 ke 21 karena Tahap 20a-20d di main sudah dipakai untuk optimasi.

| No | Pertanyaan | Keputusan (usulan bawaan) |
| --- | --- | --- |
| 1 | Berapa ramai pengunjung air mancur, dan boleh duduk di bibir kolam? | 8 orang, sepertiga duduk |
| 2 | Kelompok mengobrol di plaza lain juga bubar dan pindah berkala? | Ya, tiap 3-8 menit |
| 3 | Lampu sorot bawah air saat malam? | Ya, putih hangat |
| 4 | Warna lampu mahkota gedung: putih saja, atau boleh biru / ungu seperti gambar 5? | Sebagian besar putih, sekitar 1 dari 5 berwarna |
| 5 | Suara air mancur? | Ya |

## Batasan

- Sandbox uji memakai SwiftShader: tidak memperlihatkan NaN seperti Apple M1, dan tidak mengukur FPS. Visual dan FPS diuji Bhakti di GTX 1060 dan MacBook M1.
- Angka jam nyala gedung, jumlah partikel, dan kekuatan riak adalah usulan awal, bukan dari data, dan akan disetel setelah dilihat.
- Laju kedip lampu penanda atap dari ingatan tentang ICAO Annex 14; perlu dicek bila ingin tepat.
- "Pertahankan yang ada": posisi air mancur, plakat, tur, tombol 9, dan semua angka fisika tetap.
