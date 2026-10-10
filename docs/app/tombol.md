# Standar Tombol Interstellia

Per 30 September 2026. Patokan: Copper Corn Station. Fungsi yang sama memakai tombol yang sama di semua experience. Tombol yang di Copper dipakai untuk fungsi lain tidak dipakai untuk fungsi umum di experience lain.

## Tombol umum

| Tombol | Fungsi | Copper Corn Station | Millar's World | Gargantua |
| --- | --- | --- | --- | --- |
| W A S D | Berjalan | ya | ya | - (seret mouse) |
| Shift | Lari | ya | ya | - |
| Space | Lompat | ya | ya | jeda waktu (tidak ada lompat) |
| Q | Kualitas grafik (preset berikutnya) | ya | ya (dulu P) | ya (baru) |
| P | Efek layar: Tinggi / Sedang / Mati | ya | ya (baru) | ya (baru; dulu tangkap layar) |
| U | Suara nyala / mati | ya | ya (dulu M) | ya (G7, suara disintesis) |
| N | Cuaca / suasana | cuaca | suasana | - |
| Z | Kecepatan waktu | ya | ya | - |
| V | Tampilan / kamera luar | kamera luar | jalan kaki, drone, tinggi | wahana GX-01: kamera luar / kokpit (Esc keluar) |
| F | Kamera rangefinder (Rencana K; jenis terakhir diingat, panel kamera = Foto bebas lama: UI disembunyikan, Enter simpan PNG), F atau Esc keluar | ya | ya | ya (di luar misi atau saat jeda) |
| R | Kembali ke titik awal / atur ulang | ya | ya | atur ulang kamera |
| H | Sembunyikan HUD | ya | ya | ya |
| ` (backtick) | Panel kontrol | ya | ya (baru) | buka / lipat panel (baru) |
| ? (atau F1) | Bantuan | ya | ya (baru) | ya (baru) |
| 1 - 9, 0 | Lokasi / sudut pandang | lokasi | - | sudut pandang 1-4 |
| Esc | Lepas kursor, tutup bantuan, keluar mode foto | ya | ya | ya |

## Tombol lokal mode kamera rangefinder (Rencana K, `shared/camera.js`)

Hanya berlaku selama mode kamera aktif, sama di ketiga experience. Tombol khusus Copper (B, G, E, M, L, T, I, C) tidak dipakai. WASD, Shift, mouse, Z, Q, P, N, U tetap seperti biasa.

| Tombol | Fungsi |
| --- | --- |
| Klik kiri (kursor terkunci) / Enter | Rana foto, atau mulai / berhenti rekam video; rana B: tahan |
| Roda mouse | Cincin fokus (patch rangefinder di tengah) |
| Shift + roda, atau , dan . | Aperture |
| [ dan ] | Kecepatan rana (mode A / P pindah ke M) |
| - dan = | ISO; dengan Shift = kompensasi eksposur |
| Klik tengah | Autofocus ke patch tengah (lokal mode kamera) |
| M | Mode eksposur A / M / P (berganti; lokal mode kamera, tidak membuka peta / radar) |
| 1 - 6 | Lensa 21 / 28 / 35 / 50 / 75 / 90 mm |
| Tab | Foto / video |
| V | Jendela bidik optik / live view |
| Klik kanan tahan | Kunci eksposur (AE-L) |
| H | Sembunyikan HUD kamera |
| ` | Panel kamera (mode M / A / P, tripod, format, fps, bitrate, Foto bebas) |
| ? / F1 | Bantuan tombol kamera |
| F / Esc | Keluar |

## Tombol khusus Copper Corn Station (jangan dipakai untuk fungsi lain)

| Tombol | Fungsi |
| --- | --- |
| B · G | Lempar bola · jatuhkan bola |
| E | Aksi |
| M | Peta |
| L | Lift |
| T | Kecepatan orbit |
| I | Lompat ke gerhana |
| C | Motor |
| O · X | Jalan otomatis · turbo |
| K | Kualitas vegetasi |
| J | Musik (Copper: generatif / file sendiri / mati; Gargantua dan Millar: putar / jeda musik dari file sendiri, file dipilih di panel) |
| Y | Tur sinematik |

Pengecualian yang sudah ada: Millar G = panggil gelombang raksasa (aksi eksperimen, setara G jatuhkan bola di Copper). Millar M = radar misi (setara M peta di Copper), E = ambil barang / naik ke KS-07 / mendarat (setara E aksi di Copper). Di wahana Millar berlaku tombol pesawat Copper: W/S, A/D, R/F (Space juga naik), Shift, mouse, V kamera, E.

Sinematik (Millar M4): Spasi, Enter, Esc, atau klik = lewati. Pandangan orbit tidak memakai tombol baru, dibuka dari panel kontrol (`); tombol apa saja kembali. Di kokpit wahana (V) layar MFD tidak butuh tombol.

## Perubahan 30 September 2026

| Experience | Sebelum | Sesudah |
| --- | --- | --- |
| Millar | P grafik | Q grafik, P efek layar |
| Millar | M suara | U suara; M kini radar (setara peta di Copper, M3c) |
| Millar | B gerak kepala | Panel kontrol ` (seperti tab Gerak di Copper; B di Copper = lempar bola) |
| Millar | tidak ada | F mode foto, ` panel, ? / F1 bantuan |
| Gargantua | F layar penuh | Tombol "Layar penuh" di panel; F = mode foto |
| Gargantua | P tangkap layar | Enter di mode foto, atau tombol "Tangkap layar" di panel; P = efek layar |
| Gargantua | tidak ada | Q kualitas, ` panel, ? / F1 bantuan |

## Perubahan 4 Oktober 2026

| Experience | Sebelum | Sesudah |
| --- | --- | --- |
| Millar | tidak ada | Tubuh astronaut (Mati / Bayangan / Tampil) hanya di panel kontrol `, tanpa tombol (M6a) |
| Millar | tidak ada | Visor helm (Mati / Tipis / Penuh) hanya di panel kontrol `, tanpa tombol (M6d) |

## Aturan untuk experience baru

- Pakai tabel tombol umum di atas. Fungsi baru yang khusus experience: pilih tombol yang tidak ada di kedua tabel, atau letakkan di panel kontrol.
- Semua tombol dicantumkan di bantuan (?) dan teks tombol di layar, dua bahasa.
- Penerbangan (shuttle KS-07) mengikuti tombol pesawat di Copper: W/S, A/D, R/F, Z/C, mouse, Shift, X, V, E, L.
- Misi Gargantua (wahana GX-01, G2 + G3 + G4): W/S, A/D, R/F dorong, Shift mesin utama, seret mouse di kamera luar = kamera mengitari wahana (klik ganda = kembali ke belakang wahana), seret kanan (atau Ctrl + seret) dan seret di kokpit = arah hidung, X sikap (pusat / mendatar / searah lintasan / bebas), O autopilot susur piringan (O = otomatis, seperti jalan otomatis di Copper; selama autopilot R/F tinggi, W/S laju turun), E tembak suar (G4, setara E aksi di Copper), M pandangan relai dan diagram ruang-waktu (G4, setara M peta di Copper dan M radar di Millar), Z waktu, V tampilan (kamera luar, kokpit, relai 22 rs; di pandangan relai seret = relai mengitari lubang hitam, seret kanan = arah pandang, roda = zoom, klik ganda = awal), Space jeda, Esc akhiri, Enter terbang lagi; skenario tesseract (G5): selama membidik W/S sudut, A/D bidang orbit, Shift kasar, Enter kunci bidikan dan berangkat. U = suara (G7). Z/C guling tidak dipakai (Z = waktu, sesuai tabel umum). Selama misi F dan R = dorongan, jadi mode foto dan atur ulang kamera menunggu misi selesai.
