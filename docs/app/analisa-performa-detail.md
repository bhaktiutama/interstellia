# Analisa performa halaman detail (Copper, Gargantua, Millar)

## Ringkasan

- Detail Gargantua terasa lambat karena tiga hal: kanvas hero berukuran 1120² px yang diblur penuh tiap frame, piringan dengan ~1.050 `shadowBlur` per frame, dan simulasi yang tetap menggambar walau panelnya di luar layar. Ketiganya sudah diperbaiki.
- Hasil di sandbox: hero Gargantua naik dari 17 ke 61 fps (desktop) dan dari 9 ke 42 fps (ponsel lambat); piringan naik dari 14 ke 54 fps. Muat Gargantua turun dari 1.480 ms ke 399 ms, dengan tugas terpanjang turun dari 682 ms ke 128 ms.
- Tidak ada fitur, animasi, kontrol, atau angka yang berubah. Simulasi tetap berjalan walau panelnya di luar layar, dan semua uji detail lulus.

## Cara mengukur

Alat ukurnya `node tools/ukur_detail.cjs [gargantua millar cooper-station]` (Chromium sandbox tanpa GPU), dengan tiga konfigurasi:

| Konfigurasi | Isi |
| --- | --- |
| Desktop | 1440 x 900, DPR 2 |
| Ponsel lambat | 390 x 844, DPR 3, CPU 4x lebih lambat |
| Simulasi berjalan | Desktop, CPU 4x lebih lambat; tombol Jalankan ditekan satu per satu, lalu halaman digulir ke galeri |

Batasan pengukuran:
- Sandbox tidak punya GPU, jadi raster kanvas dikerjakan CPU. Angka absolut lebih pesimis dari PC atau Mac asli, tetapi perbandingan sebelum / sesudah tetap berlaku.
- Selisih +-3 fps antar-run adalah derau.
- Penyebab tiap masalah dipastikan dengan uji A/B: satu efek dimatikan, lalu fps diukur ulang.

## Penyebab yang ditemukan

| Masalah | Bukti A/B | Halaman |
| --- | --- | --- |
| Kanvas hero 1120² px (DPR 2) untuk gambar sumber 300² px | DPR 1: 18 -> 44 fps | Gargantua |
| `filter: blur(6px)` resolusi penuh tiap frame | Tanpa blur: 18 -> 25 fps | Gargantua |
| `shadowBlur` 18 px pada ~1.050 sel piringan tiap frame | Tanpa shadow: 15 -> 41 fps | Gargantua |
| Garis tepi 0,7 px pada 2.112 sel (penutup celah) | Tanpa garis: 34 -> 61 fps | Gargantua |
| Pemutar menggambar ulang kanvas tiap frame walau di luar layar | Semua simulasi berjalan, semua panel di luar layar: 9 fps | Gargantua, Millar |
| `seenR()` (bisection 60 langkah) dipanggil ~800x per frame untuk kurva | Gambar bab jatuh 16 ms (CPU 4x) | Gargantua |
| `fmt()` memakai `toLocaleString`, yang membuat formatter baru tiap panggilan | ~25x lebih lambat dari formatter yang disimpan | Ketiganya |
| Readout angka diperbarui tiap frame walau di luar layar | Tanpa pembaruan: 45 -> 61 fps | Millar, Gargantua |
| `shadowBlur` pada cincin dan lintasan panjang (area blur selebar kanvas) | Tanpa shadow: Coriolis 15 -> 51 fps | Ketiganya |
| Saat muat, semua panel digambar, termasuk yang di luar layar | Bagian dari tugas panjang 682 ms | Ketiganya |
| Coriolis selesai tetap digambar ulang tiap frame | Gambar diam | Copper |

Yang diukur tetapi tidak berarti (tidak diubah): bintang latar `bgStars` (0,2 ms), `backdrop-filter` header, dan `mask-image` hero.

## Perubahan

| No | Perubahan | Halaman |
| --- | --- | --- |
| P1 | `panel().req()`: gambar hanya bila terlihat; di luar layar ditandai lalu digambar sekali saat masuk layar (juga saat muat) | Ketiganya |
| P1 | Resolusi adaptif `Q`: bila frame > 22 ms selama 1,5 s saat ada animasi, skala backing kanvas turun 1 -> 0,8 -> 0,65 (DPR efektif tidak di bawah 1); naik lagi bila < 14 ms selama 4 s. Di perangkat cepat tidak berubah | Ketiganya |
| P1 | `player()`: angka dan gambar bagian yang tidak terlihat ditunda, lalu disusulkan saat bagian itu masuk layar | Gargantua, Millar |
| P1 | `fmt()` / `fmtE()` memakai `Intl.NumberFormat` yang disimpan per bahasa dan digit | Ketiganya |
| P2 | Hero (lihat rincian di bawah) | Gargantua |
| P3 | Piringan (lihat rincian di bawah) | Gargantua |
| P4 | `haloStroke()` menggantikan `shadowBlur` untuk cincin dan lintasan panjang: tiga garis lebar tembus pandang di bawah garis asli, dengan profil setara Gauss. Titik dan bentuk kecil tetap memakai glow lama karena murah | Ketiganya |
| P5 | Kurva yang dilihat relai dari tabel `seenR()` 401 titik (galat maks 1,8e-4 rs). Titik dan angka tetap memakai `seenR()` persis | Gargantua |
| - | `cStep()` tidak lagi menggambar ulang simulasi Coriolis yang sudah selesai | Copper |

Rincian P2, hero Gargantua:
- Backing kanvas DPR 1, label pindah ke HTML agar tetap tajam.
- Blur dikerjakan di kanvas setengah resolusi.
- Konstanta per piksel dihitung sekali; gamma memakai LUT.
- Frame pertama memakai resolusi peta 130, lalu resolusi penuh menyusul setelah 0,7 s.

Rincian P3, piringan Gargantua:
- Geometri sel di-cache per ukuran, kemiringan, dan mode.
- Glow dibuat sekali dari kanvas setengah resolusi.
- Sel dilebarkan 0,35 px sebagai ganti garis tepi.
- String warna di-cache.

## Hasil (fps, 60 = lancar; sebelum -> sesudah)

### Gargantua

| Kanvas | Desktop | Ponsel lambat |
| --- | --- | --- |
| Hero | 17 -> 61 | 9 -> 42 |
| Anatomi | 59 -> 61 | 44 -> 61 |
| Piringan | 14 -> 54 | 5 -> 37 |
| Aberasi | 61 -> 61 | 33 -> 46 |
| Lainnya | 61 -> 61 | 61 -> 61 |

| Simulasi berjalan (desktop CPU 4x) | Sebelum | Sesudah |
| --- | --- | --- |
| Sinar | 29 | 36 |
| + jatuh | 19 | 49 |
| + relai | 14 | 58 |
| + orbit | 11 | 34 |
| Semua di luar layar | 9 | 61 |

| Muat | Sebelum | Sesudah |
| --- | --- | --- |
| Siap | 1.480 ms | 399 ms |
| Tugas terpanjang | 682 ms | 128 ms |
| Total tugas panjang | 2.751 ms | 357 ms |

### Millar
Semua kanvas sudah 60 fps sebelum dan sesudah. Muat 207 -> 138 ms.

| Simulasi berjalan (desktop CPU 4x) | Sebelum | Sesudah |
| --- | --- | --- |
| Dua jam | 16 | 37 |
| + cakrawala | 13 | 60 |
| + gelombang | 15 | 31 |
| + orbit | 11 | 44 |
| + putaran | 8 | 45 |
| Semua di luar layar | 9 | 61 |

### Copper

| Kanvas | Desktop | Ponsel lambat |
| --- | --- | --- |
| Hero | 61 -> 61 | 40 -> 61 |
| Air mancur | 58 -> 57 | 33 -> 39 |
| Hujan | 61 -> 61 | 32 -> 53 |
| Lainnya | 61 -> 61 | 61 -> 61 |

| Simulasi berjalan (desktop CPU 4x) | Sebelum | Sesudah |
| --- | --- | --- |
| Coriolis | 10 | 59 |
| + orbit | 23 | 33 |

## Perbedaan visual (dicek dengan tangkapan layar berdampingan)

- **Hero Gargantua:** setara. Glow lembut berasal dari blur setengah resolusi, dan label tetap tajam.
- **Piringan Gargantua:**
  - Mode film: selisih maksimal 17 tingkat warna di 0,7% piksel, pada waktu animasi yang sama.
  - Mode fisika: identik, dengan selisih maksimal 2 tingkat.
  - Garis cincin tipis di belahan jauh versi lama ikut hilang. Garis itu efek samping shadow per baris sel; warnanya ditiru dengan glow kedua (`DK.tint` 0,6).
- **Glow garis (`haloStroke`):** halo setara di cincin stasiun, lintasan Coriolis, air mancur, jam Millar, orbit, sinar, dan cincin aberasi.

## Yang masih bisa ditingkatkan (belum dikerjakan)

- **Air mancur Copper dan aberasi Gargantua di ponsel lambat** (39-46 fps): biayanya murni raster DPR 3. Resolusi adaptif `Q` akan turun sendiri setelah sekitar 1,5 s; jendela ukur alat ini lebih pendek.
- **Simulasi sinar dan orbit Gargantua, serta gelombang Millar, saat berjalan** (31-36 fps desktop CPU 4x): juga sebagian besar raster. Perlu dilihat di perangkat asli dulu.
- **Uji rasa lancar di GTX 1060 dan M1** oleh Bhakti: sandbox tidak punya GPU.

## Uji

- `tools/uji_detail_gargantua.cjs`, `uji_detail_millar.cjs`, dan `uji_detail_copper.cjs` lulus semua.
- Cek baru di ketiga uji:
  - Panel di luar layar tidak digambar saat simulasinya berjalan, lalu langsung tergambar saat digulir masuk.
  - Resolusi adaptif turun lalu pulih (cek DPR 2: 2x -> 1,3x -> 2x).
  - Hero Gargantua tanpa blur resolusi penuh dengan DPR 1, dan piringan tanpa `shadowBlur`.
