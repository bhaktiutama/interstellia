# Rencana tahap 30 Copper Corn Station: Jupiter sebagai pilihan planet, orbit dekat

Per 22 Oktober 2026 · Status: J1-J4 dikerjakan, J5 (tur) tidak diubah, J6 uji ditulis (`tools/uji_planet.py`); menunggu uji visual dan FPS pemilik · Pemilik: Bhakti · Lanjutan: bulan di `rencana-tahap-31-bulan-cooper-station.md`

## Ringkasan

- Pemain memilih **Saturnus** (bawaan, tidak berubah) atau **Jupiter** di layar mulai. Pilihan berlaku sejak muat halaman (muat ulang saat diganti), jadi seluruh kode jauh, gerhana, tur, dan HUD memakai satu tabel `PLANET`.
- Jupiter diorbit lebih dekat supaya terasa besar: **150.000 km** (2,10 radius Jupiter dari pusat). Dari stasiun, Jupiter tampak berdiameter sudut **56,9 derajat**, dibanding Saturnus **26,8 derajat** dari 260.000 km. Luas sudut piringan 4,23 kali lebih besar.
- Periode orbit turun dari 37,57 jam menjadi **9,01 jam**; gerhana tiap orbit **1,42 jam** (Saturnus 2,80 jam). Gerhana jadi 4,2 kali lebih sering.
- Pekerjaan utama: tabel planet (J1), shader Jupiter (J2), umum-kan gerhana dan cahaya (J3), pemilih dan teks (J4), tur dan uji (J5). Saturnus harus render identik dengan sebelum tahap ini (uji piksel).
- Satu keputusan butuh pemilik: radius orbit (bagian Pilihan). Saran: 150.000 km, bukan 160.000 km (orbit sinkron, wajah planet tidak berputar).

## Status (22 Oktober 2026)

Keputusan pemilik: orbit **150.000 km**, cincin Jupiter ditunda (tanpa cincin), pemilih di layar mulai (muat ulang saat ganti), halaman detail tetap Saturnus.

| Langkah | Hasil |
| --- | --- |
| J1 tabel planet | `PLANETS` / `PLANET` (dibaca sekali: `?planet=` lalu localStorage `cooperStation.planet`), `SATURN`, `ORBIT`, `T_ORB`, `SAT_SPIN`, `SUN_ANG`, `uSatCol` mengikuti planet; nama lama dipertahankan (alias) |
| J2 shader Jupiter | `JUP_FS`: pita `JUP_BANDS`, zona ekuator 1% lebih cepat (`spinWrap` 100 agar putaran menutup), tepi sabuk bergelombang, festoon, Bintik Merah Besar (22 derajat selatan), 3 oval putih, kutub lebih gelap; tanpa pow basis negatif. Cincin hanya Saturnus |
| J3 gerhana dan cahaya | Rumus `ECL.half`, penumbra `SUN_ANG` (0,1026 derajat), `limbMat` warna per planet, `uSatCol` Jupiter = Saturnus x 4,2 (tebakan awal, disetel mata) |
| J4 pemilih, HUD, teks | `#planetPick` di kartu mulai, `t()` mengganti "Saturnus" / "Saturn" dengan nama planet dan angka periode / lama gerhana di bantuan, `data-notr`, kamus "Planet", deskripsi kartu menu |
| J5 tur | Tidak diubah: tur memakai `T_ORB` / `ECL` / `tourSatAt()` secara umum; belum diperiksa visual untuk Jupiter (sudut penutup 115-245 derajat dari gerhana) |
| J6 uji | `tools/uji_planet.py` (periode, gerhana, diameter sudut, teks, pemilih, render, Saturnus identik lewat `?bulan=0`) |

### Revisi 22 Oktober 2026 (permintaan pemilik: Jupiter harus terasa sangat dekat)

| Item | Sebelum | Sesudah | Dasar |
| --- | --- | --- | --- |
| Radius orbit | 150.000 km | **82.550 km** | `r = R / sin(60 derajat)`, R ekuator 71.492 km (NASA) |
| Diameter sudut planet | 56,9 derajat | **120,0 derajat** | `2 asin(R / r)` |
| Periode orbit | 9,008 jam | **3,678 jam** | Kepler, GM 1,26687e17 m3/s2 |
| Gerhana per orbit | 1,42 jam | **1,226 jam** | `2 asin(R / r) / 360 x T` |
| Tinggi di atas puncak awan | 78.508 km | **11.058 km** | `r - R` |
| Permukaan planet | pita prosedural dan oval perkiraan | **peta global Hubble OPAL 2015 (NASA / ESA / A. Simon / OPAL Team, STScI-01EVT28CB7CN0CEYRV56WP1S6A)** (diganti dari Cassini PIA07782 atas permintaan pemilik karena lebih tajam; sumber 3600 x 1598 lintang +-80 derajat, kutub diisi; hasil 3600 x 1800, `assets/jupiter.data.js`, `tools/siapkan_jupiter.py`); Bintik Merah Besar, oval putih, dan pita adalah data asli | `?jupiter=prosedural` = tampilan prosedural lama |
| Cincin | tanpa cincin | sempat ditambah (kedalaman optik dibesarkan) lalu dihapus atas permintaan pemilik | tanpa cincin |
| Rotasi permukaan peta | zona ekuator 1% lebih cepat | putaran padat ke timur (prograde) periode 9,925 jam (beda 1% = 3,6 derajat per putaran, tidak terlihat) | - |

Revisi ketiga (permintaan pemilik: peta masih pecah): peta diganti `20180511_jupiter_map_css_plus_juno_bj.jpg` (Bjorn Jonsson, Cassini + Juno, The Planetary Society; 14400 x 7200, kutub penuh) diperkecil ke 8192 x 4096 (5,2 MB berkas data, sekitar 180 MB memori GPU; resolusi penuh 14400 butuh sekitar 550 MB). Orbit Jupiter bawaan 30x: pada 1x planet bergeser hanya 0,027 derajat per detik sehingga tampak diam; 30x = periode 7,4 menit; tombol T berputar 30, 100, 1000, 10000, 1; tur tetap memakai 1x.

Catatan: pada 82.550 km stasiun berada di bawah sistem cincin (halo mulai 92.000 km), jadi cincin hanya terlihat sebagai garis tipis ke arah luar. Peta Juno tidak dipakai (tidak ada sumber NASA langsung dengan lisensi jelas); Hubble OPAL dari aset NASA yang dikirim pemilik.

Hasil uji (SwiftShader): `tools/uji_planet.py` lulus: periode 37,570 / 9,008 jam, setengah sudut gerhana 13,40 / 28,46 derajat, diameter sudut 26,8 / 56,9 derajat, lama gerhana 2,790 / 1,421 jam, Saturnus identik dengan komit sebelum tahap 30 (0 nilai berbeda di 9 render langit jauh dengan `?bulan=0`). `tools/uji_gerhana.py` dan `tools/uji_bahasa.py` lulus. Belum diuji visual, FPS, dan NaN di GTX 1060 dan M1; tur (J5) belum diperiksa untuk Jupiter.

## Angka dasar

Sumber: NASA NSSDCA Jupiter Fact Sheet (diambil 21 Oktober 2026) dan perhitungan di bawah. Rumus: `T = 2 pi sqrt(r^3 / GM)`, sudut radius `asin(R / r)`, durasi gerhana `2 asin(R / r) / 360 x T` (sama dengan `ECL.half = asin(rEq / r)` di kode, mengabaikan penumbra).

| Besaran | Saturnus (sekarang) | Jupiter | Sumber |
| --- | --- | --- | --- |
| GM | 3,7931e16 m^3/s^2 | 1,26687e17 m^3/s^2 (massa 1.898,13e24 kg x G 6,6743e-11) | Lembar fakta NASA; G nilai baku |
| Radius ekuator | 60.268 km | 71.492 km (level 1 bar) | NASA |
| Radius kutub | 54.364 km | 66.854 km | NASA |
| Rotasi sideris | 10,56 jam (`SAT_SPIN` 38.018 s) | 9,9250 jam = 35.730 s (Sistem III) | NASA |
| Kemiringan sumbu | (cincin 15 derajat di `ORBIT.tiltDeg`) | 3,13 derajat | NASA |
| Albedo Bond | belum diambil | 0,343 | NASA |
| Jarak Matahari | 9,58 AU (dipakai `SUN_ANG`) | 5,204 AU (778,479 juta km) | NASA |
| Diameter sudut Matahari | 0,0557 derajat (`SUN_ANG`) | 0,533 / 5,204 = sekitar 0,1025 derajat (turunan: 0,533 derajat di 1 AU, perkiraan) | Perhitungan |
| Radius orbit stasiun | 260.000 km | 150.000 km (usulan) | Keputusan |
| Ketinggian dari awan | 199.732 km | 78.508 km | Perhitungan |
| Periode orbit | 37,57 jam | 9,008 jam | Perhitungan |
| Kecepatan orbit | sekitar 12,1 km/s (turunan `sqrt(GM/r)`) | 29,06 km/s | Perhitungan |
| Diameter sudut planet | 26,8 derajat | 56,9 derajat | `2 asin(R/r)` |
| Gerhana per orbit | 2,80 jam | 1,42 jam | `2 asin(R/r) / 360 x T` |

Alternatif radius orbit (semua dihitung dengan rumus di atas):

| r (km) | T (jam) | Diameter sudut | Luas sudut vs Saturnus | Gerhana (jam) | Catatan |
| --- | --- | --- | --- | --- | --- |
| 130.000 | 7,27 | 66,7 | 5,63 kali | 1,35 | Sangat besar; berada di sekitar cincin tipis Jupiter (radius cincin belum diverifikasi, dari ingatan sekitar 122.500 sampai 129.000 km) |
| **150.000** | **9,01** | **56,9** | **4,23 kali** | **1,42** | **Usulan** |
| 160.000 | 9,92 | 53,1 | 3,72 kali | 1,46 | Hampir sinkron dengan rotasi planet (radius sinkron dihitung 160.010 km): wajah planet nyaris diam di langit stasiun |
| 180.000 | 11,84 | 46,8 | 2,94 kali | 1,54 | |
| 200.000 | 13,87 | 41,9 | 2,38 kali | 1,61 | |

## Rancangan

| Topik | Keputusan |
| --- | --- |
| Pemilihan | `PLANETS = { saturn, jupiter }` dan `PLANET`. Urutan: `?planet=`, lalu localStorage `cooperStation.planet` (gaya kunci `cooperStation.preset`), lalu `saturn`. Ganti planet di panel = simpan lalu muat ulang (aman: `const` di kode jauh tidak perlu dibangun ulang saat jalan) |
| Alias | `SATURN`, `ORBIT`, `T_ORB`, `SAT_SPIN`, `SUN_ANG` tetap ada sebagai nama, nilainya diambil dari `PLANET`; objek `saturn` (Group) tetap bernama itu agar uji dan `window.__station` tidak patah. Nama baru `PLANET.key` dipakai teks |
| Orientasi | Geometri stasiun tidak berubah: sumbu 65 derajat dari normal orbit, Matahari 25 derajat dari sumbu di bidang orbit, gerhana tiap orbit. Hanya radius dan GM berganti |
| Kemiringan khatulistiwa terhadap bidang orbit | Parameter `PLANET.tiltDeg` (Saturnus 15 derajat seperti sekarang). Jupiter: nilai awal 12 derajat supaya Bintik Merah Besar (belahan selatan) terlihat; bukan data NASA, hanya pilihan tampilan |
| Cincin | Jupiter: cincin tipis hampir tak terlihat (alpha kecil) atau tanpa cincin pada versi pertama. Saran: tanpa cincin dulu |
| Cahaya planet ke stasiun | `uSatCol` (cahaya pantulan planet) naik dengan luas sudut dan albedo: skala awal sebanding `(R / r)^2 x albedo`, lalu disetel dengan mata dan batas agar adaptasi mata `ADAPT` tidak berubah liar. Cahaya Matahari di stasiun tidak diubah (jarak Matahari hanya dipakai untuk ukuran piringan Matahari) |
| Radiasi | Tidak dimodelkan. Plakat fiksi: stasiun berperisai. Tidak ada klaim angka dosis |
| Detail fisika | Halaman `detail.html` Copper memuat 14 rujukan Saturnus: tetap Saturnus pada versi pertama, diberi catatan "angka untuk orbit Saturnus" |

## Langkah

Effort mengikuti tabel di `CLAUDE.md`.

| No | Langkah | Isi | File dan fungsi | Effort | Model | Thinking |
| --- | --- | --- | --- | --- | --- | --- |
| J1 | Tabel planet | `PLANETS`, `PLANET`, alias lama, `T_ORB`, `ECL.half`, `SUN_ANG`, `SAT_SPIN`, kamera jauh `far` cukup (20.000 satuan = 20 juta km; Jupiter dan bulan masuk) | `experiences/cooper-station/index.html`: blok TAHAP 3 (`SATURN`, `ORBIT`, `T_ORB`, `RINGS`), `ECL`, `eclipseIn()` | Medium | Sonnet 5.5 | medium |
| J2 | Shader Jupiter | Bangun dari blok shader Saturnus (`SAT_U`, pita lintang `BANDS`, noise 3D, gelap tepi Minnaert): pita zona dan sabuk (palet krem, oker, cokelat karat, putih), geser diferensial, Bintik Merah Besar (oval di sekitar 22 derajat Lintang Selatan, dari ingatan, verifikasi), oval putih kecil, turbulensi di tepi pita, kutub lebih gelap, pepat 66.854 / 71.492. Tanpa heksagon kutub dan tanpa bayangan cincin. Pilih program lewat `PLANET.shader`; jumlah oktaf noise per preset (Hemat lebih sedikit) | `saturn.userData.U` (`SAT_U`), `planet` mesh, `limbMat`, `updateFar()` (`uSpin`) | High | Opus 5.5 | high |
| J3 | Gerhana dan cahaya | `ECL.half`, `eclipseIn()`, penumbra memakai `SUN_ANG` Jupiter, `glareMat`, cahaya tepi atmosfer (`limbMat`: warna dan tebal untuk atmosfer H2), `uSatCol`, lampu dermaga `ECL.dockLight`, tombol I | `updateEclipse()`, `jumpToEclipse()`, `ECL`, `LIGHT` | High | Opus 5.5 | high (kerangka inersia dan matematika gerhana) |
| J4 | Pemilih, HUD, teks | Pemilih di kartu mulai (`#presetPick` gaya sama) dan di panel Grafik; HUD `hSat` memakai nama planet; ubah teks "Saturnus" menjadi `{p}` (sekitar 25 kunci di `I18N.en`, termasuk caption tur, tombol T dan I, plakat) | `startEl`, `labTab`, `LABUI`, `uiLabel`, `I18N.en`, `translateDom()`; menu `index.html` (deskripsi kartu Copper "di orbit Saturnus atau Jupiter"), `README.md` | Medium | Sonnet 5.5 | medium |
| J5 | Tur dan kecepatan orbit | `TOUR` memakai `T_ORB` dan `ECL` secara umum; periksa `tourSatAt`, `tourOutroC`, `tourOutroPlan`, `K.oA`, `K.oB`; `ORBIT_SPEEDS` (1, 100, 1.000, 10.000x) tetap wajar untuk T 9,01 jam; teks caption `{p}`, `{eH}`, `{oH}` | `startTour()`, `stepTour()`, `TOUR` keys, `cycleOrbitSpeed()` | High | Opus 5.5 | high |
| J6 | Uji | Lihat bagian Uji | `tools/uji_planet.py` baru, `tools/uji_gerhana.py`, `tools/uji_bahasa.py`, `tools/uji_ladang_foto_tur.py` | Medium | Sonnet 5.5 | medium |

## Uji

| Uji | Isi | Kriteria |
| --- | --- | --- |
| Saturnus identik | Render 6 pandangan jauh (kamera luar V, end cap A dan B, gerhana) sebelum dan sesudah tahap | 0 piksel berbeda dengan commit sebelum tahap 30 (pola uji 20d) |
| Angka Jupiter | `T_ORB` = 9,008 jam, `ECL.half` = 28,46 derajat, diameter sudut dari kamera jauh = 56,9 derajat | Toleransi 0,05 jam dan 0,1 derajat |
| Gerhana | Lompat ke gerhana (I), durasi gerhana dan penumbra, sinar padam, tanpa nilai tidak valid | Durasi dalam 2% dari 1,42 jam |
| Tanpa NaN | Render HDR piringan Jupiter di 5 preset, pada pandangan dekat dan jauh | 0 nilai tidak valid, 0 titik > 50 |
| Bahasa | Kunci baru ada di `I18N.en`; label berganti nama planet tanpa muat ulang teks statis (nama planet berubah hanya setelah muat ulang) | `tools/uji_bahasa.py` lulus |
| Tur | Tur sinematik berjalan penuh untuk kedua planet tanpa error | Selesai, tanpa pesan konsol |
| Performa | Waktu frame pandangan penuh Jupiter (kamera luar) vs Saturnus di preset Tinggi dan Hemat, memakai `GPUT` | Dicatat; target Jupiter tidak lebih dari 1,5 kali Saturnus (tebakan, perlu diukur) |

Pemilik menguji visual, FPS, dan NaN di GTX 1060 dan M1.

## Pilihan untuk pemilik

| No | Pertanyaan | Pilihan | Disarankan |
| --- | --- | --- | --- |
| 1 | Radius orbit Jupiter | a. 150.000 km (periode 9,01 jam, 56,9 derajat) · b. 160.000 km (nyaris sinkron: planet nyaris tidak berputar dari stasiun, tiap pagi Bintik Merah Besar di tempat sama) · c. 130.000 km (terbesar, tetapi di sekitar cincin) | a |
| 2 | Cincin Jupiter | a. Tanpa cincin dulu · b. Cincin tipis hampir tak terlihat | a |
| 3 | Pemilih | a. Layar mulai + panel (muat ulang saat ganti) · b. Hanya `?planet=` | a |
| 4 | Halaman detail fisika | a. Tetap Saturnus dengan catatan · b. Ikut planet pilihan (kerja tambahan di `detail.html` dan diagram) | a |

## Risiko dan batasan

| Risiko | Penjelasan | Penanganan |
| --- | --- | --- |
| Beban piksel | Piringan Jupiter menutup luas sudut 4,23 kali Saturnus; shader noise 3D mahal per piksel di GTX 1060 dan M1 | Oktaf per preset, pengujian `GPUT`, preset Hemat dengan pita sederhana |
| Adaptasi mata | Planet sangat besar dan terang bisa menggeser `ADAPT` dan membuat bagian dalam stasiun gelap | Batas pada `uSatCol`; uji adaptasi (`tools/uji_cahaya_lanjut.py`) |
| Presisi | Permukaan Jupiter 78.508 km dari stasiun (78,5 satuan) dengan `near = 1` (1.000 km): aman. Bulan terjauh (tahap 31) sekitar 3,8 juta km (3.820 satuan, Iapetus) | Dicek dari kode: `far` 20.000 satuan = 20 juta km, jadi semua masuk |
| Angka dari ingatan | Posisi Bintik Merah Besar, radius cincin, dan nilai `tiltDeg` Jupiter bukan dari lembar fakta yang diambil | Diverifikasi di J2; `tiltDeg` ditandai sebagai pilihan tampilan |
| Gerhana lebih sering | 9 jam sekali: bisa mengganggu tur dan jadwal cahaya | J5 menyetel kunci tur; gerhana tidak mengubah jam stasiun |
| Pengukuran | Estimasi waktu kerja tidak diberikan | Hanya label effort |
