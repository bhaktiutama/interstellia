# Rencana Tahap 12b: Kota hidup dan suasana (Cooper Station)

Status: rencana detail, belum dikerjakan. Titik awal = tahap 12a (commit `6db47ef`). Semua yang sudah ada tetap dipertahankan.

## Ringkasan

- Tujuan: kota yang sekarang detail tapi sepi terasa hidup. Ada orang, lampu lalu lintas sungguhan, mobil yang berhenti untuk trem, burung, daun kuning yang tertiup angin, dan pohon yang lebih beragam.
- Dari cek kode ditemukan satu masalah nyata: mobil di arteri melingkar melintasi rel trem di 8 perlintasan tanpa pengaman, jadi mobil dan trem bisa saling tembus. Masalah ini masuk prioritas pertama bersama lampu lalu lintas.
- Dikerjakan dalam 5 sub-tahap (12b-1 sampai 12b-5). Tiap sub-tahap bisa diuji sendiri. Item berat (pejalan kaki, pohon baru) punya saklar per preset.

## Kondisi sekarang (hasil cek kode)

| Area | Kondisi di kode | Dampak |
| --- | --- | --- |
| Mobil | 3.301 mobil GPU (`TRAFFIC`). Posisi dihitung di shader dari waktu: `p = mod(awal + v x t, panjang)`, kecepatan tetap 11-16 m/s, tidak pernah berhenti | Tidak ada antrean, mobil menembus simpang dan rel |
| Lampu lalu lintas | 216 simpang arteri (24 arteri keliling x 9 arteri melingkar), 4 tiang per simpang (`FURN.signal`). Satu material untuk semua lampu, kuning berkedip (`updateFurniture`) | Tidak ada merah/hijau |
| Trem vs mobil | Rel trem di s = 0 (boulevard 40 m). Arteri melingkar di za 250, 500, 750, 1.250, 1.500, 1.750, 2.250, 2.500 memotong rel (za 1.000 dan 2.000 adalah cincin struktur, tanpa mobil). Tidak ada lampu atau palang. Halte Pusat kota (za 500) dan Kota (za 1.250) tepat di perlintasan, trem berhenti 12 s di sana | Mobil melintas menembus trem, terutama saat trem berhenti di halte |
| Pohon | 3 jenis (oak, elm, poplar), 6 template, 1 atlas daun 2 kolom, warna hijau dengan variasi kecil per pohon (`vTint`). Goyang daun kecil (5 cm), bergantung `windAt()` | Kota dan taman terlihat seragam |
| Angin | Hanya noise `windAt(P)` di shader rumput, jagung, daun. Tidak ada arah angin global | Daun gugur dan bendera butuh arah angin yang sama |
| Orang, burung | Tidak ada. Kicau burung hanya suara | Kota sepi |

## 12b-1. Lampu lalu lintas sungguhan dan pengaman trem (prioritas 1)

| No | Item | Rencana | Biaya |
| --- | --- | --- | --- |
| A4a | Siklus lampu | Tiap simpang punya siklus 60 s: hijau arteri keliling 26 s, kuning 3 s, merah semua 1 s, hijau arteri melingkar 26 s, kuning 3 s, merah semua 1 s. Fase tiap simpang digeser mengikuti jarak (gelombang hijau sederhana: mobil yang lolos satu simpang cenderung lolos berikutnya). Satu fungsi fase yang sama ditulis di JS dan GLSL | Rendah |
| A4b | Tampilan lampu | Muka lampu diganti 3 lampu (merah, kuning, hijau) per tiang. Warna per instance dihitung di shader dari fase simpang, jadi CPU tidak perlu update. Malam hari lampu menyala (bloom) | Rendah |
| A4c | Mobil berhenti | Tetap di GPU tanpa beban CPU. Tiap mobil masih punya posisi "nominal" seperti sekarang. Saat lampu di depannya merah, mobil dalam 90 m sebelum garis henti ditahan: mengerem halus ke garis henti, dan mobil di belakangnya berbaris dengan jarak 7 m (urutan antrean dari waktu tiba). Saat hijau, mobil berangkat berurutan (jeda 1,5 s per mobil) lalu mengejar posisi nominalnya dalam 120 m setelah simpang. Mobil yang sudah melewati garis henti saat lampu berubah tetap jalan | Sedang |
| A4d | Lampu rem | Lampu belakang lebih terang saat mobil melambat atau berhenti (dari turunan posisi di shader) | Rendah |
| T1 | Perlintasan trem | 8 perlintasan di s = 0. Posisi, kecepatan, dan status berhenti trem dikirim ke shader mobil lewat uniform (1 vec4 per frame). Perlintasan "tertutup" bila trem berada dalam 60 m dari perlintasan, akan tiba dalam 8 s, atau sedang berhenti di halte perlintasan. Mobil berhenti di garis henti 24 m dari as rel, memakai logika antrean A4c | Rendah-sedang |
| T2 | Rambu perlintasan | Tiang lampu merah berkedip ganda + palang yang turun/naik di 4 kaki tiap perlintasan (InstancedMesh, sudut palang dari shader). Garis henti dan tulisan "AWAS TREM" di aspal (shader tanah) | Rendah |
| T3 | Suara | Bel perlintasan (ding-ding) saat perlintasan tertutup dan pemain dalam 150 m. Bel trem saat berangkat dari halte | Rendah |
| T4 | Uji tabrakan | Skrip uji: simulasikan 30 menit waktu trem (percepat `uTime`), hitung setiap mobil yang posisinya berada di kotak perlintasan saat trem ada di kotak yang sama. Target: 0 kejadian | Rendah |

Catatan: pemain yang berdiri di jalan tetap tidak ditabrak mobil (mobil GPU tidak tahu posisi pemain). Ini batasan yang sudah ada sejak tahap 10.

## 12b-2. Pohon lebih bervariasi, daun kuning, angin

| No | Item | Rencana | Biaya |
| --- | --- | --- | --- |
| P1 | Jenis pohon baru | Dari 3 jenis menjadi 8. Baru: maple (tajuk bulat lebar, daun kuning-jingga-merah), birch (batang putih bergaris, ramping, daun kuning-hijau), pinus (kerucut, daun jarum), willow (cabang menjuntai, di tepi sungai dan danau), pohon berbunga (tajuk merah muda atau jingga menyala, sedikit, di taman). Tetap prosedural dengan `makeTree()`, bentuk dan warna batang orisinal | Sedang |
| P2 | Atlas daun | Atlas daun diperluas dari 2 ke 4 kolom: gugus daun lebar (lama), poplar (lama), jarum pinus, untaian willow. Tekstur digambar di kanvas saat muat seperti sekarang | Rendah |
| P3 | Variasi per pohon | Template naik dari 6 ke 16 (2 bentuk per jenis). Tiap instance dapat warna tajuk dari palet jenisnya (hash posisi), skala 0,75-1,3, sedikit condong. Pohon kota dan pohon taman dipilih per zona: jalan kota = elm, maple, birch; taman = campur semua; tepi air = willow; penahan angin = poplar (lama) dan pinus; bukit Cooper tetap campuran lama plus maple | Sedang |
| P4 | Daun kuning | Sekitar 20% pohon (maple, birch, sebagian elm) bertajuk kuning-jingga. Satu pengaturan "Suasana daun" di panel Grafik: Hijau (seperti sekarang), Campur (bawaan), Gugur (60% kuning, lebih banyak daun jatuh) | Rendah |
| P5 | Daun jatuh tertiup angin | Partikel daun GPU (1 draw call, 2.000 di Ultra, 600 di Rendah). Daun lepas dari tajuk pohon kuning dalam 120 m dari pemain, melayang turun sambil berputar dan bergoyang, terbawa arah angin, lalu tergeletak di tanah beberapa detik sebelum hilang. Lintasan dihitung analitik di shader dari (pohon asal, waktu lahir), jadi tanpa beban CPU. Saat hembusan kuat, sebagian daun di tanah terangkat dan tergulung | Sedang |
| P6 | Serakan daun di tanah | Bercak daun kuning di bawah pohon kuning (dari tekstur bayangan tajuk yang sudah ada, dipakai ulang di shader tanah) dan di tepi trotoar | Rendah |
| W1 | Angin global | Objek `WIND` baru: arah (berubah pelan), kekuatan dasar, hembusan (gust) yang berjalan melintasi kota sebagai gelombang. Dipakai daun jatuh, goyang tajuk (amplitudo dinaikkan dari 5 cm menjadi 5-25 cm saat hembusan), rumput, bendera, dan suara angin. Tahap 12c (B5) nanti tinggal menaikkan kekuatan saat mendung | Rendah |
| W2 | Catatan fisika | Udara stasiun ikut berputar, jadi dalam kerangka stasiun daun jatuh hampir lurus ke bawah bila tidak ada angin. Pergeseran Coriolis untuk daun (turun pelan, sekitar 1 m/s dari 10 m) kurang dari 2 m, dihitung sekalian di rumus lintasan supaya konsisten dengan bola | Rendah |

## 12b-3. Pejalan kaki

| No | Item | Rencana | Biaya |
| --- | --- | --- | --- |
| B1a | Model | Orang low-poly sekitar 250 segitiga: kepala, badan, lengan, kaki, sebagian membawa tas. Variasi tinggi 1,55-1,90 m, warna baju dan celana dari palet, warna kulit dan rambut beragam. Anak-anak (skala 0,6) sekitar 8% di taman | Rendah |
| B1b | Animasi | Di vertex shader: ayunan kaki dan lengan dari fase langkah, badan naik-turun sedikit. Pose duduk untuk orang di bangku (kaki ditekuk) | Rendah |
| B1c | Gerak | Dihitung di GPU dari (jalur, waktu), seperti mobil. Jalur: trotoar di kedua sisi arteri (bolak-balik dalam satu blok, berbalik di ujung blok), jalan setapak taman, plaza spaceport, dalam terminal, halte trem. Kecepatan 1,1-1,6 m/s. Menyeberang jalan hanya di zebra saat lampu pejalan kaki hijau (fase dari 12b-1) | Sedang-tinggi |
| B1d | Duduk dan diam | Sebagian orang duduk di bangku kota (`FURN` bench), bangku terminal, halte, atau berdiri mengobrol berdua-bertiga di plaza dan taman | Rendah |
| B1e | Kepadatan | Mengikuti kelas kota (pusat paling ramai) dan jam: pagi dan sore ramai, tengah malam sangat sepi. Anak-anak dan orang di taman hanya siang | Rendah |
| B1f | LOD dan preset | Satu InstancedMesh (1 draw call + 1 bayangan). Hanya orang dalam radius dari pemain yang digambar: Ultra 300 m, Tinggi 250 m, Sedang 180 m, Rendah 120 m. Total instance direncanakan sekitar 12.000 (perkiraan, disesuaikan setelah uji FPS) | Sedang |
| B1g | Batasan | Pejalan kaki tidak menghindari pemain (pemain bisa menembus). Pejalan kaki di dalam trem dan di lift belum ada | - |

## 12b-4. Burung

| No | Item | Rencana | Biaya |
| --- | --- | --- | --- |
| B3a | Kawanan terbang | 3-5 kawanan (15-40 ekor) di sekitar pemain di taman, ladang, dan atas kota. Boids sederhana di CPU (sekitar 150 burung total, murah): kohesi, separasi, arah, menghindari gedung dengan batas tinggi. Sayap mengepak di shader, sesekali meluncur | Rendah-sedang |
| B3b | Merpati di plaza | Kelompok burung di tanah (plaza spaceport, alun-alun, taman) yang mematuk-matuk, lalu terbang serentak saat pemain mendekat 6 m, dan hinggap lagi setelah beberapa detik | Rendah |
| B3c | Siklus hari | Aktif pagi sampai sore, pulang ke pohon saat senja (terbang ke pohon terdekat lalu hilang), malam tidak ada. Kicau yang sudah ada disesuaikan dengan lokasi kawanan (panning stereo) | Rendah |
| B3d | Catatan fisika | Burung terbang di udara yang ikut berputar, jadi tidak ada efek Coriolis yang terlihat pada kecepatan burung. Burung tidak terbang ke atas 300 m (batas awan) | - |

## 12b-5. Suasana (vibe)

| No | Item | Rencana | Biaya |
| --- | --- | --- | --- |
| V1 | Suara kota berlapis | Gumam keramaian dekat banyak pejalan kaki, langkah orang lewat, bunyi mobil lewat (desis ban + mesin listrik) dari mobil terdekat, bunyi penyeberangan (tik-tik saat hijau pejalan kaki), bel trem. Suara diperkecil malam hari | Rendah-sedang |
| V2 | Kafe trotoar | Meja bulat, kursi, payung warna-warni di depan sebagian gedung pusat kota, dengan orang duduk (dari B1d). Malam hari lampu gantung hangat | Rendah |
| V3 | Bendera dan umbul-umbul | Tiang bendera di plaza spaceport dan terminal, umbul-umbul di tiang lampu boulevard. Kain berkibar di shader mengikuti `WIND` | Rendah |
| V4 | Lampu taman malam | Untaian lampu hangat di jalan setapak taman dan kafe, menyala saat senja | Rendah |
| V5 | Detail kecil | Sepeda di rak dekat halte, beberapa orang bersepeda di boulevard, gelembung sabun atau layang-layang di taman siang hari (satu atau dua, bukan massal) | Rendah |
| V6 | Warna suasana | Cahaya sore lebih hangat saat "jam emas" (penyesuaian kecil tone di `updateLighting()`), kabut tipis pagi di taman | Rendah |

## Urutan kerja dan uji

| Urutan | Sub-tahap | Isi | Yang diuji |
| --- | --- | --- | --- |
| 1 | 12b-1 | Lampu lalu lintas, mobil berhenti, perlintasan trem | Uji otomatis 0 tabrakan mobil-trem; pemilik: mobil antre dan berangkat wajar, FPS tidak turun |
| 2 | 12b-2 | Pohon baru, daun kuning, daun jatuh, angin global | Waktu muat (bake impostor 16 template), FPS di taman (GTX 1060 dan M1) |
| 3 | 12b-3 | Pejalan kaki | FPS di Pusat kota pada jam ramai; angka kepadatan disesuaikan |
| 4 | 12b-4 | Burung | Kawanan terlihat wajar, merpati terbang saat didekati |
| 5 | 12b-5 | Suasana | Kesan keseluruhan pagi, siang, sore, malam |

Tiap sub-tahap: `tools/qc_load.py` tanpa error, uji otomatis ditambah ke `tools/`, dokumen ini diperbarui dengan hasil.

## Perkiraan biaya render (rencana, belum diukur)

| Item | Draw call tambahan | Beban utama |
| --- | --- | --- |
| Lampu lalu lintas + perlintasan | 2-3 | Hampir nol (shader) |
| Pohon 16 template | Sekitar +30 (kulit, daun, impostor per template) | Waktu muat bake impostor, sedikit memori tekstur |
| Daun jatuh | 1-2 | Vertex shader, kecil |
| Pejalan kaki | 2 (+1 bayangan) | Vertex shader; paling berat di pusat kota |
| Burung | 1-2 | CPU boids kecil |
| Suasana (kafe, bendera, lampu) | 4-6 | Kecil |

Pejalan kaki dan daun jatuh ikut preset (Ultra sampai Rendah) dan ikut turun otomatis bila FPS di bawah 30.

## Keputusan yang perlu dari pemilik

| No | Pertanyaan | Usulan bawaan |
| --- | --- | --- |
| K1 | Stasiun tidak punya musim alami. Daun kuning dibuat permanen di sebagian pohon (Campur) atau lewat pengaturan musim? | Pengaturan "Suasana daun" dengan bawaan Campur (20% kuning) |
| K2 | Perlintasan trem: palang turun atau cukup lampu berkedip? | Palang + lampu |
| K3 | Pejalan kaki menembus pemain (murah) atau menghindar (butuh CPU per orang dekat) | Menembus dulu; menghindar bisa di cadangan |
| K4 | Target jumlah pejalan kaki | 12.000 total, disesuaikan setelah uji FPS |

## Risiko dan catatan

- Antrean mobil di GPU adalah pendekatan: tiap mobil tidak benar-benar tahu mobil di depannya. Urutan antrean dihitung dari waktu tiba, dan karena jarak antarmobil di lajur 66-320 m, antrean biasanya 1-3 mobil. Bila terlihat mobil tumpang tindih, jarak antrean diperbesar atau kepadatan di simpang dikurangi.
- 16 template pohon menambah waktu muat (bake impostor 256 x 256 per template). Perkiraan tambahan kurang dari 1 s, belum diukur.
- Pejalan kaki adalah item terberat. Bila FPS di GTX 1060 turun di bawah 50 di pusat kota, radius LOD dan kepadatan diturunkan dulu sebelum mengurangi fitur lain.
- Item 12c (hujan, B5 angin mengikuti cuaca, air mancur Coriolis) tetap di 12c. `WIND` dari 12b-2 disiapkan supaya B5 tinggal disambungkan.
