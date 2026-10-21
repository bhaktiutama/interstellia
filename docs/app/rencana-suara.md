# Rencana perbaikan tema suara bawaan (S0-S7)

Tujuan: suara bawaan ketiga experience tidak lagi terdengar datar dan seperti bip synth murahan, tanpa memakai repo sound-layer (tidak cocok untuk app real-time). Semua tetap jalan dari file:// tanpa build step.

## Ringkasan

- Penyebab utama datar: lapisan latar adalah satu loop noise 2-6 s lewat satu filter statis, nada adalah sinus murni tanpa gerak, dan Gargantua serta Millar tidak punya ruang (gema) sama sekali.
- Rencana: fondasi bersama `shared/audio.js` dulu (ruang, gerak, variasi, master), lalu perbaiki tiap experience, lalu rekaman CC0 hanya untuk efek yang memang sulit disintesis.
- Karena Claude tidak bisa mendengar, tiap tahap diukur dengan alat `tools/ukur_suara.cjs` (angka "kedataran"), lalu Bhakti mendengar dengan daftar cek.

## Status

| Tahap | Status | Catatan |
| --- | --- | --- |
| S0 | Dibatalkan | `tools/ukur_suara.cjs` dihapus (masih ada di commit `ca80416`) |
| S1 | Dibatalkan | `shared/audio.js` dihapus (masih ada di commit `ca80416`) |
| S2 | Dibatalkan | Hasil dengar Bhakti: suara baru Gargantua jauh lebih jelek dan kurang realistis dari sebelumnya. Suara G7 lama dikembalikan persis (versi commit `fe3a9d9`) |
| S3-S7 | Ditunda | Pendekatan sintesis berlapis tidak dilanjutkan tanpa keputusan baru |

Pelajaran: angka ukur (loop, variasi, fluks) membaik, tapi telinga menilai sebaliknya. Angka "kurang datar" tidak sama dengan "lebih realistis"; berikutnya keputusan suara dimulai dari dengar, bukan dari angka.

## Hasil ukur S2 (arsip, versi yang dibatalkan; Gargantua, render offline 12 s, detik pertama dibuang)

Diukur `node tools/ukur_suara.cjs gargantua --md`. Lama = `audioBuildOld` (suara sebelum S2), baru = `audioBuildNew`.

| Keadaan | Versi | RMS dBFS | Puncak dBFS | Variasi dB | Fluks | Pusat Hz | Loop | Korelasi L/R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kabin diam | lama | -33.5 | -28.4 | 0 | 0.108 | 124 | 1 | 1 |
|  | baru | -34.9 | -24.1 | 0.6 | 0.31 | 886 | 0.142 | 0.779 |
| pendorong (W) | lama | -32.8 | -23.8 | 0 | 0.474 | 4578 | 1 | 1 |
|  | baru | -34.4 | -21.4 | 0.5 | 0.488 | 4767 | 0.128 | 0.623 |
| mesin utama (Shift) | lama | -15.5 | -7.5 | 0.1 | 0.347 | 2416 | 1 | 1 |
|  | baru | -14.4 | -5.4 | 1.1 | 0.347 | 2335 | 0.243 | 0.917 |
| susur piringan + tumbukan | lama | -24 | -6.1 | 0.2 | 0.659 | 3678 | 0.233 | 1 |
|  | baru | -24.1 | -5.7 | 0.7 | 0.625 | 2337 | 0.169 | 0.528 |
| ping relai melambat | lama | -33.4 | -21.8 | 0.2 | 0.122 | 129 | 0.956 | 1 |
|  | baru | -34.6 | -19.7 | 0.7 | 0.321 | 911 | 0.616 | 0.764 |
| pasang surut dalam horizon | lama | -23.5 | -17.9 | 0.1 | 0.108 | 133 | 0.547 | 1 |
|  | baru | -24.5 | -13.2 | 2.4 | 0.276 | 505 | 0.163 | 0.645 |
| tesseract | lama | -24.4 | -15.4 | 0.2 | 0.099 | 193 | 0.586 | 1 |
|  | baru | -24.4 | -9.4 | 1.3 | 0.259 | 1816 | 0.246 | 0.058 |
| suar x2 | lama | -33.3 | -18.6 | 0.6 | 0.132 | 272 | 0.704 | 1 |
|  | baru | -32 | -7.4 | 3 | 0.342 | 1991 | 0.696 | 0.621 |
| kaca pecah | lama | -29.7 | -3.1 | 3.2 | 0.147 | 1081 | 0.113 | 1 |
|  | baru | -31.1 | -2.7 | 3.2 | 0.348 | 1203 | 0.103 | 0.548 |

Yang terbaca dari angka (bukan dari telinga):

- Loop: kabin, pendorong, dan mesin versi lama = 1,0 (noise 2 s yang sama diulang terus; adegan ping 0,96), versi baru semua lapisan terus-menerus 0,13-0,25. Ping (0,62) dan suar (0,70) tinggi karena peristiwanya memang berulang (ping tiap 1,6 s).
- Variasi kekerasan lama 0-0,2 dB (diam), baru 0,5-3 dB; fluks spektrum naik 2-3x di kabin, ping, pasang surut, tesseract.
- Kekerasan rata-rata baru dalam -1,6 sampai +1,3 dB dari lama di semua keadaan (sengaja disetel agar volume yang biasa dipakai tidak berubah).
- Pusat spektrum kabin naik 124 -> 886 Hz (kipas sirkulasi terdengar); bila terasa melelahkan di misi panjang, kipas bisa diturunkan.
- Lebar stereo: lama mono (1,0), baru 0,53-0,92; tesseract 0,06 (lebar, tetap positif sehingga aman di speaker mono).
- Puncak tertinggi kaca pecah -2,7 dBFS (lama -3,1).

Biaya CPU (render offline 12 s di sandbox, termasuk analisis yang sama untuk keduanya): lama 0,4-0,9 s, baru 1,9-2,7 s (tesseract 3,7-4,4 s). Per komponen: ruang kabin 0,47 s, 2 kompresor master 0,27 s, 20 osilator 0,25 s, 10 loop noise 0,15-0,19 s. Audio berjalan di thread sendiri; FPS di MacBook M1 perlu dicek Bhakti.

## Diagnosis dari kode (keadaan sebelum S2)

| Experience | Lapisan | Cara dibuat sekarang | Kenapa terdengar datar / murah |
| --- | --- | --- | --- |
| Copper | angin, kota, hujan, keramaian, ban mobil | noise 2 s diulang, satu biquad statis per lapisan (`startAudio()` `loop()`) | spektrum diam; loop 2 s bisa terdengar berulang; tidak ada hembusan atau peristiwa |
| Copper | dengung mesin, kabin, mesin shuttle | sinus / gergaji 38-150 Hz tetap | nada tetap tanpa getar, tanpa beat, tanpa resonansi struktur |
| Copper | burung `chirp()`, jangkrik `cricket()` | sinus naik 0,06 s | satu bentuk siulan, bunyi seperti alarm kecil |
| Copper | langkah `playStep()` | noise putih tersaring + sinus 140 Hz (kayu) | tanpa hentakan tumit / gesek, tanpa variasi permukaan yang jelas |
| Copper | penjepit dermaga `portClank()`, bel `ding()`, klakson | sinus turun + 3 parsial tetap, gelombang kotak | logam tanpa modus resonansi yang banyak, tanpa ruang |
| Copper | musik generatif | akor organ dari harmonik sinus + nada piano 2 sinus | warna seragam, tanpa envelope filter, tanpa lebar stereo |
| Gargantua | kabin, pendorong, mesin utama | 55 + 110 Hz sinus, noise bandpass, gergaji 41 Hz | statis; tidak ada getaran badan wahana saat dorong |
| Gargantua | bip relai | `sfxTone()` sinus 880 Hz tiap 1,6 s | paling mirip "bip murahan" |
| Gargantua | tumbukan, suar, kaca pecah | noise tersaring + segitiga | tanpa lapisan (serangan, badan, ekor), tanpa variasi |
| Gargantua | gemuruh piringan, pasang surut, tesseract | noise lowpass, sinus naik, 5 sinus | gerak hanya dari cutoff; tesseract akor sinus polos |
| Millar | angin, laut, arus, seretan | noise pink / cokelat 2,5-6 s, satu filter | laut tanpa ombak pecah satu-satu; angin tanpa siul atau desir |
| Millar | gemuruh gelombang raksasa | noise cokelat lowpass + sinus 27 / 38,5 Hz | gemuruh rata; tanpa derak, tanpa pukulan air |
| Millar | ping blackbox, bip ambil barang | `tone2()` sinus | "bip" |
| Semua | ruang | hanya Copper punya gema noise 4,5 s (satu untuk semua tempat); Gargantua dan Millar kering | di kokpit, helm, dan stasiun besar terdengar sama |
| Semua | ruang 3D | `StereoPanner` di beberapa efek saja | sumber tidak punya jarak atau arah depan / belakang |
| Semua | master | satu `DynamicsCompressor` | tidak ada EQ, kekerasan antarexperience tidak seragam |

Catatan: diagnosis ini dari membaca kode (`startAudio()`, `audioInit()`, `updateAudio()`, `sfx*()` di ketiga `index.html`), belum diukur. Angka pertama baru ada setelah S0.

## Prinsip

- Pertahankan yang ada: tiap perubahan bisa dimatikan lewat `?snd=0` (suara lama persis) sampai Bhakti setuju.
- Sintesis tetap boleh untuk latar dan nada, tapi harus bergerak: modulasi lambat, peristiwa acak, variasi tiap pemicu.
- Efek sekali bunyi (benturan, klik, kaca) memakai rekaman CC0 hanya bila sintesis yang diperbaiki masih kalah (S5). Rekaman disimpan base64 di `assets/*.data.js`, kredit di `KREDIT.md` dan tab Tentang.
- Fisika tetap jadi sumber: laju jam relai Gargantua tetap mengatur nada ping, jarak gelombang Millar tetap mengatur gemuruh (fungsi murni `audioMix()` tidak berubah artinya).
- Musik dari file sendiri (tombol J) sudah ada di ketiga experience; rencana ini hanya tentang tema bawaan.

## Tahap

| Tahap | Isi | Effort | Model | Thinking | File dan fungsi yang disentuh |
| --- | --- | --- | --- | --- | --- |
| S0 | Alat ukur suara: render offline 30 s tiap keadaan (`OfflineAudioContext`), angka: kekerasan (LUFS perkiraan), puncak, variasi kekerasan 400 ms (std dB), fluks spektrum, pusat spektrum, deteksi pengulangan loop (autokorelasi 1-8 s), lebar stereo; laporan sebelum / sesudah | Medium | Sonnet 5.5 | medium | `tools/ukur_suara.cjs` (baru); `startAudio(ctx)` / `audioInit(ctx)` menerima konteks dari luar |
| S1 | Fondasi bersama `shared/audio.js` (`window.AUDIOKIT`, skrip biasa): bank noise panjang 12 s dengan titik mulai acak, ruang konvolusi dari IR buatan per tempat (kabin kecil, helm, aula stasiun, terbuka), `voice()` sekali bunyi dengan acak nada / kekerasan / filter dan round robin, pengendali modulasi lambat (hembusan, napas), panner HRTF dengan jarak, rantai master (EQ rak rendah / tinggi, kompresor lem, limiter puncak), bus ducking | Medium | Sonnet 5.5 | medium | `shared/audio.js` (baru); belum mengubah experience |
| S2 | Gargantua: kabin dengan resonansi badan (filter modus dari ukuran GX-01), pendorong dan mesin dengan getaran naik saat dorong, gemuruh piringan granular yang ikut laju gas, ping relai baru (badan sonar beresonansi + ekor ruang, nada tetap dikali `relMsg().rate`), tumbukan kaca 3 lapis (klik, badan modus, ekor), kaca pecah dari banyak serpih, tesseract dengan pad bergerak (detune, filter, lebar stereo) | Medium | Sonnet 5.5 | medium | `audioInit()`, `updateAudio()`, `sfxTone()`, `sfxImpact`, `sfxFlare`, `sfxShatter`; `tools/uji_misi_gargantua.py` kelompok 7 |
| S3 | Millar: laut dari ombak pecah satu-satu (peristiwa granular, jarak dan arah), angin berhembus dengan siul tipis saat kencang, gemuruh gelombang raksasa berlapis (sub, gemuruh tengah, derak buih makin dekat makin terang), cipratan 3 lapis, helm dengan ruang kecil dan napas yang lebih alami, ping blackbox dan ambil barang bernada logam, bukan sinus | Medium | Sonnet 5.5 | medium | `startAudio()`, `audioMix()` (tetap murni, kolom baru boleh), `updateAudio()`, `sfxSplash()`, `sfxImpact()`, `sfxBubble()`, `tone2()`, `sfxPickup()`; `tools/uji_millar.py` R5 |
| S4 | Copper: angin dan kota berlapis dengan peristiwa (mobil lewat dengan Doppler, keramaian dekat / jauh), hujan 2 lapis (tetes dekat + desis jauh) ikut naungan, burung dengan pola lagu per jenis (siul FM, trill), langkah 2 lapis per permukaan, logam dermaga dan bel dengan banyak modus, gema per tempat (rumah Cooper, terminal, kota, ladang, hub), musik generatif dengan warna lebih kaya (detune, envelope filter, lebar stereo, variasi voicing) | High | Opus 5.5 | high | `startAudio()`, `updateAudio()`, `playStep()`, `chirp()`, `cricket()`, `portClank()`, `ding()`, `playChord()`, `playNote()`, `motoHornSound()`; `tools/uji_bahasa.py` bila ada teks baru |
| S5 | Rekaman CC0 untuk efek yang masih kalah setelah S2-S4 (Bhakti memilih dari hasil dengar): unduh, potong, normalisasi, simpan base64 MP3 kecil; anggaran per experience 1,5 MB | Medium | Sonnet 5.5 | medium | `tools/siapkan_suara.py` (baru, ffmpeg), `experiences/<id>/assets/sfx.data.js`, `KREDIT.md`, tab Tentang |
| S6 | Kekerasan seragam: target master sama di ketiga experience (diukur S0), batas puncak, ducking efek penting di atas latar | Low | Haiku 4.5 | low | konstanta master di tiap experience |
| S7 | Dengar dan setel: Bhakti mendengar dengan daftar cek, perbaikan per catatan, `?snd=0` dihapus bila sudah setuju | Low | Sonnet 5.5 | low | sesuai catatan |

Urutan yang disarankan: S0, S1, S2 (Gargantua paling sedikit lapisan dan bip relainya paling mencolok), dengar dulu, baru S3 dan S4.

## Ukuran "datar" yang dipakai S0

| Angka | Arti | Arah perbaikan |
| --- | --- | --- |
| Variasi kekerasan (std dB jendela 400 ms, 30 s) | Latar yang diam nyaris 0 dB | naik, tapi tidak melonjak (batas atas ditentukan setelah S0) |
| Fluks spektrum rata-rata | Seberapa banyak warna bunyi berubah | naik |
| Puncak autokorelasi 1-8 s | Loop noise yang terdengar berulang | turun |
| Lebar stereo (korelasi L / R) | Mono = 1 | turun di latar, efek dekat tetap terpusat |
| Kekerasan dan puncak master | Antarexperience tidak seragam | sama di ketiga experience |

Angka ini alat bantu, bukan bukti bagus. Keputusan akhir tetap telinga Bhakti.

## Cara membandingkan (Gargantua)

Buka `experiences/gargantua/index.html` (suara baru) dan `experiences/gargantua/index.html?snd=0` (suara lama) di tab berbeda, mulai misi yang sama, dengarkan momen di daftar cek.

## Daftar cek dengar (S7, per experience)

| Experience | Momen yang didengar |
| --- | --- |
| Copper | pagi di kota (kabut), hujan di bawah pohon vs di jalan, rumah Cooper (dalam), terminal, kokpit shuttle saat sandar, motor 150 km/h, burung di taman |
| Gargantua | kabin diam, dorong biasa vs Shift, susur piringan (G3), ping relai saat jatuh (nada turun), kaca pecah, tesseract |
| Millar | berdiri diam di laut, berjalan di air, gelombang dari 20 km sampai tersapu, bawah air, kokpit KS-07, ping blackbox |

## Risiko

| Risiko | Penanganan |
| --- | --- |
| Biaya CPU (konvolusi, granular) di MacBook M1 dan ponsel | ruang konvolusi satu per experience, IR pendek; granular dibatasi jumlah suara; ikut preset Hemat |
| Uji audio yang ada memeriksa nama simpul (`AUDIO.brG`, `N.thr`, dll.) | nama lama dipertahankan sebagai titik kendali |
| Rekaman memperbesar halaman | anggaran 1,5 MB per experience, MP3 mono pendek |
| Format audio di Safari | memakai MP3 (dukungan `decodeAudioData` paling luas); Opus belum dipakai sampai diuji di Safari Bhakti |
| Kebijakan putar otomatis peramban | tetap dibuat setelah gerakan pengguna pertama seperti sekarang |
