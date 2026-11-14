# CLAUDE.md - Aplikasi multi-experience (nama: Interstellia)

Kumpulan experience 3D bertema perjalanan antarbintang, dipanggil dari menu utama (`index.html`). Proyek penggemar, tidak berafiliasi dengan studio film mana pun. Pemilik proyek: Bhakti; diuji di PC GTX 1060 dan MacBook M1.

## Struktur repo (ringkas)

| Path | Isi |
| --- | --- |
| `index.html` | Menu utama infografis (konstanta `APP`, `EXPERIENCES`, `TXT`; foto `experiences/<id>/menu.webp`) |
| `experiences/cooper-station/` | Copper Corn Station: silinder O'Neill di orbit Saturnus / Jupiter (`index.html` satu file besar, `detail.html`, `assets/`) |
| `experiences/gargantua/` | Lubang hitam berputar, WebGL mandiri, misi wahana GX-01 (`index.html`, `detail.html`, `assets/`) |
| `experiences/millar/` | Millar's World: planet air, gelombang raksasa, misi radar, shuttle (`index.html`, `detail.html`, `prototipe.html`) |
| `shared/` | Modul bersama skrip biasa (`window.*`): `ui.css` / `ui.js`, `kestrel.js`, `petrel.js`, `armada.js`, `camera.js`, `vr.js`, `post.js`, `warm.js`, `prof.js`, `music.js`, `orang_data.js`, `wahana/`, `musik/` |
| `tools/` | Skrip olah aset (`siapkan_*`), uji (`uji_*`, Playwright + SwiftShader, `THREE_LOCAL` / `CHROMIUM` opsional), ukur (`ukur_*`) |
| `docs/app/`, `docs/<id>/` | Konsep, rencana (`rencana-*.md`), analisa, bahan halaman detail |

## Peta kode (baca yang relevan sebelum mengedit)

| Berkas | Isi |
| --- | --- |
| `docs/cooper-station/peta-kode.md` | Copper: berkas, aset, alat uji, peta nama fungsi / objek per area (cari dengan nama) |
| `docs/cooper-station/riwayat-tahap.md` | Copper: riwayat tahap 1-32, V1-V5, X1-X4, tur v2.x, K, 28-31 |
| `docs/gargantua/peta-kode.md` | Gargantua: `index.html` (misi G1-G9, kokpit K1-K7, MK, AA1), `detail.html`, alat uji |
| `docs/millar/peta-kode.md` | Millar: `index.html` (R1-R5, M3-M6, V4-V5, P2 / P4), `detail.html`, alat uji |
| `docs/app/peta-repo.md` | Menu utama, `shared/*`, dokumen aplikasi, alat bersama (wahana, performa, VR, UI) |
| `docs/app/tombol.md` | Standar tombol ketiga experience |

Aturan: fitur baru dicatat di peta kode experience-nya (dan riwayat tahap untuk Copper), bukan di `CLAUDE.md`. `CLAUDE.md` hanya berisi aturan dan ringkasan yang berlaku untuk setiap tugas.

## Aturan aplikasi

- Menambah experience: buat `experiences/<id>/index.html` + `preview.jpg`, lalu tambahkan entri di `EXPERIENCES` (ready: true) dan bagian infografisnya di `index.html` (section, `SPOTS`, `STATS`, `FEATS`, `KEYS`, foto `menu.webp`). Tiap experience wajib punya tautan kembali ke `../../index.html`.
- Tiap experience tetap halaman terpisah (memori GPU bersih saat pindah). Kode bersama dipindah ke `shared/` bertahap, jangan membongkar Copper Corn Station sekaligus.
- Status dan urutan kerja berikutnya: `docs/app/review-kode-dan-fase-berikutnya.md` (Fase A uji dan stabilisasi, B rapikan fondasi, C pengalaman pemain seragam, D konten baru: Penerbangan Kestrel). Rencana per experience di `docs/<id>/rencana-*.md` (Millar M5 / M6, Gargantua misi G1-G9 dan kokpit K1-K7, Copper tahap). Usulan nama: `docs/app/penamaan.md`.
- Tombol seragam di semua experience dengan Copper Corn Station sebagai patokan (Q grafik, P efek layar, U suara, N cuaca/suasana, Z waktu, V tampilan, F foto, R kembali, H sembunyikan, ` panel, ? bantuan): `docs/app/tombol.md`. Tombol khusus Copper (B, G, E, M, L, T, I, C, ...) tidak dipakai untuk fungsi umum lain.
- Rencana misi Gargantua (wahana GX-01 dari blokout v3 jatuh ke lubang hitam, terbang rendah di atas piringan, partikel menabrak kaca, informasi tidak bisa keluar dari horizon, sudut masuk tesseract fiksi; tahap G1-G6): `docs/gargantua/rencana-misi-lubang-hitam.md`. Rencana kokpit GX-01 lebih detail dan menoleh dengan mouse (K1-K7 dikerjakan, K2-K7 menunggu uji pemilik): `docs/gargantua/rencana-kokpit-gx01.md`.
- Jangan memakai judul film, logo, huruf judul, musik, cuplikan, atau desain kendaraan film.
- Bahasa aplikasi: Indonesia dan English (Jepang dan Mandarin ditunda). Semua halaman berbagi pilihan lewat localStorage `lazarus.lang` dan `?lang=id|en`, dan tautan antarhalaman meneruskan `?lang=`. Menu utama: teks di `APP`, `EXPERIENCES` (field `en`) dan `TXT`. Gargantua: sumber English, kamus `ID`, fungsi `txt()`.

## Pengelompokan task berdasarkan effort

Tiap task di rencana (`docs/<id>/`) diberi label effort di awal rencana. Label menentukan seberapa dalam analisis dan model mana yang dipakai. Saran model di bawah adalah rekomendasi awal (belum diukur di proyek ini); naikkan satu tingkat bila hasil pertama salah, turunkan bila sering berlebihan.

| Effort | Dipakai bila | Contoh Three.js umum | Contoh di proyek ini | Saran model | Saran thinking |
| --- | --- | --- | --- | --- | --- |
| Low | Tugas jelas, lokal, mudah diverifikasi secara visual | Ganti warna material atau tekstur, atur FOV kamera, tambah lampu, ganti nama atau ekstrak fungsi, ubah UI/HUD, tambah handler resize, tulis boilerplate (scene, renderer, loop) | Tambah entri `I18N.en`, ubah teks HUD atau label panel, atur `CONFIG.fov`, ubah warna bangunan, tambah entri `EXPERIENCES` | Haiku 4.5 (paling hemat); Sonnet 5.5 bila menyentuh banyak file | low |
| Medium | Menyentuh beberapa bagian kode atau butuh sedikit desain | Fitur baru (kontrol first-person, tabrakan kapsul sederhana, sprite atau partikel), muat glTF dengan animation mixer, post-processing, refactor ke modul, bayangan dasar atau kabut | Fasilitas atau distrik baru, perabot kota baru, preset grafis, suara baru, panel dan tombol baru, memindahkan kode ke `shared/`, skrip `tools/uji_*.py` baru | Sonnet 5.5 (default harian) | medium |
| High | Kebenaran bergantung pada penalaran halus, atau desain sulit diubah nanti | Arsitektur keseluruhan (ECS vs scene-graph, loop langkah tetap), integrasi fisika (Rapier/cannon-es), shader GLSL kustom, kerangka acuan berputar, instancing atau LOD untuk scene besar, kebocoran memori dan profiling performa GPU, bug sulit (jitter, z-fighting, tunneling, drift numerik) | Fisika kerangka berputar (Coriolis, bola, motor, jatuh dari dek), shader cahaya `LIGHT_GLSL`, peta bayangan koordinat silinder terbuka (`shUnroll`), pemilihan bayangan `SHP`, LOD pohon dan impostor, NaN di Apple M1, optimasi draw call dan waktu muat | Opus 5.5; Fable 5.1 hanya untuk bug yang tetap gagal setelah dua percobaan Opus | high; xhigh untuk shader yang rawan NaN di M1, relativitas, atau kerangka berputar |

Aturan pemakaian:

- Pecah task High menjadi langkah kecil: bagian desain dan penalaran dikerjakan model High, bagian mekanis (ganti nama, teks UI, entri kamus) diserahkan ke Low.
- Task yang menyentuh `LIGHT_GLSL`, `shUnroll`, kerangka berputar (scene.rotation.z), atau `groundH` / `TER` otomatis High, sebab salah kecil baru terlihat di GPU lain (GTX 1060 dan M1) dan sandbox SwiftShader tidak menampakkannya.
- Rencana (plan) disusun oleh model satu tingkat di atas effort task terberat di dalamnya; eksekusi per langkah memakai model sesuai label langkah.
- Label effort ditulis di tabel rencana tahap (kolom `Effort`, `Model`, `Thinking`), bersama perkiraan file dan fungsi yang disentuh. Thinking = tingkat effort Claude Code (`/effort low`, `medium`, `high`, `xhigh`); rekomendasi awal, naikkan satu tingkat bila hasil pertama salah.

# Experience: Copper Corn Station

Simulasi silinder O'Neill yang mengorbit Saturnus. Satu file HTML (`experiences/cooper-station/index.html`), three.js, bisa dijelajahi berjalan kaki. Dibangun bertahap.

## Aturan kerja

- Bahasa: Indonesia untuk komentar kode, dokumen, dan balasan. Teks UI ditulis dalam bahasa Indonesia sebagai sumber, lalu diterjemahkan lewat kamus `I18N` (M3). Teks UI baru wajib lewat `t('...')` (atau label `uiLabel`) dan diberi entri di `I18N.en`; `tools/uji_bahasa.py` memeriksa kelengkapannya.
- Satu file: semua kode Copper Corn Station ada di `experiences/cooper-station/index.html` (CSS + JS modul). Tidak ada build step, tidak ada addon three.js (GLTFLoader juga tidak: model dari luar diolah dulu dengan skrip di `tools/`). Aset data di `experiences/cooper-station/assets/` dimuat lewat `<script>` biasa (base64) agar jalan dari file://; aset pihak ketiga wajib dicantumkan di `assets/KREDIT.md` dan tab Tentang.
- three.js 0.186.1 dari importmap `https://cdn.jsdelivr.net/npm/three@0.186.1/build/three.module.js`.
- "Pertahankan yang ada": fitur lama tidak boleh hilang atau berubah tanpa diminta.
- Uji: pemilik proyek yang menguji visual dan FPS. Cukup cek halaman termuat tanpa error (lihat `tools/`). Jangan menghabiskan waktu dengan screenshot berulang.
- Hak cipta: jangan meniru desain kendaraan/musik film (Endurance, Ranger, musik Interstellar). Desain pesawat orisinal (shuttle "Kestrel" KS-07).
- Dokumen rencana ditulis sebagai file .md di `docs/<id>/` (pemilik membaca di ponsel).
- Format laporan: ringkasan dulu, tabel, tanpa em dash.

## Angka dasar

| Item | Nilai |
| --- | --- |
| Radius R | 1.000 m |
| Panjang L | 8.000 m (HALF_L 4.000) |
| Putaran | omega 0,09905 rad/s, periode 63,4 s, 1 g di tanah, kecepatan tepi 99,05 m/s |
| Koordinat | sumbu = world Z; za = z + 4.000 (jarak dari end cap A); s = theta x R (busur keliling) |
| Kerangka | dalam stasiun = kerangka berputar; kamera luar (V) dan pesawat = kerangka inersia (scene.rotation.z = omega t) |
| Orbit (17a) | radius 260.000 km, periode 37,57 jam; sumbu 65 derajat dari normal orbit; Matahari di bidang orbit, 25 derajat dari sumbu +z (masuk lewat end cap B); gerhana 2,78 jam per orbit |
| Dua scene | farScene (1 unit = 1.000 km: Saturnus, bintang, Matahari) + scene utama |

## Status pemain (`player.state`)

`ground` (`player.deck` true = di dek pandang menara; `MOTO.on` true = naik motor, fisika `stepMoto`), `air`, `lift`, `float` (hub nol-g), `tram`, `pod` (kapsul terowongan ke dermaga), `ship` (di shuttle; `ext.active` dan `ext.flight` true), `tour` (tur sinematik, pemain dibekukan). `PORT.trip` true = sedang perjalanan otomatis dari gerbang B1 (lift dan kapsul 5x, E = langsung ke kokpit).

## Tombol

W A S D, Shift, Space, B, G, L, T, E, M, V, [ ], Z (kecepatan waktu), N (cuaca), O, X, R, H, 0-9 (lokasi; 8 = kokpit shuttle, 9 = air mancur Coriolis, 0 = hutan lebat), K, Q, P, U, J, F (mode foto, Enter simpan PNG), Y (tur sinematik), I (lompat ke gerhana Saturnus), C (naik / turun motor), ` (panel kontrol), / atau F1. Di pesawat: W/S gas (bertahan), A/D guling, Z/C geser samping, R/F naik-turun, panah hidung / rudder, mouse melihat, Shift boost, X rem, V, E, L. Jalan kaki: lari bawaan, tahan Shift = jalan pelan, X turbo (debug). Di motor: W gas, S rem / mundur, A/D belok, Shift sport, Space klakson, O gas terus, mouse menoleh, C atau E turun (di bawah 10 km/h).

Catatan muat (M1): modul memakai `await bootStep(...)` di tingkat atas di antara bagian besar. P-A2 (analisa performa three.js / WebGPU): `orang.data.js` dan `rumput.data.js` tidak lagi `<script src>` yang memblokir modul, tetapi dimuat async oleh skrip kecil di `index.html` (`window.__dataP.orang` / `.rumput`, resolve juga saat gagal) dan ditunggu dengan `await` tepat sebelum dipakai (`FLUFFLAMA`, `PEDS.newModel`): data baru bisa dipakai hanya setelah `await window.__dataP.<nama>`; `fsQuad` pass layar penuh = satu segitiga (uv 0 / 2), jangan diganti kuad; `fluffAtlas()` memakai kanvas `willReadFrequently`; Copper dan Millar punya `preconnect` + `modulepreload` untuk three.js di `<head>`. P1: material layar penuh baru wajib dibuat lewat `fsMat()` (masuk `FS_MATS`, dikompilasi saat muat); pass akhir ke kanvas ditambahkan ke `FS_TO_CANVAS`; objek yang digambar dengan target lain atau override material ikut `warmFrame()`. Cek dengan `tools/ukur_muat.py cooper-station --cek` (0 program baru di frame pertama dan saat tombol). Bagian baru ditambah di tingkat atas modul (bukan di dalam fungsi) dan diberi titik jeda bila berat; `window.__stationReady` baru true setelah shader dikompilasi.

Catatan GPU: geometri buatan sendiri yang memakai material dasar (dicahayai `patchLit`) wajib punya atribut normal (`computeVertexNormals()`); shader cahaya kini juga dijaga. Di shader jangan `normalize()` vektor yang bisa nol, jangan `pow()` bilangan yang bisa negatif, jangan `sqrt()`/`asin()` di luar rentang (NaN di Apple M1 disebar bloom jadi titik putih berkedip). Sandbox uji (SwiftShader) tidak memperlihatkan NaN.
