# Rencana Tahap 12: Copper Corn Station

Status: 12a selesai (lihat bagian 12a). 12b selesai (lihat `rencana-tahap-12b-cooper-station.md`). 12c selesai (lihat bagian 12c). 12d selesai (lihat bagian 12d). Tahap 12 selesai; sisa ada di Cadangan. Titik awal = tahap 11d (artifact versi 24). Semua yang sudah ada tetap dipertahankan.

## Ringkasan

- Kekurangan terbesar sekarang adalah kehidupan: kota detail tapi sepi (tidak ada orang, burung, aktivitas ladang).
- Prioritas 1: rapikan alur spaceport yang masih terputus (terminal belum tersambung ke lift dan pesawat).
- Prioritas 2: kota hidup (pejalan kaki, lampu lalu lintas sungguhan, burung). Prioritas 3: hujan dengan fisika Coriolis.

## Kondisi sekarang (titik awal)

| Area | Sudah ada | Kekurangan |
| --- | --- | --- |
| Spaceport | Terminal kaca, lift ke hub, kapsul terowongan 766 m, dermaga despun 4 berth, shuttle KS-07 bisa diterbangkan | Terminal tidak punya gerbang ke lift/pesawat, pintu kaca sulit dikenali, pesawat tanpa suara, tidak ada panduan sandar visual |
| Lalu lintas | 3.301 mobil GPU, lampu lalu lintas kuning berkedip | Mobil tidak berhenti di simpang |
| Kota | Gedung, perabot jalan, taman, halte | Tidak ada pejalan kaki |
| Cuaca | Cerah, berawan, mendung, sunrays | Tidak ada hujan, angin tidak mengikuti cuaca |
| Alam | Pohon, rumput, jagung, gandum, sungai, danau | Tidak ada burung, ladang statis |

## 12a. Merapikan spaceport

| No | Item | Rencana | Biaya |
| --- | --- | --- | --- |
| A1 | Gerbang keberangkatan | Gerbang di sisi utara terminal, E = naik lift ke hub lalu terowongan lalu kokpit (bisa dilewati otomatis). Papan arah "Ke lift dermaga" dan "Keluar", bingkai pintu berwarna | Rendah |
| A1b | Cek kolisi pintu terminal | Pastikan pintu selatan (12 m) dan barat (10 m) bisa dilewati | Rendah |
| A2 | Suara shuttle | Dengung mesin utama sesuai dorongan, desis RCS, bunyi penjepit saat sandar/lepas, dengung kokpit | Rendah |
| A3 | Panduan sandar | Kotak target di berth, garis arah, kecepatan relatif dan jarak di layar kokpit | Rendah |

### Hasil 12a (selesai)

| No | Status | Yang dikerjakan |
| --- | --- | --- |
| A1 | Selesai | Gerbang B1 (bingkai jingga, pintu geser tertutup, lantai tunggu) di tengah dinding utara, di ujung lorong antar-bangku. E di depan gerbang = lift naik ke hub, kapsul terowongan, lalu kokpit KS-07, semua otomatis 5x (sekitar 19 s waktu simulasi). E lagi selama perjalanan = langsung ke kokpit. Papan: "GERBANG B1 · KE LIFT DERMAGA" di atas gerbang, papan gantung di tengah aula dan dekat pintu barat, "KELUAR · KOTA" / "KELUAR · HALTE TREM" di dalam, "MASUK · TERMINAL" di luar. Bingkai pintu hijau di pintu selatan dan barat. Papan keberangkatan KS-07: "SIAP · GERBANG B1" |
| A1b | Selesai, ada bug | Pintu selatan ternyata tidak bisa dilewati sama sekali: hanggar lama dari generator plaza (s 120,8 m, za 205 m, sekitar 107 x 53 m) berada di dalam terminal, lengkap dengan kolisi. Hanggar itu kini dilewati (urutan acak kota tetap sama). Tiang di tengah pintu selatan, pintu barat, dan gerbang dihapus. Celah kaca kini sama persis dengan celah kolisi (dulu kaca terbuka di z -7..3 di pintu barat, kolisi di -5..5) |
| A2 | Selesai | Bus suara shuttle sendiri (tetap terdengar di pesawat): gemuruh mesin utama mengikuti dorongan (nada naik saat boost), desis RCS saat geser, guling, mundur, rem, dan memutar dengan mouse, dengung avionik dan kipas di kokpit (mati di kamera belakang), bunyi penjepit saat lepas sandar (satu hentakan + desis udara) dan saat sandar (dua penjepit) |
| A3 | Selesai | Kotak garis seukuran shuttle di berth 1 dan garis putus-putus dari kapal ke berth, tampil saat terbang. Hijau berkedip = E sandar otomatis bisa dipakai (jarak < 400 m, kecepatan < 30 m/s), jingga = belum. Layar kokpit diperbarui 10 kali per detik: jarak, kecepatan, kecepatan mendekat, kecepatan geser, jarak ke stasiun, status (E SANDAR / KURANGI V / REM), batang kecepatan dengan tanda 30 m/s, dan penunjuk arah berth (tengah = tepat di depan hidung, merah = di belakang). Prompt layar juga menampilkan kecepatan mendekat |

Uji otomatis: `tools/uji_spaceport.py` (pintu, gerbang, urutan lift > kapsul > kokpit, lepas sandar, sandar otomatis). FPS dan kesan visual belum diuji di GTX 1060 dan M1.

## 12b. Kota hidup

Rencana detail (diperluas: perlintasan trem, pohon beragam, daun kuning, suasana): `rencana-tahap-12b-cooper-station.md`.

| No | Item | Rencana | Biaya |
| --- | --- | --- | --- |
| B1 | Pejalan kaki | Orang low-poly berjalan di trotoar, taman, terminal, halte; sebagian duduk di bangku. Instancing GPU (1 draw call), animasi langkah di shader, LOD radius 300 m. Kepadatan mengikuti kelas kota dan jam | Sedang-tinggi |
| A4 | Lampu lalu lintas sungguhan | Siklus merah-kuning-hijau per simpang; mobil melambat dan berhenti (dihitung di GPU dari fase lampu, tanpa beban CPU) | Sedang |
| B3 | Burung | Kawanan berkelompok (boids sederhana) di taman dan ladang, pulang saat senja, suara kicau sudah ada | Rendah-sedang |

## 12c. Hujan dan fisika Coriolis

| No | Item | Rencana | Biaya |
| --- | --- | --- | --- |
| B2 | Hujan | Muncul saat mendung. Tetes jatuh dari ketinggian awan (sekitar 300 m) dan lintasannya melengkung karena Coriolis (meleset beberapa meter berlawanan arah putaran). Tanah basah mengilap, genangan, suara hujan | Sedang |
| B5 | Angin mengikuti cuaca | Pohon, jagung, rumput bergoyang lebih kuat saat mendung; suara angin naik | Rendah |
| B6 | Air mancur Coriolis | Air mancur di taman kota yang semburannya melengkung, dengan plakat penjelasan | Rendah |

### Hasil 12c (selesai)

| No | Status | Yang dikerjakan |
| --- | --- | --- |
| B2 | Selesai | Hujan saat mendung tebal (awan > 0,6, penuh pada 0,85). Fisika: tetes jatuh dengan kecepatan terminal sekitar 7 m/s di udara yang ikut berputar; Coriolis diimbangi hambatan udara sehingga tetes bergerak menyamping 2 omega vt^2 / g = 0,989 m/s melawan arah putaran. Hujan miring 8,0 derajat walau tanpa angin (plus angin). Rencana awal menyebut "meleset beberapa meter"; hitungan sebenarnya: dari awan 300 m tetes hanyut sekitar 40-45 m. Partikel garis di kotak 70 x 70 x 45 m sekitar kamera: Ultra 12.000, Tinggi 9.000, Sedang 6.000, Rendah 3.000, Hemat 1.500. Tanah basah (gelap, basah penuh sekitar 1 menit, kering sekitar 5 menit), genangan di aspal dan paving memantulkan warna langit. Suara hujan (teredam di dalam terminal, trem, lift). Tidak ada hujan di dalam terminal, trem, lift, hub, kapsul. Burung berteduh saat hujan |
| B5 | Selesai | Angin dasar naik dari 1,4 m/s (cerah) sampai 3,5 m/s (mendung penuh). Goyang rumput, jagung, dan tajuk ikut kuat; suara angin mengikuti hembusan (12b-2) |
| B6 | Selesai | Air mancur di plaza pusat kota terdekat dari titik awal (tombol 9). Semburan tengah 10 m/s setinggi 5,1 m mendarat 1,37 m searah putaran, 8 semburan kecil 6 m/s bergeser 0,30 m. Lintasan memakai rumus orde pertama (4/3) omega v^3 / g^2; dibandingkan hitungan eksak di kerangka inersia (1,352 m dan 0,292 m) selisihnya sekitar 1,5%. Plakat di depan kolam (E) menjelaskan Coriolis dan hujan miring |

Uji: `tools/uji_hujan.py` (7 cek). Waktu muat di sandbox sekitar 6,6 s.

### Revisi hujan (setelah uji pemilik)

| Masalah | Penyebab | Perbaikan |
| --- | --- | --- |
| Gerak tetes aneh, seperti zoom in/out ke arah kamera | Tetes yang lewat sangat dekat kamera ikut digambar (besar dan melesat), dan lebar garis membesar dengan jarak | Tetes dalam 1,2 m dari kamera tidak digambar, redup sampai 5 m; lebar garis tetap 1 cm |
| Garis tetes terlalu terang di malam hari | Warna tetes tetap (0,72), tidak ikut cahaya | Warna tetes diambil dari warna kabut (terang siang, gelap malam). Air mancur juga ikut pencahayaan |
| Hujan global | Hujan hanya bergantung tingkat mendung seluruh stasiun | Hujan hanya di bawah awan: tiap tetes membaca peta bayangan awan tepat di atasnya. Saat mendung penuh, awan menutupi sekitar 20% area, jadi hujan turun di bawah gugusan awan dan kering di celahnya. Tanah basah terutama di bawah awan, suara hujan mengikuti awan di atas pemain (dibaca tiap 0,4 s) |
| Genangan kurang nyata | Genangan hanya bercak abu-abu rata (lebih terang dari jalan) | Air genangan gelap, memantulkan langit kuat saat dilihat miring (Fresnel), memantulkan lampu jalan malam hari, riak cincin saat hujan, tepi lembut, mengecil saat mengering |
| Genangan tidak kering sampai besok | Pengeringan memakai waktu nyata 5 menit; dengan jam 1 menit = 1 jam itu sama dengan 5-15 jam stasiun | Basah dan kering mengikuti jam stasiun: kering sekitar 1-1,5 jam stasiun di siang hari (lebih lambat malam), saat waktu berhenti sekitar 5 menit nyata. Terukur: basah 1,0 menjadi 0,10 setelah 1 jam stasiun, 0,01 setelah 2 jam |
 Belum dibuat: percikan tetes di tanah, tirai hujan di kejauhan (diwakili kabut mendung yang sudah ada).

### Revisi setelah uji pemilik (baseball, layang-layang, kursor)

| Masalah | Penyebab | Perbaikan |
| --- | --- | --- |
| Pagar lapangan baseball tertimbun gundukan, papan skor setengah terpendam | Model lapangan dibangun sebagai bidang datar yang menyinggung tanah di home plate, padahal lantai stasiun melengkung naik u^2/2R: 5,7 m di pagar tengah (107 m), 6,5 m di papan skor (114 m) | Semua bagian lapangan dipindah ke permukaan silinder dan dimiringkan mengikuti arah atas setempat; decal lapangan ditekuk per vertex. Terukur: pusat pagar 2,4 m tepat 1,2 m di atas tanah di seluruh busur |
| Dua kilau seperti komet di sekitar lapangan (ternyata layang-layang) | Geometri layang-layang tanpa atribut normal; shader cahaya stasiun menormalkan vektor nol, jadi NaN di M1, disebar bloom dan berkas sunrays | Normal dihitung; shader cahaya stasiun dijaga (normal nol memakai arah atas setempat). Pindai: 0 mesh bercahaya tanpa normal |
| Lapangan baseball sepi di siang hari | Belum ada pemain | Pertandingan 09.00-17.30 (tidak saat hujan): pitcher, catcher, wasit, pemukul, 7 pemain bertahan, pemain di dugout, 18 penonton di tribun. Siklus lempar; 30% dipukul: bola melambung ke outfield, pemain terdekat mengejar, pemukul lari ke base, pelari maju, bola dilempar balik. Memakai model pejalan kaki (tanpa draw call baru) |
| Harus menekan Esc untuk memakai panel kanan | Klik hanya mengunci kursor | Klik kiri saat kursor terkunci = kursor bebas; klik lagi di layar = kunci lagi. Esc tetap bisa |

## 12d. Ladang, foto, tur

| No | Item | Rencana | Biaya |
| --- | --- | --- | --- |
| B4 | Aktivitas ladang | Mesin panen dan traktor bergerak di petak, debu saat panen, warna tanaman berubah mengikuti siklus tanam | Sedang |
| C2 | Mode foto | Sembunyikan HUD, atur jam dan cuaca, fokus kamera, tombol simpan gambar | Rendah |
| C3 | Tur sinematik | Kamera otomatis berkeliling stasiun dengan teks penjelasan fisika (gravitasi buatan, Coriolis, despun) | Rendah-sedang |

### Hasil 12d (selesai)

| No | Status | Yang dikerjakan |
| --- | --- | --- |
| B4 | Selesai | Siklus tanam 96 jam stasiun (4 hari) per petak gandum, fase digeser per petak: tumbuh hijau (0-45%), menguning (45-72%), masak keemasan (72-82%), tunggul pucat (82-100%). Tinggi dan warna gandum 3D serta warna tanah ikut fase. Saat uji: 141 tumbuh, 78 menguning, 27 masak, 41 tunggul |
| B4 | Selesai | Mesin ladang: sampai 10 mesin di petak terdekat (radius 900 m, dipilih ulang tiap 3 s). Mesin panen (2,2 m/s) di gandum yang masak, traktor (3,0 m/s) membajak petak kosong dan kedelai muda. Pola bolak-balik lajur 8 m dengan belokan setengah lingkaran, debu di belakang (maks 400 partikel) terbawa angin. Bekerja 06.30-18.30, berhenti saat hujan. Desain mesin orisinal (putih, teal, jingga) |
| C2 | Selesai | Mode foto (F): HUD dan panel disembunyikan, panel kecil untuk jam, sudut pandang 15-100 derajat, jarak fokus 0,5-2.000 m, blur di luar fokus (kedalaman bidang 16 tap di shader komposit, bobot per tap agar tepi tajam tidak meleber), eksposur, hentikan waktu, cuaca (N). Enter atau Simpan = unduh PNG tanpa panel. Semua pengaturan kembali saat keluar. Bila efek layar Mati, blur menyalakan mode Sedang selama mode foto |
| C3 | Selesai | Tur sinematik (Y, Esc atau tombol Berhenti): 9 titik, sekitar 2 menit. Boulevard (gravitasi dari putaran), di atas kota (ukuran), air mancur (Coriolis), Skyway (bintang berputar), 100 m dari sumbu (g = omega2 x r, 0,1 g), ladang (siklus tanam), rumah Cooper, kamera luar (kerangka inersia), dermaga despun. Terbang melengkung antar titik, tidak melewati sumbu. Malam hari jam dipindah ke 09.30. Selesai atau berhenti = kembali ke posisi semula |

Uji: `tools/uji_ladang_foto_tur.py`. Belum dibuat: jejak panen di belakang mesin (petak berubah menjadi tunggul mengikuti fase, bukan mengikuti lintasan mesin).

## Cadangan (belum dijadwalkan)

| No | Item | Catatan | Biaya |
| --- | --- | --- | --- |
| B7 | Interior jendela gedung | Ruangan terlihat di balik kaca saat didekati (interior mapping) | Sedang |
| C1 | Kabin shuttle bisa dijelajahi | Melayang nol-g di kabin, palka ke kokpit | Sedang |
| C4 | Fisika orbit penerbangan | Gerak relatif dekat stasiun mengikuti persamaan Clohessy-Wiltshire, percepatan waktu untuk terbang ke cincin Saturnus | Tinggi |
| C5 | Simpan posisi dan pengaturan | Lanjut dari posisi terakhir saat dibuka lagi | Rendah |

## Urutan dan uji

| Urutan | Sub-tahap | Yang diuji |
| --- | --- | --- |
| 1 | 12a | Alur terminal ke pesawat, suara, panduan sandar |
| 2 | 12b | FPS dengan pejalan kaki di pusat kota (GTX 1060 dan M1) |
| 3 | 12c | Hujan saat mendung, FPS, tampilan tanah basah |
| 4 | 12d | Ladang, mode foto, tur |

## Catatan dan risiko

- B1 (pejalan kaki) dan B2 (hujan) paling berpotensi menurunkan FPS. Keduanya akan diatur per preset (Ultra sampai Rendah) dan ikut turun otomatis bila FPS di bawah 30.
- Angka kepadatan dan radius LOD masih rencana awal, disesuaikan setelah uji.
- C4 butuh sistem gerak pesawat baru; dijadwalkan terpisah.
