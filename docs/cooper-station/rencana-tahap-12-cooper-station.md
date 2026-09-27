# Rencana Tahap 12: Cooper Station

Status: 12a selesai (lihat bagian 12a). 12b selesai (lihat `rencana-tahap-12b-cooper-station.md`). 12c dan 12d belum dikerjakan. Titik awal = tahap 11d (artifact versi 24). Semua yang sudah ada tetap dipertahankan.

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

## 12d. Ladang, foto, tur

| No | Item | Rencana | Biaya |
| --- | --- | --- | --- |
| B4 | Aktivitas ladang | Mesin panen dan traktor bergerak di petak, debu saat panen, warna tanaman berubah mengikuti siklus tanam | Sedang |
| C2 | Mode foto | Sembunyikan HUD, atur jam dan cuaca, fokus kamera, tombol simpan gambar | Rendah |
| C3 | Tur sinematik | Kamera otomatis berkeliling stasiun dengan teks penjelasan fisika (gravitasi buatan, Coriolis, despun) | Rendah-sedang |

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
