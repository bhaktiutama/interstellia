# Rangkuman Visual Cooper Station (dari 4 referensi)

Per 26 September 2026 · Bhakti · untuk disepakati sebelum tahap mempercantik (tahap 5 dan seterusnya)

## Ringkasan

- **Arah visual:** kota dan ladang yang padat dan bervariasi, sungai berkelok, tulang sumbu bercahaya, dan udara berkabut kebiruan dengan awan, ditambah satu momen hangat keemasan di sekitar rumah Cooper dan end cap.
- **Tiga elemen baru dibanding rencana awal:** tulang sumbu (spine) berstruktur dengan cincin-cincin, sungai dan danau, dan awan di dalam silinder.
- **Satu keputusan besar soal cahaya:** cahaya dari sumbu saja membuat bayangan selalu tegak lurus seperti tengah hari. End cap kaca yang sudah disepakati memang meloloskan sinar Matahari, tapi sinar itu lemah dan datang miring sehingga hanya menerangi pita sekitar 800 m di dekat satu ujung, berputar tiap 63,4 detik. Untuk bayangan panjang keemasan seperti referensi 2, perlu cahaya tambahan di end cap: cincin lampu atau cermin pemantul (lihat Keputusan 1).

## Apa yang terlihat di tiap referensi

| No | Referensi | Elemen yang diambil |
| --- | --- | --- |
| 1 | Pandangan menyusuri silinder, cincin-cincin terang | Cincin struktur melingkar yang membagi silinder menjadi segmen; bangunan putih berderet di sepanjang cincin; ladang petak-petak hijau dengan batas tegas; kontras terang-gelap tinggi |
| 2 | Rumah Cooper dan end cap bercahaya | Rumah kayu putih 2 lantai dengan beranda keliling dan atap seng merah; ladang tanaman rendah di depan; deretan silo putih beratap kerucut; end cap sebagai cincin terang keemasan dengan lingkaran gelap berbintang di tengah; cahaya hangat dan silau (bloom) |
| 3 | Pandangan aksial "O'Neill Cylinder" | Sungai biru berkelok memotong kota dan ladang; jalan raya utama sepanjang sumbu; jalan melingkar; kepadatan kota bervariasi dari menara sampai rumah; petak ladang oranye, kuning, hijau; titik terang di pusat sumbu |
| 4 | Pandangan ke atas ke tulang sumbu | Tulang sumbu dengan cincin/torus di beberapa titik; awan melayang di dalam silinder; kabut udara biru; kota dengan blok dan jalan protokol; pusat kota dengan gedung tinggi; ladang cokelat dan hijau di tepi |

Catatan: referensi 3 berwatermark "AI SCIFI FUTURE" dan referensi 2 adalah lukisan konsep. Keduanya dipakai sebagai acuan suasana, bukan acuan skala.

## Usulan per komponen

### 1. Cahaya dan atmosfer

| Elemen | Usulan | Sumber referensi |
| --- | --- | --- |
| Sunline di sumbu | Tabung cahaya putih hangat di sepanjang sumbu, inti sangat terang dengan bloom; siklus siang dan malam lewat peredupan dan pergeseran warna | 3, 4 |
| Kabut udara | Kabut biru muda yang makin pekat dengan jarak; sisi seberang (2 km) tampak kebiruan, ujung jauh (8 km) samar | 4 |
| Awan | 30-60 awan billboard lembut di ketinggian 250-450 m, ikut berputar bersama stasiun | 4 |
| Sinar Matahari asli lewat end cap kaca | Selalu ada (konsekuensi end cap kaca): petak cahaya lemah di dekat satu ujung yang berputar mengikuti rotasi stasiun | Fisika |
| Cahaya end cap tambahan (lihat Keputusan 1) | Cincin lampu di tepi end cap atau cermin pemantul, warna keemasan, memberi bayangan panjang dan suasana sore | 2 |
| Malam | Sunline redup kebiruan, lampu jalan dan jendela menyala; kota di atas kepala tampak seperti galaksi titik cahaya | Tambahan saya |

### 2. Tulang sumbu (spine) dan struktur

| Elemen | Usulan | Sumber referensi |
| --- | --- | --- |
| Tulang sumbu | Silinder ramping di sumbu (diameter sekitar 20 m) yang membungkus sunline, dengan modul cincin/torus setiap 1-1,5 km | 4 |
| Cincin struktur | Rangka melingkar setiap 1 km (8 cincin) di permukaan dalam, tampak sebagai garis terang yang menegaskan kelengkungan dan kedalaman | 1 |
| End cap | Tetap kaca dengan 12 jari-jari, ditambah tepi yang bercahaya keemasan dan silau saat cahaya end cap aktif | 2 |
| Lift dan hub | Rel lift diberi kabin dan lampu; hub di sumbu tersambung ke tulang sumbu | 4 |

### 3. Tata guna lahan

| Elemen | Usulan | Sumber referensi |
| --- | --- | --- |
| Sungai | Satu sungai berkelok (lebar 30-60 m) yang melingkari silinder, melewati kota, taman, dan ladang; plus 2-3 danau | 3 |
| Ladang | Petak persegi berbagai ukuran dan warna: hijau muda, hijau tua, kuning gandum, oranye, cokelat bajak; pola baris tanaman terlihat dari dekat | 1, 3, 4 |
| Taman dan hutan | Kelompok pohon tidak beraturan, bukan baris seragam | 3 |
| Jalan | Jalan raya utama sepanjang sumbu, jalan melingkar di tiap cincin struktur, jalan kota yang tidak seragam | 3, 4 |

### 4. Kota (menjawab permintaan kota yang lebih bervariasi)

| Distrik | Isi | Tinggi bangunan |
| --- | --- | --- |
| Pusat kota | Menara kantor dan apartemen, alun-alun, stasiun trem utama | 6-20 lantai (20-70 m) |
| Kota menengah | Ruko, apartemen rendah, sekolah, klinik, pasar | 2-6 lantai |
| Permukiman | Rumah berbagai tipe (pelana, bentuk L, dengan garasi, rumah deret), kavling berbagai ukuran, jalan melengkung dan buntu | 1-2 lantai |
| Tepi kota | Rumah jarang, kebun, peralihan ke ladang | 1-2 lantai |

Semua bangunan tetap dirender per tipe (satu tipe = satu draw call), jadi variasi tidak membebani performa.

Dengan tinggi maksimal 70 m di stasiun berjari-jari 1 km, gravitasi di puncak menara sekitar 0,93 g (menurut rumus g × (R - h) / R).

### 5. Museum Cooper Farm

- Rumah kayu putih 2 lantai, beranda keliling, atap seng merah, jendela bertirai.
- Deretan 4-6 silo putih beratap kerucut, pagar kayu, truk pickup, rak buku Murph di dalam.
- Ladang tanaman rendah di sekitar rumah; sisi seberang silinder terlihat naik di belakangnya.
- Kalau cahaya end cap tambahan dipakai, museum ditempatkan dekat end cap supaya mendapat cahaya keemasan dari samping seperti referensi 2.

### 6. Detail hidup

- Mobil kecil bergerak di jalan raya utama (titik bergerak dari jauh).
- Trem dengan lampu, lampu jalan, jendela menyala saat malam.
- Burung atau daun beterbangan: opsional, hanya dekat pemain.

## Keputusan yang perlu disepakati

| No | Keputusan | Pilihan | Rekomendasi saya |
| --- | --- | --- | --- |
| 1 | Cahaya end cap | (a) Hanya sunline plus sinar Matahari asli yang lemah lewat end cap kaca: realistis, tapi bayangan panjang hanya samar di dekat satu ujung; (b) Ditambah cincin lampu keemasan di tepi end cap (buatan, stabil, mirip referensi 2); (c) Ditambah cermin di luar end cap yang memantulkan Matahari sepanjang sumbu (O'Neill klasik; tetap lemah karena Matahari di Saturnus redup) | **Disepakati: (b)**, dengan bayangan real-time hanya dalam radius sekitar 300 m dari pemain; sinar Matahari asli tetap disimulasikan sebagai detail |
| 2 | Suasana utama | (a) Siang biru berkabut (referensi 4); (b) Keemasan sore (referensi 2); (c) Keduanya lewat siklus hari | **Disepakati: (c)**, siang biru, menjelang malam berubah keemasan |
| 3 | Sungai | (a) Satu sungai melingkar plus danau; (b) Tanpa sungai | **Disepakati: (a)**, karena sungai sangat membantu membaca kelengkungan silinder |
| 4 | Posisi pusat kota | (a) Dekat spaceport (end cap A); (b) Di tengah silinder | **Disepakati: (a)**, sesuai pola kota pelabuhan; tengah silinder untuk ladang dan museum |
| 5 | Cincin struktur | (a) Setiap 1 km, terlihat tegas; (b) Tanpa cincin (lahan menerus seperti film) | **Disepakati: (a)**, tapi tipis dan tidak memotong jalan |

## Dampak ke performa (target laptop dan PC)

| Target | Resolusi | FPS minimal | Catatan |
| --- | --- | --- | --- |
| Laptop GPU terintegrasi (Intel Iris Xe, Apple M1) | 1080p | 30 | Preset Medium: tanpa bayangan real-time, awan lebih sedikit |
| PC GPU diskrit | 1440p | 60 | Preset High/Ultra: bayangan dekat pemain, bloom penuh, SSAO |

| Fitur | Perkiraan biaya | Cara menekan |
| --- | --- | --- |
| Bangunan bervariasi (sekitar 5.000-8.000 unit) | Draw call naik sekitar 10-15 | Instancing per tipe, impostor untuk sisi seberang |
| Bayangan dari cahaya end cap | Render tambahan 1-2 kali per frame | Hanya dalam radius sekitar 300 m, dimatikan di preset Medium |
| Awan | Overdraw transparan | Jumlah dibatasi, dirender setengah resolusi |
| Sungai | Shader air sederhana | Tanpa pantulan real-time; pantulan warna langit dan sunline saja |
| Post-processing (bloom, ACES, SSAO) | 3-5 pass layar penuh | Tiap efek punya saklar di panel kualitas |

Angka biaya di atas adalah perkiraan desain, bukan hasil ukur. Diukur di tiap gate.

## Urutan pengerjaan setelah disepakati

| Tahap | Isi |
| --- | --- |
| 4c | Kota bervariasi versi gray-box: distrik, jaringan jalan, tipe bangunan, sungai dan danau, ladang petak-petak, cincin struktur. Diuji dulu tata letak dan performanya. |
| 5 | Cahaya: sunline dengan siklus hari, kabut, awan, sinar Matahari asli lewat end cap, cahaya end cap tambahan (bila dipilih) |
| 6 | Material: tanah, jalan, air, ladang dengan pola baris tanaman |
| 7 | Saturnus dan cincin versi shader, tepi end cap bercahaya |
| 8 | Detail bangunan dan museum Cooper (rumah kayu, silo, beranda), LOD dan impostor |
| 9 | Post-processing dan audio |
| 10 | Preset kualitas PC, kamera luar yang lebih lengkap, mobil dan lampu malam |

## Batasan fisika dan realisme

- **Bayangan dari sunline selalu tegak lurus ke bawah**, karena cahaya datang dari garis di sumbu. Bayangan panjang seperti di referensi 1 dan 2 hanya mungkin dengan cahaya dari arah end cap.
- **Sinar Matahari lewat end cap kaca itu nyata, tapi terbatas.** Iradiansi di Saturnus 14,82 W/m2, sekitar 1,1% dari Bumi ([NASA](https://nssdc.gsfc.nasa.gov/planetary/factsheet/saturnfact.html)). Dengan arah Matahari di simulasi sekarang (sekitar 68 derajat dari sumbu stasiun), sinar yang masuk lewat end cap memotong silinder dalam jarak sekitar 800 m (2R / tan 68 derajat), jadi hanya menerangi pita di dekat satu ujung. Karena stasiun berputar, petak cahaya itu ikut berputar sekali tiap 63,4 detik seperti sorot mercusuar.
- **Referensi 3 dan 4 tampak jauh lebih besar dari stasiun kita.** Dengan jari-jari 1 km, sisi seberang hanya 2 km dan ujung ke ujung 8 km. Jumlah bangunan dan panjang sungai disesuaikan dengan ukuran ini.
- **Gravitasi turun di tempat tinggi.** Menara 70 m hanya mendapat sekitar 0,93 g di puncaknya. Tidak mengubah tampilan, tapi bisa ditampilkan di HUD saat pemain naik gedung.
