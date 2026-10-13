# Rencana: Tur sinematik Y Copper Corn Station versi 2 (fly demo)

## Revisi v2.3: masukan uji Bhakti (selesai, menunggu uji visual)

Tetap tanpa mengubah fungsi lain.

| Titik | Masukan | Penyebab | Perubahan | Hasil uji |
| --- | --- | --- | --- | --- |
| Pembuka luar | Pucat, terlalu berkabut | Adaptasi mata menaikkan eksposur karena layar luar hampir hitam (sampai 2,2x); bloom 0,5 menambah pendar seperti kabut. Sunrays, AO, kabut sudah mati di kamera luar | Selama titik kamera luar: adaptasi mata mati (seperti tombol panel Grafik) dan bloom 0,25; dikembalikan sesudahnya | Adaptasi mati dan bloom 0,25 di kamera luar, kembali normal setelah tur |
| Lempar bola | 80 m/s, kamera di kanan belakang bola, ikut lalu makin tertinggal | Dulu 80 km/h | 80 m/s, 10 derajat, melawan putaran; kamera di jalur bola yang sama, 3 m ke kanan dan 1 m ke atas, selalu menghadap bola, jarak tertinggal tumbuh 5 m sampai 60 m saat bola menyentuh tanah | Bola melayang 46,5 s, jatuh 2.885 m keliling (sisi seberang silinder); kamera 4 m lalu 60 m dari bola, meleset 0,0 derajat |
| Burung | Natural, tidak terlalu tinggi | Formasi V terbang 150-250 m | Ikut kawanan burung biasa (18-45 m di atas tanah di luar kota), lalu turun ke tanah | Mulai 24 m dari kawanan, berakhir 66 m, menengadah 26 derajat |
| Gerhana | Dari ladang jagung setinggi pemain | Kamera dekat sumbu | Tepi ladang jagung dekat rumah Cooper, mata 1,7 m, menghadap end cap B, menengadah 18 derajat | Setinggi mata, cahaya Matahari turun ke 0 |
| Genangan | Tertutup pohon | Kamera diam di trotoar | Berjalan 24 m di tepi dalam trotoar ke arah pusat kota, menoleh sedikit ke jalan | 24 m setinggi mata, basah 0,62, awan di jalan 0,27 |

Durasi tur 294 s (titik bola sekitar 50 s karena bola melayang 46,5 s).


## Revisi v2.2: masukan uji Bhakti (selesai, menunggu uji visual)

Tetap tanpa mengubah fungsi lain; hanya data dan alur titik tur.

| Titik | Masukan | Penyebab | Perubahan | Hasil uji |
| --- | --- | --- | --- | --- |
| Skyway | Saturnus tertutup palang abu-abu | Balok melintang jendela ada tiap 50 m (za kelipatan 50); kamera di za 1.400 tepat di atas balok | Maju ke za 1.425, tengah di antara dua balok | 25 m dari balok terdekat |
| Dek 175 m | Terlalu tinggi, pandangan tertutup pagar | Mata 3,4 m di atas lantai dek, 2,6 m dari pagar | Mata 1,7 m (tinggi manusia), berdiri 0,5 m dari pagar, menunduk 6 derajat | Mata tepat 1,7 m, 0,50 m dari pagar |
| Hutan | Jalan setinggi mata keluar hutan | Kamera diam | Berjalan 3 m/s selama 12 s di jalan setapak, dari 26 m di dalam hutan sampai 10 m di luar | 41 m, setinggi mata, dari dalam ke luar hutan |
| Burung | Ikut burung lalu turun ke tanah, tetap mengarah ke burung | Kamera hanya ikut di ketinggian | 6 s turun dari ketinggian formasi ke tanah sambil mengarah ke pemimpin formasi, 3 s berdiri di tanah menengadah; titik mendarat dicek bebas gedung dan air; titik dipindah ke setelah bukit (area ladang) | Mulai 38 m dari formasi, mendarat di tanah, menengadah 66 derajat, meleset 0,2 derajat |
| Lempar bola | Dari sudut pandang pemain, 80 km/h, 10 derajat, kamera ikut bola | Dua bola dari titik lain | Satu lemparan dari mata pemain di lapangan baseball, melawan putaran; kamera mengejar bola sampai jatuh | 35,1 m dalam 1,61 s (fisika game, dari tinggi tangan 1,5 m); kamera ikut 32 m |

Catatan bola: dengan 80 km/h dan 10 derajat bola tidak bisa sampai ke sisi seberang silinder. Untuk itu laju lempar harus mendekati laju lantai (sekitar 357 km/h); teks titik menjelaskan ini. Durasi total tur 249 s.


## Revisi v2.1: masukan uji Bhakti (selesai, menunggu uji visual)

Aturan: tidak mengubah fungsi apa pun (hujan, shader, genangan, burung, motor, bola). Tur hanya mengatur jam, laju jam, tutupan awan, waktu orbit, posisi dan arah kamera, motor, dan lemparan, yaitu keadaan yang juga bisa diatur pemain. Dua perubahan v2 di luar tur (pengaman label jam HUD, percepatan awan `WEATHER.fast`) dikembalikan ke kode asli.

| Masukan | Penyebab | Yang dilakukan tur |
| --- | --- | --- |
| Hujan tidak terlihat | Tetes hujan hanya jatuh di bawah awan tebal; kamera sungai v2 tidak di bawah awan | Lokasi titik hujan dipilih saat titik mulai: dari 25 titik tepi sungai, yang awannya paling tebal |
| Genangan tidak terlihat | Genangan penuh hanya di bawah awan; titik v2 malam cerah dan jam dipercepat (cepat kering) | Titik genangan tepat sesudah hujan reda, awan masih tebal (tutupan 0,75), jam berhenti, jalan kota di bawah awan, setinggi mata menghadap pusat kota |
| Kurang setinggi mata | Banyak titik tinggi | 10 titik setinggi mata (1,7 m): gravitasi, air mancur, lempar bola, Skyway, bukit, ladang, hutan, sungai, genangan, danau |
| Burung di awan | Formasi V di 150-250 m, jauh dari kamera | Kamera mengikuti formasi V 35 m di belakangnya |
| Gerhana dari dalam | Titik v2 di kamera luar | Titik dekat sumbu menghadap kaca end cap B saat malam; Matahari dan sinarnya padam |
| Motor dari luar kota | Belum ada | 27 s naik motor (fisika motor apa adanya, gas terus + sport) di jalan lingkar keliling za 500 (rute bus merah) dari distrik Galileo ke New York, melawan arah putaran. Revisi: dulu arteri searah sumbu, salah menurut Bhakti |
| Lempar bola | Belum ada | Dua bola 25 m/s 40 derajat: searah putaran dan melawan putaran, angka dari `landingOf()` |
| Diam terlalu lama | 7-8 s | 4-5 s |

| Hasil uji (sandbox) | Nilai |
| --- | --- |
| Titik, durasi | 22, 243 s |
| Hujan di sungai | `RAIN.k` 0,97, awan di atas kamera 0,28 (tetes jatuh bila > 0,12) |
| Genangan | basah minimal 0,59, hujan sudah berhenti (0,03), awan di jalan 0,46 |
| Burung | formasi V 38 m dari kamera |
| Motor | 1.120 m keliling, Galileo ke New York, lajur za 496,5, 144-150 km/h, terasa 0,33 g (melawan putaran), tanpa tabrakan |
| Bola | searah putaran 48,4 m / 2,35 s; melawan putaran 84,4 m / 4,94 s |
| Gerhana | `ECL.k` turun ke 0,00, kamera di dalam |


## Status: T1-T10 selesai, menunggu uji visual Bhakti

| Hasil | Nilai |
| --- | --- |
| Titik | 18 (10 lama + 6 baru + pembuka + penutup) |
| Durasi di uji | 228 s (sekitar 3 menit 48 detik) |
| Jam | 12:00 sampai 07:00 |
| Hujan di titik sungai | `RAIN.k` 0,99 |
| Genangan di trem malam | `RAIN.wet` minimal 0,83 |
| Gerhana | `ECL.k` turun ke 0,00 |
| Uji tur, uji bahasa | Lulus, tanpa error |

Perbedaan dari draf di bawah:

- Teks menara: draf "gravitasi 4% lebih ringan" salah. Gravitasi di puncak = (R - tinggi) / R, untuk menara sekitar 221 m sekitar 0,78 g (sekitar 22% lebih ringan). Teks kini menghitung angka dari `LANDMARK.h`; tinggi dek dari `DECK.h`; lama gerhana dan orbit dari `ECL.half` dan `T_ORB`.
- Penutup: tidak naik ke sumbu dulu. Dari danau langsung layar gelap, lalu kamera luar menjauh dari stasiun.
- Titik trem malam: posisi kamera dihitung saat titik dimulai, 140 m di depan trem searah jalannya, supaya trem datang ke arah kamera (bila trem sedang di luar kota, posisi dijepit ke kota dan trem bisa tidak terlihat).
- Uji `mesin ladang dekat pemain` (bagian 12d) sudah gagal sebelum perubahan ini (dicek di commit sebelumnya), tidak terkait tur.
- `tools/qc_load.py` tidak dijalankan (tidak bisa memakai Chromium sandbox); error halaman diperiksa lewat uji tur dan uji bahasa, ditambah uji asap semua 18 titik di loop render sungguhan.

## Konteks

Tur Y (`TOUR`, `tourKeys()`, `stepTour()` di `experiences/cooper-station/index.html` sekitar baris 15004-15107) sekarang punya 10 titik dengan teks panjang, jam tetap (malam dipindah ke 09:30), cuaca tidak diatur, dan mulai di dalam stasiun. Bhakti minta:

- 10 titik lama tetap, disisipi tempat ikonik baru
- teks tiap titik dipersingkat
- jam 24 jam dipercepat: mulai siang, berakhir pagi berikutnya
- cuaca berurutan: terang, mendung, hujan, terang lagi
- detail terlihat: burung, genangan bekas hujan, gerhana Saturnus
- pembuka: dari jauh mengitari stasiun lalu masuk ke kota; penutup: meninggalkan kota menjauh
- total sekitar 4 menit (jawaban Bhakti)

## Ringkasan pendekatan

| Bagian | Cara |
| --- | --- |
| Urutan | 18 titik: pembuka luar + 10 lama + 6 baru + penutup luar |
| Waktu | Tiap titik punya `hr` (jam tujuan). Jam diinterpolasi linear selama titik; `clock.hourRate` diisi laju sebenarnya (jam/s) supaya sistem lain (lalu lintas, kering genangan, cuaca) ikut |
| Cuaca | Tiap titik punya `wx` ('cerah', 'berawan', 'mendung'); tur memaksa `WEATHER.mode`, transisi awan 3x lebih cepat saat tur |
| Genangan | `TOUR.wetMin` menahan `RAIN.wet` sampai titik genangan selesai (tanpa ini genangan kering sekitar 20 s nyata) |
| Gerhana | Titik luar khusus: `clock.orbit` digeser agar gerhana mulai 2 s setelah tiba, `orbitScale` 4 sementara, kamera di sisi berlawanan Saturnus |
| Pembuka / penutup | Kamera luar dengan jalur sendiri (jarak 40 km ke 700 m di dermaga dan sebaliknya), pergantian luar ke dalam lewat layar gelap 0,5 s |
| Pulihkan | Saat tur selesai: posisi, jam, laju jam, mode cuaca, `clock.orbit`, `orbitScale` dikembalikan |

## Daftar titik (durasi target sekitar 240 s)

Jam dan cuaca adalah tujuan di akhir titik. Teks final ID sekitar 1-2 kalimat, maks sekitar 140 karakter.

| # | Titik | Baru / lama | Jam | Cuaca | Detail yang dipamerkan | Teks singkat (draf) |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | Mendekat dari luar | baru (pembuka) | 12:00 | cerah | Stasiun berputar, Saturnus, masuk ke dermaga end cap A | Silinder 8 km mengorbit Saturnus, berputar sekali tiap 63,4 s. |
| 1 | Gravitasi dari putaran | lama | 12:20 | cerah | Turun dari sumbu ke tanah | Putaran memberi 1 g. Tanah melengkung naik di kiri dan kanan. |
| 2 | Ukuran stasiun | lama | 12:50 | cerah | Kawanan burung di bawah kamera | Radius 1 km, panjang 8 km. Tanah seberang 2 km di atas kepala. |
| 3 | Pusat New York, menara ikon 221 m | baru | 13:20 | cerah | Menara ikon, alun-alun (`SPOTS.nyc`) | Menara tertinggi stasiun. Di puncaknya gravitasi 4% lebih ringan. (angka diturunkan dari g = omega^2 r, dicek saat implementasi) |
| 4 | Air mancur Coriolis | lama | 13:50 | cerah | Merpati di plaza (kamera rendah) | Air naik lurus, mendarat {s10} m searah putaran: efek Coriolis. |
| 5 | Skyway | lama | 14:30 | berawan | Bintang dan Saturnus di bawah kaca | Di bawah kaca ini ruang hampa. Tepi silinder bergerak 99 m/s. |
| 6 | Dekat sumbu | lama | 15:10 | berawan | Awan dari atas | Dekat sumbu gravitasi mengecil: 100 m dari sumbu hanya 0,1 g. |
| 7 | Ladang gandum | lama | 16:00 | mendung | Mesin panen, langit gelap | Satu siklus tanam 96 jam: tumbuh, menguning, dipanen. |
| 8 | Hutan lebat | lama | 17:00 | mendung | Hujan mulai | Pohon 22-35 m. Di pucuknya gravitasi 3% lebih ringan. |
| 9 | Hujan miring di sungai | baru | 18:00 | mendung (hujan) | Hujan miring 8 derajat, jembatan `BRIDGES`, alur sungai | Hujan jatuh miring 8 derajat: Coriolis yang sama dengan air mancur. |
| 10 | Rumah Cooper | lama | 19:00 | berawan | Hujan reda, senja | Rumah tetap tegak ke sumbu dari segala arah. |
| 11 | Trem malam dan genangan | baru | 21:00 | cerah | Genangan memantulkan lampu (SSR), trem menyala, halo lampu | Genangan sisa hujan memantulkan lampu jalan dan trem. |
| 12 | Dek pandang malam | baru | 23:00 | cerah | Gedung malam bertingkat, lampu merah atap, kota di seberang | Dek 175 m. Lampu kota di seberang tergantung di atas kepala. |
| 13 | Dari luar: kerangka inersia | lama | 01:00 | cerah | Stasiun berputar | Dari luar tidak ada tarikan ke bawah; lantai yang membelokkan kita. |
| 14 | Gerhana Saturnus | baru | 02:00 | cerah | Saturnus menutup Matahari, cahaya tepi atmosfer, sinar padam | Saturnus menutup Matahari 2,8 jam tiap orbit 37,6 jam. |
| 15 | Dermaga despun | lama | 03:30 | cerah | Shuttle KS-07 | Dermaga tidak ikut berputar; shuttle sandar di sini. |
| 16 | Kabut pagi di danau | baru | 06:30 | cerah | Kabut pagi 5x, burung kembali (setelah 06:00), danau `SPOTS.lake` | Pagi: kabut tipis menempel tanah, burung kembali terbang. |
| 17 | Meninggalkan kota | baru (penutup) | 07:00 | cerah | Naik ke sumbu, keluar lewat dermaga, menjauh 40 km | Sampai jumpa di Copper Corn Station. |

Catatan urutan: titik lama tetap berurutan sama (1, 2, 4, 5, 6, 7, 8, 10, 13, 15); titik baru disisipkan. Burung aktif 06:00-18:30 dan tidak terbang saat hujan (`birdDay()`, `stepBirds()`), jadi titik burung ada di siang (2, 4) dan pagi (16).

## Perubahan kode (semua di `experiences/cooper-station/index.html`)

| Langkah | Isi | Fungsi / nama | Effort | Model | Thinking |
| --- | --- | --- | --- | --- | --- |
| T1 | Data titik baru: `tourKeys()` diperluas dengan field `hr`, `wx`, `wet`, `ext` jenis baru ('in', 'out', 'eclipse'); teks lama dipersingkat; lokasi baru dari `SPOTS.nyc`, `DECK`, `BRIDGES`, `TRAM.s`, `SPOTS.lake`, `LANDMARK` | `tourKeys()` | Medium | Sonnet 5.5 | medium |
| T2 | Jam dan cuaca terjadwal: `tourClock(K, u)` dipanggil di `stepTour()`; simpan dan pulihkan `clock.hour`, `hourRate`, `WEATHER.mode`, `clock.orbit`, `orbitScale` di `startTour()` / `stopTour()`; hapus pindah-ke-09:30 lama; jam mulai dipaksa 12:00 | `startTour()`, `stopTour()`, `stepTour()`, `tourNext()` | Medium | Sonnet 5.5 | medium |
| T3 | Pengaman HUD: `TIME_RATES.find(...)[1]` (baris sekitar 6745 dan 6903) error bila `hourRate` bukan nilai daftar; saat tur tampilkan "tur" | `updateTimeLabels()`, HUD jam | Low | Sonnet 5.5 | low |
| T4 | Transisi cuaca cepat saat tur (`maxStep` wdt/40 bila `TOUR.on`) di `updateClouds()`; `RAIN.wet = max(RAIN.wet, TOUR.wetMin)` di `updateRain()` | `updateClouds()`, `updateRain()` | Low | Sonnet 5.5 | low |
| T5 | Gerhana: saat titik 14 mulai, `clock.orbit` diatur agar `eclipseIn()` = 2 s, `orbitScale` 4; kamera luar diarahkan dari `saturnDirInertial()` (kamera di sisi lawan Saturnus, sedikit miring agar Saturnus di belakang stasiun), `ext.auto` mati | `stepTour()` cabang `ext: 'eclipse'` | Medium | Sonnet 5.5 | medium |
| T6 | Pembuka dan penutup luar: jalur kamera luar sendiri (yaw berputar setengah keliling, jarak 40 km -> 700 m di `EXT_FOCUS[4]` dermaga; penutup kebalikan), `ext.dist` / `ext.distT` / target diisi langsung tiap frame; pergantian luar <-> dalam lewat elemen baru `#tourFade` (opacity 0,5 s); bagian dalam pembuka mulai di sumbu dekat end cap A (h = R - 60) lalu turun ke titik 1; penutup naik ke sumbu dulu | `stepTour()`, `toggleExterior()` (dipakai, tidak diubah), CSS `#tourFade` | Medium | Sonnet 5.5 | medium |
| T7 | Tempo: `tourTravel()` durasi maks 9 -> 7 s, `hold` 5-7 s; total diukur di uji = 230-260 s | `tourTravel()` | Low | Sonnet 5.5 | low |
| T8 | Kamus: entri `I18N.en` untuk semua judul dan teks baru, entri teks lama yang diganti dihapus | `I18N.en` | Low | Haiku 4.5 | low |
| T9 | Uji: perbarui `tools/uji_ladang_foto_tur.py` (>= 18 titik, total 230-260 s, jam awal 12:00 dan akhir sekitar 07:00, `RAIN.k` > 0,5 di titik hujan, `RAIN.wet` > 0,5 di titik genangan, `ECL.k` < 0,5 di titik gerhana, segmen luar pembuka dan penutup, semua dipulihkan setelah tur, tanpa NaN, tidak melewati sumbu); jalankan juga `tools/uji_bahasa.py` dan `tools/qc_load.py` | `tools/uji_ladang_foto_tur.py` | Medium | Sonnet 5.5 | medium |
| T10 | Dokumen: baris riwayat tahap baru dan baris `TOUR` di peta kode `CLAUDE.md` | dokumen | Low | Haiku 4.5 | low |

Catatan: uji memanggil `stepTour(0.05)` tanpa `frame()`, jadi jam, cuaca terjadwal, dan gerhana harus diatur di dalam `stepTour()`, bukan hanya di loop render. `RAIN.k` dan `ECL.k` diperbarui di `updateRain()` / `updateEclipse()`; uji akan memanggil keduanya (sudah diekspor atau ditambahkan ke `window.__station`).

## Yang tidak berubah

- Fitur lain di luar tur, tombol (Y, Esc, H, U saat tur), panel `labTour` / `btnTour`, dan `#tourCap`.
- Posisi pemain dikembalikan seperti sekarang; tambahan: jam, cuaca, orbit juga dikembalikan.

## Verifikasi

1. `python tools/uji_ladang_foto_tur.py` (daftar cek T9) lulus.
2. `python tools/uji_bahasa.py` lulus (kamus English lengkap).
3. `python tools/qc_load.py` tanpa error.
4. Bhakti menguji visual dan FPS di GTX 1060 dan M1: urutan cuaca, genangan malam, burung, gerhana, transisi luar-dalam (sandbox SwiftShader tidak menampakkan NaN).

## Risiko dan catatan

| Risiko | Penanganan |
| --- | --- |
| Pergantian kamera luar (kerangka inersia) ke dalam (berputar) terlihat melompat | Layar gelap 0,5 s menutupi pergantian |
| 4 menit untuk 18 titik cukup padat (rata-rata 13 s per titik) | Teks maks sekitar 140 karakter; bila terlalu cepat, hold dinaikkan ke 8 s (total sekitar 5 menit) |
| Genangan ditahan lebih lama dari fisika kering normal (0,7 jam stasiun) | Hanya saat tur, disebut di dokumen |
| Angka baru di teks (menara 221 m, gerhana 2,8 jam) | Diturunkan dari `CONFIG` / `ECL` / `LANDMARK.h` saat implementasi, bukan ditulis tetap bila bisa dihitung |
