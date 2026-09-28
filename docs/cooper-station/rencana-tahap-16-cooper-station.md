# Rencana Tahap 16 Copper Corn Station: distrik, fasilitas kota, peta baru

Status: disetujui pemilik, dikerjakan berurutan 16a-16f.

## Latar belakang

Pemilik meminta: (1) nama distrik untuk tiap daerah, (2) variasi bangunan seperti pasar, pusat kota (downtown), taman di tempat yang strategis, (3) peta diperbarui. Keputusan pemilik: distrik padat memakai nama megacity dunia yang ikonik (pusat kota = New York, bukan Jakarta), distrik permukiman memakai nama astronom; zona luar kota memakai nama lumbung pangan dunia (pertanian) dan sungai besar (taman).

Dikerjakan per sub-tahap 16a-16f; tiap sub-tahap commit dan push sendiri ke branch dan `main`, hasil dicatat di dokumen ini.

## Temuan kode (`experiences/cooper-station/index.html`)

| Bagian | Yang ada |
| --- | --- |
| Tata kota | Sel 26 kolom (arteri sepanjang za tiap `ART` 241,7 m; k = 0 boulevard trem, k = 13 Skyway) x 9 baris (za 250-2500, `ART_Z` 250). `cityDensity()` punya 4 pusat: (s 0, za 480), (0,42 keliling = k 10,9, za 1150), (0,75 keliling = k 19,5, za 900), (0,22 keliling = k 5,7, za 1750). `cityClass()` pusat/menengah/permukiman/tepi |
| Taman kota | `parkBlocks` acak (8% blok pusat, 5% lainnya), jalur keliling `PARK_PATHS` (15c) |
| Pasar/sekolah | Hanya satu bangunan `flat` 45 x 22 warna `#d9c9a8` di 4% blok menengah (acak) |
| Halte trem | `TRAM.stops`: Spaceport 120, Pusat kota 625, Kota 1125, Permukiman 2125, Taman 2950, Pertanian 4800, Utilitas 6650, Museum Cooper 7250 (semua di boulevard s = 0) |
| Peta | `drawMapStatic()` (tekstur tanah + kotak rumah), `drawMap()` (Skyway, rel, halte, nama `CONFIG.zones`, `MAP_MARKS` 0-9 dan L, pemain, skala), `buildMapLegend()` (lokasi, zona, tanda) |
| Teks | Semua nama lewat `t()` + `I18N.en`; nama distrik = nama diri (sama di dua bahasa) |

## Nama distrik (usulan)

Kota dibagi 7 sektor keliling x 2 pita (za 150-1250 dekat spaceport, za 1250-2500 dekat sungai) = 14 distrik. Batas sektor di kolom arteri: k 24-2, 2-6, 6-10, 10-13 (Skyway), 13-16, 16-20, 20-24.

| Sektor (kolom) | Pita dekat spaceport (za 150-1250) | Pita dekat sungai (za 1250-2500) |
| --- | --- | --- |
| 1 (24-2, boulevard trem) | **New York** (pusat kota, CBD) | **Kairo** (koridor trem) |
| 2 (2-6) | Kepler | **Delhi** (pusat ke-4) |
| 3 (6-10) | Galileo | Copernicus |
| 4 (10-13, sampai Skyway) | **Tokyo** (pusat ke-2) | Tsiolkovsky |
| 5 (13-16, dari Skyway) | Hypatia | Sagan |
| 6 (16-20) | **Shanghai** (pusat ke-3) | Chandrasekhar |
| 7 (20-24) | Ulugh Beg | Al-Battani |

Tebal = megacity (distrik yang memuat pusat kepadatan). Luar kota:

| Zona | Nama |
| --- | --- |
| Taman dan sungai, sisi s 0-3.141 | Taman Nil |
| Taman dan sungai, sisi seberang Skyway | Taman Mekong |
| Pertanian za 3.200-4.000 / 4.000-5.000 (hutan) / 5.000-6.000 / 6.000-6.400 | Punjab / Pampas / Iowa / Ukraina |
| Spaceport, Utilitas, Museum Cooper, Engineering | Tetap |

Halte trem ikut distrik: New York (625), Pasar New York (1125), Kairo (2125), Taman Nil (2950), Pampas (4800); lainnya tetap.

## Temuan kepadatan rumah (diukur, sesudah 15d)

Permintaan tambahan pemilik: rumah di lingkar terjauh dari kota harus makin jarang. Hasil ukur rumah per sel (241,7 x 250 m):

| Kepadatan sel (`cityDensity`) | Kelas | Sel | Rumah per sel |
| --- | --- | --- | --- |
| 0,4-0,5 | permukiman | 20 | 70 |
| 0,3-0,4 | permukiman | 100 | 64 |
| 0,2-0,3 | permukiman | 46 | 61 |
| 0,2-0,3 | tepi | 24 | 46 |
| 0,1-0,2 | tepi | 18 | 38 |

Per baris za rata-rata 53-62 rumah per sel dari za 250 sampai 2000, baru turun di baris terakhir (za 2250: 38). Jadi kepadatan hampir rata; penurunan hanya di tepi sungai. Penyebab: `fillHomes()` (15d) memakai kavling tetap 16-22 m dan gang di semua blok dalam, tanpa melihat jarak dari pusat.

## Sub-tahap

### 16a Gradasi kepadatan permukiman (perbaikan 15d)
- Bentuk dan ukuran kavling mengikuti kepadatan `d` (makin jauh dari pusat, makin kecil `d`):

| d | Bentuk | Kavling | Kavling kosong | Gang |
| --- | --- | --- | --- | --- |
| lebih dari 0,45 | rumah deret (tetap) | 7-9 m per unit | 0% | ya |
| 0,38-0,45 | rumah tunggal | 16-20 m | 0% | ya |
| 0,30-0,38 | rumah tunggal berhalaman | 20-26 m | 10% | hanya blok lebih dari 80 m |
| 0,22-0,30 | rumah besar | 26-34 m | 20% | tidak |
| kurang dari 0,22 (lingkar terluar, dekat sungai) | rumah desa berkebun, pohon lebih banyak | 36-50 m | 35% | tidak |

- Target: rumah per sel turun bertahap dari sekitar 70 ke sekitar 20. Uji: rata-rata rumah per sel turun menurut kelompok `d` (monoton), dan per baris za dari pusat ke sungai.

**Hasil 16a (selesai):** fungsi baru `homeDensity(s, za)`: pengaruh keempat pusat dengan jari-jari 1,6x dan tanpa lantai 0,34, jadi turun terus menjauhi pusat dan ke arah sungai. Ambang tingkat dikalibrasi ke kuintil sel permukiman (0,47 / 0,33 / 0,21 / 0,07), tiap tingkat sekitar 20% sel. Lingkar terluar (desa) tanpa baris samping, dengan kebun buah di belakang rumah.

| Tingkat | Sel | Rumah per sel (sebelum 16a: rata 53-70) |
| --- | --- | --- |
| Rumah deret | 40 | 117 |
| Rumah tunggal 16-20 m | 43 | 74 |
| Rumah berhalaman 20-26 m | 40 | 50 |
| Rumah besar 26-34 m | 44 | 34 |
| Desa berkebun 36-50 m | 41 | 14 |

Per baris za: puncak 90 rumah per sel (za 750), turun ke 53 (za 1500), 27 (za 2000), 16 (za 2250 di tepi sungai). Total rumah permukiman sama (sekitar 12.600). Biaya titik awal kota Ultra 3,20 jt, Hemat 1,14 jt segitiga. Uji `tools/uji_permukiman.py` (cek gradasi baru), `uji_trotoar` dan uji lama lulus.

### 16b Data distrik, nama, HUD
- `DISTRICTS` (id, nama, jenis mega/astro/taman/tani/lain, rentang kolom dan za, pusat) dan `districtAt(s, za)`.
- Nama halte trem diganti (entri `I18N.en` diperbarui).
- HUD: notifikasi "Distrik {nama}" (lewat `setLabText`/toast) saat pemain masuk distrik baru; nama distrik di baris lokasi HUD lengkap.

### 16c Pusat kota New York (downtown) dan balai distrik
- Blok dalam radius sekitar 350 m dari (s 0, za 480) dijadikan CBD: menara 60-150 m, podium, satu menara ikon orisinal sekitar 200 m (kaca, meruncing, puncak antena) di blok strategis dekat halte New York.
- Alun-alun (plaza) di depan halte New York dengan bangku dan pohon.
- Tiap distrik: balai distrik (gedung sipil rendah berpilar) di blok dekat simpang arteri paling tengah distrik.

### 16d Pasar
- Pasar New York: gedung pasar besar beratap lengkung + lapak terbuka di blok samping halte 1125 (akses trem).
- Pasar distrik: di tiap megacity (Tokyo, Shanghai, Delhi, Kairo) di blok pusat kepadatan dekat simpang besar; pasar lingkungan kecil (lapak saja) di tiap distrik astronom di blok tengah.
- Pasar tani Taman Nil di halte Taman Nil (2950), di tepi pertanian.
- Lapak: meja dan tenda warna-warni sebagai satu `InstancedMesh` dengan LOD radius (pola `FURN`); pedagang dan pembeli = pejalan kaki `still` dan `seg` di pasar (pola `PEDS`).

### 16e Taman distrik, sekolah, rumah sakit
- Tiap distrik satu taman distrik di blok dekat pusat distrik (bukan blok pasar/balai), dengan jalur keliling dan jalur silang (`PARK_PATHS`), pohon, bangku, kolam kecil di megacity. Taman acak lama tetap dipertahankan.
- Sekolah (gedung rendah + lapangan) satu per distrik astronom; rumah sakit di New York dan Delhi. Menggantikan bangunan `#d9c9a8` acak lama secara terarah.

### 16f Peta
- Batas distrik (garis putus tipis) dan nama distrik di pusat distrik (megacity lebih besar), tampil saat zoom cukup; nama zona luar kota baru.
- Ikon fasilitas: pasar, balai, taman distrik, sekolah, rumah sakit, masjid, gereja, menara ikon; tombol lapisan di legenda (Distrik, Fasilitas).
- Penanda klik-pindah baru: Pusat New York, Pasar New York, Pasar tani Taman Nil (huruf, bukan tombol keyboard).
- Legenda: bagian Distrik (daftar, klik = pindah ke pusat distrik) dan Fasilitas.

## Berkas

- `experiences/cooper-station/index.html`: `DISTRICTS`, loop penempatan kota (CBD, balai, pasar, taman, sekolah), `TRAM.stops`, HUD, `drawMap`/`buildMapLegend`/`MAP_MARKS`, `I18N.en`.
- `tools/uji_permukiman.py` ditambah cek gradasi kepadatan (16a).
- Uji baru `tools/uji_distrik.py`: tiap sel kota tepat satu distrik, nama unik, tiap distrik punya taman dan balai, pasar di tempat yang direncanakan (jarak ke halte atau simpang), tanpa bangunan bertumpuk atau di trotoar, toast distrik muncul saat pindah, peta menggambar label dan ikon.
- Dokumen: `docs/cooper-station/rencana-tahap-16-cooper-station.md`, `CLAUDE.md`, `README.md`.

## Verifikasi

- Tiap sub-tahap: halaman termuat tanpa error, uji baru lulus, uji lama tetap lulus (khususnya `uji_permukiman`, `uji_trotoar`, `uji_peta`, `uji_bahasa`, `uji_pejalan_kaki`, `uji_lalu_lintas`).
- Biaya segitiga Ultra dan Hemat di pusat kota dicatat.
- Pemilik mengecek visual dan FPS.
