# Review kode dan usulan fase berikutnya

Per 14 November 2026, `main` di commit `4369107`. Review statis: struktur, ukuran, pola berulang, status uji di dokumen rencana. Tidak ada uji FPS / visual di GPU asli.

## Ringkasan

- Fitur sudah sangat banyak. Risiko terbesar adalah **utang uji**: 22 dokumen rencana masih berstatus "menunggu uji" / "belum diuji", dan FPS saat bermain di GTX 1060 / M1 (P6) belum pernah diukur.
- Fondasi mulai berat: Copper 19.877 baris dalam satu file, `CLAUDE.md` 147 KB, tiga cara terjemahan berbeda, 24 saklar URL di Copper, repo 55 MB.
- Usulan: **Fase A (uji dan stabilisasi) dulu, lalu Fase B (rapikan fondasi)**. Konten baru (Penerbangan Kestrel) setelahnya.

## 1. Data dasar

| Item | Nilai | Sumber |
| --- | --- | --- |
| Menu utama `index.html` | 757 baris, 66,5 KB | `wc` |
| Copper `index.html` | 19.877 baris, 1,50 MB | `wc` |
| Gargantua `index.html` | 4.438 baris, 335 KB | `wc` |
| Millar `index.html` | 4.400 baris, 346 KB | `wc` |
| Halaman detail (3) | 1.206 / 1.465 / 1.178 baris | `wc` |
| `shared/` | 14 MB (12,7 MB lagu tema base64) | `du` |
| Aset Copper | 29 MB (Jupiter 14k 14 MB, orang 3,4 MB, motor 3,0 MB) | `du` |
| Repo terkemas | 55,4 MB | `git count-objects` |
| Skrip `tools/` | 65 | `ls` |
| `CLAUDE.md` | 147.454 byte; baris terpanjang 12.726 karakter | `wc`, `awk` |
| Cabang remote | 44 (sebagian besar lama, tertinggal dari `main`) | `git branch -r` |
| TODO / FIXME / console.log di 4 halaman utama | 0 | `grep` |

## 2. Temuan

Tingkat: Tinggi = berisiko bug atau memperlambat semua kerja; Sedang = biaya perawatan; Rendah = rapi-rapi.

### Lintas aplikasi

| # | Tingkat | Temuan | Dampak |
| --- | --- | --- | --- |
| X1 | Tinggi | Utang uji: 22 dokumen di `docs/` berisi "menunggu uji" / "belum diuji" (tahap 25a-25l, 28, 30, 31, 32, UI1-UI8, K1-K9 kamera, M5, M6, VR8, P0-P4). P6 (FPS saat bermain) berstatus "Belum, menunggu angka P0 GPU asli" | Bug NaN di M1 dan penurunan FPS bisa menumpuk tanpa diketahui; sandbox SwiftShader tidak menampakkannya (catatan GPU di `CLAUDE.md`) |
| X2 | Tinggi | `CLAUDE.md` 147 KB dimuat di setiap sesi agen; baris tabel Gargantua / Millar ribuan karakter | Konteks agen penuh sebelum mulai kerja, biaya token tinggi, entri mudah basi (mis. baris tahap 30 di tabel struktur masih "belum dikerjakan", padahal riwayat tahap 30 dan 31 selesai) |
| X3 | Sedang | Tiga cara terjemahan: Copper `I18N.en` dengan kunci teks Indonesia + `translateDom()`; Gargantua sumber English + kamus `ID` + `txt()`; Millar atribut `data-t` + `t()` | Teks baru rawan lupa diterjemahkan; uji bahasa hanya ada untuk Copper (`tools/uji_bahasa.py`) |
| X4 | Sedang | Subsistem berulang di tiap experience: audio (`AudioContext`), bantuan (`toggleHelp` / `buildHelp`), preset, musik file sendiri; halaman detail mengulang `panel()`, `loop()`, `qTune()` 3 kali | Perbaikan harus dibuat 3 kali |
| X5 | Sedang | Saklar URL warisan: Copper membaca 24 parameter (`?pohon=lama`, `?orang=lama`, `?rumput=lama`, `?v4=0`, `?v5=0`, ...), 8 di antaranya jalur `lama` | Tiap saklar menyimpan jalur kode lama; makin lama makin sulit diubah |
| X6 | Sedang | Tidak ada CI (`.github/` tidak ada); 65 skrip uji dijalankan manual | Regresi (galat muat, kamus kurang) baru ketahuan saat Bhakti menguji |
| X7 | Rendah | 44 cabang remote, kebanyakan tertinggal dari `main` (riwayat `main` dimulai 29 September 2026) | Membingungkan saat memilih cabang |
| X8 | Rendah | `document.write` untuk data wahana: `experiences/gargantua/index.html:111`, `experiences/millar/index.html:144` | Usang dan memblokir parser; Chrome bisa memblokirnya di koneksi lambat |
| X9 | Rendah | Aset base64 di git (Jupiter 14k 14 MB, lagu 12,7 MB) | Tiap perubahan aset menambah ukuran repo permanen; base64 +33% dari ukuran biner. Ini harga dari aturan "jalan dari file://", jadi diterima, cukup jangan sering diganti |

### Menu utama (`index.html`)

| # | Tingkat | Temuan |
| --- | --- | --- |
| L1 | Rendah | Tanpa `<meta name="description">`, Open Graph, dan favicon: tautan yang dibagikan tampil polos |
| L2 | Rendah | Tautan Mulai / Pelajari `a.go` baru mendapat `href` lewat JS (`index.html:625`) |
| L3 | Info | Kartu "Penerbangan Kestrel" masih `ready: false` sejak awal |
| Baik | - | Tanpa library, reduced-motion dihormati, bahasa dibagi lewat `lazarus.lang`, `aria-label` di navigasi, paralaks satu rAF terhemat |

### Copper Corn Station

| # | Tingkat | Temuan |
| --- | --- | --- |
| C1 | Tinggi | Satu modul 19.877 baris / 1,5 MB, 27 baris > 400 karakter (terpanjang 2.822). Setiap edit agen harus mencari di file raksasa; risiko salah tempel tinggi |
| C2 | Sedang | Sisa tahap: 21a-2 semburan dan 21a-3 riak air mancur belum; tahap 32 "belum diuji visual dan FPS" |
| C3 | Info | Fitur baru (petunjuk awal, lari bawaan, A/D guling, penanda bulan) di `main` sejak `4369107`, belum diuji Bhakti |

### Millar's World

| # | Tingkat | Temuan |
| --- | --- | --- |
| M1 | Sedang | M5 kelompok 1-3 dan M6c / M6g "menunggu uji pemilik"; M6 tangan ke tangga dan tubuh terguling saat tersapu ditunda |
| M2 | Rendah | Tidak ada demo otomatis (Copper punya tur Y); sinematik kedatangan sudah ada dan bisa jadi dasar |

### Gargantua

| # | Tingkat | Temuan |
| --- | --- | --- |
| G1 | Sedang | Kartu mulai belum punya "Petunjuk singkat" seperti Copper dan Millar; misi G1-G9 punya banyak tombol (V, O, E, M, W/S A/D, Enter) yang hanya ada di bantuan |
| G2 | Rendah | Usulan lanjutan misi (baris "delta-v untuk lolos", skenario tantangan) menunggu keputusan pemilik; S3-S7 suara ditunda |
| G3 | Rendah | Tanpa demo otomatis |

## 3. Usulan fase berikutnya

### Fase A: uji dan stabilisasi (disarankan pertama)

Tujuan: semua fitur yang "menunggu uji" diuji sekali di GTX 1060 dan M1, angka FPS tercatat, bug diperbaiki sebelum menambah fitur.

| Langkah | Isi | Effort | Model | Thinking |
| --- | --- | --- | --- | --- |
| A1 | Daftar uji satu halaman (`docs/app/daftar-uji-gpu.md`): per experience titik uji tetap (lokasi, preset, tombol), apa yang dilihat, kolom FPS dan catatan; dirangkum dari 22 dokumen "menunggu uji" | Low | Sonnet 5.5 | low |
| A2 | Bhakti mengukur dengan `?prof=1` dan HUD GPU (`GPUT`) di GTX 1060 dan M1, kirim JSON "Salin hasil" | - (pemilik) | - | - |
| A3 | P6: perbaiki titik panas FPS dari data A2, hanya perubahan dengan hasil identik | High | Opus 5.5 | high |
| A4 | Perbaikan bug visual dan NaN M1 dari A2 | High | Opus 5.5 | xhigh |
| A5 | Tandai status dokumen rencana "diuji" / "perlu revisi" | Low | Haiku 4.5 | low |

### Fase B: rapikan fondasi

| Langkah | Isi | Effort | Model | Thinking |
| --- | --- | --- | --- | --- |
| B1 | Rampingkan `CLAUDE.md` ke sekitar 20-30 KB: aturan, struktur ringkas, angka dasar; peta kode per experience pindah ke `docs/<id>/peta-kode.md` (dibaca agen bila perlu) | Medium | Sonnet 5.5 | medium |
| B2 | CI ringan GitHub Actions: `node --check` blok skrip, muat ketiga experience + menu headless tanpa galat (`qc_load.py`, three.js lokal), `uji_bahasa.py`, `uji_wahana.mjs` | Medium | Sonnet 5.5 | medium |
| B3 | Satu sistem bahasa `shared/lang.js` (kamus per halaman, `t()`, `data-t`, pemeriksa kunci); pindah Millar lalu Gargantua, Copper terakhir | High | Opus 5.5 | high |
| B4 | `shared/detail.js` untuk `panel()`, `loop()`, `Q` / `qTune()`, `player()` ketiga halaman detail | Medium | Sonnet 5.5 | medium |
| B5 | Pensiunkan saklar `?xxx=lama` yang fiturnya sudah diterima Bhakti (daftar diputuskan pemilik), hapus jalur lama | Medium | Sonnet 5.5 | medium |
| B6 | Copper dipecah bertahap: string GLSL besar (`LIGHT_GLSL`, `BUILD_FS`, shader tanah) ke `experiences/cooper-station/glsl/*.js` (skrip biasa, `window.GLSL_*`, tetap jalan dari file://); logika tetap di modul | High | Opus 5.5 | high |
| B7 | Hapus cabang remote lama (setelah dicek tidak berisi kerja yang belum masuk), ganti `document.write` dengan pemuatan skrip yang ditunggu | Low | Haiku 4.5 | low |

### Fase C: pengalaman pemain seragam

| Langkah | Isi | Effort | Model | Thinking |
| --- | --- | --- | --- | --- |
| C1 | Petunjuk singkat di kartu mulai Gargantua (misi, V, O, M) | Low | Sonnet 5.5 | low |
| C2 | Demo otomatis Y di Millar (sinematik kedatangan + jalan ke pecahan + lepas landas) dan Gargantua (skenario jatuh dengan kamera otomatis) | High | Opus 5.5 | high |
| C3 | Menu utama: meta description, Open Graph, favicon, `href` bawaan di HTML | Low | Haiku 4.5 | low |
| C4 | Sisa yang ditunda: air mancur 21a-2 / 21a-3 (Copper), tangan ke tangga M6 (Millar) | Medium | Sonnet 5.5 | medium |

### Fase D: konten baru (setelah A dan B)

| Opsi | Isi | Effort |
| --- | --- | --- |
| D1 | Experience ke-4 "Penerbangan Kestrel": dari dermaga Copper ke cincin Saturnus, memakai `shared/kestrel.js`, `armada.js`, kokpit v5, kendali terbang yang sudah seragam | High (rencana dulu, dipecah langkah) |
| D2 | Usulan misi Gargantua yang menunggu keputusan (delta-v lolos, skenario tantangan) | Medium |

## 4. Rekomendasi urutan

1. A1-A2 minggu ini (daftar uji + pengukuran Bhakti), A3-A4 dari hasilnya.
2. B1 dan B2 segera (murah, mempercepat semua kerja berikutnya), B3-B6 bertahap.
3. C1 dan C3 bisa diselipkan kapan saja (kecil).
4. D1 dimulai setelah FPS ketiga experience tercatat di GPU asli.

## 5. Keterbatasan review

- Review statis: kode tidak dibaca baris per baris (lebih dari 36.000 baris di halaman dan `shared/`), jadi bug logika tertentu bisa terlewat. Temuan diambil dari ukuran, pencarian pola, dan status dokumen rencana.
- Tidak ada pengukuran FPS atau uji visual; semua dampak performa adalah perkiraan.
- Status "lama / tertinggal" cabang remote dari perbandingan `git diff` dengan `main`; isi tiap cabang belum diperiksa satu per satu.
