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

## Tambahan dari data `?prof=1` (15 November 2026)

| # | Temuan | Data | Arti |
| --- | --- | --- | --- |
| P1 | Copper muat pertama: 76 s di kompilasi shader | "Menyiapkan shader" 10,1 s -> "Pemanasan GPU" 37,6 s -> "Siap" 86,1 s; satu long task 35,6 s + 12,9 s di pemanasan. Jalan berikutnya (cache shader Chrome terisi): 7,4 s -> 9,2 s | Kompilasi HLSL Direct3D11 sekali per mesin (diulang bila Chrome / driver diperbarui). Selama pemanasan halaman membeku 35 s tanpa bar bergerak |
| P2 | Copper tombol Q: 118 program baru, halaman membeku 67 s | Tekan Q kedua (Tinggi -> Sedang): `programs` 118, long task 67.192 ms. Dengan cache terisi (putaran Jupiter): 117 program, 224 ms | `warmLater()` hanya memanaskan varian efek layar P, bukan varian preset Sedang / Rendah / Hemat (vegetasi, post). Pemain yang pertama kali menurunkan preset membeku lama |
| P3 | Gargantua muat pertama 88 s | 14 program, "Kompilasi program" 1,0 s -> "Siap" 89,4 s; menunggu program hanya 129 ms (kompilasi paralel, halaman tidak membeku) | Satu shader besar (`SCENE_FS`) dikompilasi HLSL sekitar 88 s saat cache kosong; kedua kali sekitar 15 s |
| P4 | Millar: 22 program baru tepat setelah Mulai, membeku 8,7 s | `main` 22 program, menunggu 8.727 ms, long task 8.761 ms di 13,8 s | Skrip memilih Ultra di kartu mulai, bawaan Millar Tinggi; pemanasan muat hanya untuk preset bawaan. Pemain yang memilih Ultra di kartu juga kena |
| P5 | Millar dan Gargantua "tersendat" kemungkinan besar efek uji tanpa vsync | Millar: interval rAF p50 2,2 ms (450 fps) padahal GPU sekitar 6 ms per frame; long task 100-980 ms terus-menerus. Gargantua: p50 0,4 ms, long task 1-96 s | Tanpa vsync, JavaScript mengirim frame lebih cepat dari yang bisa diselesaikan GPU; antrean penuh lalu halaman menunggu. Tafsiran T1 dan T3 di atas belum boleh dipakai sebelum uji ulang dengan vsync |

Koreksi: tafsiran T1 (Gargantua) dan T3 (Millar) di atas kemungkinan besar keliru penyebabnya. Skrip kini memakai vsync sebagai bawaan (`--tanpa-vsync` untuk cara lama) dan punya `--adaptif` (resolusi adaptif Gargantua menyala, seperti pemain biasa; skala render dicatat per titik).

Perbaikan yang sudah jelas tanpa uji ulang (A3):

| Langkah | Isi | Effort | Model | Thinking |
| --- | --- | --- | --- | --- |
| A3-Q | Dikerjakan 15 November 2026 (lihat bawah). Copper: panaskan varian preset lain di latar belakang (lanjutan `warmLater()`), dan bar muat bergerak selama pemanasan GPU (pecah `warmFrame()`) | High | Opus 5.5 | high |
| A3-M | Dikerjakan 15 November 2026 (lihat bawah). Millar: panaskan preset yang dipilih di kartu mulai sebelum Mulai aktif (`warmPresets(force)` untuk preset itu) | Medium | Sonnet 5.5 | medium |
| A3-G | Gargantua: selidiki waktu kompilasi HLSL `SCENE_FS` (loop yang dibuka penuh oleh kompiler, jumlah sampel AA / debu sebagai konstanta) | High | Opus 5.5 | xhigh |

### A3-Q dan A3-M: yang dikerjakan

| Langkah | Perubahan | Akibat yang diharapkan | Efek samping |
| --- | --- | --- | --- |
| A3-Q a | Copper mode efek layar Mati (P, juga preset Rendah dan Hemat) kini menggambar scene ke target HDR yang sama lalu disalin ke kanvas (`postCopy()`), bukan langsung ke kanvas | Ganti preset / P / turun otomatis tidak lagi mengompilasi sekitar 117 program (dulu beku 67 s di GTX 1060 saat cache kosong); `warmNext()` dihapus | Mode Mati: satu pass salin layar penuh tambahan dan target half float (Rendah / Hemat sedikit lebih berat, perkiraan < 1 ms, belum diukur); objek tembus pandang dicampur di ruang linear seperti mode efek layar lain (sedikit berbeda dari dulu di mode Mati) |
| A3-Q b | `warmShaders()` menunggu kompilasi sampai 4 menit (dulu 20 s) dengan label "Menyiapkan shader N% (pertama kali di komputer ini bisa 1-2 menit)" | Bar muat bergerak selama kompilasi pertama; pemanasan GPU tidak lagi membeku 35 s | Tidak ada di kunjungan berikutnya (cache terisi) |
| A3-M | Millar: memilih preset lain di kartu mulai mengulang pemanasan muat untuk preset itu (bar muat tampil, Mulai menunggu) | Tidak ada lagi beku 8,7 s tepat setelah Mulai | Menunggu beberapa detik di kartu mulai saat preset diganti (pertama kali di komputer: lebih lama) |

## Uji ulang dengan vsync dan resolusi adaptif (15 November 2026, sebelum A3-Q / A3-M)

`tools\uji_gpu_lokal.bat --exp millar,gargantua --adaptif`, vsync menyala (layar sekitar 144 Hz menurut interval frame 6,9 ms).

| Experience | Titik | Preset | FPS | p50 / p95 (ms) | Frame > 50 ms / 10 s | Catatan |
| --- | --- | --- | --- | --- | --- | --- |
| Millar | M2, M2j, M4 | Tinggi | 139-141 | 6,9 / 7,1-7,2 | 0 | Lancar. GPU 6-7 ms per frame |
| Millar | M2, M2j, M4 | Ultra | 1,0 | 1.007 / 1.007 | 10 | Tidak sah: frame tepat 1 s = Chrome memperlambat jendela yang tidak aktif. Log tombol berisi AltLeft / MetaLeft di 17 s (jendela ditinggalkan). GPU tetap 10-13 ms |
| Millar | Mulai di Ultra | Ultra | - | - | - | 22 program baru, beku 7,4 s setelah Mulai (masalah A3-M, sudah diperbaiki sesudah uji ini) |
| Gargantua | G1 / G2 | Ultra, Tinggi | 35-43 | 21-28 / 35-42 | 0-8 | Skala adaptif turun ke 0,4-0,8 dan bertahan di 30-55 FPS |
| Gargantua | G3 misi, kokpit | Ultra, Tinggi | 37-40 | 7,2 / 90-97 | 71 | Frame cepat dan lambat bergantian; long task CPU 50-160 ms sekitar tiap 130 ms selama misi |
| Gargantua | G3c misi, kamera luar | Ultra, Tinggi | 34-40 | 21 / 49-55 | 19-20 | Sama, lebih ringan |

Kesimpulan:

- T3 (Millar tersendat) terbukti efek uji tanpa vsync: dengan vsync Millar Tinggi 140 FPS tanpa satu pun frame > 50 ms.
- T1 (Gargantua beku belasan detik) juga efek uji (vsync dilepas, resolusi adaptif mati). Dengan pengaturan pemain biasa Gargantua 34-43 FPS di GTX 1060, skala render 0,4-0,9.
- Masalah nyata baru: **misi Gargantua tersendat karena kerja CPU** (71 frame > 50 ms per 10 s di kokpit). Kandidat (belum dibuktikan): `misPredict()` (sampai 400 langkah x 300 sub-langkah RK4 tiap 0,4 s), gambar 5 layar MFD di kanvas 2D (`drawMFD()`, kanvas `willReadFrequently` = render CPU) lalu `texSubImage2D`, jendela relai dan peta corong.

| Langkah | Isi | Effort | Model | Thinking |
| --- | --- | --- | --- | --- |
| A3-G2 | Profil CPU misi Gargantua (`performance.mark` di `stepMission`, `misPredict`, `drawMFD`, `drawRelay`, `drawFunnel`), lalu pecah kerja terberat ke beberapa frame atau kurangi frekuensinya; hasil fisika tetap sama | High | Opus 5.5 | high |
| A2d | Uji ulang Millar Ultra tanpa meninggalkan jendela, setelah A3-M | - (pemilik) | - | - |

## Keterbatasan

- Satu kali jalan per preset, 10 s per titik; variasi antar jalan belum diketahui.
- Vsync dilepas dan resolusi adaptif Gargantua mati: angka Gargantua adalah kasus terburuk, bukan pengalaman pemain biasa.
- Waktu GPU Copper dan Millar adalah rata-rata `GPUT`; Gargantua belum punya pengukur GPU.
- Foto dan `prof-*.json` belum dibaca (hanya `laporan.md` yang dikirim).
