# Rencana Misi Gargantua: wahana GX-01 masuk lubang hitam

Per 4 Oktober 2026 · Bhakti · Revisi 2 (wahana baru, terbang rendah di atas piringan, partikel menabrak kaca)

## Ringkasan

- **Wahana baru GX-01 (usulan nama "Ambang"):** bukan KS-07. Model diambil dari blokout v3 (`docs/app/kestrel/blokout-ks07-v3.html`, panjang sekitar 27,5 m) yang kini tidak dipakai Millar maupun Copper (keduanya memakai v5). Stensil "KS-07" diganti "GX-01". Kode dan nama boleh diganti pemilik.
- **Masuk langsung, gaya foto 1:** wahana terbang rendah di atas permukaan piringan akresi. Piringan tampak seperti dataran bergolak di bawah, dinding cahaya (piringan sisi jauh yang dibelokkan) menjulang di samping, bayangan hitam di depan. Setelah lewat ISCO (3 rs) wahana menukik ke horizon.
- **Partikel menabrak kaca, gaya foto 2:** gas dan debu piringan melesat ke arah kamera sebagai garis bara jingga dan awan abu, sebagian menghantam kaca kokpit (kilat tumbukan, bekas pijar yang memudar). Bagian ini distilisasi: di dunia nyata satu butir debu 1 mikrogram pada 0,707 c membawa energi setara 8,9 kg TNT.
- Dua syarat lain tetap: informasi tidak bisa keluar dari horizon (G4) dan sudut masuk tesseract (G5, fiksi).

Urutan kerja: G1 wahana GX-01, G2 kamera jatuh dan jalur kutub, G3 terbang rendah dan partikel, G4 informasi, G5 tesseract, G6 uji dan bahasa.

Cara menjalankan di sesi baru: "jalankan kelompok 1 dari `docs/gargantua/rencana-misi-lubang-hitam.md`" (lalu kelompok 2, dan seterusnya). Tiap kelompok berhenti untuk diuji pemilik. Perbarui bagian Status tiap tahap selesai.

## Kelompok menurut effort, model, dan thinking (aturan CLAUDE.md "Pengelompokan task berdasarkan effort")

Label mengikuti tabel effort di CLAUDE.md: shader GLSL kustom, relativitas, dan bug sulit = High (Opus 5.5); fitur yang menyentuh beberapa bagian kode, partikel, alat olah, dan skrip uji = Medium (Sonnet 5.5); teks UI, entri kamus `ID`, dan dokumen = Low (Haiku 4.5). Tugas terberat High, jadi rencana ini disusun Opus 5.5 (tidak ada tingkat di atasnya selain Fable 5.1 untuk bug yang gagal dua kali).

Kolom Thinking = saran tingkat effort/thinking Claude Code (`/effort low`, `medium`, `high`, `xhigh`). Ini rekomendasi awal, belum diukur di proyek ini: naikkan satu tingkat bila hasil pertama salah.

| Kelompok | Tahap | Isi | Effort | Model | Thinking | Alasan | Risiko |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | G1a | Alat olah `tools/siapkan_wahana_gx.mjs`, aset `gx01.data.js`, stensil GX-01 | Medium | Sonnet 5.5 | medium | Alat seperti `siapkan_motor.py`, geometri sudah ada di `KESTREL.buildV3()` | Rendah |
| 1 | G1b | Raster GX-01 di Gargantua (program WebGL2 + depth, sebelum bloom), kokpit, kamera luar | Medium | Sonnet 5.5 | medium | Program raster kecil terpisah dari ray tracer; tidak menyentuh `SCENE_FS` | Rendah |
| 2 | G2 | Kamera jatuh di shader (`vel0`, aturan tertelan, aberasi, frekuensi), jalur kutub, HUD | High | Opus 5.5 | xhigh | Relativitas halus di dalam horizon, mudah NaN di M1 (`sqrt`, pembagian dekat r = 0), harus identik saat `uFall = 0` | Sedang |
| 3 | G3a | Piringan tebal volumetrik dekat kamera, jalur susur piringan | High | Opus 5.5 | high | Shader GLSL kustom, biaya GPU terbesar, harus menyatu dengan piringan tipis lama | Tinggi (FPS GTX 1060 dan M1) |
| 3 | G3b | Partikel garis bara, awan debu, tumbukan kaca, guncangan | Medium | Sonnet 5.5 | medium | Partikel dan overlay; kecepatan relatif sudah dihitung di rencana | Rendah |
| 4 | G4 | Pulsa ke relai, pandangan relai, diagram ruang-waktu, uji suar | High | Opus 5.5 | high | Koordinat tortoise menuju tak hingga di horizon, sinkron waktu wahana dan relai. Gambar diagram kanvas sendiri boleh Medium | Sedang |
| 5 | G5 | Bidik sudut, prediksi geodesik CPU, zoom-whirl, gerbang, hiperkubus | High | Opus 5.5 | high | Integrasi geodesik dekat orbit tak stabil 2 rs sangat peka (drift numerik). Hiperkubus sendiri Medium | Sedang |
| tiap kelompok | G6 | `tools/uji_misi_gargantua.py` (bagian per tahap) | Medium | Sonnet 5.5 | medium | Skrip uji baru = Medium di CLAUDE.md | Rendah |
| tiap kelompok | G6 | Entri kamus `ID`, teks panel dan bantuan, CLAUDE.md, `tombol.md`, `penamaan.md`, Status di dokumen ini | Low | Haiku 4.5 | low | Mekanis | Rendah |

Langkah mekanis di dalam tahap High (entri kamus, teks HUD, pembaruan dokumen) berlabel Low dan boleh diserahkan ke Haiku 4.5, sesuai aturan "pecah task High menjadi langkah kecil".

## Status

| Tahap | Status |
| --- | --- |
| G1a | Selesai 4 Oktober 2026: `tools/siapkan_wahana_gx.mjs` (Node, bukan Python: tidak perlu browser) membuat `experiences/gargantua/assets/gx01.data.js` dari `KESTREL.buildV3()`: 5.184 segitiga (dari 6.092; kaki pendarat dibuang di bawah y = -2,45 m), 102 verteks kaca kokpit, 264 KB. Stensil GX-01 = quad bertekstur kanvas di halaman |
| G1b | Selesai 4 Oktober 2026: V = wahana GX-01 (kamera luar 40 m di belakang, 7,5 m di atas), V lagi = kokpit (mata 0, 1,25, -7,2 m; kaca tidak digambar dari dalam, sekat tetap; dasbor kanvas), Esc keluar, tombol panel. Wahana menahan posisi di titik orbit kamera menghadap pusat; disinari dari titik piringan terdekat. Uji `tools/uji_misi_gargantua.py` 13/13 lulus (SwiftShader). Belum diuji di GTX 1060 dan M1. Catatan: tangkap layar dan mode foto tidak memuat dasbor kokpit (lapisan HTML) |
| G2 | Selesai 4 Oktober 2026 (lihat bagian G2 di bawah): kamera jatuh di shader (`uFall`), 7 skenario jatuh, kendali terbatas (dorongan W/S A/D R/F, Shift, anggaran delta-v), sikap X (pusat / mendatar / bebas), waktu Z, HUD dan 3 layar MFD, layar akhir. Kokpit diganti pod kaca di depan (permintaan pemilik: pandangan tidak lagi tertutup 2 lengan). Uji 35/35 lulus (SwiftShader). Belum diuji di GTX 1060 dan M1 |
| G3a | Selesai 4 Oktober 2026 (lihat bagian G3): jalur susur piringan dengan autopilot (2 skenario baru, melawan dan searah arus gas), lempeng piringan tebal volumetrik di sekitar kamera (derau 3D, menyambung dengan piringan tipis), disk berputar menurut waktu wajar wahana selama misi, eksposur otomatis misi. Belum diuji di GTX 1060 dan M1 |
| G3 perbaikan beban GPU | 4 Oktober 2026, laporan pemilik: setelah G3 Ultra hanya 10 FPS, pandangan susah digerakkan, juga di luar misi. Sebab: kode lempeng tebal ikut terkompilasi di shader utama walau tidak dipakai (register dan cabang tambahan di loop sinar). Perbaikan: shader dipisah jadi dua varian (`VOL 0` = kode G2 persis, `VOL 1` hanya saat dekat piringan), satu panggilan `shadeDisk()` per langkah, sampel dan radius lempeng diturunkan, `textureLod`. Terukur di SwiftShader (bukan GPU nyata): tampilan biasa Sedang 2.173 ms menjadi 1.214 ms per frame (G2: 1.198), Ultra 4.906 menjadi 2.822 (G2: 2.639); susur di 6 rs Sedang 1.459 menjadi 966 ms. Belum diukur di GTX 1060 dan M1 |
| G3b | Selesai 4 Oktober 2026: garis bara (partikel GPU), awan debu, tumbukan kaca kokpit (kilat, pijar, retak menetap), guncangan, kerusakan kaca (100% = akhir misi), label distilisasi di panel dan layar akhir |
| Masukan pemilik setelah G3 | 4 Oktober 2026: saat misi, seret mouse di kamera luar memutar sikap wahana sehingga yang tampak berputar adalah lingkungan lubang hitam, wahana tidak bisa dilihat dari sudut lain. Perbaikan: di kamera luar seret = kamera mengitari wahana (`MIS.orb`, hanya kamera, sikap dan fisika tidak berubah), klik ganda = kembali ke belakang wahana, seret kanan (atau Ctrl + seret) = arah hidung seperti dulu. Di kokpit seret tetap arah hidung. Kolom nilai HUD digeser sedikit dan dipadatkan agar label "Pasang surut 2 m" dan prakiraan panjang tidak saling tumpuk. Bug kecil G3 ikut diperbaiki: saat misi diulang, satu hasil baca terang dari adegan misi sebelumnya bisa terpakai sebagai ukuran pertama eksposur otomatis (sekarang diabaikan) |
| G4 | Selesai 4 Oktober 2026 (lihat bagian G4): waktu bersama Painleve-Gullstrand, relai 22 rs, pulsa tiap 1 s waktu wajar, jam wahana terlihat relai (melambat, memerah, membeku), pesan relai ke wahana, suar E, jendela relai dan diagram ruang-waktu (M), layar akhir dengan jendela relai hidup. Belum diuji di GTX 1060 dan M1 |
| G5 | Selesai 4 Oktober 2026 (lihat bagian G5): skenario "Bidik tesseract (fiksi)", membidik sudut d dan bidang orbit dengan waktu beku, peta orbit, lintasan acuan yang dipakai saat terbang (prakiraan = hasil), gerbang fiksi di dalam horizon, adegan hiperkubus 4D, kartu akhir. Belum diuji di GTX 1060 dan M1 |
| G6 | Berjalan per kelompok: uji G1 sampai G5 di `tools/uji_misi_gargantua.py`, kamus ID, CLAUDE.md, `tombol.md` |
| G7 suara | Selesai 4 Oktober 2026 (lihat bagian G7): suara disintesis Web Audio, U nyala / mati, pilihan di panel. Belum didengar pemilik |
| G8 peta corong | Selesai 8 Oktober 2026 (rumus: `docs/gargantua/rumus-peta-corong.md`): panel kanan bawah untuk semua misi, corong z = 2 sqrt(r) (irisan Eddington-Finkelstein, menembus horizon sampai singularitas) dengan riwayat, prakiraan, dan posisi live; tesseract tetap memakai peta orbit saat membidik, corong setelah Enter. Susur searah arus: partikel datang dari arah tampak lubang hitam (dulu 9-14 derajat di sampingnya); melawan arus tidak berubah. Uji kelompok 8. Belum diuji di GTX 1060 dan M1. Revisi 8 Oktober: panel corong seukuran jendela relai (340 x sampai 380 px), elevasi pandang 28-45 derajat agar panel terisi; informasi delta-v lolos di bagian "Bisakah lolos dari lubang hitam?" |

Catatan hak cipta: kedua foto rujukan tampaknya cuplikan film. Dipakai hanya sebagai rujukan suasana (warna, komposisi, gerak); bingkai, bentuk kapal, dan susunan gambarnya tidak ditiru, sesuai aturan proyek.

## Keputusan pemilik

| Item | Keputusan |
| --- | --- |
| Wahana | Wahana baru khusus Gargantua, bukan KS-07 (KS-07 dipakai di Millar's World, terlalu kecil). Model 3D dari blokout v3 |
| Kamera | Kokpit + kamera luar |
| Masuk lubang hitam | Seperti foto 1: menyusur dekat permukaan piringan |
| Partikel | Seperti foto 2: partikel piringan menabrak kaca wahana |
| Tesseract | Hiperkubus 4D abstrak, berlabel fiksi |

## Kondisi sekarang

| Item | Isi | Lokasi (cari nama) |
| --- | --- | --- |
| Render | Ray tracing di fragment shader, satuan rs = 1, M = 0,5. Bentuk lintasan foton dari persamaan Binet dalam koordinat Kartesius datar, integrator Verlet, langkah sebanding r | `SCENE_FS`, `accel()` |
| Kamera | Pengamat diam di 6-60 rs, arah awal sinar `vel = dir` | `cameraBasis()`, `CAM_PRESETS` |
| Piringan | Bidang tipis y = 0 (tanpa tebal), rIn 3 rs, rOut 12 rs, tekstur 2D fbm, Doppler dan redshift opsional, mode film | `shadeDisk()`, `diskDensity()` |
| Tanpa three.js | WebGL2 murni, satu segitiga layar penuh, bloom dan streak | `P`, `pass()`, `frame()` |
| Model v3 | three.js, daftar geometri `parts` (loft poligon berwarna per sisi), decal kanvas, kaki pendarat | `docs/app/kestrel/blokout-ks07-v3.html` |
| Tombol | Standar `docs/app/tombol.md`: Gargantua memakai Space, Q, P, F, R, H, `, ?, 1-4, Esc | |

## Angka dasar

Asumsi massa Gargantua 1e8 massa Matahari (mengikuti buku Kip Thorne, The Science of Interstellar, 2014). Konstanta G = 6,674e-11, c = 2,998e8 m/s, massa Matahari 1,989e30 kg.

| Item | Nilai | Rumus |
| --- | --- | --- |
| Radius Schwarzschild rs | 2,954e8 km (1,97 AU) | 2GM/c^2 |
| Satuan waktu rs/c | 985,3 s | |
| Jatuh radial 22 rs ke horizon (dari diam di tak hingga) | 67.123 s = 18,65 jam waktu wajar | (2/3)(r0^1,5 - 1) rs/c |
| Horizon ke singularitas | 656,8 s (10,9 menit) | (2/3) rs/c |
| Waktu wajar maksimum di dalam horizon | 1.547,7 s (25,8 menit) | (pi/2) rs/c |
| Pasang surut tubuh 2 m di horizon | 2,1e-7 g | 2GML/r^3 |
| Pasang surut 1 g (awal spagetifikasi) | r = 0,00594 rs, 0,30 s sebelum singularitas | |
| Sudut tangkap kritis di 22 rs | 24,62 derajat (36,87 di 10 rs; 48,19 di 6 rs) | sin d = 2 rs / (r0 gamma v) |
| Langit di belakang saat lewat horizon | frekuensi x 0,5 | 1 / (1 + beta), beta = 1 |

Kecepatan gas piringan terhadap wahana yang jatuh lurus di dekatnya (keduanya diukur pengamat diam setempat, arah saling tegak lurus):

| r | Gas piringan (orbit melingkar) | Wahana jatuh | Relatif | Lorentz gamma |
| --- | --- | --- | --- | --- |
| 12 rs | 0,213 c | 0,289 c | 0,354 c | 1,069 |
| 6 rs | 0,316 c | 0,408 c | 0,500 c | 1,155 |
| 3 rs (ISCO) | 0,500 c | 0,577 c | 0,707 c | 1,414 |

Rumus: gas sqrt(M/(r - 2M)), wahana sqrt(rs/r), gamma relatif = gamma1 x gamma2. Angka ini menentukan arah dan laju garis partikel di G3.

## Inti fisika render

Satu perubahan kunci di shader: arah awal jejak sinar untuk kamera yang ikut jatuh.

| Item | Sekarang | Mode misi |
| --- | --- | --- |
| Arah awal jejak mundur | `vel = dir` | `vel = dir + beta * r_hat`, beta = sqrt(rs/r) |
| Kamera di dalam horizon | Tidak mungkin | Boleh: semua jejak mundur bergerak ke r lebih besar |
| Aturan tertelan | `r < RS` | `r < RS && dot(pos, vel) < 0` |
| Frekuensi teramati | Pengamat diam | eps_obs = E / (1 - beta cos a) |

Asal rumus: di koordinat Painleve-Gullstrand p^r = eps (cos a - beta), jadi dr/dphi = r (cos a - beta) / sin a. Bentuk orbit (r, phi) sama dengan koordinat Schwarzschild, jadi integrator Binet tetap dipakai. Untuk lintasan bermomentum sudut, kecepatan wahana relatif rain frame dari (beta^2 - 1) w^2 + 2 E beta w + E^2 - 1 - L^2/r^2 = 0 (reguler di horizon), lalu aberasi biasa.

Pertahankan yang ada: uniform baru `uFall` (0 = perilaku lama persis), `uBeta`, basis kamera wahana. Preset 1-4 dan tampilan lama tidak berubah saat misi mati.

Lintasan wahana di CPU: geodesik timelike Schwarzschild, RK4 pada (r, dr/dtau, phi), d2r/dtau2 = -M/r^2 + L^2/r^3 - 3 M L^2/r^4.

## G1: wahana GX-01

| Bagian | Isi |
| --- | --- |
| Sumber | Blokout v3, yang sudah dipindah ke modul bersama sebagai `KESTREL.buildV3(THREE)` di `shared/kestrel.js` (geometri blokout + pintu, tapak, lampu). Kaki pendarat dilipat (tidak digambar saat terbang). Stensil diganti "GX-01". `buildV3` tidak diubah (pertahankan yang ada) |
| Alat olah | `tools/siapkan_wahana_gx.mjs` (baru, Node): muat three.js + `shared/kestrel.js` di Node (vm), panggil `buildV3`, gabungkan geometri jadi satu array posisi, normal, warna, simpan base64 ke `experiences/gargantua/assets/gx01.data.js`. Sama seperti cara `tools/siapkan_motor.py`: Gargantua tetap tanpa three.js dan jalan dari file:// |
| Render | Program raster kecil + depth di Gargantua, digambar ke `T.scene` sebelum bloom. Disinari dari arah piringan (warna jingga, kuat dari bawah saat terbang rendah), sisi lain ambient redup. Pembelokan cahaya di skala 27,5 m nol (rs = 2,954e11 m), jadi raster biasa tetap benar |
| Kokpit | G2: kokpit v3 di tengah (kaca sempit, sekat tepat di depan mata, ujung lengan garpu menutup pandangan) diganti pod kaca di depan, duduk di pelat dek di antara ujung lengan, disambung leher ke badan tengah. Mata pilot (0; 1,0; -13,0 m) sejajar kabin ujung lengan, jadi lengan ada tepat di samping (80-90 derajat) dan pandangan depan sekitar 160 derajat bebas. Kaca depan, atas, samping; rangka 6 cm gelap doff hanya di sudut; konsol rendah dengan 3 layar MFD; interior hanya disinari cahaya yang masuk lewat kanopi. FOV kokpit 75 derajat |
| Kamera luar | Kamera kejar di belakang-atas wahana, seperti komposisi foto 1 (wahana kecil di tengah, piringan di bawah) |
| Nama | GX-01 "Ambang" (ambang = batas, horizon). Usulan, bisa diganti |
| Dokumen | `docs/app/penamaan.md` ditambah baris GX-01 |

## G2: kamera jatuh, skenario, kendali terbatas (selesai)

Permintaan tambahan pemilik saat menjalankan kelompok 2: (1) saat jatuh ada kendali terbatas, (2) berbagai cara dan kondisi jatuh, (3) kokpit diperbaiki, pandangan tidak tertutup 2 lengan.

| Bagian | Isi |
| --- | --- |
| Masuk misi | Panel kontrol (`): bagian "Misi: jatuh ke Gargantua", pilih skenario, Mulai misi. Tidak ada huruf baru |
| Kamera | Shader: `uFall`, `uObsV` (kecepatan wahana di kerangka rain), `uObsG`, `uBeta`. Arah foton di kerangka wahana diaberasi ke kerangka rain, jejak mundur = -n + beta r_hat, langkah = jarak tempuh (laju datar jauh dari 1 di r kecil), tertelan hanya bila r < 1 dan bergerak ke dalam. Foton dengan E <= 0 (di dalam horizon, dari arah bawah) digambar gelap: dalam lubang hitam nyata cahaya itu berasal dari materi yang jatuh lebih dulu, tidak dimodelkan. Warna dan kecerahan piringan dan langit memakai faktor frekuensi pengamat jatuh (dibatasi agar tidak meledak) |
| Fisika wahana | CPU, `misAcc()` / `rk4()` / `misAdvance()`: geodesik Schwarzschild dalam koordinat Kartesius datar, d2x/dtau2 = -M x / r^3 (1 + 3 L^2 / r^2), reguler di horizon, langkah ikut waktu dinamis. Kerangka rain `rainOf()`: gamma = K / (E - beta ur). Terukur: 22 rs ke horizon 68,1261 rs/c (rumus 68,1261), dilepas diam ke singularitas 162,0888 (rumus 162,0891) |
| Kendali terbatas | W/S maju-mundur, A/D kiri-kanan, R/F naik-turun di kerangka wahana (boost relativistik `misThrust()`), Shift = mesin utama 0,004 c per detik nyata, tanpa Shift 0,0008 c/s. Anggaran delta-v 0,02-0,04 c per skenario. E dijaga >= 0,01. Di dalam horizon dorongan penuh ke luar tetap tidak bisa membuat dr/dtau >= 0 (diuji). Seret mouse = arah hidung |
| Sikap (X) | Hidung ke pusat / hidung mendatar (tegak lurus jari-jari, atas = menjauhi lubang hitam; dari dalam horizon langit tampak sebagai pita mendatar) / bebas (seret) |
| Waktu (Z) | Otomatis: 1 s nyata = 985 x 1,41 r^1,5 / 10 detik waktu wajar (sekitar 14.400 di 22 rs, minimum 1 di r < 0,03), jadi jatuh lurus sekitar 50 s nyata: 22 s sampai horizon, sisanya di dalam, beberapa detik terakhir dalam waktu nyata. Pilihan: Otomatis, x4, x16, Lambat x0,25. Space menjeda |
| HUD | Kiri atas di kedua tampilan: skenario, r (rs dan km), status di luar / DI DALAM HORIZON, waktu wajar, prakiraan (singularitas dalam ..., lolos, menabrak piringan, orbit terikat), laju (terhadap pengamat diam di luar horizon, terhadap kerangka jatuh di dalam), faktor frekuensi langit depan dan belakang, pasang surut 2 m, delta-v, laju waktu. Baris tombol di bawah |
| MFD kokpit | Atlas kanvas 3 layar, 5 kali per detik: kiri r (skala log) terhadap waktu wajar dengan garis ISCO, 1,5 rs, horizon, riwayat dan prakiraan; tengah data utama; kanan langit, laju, delta-v, dorongan, sikap |
| Akhir | Singularitas (r < 0,006 rs, pasang surut 1 g), menembus piringan (bidang y = 0 di rIn..rOut), lolos (r > 70 rs bergerak keluar). Layar ringkasan: waktu wajar total, waktu lewat horizon, horizon sampai akhir, laju tercepat, delta-v. Enter atau "Terbang lagi" mengulang, Esc keluar |

Tujuh skenario (rs = 1, mulai di 22 rs kecuali orbit tak stabil). Hasil tanpa dorongan terukur di `tools/uji_misi_gargantua.py`:

| Skenario | Kondisi awal | Hasil tanpa dorongan | Waktu wajar | Yang diperlihatkan |
| --- | --- | --- | --- | --- |
| Lurus lewat kutub | E = 1 (datang dari jauh), radial | singularitas | 68,79 rs/c = 18,8 jam | Masuk langsung; horizon tanpa tanda |
| Dilepas diam di 22 rs | E = 0,977, radial | singularitas | 162,09 rs/c = 44,4 jam | Mulai diam, jatuh makin cepat |
| Datang cepat | E = 1,3 (0,86 c di 22 rs) | singularitas | 23,73 rs/c | Aberasi: langit memampat ke depan, bayangan tampak lebih kecil |
| Miring, lewat celah dalam | L = 1,6 (0,8 kritis), bidang miring 35 derajat, sudut awal 57,5 derajat | singularitas, memotong bidang piringan di sekitar 2 rs (di dalam tepi 3 rs) | 78,41 rs/c | Berayun, menyelinap di antara piringan dan horizon |
| Berputar di 2 rs | L = 2 (1 - 2e-6), sedikit di bawah kritis | singularitas setelah beberapa putaran | 117,61 rs/c | Zoom-whirl di orbit tak stabil |
| Nyaris lolos | L = 2,05, sedikit di atas kritis | lolos | - | Dorongan mundur 0,02 c sebelum 4 rs = tertangkap; rem terlambat = orbit terikat yang menembus piringan |
| Orbit tak stabil 2,4 rs | Orbit melingkar di dalam ISCO, gangguan kecil ke dalam | singularitas | 43,96 rs/c | Tidak ada orbit stabil di dalam 3 rs; dorongan bisa menunda |

Sudut awal skenario miring, berputar, dan nyaris lolos dipilih dari hitungan numerik lintasan agar perpotongan dengan bidang piringan jatuh di luar 3-12 rs. Bila pemain mengubah radius piringan di panel, hasilnya bisa berubah (wajar).

## G3: terbang rendah di atas piringan dan partikel (foto 1 dan 2) (selesai)

### Hasil G3 (4 Oktober 2026)

| Bagian | Isi |
| --- | --- |
| Skenario baru | "Susur piringan, melawan arus" (pilihan awal di panel, jalur utama) dan "Susur piringan, searah arus". Mulai di 16 rs, 0,05 r di atas bidang piringan, orbit melingkar + turun 0,1 c. Total 9 skenario |
| Autopilot susur (O) | Kecepatan sasaran = orbit melingkar (melawan atau searah gas) + laju turun + koreksi tinggi ke h r di atas bidang piringan. Selisih di kerangka rain dikoreksi dengan dorongan (`misThrust`, ikut anggaran delta-v 0,3 c), paling besar 0,02 c per rs/c. Dilepas otomatis di dalam ISCO (3 rs): tidak ada orbit stabil, wahana menukik dan memotong bidang di celah dalam. Selama autopilot: R/F tinggi sasaran (0,015-0,3 r), W/S laju turun (0-0,25 c), Shift 3x lebih cepat. O mematikan: orbit miring segera menembus piringan (diuji). Delta-v habis = autopilot lepas, wahana turun ke piringan (diuji) |
| Terukur | Melawan dan searah arus: 16 rs ke ISCO lalu singularitas, waktu wajar 143,5 rs/c (39,3 jam), delta-v 0,19 c dari 0,3 c (tinggi 0,03 r: 0,275 c), galat tinggi < 0,005 r. Waktu nyata dengan waktu Otomatis: 47 s sampai ISCO, 75 s sampai horizon, 80 s sampai akhir |
| Lempeng tebal | Shader varian terpisah (`#define VOL 1`, program `P.sceneVol`), hanya dipakai saat kamera dekat piringan; tampilan biasa dan misi lain memakai varian `VOL 0` yang sama persis dengan G2. Daerah bola 0,3 r (0,6-2 rs) di sekitar kamera, H = 0,025 r, profil exp(-(y/H)^4) dengan tinggi lapisan diangkat oleh derau (permukaan bergolak), derau 3D 64^3 berulang dibuat di CPU (koordinat mutlak ln r, phi, y/H, memanjang 4,5x searah orbit, ikut rotasi Kepler dua lapis). Warna dan pola besar dari `shadeDisk()` di titik tengah langkah, jadi menyambung dengan piringan tipis (di tepi daerah bobot berpindah). Satu panggilan `shadeDisk()` per langkah (lempeng dan piringan tipis berbagi). Paling banyak 10 / 14 / 18 / 24 sampel per piksel (Rendah / Sedang / Tinggi / Ultra). Aktif hanya saat misi dan kamera kurang dari 6 H dari bidang |
| Waktu piringan | Selama misi piringan berputar menurut waktu wajar wahana (sebelumnya waktu tampilan tetap), jadi gerak gas relatif wahana konsisten |
| Eksposur otomatis | Hanya saat misi: rata-rata 30% bagian layar paling terang (grid 16 x 9, dibaca asinkron dengan PBO + fence), eksposur turun bila terang (paling kecil 0,12), ambang bloom ikut. Di luar misi tidak berubah |
| Partikel | 400 / 900 / 1.600 / 2.500 garis bara per preset di kotak 300 m sekitar mata, bergerak searah kecepatan gas relatif wahana (boost dari kerangka rain), laju tampilan 80 + 700 v m/s (distilisasi). Awan debu layar penuh dalam koordinat terowongan di sekitar arah datang gas. Kerapatan debu exp(-(y / 2,5 H)^2), nol di jalur kutub |
| Kaca | Tumbukan hanya di kaca yang menghadap arus (segitiga kaca GX-01 dibobot luas x cos), laju 30 x kerapatan x min(1, (v / 0,4)^2) per detik nyata. Kilat putih, pijar jingga, retak menetap (paling banyak 96). Kerusakan 0,05% x (v / 0,5)^2 per tumbukan; 100% = "Kaca kokpit pecah" (akhir misi). Terukur dengan waktu Otomatis: melawan arus 774 tumbukan, kerusakan 71% di akhir; tinggi 0,03 r: 1.100 tumbukan, 99%; searah arus 58 tumbukan, 0,1% |
| Guncangan | Sudut kecil ikut kerapatan debu x laju relatif + hentakan tiap tumbukan |
| HUD dan MFD | Baris baru: piringan (tinggi dalam H, gas relatif), autopilot, kaca. Prakiraan "autopilot menahan tinggi (tanpa autopilot: piringan dalam ...)" |

Kecepatan gas relatif wahana pada susur melawan arus (keduanya orbit melingkar berlawanan, terhadap pengamat diam: 2v / (1 + v^2), v = sqrt(M / (r - 2M))). Diuji: 0,5750 c di 6 rs dan 0,8000 c di 3 rs. Searah arus: 0 (gas hanya lewat sebesar laju turun 0,1 c).

| r | Gas (thd diam) | Relatif melawan arus | Lorentz gamma | Energi 1 mikrogram debu |
| --- | --- | --- | --- | --- |
| 12 rs | 0,213 c | 0,408 c | 1,095 | 8,6e6 J (2,0 kg TNT) |
| 6 rs | 0,316 c | 0,575 c | 1,222 | 2,0e7 J (4,8 kg TNT) |
| 4 rs | 0,408 c | 0,700 c | 1,400 | 3,6e7 J (8,6 kg TNT) |
| 3 rs (ISCO) | 0,500 c | 0,800 c | 1,667 | 6,0e7 J (14,3 kg TNT) |

Rencana awal di bawah dipertahankan sebagai rujukan.

### Jalur "susur piringan" (jalur utama misi)

| Fase | Isi |
| --- | --- |
| 1. Turun ke piringan | Dari 22 rs, wahana turun ke ketinggian rendah di atas permukaan piringan di sekitar 12 rs |
| 2. Menyusur | Terbang di atas piringan dari 12 rs ke 3 rs, ketinggian beberapa kali tebal piringan. Kamera kejar seperti foto 1: piringan memenuhi separuh bawah layar sebagai dataran bergolak, dinding cahaya menjulang di sisi (piringan sisi jauh di atas dan bawah bayangan, sudah dihasilkan ray tracer), bayangan hitam di depan |
| 3. Menukik | Di dalam ISCO gas ikut jatuh; wahana menukik ke horizon. Partikel menipis, gelap, garis bara seperti foto 2 |
| 4. Horizon dan dalam | Sama dengan G2 |

### Piringan tebal di dekat kamera

Piringan sekarang setipis kertas, jadi dari dekat tidak bisa tampak seperti foto 1. Tambahan:

| Bagian | Isi |
| --- | --- |
| Lapisan volumetrik | Hanya di sekitar kamera (misal radius 1,5 rs): sinar melangkah di dalam lempeng tebal H(r) = 0,03 r, kepadatan dari fbm 3D yang memanjang searah orbit (garis seret seperti foto 1), cahaya dari suhu `shadeDisk()` yang sudah ada. Di luar radius itu tetap piringan tipis lama, jadi biaya terbatas |
| Gerak | Pola ikut rotasi Kepler (`diskDensity()`), ditambah kabur gerak searah kecepatan relatif (0,35 sampai 0,71 c, tabel angka dasar) |
| Silau | Permukaan piringan di bawah wahana sangat terang; eksposur misi diatur otomatis agar seperti foto 1 (putih di dinding cahaya, jingga di dataran) |
| Biaya | Langkah volumetrik hanya untuk piksel yang sinarnya masuk lempeng dekat kamera; jumlah langkah dibatasi per preset kualitas |

### Partikel dan kaca

| Bagian | Isi |
| --- | --- |
| Garis bara | Partikel GPU (titik instance) di kotak di sekitar wahana, dipindah ulang saat keluar kotak. Digambar sebagai garis memanjang searah kecepatan relatif, jadi tampak memancar dari satu titik hilang di depan seperti foto 2. Warna bara jingga-putih, panjang ikut laju |
| Awan debu | Lapisan kabut abu-kebiruan bergerak cepat di sekitar titik hilang (fbm 2D di layar), gelap seperti foto 2 |
| Tumbukan kaca | Hanya di kamera kokpit. Partikel yang lintasannya memotong bidang kaca: kilat putih singkat, lalu bekas pijar jingga yang mendingin dan memudar beberapa detik, retak halus bertambah pelan. Di kanvas overlay atau tekstur kaca kecil |
| Guncangan | Kamera bergetar kecil saat banyak tumbukan; HUD "kerusakan kaca" naik (distilisasi) |
| Kepadatan | Banyak saat menyusur (fase 2), memuncak dekat ISCO, menipis saat menukik, hampir nol di dalam horizon |
| Preset | Jumlah partikel turun di Rendah; tumbukan kaca tetap ada |
| Label | Panel menulis bahwa fisika partikel distilisasi (debu 1 mikrogram pada 0,707 c = 3,7e7 J, sekitar 8,9 kg TNT; wahana nyata tidak akan selamat) |

## G4: informasi tidak bisa keluar

### Hasil G4 (4 Oktober 2026)

| Bagian | Isi |
| --- | --- |
| Waktu bersama | Waktu Painleve-Gullstrand T (waktu wajar pengamat yang jatuh dari diam di tak hingga), reguler di horizon. Untuk wahana dT/dtau = gamma wahana terhadap kerangka rain, diintegrasikan bersama lintasan (`MIS.T`). Jatuh lurus E = 1: T = waktu wajar persis (diuji) |
| Sinar radial | Keluar: T - Gout(r) tetap, Gout = r + 2 akar r + 2 ln abs(akar r - 1), dr/dT = 1 - 1/akar r (di dalam horizon negatif: cahaya "keluar" pun turun). Masuk: T + Hin(r) tetap, Hin = r - 2 akar r + 2 ln(akar r + 1). Diuji terhadap integrasi numerik (galat < 1e-6 rs/c) |
| Relai | Orbit melingkar 22 rs, jam relai = T x akar(1 - 1,5/22) = T x 0,9653. Tanpa model 3D (titik di diagram) |
| Pulsa | 1 per detik waktu wajar. HUD dan jendela: terkirim, tiba, di jalan, tak akan tiba (dikirim dari dalam horizon). Jatuh lurus: 67.779 terkirim, 657 dari dalam horizon |
| Pandangan relai | Jam wahana seperti terlihat relai (balikan waktu tiba di log lintasan yang rapat dekat horizon), warna dan terang ikut faktor frekuensi (biru > 1, memerah, padam), "cahaya ini berangkat dari r = ...". Di awal jatuh lurus laju = (akar r - 1) / (akar r x 0,9653) (Doppler + dilatasi relai, diuji) |
| Membeku | Relai melihat jam berhenti tepat di waktu lewat horizon (jatuh lurus 68,1261 rs/c = 18 jam 38 menit 43 detik, diuji < 1e-6). Menjelang akhir laju jam terlihat turun faktor e tiap 2 rs/c waktu bersama (gravitasi permukaan 1/(2 rs), diuji): frekuensi faktor e tiap 31,7 menit jam relai, terang tiap 15,9 menit |
| Setelah misi | Layar akhir memuat jendela relai hidup: waktu relai terus berjalan 3 rs/c per detik nyata, jadi jam wahana tampak melambat, memerah, lalu padam |
| Arah sebaliknya | Pesan relai tetap sampai ke wahana di dalam horizon (jam relai terlihat dari wahana terus naik sampai singularitas, berhingga). Jatuh lurus: pesan terakhir yang diterima dikirim pada jam relai 13:55:19 |
| Suar (E) | Ditembakkan lurus menjauhi pusat (radial di kerangka rain) pada c. Dari luar horizon naik dan tiba di relai; dari dalam horizon r tetap turun sampai 0 (diuji). Garis biru muda di diagram, baris HUD "Suar" |
| Diagram ruang-waktu (M) | Koordinat Eddington-Finkelstein masuk: r mendatar, waktu ke atas, skala sama (sinar masuk 45 derajat). Kerucut cahaya (biru di luar, merah di dalam horizon: kedua kaki ke kiri), horizon putus-putus, singularitas zigzag, relai hijau, garis dunia wahana, sinar pulsa (jingga sampai relai, merah jatuh ke r = 0), titik yang sedang terlihat relai. Zoom mengikuti r wahana (3 sampai 24,5 rs) |
| Tombol | E suar, M jendela relai (juga di panel). Seret di kamera luar = kamera mengitari wahana (masukan pemilik) |

Tunda sinyal radial dari wahana ke relai 22 rs (waktu bersama T; jam relai x 0,9653):

| r kirim | Tunda | |
| --- | --- | --- |
| 16 rs | 7,8 rs/c | 2,1 jam |
| 6 rs | 22,4 rs/c | 6,1 jam |
| 3 rs | 28,2 rs/c | 7,7 jam |
| 1,5 rs | 33,0 rs/c | 9,0 jam |
| 1,01 rs | 41,6 rs/c | 11,4 jam |
| 1,0001 rs | 50,8 rs/c | 13,9 jam |
| 1 + 1e-8 rs | 69,2 rs/c | 18,9 jam |
| 1 rs atau kurang | tidak pernah | |

Rencana awal:

| Bagian | Isi |
| --- | --- |
| Relai | Satelit relai orbit melingkar di 22 rs (desain orisinal sederhana) |
| Pulsa | Wahana mengirim pulsa tiap 1 s waktu wajar. Tiba di relai: t_tiba = u_kirim + r*(r_relai), u = t - r*, r* = r + rs ln abs(r/rs - 1); u_kirim menuju tak hingga saat r menuju rs |
| Pandangan relai | Jendela kecil: jam wahana melambat, memerah, membeku di horizon. Penghitung "pulsa belum tiba" terus naik setelah horizon |
| Diagram ruang-waktu | Kanvas 2D, Eddington-Finkelstein masuk: kerucut cahaya makin miring, garis dunia wahana, pulsa |
| Uji suar | E di dalam horizon: suar ditembak "keluar" pada c, HUD menunjukkan r suar tetap turun (p^r = eps (cos a - beta) < 0) |
| Arah sebaliknya | Pesan relai ke wahana tetap masuk |

## G5: sudut masuk tesseract (fiksi)

### Hasil G5 (4 Oktober 2026)

| Bagian | Isi |
| --- | --- |
| Skenario | "Bidik tesseract (fiksi)" (ke-10). Wahana di 22 rs, 30 derajat di atas bidang piringan, E = 1 (datang dari jauh). Waktu beku selama membidik |
| Bidikan | d = sudut arah gerak dari arah radial ke dalam (pengamat diam setempat), bidang orbit psi (0 = lewat atas kutub). L = 22 sin d / akar 21. Kritis L = 2 rs c, d kritis = asin(2 akar 21 / 22) = 24,619977 derajat (diuji). Di bawah kritis tertangkap, di atas lolos (diuji) |
| Tombol | W/S sudut d: mendekat / menjauh dari kritis secara eksponensial (delta = 1 - L/Lkrit dikali faktor tetap per detik; Shift 8 kali lebih cepat). Lewat 1e-12 berpindah ke sisi lolos. A/D bidang orbit (15 derajat/s, Shift 60). Enter kunci dan berangkat. Juga tombol panel "Kunci bidikan dan berangkat" |
| Zoom-whirl | Tiap delta 10 kali lebih kecil, wahana berputar ln(10) / akar(1/2) = 186,6 derajat lebih banyak di sekitar 2 rs (eksponen ketidakstabilan orbit 2 rs: akar(1/2) per radian). Terukur 186,4 (diuji). Sampai sekitar 4,5 putaran (delta 1e-9); lebih kecil dari itu galat angka mendominasi |
| Piringan | Bidang orbit menentukan di mana lintasan memotong bidang piringan. Bidang 90 derajat selalu menembus piringan di 3-12 rs (diuji). Perpotongan di dalam 3 rs (celah dalam) aman |
| Gerbang (fiksi) | Di r 0,6 rs (di dalam horizon) pada arah tertentu: bidang 25 derajat, 200 derajat dari arah awal. Toleransi 5 derajat. Solusi: sapuan 200 + 360 k derajat, misalnya 920 derajat (delta sekitar 6e-5, 2,6 putaran) atau 1.280 derajat (delta sekitar 7e-7, 3,6 putaran) |
| Peta orbit | Kanan bawah (besar saat membidik, digeser ke kiri panel kontrol bila panel terbuka): bidang lintasan, jari-jari logaritmik ln(1 + r) agar 2 rs dan 22 rs sama-sama terlihat (sudut tetap benar). Lingkaran horizon, foton 1,5, orbit tak stabil 2, ISCO 3, relai 22. Garis merah = potongan piringan (rIn sampai rOut), belah ketupat biru = gerbang, X = titik menabrak piringan. Baris: bidikan, hasil (tepat sasaran / meleset / menabrak / lolos), jarak gerbang dari bidang |
| Prakiraan = hasil | Setelah Enter (titik tanpa kembali, mesin dikunci) wahana mengikuti lintasan acuan yang sama persis dengan prakiraan: langkah RK4 disimpan, posisi di antara langkah = interpolasi Hermite kubik. Alasan: di dekat orbit tak stabil, selisih langkah integrasi kecil tumbuh cepat, sehingga integrasi ulang bisa berbeda jumlah putaran dari prakiraan (terlihat di uji: di bawah delta 1e-9 hasil jenuh karena galat angka) |
| Penanda gerbang | Belah ketupat biru di layar 3D: proyeksi garis lurus dari wahana (pembelokan cahaya diabaikan; gerbang fiksi) |
| Tepat sasaran | Kilat putih, lalu adegan hiperkubus 4D (16 titik sudut, 32 rusuk, 24 sisi persegi, 8 sel kubus) berputar di bidang xw, yw, zw, diproyeksikan 4D ke 3D ke layar, garis bercahaya jingga (bagian dalam) dan biru pucat (luar), kisi 26 hiperkubus redup. Desain sendiri: bukan ruangan atau rak dari film. Label fiksi di layar dan kartu. Kartu akhir setelah 10 s (bidikan, sapuan dan putaran, galat gerbang, semua baris G4) |
| Meleset | Notifikasi galat, lintasan berlanjut ke singularitas, galat tercatat di kartu akhir |
| Contoh uji | d = 24,61995916 derajat, L/Lkrit = 1 - 6,9e-7, bidang 25: 1.280 derajat (3,55 putaran), galat gerbang 0,3 derajat, waktu wajar 33 jam, lewat horizon 4 menit 44 detik sebelum gerbang |

Rencana awal:

| Bagian | Isi |
| --- | --- |
| Bidik | Sebelum titik tanpa kembali: W A S D atur sudut d dan bidang orbit, Shift kasar, Enter kunci (mengikuti tombol pesawat Copper) |
| Prediksi | Peta orbit 2D: lintasan, piringan 3-12 rs, horizon, lingkaran foton 1,5 rs, orbit tak stabil 2 rs, gerbang |
| d > d_krit | Terlempar keluar |
| d jauh di bawah d_krit | Langsung ke singularitas |
| Menembus piringan | Jalur susur di atas piringan diperbolehkan; menembus bidang piringan di 3-12 rs = wahana hancur |
| d sedikit di bawah d_krit | Zoom-whirl di sekitar 2 rs, jumlah putaran menentukan azimut masuk horizon |
| Gerbang | Di dalam horizon pada azimut dan bidang tertentu, toleransi +/- 5 derajat |
| Tesseract | Hiperkubus 4D berputar, diproyeksikan ke layar, garis bercahaya orisinal. Label: "Fiksi / spekulatif: fisika nyata tidak mengenal tesseract di dalam lubang hitam" |

## G7: suara (selesai)

### Hasil G7 (4 Oktober 2026)

| Bagian | Isi |
| --- | --- |
| Mesin | Web Audio, semua disintesis (derau putih 2 s berulang + osilator), kompresor di ujung. AudioContext dibuat pada tombol atau klik pertama (kebijakan putar otomatis browser) |
| U | Nyala / mati, tersimpan di localStorage `gargantua.sound` (bawaan nyala); juga kotak centang "Suara (U)" di panel |
| Dengung kabin | 55 + 110 Hz + desis rendah, selama misi |
| Pendorong | Desis pita 1,4 kHz saat W/S A/D R/F; Shift = mesin utama (gergaji 41 Hz lewat lowpass). Autopilot = desis pelan. Diam saat membidik (G5) dan saat delta-v habis |
| Gemuruh piringan | Derau lowpass, keras = kerapatan debu x laju gas, potongan 180 sampai 2.380 Hz ikut laju gas: di 6 rs melawan arus 0,70 / 1.784 Hz, searah arus 0,33 / 478 Hz, jalur kutub 0 (diuji) |
| Tumbukan kaca | Ketukan derau tinggi tiap tumbukan; denting retak setelah kerusakan > 60%; pecah berlapis saat kaca 100% |
| Pesan relai | Bip tiap 1,6 s nyata, nada 880 Hz dikali laju jam relai yang terlihat wahana (makin rendah saat jatuh menjauh, tetap terdengar di dalam horizon) |
| Suar | Desis naik + nada naik |
| Horizon | Tidak berbunyi (tidak ada yang terasa saat lewat horizon) |
| Pasang surut | Di dalam horizon nada rendah naik menjelang singularitas (r 0,5: 104 Hz; 38 sampai 298 Hz) |
| Tesseract | Akord 110, 165, 220, 275, 330 Hz, nadanya bergeser pelan (fiksi) |
| Uji | `audioMix()` fungsi murni diuji (gemuruh, pasang surut, pendorong, membidik, tesseract), AudioContext, U, localStorage, panel |

Usulan awal:

Usulan mengikuti cara Copper Corn Station dan Millar's World: semua suara disintesis Web Audio (tanpa berkas audio), tombol U nyala / mati sesuai `docs/app/tombol.md`, pilihan tersimpan di localStorage.

| Suara | Kapan | Catatan |
| --- | --- | --- |
| Dengung kabin | Selama misi | Dasar, sangat pelan; naik sedikit saat dorongan |
| Mesin dan pendorong | W/S A/D R/F, Shift | Desis pendorong kecil, gemuruh mesin utama; autopilot = koreksi pendek berulang |
| Gemuruh piringan | Dekat piringan | Distilisasi (di ruang hampa tidak ada suara dari luar): kerasnya ikut kerapatan debu x laju gas relatif |
| Tumbukan kaca | Tiap tumbukan G3 | Ketukan tajam, retak saat kerusakan naik, pecah di 100% |
| Pulsa dan relai | G4 | Bip pelan tiap pesan relai yang diterima, nadanya dikali faktor frekuensi (makin rendah saat menjauh); suar = desis naik |
| Horizon dan pasang surut | G2 | Tidak ada apa-apa saat lewat horizon (fisika); nada rendah naik menjelang singularitas |
| Tesseract | G5 | Lapisan nada harmonis yang berputar pelan mengikuti putaran 4D (fiksi) |

| Effort | Model | Thinking | File | Risiko |
| --- | --- | --- | --- | --- |
| Medium | Sonnet 5.5 | medium | `experiences/gargantua/index.html` (blok AUDIO baru, `stepMission`, `spawnImpact`, `fireFlare`, panel, bantuan, kamus ID), `docs/app/tombol.md`, uji kelompok 7 | Rendah (tidak menyentuh shader) |

## G6: uji dan bahasa

| Bagian | Isi |
| --- | --- |
| `tools/uji_misi_gargantua.py` (baru) | Waktu jatuh vs rumus, d_krit 24,62 derajat vs integrator, faktor langit 0,5 di horizon, kecepatan relatif 0,707 c di 3 rs, model GX-01 termuat, tanpa nilai tidak valid di r 0,5 dan 0,01 rs dan di dalam lempeng piringan, `uFall = 0` render sama dengan sebelum |
| Bahasa | Teks baru sumber English, entri kamus `ID`, lewat `txt()` |
| Cek muat | `python tools/qc_load.py experiences/gargantua/index.html` |
| Dokumen | CLAUDE.md (alat uji, aset), `docs/app/tombol.md` (tombol misi Gargantua), `docs/app/penamaan.md` (GX-01) |

## Tombol misi

Mengikuti `docs/app/tombol.md`: tidak ada huruf baru.

| Tombol | Fungsi |
| --- | --- |
| Panel ` | Mulai misi, pilih skenario (G2: 7 skenario; G3: + 2 susur piringan) dan sikap; tombol autopilot susur |
| V | Kokpit / kamera luar |
| Z | Kecepatan waktu (Otomatis, x4, x16, Lambat x0,25) |
| W/S, A/D, R/F, Shift | Dorong maju-mundur, kiri-kanan, naik-turun; Shift = mesin utama (G2, mengikuti tombol pesawat Copper) |
| Seret mouse, roda | Kamera luar: seret = kamera mengitari wahana (klik ganda kembali), seret kanan = arah hidung; kokpit: seret = arah hidung; roda = jarak kamera luar |
| X | Sikap: hidung ke pusat / mendatar / searah lintasan dengan piringan di bawah (G3; seret = arah pandang) / bebas (G2) |
| O | Autopilot susur nyala / mati (G3; huruf O = "otomatis", seperti jalan otomatis di Copper). Selama autopilot: R/F tinggi, W/S laju turun |
| Enter | Terbang lagi di layar akhir (G2); kunci bidikan dan berangkat (G5) |
| W/S, A/D saat membidik (G5) | Sudut d mendekat / menjauh dari kritis, bidang orbit; Shift kasar |
| E | Tembak suar (G4) |
| M | Pandangan relai dan diagram ruang-waktu nyala / mati (G4, setara M peta di Copper) |
| Space | Jeda |
| Esc | Akhiri misi |

Selama misi F dan R dipakai untuk dorongan (seperti pesawat Copper), jadi mode foto dan atur ulang kamera tidak tersedia sampai misi diakhiri.

## Bisakah lolos dari lubang hitam? (informasi, 8 Oktober 2026)

Ringkasan:
- Dorongan berfungsi. Delta-v dihitung dari besar dorongan, jadi semua arah (W/S/A/D/R/F) mengurangi anggaran yang sama.
- Anggaran tiap skenario sengaja kecil (0,02 sampai 0,04 c; susur 0,3 c), tapi sudah jauh di atas wahana nyata. Dari jatuh lurus, lolos butuh minimal 0,091 c di 22 rs dan makin mahal ke dalam; di dalam horizon mustahil.
- Hanya "Nyaris lolos" yang bisa lolos dengan anggaran sekarang (momentum sudut awal sudah di atas kritis). Tertangkap di skenario lain adalah hasil yang realistis.

Delta-v minimum untuk lolos dari jatuh lurus (E = 1, dihitung dengan rumus boost `misThrust()` dan integrator `misAdvance()`, arah dicari tiap 5 derajat di bidang radial-tangensial, besar dengan bisection):

| r (rs) | Laju jatuh vs pengamat diam | Delta-v min lolos | Arah terbaik dari radial keluar |
| --- | --- | --- | --- |
| 22 | 0,213 c | 0,091 c | 90 derajat (menyamping) |
| 10 | 0,316 c | 0,203 c | 85 derajat |
| 6 | 0,408 c | 0,340 c | 75 derajat |
| 3 | 0,577 c | 0,658 c | 55 derajat |
| 2 | 0,707 c | 0,866 c | 35 derajat |
| 1,5 | 0,816 c | 0,965 c | 20 derajat |
| 1,2 | 0,913 c | di atas 0,99 c (batas satu dorongan) | - |
| di dalam horizon | - | mustahil: semua arah menuju r = 0 | - |

Jauh dari lubang hitam, cara termurah adalah dorongan menyamping: momentum sudut cukup besar membuat wahana berayun lewat (kritis L = 2 rs c untuk E = 1). Dekat horizon dorongan harus makin lurus keluar dan mendekati c.

Pembanding realisme:

| Item | Delta-v |
| --- | --- |
| Roket kimia (satu tahap, terbaik) | sekitar 10 km/s = 3,3e-5 c |
| Anggaran skenario jatuh 0,03 c | 8.994 km/s (sekitar 900 kali roket kimia) |
| Anggaran susur 0,3 c | 89.938 km/s |
| Lolos dari jatuh lurus di 22 rs | 0,091 c = 27.282 km/s |

Catatan susur: autopilot memakai anggaran 0,3 c untuk menahan tinggi dan orbit (sekitar 0,19 c sampai ISCO bila setelan tidak diubah). W/S (laju turun) dan R/F (tinggi) saat autopilot mengubah sasaran, jadi autopilot ikut membakar delta-v. Bila habis, autopilot lepas dan tombol tidak lagi berefek (contoh foto Bhakti: 0,0000 / 0,300 di r 9,7).

Usulan lanjutan (belum dikerjakan, menunggu keputusan pemilik): baris "delta-v untuk lolos" di HUD dan MFD (dihitung ulang tiap sekitar 1 s), skenario tantangan lolos (jatuh lurus dengan anggaran 0,4 c: lolos bila mendorong sebelum sekitar 6 rs), opsi delta-v tak terbatas (fiksi).

## Batasan dan catatan

- Render dan lintasan memakai Schwarzschild. Gargantua di buku berputar hampir maksimum (Kerr); Kerr penuh bisa jadi tahap lanjutan.
- Partikel, tumbukan kaca, dan kepadatan piringan distilisasi demi tampilan; piringan akresi nyata jauh lebih tipis dan wahana tidak akan selamat.
- Tesseract dan gerbang murni fiksi. Jatuh, horizon, pulsa, kecepatan relatif, dan sudut tangkap mengikuti fisika.
- Animasi piringan tidak memperhitungkan waktu tunda cahaya.
- Sinyal ke dan dari relai dihitung sepanjang arah radial (relai dianggap tepat di atas wahana). Beda sudut hanya menambah tunda yang berhingga, tidak mengubah kesimpulan: dari dalam horizon tidak ada sinyal yang keluar.
- Biaya GPU terbesar: lapisan volumetrik dekat kamera (G3). Perlu diukur di GTX 1060 dan M1; bila berat, jumlah sampel (`vol` di `CONFIG.presets`) dan radius daerah (`volParams()`) diturunkan.
- Autopilot susur fiksi: menahan wahana di atas piringan butuh dorongan terus-menerus (0,19 c untuk satu jalur). Laju partikel, tumbukan, dan kerusakan kaca dihitung per detik nyata (bukan waktu wajar), jadi Z (waktu lebih cepat) mengurangi tumbukan.
- Nama Ranger dan desain kendaraan film tidak dipakai.
