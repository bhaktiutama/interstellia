# Konsep Simulasi Cooper Station

Per 26 September 2026 · Bhakti

## Ringkasan

Cooper Station disimulasikan sebagai silinder O'Neill berjari-jari 1 km dan panjang 8 km. Silinder berputar 0,946 rpm untuk menghasilkan gravitasi 1 g dan dijelajahi first-person dengan berjalan kaki di browser (three.js).

- **Skala walkable sebagai default:** keliling 6,28 km (sekitar 75 menit jalan kaki). Ada preset alternatif skala O'Neill Island Three (radius 4 km, panjang 32 km) lewat satu parameter.
- **Fisika rotasi yang terasa:** gravitasi buatan, Coriolis saat melompat atau melempar bola, dan gravitasi yang melemah menuju sumbu (0 g di pusat). Bukan sekadar gravitasi ke bawah biasa.
- **Saturnus sebagai latar utama:** terlihat lewat strip jendela dan lantai kaca, lewat di pandangan setiap 63,4 detik mengikuti rotasi stasiun.

## Referensi film dan batasan kanon

Film hanya memberi suasana dan beberapa landmark. Dimensi, jendela, dan orbit tidak disebut, jadi bagian itu adalah keputusan desain kita.

| Elemen | Status | Pegangan untuk simulasi |
| --- | --- | --- |
| Bentuk silinder O'Neill | Kanon [1] | Silinder berputar, permukaan tinggal di sisi dalam |
| Mengorbit Saturnus | Kanon [1] | Saturnus dan cincin sebagai latar luar |
| Tanah melengkung naik dan rumah terlihat di atas kepala | Kanon [2] | Horizon naik ke atas, kota terlihat terbalik di langit |
| Adegan bola baseball memecahkan kaca rumah di atas | Kanon [2] | Demo lempar bola dengan lintasan Coriolis |
| Replika rumah pertanian Cooper sebagai museum | Kanon [2][3] | Landmark utama yang bisa dimasuki |
| Dinamai dari Murphy Cooper | Kanon [3] | Papan nama dan plakat di museum |
| Mayoritas lahan untuk pertanian, cahaya besar yang bisa diredupkan untuk siang dan malam | Wiki penggemar, bukan dialog film [3] | Ladang jagung dominan, lampu sumbu dengan siklus hari |
| Dimensi, rpm, jendela, radius orbit | Tidak disebut | Ditetapkan di bagian berikut sebagai keputusan desain |

## Parameter stasiun dan fisika rotasi

Default walkable (R = 1.000 m) berputar 0,946 rpm. Itu jauh di bawah batas nyaman sekitar 2 rpm yang umum dipakai di literatur habitat berputar. Coriolis saat berjalan hanya 2,83% g.

Rumus yang dipakai (g target = 9,81 m/s2):

```
omega = sqrt(g / R)
g(h)  = omega^2 * (R - h)          gravitasi pada ketinggian h
a_cor = -2 * (omega x v)           percepatan Coriolis
a_cf  = -omega x (omega x r)       percepatan sentrifugal
```

| Parameter | Walkable (default) | O'Neill Island Three |
| --- | --- | --- |
| Radius R (m) | 1.000 | 4.000 |
| Panjang L (m) | 8.000 | 32.000 |
| Kecepatan sudut omega (rad/s) | 0,09905 | 0,04952 |
| Rotasi (rpm) | 0,946 | 0,473 |
| Periode rotasi (s) | 63,4 | 126,9 |
| Kecepatan tanah di lingkar (m/s) | 99,0 | 198,1 |
| Keliling (km) | 6,28 | 25,13 |
| Jalan kaki keliling, 1,4 m/s (menit) | 75 | 299 |
| Jalan kaki ujung ke ujung (menit) | 95 | 381 |
| Coriolis saat jalan 1,4 m/s (m/s2, % g) | 0,277 (2,83%) | 0,139 (1,41%) |
| Selisih gravitasi kepala vs kaki, tinggi 1,7 m (%) | 0,170 | 0,042 |

Angka di tabel diturunkan dari rumus di atas (dihitung dengan Python). Dimensi Island Three (diameter 8 km, panjang 32 km) adalah angka yang umum dikutip untuk desain O'Neill, belum dicek ke sumber primer.

**Efek yang wajib terasa di simulasi:**

- **Arah bawah = keluar radial.** Pemain selalu berdiri dengan kepala menghadap sumbu silinder.
- **Gravitasi melemah ke atas.** Di menara 100 m gravitasi tinggal 90%, di sumbu 0 g. Lift ke sumbu menjadi pengalaman zero-g.
- **Coriolis di udara.** Saat melompat 2 m/s, pergeseran hanya sekitar 1 cm (tidak terasa). Efek besar muncul pada lemparan dan benda yang jatuh dari tempat tinggi.
- **Demo baseball (dihitung untuk R = 1 km):**
    - Bola 40 m/s pada sudut 45 derajat mendarat 108 m bila dipukul searah putaran, dan 204 m bila dipukul melawan arah putaran.
    - Bola 50 m/s (batas realistis pukulan) paling jauh mendarat 29 derajat keliling (sekitar 507 m).
    - Untuk mencapai rumah tepat di atas kepala (180 derajat) dibutuhkan sekitar 79 m/s melawan arah putaran pada sudut 11 derajat, dengan waktu terbang 43,7 detik. Jadi adegan film itu hanya masuk akal dengan pukulan super, dan simulasi akan menunjukkannya apa adanya.

**Keputusan model:**

- Fisika dihitung di kerangka berputar: stasiun diam, alam semesta luar yang berputar.
- Saat menapak tanah cukup gravitasi radial. Saat di udara ditambah gaya sentrifugal dan Coriolis secara eksplisit.
- Proyektil (bola) diintegrasikan di kerangka inersia lalu ditransformasikan ke kerangka stasiun, sehingga lintasannya eksak.

## Orbit Saturnus dan pemandangan luar

Rekomendasi: orbit melingkar 260.000 km dari pusat Saturnus, miring 15 derajat terhadap bidang cincin. Saturnus tampak selebar 26,1 derajat dan cincin A selebar 55,5 derajat di langit, dengan cincin terlihat terbuka (tidak edge-on).

| Radius orbit (km) | Periode orbit (jam) | Kecepatan orbit (km/s) | Lebar sudut Saturnus, ekuator (derajat) | Lebar sudut tepi luar cincin A (derajat) |
| --- | --- | --- | --- | --- |
| 210.000 | 27,27 | 13,44 | 32,0 | 66,2 |
| 260.000 (rekomendasi) | 37,57 | 12,08 | 26,1 | 55,5 |
| 450.000 | 85,55 | 9,18 | 15,3 | 33,8 |

Derivasi: T = 2 pi sqrt(r^3 / GM), lebar sudut = 2 atan(R / r). Nilai yang dipakai: GM = 37,931 x 10^6 km3/s2 dan radius ekuator 60.268 km [4], tepi luar cincin A 136.780 km [5].

**Data visual Saturnus untuk shader:**

- **Bentuk:** oblate, flattening 0,09796 (radius kutub 54.364 km) [4].
- **Cincin (radius dari pusat, km):** D 66.900 s.d. 74.510, C 74.658 s.d. 91.975, B 91.975 s.d. 117.507, celah Cassini, A 122.340 s.d. 136.780, F 139.826 [5]. Dijadikan tekstur 1D kepadatan radial prosedural.
- **Bayangan:** bayangan planet di cincin dan bayangan cincin di planet, dihitung analitik di shader (ray vs bola dan bidang).
- **Matahari:** titik kecil sangat terang, lebar sekitar 3,3 menit busur (diameter Matahari dibagi jarak 1.432 juta km). Iradiansi di Saturnus 14,82 W/m2 [4], sekitar 1,1% dari Bumi. Konsekuensinya interior stasiun harus diterangi lampu buatan, cocok dengan "cahaya besar" di wiki film.

**Catatan:** radius 260.000 km masih di dalam cincin E yang tipis dan berdebu (180.000 s.d. 480.000 km) [5]. Di simulasi ini hanya dipakai sebagai bahan narasi (pelindung debu di jendela), bukan kendala teknis. Posisi relatif terhadap bulan-bulan Saturnus belum dicek.

**Orientasi stasiun:** sumbu silinder tegak lurus bidang orbit. Dari jendela, Saturnus lewat sekali setiap 63,4 detik (periode rotasi stasiun), sementara gerak orbit 37,57 jam hanya menggeser latar pelan-pelan.

## Layout dunia

Silinder 8 km dibagi 7 zona sepanjang sumbu. Lahan menerus 360 derajat seperti di film, dipotong satu strip jendela memanjang supaya Saturnus terlihat di bawah kaki dan di langit.

| Posisi sepanjang sumbu z (m) | Zona | Isi utama | Fungsi di simulasi |
| --- | --- | --- | --- |
| 0 s.d. 150 | End cap A: spaceport | Dok kapal di sumbu (0 g), lift di dinding ujung turun ke tanah | Titik spawn alternatif, demo zero-g |
| 150 s.d. 1.200 | Kota pusat | Rumah suburban, jalan utama, sekolah, klinik, stasiun trem | Spawn default, rumah "di atas kepala" terlihat jelas |
| 1.200 s.d. 1.800 | Rekreasi | Lapangan baseball, taman, danau kecil | Demo lempar bola Coriolis |
| 1.800 s.d. 2.300 | Museum Cooper Farm | Replika rumah pertanian, beranda, truk pickup, rak buku, ladang jagung kecil | Landmark utama, interior bisa dimasuki, plakat Murphy Cooper |
| 2.300 s.d. 6.500 | Pertanian | Ladang jagung dominan, rumah kaca, kanal irigasi, barisan pohon | Skala dan suasana sunyi, trem melintas |
| 6.500 s.d. 7.850 | Utilitas | Bengkel, pengolahan air dan udara, gudang | Detail teknis stasiun |
| 7.850 s.d. 8.000 | End cap B: engineering | Dek observasi berlantai kaca di bawah permukaan tanah | Saturnus lewat di bawah kaki setiap 63,4 detik |

**Elemen melintang:**

- **Skyway (strip jendela):** 1 strip kaca selebar 30 m sepanjang silinder. Dari sisi seberang tampak sebagai pita gelap di langit berisi bintang dan Saturnus yang bergerak. Dari dekat bisa dilihat ke bawah lewat kaca. Jumlah strip bisa diatur 0, 1, atau 3.
- **Sunline:** tabung cahaya di sepanjang sumbu, dengan siklus siang dan malam lewat peredupan. Default: 1 menit nyata = 1 jam stasiun (satu hari = 24 menit).
- **Trem:** satu jalur lurus sepanjang sumbu z dengan 5 halte (spaceport, kota, museum, pertanian, utilitas), supaya jarak 8 km tidak melelahkan.
- **Dinding end cap:** bertingkat seperti amfiteater yang naik ke sumbu, dengan tangga dan lift. Makin ke atas gravitasi makin ringan.

## Pengalaman berjalan kaki dan kontrol

Inti pengalaman adalah berjalan first-person di tanah yang melengkung ke atas, jadi controller harus dibuat sendiri. `PointerLockControls` bawaan three.js mengasumsikan arah atas tetap (+Y), sedangkan di sini arah atas berubah di setiap titik.

**Cara kerja controller:**

1. Posisi pemain disimpan dalam koordinat silinder (theta, z, h): sudut keliling, posisi sepanjang sumbu, dan ketinggian di atas tanah.
2. Setiap frame dibentuk basis lokal: up = menuju sumbu, forward = arah pandang yang diproyeksikan ke bidang singgung, right = cross(forward, up).
3. Yaw dan pitch mouse diterapkan relatif ke basis lokal ini, lalu kamera dibentuk dari basis tersebut.
4. Gerak WASD mengubah theta dan z (delta theta = jarak / R), sehingga berjalan lurus otomatis mengikuti lengkungan.
5. Tabrakan dengan bangunan memakai grid kolisi 2D di peta (theta, z), cukup untuk dunia yang sebagian besar datar.

| Input | Aksi |
| --- | --- |
| Mouse | Melihat (pointer lock) |
| W A S D | Berjalan 1,4 m/s |
| Shift | Lari 5 m/s |
| Space | Lompat (dengan Coriolis) |
| E | Interaksi: pintu, plakat, naik trem, tombol lift |
| B | Lempar bola baseball dari posisi pemain (lintasan diperlihatkan) |
| T | Percepat waktu siang dan malam |
| M | Peta silinder yang dibuka (theta x z) dengan posisi pemain |
| V | Kamera luar: terbang keluar dan melihat stasiun berputar dengan Saturnus |
| Tab | Panel pengaturan (skala, jumlah strip jendela, kualitas) |
| Layar sentuh | Joystick kiri untuk jalan, geser kanan untuk melihat |

**Pengalaman khusus yang direncanakan:**

- **Naik ke sumbu:** lift di dinding end cap. HUD menampilkan gravitasi yang turun dari 1,00 g ke 0 g. Di sumbu pemain beralih ke mode melayang 6 arah.
- **Menjatuhkan benda dari menara:** benda tidak mendarat tepat di bawah, tapi tertinggal melawan arah putaran (dari menara 100 m bergeser sekitar 33 m).
- **Berdiri di atas kaca Skyway:** Saturnus dan cincinnya lewat di bawah kaki, bintang berputar.
- **Museum Cooper Farm:** interior rumah bisa dimasuki, dengan plakat teks singkat tentang Murphy Cooper.

## Arsitektur teknis three.js

Satu file HTML. three.js dimuat lewat import map dari cdn.jsdelivr.net dengan versi yang dipin. Semua tekstur dan model dibuat prosedural (tanpa file aset). Dunia dirender dari dua scene terpisah: near (stasiun, satuan meter) dan far (Saturnus, bintang, Matahari).

**Kerangka koordinat:**

- **Near scene:** kerangka stasiun (ikut berputar, jadi stasiun diam di layar). Sumbu silinder = sumbu Z dunia, titik asal di tengah silinder, satuan meter. Koordinat maksimum 4.000 m (walkable) atau 16.000 m (O'Neill) masih aman untuk presisi float32.
- **Far scene:** kamera selalu di titik asal, hanya rotasi. Orientasinya = rotasi stasiun terhadap ruang inersia pada waktu t, dikalikan orientasi kamera pemain. Satuannya km dengan skala sendiri, jadi tidak ada masalah depth buffer untuk objek sejauh 260.000 km.
- **Urutan render:** far scene dulu, clear depth, lalu near scene. Strip jendela dan lantai kaca bermaterial transparan, jadi far scene hanya terlihat lewat bukaan itu.

| Modul | Tanggung jawab |
| --- | --- |
| CONFIG | Semua parameter: R, L, g, jumlah strip jendela, radius orbit, kecepatan waktu, preset kualitas |
| WorldGen | Peta zona dan heightmap di bidang (theta, z), penempatan rumah, pohon, ladang dengan seed tetap |
| Terrain | Mesh tanah per chunk yang dibungkus ke silinder, LOD per jarak |
| Props | Rumah, pohon, jagung, pagar sebagai InstancedMesh dari geometri prosedural |
| Landmarks | Rumah Cooper (interior), lapangan baseball, end cap, lift, trem |
| Lighting | Patch shader material untuk cahaya dari sumbu, siklus siang dan malam |
| FarSky | Saturnus oblate dengan pita awan, cincin, bayangan, Matahari, bintang |
| Player | Controller basis lokal, kolisi grid (theta, z), mode jalan, lari, melayang |
| Physics | Gravitasi radial, sentrifugal dan Coriolis saat di udara, proyektil di kerangka inersia |
| Tram | Kendaraan pada jalur z dengan halte, pemain bisa naik |
| UI | HUD (g lokal, rpm, jam stasiun), peta, panel pengaturan, fallback bila WebGL2 tidak ada |

**Urutan per frame:**

1. Update waktu: sudut rotasi stasiun (omega x t), posisi orbit, jam siang dan malam.
2. Input, lalu Player dan Physics di kerangka berputar.
3. Proyektil diintegrasikan di kerangka inersia, lalu dirotasi balik ke kerangka stasiun.
4. Streaming chunk dan LOD berdasarkan posisi pemain.
5. Render far scene, lalu near scene, lalu post-processing.

## Rendering dan visual

Kesan skala ditentukan tiga hal: kabut udara yang membuat sisi seberang silinder (2 km jauhnya) tampak kebiruan, cahaya yang datang dari sumbu, dan detail tanah yang tetap terbaca saat terlihat "di langit".

| Aspek | Pendekatan | Alasan |
| --- | --- | --- |
| Tanah | Grid (theta, z) dengan heightmap kecil (maks. sekitar 20 m), dibungkus ke radius R di vertex shader | Satu sumber data untuk mesh, kolisi, dan peta |
| Cahaya Sunline | Arah cahaya per fragmen = menuju sumbu, dipasang lewat onBeforeCompile pada MeshStandardMaterial | Light bawaan three.js hanya directional/point, tidak bisa berupa garis |
| Bayangan | Tanpa shadow map real-time untuk Sunline; ambient occlusion di-bake ke vertex plus SSAO ringan | Shadow map untuk sumber cahaya garis mahal dan rawan artefak |
| Kabut interior | Fog berbasis jarak berwarna biru-abu, kepadatan naik pelan dengan jarak | Kota di atas kepala terasa jauh, sesuai tampilan film |
| Langit interior | Tidak ada langit: di atas selalu tanah seberang, diselimuti kabut dan cahaya Sunline | Topologi silinder yang benar |
| Saturnus | Bola oblate dengan shader pita awan prosedural (noise diregangkan menurut lintang) | Tanpa file tekstur |
| Cincin | Annulus dengan tekstur kepadatan radial dari tabel cincin NASA, sedikit tembus pandang, hamburan maju bila dilihat melawan cahaya | Celah Cassini dan batas cincin terlihat benar |
| Bintang | Starfield prosedural seperti di simulasi Gargantua | Konsisten dengan proyek sebelumnya |
| Jendela dan kaca | Material transparan dengan pantulan tipis, far scene terlihat di baliknya | Saturnus lewat di bawah kaki |
| Post-processing | Tone mapping ACES, bloom halus untuk Sunline dan Matahari, SSAO, film grain opsional | Tampilan sinematik tanpa beban berlebihan |
| Kamera luar (V) | Model eksterior silinder low-poly dengan strip jendela bercahaya, berputar di kerangka inersia | Memperlihatkan skala stasiun terhadap Saturnus |

**Arah gaya visual:** Amerika pedesaan yang hangat (rumah kayu, ladang jagung, truk pickup) di dalam struktur teknik yang dingin, sesuai kontras di akhir film.

## Budget performa dan LOD

Target 60 FPS di laptop dengan GPU diskrit dan minimal 30 FPS di GPU terintegrasi (Intel Iris Xe / Apple M1) pada 1080p. Angka budget di bawah adalah target desain yang harus divalidasi di perangkat nyata.

| Sumber daya | Budget per frame | Cara menjaga |
| --- | --- | --- |
| Draw call | di bawah 300 | InstancedMesh per jenis prop, merge geometri statis per chunk |
| Segitiga | di bawah 2 juta | LOD 3 tingkat per chunk, impostor untuk rumah dan pohon di sisi seberang |
| Tanaman jagung | Mesh instance hanya dalam radius 150 m, sisanya tekstur ladang | Jutaan batang jagung tidak mungkin di-instance semua |
| Memori GPU | di bawah 500 MB | Tekstur prosedural di-generate sekali ke canvas atau render target |
| Waktu generate dunia | di bawah 5 detik saat load | Seed tetap, chunk di-generate bertahap, layar loading |

**Strategi LOD khas silinder:** jarak tidak monoton seperti di dunia datar. Tanah tepat di atas kepala berjarak 2R (2 km) tapi memenuhi layar, jadi LOD dipilih berdasarkan jarak 3D nyata dan ukuran di layar, bukan jarak di permukaan.

**Pembagian chunk:** 32 segmen keliling x 32 segmen panjang (walkable: sekitar 196 m x 250 m per chunk). Preset kualitas Low, Medium, dan High mengatur kepadatan instance, SSAO, dan resolusi render.

## Roadmap implementasi

Implementasi dibagi 5 fase. F1 saja sudah menghasilkan demo yang bisa dijelajahi (jalan kaki keliling silinder kosong dengan gravitasi yang benar). Setiap fase ditutup gate yang bisa diuji.

| Fase | Isi | Gate penutup |
| --- | --- | --- |
| F1 Fondasi (MVP) | Silinder + tanah, controller jalan, gravitasi radial | G1: jalan keliling 360 derajat mulus, HUD g dan rpm benar |
| F2 Langit luar | Saturnus + cincin, bintang dan Matahari, Skyway kaca | G2: Saturnus lewat setiap 63,4 detik |
| F3 Konten | Zona + rumah, jagung instancing, museum + trem | G3: 30 FPS di iGPU, preset Medium |
| F4 Fisika demo | Lompat Coriolis, bola baseball, lift ke sumbu dan 0 g | G4: bola mendarat 108 m / 204 m sesuai hitungan |
| F5 Polish | Kabut + post-processing, peta, audio, mobile, kamera luar | Semua acceptance criteria lolos |

Durasi per fase belum ditetapkan; tergantung apakah dikerjakan sekaligus atau bertahap per sesi.

## Acceptance criteria

Simulasi dianggap selesai bila 10 kriteria ini lolos. Angka pembanding diambil dari bagian parameter dan orbit di atas.

- [ ] Terbuka dari satu file HTML tanpa aset eksternal selain three.js dari CDN, tanpa error di console.
- [ ] Pemain bisa berjalan keliling 360 derajat dan dari ujung ke ujung tanpa tersangkut, kamera melompat, atau orientasi terbalik.
- [ ] Dari zona kota, rumah dan jalan di sisi seberang terlihat di atas kepala, berkabut kebiruan.
- [ ] HUD menampilkan g lokal 1,00 di tanah dan turun linear saat naik lift sampai 0 di sumbu.
- [ ] Saturnus terlihat lewat Skyway dan lantai kaca, lewat sekali setiap 63,4 detik (toleransi 1%).
- [ ] Cincin menampilkan celah Cassini, bayangan planet di cincin, dan bayangan cincin di planet.
- [ ] Bola 40 m/s pada 45 derajat mendarat sekitar 108 m searah putaran dan sekitar 204 m bila melawan arah putaran (toleransi 5%).
- [ ] Replika rumah Cooper bisa dimasuki dan plakat Murphy Cooper bisa dibaca.
- [ ] Mengganti preset ke skala O'Neill (R 4 km, L 32 km) membangun ulang dunia dan HUD menunjukkan 0,473 rpm.
- [ ] Minimal 30 FPS di GPU terintegrasi pada preset Medium, 1080p (diukur di perangkat nyata).

## Keputusan terbuka dan risiko

Empat keputusan perlu dijawab sebelum implementasi. Default di dokumen ini sudah dipakai dan bisa diganti.

| Keputusan | Default di dokumen | Alternatif | Dampak |
| --- | --- | --- | --- |
| Skala stasiun | Walkable R 1 km, L 8 km | O'Neill R 4 km, L 32 km | Skala besar lebih megah, tapi 4x lebih lama dijelajahi dan lebih berat dirender |
| Jendela | 1 strip Skyway + lantai kaca di end cap | 0 strip (lahan penuh, paling mirip film) atau 3 strip (desain O'Neill klasik) | Tanpa strip, Saturnus hanya terlihat di dek observasi |
| Kesetiaan ke film | Terinspirasi, dengan fisika yang benar | Meniru adegan film apa adanya | Adegan bola di film butuh pukulan sekitar 79 m/s; fisika yang benar tidak bisa meniru itu |
| Bentuk file | 1 file HTML, three.js dari CDN | Proyek multi-file (Vite) | Satu file mudah dibagikan; multi-file lebih mudah dirawat bila fitur bertambah |

| Risiko | Kemungkinan | Mitigasi |
| --- | --- | --- |
| Controller silinder terasa aneh (kamera berputar tiba-tiba) | Sedang | Basis lokal dihaluskan antar frame, diuji di F1 sebelum konten |
| Performa jatuh karena ladang jagung dan kota di sisi seberang | Tinggi | Instancing hanya dekat pemain, impostor dan tekstur untuk jarak jauh |
| Cahaya dari sumbu tanpa bayangan terlihat datar | Sedang | AO yang di-bake, SSAO, variasi warna material |
| File HTML tunggal menjadi sangat besar | Sedang | Modul dipisah rapi di dalam file, lebih mengandalkan generator prosedural daripada data |
| Detail Cooper Station di film minim, hasil bisa terasa beda dari ingatan penonton | Rendah | Fokus pada landmark kanon: tanah melengkung, rumah Cooper, baseball |

## Sumber

1. [Interstellar (film), Wikipedia](https://en.wikipedia.org/wiki/Interstellar_(film))
2. [Ground Into Sky: The Topology of Interstellar, The Avery Review](https://averyreview.com/issues/6/ground-into-sky)
3. [Cooper Station, Interstellar Wiki (Fandom)](https://interstellarfilm.fandom.com/wiki/Cooper_Station)
4. [Saturn Fact Sheet, NASA NSSDCA](https://nssdc.gsfc.nasa.gov/planetary/factsheet/saturnfact.html)
5. [Saturnian Rings Fact Sheet, NASA NSSDCA](https://nssdc.gsfc.nasa.gov/planetary/factsheet/satringfact.html)
