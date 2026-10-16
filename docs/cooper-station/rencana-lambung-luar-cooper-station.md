# Rencana X1: lambung luar Copper berblok abu-putih

Revisi dari foto Bhakti: tampilan luar stasiun terlalu datar dan monoton. Sketsa disetujui: `sketsa-lambung-luar.svg`.

## Ringkasan

- Kulit luar kini blok bertingkat dominan putih, abu muda, abu tua, dicahayai Matahari sungguhan (sisi terang dan gelap, gerhana ikut padam).
- Relasi dalam-luar: kulit di balik kompleks utilitas (za 6.400-6.900, dekat rumah Cooper) menjadi zona industri abu tua dengan utilitas luar 3D.
- `?lambung=lama` = tampilan sebelum X1 persis. Hanya terlihat saat kamera luar / pesawat; tampilan dari dalam tidak berubah.

## Langkah

| Langkah | Isi | Status | Effort | Model | Thinking |
| --- | --- | --- | --- | --- | --- |
| X0 | Sketsa SVG, revisi tidak simetris, zona industri di balik utilitas | selesai | Low | Sonnet | low |
| X1a | `EXT_LIGHT` + `extShade()` + `extLightUpdate()` (Matahari x `ECL.k`, Saturnus, ambient bintang) | selesai | High | Opus | high |
| X1b | `hullMatX(mode)`: tipe segmen `HX.seg` (polos, padat, pita, modul, industri), zona makro, BSP, bevel, alur, ventilasi, palka, jendela, lampu navigasi lama | selesai | High | Opus | high |
| X1c | Utilitas luar 3D `HX.lists` (9.089 instans, 7 draw call), `extBoxMat()` dengan LOD ciut di vertex shader | selesai | Medium | Opus | high |
| X1d | Kerah end cap (kulit, muka, dalam), rel, rangka, sirip, crawler, cincin dermaga memakai material bercahaya. Struktur end cap, hub, batang dermaga (juga terlihat dari dalam) ditunda | sebagian | Medium | Sonnet | medium |
| X1e | `exteriorGroup` ikut dikompilasi di `warmShaders()` | selesai | Low | Sonnet | low |
| X1f | `?lambung=lama`, dokumen, CLAUDE.md | selesai | Low | Sonnet | low |

## Utilitas luar (X1c)

| Tempat | Isi | Fungsi |
| --- | --- | --- |
| Zona industri, 4 lajur di antara rangka za 6.500 dan lorong servis | ladang tangki di atas pelana (cincin ujung, pipa pengumpul), deret radiator panas, rumah pompa bertingkat dengan cerobong, palka udara + modul kru, tiang komunikasi + piringan | penyimpanan, buang panas, pemrosesan, akses kru, komunikasi |
| Lorong tengah za 6.650 | rak pipa keliling, dua pipa di 15 m melintas di atas rel, penyangga tiap 20 m | jalur air dan gas |
| Luar zona | modul kecil (kepadatan ikut tipe segmen), palka berlampu, pasangan tangki kecil, 12 tiang komunikasi | perawatan, akses |
| Tiap rangka melingkar | pod RCS 6 posisi keliling, nosel 4 arah, lampu kedip merah | kendali sikap |

Semua di bawah R_OUT + 29 m (batas tabrak pesawat). Instans lebih kecil dari sekitar 1,5 piksel diciutkan; detail shader lebih kecil dari piksel dipudarkan ke rata-ratanya.

## Uji (sandbox SwiftShader)

| Cek | Hasil |
| --- | --- |
| Muat tanpa error (preset Sedang), X1 dan `?lambung=lama` | tidak ada error |
| Kamera luar 6,5 km, utilitas 900 m, dekat 160 m, end cap A 2,6 km | tergambar, tanpa error |
| FPS GTX 1060 / M1, NaN di M1 | menunggu uji Bhakti |

## X2: cahaya bergeser di atap saat kamera luar (revisi Bhakti)

| Item | Isi |
| --- | --- |
| Gejala | Dari kamera luar, cahaya berpindah dari atap ke atap dalam barisan rapi, juga di lapangan baseball; dari dalam tidak ada |
| Penyebab | Kamera luar memutar scene (`scene.rotation.z = omega t`), jadi posisi dunia di shader ikut berputar, tetapi fungsi cahaya menghitung lokasi kerangka stasiun dari posisi itu (s = atan x R): kolam lampu jalan dan trem, peta daratan dan awan untuk pantulan, peta bayangan sunline tetap diam sementara kota berputar di bawahnya |
| Perbaikan | `uL_Rot` + `stF()` di `LIGHT_GLSL`: `stationLight()`, `nightLight()`, `farEnv()`, `sunShCover()` memutar balik masukan ke kerangka stasiun; `uL_SunDir` selalu kerangka stasiun. Di dalam stasiun `uL_Rot` = (1, 0), hasil identik |
| Uji (sandbox) | Render dua kali dengan stasiun dan kamera diputar bersama (0,3 dan 1,25 rad, Matahari dimatikan agar hanya efek kerangka yang diukur): siang beda rata-rata per piksel 1,58 -> 0,05; malam 3,15 -> 1,41 (sisa tersebar merata = aliasing titik lampu kecil, gugus kolam lampu hilang); tanpa error |
| Tetap | Kilau Matahari langsung lewat kaca end cap B tetap ada (efek fisika nyata, arah Matahari inersia) |
