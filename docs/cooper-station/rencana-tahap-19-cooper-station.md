# Rencana Tahap 19 Copper Corn Station: gerak (jalan, lari, motor)

Per 28 September 2026 · Bhakti

## Ringkasan

- **19a (selesai):** kamera ikut langkah saat jalan dan lari (naik-turun, ayun samping, guling kecil), napas halus saat diam, hentakan saat mendarat, FOV sedikit melebar saat lari. Suara langkah kini jatuh tepat saat kaki menapak. Bisa diatur di panel Gerak: Mati, Halus, Normal.
- **19b + 19c (selesai):** motor (tombol C), sejak 19c memakai model café racer V-twin pilihan Bhakti (model pihak ketiga, CC BY 4.0). POV: stang jepit dengan sarung tangan, fairing dan kaca, dial speedometer berjarum, tangki; motor miring di tikungan, stang ikut berbelok. Sport sampai 150 km/h. Getaran diredam: guling kamera sekitar 22-27 kali lebih kecil, naik-turun sekitar 5 kali lebih kecil. Malam: lampu depan menyorot jalan dan objek.
- Fisika tetap jujur: berat terasa di motor = (omega r + v_t)^2 / r, jadi searah putaran stasiun lebih berat (2,02 g di 150 km/h), melawan putaran lebih ringan (0,34 g); cengkeraman ban ikut berubah.

## 19a: gerak kepala

| Bagian | Nilai | Keterangan |
| --- | --- | --- |
| Panjang langkah | jalan 0,72 m, lari 1,3 m | sama dengan suara langkah lama; 1,4 m/s = 1,9 langkah/s, 5 m/s = 3,8 langkah/s |
| Naik-turun | jalan 3,6 cm, lari 7,2 cm (puncak ke puncak) | terendah saat kaki menapak; saat lari sedikit setelah menapak |
| Ayun samping | jalan 1,2 cm, lari 1,8 cm | sekali per dua langkah (ke kaki tumpuan) |
| Guling / angguk | 0,35-0,75 derajat / 0,12-0,4 derajat | kecil, agar tidak memusingkan |
| Napas saat diam | 4 mm, 0,23 Hz | hanya di level Halus dan Normal |
| Mendarat | pegas 1,9 Hz, redaman 0,7 | kepala turun sekitar 2,7 cm setelah lompat 0,6 s |
| FOV | +4 derajat saat lari, motor sampai +9 derajat di atas 100 km/h | kembali tepat 70 derajat saat diam |
| Mati otomatis | mode foto, tur, kamera luar, turbo X | |

Level tersimpan di localStorage `cooperStation.bob` (0 / 0,5 / 1).

## 19b: motor

### Kendali

| Tombol | Fungsi |
| --- | --- |
| C | Naik (motor datang ke sebelah Anda, atau naik motor yang diparkir dalam 4 m) / turun (hanya di bawah 10 km/h) |
| E | Di dekat motor parkir: naik. Di motor saat pelan: turun |
| W / S | Gas / rem. S saat diam: mundur pelan (kaki mendorong, maks 1,6 m/s) |
| A / D | Belok. Motor miring ke dalam tikungan |
| Shift | Mode sport (puncak 150 km/h; normal sekitar 60 km/h) |
| Space | Klakson (merpati dalam 30 m terbang) |
| O | Gas terus (cruise) |
| Mouse | Menoleh sampai 110 derajat, kembali ke depan sendiri 1,2 s setelah mouse diam |
| Layar sentuh | Tombol Motor; joystick = gas, rem, belok; tombol Lompat = klakson |

### Fisika

| Bagian | Rumus / nilai | Sumber |
| --- | --- | --- |
| Berat terasa | g' = (omega r + v_t)^2 / r, v_t = komponen kecepatan searah putaran | gerak di kerangka berputar; di lantai silinder Coriolis hanya mengubah berat, tidak mendorong ke samping |
| Contoh 54 km/h | searah 1,326 g, melawan 0,720 g, sejajar sumbu 1,000 g | hitungan di atas, dicek `tools/uji_gerak.py` |
| Contoh 150 km/h | searah 2,02 g, melawan 0,34 g | hitungan di atas (omega r = 99,05 m/s, v = 41,67 m/s) |
| Cengkeraman ban | mu x g', mu 0,85 aspal / 0,55 tanah dan rumput, -35% saat basah (hujan) | membatasi gas, rem (0,9 mu g'), dan belok (0,75 mu g') |
| Belok | laju yaw = min(v / jarak sumbu roda x tan 34 derajat, 0,75 mu g' / v); jarak sumbu roda 1,474 m (model 19c) | sudut setang di kecepatan rendah, gaya samping di kecepatan tinggi |
| Miring | tan(lean) = v x yaw / g' | keseimbangan gaya di tikungan; kamera ikut 65% |
| Hambatan | gulir 0,012 g' (tanah 0,05 g'), udara 0,00095 v^2 (1,65 m/s^2 di 150 km/h) | |
| Dorongan (19c) | min(batas awal, daya / v): normal 3,2 m/s^2, sport 5,0 m/s^2, daya 190 W/kg; dikali pembatas yang turun ke nol dalam 1,5 m/s sebelum batas; dibatasi cengkeraman ban | |
| Kecepatan puncak (19c) | normal 60 km/h (batas 16,9 m/s), sport 150 km/h (batas 42,3 m/s) | titik dorongan = hambatan; `uji_gerak.py`: 150,1 km/h, 0-100 km/h 6,5 s |
| Gigi (19c) | 6 gigi, pindah otomatis (batas 40, 61, 86, 112, 133, 157 km/h); rpm 1.100 (langsam) sampai 7.800 | untuk suara dan dial |
| Tabrakan | collider yang sama dengan pejalan kaki (radius 0,45 m); dari depan di atas 12,6 km/h = berhenti, layar bergetar, bunyi benturan | |
| Air, end cap | berhenti di tepi | |

### Tampilan dan suara

| Bagian | Isi |
| --- | --- |
| Model (19c) | café racer V-twin dari `experiences/cooper-station/assets/motor.data.js` (lihat bagian 19c). Motor sederhana dari primitif (tahap 19b) tetap dibuat sebagai cadangan bila aset gagal dimuat |
| Bagian depan | berputar di sumbu kemudi 26,2 derajat (sejajar kaki garpu): garpu, roda depan, spakbor, fairing, kaca, stang jepit, tuas, dial, lampu |
| Pengendara | sarung tangan di grip (mengikuti sudut grip), lengan bawah, pangkuan, paha, lutut di sisi tangki, tulang kering, sepatu di pijakan; dihitung dari titik grip, jok, pijakan model |
| Mata | 1,38 m di atas tanah, 0,25 m di belakang pusat motor; saat naik pandangan menunduk 12 derajat agar dial dan stang terlihat |
| Bayangan | tubuh, lengan atas, dan helm pengendara hanya di pass bayangan: terlihat bayangannya di tanah, tidak menghalangi kamera |
| Dial (19c) | kanvas 256 x 256 di muka tudung instrumen: skala 0-200 km/h dalam 270 derajat, jarum, angka km/h, gigi (N hijau), lampu hijau (lampu utama), lampu jingga (sport); redup saat malam. Model sederhana cadangan tetap memakai dasbor digital 19b |
| Lampu depan | malam saja (mengikuti lampu jendela kota). Tanah: kolam sorot sampai sekitar 40 m, melebar sekitar 17 derajat (`headPoolL`, juga pantulan di aspal basah). Objek: sorot kerucut 13-30 derajat, meredup 1/d^2 (`headSpotL` di `nightLight`). Arah ikut setang |
| Lampu belakang | merah, lebih terang saat mengerem |
| Parkir | bersandar ke kiri di standar samping (standar model hanya terlihat saat parkir), setang dikunci ke kiri, lampu mati |
| Suara (19c) | mesin V-twin disintesis (letupan rata-rata rpm / 60 Hz, siklus rpm / 120 Hz memberi dentum tidak rata: gergaji + kotak + modulasi), angin sesuai kecepatan, starter saat naik, klakson dua nada, bunyi benturan |

Status: sub-mode state `ground` (`MOTO.on`), seperti `player.deck`. Masuk lift, trem, tur, atau pesawat = motor ditinggal di tempat. Teleport (1-9, 0, peta) = motor ikut pindah, kecuali ke dek pandang.

## 19c: revisi setelah uji Bhakti

| Permintaan | Perubahan |
| --- | --- |
| Getaran motor terlalu kencang, termasuk saat keluar jalur | Guncangan jalan: aspal 0,5 mm, tanah 2 mm (dulu 2,5 dan 12 mm); guling dari jalan 0,03-0,1 derajat (dulu 0,57-2,75 derajat); suspensi memakai kecepatan naik-turun tanah yang dihaluskan 0,08 s (tepi segitiga tanah 8 m tidak lagi jadi hentakan), redaman lebih besar, batas 4 cm (dulu 12 cm), kamera ikut 50%. Semua ikut level gerak kepala (Mati = tanpa getaran) |
| Kecepatan sampai 150 km/h | Mode sport sampai 150 km/h (lihat Fisika) |
| Model motor diganti model terlampir | Model "moto guzzi v-twin" (café racer) diolah `tools/siapkan_motor.py`: 21,9 MB menjadi aset 3,1 MB (52.214 segitiga, tekstur 0,8 MB) |

Getaran diukur di kamera (puncak ke puncak, 2 s lurus, level Normal, versi 19b vs 19c):

| Permukaan (sekitar 60 km/h) | Guling 19b | Guling 19c | Naik-turun 19b | Naik-turun 19c |
| --- | --- | --- | --- | --- |
| Aspal | 1,146 derajat | 0,052 derajat | 4,61 mm | 0,91 mm |
| Tanah | 5,499 derajat | 0,206 derajat | 22,19 mm | 4,60 mm |

Pengolahan model (`tools/siapkan_motor.py sumber.glb`, sumber tidak disimpan di repo):

| Langkah | Isi |
| --- | --- |
| Kerangka | model +x depan, +y atas, +z kanan menjadi halaman +x kiri, +y atas, +z depan; titik asal di tanah di tengah kedua poros roda |
| Data | posisi, normal int8, UV, indeks. Peta normal, kekasaran-logam, tangen, warna verteks dibuang (stasiun memakai material dasar + `patchLit`); kilap tiap material dari rata-rata peta kekasaran-logam (`specMat`) |
| Tekstur | warna dasar diperkecil 128-1024 piksel, JPEG (rem PNG beralfa, dipakai sebagai cutout) |
| Kelompok | pulau segitiga terhubung: depan (di depan sumbu kemudi, atau stang jepit, tuas, saklar), standar samping (kiri, menyentuh tanah), badan. Diperiksa dengan render tampak samping dan atas |
| Muat | `<script src="assets/motor.data.js">` (base64), jalan juga dari file://; boot menunggu maks 10 s sebelum kompilasi shader |
| Kredit | di tab Tentang (bantuan) dan `experiences/cooper-station/assets/KREDIT.md` (wajib menurut CC BY 4.0). Tangki membawa logo elang Moto Guzzi dari model sumber |

## Hasil uji

`tools/uji_gerak.py` (25 pemeriksaan, semua OK di SwiftShader; angka 19c):

| Kasus | Hasil |
| --- | --- |
| Jalan 3 s | naik-turun 3,6 cm, 5 langkah untuk 4,20 m |
| Lari 3 s | naik-turun 7,2 cm, FOV 74,0 derajat |
| Berhenti | FOV kembali 70,00 derajat, sisa gerak sekitar 2 mm (napas) |
| Level Mati | gerak 0,000 mm |
| Lompat 0,6 s | kepala turun 2,7 cm lalu kembali |
| Model motor dari aset | termuat, 53.162 segitiga termasuk pengendara, jarak sumbu roda 1,474 m, kredit CC BY 4.0 |
| Gas 10 s (normal) | 60,2 km/h, gigi 3, 119 m |
| Sport di jalur lurus 1,6 km (tanah pertanian) | puncak 150,1 km/h, 0-100 km/h 6,5 s |
| Getaran | aspal 60 km/h: guling 0,052 derajat, naik-turun 0,91 mm; tanah 150 km/h: guling 0,206 derajat, naik-turun 7,34 mm |
| Belok kanan 0,67 s di 58 km/h | miring 30,6 derajat ke kanan, heading -11,8 derajat |
| Rem dari 53 km/h | berhenti 1,9 s, 13,1 m (rem saja 14,4 m, sisanya hambatan) |
| Berat terasa 54 km/h | searah 1,326 g, melawan 0,720 g, sejajar sumbu 1,000 g (sama dengan analitik) |
| Menabrak gedung (53 km/h) | berhenti 0,45 m dari muka gedung |
| Melaju ke sungai | tidak pernah masuk air |
| Turun di 36 km/h | ditolak; saat diam turun 0,95 m di samping motor |
| Lampu depan | malam 1,00, 0,65 m di depan pusat motor; siang 0; diparkir 0 |

## Usulan lanjutan (belum dikerjakan)

| Usulan | Isi | Perkiraan beban |
| --- | --- | --- |
| Sepeda | Pakai kerangka motor: kayuh (W), gigi sepeda, bel, lebih pelan (sekitar 20 km/h), bisa masuk jalan setapak taman dan hutan | rendah |
| Motor di lalu lintas | Motor dan ojek sebagai kendaraan di `TRAFFIC` (lajur kiri, menyalip pelan) | sedang |
| Kabin masinis trem | Duduk di depan trem: tuas, papan halte, pandangan rel | sedang |
| Stik game (Gamepad API) | Gas dan setang analog untuk motor, dua stik untuk jalan | rendah |
| Spion sungguhan | Render pandangan belakang ke tekstur kecil (Ultra dan Tinggi saja) | sedang (1 pass tambahan) |
| Lampu sein, lampu jauh, boncengan | Detail motor tambahan | rendah |
| Bayangan diri saat berjalan | Proksi tubuh dengan kaki berayun di pass bayangan (sudah ada untuk motor) | rendah |

## Batasan

- Lampu depan tidak membuat bayangan (sorot menembus pagar atau gedung tipis di tanah di belakangnya).
- Kolam sorot di tanah dihitung di bidang (s, za), tidak mengikuti lereng bukit.
- Mobil, trem, dan pejalan kaki tidak bertabrakan dengan motor (sama seperti pemain berjalan kaki).
- Nilai rasa (amplitudo, FOV, cengkeraman, dorongan) adalah pilihan desain, bukan hasil ukur; mohon dicek di GTX 1060 dan MacBook M1.
- Model 19c tanpa peta normal: detail permukaan dari tekstur warna saja. Bila terlihat datar di jarak dekat, peta normal bisa ditambahkan (butuh material dengan cahaya stasiun + normal map, beban GPU naik).
- Aset menambah 3,1 MB unduhan dan sedikit waktu muat (dekode base64 dan tekstur; belum diukur terpisah).
