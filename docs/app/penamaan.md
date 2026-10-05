# Nama Aplikasi dan Experience

Status: final (keputusan pemilik proyek). Nama aplikasi diubah cukup di `APP` pada `index.html`, nama experience di `EXPERIENCES`.

Catatan: ini bukan nasihat hukum. Prinsipnya: logo, huruf judul, cuplikan gambar, musik, dan desain kendaraan film tidak dipakai. Selalu cantumkan "Proyek penggemar, tidak berafiliasi dengan studio film mana pun" (sudah ada di footer menu dan README).

## Ringkasan

- Nama aplikasi: **Interstellia**.
- Experience: **Copper Corn Station**, **Gargantua Black Hole**, **Millar's World** (rencana), **Penerbangan Kestrel** (rencana).
- Tidak ada pesawat bernama Ranger atau Ranzer; shuttle tetap **Kestrel KS-07** (nama dan desain orisinal).

## Keputusan nama

| Asli (film) | Nama di aplikasi | Dipakai di | Catatan |
| --- | --- | --- | --- |
| Interstellar | Interstellia | Nama aplikasi (menu utama, README), nama repo | Pilihan pemilik. Catatan risiko: plesetan yang hanya beda beberapa huruf dari judul lebih mudah dianggap mirip; usulan sebelumnya adalah Lazarus |
| Cooper Station | Copper Corn Station | Judul experience di menu, layar awal, judul tab, dokumen, papan skor baseball | Hanya teks. Folder dan URL tetap `experiences/cooper-station/`, nama variabel kode tetap |
| Miller's Planet | Millar's World | Kartu rencana di menu (id `millar`) | Sebelumnya "Planet Ombak" |
| Gargantua | Gargantua Black Hole | Judul experience di menu, judul halaman, panel | Gargantua dari novel Rabelais (1534), domain publik |
| Ranger | (tidak dipakai) | - | Shuttle tetap Kestrel KS-07 |
| Endurance | (tidak dipakai) | - | Tidak ada pesawat induk di aplikasi |
| - | GX-01 "Ambang" | Wahana misi Gargantua (`docs/gargantua/rencana-misi-lubang-hitam.md`) | Orisinal, dari blokout KS-07 v3 (`KESTREL.buildV3`); nama usulan, bisa diganti |

Nama yang tetap:

| Nama | Alasan |
| --- | --- |
| Rumah Cooper (lokasi tombol 1, tur, peta) dan plakat museumnya | Pilihan pemilik; "Cooper" nama umum |
| Penerbangan Kestrel, shuttle KS-07 | Orisinal |
| Nama variabel kode (`COOPER`, `cooperStation.preset` di localStorage) | Internal; mengganti kunci localStorage akan menghapus preset yang tersimpan |

## Yang tetap dihindari

- Logo, huruf judul, poster, cuplikan, dan musik film.
- Desain kendaraan film (pesawat induk berbentuk cincin, shuttle bersayap dari film).
- Rujukan ke film di dokumen hanya sebagai sumber konsep (daftar pustaka di `docs/cooper-station/konsep-cooper-station.md`).
