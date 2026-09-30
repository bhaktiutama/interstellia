# Konsep Experience: Millar's World

Per 27 September 2026 · Bhakti · Status: konsep; prototipe low poly ada (`prototipe-low-poly-millar.md`)

## Ringkasan

- Planet air dangkal yang mengorbit sangat dekat Gargantua. Pemain berjalan di laut setinggi lutut dengan gravitasi 1,3 g, dengan lubang hitam raksasa menggantung di langit.
- Inti pengalaman: gelombang pasang setinggi sekitar 1,2 km datang berkala karena planet bergoyang, ditambah jam dilatasi waktu (1 jam di planet = 7 tahun di luar) yang berlari selama pemain berada di permukaan.
- Dibangun sebagai experience ke-3 (`experiences/millar/`), memakai ulang shader lubang hitam dari Gargantua dan shuttle KS-07 dari Cooper Station.

## Angka dasar

| Besaran | Nilai | Asal |
| --- | --- | --- |
| Dilatasi waktu | 1 jam = 7 tahun, faktor sekitar 61.362 | Film; dihitung 7 x 365,25 x 24 jam |
| Artinya | 1 detik = 17,0 jam; 1 menit = 42,6 hari; 10 menit = 1,17 tahun | Turunan dari faktor di atas |
| Gravitasi | 1,3 g (12,75 m/s²) | Film ("130% gravitasi Bumi") |
| Tinggi gelombang | sekitar 1.200 m (4.000 kaki) | Film, dikutip Interstellar Wiki |
| Massa Gargantua | sekitar 100 juta massa Matahari | Kip Thorne, The Science of Interstellar |
| Putaran Gargantua | kurang dari maksimum sekitar 1 per 100 triliun | Kip Thorne |
| Kedalaman laut | sekitar 0,3-0,6 m (setinggi mata kaki sampai lutut) | Perkiraan dari adegan film, tidak disebut angkanya |
| Penyebab gelombang | Planet terkunci pasang surut tapi bergoyang (librasi), air terlempar bolak-balik | Penjelasan Kip Thorne |

## Angka desain (turunan dan pilihan kita)

| Besaran | Nilai | Cara dapat |
| --- | --- | --- |
| Radius planet | 8.282 km | Asumsi massa jenis sama dengan Bumi, jadi radius sebanding gravitasi: 1,3 x 6.371 km |
| Jarak cakrawala dari mata (1,7 m) | 5,3 km | sqrt(2 x R x h) |
| Puncak gelombang mulai terlihat | sekitar 147 km | Cakrawala mata + cakrawala puncak 1.219 m |
| Kecepatan muka gelombang | sekitar 125 m/s | Perkiraan kasar sqrt(g x H); parameter desain, bisa diatur |
| Waktu peringatan | sekitar 20 menit waktu planet (sekitar 2,3 tahun di luar) | 147 km / 125 m/s |
| Tinggi lompat | 77% dari di Bumi | Kecepatan lompat sama, gravitasi 1,3x |
| Interval gelombang | Mode realistis: panjang (puluhan menit). Mode permainan: 4-6 menit | Keputusan desain, lihat pertanyaan |

## Pengalaman pemain

| Momen | Yang dirasakan |
| --- | --- |
| Tiba | Berdiri di samping shuttle KS-07 yang mendarat di air dangkal. Kabut tipis, cahaya pucat keabuan dari piringan akresi, Gargantua memenuhi sebagian besar langit |
| Menjelajah | Berjalan di air setinggi lutut: cipratan tiap langkah, riak menyebar, dasar laut terlihat (pasir, batu, gundukan). Langkah lebih berat (1,3 g) |
| Jam waktu | HUD dua jam: waktu planet berjalan normal, "waktu di luar" melompat hari demi hari. Tiap menit di planet = 42 hari di luar |
| Tanda bahaya | Langit sedikit bergoyang (planet bergoyang). Di cakrawala tampak garis putih seperti pegunungan, lalu ternyata bergerak |
| Air surut | Sebelum gelombang tiba, air tertarik ke arah gelombang: laut makin dangkal, dasar laut muncul, arus terasa |
| Gelombang tiba | Dinding air 1,2 km, buih di puncak, kabut semburan, gemuruh rendah, tanah bergetar. Kalau tersapu: layar putih buih, kamera terguling, lalu kembali di shuttle dengan catatan "waktu yang hilang: X tahun" |
| Selamat | Kembali ke shuttle, lepas landas sebelum gelombang tiba. Atau berdiri di punggung gelombang yang lewat (versi realistis: tetap tersapu) |
| Pandangan orbit | Dari luar: planet kecil di dekat piringan akresi Gargantua, cahaya planet terbelokkan (memakai shader Gargantua) |

## Misi (opsional, untuk memberi tujuan)

| Misi | Isi |
| --- | --- |
| Suar yang hilang | Cari suar pendarat misi sebelumnya (desain orisinal) dalam radius 1-2 km, ambil kotak data, kembali ke shuttle sebelum gelombang |
| Pengukuran | Pasang 3 pelampung sensor; tiap pelampung menampilkan kedalaman dan arus saat air surut |
| Skor | Waktu di luar yang terpakai (tahun). Makin sedikit makin baik |

## Pendekatan teknis

| Bagian | Rencana |
| --- | --- |
| Halaman | `experiences/millar/index.html`, three.js 0.186.1, satu file, pola sama dengan Cooper Station |
| Langit dan Gargantua | Porting shader lensa gravitasi dari experience Gargantua, dirender ke cubemap. Diperbarui bergilir satu sisi per frame supaya piringan tetap bergerak tanpa membebani GPU. Arah Gargantua tetap di langit (terkunci pasang surut), bergoyang pelan sesuai siklus goyangan |
| Cahaya | Tanpa matahari. Cahaya utama dari piringan akresi (lebar, lembut, keemasan pucat), ditambah langit berkabut keabuan. Bayangan lembut |
| Lengkung planet | Permukaan laut turun d²/(2R) di shader, sehingga cakrawala di 5,3 km dan gelombang muncul dari balik cakrawala |
| Laut dangkal | Grid mengikuti kamera dengan LOD. Riak kecil (Gerstner, di bawah 10 cm), normal detail, air bening dengan refraksi dan kaustik ke dasar. Kedalaman berubah-ubah (gundukan pasir) |
| Dasar laut | Heightmap prosedural: pasir, batu datar, ganggang tipis; terlihat saat air surut |
| Gelombang | Profil analitik bergerak: muka curam, punggung landai, melengkung ratusan km ke samping. Resolusi tinggi hanya di dekat pemain. Buih di puncak, partikel semburan, kabut. Fase surut: kedalaman di depan gelombang berkurang |
| Pemain | Berjalan di air: kecepatan turun sesuai kedalaman, cipratan dan riak per langkah, suara langkah air. Lompat 77% |
| Shuttle | KS-07 dari Cooper Station (desain orisinal), ditambah kaki pendarat. Kode dipindah ke `shared/kestrel.js`, jadi ini modul bersama pertama |
| Audio | Disintesis: gemericik, angin, gemuruh gelombang frekuensi rendah yang makin keras, getaran tanah. Musik generatif sendiri |
| HUD | Dua jam (planet, luar), gravitasi, kedalaman air, jarak dan waktu tiba gelombang, fase goyangan |
| Preset | Ultra sampai Rendah seperti Cooper Station: resolusi cubemap, jumlah partikel semburan, jarak LOD laut |

## Tahapan

| Tahap | Isi | Yang diuji |
| --- | --- | --- |
| M1 | Laut dangkal, dasar laut, lengkung planet, berjalan di air 1,3 g, langit dengan Gargantua (cubemap), jam dilatasi | Tampilan dan FPS dasar |
| M2 | Siklus goyangan, gelombang (tampak di cakrawala, air surut, datang, lewat), tersapu, audio gemuruh | Kesan skala dan ketegangan |
| M3 | Shuttle KS-07 mendarat, naik, lepas landas; misi suar | Alur permainan |
| M4 | Pandangan orbit (planet di dekat Gargantua), sinematik kedatangan, preset kualitas, penyelarasan dengan menu (selesai: `rencana-m4-millar.md`) | Keseluruhan |

## Keputusan yang perlu kamu pilih

1. Kedalaman laut: setinggi lutut seperti di film (0,3-0,6 m), atau bervariasi dengan alur dalam (sampai 2 m) supaya ada area yang tidak bisa diseberangi?
2. Tersapu gelombang: kembali ke shuttle dengan penalti waktu (disarankan), atau "misi gagal" lalu mulai ulang?
3. Interval gelombang: mode permainan 4-6 menit sebagai bawaan (disarankan) dengan opsi mode realistis?
4. Misi suar dimasukkan sejak M3, atau murni menjelajah dulu?

## Catatan dan keterbatasan

- Kecepatan gelombang 125 m/s adalah perkiraan kasar untuk desain. Fisika gelombang 1,2 km di laut 0,5 m tidak bisa dihitung dengan rumus gelombang air dangkal biasa. Kip Thorne sendiri menjelaskannya sebagai air yang terlempar oleh goyangan planet, bukan gelombang laut biasa.
- Radius planet tidak disebut di film. Angka 8.282 km adalah asumsi kita (massa jenis seperti Bumi).
- Kedalaman laut dan interval gelombang tidak diberi angka pasti di sumber; di sini jadi parameter yang bisa diatur.
- Nama "Millar's World" dekat dengan nama planet di film. Untuk proyek pribadi aman; kalau aplikasinya dibuka untuk publik, pertimbangkan nama versi publik (lihat `docs/app/penamaan.md`).

## Sumber

- [The Science of Interstellar, kutipan buku (Space.com)](https://www.space.com/28077-science-of-interstellar-book-excerpt.html): massa dan putaran Gargantua, 1 jam = 7 tahun
- [Miller's Planet, Interstellar Wiki](https://interstellarfilm.fandom.com/wiki/Miller_(planet)): gravitasi 130%, gelombang 4.000 kaki, penjelasan goyangan planet
