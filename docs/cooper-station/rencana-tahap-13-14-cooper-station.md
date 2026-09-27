# Rencana Tahap 13-14 Copper Corn Station

Status: disetujui pemilik. Tahap 13 selesai (13a-13d), 14a selesai. Berikutnya 14b. Titik awal: tahap 12d+ dan M1-M4 (menu, bahasa). Semua fitur lama dipertahankan.

## Ringkasan

- Tahap 13 (perbaikan dan navigasi): rel trem bersih dari tiang dan pohon, jembatan kaca di Skyway supaya luar angkasa langsung terlihat, jembatan jalan dan akuaduk sungai melintasi Skyway (mobil dan sungai tidak hilang lagi), peta M besar dan jelas.
- Tahap 14 (dunia dan visual): hutan lebat bertombol 0, rumput tinggi di bukit ala Breath of the Wild, interior ruangan di balik jendela gedung.
- Keputusan pemilik: Skyway dilintasi jembatan terbuka (bukan terowongan); hutan di pertanian tengah.

## Penyebab yang ditemukan

| Masukan | Penyebab |
| --- | --- |
| Tiang dan pohon di tengah rel trem | Lampu cincin struktur dipasang tiap 40 m mulai tepat dari garis rel (s = 0), jadi satu tiang per cincin berdiri di rel. Aturan jarak aman dari rel berbeda-beda antar bagian (kota, taman, pertanian, perabot), jadi sebagian pohon dan tiang lolos |
| Skyway tidak memperlihatkan luar (tombol 5 dan tur) | Titik lokasi 3 m dari tepi jendela dengan pandangan 40 derajat ke bawah: garis pandang jatuh ke lantai sekitar 2 m di depan, sebelum tepi kaca |
| Mobil dan sungai hilang di Skyway | Jendela Skyway adalah celah 30 m di tanah sepanjang 8 km. Jalan melingkar dan sungai berhenti di tepi celah; mobil lenyap lalu muncul lagi di seberang |
| Peta kecil | Peta sekarang kartu maksimal 420 px, tanpa penanda lokasi penting |

## Tahap 13: perbaikan dan navigasi

| No | Item | Rencana | Uji |
| --- | --- | --- | --- |
| 13a | Rel trem bersih | Satu aturan koridor rel (lebar peron + 1 m, sepanjang stasiun) dipakai semua penempat objek: lampu cincin, pohon, perabot kota, kafe dan sepeda, lampu jalan, tiang. Lampu cincin di garis rel dipindah ke kedua sisi rel | Skrip audit: nol benda dalam 2,5 m dari as rel selain rel, peron, halte, dan palang perlintasan |
| 13b | Skyway: jembatan kaca pandang | Jembatan pejalan kaki berlantai kaca melintang jendela (di Skyway kota dan satu di area taman), pagar kaca. Tombol 5 dan titik tur dipindah ke tengah jembatan, memandang ke bawah, sehingga bintang dan Saturnus melintas langsung di bawah kaki | Tombol 5 dan tur memperlihatkan luar angkasa; bisa berjalan melintas tanpa jatuh |
| 13c | Jembatan jalan dan akuaduk | Tiap jalan melingkar yang memotong Skyway mendapat jembatan 30 m: dek tipis, pagar kaca, rangka ramping supaya pandangan jendela tetap terbuka. Mobil melintas tanpa hilang (jalur jadi lingkaran utuh). Sungai menyeberang lewat akuaduk kaca: air terlihat mengalir di atas bintang | Uji lalu lintas lama tetap lulus; mobil melintasi Skyway; tidak ada tabrakan |
| 13d | Peta besar (M) | Hampir layar penuh, mendatar (sumbu 8 km ke samping, keliling ke bawah). Lapisan: zona, kota, ladang, sungai, jalan, rel dan halte, Skyway dan jembatan, cincin struktur. Penanda bernomor sesuai tombol 1-9 dan 0 (hutan), plus lift, terminal, air mancur, baseball, rumah Cooper. Posisi dan arah pemain, posisi trem langsung. Zoom (roda / cubit), geser (seret), klik penanda = pindah ke sana. Legenda dua bahasa | Peta terbuka, klik penanda memindah pemain, uji bahasa lulus |

### Hasil 13a (selesai)

| Temuan audit | Perbaikan |
| --- | --- |
| Tiang lampu cincin 9 m tepat di as rel di tiap cincin struktur (7 tiang, za 1.008 sampai 7.008) beserta kepala lampunya | Tiang di as rel dipindah 9 m ke sisi tanpa peron (daftar posisi `RING_LAMP_S` dipakai bersama oleh tiang dan kepala lampu) |
| 3 pohon di atau dekat rel (za 3.930, 4.087, 7.120) dari penahan angin dan pinggir danau | Semua penanaman pohon lewat `tree()` menolak koridor rel 8 m (`inTramCorridor`). Urutan angka acak dijaga, jadi kota dan ladang tidak bergeser (uji suasana: 33 kafe, 946 bohlam, 50 bendera, sama seperti sebelumnya) |

Uji `tools/uji_rel_trem.py`: 0 benda di koridor rel (dalam 2,4 m dari as rel, lebih tinggi dari 0,3 m), 0 pohon dalam 7 m, 0 collider di atas rel.

### Hasil 13b dan 13c (selesai)

| Item | Hasil |
| --- | --- |
| Temuan tambahan | Jendela Skyway ternyata sudah lantai kaca yang bisa diinjak (tanpa penghalang). Jadi jembatan pejalan kaki terpisah tidak diperlukan; masalahnya hanya titik lokasi yang berdiri di lantai beton dan memandang landai |
| Tombol 5 dan tur | Pemain berdiri di atas kaca (2 m dari garis tengah jendela, za 1.400), memandang ke bawah 62 derajat: bintang dan Saturnus langsung terlihat di bawah kaki |
| Jembatan jalan | 8 jalan melingkar kota (za 250, 500, 750, 1.250, 1.500, 1.750, 2.250, 2.500) kini melintasi promenade dan jendela. Dek aspal dengan marka tengah, tepi beton, pagar kaca dan pegangan baja; dibuat per ruas 5 m mengikuti lengkung silinder. Pohon promenade yang jatuh di jalan baru dibuang (urutan acak dijaga) |
| Mobil | Lajur melingkar kini satu keliling penuh (6.283 m); mobil melintasi jembatan, tidak hilang lagi. Terukur: 80 lintasan dalam 60 s simulasi. Uji lalu lintas 30 menit tetap lulus (0 tumpang tindih, 0 konflik di simpang) |
| Akuaduk sungai | Sungai memotong jendela di za sekitar 2.382. Air tembus pandang dengan alur mengalir searah keliling di atas bintang, dinding kaca dan rangka tepi |

Uji `tools/uji_skyway.py`.

### Hasil 13d (selesai)

| Item | Hasil |
| --- | --- |
| Ukuran | Hampir layar penuh (sebelumnya kartu 340 px). Ponsel: legenda pindah ke bawah |
| Orientasi | Mendatar: kiri-kanan = sumbu 8 km, atas-bawah = keliling. Rel trem di tengah, Skyway di tepi atas dan bawah; geser atas-bawah berulang tanpa ujung (silinder) |
| Isi | Latar tanah dan rumah (1 px = 2 m), rel dan halte (nama saat zoom), trem langsung, zona, Skyway dengan jembatan dan akuaduk, pemain berupa panah arah, skala 1 km |
| Penanda | 10 lokasi bernomor sesuai tombol: 1-9 dan L (lift). Tombol 0 (hutan) ditambah di 14a |
| Kendali | Roda atau cubit = zoom (1-10x), seret = geser, tombol + - dan "Posisi saya", klik penanda atau nama di legenda = pindah ke sana (peta tertutup). Keyboard: M atau Esc tutup, + - zoom |
| Bahasa | Semua teks peta dan legenda dua bahasa |

Uji `tools/uji_peta.py`.

## Tahap 14: dunia dan visual

| No | Item | Rencana | Uji |
| --- | --- | --- | --- |
| 14a | Hutan lebat | Blok hutan sekitar 600 x 450 m di pertanian tengah (za sekitar 4.300-4.900), beberapa ladang diganti. Pohon tinggi 22-35 m (pinus, ek, birch, elm) berjarak 6-9 m, semak dan pakis di bawah, tanah gelap berserasah, kabut tipis, berkas cahaya matahari di sela pohon. Tombol 0 (lokasi baru) dan masuk tur sinematik. Kepadatan per preset (Hemat lebih jarang) | FPS di GTX 1060 dan M1, jumlah pohon per preset |
| 14b | Rumput tinggi di bukit | Padang rumput bukit mendapat rumput setinggi 0,6-1,1 m, rapat, gelap di pangkal dan terang di ujung, berkilau saat searah matahari. Gelombang angin besar terlihat berjalan di atas padang (mengikuti angin global), rumput menunduk di sekitar pemain. Di kejauhan tanah meniru warna dan gelombang yang sama, jadi tidak ada batas tajam. Radius per preset | Tidak ada titik NaN (aturan GPU), FPS per preset |
| 14c | Interior jendela | Dari luar, tiap jendela memperlihatkan ruangan dengan kedalaman (lantai, plafon, dinding, perabot sederhana, tirai di sebagian jendela) yang ikut bergeser saat kamera bergerak (interior mapping). Malam hari sebagian ruangan menyala. Hanya untuk gedung dekat; gedung jauh tetap seperti sekarang. Mati di preset Hemat | Tidak ada NaN, tampilan siang dan malam, FPS |


### Hasil 14a (selesai)

| Item | Hasil |
| --- | --- |
| Lokasi | Blok pertanian s 2.425-2.892, za 4.260-4.940 (sekitar 470 x 680 m), antara jalan tanah k = 10 dan k = 12. Blok rencana awal (k = 8) ternyata berisi bukit dan danau, jadi dipilih blok sebelahnya yang bersih (0 rumah, 0 bukit, 0 air, dicek dengan pindai). Tata letak kota dan ladang lain tidak bergeser |
| Pohon | 5.222 pohon setinggi 22-35 m: pinus 2.400, elm 1.024, ek 980, birch 818. Jarak sekitar 7 m, 10% sel dibiarkan kosong (celah cahaya), batang ber-collider. Ikut suasana daun (Campur/Gugur) seperti pohon lain |
| Lantai hutan | Tanah gelap berserasah, jalan setapak tanah berkelok membelah hutan dari ujung ke ujung. 27.634 posisi semak dan pakis (kartu silang bergoyang angin); yang digambar hanya di sekitar pemain: Ultra 60 m, Hemat tidak ada. Ladang di dalam blok tidak ditanami dan tidak didatangi mesin ladang |
| Suasana | Di dalam hutan kabut lebih rapat dan kehijauan, kicau burung lebih sering (berubah halus saat masuk dan keluar) |
| Akses | Tombol 0 (berdiri di jalan setapak tengah hutan), tombol "0 Hutan lebat" di tab Lokasi, penanda 0 di peta, baris bantuan. Tur sinematik mendapat titik ke-11 "Hutan lebat": di pucuk pohon 30 m gravitasi 0,97 g |
| Biaya | Pohon hutan memakai mesh penuh hanya dalam radius per preset (Ultra 70 m sampai Hemat 25 m), di luar itu impostor. Terukur di tengah hutan: Ultra 256 pohon mesh penuh, 4,06 juta segitiga (titik awal kota: 3,80 juta); Hemat 28 pohon, 1,37 juta segitiga (kota: 1,88 juta) |
| Muat | Sekitar 4,1 s di sandbox; bobot garis progres diukur ulang |

Uji `tools/uji_hutan.py`. Uji lama tetap lulus (suasana, rel, bahasa, peta 11 penanda, ladang/foto/tur 11 titik, pohon, Skyway).

## Urutan kerja

| Urutan | Sub-tahap | Alasan |
| --- | --- | --- |
| 1 | 13a | Kecil, memperbaiki bug yang terlihat |
| 2 | 13b + 13c | Satu area (Skyway), jembatan memakai bahan dan aturan yang sama |
| 3 | 13d | Peta menampilkan jembatan baru dan disiapkan untuk penanda hutan |
| 4 | 14a | Lokasi baru (tombol 0) |
| 5 | 14b | Rumput bukit |
| 6 | 14c | Paling berat di shader, dikerjakan terakhir |

Tiap sub-tahap: commit dan push sendiri, uji muat dan uji lama tetap lulus, pemilik mengecek visual dan FPS (GTX 1060 dan MacBook M1 preset Hemat).

## Catatan dan risiko

- Hutan lebat dan rumput tinggi paling berpotensi menurunkan FPS; keduanya diatur per preset dan ikut turun otomatis bila FPS di bawah 30.
- Shader baru (rumput, interior, kaca) mengikuti aturan GPU M1: tanpa normalisasi vektor nol, tanpa pangkat bilangan negatif, semua geometri punya normal. Sandbox uji tidak memperlihatkan NaN, jadi pengecekan akhir di M1.
- Jembatan dan akuaduk dibuat melengkung mengikuti lantai silinder (pelajaran dari pagar baseball).
- Semua teks baru dua bahasa (Indonesia dan English).
- B7 (interior jendela) dari daftar cadangan tahap 12 dipindah ke 14c.
