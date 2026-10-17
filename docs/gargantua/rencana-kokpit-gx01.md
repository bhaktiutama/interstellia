# Rencana kokpit GX-01 lebih detail + melihat sekitar dengan mouse

Per 17 Oktober 2026 · Bhakti · Revisi 1 (rencana, belum dikerjakan)

## Ringkasan

- **Melihat sekitar (K1):** di kokpit, mouse menggerakkan kepala pilot (yaw / pitch) tanpa mengubah sikap wahana dan fisika misi. Arah hidung pindah ke seret kanan / Ctrl + seret (sama dengan kamera luar). Dikerjakan pertama karena kecil, berdampak besar, dan memakai jalur yang sudah ada untuk kepala VR (`GV.head` di `viewBasis()`).
- **Kokpit lebih padat (K2-K4):** interior sekarang hanya 76 segitiga (lantai, konsol, panel layar, 2 konsol samping, ambang). Rencana menambah glare shield, rangka kanopi tebal berlampu, bezel layar, deret tombol, layar samping, tongkat dan tuas, kursi, strip LED, dan pencahayaan kabin dari layar (material memancar baru).
- **Layar dan HUD kanopi (K5-K6):** MFD digambar ulang lebih tajam dan rapi (gaya panel seperti foto kanan), lalu HUD di kaca: penanda pusat lubang hitam, vektor gerak, pita arah, dan panel misi yang menempel di kaca. Semua angka tetap dari simulasi; angka hiasan di foto kanan (AU, Titan, Earth, radiasi) tidak ditiru karena tidak punya dasar di model.

## Perbandingan foto (kiri = sekarang, kanan = rujukan)

| Bagian | Sekarang (kiri) | Rujukan (kanan) | Rencana |
| --- | --- | --- | --- |
| Rangka kanopi | Batang 6 cm polos krem, terang rata | Rangka tebal gelap dengan lampu indikator kecil jingga / sian | K2: rangka 2 lapis (luar gelap doff, dalam lis), lampu indikator di rangka (material memancar) |
| Dasbor | Satu panel miring, 3 layar, tepi tipis | Glare shield di atas layar, bezel tebal, dasbor bertingkat | K2: glare shield, bezel per layar, dasbor 2 tingkat |
| Konsol samping | Kotak polos | Deret tombol berlabel (FLIGHT, NAV, COMMS, ...), layar kecil miring | K3: deret tombol (geometri + label tekstur), layar samping kiri / kanan |
| Pencahayaan kabin | Cahaya piringan lewat kanopi + ambien tetap 0,05 | Pendar layar biru-sian, strip LED, tepi menyala | K4: pendar layar dan LED di shader interior, AO per verteks |
| Layar kiri | Grafik r terhadap waktu wajar, sebagian besar kosong | TRAJECTORY + gambar lubang hitam + kurva GRAVITY WELL | K5: grafik r + peta corong G8 (`drawFunnel()`) = "sumur gravitasi" yang benar |
| Layar tengah | Teks data, huruf kecil | SCIENCE LOG + skema wahana + tab bawah | K5: data utama lebih besar, skema GX-01 dengan kerusakan kanopi, tab halaman |
| Layar kanan | Teks langit, delta-v, dorongan | MANEUVER & CONTROL: autopilot, bola sikap, bar dorong %, lingkungan | K5: autopilot, sikap X aktif disorot, bola sikap, bar delta-v, lingkungan (pasang surut, gas, suhu piringan di r wahana) |
| HUD di kaca | Tidak ada (HUD HTML kiri atas) | Pita arah, reticle tengah, jarak, panel MISSION / SYSTEMS / NAVIGATION | K6: penanda di tak hingga (pusat lubang hitam, vektor gerak, gerbang tesseract) + panel tempel kaca |
| Pandangan | Terkunci ke hidung, FOV 75 | Sama (gambar diam) | K1: kepala bebas + roda = FOV |

Catatan hak cipta: foto kanan memuat nama dan logo kapal lain. Nama, logo, dan bentuk tidak ditiru; yang diambil hanya kepadatan detail, palet (gelap + sian + jingga), dan susunan panel. Wahana tetap GX-01 desain sendiri.

## Keadaan kode sekarang (dasar rencana)

| Item | Keadaan | Lokasi |
| --- | --- | --- |
| Model | 5.556 segitiga: badan 5.436, kaca 44, interior 76; mata pilot (0, 1,0, -13,0) m | `assets/gx01.data.js` dari `tools/siapkan_wahana_gx.mjs` |
| Interior | Lantai, badan konsol, panel layar miring 30 derajat (2,3 x 0,56 m), 2 konsol samping, 2 ambang | `siapkan_wahana_gx.mjs` bagian "interior kokpit" |
| Layar | 3 quad 0,66 x 0,44 m, atlas kanvas 1152 x 256, diperbarui tiap 200 ms | `MFD`, `drawMFD()` |
| Shader | `SHIP_FS`: material 0 badan, 1 kaca (dibuang dari dalam), 2 interior (cahaya piringan x `through` + 0,05 tetap); `uMode` 0 badan, 1 stensil, 2 layar | `SHIP_VS` / `SHIP_FS`, `drawShip()` |
| Kamera kokpit | Basis = sikap wahana `MIS.att`, FOV 75; seret = hidung (bebas) atau arah lintasan (`track`) | `viewBase()`, handler `pointermove` |
| Kepala VR | `GV.head` memutar basis dan menggeser mata raster; ray tracer ikut basis | `viewBasis()` |
| Partikel | `uEye` = `SHIP.data.eye` di kokpit | `drawParts()` |
| Roda | Saat misi = jarak kamera luar (di kokpit tidak berefek) | handler `wheel` |

## K1: melihat sekitar dengan mouse

Tujuan: di kokpit pemain bisa menoleh ke samping (lengan garpu, piringan di bawah), ke atas (kanopi), dan ke dasbor tanpa mengubah arah hidung, sikap X, autopilot, atau lintasan.

| Aspek | Usulan |
| --- | --- |
| Masuk | Klik kiri di kanvas saat kokpit = kunci kursor (Pointer Lock), seperti klik mouse di Copper. Klik lagi atau Esc pertama = lepas (Esc kedua tetap mengakhiri misi) |
| Tanpa kunci | Seret kiri = menoleh (pengganti cara lama "seret = hidung" di kokpit). Dipakai bila Pointer Lock ditolak browser |
| Hidung | Seret kanan atau Ctrl + seret = hidung / arah lintasan, persis seperti di kamera luar sekarang. Saat kursor terkunci: tahan klik kanan + gerak = hidung |
| Batas | Yaw +-140 derajat, pitch -60 sampai +80 derajat (leher manusia + putar badan di kursi) |
| Leher | Kepala berputar di titik leher 0,10 m di belakang dan 0,12 m di bawah mata, jadi mata ikut bergeser beberapa cm: rangka kanopi berparalaks, terasa seperti kepala sungguhan |
| Halus | Pegas teredam kritis (laju 14 / s) dari target mouse ke sudut kepala, supaya tidak patah-patah di 30 FPS |
| Kembali | Klik ganda = kepala kembali ke depan (sama dengan klik ganda kamera luar). R tidak dipakai karena R = dorong naik saat misi |
| Roda | Di kokpit = FOV 50-95 derajat (kini roda tidak berefek di kokpit) |
| Ponsel | Satu jari = menoleh; dua jari geser = hidung (keputusan pemilik di bawah) |
| VR | Mouse-look mati saat `GV.on` (kepala dari headset); kedua rotasi tidak ditumpuk |
| Kamera rangefinder (K) | `camAllowed()` tetap (di luar misi atau jeda); kepala ikut dipakai sebagai arah bidik |

Implementasi (perkiraan fungsi yang disentuh):

| Langkah | Isi | Fungsi / file |
| --- | --- | --- |
| K1a | Keadaan `CKP = { yaw, pitch, ty, tp, fov, lock }`, nol saat `startMission()` dan saat V masuk kokpit | blok `SHIP` |
| K1b | `viewBase()` cabang kokpit: basis S diputar yaw (sumbu `S.u`) lalu pitch (sumbu kanan baru); mata = `shipToWorld(S, leher + rot(offsetMata))`. Bentuk sama dengan cabang `GV.head` sehingga ray tracer, aberasi `obs`, dan raster tetap selaras. Kepala nol = basis lama persis | `viewBase()` / `viewBasis()` |
| K1c | Handler input: Pointer Lock, `movementX/Y`, pemetaan baru seret kiri / kanan di kokpit, roda = FOV, klik ganda | handler `pointerdown` / `pointermove` / `wheel` / `dblclick` |
| K1d | Partikel dan tumbukan kaca memakai mata yang sudah digeser (bukan `SHIP.data.eye` tetap) | `drawParts()` (`uEye`), `drawImps()` |
| K1e | Guncangan `MIS.shake` diterapkan setelah kepala (tetap); `drawGateMark()` dan HUD yang memproyeksikan arah memakai basis kepala | `viewBase()`, `drawGateMark()` |
| K1f | Teks bantuan, `tombol.md`, kamus `ID`, toast "Kursor terkunci: gerakkan mouse untuk menoleh" | `ID`, `buildHelp`, `docs/app/tombol.md` |

Risiko: rendah. Ray tracer sudah menerima basis apa pun (dipakai VR). Yang perlu dijaga: kepala nol harus memberi gambar identik dengan sebelum K1 (diuji per piksel seperti uji G2).

## K2: rangka kanopi, glare shield, dasbor (geometri)

Dikerjakan di `tools/siapkan_wahana_gx.mjs` (alat olah), keluaran `gx01.data.js` dibuat ulang. Badan luar tidak berubah.

| Bagian | Isi | Perkiraan segitiga |
| --- | --- | --- |
| Rangka kanopi | Batang 6 cm diganti profil U 9 cm (lis dalam lebih terang, luar gelap doff), sambungan sudut berbevel | +400 |
| Glare shield | Atap dasbor melengkung di atas panel layar, menahan cahaya piringan dari kaca (layar lebih terbaca) | +120 |
| Bezel layar | Bingkai 2 cm per layar, sekrup sudut, tombol tepi 6 per sisi (gaya MFD pesawat) | +600 |
| Dasbor 2 tingkat | Tingkat bawah dengan panel tombol tengah (autopilot, sikap X, suar) | +300 |
| Kursi | Sandaran kepala dan bahu terlihat saat menoleh ke belakang (yaw > 100 derajat) | +500 |
| Lantai dan pedal | Pelat lantai berpanel, sandaran kaki | +150 |

Total K2 sekitar +2.000 segitiga (interior 76 menjadi sekitar 2.100; seluruh wahana 5.556 menjadi sekitar 7.600). Format verteks tetap (int16 1 mm, normal int8, warna uint8, material uint8), aset naik sekitar 100 KB.

## K3: konsol samping, tombol, tongkat dan tuas

| Bagian | Isi |
| --- | --- |
| Deret tombol | Konsol kiri: tombol mode (FLIGHT, NAV, COMMS, SCI, MAP sebagai label buatan sendiri, bukan teks foto), konsol kanan: DOCKING, CARGO, MAP, DATABASE diganti fungsi yang ada di misi (RELAY, FUNNEL, FLARE, AUTOPILOT, CANOPY) |
| Label | Satu atlas kanvas label kecil (seperti stensil GX-01, jalur `uMode` 1 yang sudah ada), dua bahasa lewat `txt()` |
| Layar samping | Dua layar kecil miring di konsol samping: kiri = jendela relai (`drawRelay()`), kanan = peta corong (`drawFunnel()`); kedua gambar sudah ada sebagai panel HTML, jadi hanya dipindah ke atlas MFD |
| Tongkat dan tuas | Tongkat kanan dan tuas gas kiri, bergerak mengikuti `MIS.thr` (dorongan W/S A/D R/F) dan Shift, seperti `stickAt` / `throttleAt` KS-07 v5 tetapi geometri GX-01 sendiri; digambar sebagai bagian terpisah dengan matriks sendiri |
| Indikator | Lampu kecil di tombol sesuai keadaan: autopilot (O), sikap X, suar (E), kaca > 60% (merah berkedip) |

## K4: pencahayaan kabin (shader)

| Item | Isi | Catatan GPU |
| --- | --- | --- |
| Material 3 memancar | LED, lampu indikator, tepi tombol: warna verteks x intensitas, tidak dicahayai; masuk bloom (digambar sebelum bloom seperti sekarang) | Tanpa cabang baru di badan |
| Pendar layar | Tiap layar = cahaya area sederhana (titik di tengah layar, jatuh 1 / (1 + d^2), dikali kecerahan rata-rata layar dari kanvas), sian-biru ke interior | `max()` pada pembagi, tanpa `normalize` vektor nol |
| AO per verteks | Dihitung di alat olah (sinar pendek dari tiap verteks interior), disimpan di kanal warna, tanpa biaya GPU | Hanya interior |
| Kilap interior | Spekular lemah (doff) untuk cahaya piringan lewat kanopi | `pow(max(...), k)` basis tak negatif |
| Pantulan di kaca dari dalam | Opsional: kaca kanopi tidak lagi dibuang dari dalam, digambar aditif sangat redup (pantulan pendar layar, Fresnel) | Diputuskan setelah uji K2-K3; bisa mengganggu pandangan |

Label: shader kustom = High menurut CLAUDE.md (rawan NaN di M1).

## K5: layar MFD baru

| Item | Isi |
| --- | --- |
| Resolusi | Atlas 1152 x 256 menjadi 5 layar x 512 x 352 (3 dasbor + 2 samping) di satu kanvas 2560 x 352 (lebar < 4096 aman di semua GPU) |
| Unggah | `texSubImage2D` per layar yang berubah; layar kiri dan samping 4 Hz, tengah dan kanan 8 Hz; tidak diunggah bila kepala menghadap jauh dari dasbor (layar di luar layar) |
| Gaya | Latar biru gelap, garis panel tipis sian, judul kecil berhuruf kapital, tab halaman di bawah, angka besar; aksen jingga untuk peringatan |
| Layar kiri "LINTASAN" | Grafik r terhadap waktu wajar (sudah ada, kini dengan sumbu dan label) + peta corong mini (G8) = sumur gravitasi yang benar |
| Layar tengah "DATA" | r (rs dan km), status horizon, waktu wajar, prakiraan, pasang surut, laju waktu; skema GX-01 dari samping dengan kerusakan kanopi `MIS.glass` |
| Layar kanan "MANUVER" | Autopilot (ON / OFF, h, laju turun), daftar sikap X dengan yang aktif disorot, bola sikap (sudut hidung terhadap arah pusat dan bidang piringan), bar delta-v, bar dorong per sumbu, lingkungan: pasang surut, kecepatan gas relatif, suhu piringan di r wahana |
| Halaman | Klik pada layar saat kursor terkunci (titik tengah layar = reticle) mengganti halaman layar itu; tanpa kunci, tombol konsol |

Angka yang dipakai hanya yang dihitung simulasi (`misData()`, `MIS`, `REL`, `predText()`). Suhu piringan di r wahana memakai rumus yang sama dengan `shadeDisk()` (`Tn` x 7.500 K di `SCENE_FS`); kembaran JS ditulis dan diuji terhadap shader. Angka di foto kanan seperti "12,02 AU", radiasi 0,12 mSv/h, Titan, Saturnus, Earth tidak dipakai: tidak ada dasarnya di model, dan 12,02 di foto sebenarnya r dalam rs.

## K6: HUD di kaca kanopi

| Lapisan | Isi | Cara gambar |
| --- | --- | --- |
| Penanda di tak hingga (collimated) | Pusat lubang hitam (arah tampak `bhRadiant()`, dengan jarak r dan km), vektor gerak relatif kerangka rain, arah gerbang tesseract (G5, kini `drawGateMark()`), cincin ISCO saat susur | Arah dunia diproyeksikan dengan basis kepala, dipotong ke bidang kaca depan (combiner), warna sian; tetap di langit saat menoleh |
| Pita arah | Pita sudut di atas kaca depan relatif bidang piringan (0 = arah putaran piringan) | Sama dengan penanda, terikat ke hidung |
| Panel tempel kaca | Panel MISI (tujuan skenario, langkah), SISTEM (kanopi %, delta-v %, autopilot, suara) di kaca samping | Quad tekstur di ruang wahana (seperti layar), aditif, ikut bergerak saat menoleh |

Penanda di tak hingga butuh arah tampak yang benar (aberasi kerangka pengamat, `bhRadiant()`), jadi K6 = High. Panel tempel kaca = Medium.

## Kelompok menurut effort, model, dan thinking

| Kelompok | Tahap | Isi | Effort | Model | Thinking | File / fungsi utama | Risiko |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | K1a-K1e | Kepala bebas, Pointer Lock, pemetaan seret baru, roda FOV, mata ikut leher | Medium | Sonnet 5.5 | medium | `viewBase()`, handler input, `drawParts()`, `drawImps()` | Rendah (jalur VR sudah ada) |
| 1 | K1f | Teks bantuan, kamus `ID`, `tombol.md`, CLAUDE.md | Low | Haiku 4.5 | low | `ID`, bantuan, dokumen | Rendah |
| 2 | K2 | Rangka kanopi, glare shield, bezel, dasbor 2 tingkat, kursi | Medium | Sonnet 5.5 | medium | `tools/siapkan_wahana_gx.mjs`, `gx01.data.js` | Rendah |
| 2 | K3 | Konsol tombol, label, layar samping, tongkat dan tuas bergerak | Medium | Sonnet 5.5 | medium | alat olah, `drawShip()`, atlas label | Rendah |
| 3 | K4 | Material memancar, pendar layar, AO verteks, kilap interior | High | Opus 5.5 | high | `SHIP_FS`, alat olah (AO) | Sedang (NaN M1) |
| 3 | K5 | MFD 5 layar baru, unggah per layar, halaman | Medium | Sonnet 5.5 | medium | `MFD`, `drawMFD()`, `misData()` | Rendah |
| 3 | K5 suhu | Kembaran JS suhu piringan = `shadeDisk()` | High | Opus 5.5 | high | `SCENE_FS` (baca saja), fungsi JS baru | Rendah |
| 4 | K6 | Penanda HUD di tak hingga (aberasi), pita arah | High | Opus 5.5 | high | fungsi HUD baru, `bhRadiant()`, `drawGateMark()` | Sedang |
| 4 | K6 panel | Panel tempel kaca | Medium | Sonnet 5.5 | medium | `drawShip()`, atlas | Rendah |
| tiap kelompok | uji | `tools/uji_misi_gargantua.py` kelompok 10 | Medium | Sonnet 5.5 | medium | skrip uji | Rendah |

Tugas terberat High, jadi rencana disusun model Opus 5.5. Urutan: kelompok 1 dulu (bisa diuji pemilik sendiri tanpa menunggu geometri), lalu 2, 3, 4. Tiap kelompok berhenti untuk uji pemilik.

## Uji (kelompok 10 di `tools/uji_misi_gargantua.py`)

| Uji | Kelompok |
| --- | --- |
| Kepala nol = gambar identik dengan commit sebelum K1 (0 piksel berbeda, kokpit dan kamera luar) | 1 |
| Menoleh tidak mengubah `MIS.att`, `MIS.x`, `MIS.xd`, `MIS.lock`, prakiraan | 1 |
| Seret kanan / Ctrl di kokpit = hidung; seret kiri = kepala; klik ganda = kepala nol; roda = FOV dalam batas | 1 |
| Batas yaw / pitch, render tanpa nilai tidak valid di yaw 140 derajat dan pitch -60 / +80 | 1 |
| VR tiruan: mouse-look mati saat `GV.on` | 1 |
| Aset: jumlah segitiga per material, normal tidak nol, mata di dalam kabin, layar di depan bezel | 2 |
| Tongkat dan tuas bergerak sesuai `MIS.thr` | 2 |
| Render kokpit siang (dekat piringan) dan gelap (jauh) tanpa nilai tidak valid; material memancar masuk bloom | 3 |
| Atlas MFD 5 layar tergambar, unggah per layar, tanpa error saat bahasa diganti | 3 |
| Suhu piringan JS = shader (selisih < 1%) di r 3, 6, 12 rs | 3 |
| Penanda pusat lubang hitam berimpit dengan pusat bayangan di gambar ray tracer (< 1 derajat) saat diam dan saat bergerak 0,5 c | 4 |
| Waktu frame kokpit sebelum / sesudah (SwiftShader, hanya pembanding) | tiap kelompok |

## Keputusan pemilik (usulan bawaan, boleh diganti)

| Item | Usulan bawaan | Pilihan lain |
| --- | --- | --- |
| Cara menoleh | Klik = kunci kursor, gerak mouse = menoleh (seperti Copper) | Tanpa kunci: kepala mengikuti posisi kursor di layar (tepi = menoleh jauh) |
| Hidung di kokpit | Seret kanan / Ctrl + seret (sama dengan kamera luar) | Tetap seret kiri, menoleh dengan tombol tengah |
| Kepala kembali sendiri | Tidak (klik ganda) | Kembali ke depan pelan setelah 3 s diam |
| Ponsel | Satu jari menoleh, dua jari hidung | Satu jari hidung seperti sekarang, tanpa menoleh |
| Pantulan layar di kaca | Ditunda sampai uji K4 | Langsung dibuat |
| HUD kanopi | Sian, bisa dimatikan (H sudah menyembunyikan UI) | Jingga seperti layar sekarang |

## Status

| Tahap | Status |
| --- | --- |
| K1 | Selesai 17 Oktober 2026: kepala pilot `CKP` (pegas teredam kritis 14 / s, leher 0,10 m di belakang dan 0,12 m di bawah mata), klik = kunci kursor, seret kiri / satu jari = menoleh, seret kanan / Ctrl / tahan klik kanan = hidung, dua jari = hidung, roda = FOV 50-95, klik ganda = depan, Esc pertama melepas kursor; VR mengabaikan kepala mouse. Uji kelompok 10 di `tools/uji_misi_gargantua.py` 15/15 lulus (SwiftShader), termasuk render kepala nol identik 0,000% dengan commit sebelum K1. Belum diuji di GTX 1060 dan M1 |
| K2-K6 | Belum dikerjakan |
