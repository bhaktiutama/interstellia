# Prototipe Low Poly: Millar's World

Per 29 September 2026 · Status: prototipe cepat (mockup), bukan M1

## Ringkasan

- Halaman `experiences/millar/index.html`: langit low poly dengan Gargantua, laut dangkal bersegi, dasar laut, dan gelombang 1.200 m yang datang dari cakrawala.
- Tujuan: melihat skala, warna, dan kesan gelombang sebelum M1 dikerjakan. Belum ada shuttle, audio, misi, preset, atau shader lensa asli.
- Semua angka yang bisa diatur ada di `CONFIG` (satu tempat).

## Isi

| Bagian | Cara dibuat |
| --- | --- |
| Langit | Kubah ikosahedron bersegi (1.280 segi), warna per segi: zenit abu gelap, cakrawala abu pucat, cahaya hangat di sekitar Gargantua. Scene terpisah, digambar lebih dulu |
| Gargantua | Bayangan hitam 22 sisi (radius 9 derajat), cincin foton, cincin terbelokkan (citra belakang piringan), piringan akresi hampir tegak dibelah dua (belakang sebelum bayangan, depan sesudahnya), sisi kiri lebih terang (Doppler). Ketinggian 22 derajat, 28 derajat dari arah datang gelombang |
| Goyangan planet | Langit dan arah cahaya bergoyang 0,35 derajat, naik sampai 1,75 derajat saat gelombang mendekat (periode 40 s) |
| Laut | Dekat: grid persegi 2 m (titik digeser acak tetap, jadi segitiga tidak seragam) dipotong lingkaran 200 m. Jauh: cincin polar 196 m sampai 270 km. Riak di bawah 10 cm (habis sebelum 190 m), air surut 0,9 m di depan gelombang, bening di dekat (dasar laut terlihat), kilau Gargantua di air |
| Dasar laut | Grid persegi 640 m, sel 2,5 m, digeser per sel (tidak berubah bentuk saat berjalan). Kedalaman sekitar 0,1-1,4 m, beberapa gosong pasir muncul di atas air. Warna per segitiga: pasir, batu, petak ganggang; lebih gelap saat basah |
| Gelombang | Pita 30 x 221 titik: profil tetap (muka curam 350 m, bahu 600 m, punggung 5 km), puncak condong ke depan, buih di puncak, semburan 220-280 m. Muka melengkung ribuan meter sepanjang ratusan km, tinggi berubah 82-100% |
| Lengkung planet | Semua permukaan turun d²/(2R), R = 8.282 km: cakrawala 5,3 km dari mata, puncak gelombang muncul dari balik cakrawala |
| Pemain | Jalan 1,5 m/s, lari 4,2 m/s, diperlambat kedalaman air, gravitasi 12,75 m/s², lompat 0,385 m (77%) |
| Tersapu | Layar memutih, kembali ke titik awal, gelombang dianggap lewat 50 km: 400 s waktu planet = 0,78 tahun di luar |
| HUD | Dua jam (planet, di luar), gravitasi, kedalaman, jarak dan waktu tiba gelombang (plus tahun di luar), goyangan, tampilan, kecepatan waktu, FPS; dua bahasa |

## Angka gelombang di prototipe

| Item | Nilai | Catatan |
| --- | --- | --- |
| Jarak awal | 30 km | Supaya langsung terlihat; tiba dalam 4 menit |
| Gelombang berikutnya | muncul 150 km | Setelah gelombang lewat 60 km di belakang pemain; 20 menit sampai tiba |
| Kecepatan | 125 m/s | Dari konsep |
| Tombol G | gelombang ke 20 km | Tiba dalam 2 menit 40 s |
| Tombol Z | waktu 1x / 5x / 20x / 60x | Mempercepat gelombang, riak, goyangan, dan jam |

## Tombol

| Tombol | Fungsi |
| --- | --- |
| Klik | Kunci mouse (atau seret untuk menoleh) |
| W A S D, Shift, Space | Jalan, lari, lompat |
| V | Tampilan: jalan kaki / drone 60 m / tinggi 1,5 km |
| G | Panggil gelombang (20 km) |
| Z | Kecepatan waktu |
| R | Kembali ke titik awal |
| H | Sembunyikan HUD |

## Keterbatasan

- Gargantua di langit adalah susunan poligon, bukan lensa gravitasi. Porting shader Gargantua ke cubemap tetap rencana M1.
- Segitiga dekat berukuran 2-2,5 m: dari mata 1,7 m terlihat besar (memang gaya low poly). Belum ada cipratan atau riak langkah.
- Tersapu hanya dicek di titik pemain; condong puncak tidak dihitung di JS.
- Diuji di sandbox tanpa GPU (SwiftShader): hanya dicek termuat tanpa error. Tampilan dan FPS perlu dicek di GTX 1060 dan M1.
