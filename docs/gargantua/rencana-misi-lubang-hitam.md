# Rencana Misi Gargantua: Kestrel KS-07 masuk lubang hitam

Per 29 September 2026 · Bhakti

## Ringkasan

- **Masuk langsung (G1):** shuttle Kestrel KS-07 jatuh bebas dari 22 rs lewat kutub (tidak menembus piringan) sampai singularitas. Kamera di shader diganti menjadi kamera yang ikut jatuh, jadi pandangan dari dalam horizon juga benar. HUD menunjukkan jarak, waktu wajar, laju, pergeseran merah, dan gaya pasang surut.
- **Informasi tidak bisa keluar (G3):** kapal mengirim pulsa ke relay yang mengorbit di luar. Relay melihat jam kapal melambat, memerah, lalu membeku di horizon; pulsa yang dikirim setelah horizon tidak pernah tiba. Diagram ruang-waktu memperlihatkan kerucut cahaya yang miring ke dalam.
- **Sudut masuk tesseract (G4):** sebelum titik tanpa kembali, pemain mengatur sudut datang dan bidang orbit. Terlalu lebar = terlempar keluar, terlalu sempit = langsung ke singularitas, memotong piringan = hancur, tepat di bawah sudut kritis = berputar-putar di 2 rs lalu masuk ke gerbang tesseract. Tesseract diberi label fiksi.

Urutan kerja: G1, G2 (kokpit dan model Kestrel), G3, G4, G5 (uji dan bahasa). Tiap tahap bisa diuji sendiri.

Keputusan pemilik di sesi ini: pesawat Kestrel KS-07 (bukan Ranger, sesuai `docs/app/penamaan.md`), kamera kokpit + kamera luar, tesseract berupa hiperkubus 4D abstrak berlabel fiksi (tidak meniru ruang rak buku atau kamar dari film).

## Kondisi sekarang

| Item | Isi | Lokasi (cari nama) |
| --- | --- | --- |
| Render | Ray tracing di fragment shader, satuan rs = 1, M = 0,5. Bentuk lintasan foton dari persamaan Binet (u'' + u = 3 M u^2) dalam koordinat Kartesius datar, integrator Verlet, langkah sebanding r | `SCENE_FS`, `accel()`, loop di `main()` shader |
| Kamera | Pengamat diam di jarak 6-60 rs, arah awal sinar `vel = dir` | `cameraBasis()`, `CAM_PRESETS` |
| Piringan | Bidang y = 0, rIn 3 rs, rOut 12 rs, Doppler dan redshift gravitasi opsional, mode film | `shadeDisk()`, `CONFIG.disk`, `CONFIG.physics` |
| Putaran | Hanya perkiraan dipol gravitomagnetik berlabel, bukan Kerr | `accel()` (uSpin) |
| Bahasa | Sumber English, kamus Indonesia `ID`, fungsi `txt()` | `ID`, `txt()`, `applyStaticLang()` |
| Tanpa three.js | WebGL2 murni, satu segitiga layar penuh, bloom dan streak | `P`, `pass()`, `frame()` |

## Angka dasar

Asumsi massa Gargantua 1e8 massa Matahari (mengikuti buku Kip Thorne, The Science of Interstellar, 2014). Semua angka di bawah dihitung dengan konstanta G = 6,674e-11, c = 2,998e8 m/s, massa Matahari 1,989e30 kg. Kapal dianggap jatuh dari diam di jauh tak hingga (E = 1, "rain frame").

| Item | Nilai | Rumus |
| --- | --- | --- |
| Radius Schwarzschild rs | 2,954e8 km (1,97 AU) | 2GM/c^2 |
| Satuan waktu rs/c | 985,3 s | |
| Jatuh 22 rs ke horizon | 67.123 s = 18,65 jam waktu wajar | (2/3)(r0^1,5 - 1) rs/c |
| Horizon ke singularitas | 656,8 s = 10,9 menit | (2/3) rs/c |
| Waktu wajar maksimum di dalam horizon | 1.547,7 s = 25,8 menit | (pi/2) rs/c, jatuh bebas dari diam tepat di horizon |
| Pasang surut tubuh 2 m di horizon | 2,1e-7 g | 2GML/r^3 |
| Pasang surut mencapai 1 g (awal spagetifikasi) | r = 0,00594 rs (1,756e6 km), 0,30 s sebelum singularitas | |
| Laju jatuh lokal di 22 rs | 0,213 c | sqrt(rs/r), relatif pengamat diam |
| Laju jatuh lokal di 3 rs | 0,577 c | |
| Percepatan untuk melayang diam di 22 rs | 321,7 m/s^2 = 32,8 g | GM / (r^2 sqrt(1 - rs/r)). Tidak dipakai: Kestrel datang dari jauh, tidak melayang |
| Langit di belakang saat melewati horizon | frekuensi x 0,5 (memerah) | 1 / (1 + beta), beta = 1 |
| Sudut tangkap kritis d_krit (dari arah radial masuk) | 24,62 derajat di 22 rs; 36,87 di 10 rs; 48,19 di 6 rs | sin d = 2 rs / (r0 gamma v), gamma v = sqrt(rs/r0) / sqrt(1 - rs/r0); L_krit = 2 rs (4M) |

Waktu jatuh asli 18,65 jam, jadi misi memakai percepatan waktu (tombol T). HUD selalu menampilkan waktu wajar asli.

## Inti fisika render

Satu perubahan kunci di shader: arah awal jejak sinar untuk kamera yang ikut jatuh.

| Item | Sekarang | Mode misi |
| --- | --- | --- |
| Arah awal jejak mundur | `vel = dir` | `vel = dir + beta * r_hat`, beta = sqrt(rs/r) |
| Kamera di dalam horizon | Tidak mungkin (sinar langsung dianggap tertelan) | Boleh: semua jejak mundur bergerak ke r lebih besar (cahaya yang diterima datang dari luar) |
| Aturan tertelan | `r < RS` | `r < RS && dot(pos, vel) < 0` |
| Frekuensi teramati | Pengamat diam | eps_obs = E / (1 - beta cos a), a = sudut arah rambat foton dari r_hat |

Asal rumus: di koordinat Painleve-Gullstrand, momentum foton yang dilihat pengamat jatuh adalah p^r = eps (cos a - beta), p^phi = eps sin a / r. Jadi dr/dphi = r (cos a - beta) / sin a. Bentuk orbit (r, phi) sama di koordinat Schwarzschild, jadi integrator Binet yang ada tetap dipakai, hanya arah awalnya yang berubah. Di luar horizon hasil ini sama persis dengan transformasi aberasi ke kerangka diam; di dalam horizon (beta > 1) tetap berlaku.

Untuk lintasan dengan momentum sudut (G4): kecepatan kapal relatif rain frame dihitung dari persamaan kuadrat (beta^2 - 1) w^2 + 2 E beta w + E^2 - 1 - L^2/r^2 = 0 (reguler di horizon), u^T = E + beta w, lalu arah kamera ditransformasi dengan aberasi biasa sebelum rumus di atas.

Pertahankan yang ada: uniform baru `uFall` (0 = perilaku lama persis, termasuk aturan tertelan), `uBeta`, dan basis kamera kapal. Preset 1-4, panel, dan tampilan lama tidak berubah saat misi mati.

Lintasan kapal dihitung di CPU: geodesik timelike Schwarzschild, RK4 pada (r, dr/dtau, phi) dengan d2r/dtau2 = -M/r^2 + L^2/r^3 - 3 M L^2/r^4 dan dphi/dtau = L/r^2. Waktu PG ikut diintegrasikan untuk menjalankan animasi piringan.

## G1: masuk langsung

| Bagian | Isi |
| --- | --- |
| Masuk misi | Tombol Misi di panel + tombol M. Kamera bertransisi ke posisi Kestrel di 22 rs di atas kutub |
| Lintasan | Jatuh radial sepanjang sumbu putar piringan (tidak menembus piringan). Pilihan kedua: jalur miring yang aman (lihat G4) |
| Kamera | Kamera jatuh di shader (rumus di atas). Pandangan yang diharapkan: bayangan hitam membesar sampai memenuhi separuh langit, piringan terlihat dari atas sebagai cincin, langit bintang di belakang menyempit dan memerah. Saat melewati horizon tidak ada tanda visual tiba-tiba |
| HUD | r (rs dan km), waktu wajar sejak lepas, sisa waktu wajar ke singularitas, laju lokal (c), faktor pergeseran langit depan dan belakang, pasang surut tubuh 2 m (g), status (di luar / horizon / di dalam) |
| Waktu | T mengganti percepatan waktu (misal x100, x1.000, x10.000); di dekat horizon dan di dalam turun otomatis agar 10,9 menit terakhir terasa |
| Akhir | Di r = 0,006 rs (pasang surut 1 g, 0,30 s sebelum singularitas): layar gelap bertahap dan ringkasan misi (waktu wajar total, waktu menurut relay = tak hingga) |

## G2: Kestrel KS-07

| Bagian | Isi |
| --- | --- |
| Kokpit | Bingkai jendela dan panel instrumen digambar di kanvas 2D di atas render (bukan meniru kokpit film). Instrumen memakai angka HUD G1 |
| Kamera luar (V) | Model badan Kestrel (badan pengangkat superellipse 24 m, sirip miring ganda, 3 mesin) dipindah dari generator `SHUTTLE` di `experiences/cooper-station/index.html` sekitar baris 9058. Tanpa three.js: array posisi, normal, warna dibuat langsung |
| Render | Program raster kecil dengan depth, digambar ke `T.scene` sebelum bloom, disinari dari arah piringan, bagian gelap diberi ambient redup |
| Akurasi | Kapal 24 m jauh lebih kecil dari rs (2,954e11 m), jadi pembelokan cahaya di skala kapal dapat diabaikan; menggambar kapal tanpa lensa gravitasi tetap benar |
| Biaya | Ribuan segitiga, satu draw call |

## G3: informasi tidak bisa keluar

| Bagian | Isi |
| --- | --- |
| Relay | Satelit relai orbit melingkar di 22 rs (orbit stabil, di luar ISCO 3 rs). Desain orisinal sederhana, bukan pesawat induk film |
| Pulsa | Kapal mengirim pulsa tiap 1 s waktu wajar (dipercepat bersama waktu). Waktu tiba di relay: t_tiba = u_kirim + r*(r_relay), u = t - r*, r* = r + rs ln abs(r/rs - 1). u_kirim menuju tak hingga saat r menuju rs |
| Pandangan relay | Jendela kecil: gambar kapal dan jam kapal seperti dilihat relay. Jam melambat, warna memerah, kecerahan turun, lalu membeku di waktu wajar saat horizon. Pulsa setelah horizon: penghitung "belum tiba" terus naik |
| Diagram ruang-waktu | Kanvas 2D, koordinat Eddington-Finkelstein masuk (v, r): kerucut cahaya makin miring ke dalam, di horizon sisi luar kerucut tegak, di dalam seluruh kerucut menuju r kecil. Garis dunia kapal dan tiap pulsa digambar |
| Uji suar | Di dalam horizon tombol untuk menembak suar "keluar" dengan laju c di kerangka kapal. HUD menunjukkan r suar tetap turun (p^r = eps (cos a - beta) < 0 karena beta > 1) |
| Arah sebaliknya | Pesan dari relay ke kapal tetap masuk walau kapal di dalam horizon (informasi bisa masuk, tidak bisa keluar) |

## G4: sudut masuk tesseract

| Bagian | Isi |
| --- | --- |
| Bidik | Sebelum titik tanpa kembali, pemain mengatur sudut d (dari arah radial masuk) dan orientasi bidang orbit. WASD halus, Shift kasar, Enter kunci |
| Prediksi | Peta orbit 2D dengan lintasan hasil integrasi CPU, piringan 3-12 rs, horizon, lingkaran foton 1,5 rs, orbit tak stabil 2 rs, gerbang |
| Hasil d > d_krit | Terlempar kembali ke luar (tidak tertangkap) |
| Hasil d jauh di bawah d_krit | Langsung ke singularitas (misi G1) |
| Hasil bidang memotong piringan | Bila lintasan menembus bidang y = 0 di 3-12 rs: kapal hancur |
| Hasil d sedikit di bawah d_krit | Zoom-whirl: kapal berputar beberapa kali di sekitar r = 2 rs lalu jatuh. Jumlah putaran (naik secara logaritmik saat d mendekati d_krit) menentukan azimut masuk horizon |
| Gerbang tesseract (fiksi) | Di dalam horizon, pada azimut dan bidang tertentu, toleransi +/- 5 derajat. Masuk gerbang = berhasil |
| Tesseract | Hiperkubus 4D (objek matematika) berputar di 4D, diproyeksikan 4D ke 3D ke layar, garis bercahaya orisinal. Label tetap: "Fiksi / spekulatif: fisika nyata tidak mengenal tesseract di dalam lubang hitam" |

## G5: uji dan bahasa

| Bagian | Isi |
| --- | --- |
| `tools/uji_misi_gargantua.py` (baru) | Lewat `window.__gargantua`: waktu jatuh 22 rs ke horizon dan horizon ke singularitas vs rumus, d_krit 24,62 derajat vs hasil integrator (tertangkap / lolos di d_krit +/- 0,1 derajat), faktor langit belakang 0,5 di horizon, tanpa NaN saat kamera di r 0,5 dan 0,01 rs, `uFall = 0` hasil render sama dengan sebelum perubahan |
| Bahasa | Semua teks baru sumber English dengan entri kamus `ID` (aturan Gargantua), dipakai lewat `txt()` |
| Cek muat | `python tools/qc_load.py experiences/gargantua/index.html` tanpa error |
| CLAUDE.md | Tabel struktur repo ditambah alat uji baru |

## Tombol baru

| Tombol | Fungsi |
| --- | --- |
| M | Mulai / keluar misi |
| V | Kokpit / kamera luar |
| T | Percepatan waktu |
| W A S D, Shift, Enter | Bidik sudut (G4), kunci |
| Esc | Keluar misi |

Tidak bentrok dengan tombol lama: Space, H, F, P, R, 1-4.

## Batasan dan catatan

- Render dan lintasan memakai Schwarzschild (tanpa putaran). Gargantua di buku berputar hampir maksimum (Kerr); putaran di kode sekarang hanya perkiraan berlabel. Kerr penuh bisa menjadi tahap lanjutan, bukan bagian rencana ini.
- Kestrel datang dengan E = 1 (dari jauh). Anggaran bahan bakar untuk koreksi sudut tidak realistis dan disederhanakan.
- Tesseract dan gerbang murni fiksi. Bagian jatuh, horizon, pulsa, dan sudut tangkap mengikuti fisika.
- Animasi piringan tidak memperhitungkan waktu tunda cahaya.
- Biaya GPU: tambahan beberapa operasi per piksel di shader, raster Kestrel ribuan segitiga. Jejak dari dalam horizon butuh sekitar 140 langkah (perkiraan: langkah sebanding r dari 0,01 sampai 50 rs), masih di bawah 200 langkah preset Sedang. Perlu diukur di GTX 1060 dan M1.
- Nama Ranger dan desain kendaraan film tidak dipakai.
