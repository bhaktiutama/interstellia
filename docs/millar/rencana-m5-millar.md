# Rencana M5 Millar's World: Penyempurnaan setelah uji pemilik

Per 3 Oktober 2026 · Status: rencana, belum dikerjakan. Pilihan pemilik: gelombang = tembok tebal; pengerjaan dikelompokkan menurut tingkat thinking (low, medium, high), tiap kelompok berhenti untuk diuji pemilik.

## Context

Pemilik menguji M4b dan menemukan 5 hal yang masih kurang meyakinkan:
1. Percikan saat lari: butir putih terlempar terlalu ke depan, tidak menyatu dengan laut.
2. Dari ketinggian laut terlihat sintetis (pola berulang) dan ada sabit putih (gambar 3).
3. Panas masuk atmosfer berbentuk telur lonjong (gambar 4).
4. Suara terlalu berisik (angin dan langkah lari).
5. Penampang gelombang raksasa harus seperti tembok tinggi (gambar 5), bukan bukit landai.

Tiap butir dikerjakan sebagai tahap terpisah (M5a-M5e), dikelompokkan menurut tingkat thinking (low, medium, high) atas permintaan pemilik. Tiap tahap punya uji otomatis dan commit sendiri; tiap kelompok berhenti untuk diuji pemilik.

Cara menjalankan di sesi baru: "jalankan kelompok 1 dari `docs/millar/rencana-m5-millar.md`" (lalu kelompok 2, lalu 3). Perbarui bagian Status di bawah tiap tahap selesai.

Hak cipta: gambar 5 memuat judul dan logo film. Yang dipakai hanya bentuk fisik penampang gelombang (tembok air tinggi), bukan judul, huruf, atau grafisnya.

## Kelompok menurut tingkat thinking dan model

Catatan: CLAUDE.md proyek tidak mendefinisikan tingkat thinking atau model. Pengelompokan di bawah memakai daftar model yang tersedia di sesi ini (Opus 5.5 paling mampu, Sonnet 5.5) dan tingkat usaha low / medium / high. Tiap kelompok dikerjakan dalam satu jalan, commit dan push per tahap, lalu berhenti untuk diuji pemilik sebelum kelompok berikutnya.

| Kelompok | Tahap | Isi | Model + thinking | Alasan | Risiko |
| --- | --- | --- | --- | --- | --- |
| 1. Low | M5a-1 | Sabit putih (bug pusat grid laut) | Sonnet 5.5, low | Sebab sudah ditemukan, perbaikan beberapa baris di `frame()` dan `seaMat()` | Rendah |
| 1. Low | M5b | Suara lebih tenang | Sonnet 5.5, low | Penyetelan angka dan filter di `audioMix()` / `startAudio()` / `sfxSplash()`, 2 penggeser di panel | Rendah |
| 2. Medium | M5a-2 | Pola laut sintetis dari ketinggian | Opus 5.5, medium | Variasi makro di shader laut, perlu menjaga FPS dan uji ombak FFT | Sedang |
| 2. Medium | M5d | Selubung plasma mengikuti bentuk wahana | Opus 5.5, medium | Shader baru tetapi terisolasi di adegan orbit | Rendah (hanya sinematik) |
| 3. High | M5c | Percikan lari menyatu dengan laut | Opus 5.5, high | Gabungan riak, buih, mahkota air, dan partikel; menyentuh sim `RIP` dan shader laut dekat | Sedang |
| 3. High | M5e | Penampang gelombang raksasa = tembok tebal | Opus 5.5, high | Profil GLSL + kembaran JS + geometri + semburan + fisika tersapu/terbang + uji | Tinggi (banyak sistem bergantung pada `waveG`) |

Isi teknis tiap tahap di bawah tetap memakai nomor M5a sampai M5e.

## M5a. Sabit putih dan pola laut dari ketinggian

**Penyebab sabit (sudah ditelusuri):** pusat laut dekat dan laut jauh tidak sama. Di `frame()`, grid laut dekat digeser ke `P` (`seaNear.material.uniforms.uOff` dibulatkan dari `P.x/P.z`). Laut jauh juga digeser ke `P` (`seaFar...uOff.set(P.x, 0, P.z)`, cincin dalam mulai `P.near - 3`). Tapi shader laut dekat membuang piksel berdasarkan jarak ke **kamera** (`if (length(vR.xz) > uNearR) discard;` di `seaMat()`). Saat terbang, `P` = posisi wahana sementara kamera kejar 20 m di belakang, jadi ada pita yang tidak tertutup keduanya. Lewat pita itu langit terlihat sebagai sabit putih.

**Perbaikan:**
- Pusat laut = posisi kamera (xz) untuk grid dekat, laut jauh, dan uji buang, satu sumber `SEA.cx/cz` di `frame()`. Riak tetap berpusat di pemain (`RIP` tidak berubah).
- Radius laut dekat dan jarak pudar ombak ikut ketinggian kamera (`uNearR` efektif = max(near, 1,2 x tinggi)) supaya dari 300 m tidak terlihat cakram detail kecil.

**Pola sintetis:** petak FFT 37 m berulang dan buih Jacobian berulang dengan pola sama.
- Variasi makro: noise skala 300-1.500 m yang mengubah amplitudo normal, kekuatan buih, dan warna hamburan (di `seaShadeS` / `surfS`).
- Sampel kaskade kedua diputar dan diskalakan tidak bulat terhadap kaskade pertama, supaya periode gabungan sangat panjang.
- Buih memudar dengan jarak kamera dan ketinggian; dari jauh diganti tekstur buih makro (noise memanjang searah angin).
- Ombak panjang 80-200 m (2-3 Gerstner tambahan, tinggi kecil) untuk gerak besar yang tidak berulang.

**Uji baru:** di ketinggian 120 m dan 600 m, kamera kejar, render HDR: tidak ada piksel laut di dalam radius 1,5 x near yang sama dengan warna langit (sabit hilang). Ukuran pola: autokorelasi luminansi pada pergeseran 37 m turun di bawah ambang (sebelum vs sesudah).

## M5b. Suara lebih tenang

**Sumber berisik (dari `audioMix()` dan `startAudio()`):**
- Angin: pink noise bandpass 500 Hz, gain 0,16-0,32 terus-menerus.
- Kecipak jalan (`wade`): **white** noise bandpass 750 Hz sampai 0,42 saat lari (desis tajam terus-menerus).
- Efek langkah `sfxSplash` tiap langkah, dua kaki.

**Perbaikan:**
- Angin: gain 0,05-0,14, lowpass 900 Hz, hembusan lambat (amplitudo bergelombang 6-12 s).
- Kecipak: ganti ke brown/pink noise lowpass 450 Hz, gain maks 0,18, dan dibentuk per langkah (denyut mengikuti `BOB.phase`), bukan desis rata.
- `sfxSplash`: volume dikurangi sekitar 40%, durasi lebih pendek, nada acak kecil agar tidak berulang.
- Panel kontrol: 2 penggeser baru "Volume" (master) dan "Angin dan laut" (lapisan lingkungan), tersimpan di localStorage (`millar.vol`, `millar.amb`), teks lewat `t()` + kamus English.

**Uji baru:** di laut tenang saat berlari (speed 3 m/s, depth 0,5), RMS keluaran turun minimal 35% dibanding sekarang, dan pusat spektrum (rata-rata frekuensi berbobot dari AnalyserNode) turun di bawah 900 Hz. Uji lama (gemuruh naik saat gelombang dekat, bisu U) tetap lulus.

## M5c. Percikan lari menyatu dengan laut

Acuan (foto 1-2): air terdorong naik di sekitar tulang kering, gelombang haluan kecil di depan kaki, lembar air bening dan buih putih menempel di permukaan, semprotan pecah di sekitar dan di bawah tubuh (bukan jauh di depan).

**Perbaikan (berlapis):**
1. **Tonjolan dan lekuk air di kaki:** sumber riak positif di depan tulang kering dan cekung di belakang, ikut kecepatan (memakai `ripSource()` dan sim `RIP`, amplitudo naik). Air terlihat terdorong, menyatu dengan permukaan karena memang bagian dari laut.
2. **Buih menempel di permukaan:** kanal buih riak (`rf`) diperkuat di jejak kaki dan di cincin tumbukan tiap langkah, memudar 2-4 s. Buih itulah yang menyatukan percikan dengan laut.
3. **Lembar mahkota air (baru):** tiap langkah, satu mahkota tipis berbentuk cincin miring di sekitar kaki (mesh kecil, naik 0,3-0,5 m lalu jatuh dalam sekitar 0,5 s). Shader air (pantulan langit + hamburan, tembus pandang, tepi putih), bukan titik putih.
4. **Butir semprotan:** jumlah dikurangi, posisi di kaki (0,1-0,2 m di depan, bukan 0,45 m), kecepatan maju hanya sedikit di atas kecepatan pemain (`carry` 1,05-1,15, bukan 1,6-1,75), lebih ke samping dan ke atas. Warna dari pencahayaan air (tidak lebih terang dari buih), sebagian tembus pandang, memanjang searah gerak (titik diregang).
5. **Pandangan pertama:** percikan tetap terutama terlihat saat menunduk (kaki di bawah bidang pandang). Opsional: kaki dan lengan pemain terlihat saat menunduk (model tubuh `SHD.body` dipakai juga untuk tampilan). Usul ini ditanyakan ke pemilik setelah 1-4.

**Uji baru:** butir semprotan tidak terlempar lebih dari 1,2 m di depan kaki saat lari 3 m/s; riak di depan kaki naik (tinggi positif) dan buih di jejak > ambang; mahkota tampil lalu hilang dalam < 0,8 s; render tanpa nilai tidak valid.

## M5d. Selubung plasma masuk atmosfer

Masalah: plasma sekarang = bola dipipihkan (`ORB.plasma`, SphereGeometry diskalakan 3,4 x 2,2 x 6,5) sehingga tampak telur.

**Perbaikan (adegan orbit saja, `orbShip`):**
1. **Panas di lambung:** shader lambung orbit diberi cahaya panas dari arah aliran: sisi yang menghadap aliran (perut dan hidung, `dot(n, -arah gerak)`) menyala jingga sampai putih kekuningan sesuai kekuatan; tepi dan hilir merah gelap. Bentuk cahaya = bentuk wahana sendiri.
2. **Gelombang kejut haluan:** lapisan tipis dari geometri lambung yang digelembungkan sepanjang normal (bukan bola), aditif, Fresnel, hanya di sisi depan aliran, tekstur noise bergerak.
3. **Jejak plasma:** pita aditif memanjang dari ujung sayap dan tepi badan ke belakang (searah aliran), memudar dan bergelombang.
4. **Percik api:** butir kecil terkelupas mengalir ke belakang.
5. Arah aliran = arah gerak di orbit (dari `orbPlaceShip()`), pitch hidung naik saat masuk agar perut menghadap aliran.

**Uji baru:** render adegan 17 s tanpa nilai tidak valid; titik terang terbanyak berada di sisi perut/hidung (bukan merata seperti cangkang); tidak ada objek bola di grup plasma.

## M5e. Penampang gelombang raksasa = tembok

Bentuk sekarang (`waveG()` di `COMMON`, kembaran JS di `waveG`/`waveTop`, `ARC`): muka Gaussian lebar 350 m, punggung landai 5 km. Dari samping terlihat bukit.

**Profil baru (dari penampang gambar 5, pilihan pemilik: tembok tebal):**
- Muka depan cekung dan hampir tegak di 2/3 atas (kemiringan > 75 derajat), kaki depan pendek melengkung.
- Puncak sempit sedikit condong ke depan (`lean` dipertahankan), dengan semburan.
- Punggung turun cukup curam sampai sekitar 20% tinggi dalam 1,5-2,5 km, lalu ekor landai.
- Tinggi tetap 1.200 m, kecepatan 125 m/s.

**Yang harus diubah bersama:**
- `waveG()` GLSL dan JS (satu rumus, kembaran sama persis), `US` (titik profil lebih rapat di muka tegak dan punggung), `ARC`, normal di `waveMat`.
- `wavePosD()` (tonjolan meluncur) dan lapisan semburan / kabut (`SPRAY`) mengikuti tinggi puncak baru.
- Fisika: urutan tersapu (`SWEEP`), kedalaman pemain, `waveTop()` untuk terbang (tertelan / lolos, `CONFIG.fly.passU`), keadaan laut, gemuruh dan deru.
- Waktu misi tidak berubah (muka tetap tiba di detik 300); uji rute dan lepas landas dijalankan ulang.

**Uji baru dan lama:** profil JS = GLSL (sampel 50 titik); kemiringan muka atas > 75 derajat; lebar badan pada setengah tinggi 0,8-2,5 km; uji lama (kerapatan muka, gelombang 125 m/s, tersapu, lolos di atas gelombang, tertelan, preset tanpa nilai tidak valid) tetap lulus, ambang yang bergantung bentuk lama disesuaikan dan dicatat.

## File utama

| File | Tahap |
| --- | --- |
| `experiences/millar/index.html` | Semua: `frame()` (pusat laut), `seaMat()` / `seaShadeS` / `COMMON` (laut, `waveG`), `audioMix()` / `startAudio()` / `sfxSplash()`, `footstep()` / `headBob()` / `spawnSplash()` / `splMat` / `RIP`, `orbShip` / `ORB.plasma` / `cineStep()`, `US` / `ARC` / `waveGeo()` / `WAVE_VS` / `SPRAY` |
| `tools/uji_millar.py` | Uji baru tiap tahap |
| `docs/millar/rencana-m5-millar.md` | Rencana + status tiap tahap |
| `CLAUDE.md` | Peta kode Millar diperbarui di akhir tiap tahap |

## Verifikasi

- Tiap tahap: `CHROMIUM=/opt/pw-browsers/chromium THREE_LOCAL=<scratchpad> python3 tools/uji_millar.py` lulus semua (sekarang 72 pemeriksaan, ditambah uji baru).
- Tangkapan layar sandbox hanya untuk memastikan arah (sabit hilang, plasma, profil gelombang dari samping), tidak berulang-ulang (aturan CLAUDE.md).
- Uji spaceport Copper dijalankan bila `shared/kestrel.js` tersentuh (tidak direncanakan).
- Commit dan push per tahap ke branch kerja, laporan ringkas per tahap (tabel, tanpa em dash). Pemilik menguji visual dan FPS di GTX 1060 dan M1.

## Status

| Kelompok | Tahap | Status |
| --- | --- | --- |
| 1. Low | M5a-1, M5b | Belum |
| 2. Medium | M5a-2, M5d | Belum |
| 3. High | M5c, M5e | Belum |
