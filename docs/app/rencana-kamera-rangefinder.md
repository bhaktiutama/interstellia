# Rencana K: Mode kamera rangefinder (semua experience)

Per 7 Oktober 2026 · Status: rencana, belum dikerjakan. Berlaku untuk Copper Corn Station, Millar's World, dan Gargantua; dikerjakan di Copper dulu.

## Ringkasan

- Mode foto lama diganti pengalaman memegang kamera rangefinder full frame: pilih lensa (21-90 mm), aperture, kecepatan rana, ISO; membidik lewat jendela bidik optik dengan garis bingkai, patch rangefinder untuk fokus, dan HUD LED di bawah jendela.
- Foto diambil dengan render akumulasi (banyak subframe): kedalaman bidang dan bokeh dari sampel bukaan lensa sungguhan, motion blur dan eksposur lama dari waktu rana, derau sensor dari ISO. Video direkam lewat live view (EVF) dengan `MediaRecorder` plus suara.
- Logika bersama ada di modul baru `shared/camera.js` (`window.CAMKIT`); tiap experience hanya menyediakan kait (FOV, tap HDR, meter cahaya, langkah dunia). Mode foto lama tetap ada sebagai "Foto bebas".

## Context

Permintaan pemilik: mode kamera yang lebih realistis, bisa memilih lensa, ISO, aperture, speed, terasa memakai viewfinder rangefinder, ada HUD kamera di viewfinder, bisa ambil foto atau video.

Kondisi saat ini (hasil telusur kode):

| Fakta | Lokasi |
| --- | --- |
| Copper: `PHOTO` (fov, focus, blur, pause), panel `#photo` dengan slider jam, FOV, fokus, blur, eksposur; Enter simpan PNG lewat `window.__captureCb` | `experiences/cooper-station/index.html` blok "TAHAP 12d (C2)" (`togglePhoto()`, `applyPhoto()`, `savePhoto()`) |
| Copper: DOF di `compMat` = `cocAt(dist)` dengan `uDof` x jarak relatif, bukan rumus lensa; kedalaman `tDepth` tersedia | `compMat` (`uDof`, `uFocus`, `cocAt`) |
| Copper: adaptasi mata `ADAPT` (key 0,16, pow 0,6, min 0,45, max 2,2) dari luminans rata-rata `POST_R.lum` | `ADAPT`, `postEnd()` |
| Millar: `PHOTO` hanya { on, shot }: UI disembunyikan, Enter = `canvas.toBlob` PNG | `togglePhoto()`, `savePhoto()` |
| Millar: kedalaman `POST.hdr.depthTexture` hanya dibuat di Ultra (untuk TAA); resolusi dinamis `DYN` mengubah ukuran render | `makePost()`, `DYN` |
| Gargantua: `state.photo` hanya kelas CSS; Enter = `state.shot`; eksposur otomatis misi `AE` | `togglePhoto()`, `AE` |
| Semua: audio disintesis dengan simpul master (`AUDIO.master` Copper, `N.master` Gargantua, `AUDIO` Millar) | blok audio tiap experience |
| Uji yang memakai mode foto: `tools/uji_ladang_foto_tur.py` memanggil `togglePhoto(true)` lalu slider `phFov` / `phBlur` / `phPause`; `tools/uji_millar.py` menekan F dan memeriksa `PHOTO.on` + kelas `photo` | kedua file |
| Tombol huruf praktis habis (`docs/app/tombol.md`); tombol khusus Copper (B, G, E, M, L, T, I, C) tidak boleh dipakai untuk fungsi umum | `docs/app/tombol.md`, `CLAUDE.md` |

## Keputusan desain

1. **Mode kamera = jenis baru di dalam mode foto.** `PHOTO.kind` = `'kamera'` (baru) atau `'bebas'` (panel lama, tidak berubah). `PHOTO.on` dan kelas `body.photo` tetap dipakai, jadi uji lama tetap berlaku. F membuka jenis terakhir (bawaan: kamera); `togglePhoto(true)` dari skrip tetap membuka "bebas" seperti sekarang. Pindah jenis lewat tombol di panel.
2. **Jendela bidik optik, bukan lewat lensa.** Seperti rangefinder sungguhan, jendela bidik memperlihatkan dunia tajam semua (tanpa DOF), lebih lebar dari lensa, dengan garis bingkai lensa terpilih. Eksposur, ISO, dan DOF tidak terlihat di jendela bidik; yang memberi tahu adalah meter LED. Pratinjau hasil lewat layar belakang (tinjau foto) atau live view.
3. **Live view (EVF) untuk video dan pratinjau.** Tombol V (standar "tampilan") di mode kamera berganti jendela bidik optik dan live view. Live view memperlihatkan bidang lensa sebenarnya dengan DOF real-time, eksposur, dan derau. Video selalu direkam dari live view (kamera rangefinder digital juga merekam video lewat live view).
4. **Foto = render akumulasi.** Saat rana ditekan, N subframe dirender ke target HDR float: tiap subframe digeser Halton (anti alias), posisi kamera disampel di bukaan lensa (DOF dan bokeh fisik), dan waktu dunia maju sepanjang waktu rana (motion blur). Bloom, ACES, dan derau dihitung sekali dari hasil akumulasi.
5. **Eksposur dijangkar ke tampilan sekarang.** Kalibrasi tidak memakai cd/m2 sungguhan (skala HDR tiap experience berbeda dan tidak terkalibrasi). Bila EV setelan kamera = EV hasil meter, gambar sama terangnya dengan tampilan sekarang (adaptasi mata / AE). Tiap selisih 1 stop = faktor 2.
6. **Format sensor 36 x 24 mm (3:2).** Foto dipotong 3:2 dari tengah kanvas, video 16:9 (36 x 20,25 mm).
7. **Merek dan desain:** kamera fiksi tanpa nama merek; tidak meniru bentuk badan, logo, atau huruf merek kamera nyata. Bunyi rana disintesis (bukan rekaman).
8. **Tombol lokal mode kamera** memakai tombol yang tidak termasuk tombol khusus Copper (lihat tabel Tombol). WASD dan mouse tetap jalan, jadi bisa berjalan sambil membidik.

## Spesifikasi kamera

### Lensa

| Lensa | Bukaan maks | Fokus min | Bidang 3:2 H x V (derajat) | Bidang video 16:9 V (derajat) | Pasangan garis bingkai |
| --- | --- | --- | --- | --- | --- |
| 21 mm | f/2,8 | 0,7 m | 81,2 x 59,5 | 51,5 | tanpa (bidik luar, seluruh jendela) |
| 28 mm | f/2,8 | 0,7 m | 65,5 x 46,4 | 39,8 | 28 / 90 |
| 35 mm | f/1,4 | 0,7 m | 54,4 x 37,8 | 32,3 | 35 / 135 (135 tidak ada lensanya, garis tetap tampil) |
| 50 mm | f/1,4 | 0,7 m | 39,6 x 27,0 | 22,9 | 50 / 75 |
| 75 mm | f/2 | 0,7 m | 27,0 x 18,2 | 15,4 | 50 / 75 |
| 90 mm | f/2,4 | 1,0 m | 22,6 x 15,2 | 12,8 | 28 / 90 |

Derivasi bidang: 2 x atan(setengah sisi sensor / fokus), setengah sisi 18 / 12 / 10,125 mm. Bukaan maks dan fokus min adalah pilihan desain (tipikal lensa rangefinder), bukan data produk tertentu.

Karakter per lensa (kecil, bisa dimatikan): vinyet cos^4 ditambah vinyet optik saat bukaan penuh, distorsi tong 21 mm, aberasi kromatik lateral di tepi.

### Aperture, rana, ISO

| Setelan | Nilai |
| --- | --- |
| Aperture (setengah stop) | 1,4 · 1,7 · 2 · 2,4 · 2,8 · 3,4 · 4 · 4,8 · 5,6 · 6,7 · 8 · 9,5 · 11 · 13 · 16 (dibatasi bukaan maks lensa) |
| Rana (penuh stop) | 1/4000 · 1/2000 · 1/1000 · 1/500 · 1/250 · 1/125 · 1/60 · 1/30 · 1/15 · 1/8 · 1/4 · 1/2 · 1 · 2 · 4 · 8 s · B (tahan, maks 30 s) |
| ISO (1/3 stop) | 100 sampai 12.800 |
| Mode eksposur | M (manual), A (prioritas aperture, rana otomatis), P (otomatis); kompensasi -3 sampai +3 EV (1/3 stop) |
| Bilah aperture | 9 bilah, membulat di bukaan penuh, bersudut saat diciutkan (bentuk bokeh) |

### Rumus (di `CAMKIT`, diuji tanpa browser)

| Besaran | Rumus | Contoh (derivasi) |
| --- | --- | --- |
| EV setelan | EV100 = log2(N^2 / t) - log2(ISO / 100) | f/16, 1/125, ISO 100 = 14,97 (aturan "sunny 16") |
| EV meter | EV100m = log2(Lavg x C x 100 / 12,5) (meter pantul, K = 12,5), C kalibrasi per experience | C dipilih supaya siang Copper terbaca sekitar EV 13-14 (pilihan desain, belum diukur) |
| Pengali eksposur | k = kSekarang(Lavg) x 2^(EV100m - EV100 + komp) | setelan tepat meter = tampilan sekarang persis |
| Diameter CoC di sensor | c = f^2 / (N (s - f)) x abs(d - s) / d | 50 mm f/1,4, fokus 2 m, objek jauh: 0,916 mm = 41,2 px pada tinggi 1.080 px |
| | | 50 mm f/16, sama: 0,080 mm = 3,6 px |
| | | 90 mm f/2,4, fokus 5 m, objek jauh: 0,687 mm = 30,9 px |
| Jarak hiperfokal | H = f^2 / (N c0) + f, c0 = 0,03 mm | 28 mm f/8 = 3,29 m; 50 mm f/8 = 10,47 m |
| Jari-jari bukaan (sampel lensa) | r = f / (2N) | 50 mm f/1,4 = 17,86 mm; 28 mm f/2,8 = 5,00 mm |
| Derau sensor (domain linear setelah eksposur) | sigma^2 = a0 (ISO / 100) x + b0 (ISO / 100)^2 | a0, b0 nilai awal untuk disetel pemilik; ISO 100 hampir tanpa derau |
| Getar tangan | sudut acak sepanjang waktu rana, amplitudo naik bila t > 1 / fokus (aturan 1/fokus) | 50 mm aman sampai sekitar 1/50 s; tripod (panel) = 0 |

Contoh lain EV: f/1,4, 1/30, ISO 3200 = 0,88 (malam di dalam ruangan); f/2, 1 s, ISO 800 = -1,00.

### Jendela bidik rangefinder

| Unsur | Desain |
| --- | --- |
| Bidang jendela | Render dengan bidang horizontal 68 derajat (sedikit lebih lebar dari bingkai 28 mm), mirip jendela pembesaran 0,72x. Pembesaran 0,58 / 0,72 / 0,85 pilihan di panel |
| Masker okuler | Kanvas 2D overlay (DOM, tidak ikut terekam): sekeliling gelap, sudut membulat, vinyet okuler halus, sedikit bayangan bila mata "bergeser" (ikut gerak kepala) |
| Garis bingkai | Garis terang putih kekuningan, berpasangan seperti di atas; bergeser oleh paralaks saat fokus dekat (jendela bidik berada di samping atas lensa, geser = atan(jarak jendela-lensa / jarak fokus)) |
| Patch rangefinder | Kotak kecil di tengah (sekitar 6% lebar): gambar kedua digeser horizontal, sedikit kekuningan. Geser sudut = B x (1/d - 1/s), B = basis efektif 50 mm (pilihan desain). Pada 1.920 px lebar dan bidang 68 derajat: objek 2 m saat fokus tak hingga = 35,6 px, 10 m = 7,1 px, 50 m = 1,4 px (jadi fokus jauh sulit dibedakan, sesuai rangefinder nyata). Fokus pas = dua gambar menyatu |
| Geser per piksel | Dihitung di shader komposit dari kedalaman piksel (Copper `tDepth`; Millar kedalaman dibuat juga di luar Ultra saat mode kamera; Gargantua: tak hingga kecuali wahana) |
| HUD LED (bawah jendela) | Segmen merah redup gaya LED: kecepatan rana, aperture, ISO, panah meter (kurang / pas / lebih, titik tengah = tepat), kompensasi, mode M / A / P, sisa ruang atau jumlah frame, titik REC + kode waktu saat merekam, ikon tripod. Tulisan dari `CAMKIT`, ikut `t()` / `txt()` untuk label |
| Tinjau foto | Setelah rana: gambar mini hasil di "layar belakang" pojok bawah 2 s, panah histogram kecil (luminans) |

### Live view (EVF) dan video

| Unsur | Desain |
| --- | --- |
| Bidang | Bidang lensa sebenarnya (3:2 untuk foto, 16:9 untuk video), tanpa garis bingkai |
| DOF real-time | Shader DOF bersama `POSTKIT.DOF_FS` (gather sadar kedalaman, CoC dari rumus di atas, batas 32 px pada 1.080 px); Copper mengganti `cocAt` lama hanya saat mode kamera |
| Eksposur dan derau | Pengali k dan derau ISO tampil langsung |
| Motion blur video | Blur kamera dari reproyeksi kedalaman (matriks frame sebelumnya), panjang = sudut rana (bawaan 180 derajat = 1/48 s di 24 fps) |
| Perekam | `canvas.captureStream(fps)` + `MediaRecorder`; format `video/mp4;codecs=avc1` bila didukung, selain itu `video/webm;codecs=vp9` / `vp8`; fps 24 / 30 / 60; bitrate bawaan 8 Mbps (sekitar 60 MB per menit, derivasi 8 / 8 x 60) |
| Suara | `AudioContext.createMediaStreamDestination()` disambung dari simpul master experience, trek digabung ke stream video; bunyi rana dan bip REC tidak ikut |
| Batas | Maks 10 menit per klip (sekitar 600 MB di memori pada 8 Mbps); peringatan di HUD 1 menit sebelum habis |
| Selama merekam | `DYN` (Millar) dan turun preset otomatis (Copper, Millar, Gargantua) dibekukan supaya ukuran kanvas tidak berubah di tengah klip |

## Tombol (hanya saat mode kamera)

| Tombol | Fungsi | Catatan |
| --- | --- | --- |
| F / Esc | Keluar mode kamera | standar |
| Klik kiri / Enter | Rana (foto) atau mulai / berhenti rekam (video) | klik saat kursor belum terkunci = kunci kursor dulu |
| Roda mouse | Cincin fokus (0,7 m sampai tak hingga, skala 1/d) | |
| Shift + roda, atau , dan . | Cincin aperture | |
| [ dan ] | Kecepatan rana | di luar mode kamera tetap geser jam (Copper) |
| - dan = | ISO | di luar mode kamera tetap zoom kamera luar (Copper) |
| Shift + - dan = | Kompensasi eksposur | |
| 1-6 | Lensa 21 / 28 / 35 / 50 / 75 / 90 mm | di luar mode kamera tetap lokasi / preset |
| Tab | Foto / video | |
| V | Jendela bidik optik / live view | standar "tampilan" |
| Klik kanan tahan | Kunci eksposur (AE-L) di mode A dan P | |
| H | Sembunyikan HUD LED dan garis bingkai | standar |
| ` | Panel kamera (mode M / A / P, tripod, pembesaran jendela, format PNG / JPEG, resolusi, fps, bitrate, getar tangan, karakter lensa, Foto bebas) | standar |
| WASD, Shift, mouse, Z | Tetap seperti biasa (jalan, lari, menoleh, kecepatan waktu untuk jejak bintang / lampu) | |

Tombol khusus Copper (B, G, E, M, L, T, I, C) tidak dipakai. Mode M / A / P lewat panel.

Batas per experience:

| Experience | Mode kamera boleh saat | Tidak boleh saat |
| --- | --- | --- |
| Copper | jalan, di udara, dek pandang, trem, lift, kapsul, hub nol-g, shuttle sandar | naik motor bergerak (tangan di setang), shuttle terbang, tur |
| Millar | jalan kaki (visor dan tubuh disembunyikan seperti mode foto), drone | terbang, sinematik, tersapu |
| Gargantua | di luar misi, atau misi dijeda (Space) | misi berjalan (F = dorongan) |

## Kelompok menurut effort dan model

| Tahap | Isi | Effort | Model | Thinking | Risiko |
| --- | --- | --- | --- | --- | --- |
| K1 | `shared/camera.js` inti: tabel lensa, nilai stop, rumus EV / CoC / hiperfokal / bidang, mode M / A / P, nama berkas, sisip metadata PNG; uji Node | Medium | Sonnet 5.5 | medium | Rendah |
| K2 | Copper: jenis kamera di `PHOTO`, jendela bidik optik (bidang lebar), overlay 2D (masker, garis bingkai + paralaks, HUD LED), patch rangefinder di `compMat`, tombol lokal | Medium | Sonnet 5.5 | medium | Sedang |
| K3 | Eksposur fisik: kalibrasi C, meter berbobot tengah dari `POST_R.lum`, pengali k di `compMat`, derau sensor ISO (sebelum ACES), meter LED, AE-L | High | Opus 5.5 | high | Sedang (derau di shader rawan NaN di M1: `sqrt` dari varians negatif) |
| K4 | Tangkap foto akumulasi: tap HDR sebelum komposit, Halton + sampel bukaan berbilah, waktu dunia dibekukan, potong 3:2, layar dibekukan selama proses (tanpa blackout), PNG / JPEG + metadata, tinjau foto, bunyi rana | High | Opus 5.5 | xhigh | Tinggi (pipeline post, TAA, GTAO, peta bayangan per subframe) |
| K5 | Rana lambat: dunia maju per subframe (kait `stepWorld(dt)`), motion blur objek, B sampai 30 s (jejak lampu mobil, trem), getar tangan + tripod | High | Opus 5.5 | high | Tinggi (langkah simulasi Copper bergantung `performance.now`) |
| K6 | Live view + video: `POSTKIT.DOF_FS`, blur kamera sudut rana, `MediaRecorder` + audio, pembekuan `DYN` / preset, HUD REC | Medium (DOF dan blur: High) | Sonnet 5.5; Opus 5.5 untuk shader | medium / high | Sedang |
| K7 | Millar: kait kamera, kedalaman di semua preset saat mode kamera, visor / tubuh, audio | Medium | Sonnet 5.5 | medium | Sedang |
| K8 | Gargantua: kait kamera (raster wahana + ray tracer), akumulasi anti alias, DOF hanya wahana / kokpit, `AE` sebagai meter, batas misi | Medium | Sonnet 5.5 | medium | Sedang |
| K9 | Mekanis: `I18N.en` / kamus `ID` / `txt()`, bantuan, `docs/app/tombol.md`, `CLAUDE.md`, `FEATS` / `KEYS` menu utama | Low | Haiku 4.5 | low | Rendah |

Rencana ini disusun satu tingkat di atas tahap terberat (K4 High). Tahap berurutan; commit dan push per tahap; pemilik menguji visual dan FPS di GTX 1060 dan M1 setelah K2, K4, dan K6.

## K1. Inti bersama `shared/camera.js` (Medium)

**Isi `window.CAMKIT`** (skrip biasa, jalan dari file://, tanpa three.js):

| Fungsi | Kegunaan |
| --- | --- |
| `LENSES`, `APERTURES`, `SHUTTERS`, `ISOS` | Tabel di atas |
| `fovV(f, aspect)` / `fovH(f)` | Bidang dari fokus dan format |
| `ev100(N, t, iso)`, `evMeter(lum, C)`, `expMul(kNow, evM, evS, comp)` | Eksposur |
| `coc(f, N, s, d)`, `cocPx(...)`, `hyperfocal(f, N)`, `apertureR(f, N)` | Lensa |
| `bladeSample(i, n, N, blades)` | Titik sampel di poligon bilah (Halton 2D dipetakan ke poligon membulat) |
| `autoSet(mode, evM, cam)` | Mode A / P: pilih rana / aperture terdekat |
| `rfShift(B, d, s)`, `frameLines(lens, s)` | Patch dan garis bingkai + paralaks |
| `fileName(app, cam)`, `pngWithText(blob, meta)` | Nama berkas `cooper-station-20261007-153012-50mm-f2-1-250-iso200.png`, chunk `tEXt` (lensa, f, rana, ISO, experience) dengan CRC32 |
| `recorder(canvas, audioNode, opt)` | Pembungkus `MediaRecorder` (dipakai K6) |
| `hudLed(ctx, cam, w, h)` / `finder(ctx, cam, w, h)` | Gambar overlay 2D (dipakai K2) |

**Uji:** `tools/uji_kamera.py` bagian K1 menjalankan `node` atas `shared/camera.js`: EV f/16 1/125 ISO 100 = 14,97 +- 0,01; CoC 50 mm f/1,4 fokus 2 m = 0,916 mm; hiperfokal 50 mm f/8 = 10,47 m; bidang 50 mm vertikal 3:2 = 26,99 derajat; setengah stop rana dua kali = eksposur dua kali; PNG dengan chunk teks terbaca balik.

## K2. Jendela bidik rangefinder di Copper (Medium)

1. `PHOTO.kind`, `PHOTO.cam` (lensa, N, t, iso, mode, komp, fokus, video, view), simpan di localStorage `lazarus.camera` (bersama tiga experience).
2. Masuk kamera: pointer lock tetap, HUD Copper disembunyikan, overlay kanvas `#camFinder` di atas kanvas WebGL. Bidang render = bidang jendela (68 derajat horizontal, dikonversi ke vertikal sesuai aspek layar). DOF lama mati.
3. Patch rangefinder di `compMat`: uniform `uRf` (on, pusat, ukuran, B x fpx, 1/s), sampel kedua `tHdr` digeser `B x fpx x (1/d - 1/s)` per piksel dengan `d = viewDist(uv)` (dijaga `max(d, 0,05)`), dicampur 50% dan diberi tint; di luar kotak tidak berubah. Bila `uRf.x == 0` jalur identik dengan sebelumnya.
4. Garis bingkai + paralaks + HUD LED digambar `CAMKIT.finder()` tiap frame hanya bila setelan berubah atau fokus bergerak.
5. Tombol lokal dipasang di awal handler `keydown` Copper (sebelum handler lain) saat `PHOTO.on && PHOTO.kind === 'kamera'`, lalu `return`.

**Kriteria selesai:** fokus lewat roda menyatukan dua gambar di patch pada objek 1-10 m; lebar garis bingkai 50 mm = tan(19,8 derajat) / tan(34 derajat) = 0,534 dari lebar jendela (derivasi); keluar = FOV, `uDof`, eksposur, waktu kembali (uji lama tetap lulus).

## K3. Eksposur fisik dan derau ISO (High)

1. Meter: baca luminans rata-rata yang sudah ada (`POST_R.lum`, dibaca asinkron seperti label adaptasi 20b, tanpa baca piksel sinkron), dengan bobot tengah (mip tengah 60% + rata-rata 40%).
2. `kNow` = pengali tampilan sekarang (`POST.exposure` x faktor `ADAPT`); `k = expMul(...)`; adaptasi mata dibekukan saat AE-L dan saat tangkap.
3. Derau di `compMat` sebelum ACES: `x = c x k`; `sigma = sqrt(max(a x + b, 0))`, derau luminans + kroma (kroma lebih besar di bayangan), pola dari hash `gl_FragCoord` + nomor frame; butiran lama (`uGrain`) mati saat mode kamera agar tidak dobel.
4. Jendela bidik optik tidak memakai k (dunia tampak normal); live view dan foto memakai k.
5. Meter LED: panah kiri / kanan / titik dari selisih `EV100m - EV100 + komp` (titik bila |selisih| < 1/3).

**Kriteria selesai:** EV setelan = EV meter -> gambar foto sama dengan tangkapan mode bebas (beda rata-rata piksel < 1%); +1 stop -> luminans linear rata-rata x2 (+- 5% karena ACES diuji sebelum tone map); ISO 12.800 berderau terlihat, ISO 100 hampir bersih; tanpa NaN (uji `isFinite` pada pembacaan buffer).

## K4. Tangkap foto akumulasi (High)

1. **Tap HDR:** fungsi `camAccum(tHdr)` di `postEnd()` setelah scene HDR, sebelum bloom / komposit: menjumlah ke `CAM.acc` (RGBA half float, ukuran render). Pada subframe terakhir, komposit memakai `CAM.acc / N` sebagai `tHdr` sekali (bloom, GTAO tetap dari subframe terakhir, ACES, derau ISO).
2. **Subframe** (bawaan Ultra 32, Tinggi 24, Sedang 16, Rendah dan Hemat 8): proyeksi digeser Halton (pakai `POSTKIT.halton`), TAA dimatikan selama tangkap, posisi kamera digeser `apertureR x bladeSample` di bidang lensa dengan arah pandang diputar agar bidang fokus s tetap (lensa tipis). Waktu dunia dibekukan pada K4 (rana cepat).
3. **Tanpa blackout:** sebelum subframe pertama, gambar jendela terakhir disalin ke kanvas 2D penutup; dilepas setelah selesai. HUD LED menampilkan "busy" (lampu kedip) selama proses. Perkiraan: 32 subframe pada 30 fps = 1,07 s (derivasi 32 / 30).
4. **Bingkai 3:2** dari tengah kanvas: kanvas 1.920 x 1.080 -> foto 1.620 x 1.080 (1,75 MP). Pilihan "Resolusi 2x" (hanya Ultra dan Tinggi) = render tangkap pada pixel ratio 2x lalu kembali; ditandai risiko memori di M1, bisa ditunda.
5. **Simpan:** PNG (bawaan) atau JPEG 92%, metadata `tEXt`, nama berkas dari `CAMKIT.fileName`; tinjau foto 2 s; bunyi rana kain lembut disintesis dari `AUDIO`.

**Kriteria selesai:** 50 mm f/1,4 fokus 2 m: latar jauh kabur dengan bokeh bulat, f/16 latar tajam; titik lampu malam membentuk poligon 9 sisi di f/5,6; tepi gedung tanpa gerigi; foto tanpa NaN; mode jendela kembali normal setelah tangkap (TAA, adaptasi, preset otomatis).

## K5. Rana lambat, motion blur, getar tangan (High)

1. Kait `stepWorld(dt)` per experience: Copper memecah `frame()` jadi `advance(dt)` (simulasi lalu lintas, trem, pejalan kaki, burung, awan, jam) dan `render()`, dengan dt tetap saat tangkap. Millar memakai `simStep()`; Gargantua `stepMission()` / waktu piringan.
2. Waktu rana t dibagi rata ke N subframe (rana < 1/250 s: dunia tidak dimajukan). Untuk t >= 1 s jumlah subframe naik (maks 256, dibatasi waktu proses 15 s); HUD menampilkan hitung mundur.
3. B: tahan klik kiri, lepas = tutup (maks 30 s waktu dunia, berjalan real-time dengan akumulasi per frame).
4. Getar tangan: jalur acak halus (dua frekuensi) pada yaw / pitch selama t, amplitudo dari aturan 1/fokus dan napas (`BOB`); tripod di panel = 0, juga mematikan gerak kepala.

**Kriteria selesai:** Copper malam, 4 s, tripod: jejak lampu mobil kontinu di boulevard; Z dipercepat + 30 s: awan bergerak; 1/4000 s: mobil tajam; tanpa tabrakan atau keadaan simulasi rusak setelah tangkap (uji lalu lintas lama tetap lulus).

## K6. Live view dan video (Medium, shader High)

1. `POSTKIT.DOF_FS` (di `shared/post.js`): CoC per piksel dari kedalaman + uniform lensa, gather 2 cincin (Ultra 3), pisah depan / belakang bidang fokus supaya tepi objek dekat tidak bocor. Copper memakai ini menggantikan `cocAt` hanya saat mode kamera (`cocAt` lama tetap untuk Foto bebas).
2. Blur kamera video: kecepatan layar dari kedalaman + matriks pandang-proyeksi frame sebelumnya, 8 sampel sepanjang vektor, panjang = sudut rana / 360 x durasi frame.
3. Perekam `CAMKIT.recorder` + audio dari simpul master; tombol rekam di HUD; hasil diunduh saat berhenti (`.mp4` / `.webm`).
4. Pembekuan `DYN`, turun preset otomatis, dan adaptasi drastis (adaptasi tetap halus seperti mata kamera video) selama merekam.

**Kriteria selesai:** klip 10 s di headless Chromium menghasilkan blob > 0 byte dengan trek video (dan audio bila `AudioContext` jalan); DOF live view mirip foto akumulasi pada lensa dan fokus yang sama (bentuk boleh beda, besar blur beda < 20%); FPS live view turun paling banyak 15% dibanding jendela (diukur pemilik).

## K7. Millar's World (Medium)

- Kait: `camFov()`, tap HDR di `postRender()` sebelum bloom, meter dari luminans (Millar belum punya meter: tambah reduksi mip HDR kecil 1 x 1 dibaca PBO asinkron seperti `AE` Gargantua), `stepWorld` = `simStep()`.
- Kedalaman `POST.hdr.depthTexture` dibuat di semua preset saat mode kamera dibuka (dibuang saat keluar bila bukan Ultra).
- Visor helm dan tubuh disembunyikan seperti mode foto lama; tampilan drone tetap boleh. Opsional nanti: tangan astronaut memegang kamera di tampilan drone (`armReach`).
- Uji `tools/uji_millar.py` (F = `PHOTO.on` + kelas `photo`) tetap lulus.

## K8. Gargantua (Medium)

- Ray tracer: sampel bukaan tidak berpengaruh untuk piringan dan bintang (praktis tak hingga, jauh di atas jarak hiperfokal); akumulasi tetap dipakai untuk anti alias dan bintang HDR yang lebih halus. Geser sub-piksel lewat `viewBasis()`.
- Wahana GX-01 dan kokpit: DOF dan patch rangefinder dari kedalaman `T.shipFb`.
- Meter = luminans dari `LUM_FS` (`AE`), di luar misi k = 1 tetap dijangkar ke `CONFIG.post.exposure`.
- Mode kamera hanya di luar misi atau saat jeda; Enter di mode kamera = rana (bukan `state.shot` lama).

## K9. Mekanis (Low)

Teks HUD, panel, bantuan, toast lewat `t()` (Copper, Millar) dan kamus `ID` / `txt()` (Gargantua); `tools/uji_bahasa.py` lulus; tabel F dan tombol lokal kamera di `docs/app/tombol.md`; baris `shared/camera.js` dan `tools/uji_kamera.py` di `CLAUDE.md`; fitur "Kamera rangefinder" di `FEATS` dan `KEYS` menu utama.

## File dan fungsi yang disentuh

| File | Perubahan |
| --- | --- |
| `shared/camera.js` (baru) | `window.CAMKIT` |
| `shared/post.js` | `DOF_FS`, `MBLUR_FS` (blur kamera) |
| `experiences/cooper-station/index.html` | `PHOTO` (kind, cam), `togglePhoto()`, handler `keydown` / `wheel` / `mousedown`, `compMat` (`uRf`, k, derau, DOF baru), `postEnd()` (tap akumulasi), `frame()` dipecah `advance()` / `render()`, `ADAPT` (beku), `AUDIO` (rana, rekam) |
| `experiences/millar/index.html` | `PHOTO`, `togglePhoto()`, `savePhoto()`, `postRender()`, `M_COMP`, `makePost()` (kedalaman), `DYN`, `VISOR`, `BODY` |
| `experiences/gargantua/index.html` | `togglePhoto()`, `state.shot`, `viewBasis()`, komposit post, `AE`, `drawShip()` |
| `tools/uji_kamera.py` (baru) | K1 Node; K2-K8 Chromium: masuk / keluar, patch, EV, derau, akumulasi tanpa NaN, rasio 3:2, perekam, uji lama tetap lulus |
| `docs/app/tombol.md`, `CLAUDE.md`, `index.html` | K9 |

## Pertanyaan terbuka untuk pemilik

| No | Pertanyaan | Usulan bawaan |
| --- | --- | --- |
| 1 | F langsung membuka kamera rangefinder, atau tetap Foto bebas dan kamera lewat panel? | F = kamera (jenis terakhir diingat), Foto bebas lewat panel |
| 2 | Simpan tiap foto langsung sebagai unduhan, atau kumpulkan di rol (36 frame) lalu ekspor? | Unduh langsung (seperti sekarang) + tinjau foto terakhir |
| 3 | Perlu tampilan badan kamera (tangan memegang kamera) saat keluar dari jendela bidik? | Tidak di tahap ini |
| 4 | Video "render" non real-time (kualitas akumulasi, tanpa suara) untuk sinematik? | Ditunda setelah K6 |

## Caveat dan batasan

- Kalibrasi eksposur relatif terhadap tampilan sekarang, bukan luminans fisik; angka EV meter (konstanta C) adalah pilihan desain dan perlu disetel pemilik setelah K3.
- Konstanta derau a0, b0, basis rangefinder 50 mm, dan pembesaran 0,72x adalah nilai awal, belum diukur di proyek ini.
- Waktu tangkap (sekitar 1 s untuk 32 subframe pada 30 fps) adalah perkiraan dari FPS, belum diukur di GTX 1060 dan M1.
- Format `MediaRecorder` berbeda per browser (Safari: mp4; Chrome: webm, mp4 di versi baru); sandbox SwiftShader tidak menampakkan NaN dan tidak mewakili FPS.
- Resolusi foto 1x terikat ukuran kanvas (1.620 x 1.080 pada layar 1080p); resolusi 2x berisiko memori di M1.
