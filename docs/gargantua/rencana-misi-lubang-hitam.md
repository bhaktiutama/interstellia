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
| G2-G6 | Belum dimulai; G6 berjalan per kelompok |

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
| Kokpit | Mata di kokpit kaca bersekat tengah depan. Bingkai sekat kaca dari geometri kokpit model itu sendiri (dilihat dari dalam), instrumen di kanvas 2D |
| Kamera luar | Kamera kejar di belakang-atas wahana, seperti komposisi foto 1 (wahana kecil di tengah, piringan di bawah) |
| Nama | GX-01 "Ambang" (ambang = batas, horizon). Usulan, bisa diganti |
| Dokumen | `docs/app/penamaan.md` ditambah baris GX-01 |

## G2: kamera jatuh dan jalur kutub

| Bagian | Isi |
| --- | --- |
| Masuk misi | Tombol "Misi" di panel kontrol (`). Tidak memakai tombol huruf baru: semua huruf sudah terpakai di `docs/app/tombol.md` |
| Jalur kutub (langsung) | Jatuh radial lewat sumbu, tidak menyentuh piringan. Jalur paling sederhana untuk syarat "masuk langsung" |
| Kamera | Kamera jatuh di shader (rumus di atas): bayangan hitam membesar, langit belakang menyempit dan memerah, tidak ada tanda visual tiba-tiba saat lewat horizon |
| HUD | r (rs dan km), waktu wajar, sisa waktu ke singularitas, laju lokal, faktor pergeseran langit, pasang surut, status (luar / horizon / dalam) |
| Waktu | Z = kecepatan waktu (tombol umum). Melambat otomatis dekat horizon |
| Akhir | r = 0,006 rs: layar gelap bertahap, ringkasan misi |

## G3: terbang rendah di atas piringan dan partikel (foto 1 dan 2)

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

| Bagian | Isi |
| --- | --- |
| Relai | Satelit relai orbit melingkar di 22 rs (desain orisinal sederhana) |
| Pulsa | Wahana mengirim pulsa tiap 1 s waktu wajar. Tiba di relai: t_tiba = u_kirim + r*(r_relai), u = t - r*, r* = r + rs ln abs(r/rs - 1); u_kirim menuju tak hingga saat r menuju rs |
| Pandangan relai | Jendela kecil: jam wahana melambat, memerah, membeku di horizon. Penghitung "pulsa belum tiba" terus naik setelah horizon |
| Diagram ruang-waktu | Kanvas 2D, Eddington-Finkelstein masuk: kerucut cahaya makin miring, garis dunia wahana, pulsa |
| Uji suar | E di dalam horizon: suar ditembak "keluar" pada c, HUD menunjukkan r suar tetap turun (p^r = eps (cos a - beta) < 0) |
| Arah sebaliknya | Pesan relai ke wahana tetap masuk |

## G5: sudut masuk tesseract (fiksi)

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
| Panel ` | Mulai misi, pilih jalur (susur piringan / kutub) |
| V | Kokpit / kamera luar |
| Z | Kecepatan waktu |
| W A S D, Shift, Enter | Bidik sudut (G5), kunci |
| E | Tembak suar (G4) |
| Esc | Keluar misi |

## Batasan dan catatan

- Render dan lintasan memakai Schwarzschild. Gargantua di buku berputar hampir maksimum (Kerr); Kerr penuh bisa jadi tahap lanjutan.
- Partikel, tumbukan kaca, dan kepadatan piringan distilisasi demi tampilan; piringan akresi nyata jauh lebih tipis dan wahana tidak akan selamat.
- Tesseract dan gerbang murni fiksi. Jatuh, horizon, pulsa, kecepatan relatif, dan sudut tangkap mengikuti fisika.
- Animasi piringan tidak memperhitungkan waktu tunda cahaya.
- Biaya GPU terbesar: lapisan volumetrik dekat kamera (G3). Perlu diukur di GTX 1060 dan M1; bila berat, jumlah langkah dan radius lapisan diturunkan per preset.
- Nama Ranger dan desain kendaraan film tidak dipakai.
