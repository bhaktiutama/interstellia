# Rencana Tahap 19 Copper Corn Station: gerak (jalan, lari, motor)

Per 28 September 2026 · Bhakti

## Ringkasan

- **19a (selesai):** kamera ikut langkah saat jalan dan lari (naik-turun, ayun samping, guling kecil), napas halus saat diam, hentakan saat mendarat, FOV sedikit melebar saat lari. Suara langkah kini jatuh tepat saat kaki menapak. Bisa diatur di panel Gerak: Mati, Halus, Normal.
- **19b (selesai):** motor 150 cc orisinal, tombol C. POV dari atas jok: setang, dasbor digital, spion, kaca depan kecil, sarung tangan di grip, lutut di tangki. Motor miring di tikungan, setang ikut berbelok, suspensi dan guncangan jalan. Malam: lampu depan menyorot jalan dan menerangi gedung, pohon, mobil di depan.
- Fisika tetap jujur: berat terasa di motor = (omega r + v_t)^2 / r, jadi searah putaran stasiun lebih berat, melawan putaran lebih ringan; cengkeraman ban ikut berubah.

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
| Shift | Mode sport (puncak sekitar 99 km/h; normal sekitar 60 km/h) |
| Space | Klakson (merpati dalam 30 m terbang) |
| O | Gas terus (cruise) |
| Mouse | Menoleh sampai 110 derajat, kembali ke depan sendiri 1,2 s setelah mouse diam |
| Layar sentuh | Tombol Motor; joystick = gas, rem, belok; tombol Lompat = klakson |

### Fisika

| Bagian | Rumus / nilai | Sumber |
| --- | --- | --- |
| Berat terasa | g' = (omega r + v_t)^2 / r, v_t = komponen kecepatan searah putaran | gerak di kerangka berputar; di lantai silinder Coriolis hanya mengubah berat, tidak mendorong ke samping |
| Contoh 54 km/h | searah 1,326 g, melawan 0,720 g, sejajar sumbu 1,000 g | hitungan di atas, dicek `tools/uji_gerak.py` |
| Contoh 100 km/h | searah sekitar 1,64 g, melawan sekitar 0,52 g | hitungan di atas |
| Cengkeraman ban | mu x g', mu 0,85 aspal / 0,55 tanah dan rumput, -35% saat basah (hujan) | membatasi gas, rem (0,9 mu g'), dan belok (0,75 mu g') |
| Belok | laju yaw = min(v / 1,34 m x tan 34 derajat, 0,75 mu g' / v) | sudut setang di kecepatan rendah, gaya samping di kecepatan tinggi |
| Miring | tan(lean) = v x yaw / g' | keseimbangan gaya di tikungan; kamera ikut 65% |
| Hambatan | gulir 0,012 g' (tanah 0,05 g'), udara 0,0008 v^2 | |
| Kecepatan puncak | normal sekitar 60 km/h, sport sekitar 99 km/h | dorongan 3,2 / 4,2 m/s^2 x (1 - (v/vmax)^3) sama dengan hambatan |
| Gigi | 6 gigi, pindah otomatis; rpm 1.450 (langsam) sampai sekitar 10.500 | untuk suara dan dasbor |
| Tabrakan | collider yang sama dengan pejalan kaki (radius 0,45 m); dari depan di atas 12,6 km/h = berhenti, layar bergetar, bunyi benturan | |
| Air, end cap | berhenti di tepi | |

### Tampilan dan suara

| Bagian | Isi |
| --- | --- |
| Model | badan (tangki merah, jok, mesin bersirip, knalpot kanan, roda), bagian depan berputar di sumbu kemudi 22,5 derajat (garpu, roda, lampu, dasbor, kaca, setang, tuas, spion), pengendara (sarung tangan, lengan bawah, pangkuan, kaki, sepatu) |
| Bayangan | tubuh dan helm pengendara hanya di pass bayangan: terlihat bayangannya di tanah, tidak menghalangi kamera |
| Dasbor | kanvas 256 x 112: takometer, km/h, gigi (N hijau), jam, berat terasa, indikator lampu, SPORT; redup saat malam |
| Spion | memantulkan daratan seberang dan sunline (`specMat`, bukan render ulang) |
| Lampu depan | malam saja (mengikuti lampu jendela kota). Tanah: kolam sorot sampai sekitar 40 m, melebar sekitar 17 derajat (`headPoolL`, juga pantulan di aspal basah). Objek: sorot kerucut 13-30 derajat, meredup 1/d^2 (`headSpotL` di `nightLight`). Arah ikut setang |
| Lampu belakang | merah, lebih terang saat mengerem |
| Parkir | bersandar ke kiri di standar samping, setang dikunci ke kiri, lampu mati |
| Suara | mesin satu silinder disintesis (letupan = rpm / 120 Hz: gergaji + kotak + modulasi), angin sesuai kecepatan, starter saat naik, klakson dua nada, bunyi benturan |

Status: sub-mode state `ground` (`MOTO.on`), seperti `player.deck`. Masuk lift, trem, tur, atau pesawat = motor ditinggal di tempat. Teleport (1-9, 0, peta) = motor ikut pindah, kecuali ke dek pandang.

## Hasil uji

`tools/uji_gerak.py` (21 pemeriksaan, semua OK di SwiftShader):

| Kasus | Hasil |
| --- | --- |
| Jalan 3 s | naik-turun 3,6 cm, 5 langkah untuk 4,20 m |
| Lari 3 s | naik-turun 7,2 cm, FOV 74,0 derajat |
| Berhenti | FOV kembali 70,00 derajat, sisa gerak sekitar 2 mm (napas) |
| Level Mati | gerak 0,000 mm |
| Lompat 0,6 s | kepala turun 2,7 cm lalu kembali |
| Gas 10 s (normal) | 59,4 km/h, gigi 4, 111 m |
| Belok kanan 0,67 s di 58 km/h | miring 30,6 derajat ke kanan, heading -11,8 derajat |
| Rem dari 53 km/h | berhenti 1,9 s, 13,1 m (rem saja 14,4 m, sisanya hambatan) |
| Berat terasa 54 km/h | searah 1,326 g, melawan 0,720 g, sejajar sumbu 1,000 g (sama dengan analitik) |
| Menabrak gedung (53 km/h) | berhenti 0,45 m dari muka gedung |
| Melaju ke sungai | tidak pernah masuk air |
| Turun di 36 km/h | ditolak; saat diam turun 0,95 m di samping motor |
| Lampu depan | malam 1,00, 0,70 m di depan pusat motor; siang 0; diparkir 0 |

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
- Nilai rasa (amplitudo, FOV, cengkeraman) adalah pilihan desain, bukan hasil ukur; mohon dicek di GTX 1060 dan MacBook M1.
