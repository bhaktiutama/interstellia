# Daftar uji GPU (Fase A1)

Per 14 November 2026. Satu halaman untuk menguji semua fitur yang masih berstatus "menunggu uji" di 22 dokumen rencana. Diuji Bhakti di **PC GTX 1060** dan **MacBook M1**, Chrome terbaru, `main` terbaru. Hasilnya dipakai untuk A3 (perbaikan FPS, P6) dan A4 (bug visual / NaN).

## Ringkasan

- 3 experience + lintas aplikasi, 32 titik uji. Prioritas 1 (wajib) dulu: 18 titik, sekitar 45-60 menit per mesin (perkiraan).
- Yang dikirim per mesin: JSON "Salin hasil" dari `?prof=1` per experience, isi kolom FPS, dan foto layar hanya bila ada yang aneh.
- Paling dicari: **titik putih berkedip** (tanda NaN, terutama di M1), FPS di bawah 30, tersendat saat menekan tombol, dan bagian yang tampak salah.

## Cara otomatis (disarankan)

Skrip `tools/uji_gpu_lokal.py` menjalankan sebagian besar titik di bawah dengan Chrome dan GPU komputer ini, lalu menulis laporan.

| Langkah | Windows (GTX 1060) | MacBook M1 |
| --- | --- | --- |
| 1. Sekali saja | Pasang Python 3 dari python.org (centang "Add to PATH") | Terminal: `xcode-select --install` bila `python3` belum ada |
| 2. Ambil kode terbaru | `git pull` di folder repo | sama |
| 3. Jalankan | Klik ganda `tools\uji_gpu_lokal.bat` | Klik ganda `tools/uji_gpu_lokal.command` (pertama kali: klik kanan > Open) |
| 4. Tunggu | Jendela Chrome dikendalikan skrip, jangan dipakai. Prioritas 1 sekitar 15-25 menit per preset (perkiraan) | sama |
| 5. Kirim | `hasil-uji-gpu/<tanggal>-<komputer>/laporan.md` (+ foto baris yang aneh) | sama |

Pilihan (tambahkan di belakang perintah, mis. `tools\uji_gpu_lokal.bat --lengkap`):

| Pilihan | Isi |
| --- | --- |
| (tanpa pilihan) | Prioritas 1; preset bawaan Windows / Linux = Ultra, Tinggi; Mac = Hemat, Sedang |
| `--lengkap` | Juga prioritas 2: motor, kamera, tur 90 s, gelombang Millar (tunggu 130 s), sinematik Millar, relai, tesseract |
| `--preset ultra,tinggi` | Pilih preset (ultra, tinggi, sedang, rendah, hemat) |
| `--exp copper` | Hanya experience tertentu (copper, millar, gargantua) |
| `--vsync` | Biarkan batas FPS layar (bawaan dilepas supaya terlihat kemampuan GPU) |
| `--asli` | Ukuran jendela dan DPR layar asli (bawaan 1920 x 1080 DPR 1 agar bisa dibanding antar mesin) |
| `--chrome` | Pakai Google Chrome terpasang, bukan Chromium unduhan Playwright |
| `--tanpa-jupiter` | Lewati putaran Copper Jupiter |

Isi laporan per titik: FPS rata-rata, waktu frame p50 / p95 / maks, jumlah frame > 50 ms (tersendat), waktu GPU per pass (Copper: bayangan / scene / post; Millar: langit / laut / scene / post), jumlah titik putih terisolasi di dua tangkapan berturut-turut (petunjuk NaN, bukan bukti), foto layar, galat konsol, data `?prof=1` (program shader per tombol Q / P). Yang tetap perlu mata manusia: kesan visual, bagian yang tampak salah, tersendat yang terasa.

## Cara mengukur (manual)

| Langkah | Isi |
| --- | --- |
| 1 | Buka experience dengan `?prof=1` di alamat, mis. `experiences/cooper-station/index.html?prof=1`. Panel kecil muncul di kiri bawah |
| 2 | Muat sampai tombol Mulai, tekan Mulai, jalankan titik uji experience itu |
| 3 | Di akhir, tekan **Salin hasil** di panel kiri bawah, tempel ke chat / file (JSON: tahap muat, program shader per tombol, frame terpanjang) |
| 4 | FPS: Copper = klik judul HUD untuk HUD lengkap (baris FPS dan GPU: bayangan / scene / post ms); Millar = baris "GPU (langit / laut / scene / post)"; Gargantua = baris FPS di panel |
| 5 | Catat preset yang dipakai. GTX 1060: Ultra lalu Tinggi. M1: Hemat lalu Sedang |
| 6 | Biarkan 10 s di tiap titik sebelum mencatat FPS (adaptasi mata, pohon jauh, cache) |

Simbol hasil: OK = tampak benar dan lancar; ! = ada masalah (tulis singkat); NaN = titik putih / hitam berkedip.

## Copper Corn Station

| # | Pri | Titik uji (cara ke sana) | Yang dilihat | Fitur / dokumen | FPS GTX | FPS M1 | Hasil |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | 1 | Muat awal dengan `?prof=1` | Lama sampai Mulai aktif, frame pertama tidak membeku | P0-P4 `rencana-performa.md` | - | - | |
| C2 | 1 | Kartu mulai, lalu Mulai, tahan W | Kotak "Petunjuk singkat"; gerak awal lari, Shift = jalan; X turbo | commit `4369107` | - | - | |
| C3 | 1 | Tombol 1 (rumah Cooper), siang | FPS dasar; tekstur dekat aspal, trotoar, dinding, papan nama toko, teras | Tahap 32, 22 | | | |
| C4 | 1 | Peta M, klik New York (pusat), siang | Orang GLB terpadat (tidak meletup antar jarak, tanpa titik putih), mobil dekat, menara batu | Tahap 28, 26, 22 | | | |
| C5 | 1 | Tombol 2 (puncak bukit) | Rumput fluffy padang, pohon 21 jenis, tajuk bergumpal | Tahap 29, 25 | | | |
| C6 | 1 | Tombol 0 (hutan lebat) | Pohon jauh (impostor oktahedral Ultra), konifer, kabut hutan | Tahap 25, V5 | | | |
| C7 | 1 | Tombol 9 (air mancur), N sampai mendung | Hujan miring, genangan memantulkan gedung, riak air | Tahap 23 | | | |
| C8 | 1 | `]` sampai jam 21:00 di kota | Gedung malam, halo lampu (kuat hanya saat hujan / kabut), sorot lampu mobil | 21c, 24e, V4 | | | |
| C9 | 1 | V (kamera luar), lalu I (gerhana) | Lambung luar putih berblok, garis jendela Skyway tidak merayap, gerhana | X1, X4, 17a | | | |
| C10 | 1 | Kartu mulai: Planet Jupiter (8k), Mulai, panel ` > Waktu > Lompat ke Io / Europa | Kamera luar menghadap bulan, lingkaran kuning; bayangan bulan di Jupiter | Tahap 30, 31, `4369107` | | | |
| C11 | 1 | Tombol 8 (kokpit), E lepas sandar, A/D, W | A/D guling, Z/C geser; kokpit, kaca, panel lambung | V2, `4369107` | | | |
| C12 | 2 | F (kamera), klik untuk foto, Enter | Jendela bidik, foto tersimpan, tanpa membeku lama | Rencana K | | | |
| C13 | 2 | Y (tur) sampai selesai | Tidak ada layar membeku atau patah antar titik | Tur v2.15 | | | |
| C14 | 2 | C (motor) di jalan, malam, Shift | Lampu depan, getaran, FPS saat cepat | 19b, 19c | | | |
| C15 | 2 | Ganti Q dan P beberapa kali | Tidak tersendat saat ganti (0 program baru di `?prof=1`) | P4 | - | - | |
| C16 | 2 | M1 saja: Hemat di C3, C4, C7 | FPS layak (>= 30) dan tanpa NaN | Preset Hemat | - | | |

## Millar's World

| # | Pri | Titik uji (cara ke sana) | Yang dilihat | Fitur / dokumen | FPS GTX | FPS M1 | Hasil |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M1 | 1 | Muat awal `?prof=1`, sinematik kedatangan menyala | Bar muat bergerak, sinematik tanpa patah, plasma orbit | P2, M4, M5d | | | |
| M2 | 1 | Jalan di air, menunduk, lari (bawaan) dan Shift | Percikan kaki, tubuh astronaut, kain pakaian, visor basah | M5c, M6a-M6i | | | |
| M3 | 1 | Tunggu gelombang mendekat (lihat dari air) | Muka lereng halus, kaki gelombang tanpa garis lurus, busa tidak berkedip | M5e, X4 | | | |
| M4 | 1 | Misi: M radar, ambil pecahan (tahan E), E di tangga, terbang lolos | Kokpit, MFD, laut dari ketinggian | M3, M5a | | | |
| M5 | 2 | V tampilan belakang / kokpit saat terbang, Q tiap preset | Tidak tersendat saat Q | P4 | | | |
| M6 | 2 | F (kamera), foto | Seperti C12 | Rencana K | | | |
| M7 | 2 | Pilih wahana Petrel / GX-01 di kartu mulai | Wahana tampil, kaki menahan pemain | Pilihan wahana W1-W7 | | | |

## Gargantua

| # | Pri | Titik uji (cara ke sana) | Yang dilihat | Fitur / dokumen | FPS GTX | FPS M1 | Hasil |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G1 | 1 | Muat `?prof=1`, tampilan awal, Q Ultra dan Tinggi | Tepi bayangan halus, bintang HDR tidak hilang, piringan | AA1, V4 | | | |
| G2 | 1 | N (suasana Kelam) | Debu bergumpal, planet Millar, tanpa titik putih | MK1-MK9 | | | |
| G3 | 1 | Panel Misi: skenario susur piringan, V ke kokpit | Kokpit padat, layar MFD, indikator, partikel menabrak kaca | K2-K7, G3 | | | |
| G4 | 2 | Skenario tesseract | Bidik, terbang, adegan hiperkubus | G5 | | | |
| G5 | 2 | Saat misi, V sampai pandangan relai | Jejak ungu, pulsa | G9 | | | |
| G6 | 2 | F (kamera), foto | Seperti C12 | Rencana K | | | |

## Lintas aplikasi

| # | Pri | Titik uji | Yang dilihat | Dokumen | Hasil |
| --- | --- | --- | --- | --- | --- |
| U1 | 2 | Di ketiga experience: H, `, ? | UI seragam (kaca, warna aksen, tab), H menyembunyikan semua | `rencana-ui-seragam.md` | |
| U2 | 2 | Menu utama, gulir dari atas ke bawah; halaman Pelajari ketiganya | Paralaks lancar, kanvas detail beranimasi | `analisa-performa-detail.md` | |
| U3 | 2 | VR (bila sempat, Rift CV1 + GTX 1060) | Lanjutan VR8 | `rencana-vr.md` | |

## Format laporan yang paling membantu

1. Per mesin: tabel di atas dengan kolom FPS dan Hasil terisi (boleh difoto dari ponsel).
2. JSON "Salin hasil" `?prof=1` per experience (3 per mesin).
3. Foto layar hanya untuk baris bertanda ! atau NaN, sebut nomor barisnya (mis. "C4 NaN di orang dekat").

## Keterbatasan

- Daftar disusun dari dokumen rencana yang berstatus "menunggu uji"; fitur kecil di luar dokumen itu bisa terlewat.
- Perkiraan durasi belum diukur.
- FPS bergantung resolusi layar dan suhu laptop; tulis resolusi layar bila bukan 1920 x 1080.
