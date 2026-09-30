# Rencana M4 Millar's World: Pandangan Orbit dan Sinematik

Per 30 September 2026 · Status: selesai (lihat bagian "Status")

## Ringkasan

- Adegan orbit sendiri: planet air 8.282 km di dekat Gargantua, latar dari cubemap lensa Gargantua yang sudah ada (GCUBE), bintang, awan tebal, pinggir atmosfer, dan KS-07 v5 di orbit 350 km.
- Sinematik kedatangan 35 s sebelum misi (sekali per sesi, bisa dimatikan di layar mulai, bisa dilewati): jauh, orbit, masuk atmosfer, turun vertikal, mendarat di titik semula, lalu kendali diserahkan.
- Sinematik keberangkatan setelah misi berhasil: naik menembus awan, keluar atmosfer, lalu hasil misi tampil di atas pandangan jauh planet dan Gargantua.
- Pandangan orbit bisa dibuka dari panel kontrol (`) di mode Jelajah atau sebelum mulai.
- Menu utama: deskripsi kartu Millar diperbarui (turun dari orbit, radar, KS-07, gelombang).

## Urutan sinematik kedatangan

| Waktu | Adegan | Isi |
| --- | --- | --- |
| 0-7 s | Jauh | Planet sabit di depan piringan Gargantua, kamera mendekat dari 62.000 ke 44.000 km. Judul "Millar's World" dan "1 jam di sini = 7 tahun di luar" |
| 7-14 s | Orbit | KS-07 di 350 km di atas awan, kamera memutar di belakang-atas |
| 14-21 s | Masuk atmosfer | Hidung turun, ketinggian 350 ke 70 km, plasma jingga, guncangan, gemuruh, memutih |
| 21-35 s | Turun di dunia | Muncul dari putih 450 m di atas laut, 900 m di belakang titik pendaratan, melambat, melayang, turun vertikal dengan kipas menyala, semburan air, kaki turun di bawah 6 m. Kamera mengejar lalu berpindah ke mata pemain di titik awal |
| 35 s | Mulai | Wahana di titik semula, pemain di titik awal menghadap wahana, misi dan hitung mundur mulai |

Spasi, Enter, Esc, atau klik = lewati langsung ke permainan.

| Jauh | Orbit | Masuk atmosfer |
| --- | --- | --- |
| ![Jauh](m4/1-jauh.jpg) | ![Orbit](m4/2-orbit.jpg) | ![Masuk atmosfer](m4/3-masuk-atmosfer.jpg) |

| Turun | Mendarat | Hasil di orbit |
| --- | --- | --- |
| ![Turun](m4/4-turun.jpg) | ![Mendarat](m4/5-mendarat.jpg) | ![Hasil di orbit](m4/6-hasil-di-orbit.jpg) |

Gambar dari sandbox (SwiftShader, 960 x 540, preset Tinggi); warna dan kehalusan di GPU asli bisa berbeda.

## Urutan sinematik keberangkatan (misi berhasil)

| Waktu | Adegan | Isi |
| --- | --- | --- |
| 0-5 s | Dunia | Wahana naik tegak dari posisi saat lolos, kamera di bawah-belakang, memutih |
| 5-14 s | Keluar atmosfer | Ketinggian 60 ke 320 km, plasma memudar, nosel menyala. "Kembali ke orbit" |
| 14 s ke atas | Jauh | Planet dan Gargantua, layar hasil misi tampil di atasnya. Ulangi = misi baru tanpa sinematik kedatangan |

Gagal (tersapu atau tertelan) tetap langsung ke layar hasil seperti M3.

## Adegan orbit

| Bagian | Isi |
| --- | --- |
| Satuan | km, planet di titik asal (adegan terpisah dari dunia yang dalam meter; kedalaman logaritmik) |
| Latar | `GCUBE` (rgb = cahaya piringan, a = latar terlihat) + bintang prosedural di bagian latar yang terlihat. Arah Gargantua sama dengan di permukaan (`GDIR`) |
| Planet | Radius 8.282 km (1,3 x Bumi, massa jenis sama, lihat konsep). Laut gelap, awan tebal memanjang searah putaran dengan celah, kilau piringan di laut terbuka, terminator lembut, pinggir atmosfer kebiruan |
| Cahaya | Dari piringan akresi (arah `GDIR`, hangat) |
| Atmosfer | Selubung 140 km, kepadatan turun eksponensial (skala 38 km), terang di sisi siang dan saat menghadap cahaya; saat kamera di dalamnya menjadi langit |
| KS-07 | Model v5 yang sama (warna diubah ke linear untuk Lambert), lampu navigasi, nosel, plasma masuk atmosfer |

## Preset kualitas

| Preset | Oktaf awan planet | Lensa Gargantua (sudah ada) |
| --- | --- | --- |
| Ultra | 5 | 512, 320 langkah, hidup |
| Tinggi | 5 | 384, 240 langkah, hidup |
| Sedang | 4 | 384, 200 langkah |
| Rendah | 3 | sesuai preset |
| Hemat | 3 | sesuai preset |

Saat adegan orbit tampil, laut, riak, dan langit dunia tidak dirender (hanya cubemap Gargantua dan adegan orbit).

## Yang tidak dikerjakan

| Item | Alasan |
| --- | --- |
| Cahaya planet dibelokkan lensa Gargantua | Planet berada di depan Gargantua (dekat pengamat), jadi pembelokan cahaya planet sendiri kecil; bisa ditambah bila diminta |
| Gelombang raksasa terlihat dari orbit | Tertutup awan tebal di skala planet; bisa ditambah sebagai garis buih panjang bila diminta |

## Status

Selesai 30 September 2026.

Uji: `tools/uji_millar.py` kini 68 pemeriksaan, semua lulus, tanpa error halaman. Pemeriksaan M4 dan kokpit:

| Uji | Hasil |
| --- | --- |
| Adegan orbit 3 s, 10 s, 17 s | Tanpa nilai tidak valid, terang rata-rata HDR 0,262 / 0,173 / 0,225 |
| Kedatangan penuh (langkah tetap 1/30 s) | Mendarat 0,00 m dari titik semula, celah terendah ke titik mendarat 0,01 m (tidak menembus), kamera tidak pernah di bawah air, misi mulai, pemain di titik awal |
| Lewati (Spasi) | Sinematik berhenti, permainan dan misi mulai |
| Keberangkatan | Hasil tidak tampil di awal, tampil pada 14,1 s di atas adegan orbit tanpa nilai tidak valid; Ulangi = misi baru, tanpa sinematik, wahana kembali mendarat |
| Pandangan orbit dari panel | Ditolak saat misi berjalan, tampil di Jelajah, tombol apa saja kembali |
| Kokpit v5 | Kaca terpisah (36 titik) menghadap keluar 12/12, pelapis menghadap ke dalam 52/52, urutan segitiga badan 2.436/2.436, mata 0,27 m di bawah atap, pandangan lewat hidung 5,5 derajat; di pandangan kokpit layar tengah tergambar, tanpa nilai tidak valid |

Catatan: pemanggilan kunci kursor kini lewat `lockPointer()` (menangkap penolakan promise "Pointer is already locked" yang sempat muncul di uji).