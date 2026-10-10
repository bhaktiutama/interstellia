# Rencana perbaikan tema suara bawaan (S0-S7)

Tujuan: suara bawaan ketiga experience tidak lagi terdengar datar dan seperti bip synth murahan, tanpa memakai repo sound-layer (tidak cocok untuk app real-time). Semua tetap jalan dari file:// tanpa build step.

## Ringkasan

- Penyebab utama datar: lapisan latar adalah satu loop noise 2-6 s lewat satu filter statis, nada adalah sinus murni tanpa gerak, dan Gargantua serta Millar tidak punya ruang (gema) sama sekali.
- Rencana: fondasi bersama `shared/audio.js` dulu (ruang, gerak, variasi, master), lalu perbaiki tiap experience, lalu rekaman CC0 hanya untuk efek yang memang sulit disintesis.
- Karena Claude tidak bisa mendengar, tiap tahap diukur dengan alat `tools/ukur_suara.cjs` (angka "kedataran"), lalu Bhakti mendengar dengan daftar cek.

## Diagnosis dari kode (keadaan sekarang)

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
