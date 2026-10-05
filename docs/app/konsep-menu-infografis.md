# Konsep menu utama infografis

Prototipe: `docs/app/menu-infografis.html` (buka langsung di browser). `index.html` belum diubah; diganti setelah disetujui pemilik.

## Ringkasan
- Menu jadi halaman gulir: hero dengan peta perjalanan, lalu satu bagian infografis per experience.
- Tiap bagian: diagram SVG beranimasi, 4 kartu angka, 6 fitur utama berikon, strip tombol penting, tombol Mulai di atas preview.
- Dua bahasa (ID sumber, EN), localStorage `lazarus.lang` dan `?lang=` seperti menu sekarang.

## Struktur
| Bagian | Isi |
| --- | --- |
| Hero | Judul, tagline, peta SVG Saturnus -> lubang hitam -> planet air (klik = gulir ke bagian) |
| 01 Copper Corn Station (aksen emas) | Penampang silinder berputar: R, gaya sentrifugal = 1 g, sumbu nol-g, lintasan Coriolis |
| 02 Gargantua (aksen oranye) | Bayangan, horizon, ISCO, relai 22 rs, lintasan GX-01 |
| 03 Millar's World (aksen teal) | Profil gelombang 1,2 km vs KS-07, jam dilatasi |
| Segera | Penerbangan Kestrel |
| Footer | Penafian proyek penggemar (sama) |

## Angka dan sumber
| Angka | Sumber |
| --- | --- |
| Copper: L 8 km, R 1.000 m, 63,4 s, 99,05 m/s, 1 g, 14 distrik, gerhana 2,78 jam | CLAUDE.md (Angka dasar, tahap 16, 17a) |
| Gargantua: 5 misi (G1-G5 + suara G7), 0,8 c di ISCO, sudut kritis 24,62 derajat, relai 22 rs | CLAUDE.md, `tools/uji_misi_gargantua.py` |
| Millar: 1,3 g, gelombang 1,2 km dan 125 m/s, 1 jam = 7 tahun | CLAUDE.md, `experiences/millar/index.html` (teks HUD) |

## Langkah adopsi ke index.html
1. Pindahkan isi teks ke `APP` / `EXPERIENCES` / `TXT` (tambah field `stats`, `feats`, `keys` per entri).
2. Ganti grid kartu dengan bagian infografis; path gambar jadi `experiences/<id>/preview.jpg`.
3. Uji `python tools/qc_load.py index.html`.

## Catatan
- Grafis seluruhnya SVG orisinal, tanpa library; animasi mati bila `prefers-reduced-motion`.
- Ikon fitur memakai emoji (cepat untuk prototipe); bisa diganti ikon SVG garis bila ingin lebih seragam.

## Prototipe v2 (`docs/app/menu-infografis-v2.html`)
| Perubahan | Isi |
| --- | --- |
| Bagian selebar layar | Preview jadi latar penuh (paralaks), gradasi warna aksen, navigasi titik di kanan |
| Muncul saat digulir | Teks dan panel naik pelan, garis diagram tergambar, angka menghitung naik, fitur muncul berurutan |
| Diagram | Copper: silinder 3D, dinding dalam berputar, sunline menyala, penampang end cap berputar. Gargantua: piringan bercahaya, lengkung cahaya dibelokkan, wahana jatuh, relai memancarkan sinyal. Millar: langit mendung dengan Gargantua, gelombang raksasa bergerak, semburan, KS-07 terbang melewati puncak |
| Interaktif | Copper: geser radius, periode, rpm, kecepatan tanah, dan beda gaya kepala-kaki dihitung (T = 2 pi akar(R/g), v = akar(gR)). Gargantua: sentuh zona (horizon, cahaya dibelokkan, ISCO, relai, lintasan jatuh) untuk penjelasan. Millar: geser lama di planet, tahun dan hari di luar dihitung (1 jam = 7 tahun) |
| Ikon | SVG garis seragam, menggantikan emoji |

Catatan: "di atas sekitar 2 rpm banyak orang pusing" adalah pedoman umum desain habitat berputar, bukan angka dari kode proyek.

## Prototipe v3 (`docs/app/menu-infografis-v3.html`)
Foto in-game dari pemilik (`docs/app/menu/cooper.webp`, `gargantua.webp`, `millar.webp`) dipakai langsung sebagai kanvas infografis.

| Bagian | Isi |
| --- | --- |
| Hero | Tiga foto dipotong bulat sebagai "planet" di peta perjalanan, foto Gargantua samar di belakang judul |
| Foto beranotasi | Penanda bernomor berdenyut + label, kartu penjelasan; berganti sendiri tiap 5 s sampai disentuh |
| Lapisan grafis | Copper: lingkaran dan panah "bawah = menjauhi sumbu". Millar: garis ukur 1,2 km dan panah 125 m/s |
| Tetap dari v2 | Angka menghitung naik, kalkulator radius Copper dan dilatasi Millar, fitur berikon, strip tombol |

Posisi penanda ditulis dalam piksel foto asli (`SPOTS`), jadi bila foto diganti, koordinatnya ikut diubah.
Saat dipasang ke `index.html`, foto sebaiknya pindah ke `experiences/<id>/menu.webp`.

## Poles foto menu (`tools/poles_foto_menu.py`)
Foto asli disimpan di `docs/app/menu/asli/`; hasil poles menimpa `docs/app/menu/<nama>.webp` (ukuran sama, penanda tetap pas).
Hanya olahan nada dan warna per piksel, tidak ada objek yang diubah.

| Langkah | Efek |
| --- | --- |
| Clarity | Kontras lokal di nada tengah (radius 22-26 px) |
| Penajaman | Radius 1 px, berambang agar artefak kompresi tidak ikut |
| Titik hitam + kurva S | Hitam lebih dalam; Millar: nada terang dilindungi agar cincin di langit tetap terpisah |
| Split toning + saturasi | Copper hijau kaya dan highlight keemasan; Gargantua emas dalam, bayangan teal; Millar dingin dan suram |
| Bloom, vinyet, bahu highlight, butiran | Kesan sinematik tanpa highlight terpotong (0,00% di ketiga foto) |

Ubah angka di `PRESET` lalu jalankan `python tools/poles_foto_menu.py [nama]`. Di prototipe v3 ada tombol "Lihat foto asli" untuk membandingkan.

## Gaya foto: Poles / Realistis / Kartun / Asli
- Versi Realistis dan Kartun dibuat pemilik di generator AI luar memakai prompt di `docs/app/prompt-foto-menu.md` (img2img dari `docs/app/menu/asli/`, komposisi wajib sama).
- Hasil disimpan di `docs/app/menu/real/` dan `docs/app/menu/kartun/` dengan nama `cooper` / `gargantua` / `millar` (.webp).
- Di v3, pemilih gaya ada di pojok kiri atas tiap foto. Gaya yang filenya belum ada nonaktif; foto yang belum punya file untuk gaya terpilih tetap memakai versi Poles. Pilihan diingat di localStorage `interstellia.menuStyle`.
