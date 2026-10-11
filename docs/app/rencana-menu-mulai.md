# Rencana: menu mulai (boarding) seragam Copper dan Millar

Tujuan: kartu mulai Copper Corn Station dan Millar's World terlihat dan bekerja sama, tetapi opsi khusus tiap experience tetap ada. Patokan: Copper (paling lengkap, sesuai `docs/app/tombol.md`).

## Ringkasan

- Kerangka kartu, gaya, dan urutan bagian disamakan; isi khusus masuk ke satu bagian "Opsi experience".
- Millar mendapat yang belum dimilikinya: bilah muat, bahasa di dalam kartu, tautan bantuan.
- Tidak ada opsi yang dihapus; id elemen dan localStorage lama tetap (uji tidak rusak).

## Temuan (kondisi sekarang)

| Bagian | Copper (`#start`) | Millar (`#start`) | Beda |
| --- | --- | --- | --- |
| Judul | `h1` 18 px, huruf biasa | `h2` 22 px, huruf kapital berjarak lebar, tipis | Gaya beda |
| Latar | Gelap pekat 0,66, kartu padat `#14171c`, sudut 10 px | Tembus 0,25, kartu kaca blur, sudut 12 px | Gaya beda |
| Bilah muat | Ada (`#boot`, persen, label tahap); opsi muncul setelah siap (`#ready`) | Tidak ada; opsi langsung tampil | Millar kurang |
| Bahasa | Di dalam kartu, paling atas (`.langPick`) | Kotak mengambang kanan atas (`#lang`), di luar kartu | Letak beda |
| Label bagian | Aksen, kapital kecil 11 px | Redup 12 px huruf biasa | Gaya beda |
| Kualitas grafik | 5 preset + otomatis + catatan Hemat | Sama | Sama isi |
| Suasana | Tidak ada (N saat main) | 3 pilihan (`#moodPick`) | Khusus Millar |
| Mode + tingkat misi | Tidak ada | Misi / Jelajah, 3 tingkat + catatan | Khusus Millar |
| Sinematik | Tidak ada | Centang kedatangan dari orbit | Khusus Millar |
| Tombol Mulai | 14 px, padding 11 | 15 px, padding 10, margin 16 | Hampir sama |
| Tautan bawah | Bantuan (?) kiri + Kembali ke menu kanan | Hanya Kembali ke menu | Millar kurang bantuan |

Gargantua tidak punya kartu mulai (langsung jalan); di luar cakupan rencana ini, dicatat sebagai opsi U5.

## Susunan baku kartu (keduanya)

| Urutan | Bagian | Copper | Millar |
| --- | --- | --- | --- |
| 1 | Judul + subjudul | ya | ya |
| 2 | Bilah muat (opsi tersembunyi sampai siap) | ya | baru |
| 3 | Bahasa | ya | pindah dari `#lang` |
| 4 | Kualitas grafik + otomatis + catatan | ya | ya |
| 5 | Opsi experience (khusus) | kosong (bagian tidak digambar) | Suasana, Mode, Tingkat misi, Sinematik |
| 6 | Tombol Mulai | ya | ya |
| 7 | Tautan: Bantuan (?) kiri, Kembali ke menu kanan | ya | tambah Bantuan |

## Tahap

| Tahap | Isi | File / fungsi | Effort | Model | Thinking |
| --- | --- | --- | --- | --- | --- |
| U1 | Gaya bersama: satu blok CSS kartu mulai (latar, kartu, judul, `.plabel` aksen, `.pick`, `#go`, `.links`) disalin sama persis ke kedua file; Millar pakai `h1` gaya Copper | `cooper-station/index.html`, `millar/index.html` CSS `#start` | Low | Sonnet 5.5 | low |
| U2 | Bahasa Millar masuk kartu (bagian 3); `#lang` mengambang dihapus, salinan di tab Lainnya panel tetap; `translateDom()` memakai selektor gabungan | `millar` `#start`, loop `LANGS`, `translateDom()` | Low | Sonnet 5.5 | low |
| U3 | Bilah muat Millar: `#boot` + `#ready` seperti Copper, progres dari langkah muat yang sudah ada (shader, ombak FFT, cubemap); Mulai aktif setelah `__millarReady` | `millar` muat awal, `start()` | Medium | Sonnet 5.5 | medium |
| U4 | Bagian "Opsi experience" berjudul jelas; Millar: Suasana, Mode, Tingkat (disembunyikan saat Jelajah), Sinematik; tautan Bantuan (?) ke `toggleHelp()`; entri `I18N.en` baru | `millar` `#start`, `I18N.en` | Low | Sonnet 5.5 | low |
| U5 (opsional) | Gargantua kartu mulai susunan sama (bahasa, kualitas, opsi: skenario misi atau jelajah) | `gargantua/index.html` | Medium | Sonnet 5.5 | medium |

Status: U1-U4 selesai (gaya kaca dengan latar 0,45 dipakai keduanya, sesuai saran yang disetujui Bhakti). U3: modul Millar dimuat sekali jalan tanpa titik jeda, jadi bilahnya tak tentu (bergerak), bukan persen; opsi muncul setelah `__millarReady`. Tingkat misi disembunyikan saat mode Jelajah. U5 hanya bila diminta.

## Yang dipertahankan

- Semua opsi khusus Millar (suasana, mode, tingkat, sinematik) dan localStorage-nya (`millar.preset`, `millar.cine`, dst.).
- Id `#presetPick`, `#presetAuto`, `#go`, `#menuLink`, `#modePick`, `#levelPick`, `#moodPick`, `#cineOn` (dipakai `tools/uji_millar.py`).
- Copper tidak berubah perilakunya; hanya CSS bila perlu disamakan.

## Cek setelah tiap tahap

- Halaman termuat tanpa error (`tools/qc_load.py`), ganti bahasa di kartu mengganti teks kartu dan panel.
- Lebar ponsel 390 px: kartu tidak bergulir mendatar, tombol tidak terpotong.

## Keputusan

- Gaya: kartu kaca dengan latar 0,45, dipakai keduanya (disetujui).
