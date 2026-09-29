# Rencana Tahap 21 Copper Corn Station: air mancur, kaca rumah Cooper, gedung kaca malam

Per 29 September 2026 · Bhakti

## Ringkasan

- **21a air mancur:** orang dan pohon tidak lagi muncul di dalam kolam, pengunjung datang, berdiri atau duduk di bibir kolam, lalu pergi. Semburan diganti kolom air utuh + tetes bulat lembut + percikan di titik jatuh. Permukaan air beriak (dari semburan, angin, hujan), dasar kolam terlihat tembus. Angka fisika Coriolis (5,1 m, 1,37 m, 0,30 m) tidak berubah.
- **21b kaca rumah Cooper:** dari dalam rumah kaca tidak lagi memantulkan seluruh silinder. Yang terpantul hanya ruangan yang redup (lemah), jadi luar terlihat jelas. Dari luar pantulan daratan seberang tetap ada.
- **21c gedung kaca malam:** gedung jauh tidak lagi putih rata. Lampu menyala per lantai dan per blok kantor (tetap bervariasi dari jauh), warna putih dingin kantor vs kuning hangat hunian, banyak kaca gelap, jumlah lampu ikut jam, lampu mahkota di sebagian menara, lampu merah penanda di atap.

Urutan kerja: 1) 21a-1 (selesai), 2) 21b (selesai), 3) 21c, 4) 21a-2 + 21a-3 (paling besar).

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


## 21c: gedung kaca malam

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
