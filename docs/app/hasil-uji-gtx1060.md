# Hasil uji GPU: GTX 1060 (Fase A2)

Per 15 November 2026. Sumber: `laporan.md` dari `tools/uji_gpu_lokal.py`, komputer "blackhole", Windows 10, GeForce GTX 1060 6GB lewat ANGLE Direct3D11. Ukuran 1920 x 1080 DPR 1, vsync dilepas, turun-preset otomatis dan resolusi adaptif Gargantua dimatikan. M1 belum diuji.

## Ringkasan

- **Gargantua (paling parah):** di Ultra dan Tinggi skala render 1,0 ada frame 2-19 s; pengambilan foto layar habis waktu 120 s; muat pertama 90,2 s.
- **Millar:** rata-rata 104-180 FPS, tetapi tersendat teratur: 25-33 frame > 50 ms per 10 s (maks 270-476 ms), padahal waktu GPU per frame hanya 4-7 ms. Petunjuk kuat masalah di CPU atau sinkronisasi, bukan beban GPU.
- **Copper kota:** 46-61 FPS di Ultra, p95 34-47 ms, 5-31 frame > 50 ms per 10 s. Pass scene 17-20 ms di New York, hujan, dan malam. Ultra dan Tinggi hampir sama di kota. Kamera luar dan kokpit lancar (95-203 FPS). Muat pertama 86,4 s.

## Data utama

| Experience | Titik | Preset | FPS | p95 (ms) | Frame > 50 ms / 10 s | Maks (ms) | GPU (ms) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Copper | C4 New York siang | Ultra / Tinggi | 47,9 / 49,7 | 38,9 / 54,5 | 11 / 31 | 69 / 82 | scene 20,0 / 19,4 |
| Copper | C7 hujan | Ultra / Tinggi | 46,5 / 49,3 | 43,2 / 35,0 | 10 / 12 | 139 / 145 | scene 18,7 / 16,0 |
| Copper | C8 malam | Ultra / Tinggi | 49,1 / 53,3 | 47,3 / 44,6 | 21 / 17 | 127 / 147 | scene 17,6 / 15,7 |
| Copper | C3 rumah Cooper | Ultra / Tinggi | 61,2 / 91,8 | 34,0 / 20,2 | 10 / 4 | 81 / 65 | scene 8,9 / 12,2 |
| Copper | C9 kamera luar | Ultra / Tinggi | 94,9 / 95,5 | 15,0 / 15,2 | 2 / 0 | 136 / 35 | scene 6,7 / 5,9 |
| Copper | C11 kokpit | Ultra / Tinggi | 140,7 / 203,1 | 12,4 / 7,2 | 0 / 0 | 34 / 9 | scene 5,2 / 3,3 |
| Millar | M2 berdiri di air | Ultra / Tinggi | 180,1 / 142,8 | 12,3 / 11,6 | 30 / 30 | 317 / 390 | total 6,0 / 6,8 |
| Millar | M4 terbang | Ultra / Tinggi | 104,2 / 139,3 | 19,5 / 14,4 | 28 / 30 | 476 / 448 | total 5,5 / 6,8 |
| Gargantua | G1 tampilan awal | Ultra / Tinggi | 66,5 / 0,4 | 1,8 / 15.114 | 2 / 2 | 8.188 / 15.114 | belum diukur |
| Gargantua | G2 Kelam | Ultra / Tinggi | 16,0 / 17,1 | 1,3 / 0,6 | 3 / 3 | 19.361 / 18.829 | belum diukur |
| Gargantua | G3 susur, kokpit | Ultra / Tinggi | 22,2 / 28,0 | 135,2 / 62,3 | 27 / 17 | 2.260 / 1.748 | belum diukur |

| Muat sampai Mulai | Pertama (Ultra) | Kedua (Tinggi) |
| --- | --- | --- |
| Copper | 86,4 s | 29,9 s |
| Copper Jupiter | 9,3 s | 10,7 s |
| Millar | 13,4 s | 1,1 s |
| Gargantua | 90,2 s | 16,8 s |

## Tafsiran (inferensi, perlu dibuktikan)

| # | Temuan | Dasar | Kemungkinan penyebab | Keyakinan |
| --- | --- | --- | --- | --- |
| T1 | Gargantua tersendat sampai belasan detik | maks 8-19 s; p50 0,3-0,4 ms (frame kosong menumpuk) | Shader `SCENE_FS` sangat berat di skala 1,0 (Tinggi dan Ultra: `aa` 4, langkah 320 / 500); dengan vsync dilepas, perintah GPU menumpuk lalu dibayar sekaligus. Resolusi adaptif yang biasanya menolong dimatikan skrip | Sedang: perlu uji ulang dengan `--vsync` dan resolusi adaptif menyala |
| T2 | Muat pertama Copper dan Gargantua sekitar 90 s | Kedua kali 17-30 s | Kompilasi HLSL (Direct3D11) shader besar saat cache shader Chrome masih kosong | Sedang |
| T3 | Millar tersendat sekitar 3 kali per detik | 25-33 frame > 50 ms per 10 s di semua titik, GPU < 7 ms | Kerja CPU berkala atau baca balik GPU yang menunggu. Kandidat: pembaruan cubemap langit / lensa (`SKYCUBE`, `GCUBE`), resolusi dinamis `DYN` membuat ulang target render, meter eksposur | Rendah: perlu profil Chrome |
| T4 | Copper kota 47-53 FPS | Scene 16-20 ms di C4 / C7 / C8 | Beban gambar kota padat: orang GLB (28), mobil dekat (26), tekstur dekat (32), pohon. Ultra dan Tinggi sama-sama render 1,0x karena DPR layar 1 | Sedang |
| T5 | Tidak ada bukti NaN | Titik putih 62-160 di dalam stasiun, 500-620 hanya di pandangan berbintang (kamera luar, kokpit Tinggi tanpa TAA) | Bintang dihitung sebagai titik terisolasi; Ultra (TAA) melembutkan bintang | Perlu lihat foto C9 / C11 Tinggi |
| T6 | Galat 404 satu kali per halaman, 1 ERR_CONNECTION_REFUSED di Copper | Konsol | Kemungkinan `favicon.ico` (halaman tanpa favicon); sumber koneksi ditolak belum diketahui | Rendah, tidak berdampak |

## Langkah berikutnya (A3 / A4)

| Langkah | Isi | Effort | Model | Thinking |
| --- | --- | --- | --- | --- |
| A2b | Uji ulang Gargantua dengan `--vsync` dan resolusi adaptif menyala (pilihan skrip baru `--adaptif`), plus waktu GPU Gargantua di laporan | Medium | Sonnet 5.5 | medium |
| A2c | Mode banding di skrip: C4 dengan `?orang=lama`, `?mobil=lama`, `?tekstur=lama`, `?pohon=lama`, `?v5=0` untuk mencari bagian termahal di pass scene Copper | Medium | Sonnet 5.5 | medium |
| A3a | Millar tersendat: profil CPU per frame (`performance.mark` di `frame()`), cari kerja berkala, perbaiki | High | Opus 5.5 | high |
| A3b | Gargantua: batasi beban per frame (anggaran waktu GPU, skala awal aman di GTX 1060), pertimbangkan `aa` 2 di Tinggi | High | Opus 5.5 | xhigh |
| A3c | Copper kota: optimasi bagian termahal dari A2c, hanya perubahan dengan hasil identik | High | Opus 5.5 | high |
| A3d | Muat pertama: ukur program terlama per experience dari `prof-*.json`, pertimbangkan pecah shader besar | High | Opus 5.5 | high |

## Keterbatasan

- Satu kali jalan per preset, 10 s per titik; variasi antar jalan belum diketahui.
- Vsync dilepas dan resolusi adaptif Gargantua mati: angka Gargantua adalah kasus terburuk, bukan pengalaman pemain biasa.
- Waktu GPU Copper dan Millar adalah rata-rata `GPUT`; Gargantua belum punya pengukur GPU.
- Foto dan `prof-*.json` belum dibaca (hanya `laporan.md` yang dikirim).
