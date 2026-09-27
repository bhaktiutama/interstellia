# Tahapan Implementasi Copper Corn Station

Per 26 September 2026 · Bhakti · skala R = 1 km, L = 8 km

## Ringkasan

- **Dua blok besar:** Tahap 0 sampai 4 membangun versi gray-box (bentuk polos, warna datar, tanpa tekstur dan bayangan) untuk membuktikan semua sistem jalan. Tahap 5 sampai 10 baru mempercantik, satu aspek per tahap.
- **Ada gate keputusan di tengah:** tahap mempercantik baru dimulai setelah gray-box lolos semua uji fungsi, uji fisika otomatis, dan target 60 FPS di GPU terintegrasi.
- **Efisiensi dijaga sejak awal:** gray-box ditargetkan di bawah 50 draw call dan 200 ribu segitiga. Setiap tahap mempercantik wajib tetap di atas 30 FPS di GPU terintegrasi, atau dikurangi sebelum lanjut.

## Peta tahapan

| Tahap | Nama | Hasil yang bisa dicoba | Gate (harus lolos sebelum lanjut) |
| --- | --- | --- | --- |
| 0 | Kerangka dan harness | Layar kosong dengan HUD FPS, draw call, segitiga | Loop berjalan, tanpa error console |
| 1 | Silinder dan jalan kaki | Jalan keliling silinder berpola kotak-kotak | Jalan 360 derajat mulus, HUD 1,00 g dan 0,946 rpm |
| 2 | Fisika rotasi | Lompat, jatuhkan benda, lempar bola, lift ke sumbu, 0 g | Self-test fisika lolos semua (tabel nilai acuan) |
| 3 | Langit luar placeholder | Saturnus bola polos dan cincin lewat strip jendela | Saturnus lewat tiap 63,4 detik, tanpa z-fighting |
| 4 | Konten gray-box | Zona, rumah kotak, museum Cooper, lapangan baseball, trem, peta | Semua zona terjangkau, draw call di bawah 50 |
| Gate | Keputusan "sistem jalan" | Review bersama | 60 FPS di GPU terintegrasi pada DPR 1 |
| 5 | Cahaya Sunline dan kabut | Siang dan malam, sisi seberang berkabut kebiruan | Minimal 30 FPS di GPU terintegrasi |
| 6 | Terrain dan material | Kontur tanah, material prosedural | Minimal 30 FPS di GPU terintegrasi |
| 7 | Saturnus dan cincin versi shader | Pita awan, celah Cassini, bayangan planet dan cincin | Minimal 30 FPS di GPU terintegrasi |
| 8 | Detail props dan LOD | Rumah detail, pohon, ladang jagung dekat | Draw call di bawah 300, segitiga di bawah 2 juta |
| 9 | Post-processing dan audio | ACES, bloom, SSAO ringan, suara ambient dan langkah | Minimal 30 FPS di GPU terintegrasi |
| 10 | Mobile dan kamera luar | Kontrol sentuh lengkap, kamera V dari luar stasiun | Jalan di HP kelas menengah, acceptance criteria konsep lolos |

## Prinsip efisiensi di browser

| Teknik | Dipakai sejak | Alasan |
| --- | --- | --- |
| Geometri statis digabung per zona atau chunk | Tahap 1 | Setiap mesh = 1 draw call; menggabungkan menekan overhead CPU |
| `InstancedMesh` untuk objek berulang (rumah, pohon, tiang penanda) | Tahap 1 | Ratusan objek dalam 1 draw call |
| `MeshBasicMaterial` / `MeshLambertMaterial` di gray-box | Tahap 1 | Shader paling murah; `MeshStandardMaterial` baru di tahap 6 |
| Tanpa shadow map | Semua tahap | Cahaya dari garis sumbu mahal dibayangi; diganti AO di tahap 6 dan 9 |
| Batas device pixel ratio 1,5 + resolusi dinamis | Tahap 0 | Layar retina bisa 4x lipat piksel; faktor terbesar di GPU lemah |
| Fisika fixed timestep 120 Hz, terpisah dari render | Tahap 0 | Hasil fisika sama di 30 FPS maupun 144 FPS, bisa diuji deterministik |
| Nol alokasi objek di loop per frame | Tahap 0 | `Vector3` dan `Quaternion` dipakai ulang, supaya garbage collector tidak menyebabkan patah-patah |
| LOD berdasarkan ukuran di layar, bukan frustum culling | Tahap 8 | Di dalam silinder hampir seluruh interior selalu terlihat, jadi culling hanya sedikit membantu |
| Satu permukaan transparan (strip jendela) saja | Tahap 3 | Objek transparan menambah overdraw dan masalah urutan render |
| Semua aset prosedural dengan seed tetap, digenerate sekali saat load | Tahap 1 | Tidak ada unduhan selain three.js; dunia selalu sama untuk pengujian |
| `antialias: false` di gray-box | Tahap 0 | MSAA mahal di GPU terintegrasi; FXAA opsional di tahap 9 |

Library: three.js 0.186.1 (versi terbaru di npm per 26 September 2026), dimuat lewat import map dari cdn.jsdelivr.net dengan versi dipin. Satu file HTML.

## Tahap 0: Kerangka dan harness

**Tujuan:** fondasi yang dipakai semua tahap berikutnya, termasuk alat ukur performa.

- File HTML tunggal dengan import map three.js, objek `CONFIG` berisi semua parameter (R, L, g, kualitas, debug).
- Renderer WebGL2 dengan `powerPreference: 'high-performance'`, `antialias: false`, batas DPR 1,5.
- Loop: `requestAnimationFrame` untuk render, akumulator untuk fisika 120 Hz (maksimal 5 langkah per frame agar tidak spiral lambat).
- HUD debug: FPS, frame time (ms), `renderer.info` (draw call, segitiga), posisi pemain (theta, z, h), g lokal, rpm.
- Pesan fallback bila WebGL2 tidak tersedia; error shader ditampilkan di layar.

**Gate 0:**

- [ ] Halaman terbuka dari file lokal, console bersih.
- [ ] HUD menampilkan angka yang berubah setiap frame.

## Tahap 1: Silinder dan jalan kaki

**Tujuan:** membuktikan controller di permukaan melengkung terasa benar. Ini risiko terbesar proyek, jadi diuji paling awal.

**Isi (semua warna datar, tanpa tekstur):**

- Permukaan dalam silinder: 96 segmen keliling x 32 segmen panjang, 1 mesh, vertex color pola kotak 250 m x 250 m. Pola ini penting supaya mata bisa membaca kelengkungan dan gerak.
- Garis grid setiap 100 m (1 `LineSegments`, 1 draw call).
- Tiang penanda setiap 500 m dengan warna berbeda per zona (1 `InstancedMesh`).
- Dua end cap berupa piringan datar.
- Controller first-person: koordinat (theta, z, h), basis lokal (up = menuju sumbu), yaw dan pitch relatif basis lokal, WASD 1,4 m/s, Shift 5 m/s, pointer lock. Batas z dijaga oleh dinding end cap.
- Kontrol sentuh minimal: joystick kiri untuk jalan, geser kanan untuk melihat.

**Tidak termasuk:** lompat, gravitasi selain menapak tanah, objek selain penanda.

**Gate 1:**

- [ ] Jalan lurus ke satu arah kembali ke titik awal setelah 6,28 km, tanpa kamera terbalik atau patah.
- [ ] Melihat ke atas memperlihatkan pola kotak sisi seberang (jarak 2 km).
- [ ] HUD: g = 1,00 di tanah, rpm = 0,946, periode 63,4 detik.
- [ ] Minimal 60 FPS di GPU terintegrasi; draw call di bawah 10.

## Tahap 2: Fisika rotasi

**Tujuan:** semua efek rotasi berjalan dan terbukti benar secara angka, sebelum ada konten.

**Model:**

- **Di tanah:** pemain menempel ke permukaan, gerak di kerangka berputar.
- **Di udara (pemain maupun bola):** posisi dan kecepatan diubah ke kerangka inersia. Di sana benda bergerak lurus tanpa gaya, lalu setiap langkah dirotasi balik ke kerangka stasiun. Cara ini eksak dan lebih murah daripada menjumlahkan gaya Coriolis dan sentrifugal.
- **Hambatan udara:** diabaikan di tahap ini. Udara yang ikut berputar sebenarnya menyeret benda ke arah ko-rotasi, jadi efek ini dicatat sebagai penyederhanaan.
- **Lift ke sumbu:** pemain dibatasi di kabin; HUD menampilkan g(h) = omega^2 x (R - h).
- **Mode 0 g di sumbu:** melayang 6 arah dengan inersia.

**Fitur uji di layar:**

- Tombol Space: lompat. Tombol B: lempar bola dengan kecepatan dan sudut yang bisa diatur, lintasan digambar sebagai garis.
- Tombol G: jatuhkan bola dari ketinggian yang diatur.
- Tombol "Self-test fisika": menjalankan kasus-kasus di tabel bawah tanpa render, lalu menampilkan lulus atau gagal per kasus.

**Nilai acuan self-test** (R = 1.000 m, g = 9,81 m/s2; dihitung dengan Python lewat lintasan lurus di kerangka inersia):

| Kasus | Waktu terbang (s) | Titik mendarat | Toleransi |
| --- | --- | --- | --- |
| Lompat 2 m/s tegak lurus | 0,408 | 1,1 cm searah putaran | 5 mm |
| Lempar 20 m/s tegak lurus | 3,92 | 10,46 m searah putaran | 1% |
| Jatuhkan dari 10 m | 1,439 | 0,953 m melawan arah putaran | 1% |
| Jatuhkan dari 100 m | 4,89 | 33,30 m melawan arah putaran | 1% |
| Bola 40 m/s, 45 derajat, searah putaran | 3,33 | 107,8 m searah putaran | 1% |
| Bola 40 m/s, 45 derajat, melawan putaran | 9,74 | 204,3 m melawan arah putaran | 1% |

**Gate 2:**

- [ ] Semua kasus self-test lulus.
- [ ] Hasil sama pada 30 FPS dan 144 FPS (bukti fixed timestep bekerja).
- [ ] Naik lift: HUD turun linear dari 1,00 g ke 0,00 g di sumbu, lalu mode melayang aktif.

## Tahap 3: Langit luar placeholder

**Tujuan:** memastikan sistem dua scene, orientasi Saturnus, dan strip jendela benar, dengan objek paling sederhana.

- **Far scene** dengan kamera sendiri di titik asal. Satuan 1 = 1.000 km, near 1, far 1.000.000.
- **Urutan render:** `renderer.autoClear = false`; render far scene, `clearDepth()`, lalu render near scene.
- **Saturnus:** `SphereGeometry` 48 x 24 disquash menjadi rasio kutub 0,902 (dari radius kutub 54.364 km dan ekuator 60.268 km), `MeshBasicMaterial` warna krem.
- **Cincin:** `RingGeometry` dengan vertex color per pita (C, B, celah Cassini, A); 1 draw call.
- **Bintang:** `Points` sebanyak 4.000 titik, ukuran tetap, 1 draw call. **Matahari:** 1 sprite putih.
- **Strip jendela 30 m:** celah pada mesh silinder (lebar sudut 0,03 rad) yang diisi bidang kaca transparan (opacity 0,15).
- **Orbit:** radius 260.000 km, periode 37,57 jam, kemiringan 15 derajat terhadap bidang cincin.
- Kecepatan waktu bisa dipercepat (tombol T) untuk menguji gerak orbit.

**Gate 3:**

- [ ] Dari tepi strip jendela, Saturnus lewat sekali setiap 63,4 detik (toleransi 1%).
- [ ] Lebar sudut Saturnus sekitar 26 derajat dan cincin sekitar 55 derajat.
- [ ] Tidak ada kedipan atau z-fighting di antara far scene dan near scene.

## Tahap 4: Konten gray-box

**Tujuan:** semua zona dan interaksi ada dalam bentuk kotak polos, supaya alur jelajah dan performa dasar bisa dinilai.

| Konten | Bentuk gray-box | Draw call |
| --- | --- | --- |
| Lantai zona (kota, rekreasi, museum, pertanian, utilitas) | Vertex color per zona di mesh silinder | 0 tambahan |
| Rumah kota (sekitar 800 unit) | `InstancedMesh` kotak | 1 |
| Pohon | `InstancedMesh` kerucut | 1 |
| Ladang jagung | Blok warna hijau-kuning di lantai | 0 tambahan |
| Rumah Cooper | Beberapa kotak dengan pintu dan ruang dalam sederhana, plakat teks | sekitar 3 |
| Lapangan baseball | Garis diamond, base berupa kotak kecil | 2 |
| End cap: tangga dan lift | Kotak dan silinder polos | sekitar 4 |
| Trem | 1 kotak bergerak di jalur z dengan 5 halte | 2 |
| Kolisi | Grid 4 m di bidang (theta, z) sekitar 1,6 MB + cek AABB di sel | 0 |
| Peta (M) | Canvas 2D dari silinder yang dibuka | 0 (DOM) |

**Gate 4:**

- [ ] Semua zona terjangkau dengan jalan kaki dan trem; tidak ada tempat tersangkut.
- [ ] Pintu rumah Cooper bisa dimasuki, plakat bisa dibaca dengan tombol E.
- [ ] Draw call total di bawah 50, segitiga di bawah 200 ribu.

## Gate keputusan: "sistem jalan"

Tahap mempercantik dimulai hanya jika semua ini terpenuhi:

- [ ] Gate 0 sampai 4 lolos.
- [ ] Minimal 60 FPS di GPU terintegrasi (Intel Iris Xe / Apple M1) pada 1080p, DPR 1.
- [ ] Kamu sudah mencoba sendiri dan controller terasa nyaman (tidak pusing, orientasi jelas).
- [ ] Daftar perubahan desain dari hasil uji disepakati sebelum lanjut.

## Tahap 5 sampai 10: Mempercantik

Setiap tahap mengubah satu aspek dan diukur sendiri-sendiri. Jika FPS di GPU terintegrasi jatuh di bawah 30, efek tahap itu dikurangi atau diberi saklar kualitas sebelum lanjut ke tahap berikutnya.

| Tahap | Perubahan | Biaya utama | Cara menjaga biaya |
| --- | --- | --- | --- |
| 5 Cahaya dan kabut | Cahaya dari sumbu lewat patch shader, siklus siang dan malam (1 menit = 1 jam), kabut biru-abu berbasis jarak | Perhitungan per piksel | Ditambahkan ke shader yang sudah ada, tanpa light tambahan |
| 6 Terrain dan material | Heightmap tanah (maksimal sekitar 20 m), material prosedural, AO di-bake ke vertex | Segitiga dan shader | Segmen tambahan hanya dekat pemain; AO dihitung sekali saat load |
| 7 Saturnus dan cincin | Shader pita awan, kepadatan cincin dari tabel NASA, bayangan planet dan cincin analitik | Shader far scene | Far scene boleh dirender setengah resolusi |
| 8 Props dan LOD | Rumah dan pohon detail, jagung instancing dalam radius 150 m, impostor untuk sisi seberang | Draw call dan segitiga | LOD berdasarkan ukuran di layar, budget 300 draw call dan 2 juta segitiga |
| 9 Post dan audio | Tone mapping ACES, bloom halus, SSAO ringan, grain opsional, audio ambient dan langkah | Pass layar penuh | Setiap efek punya saklar, SSAO mati di preset Low |
| 10 Mobile dan kamera luar | Kontrol sentuh lengkap, preset otomatis untuk HP, kamera V dari luar stasiun | GPU HP lemah | Preset Low otomatis bila FPS di bawah 30 selama 2 detik |

## Catatan dan batasan

- Target FPS dan budget draw call adalah target desain, bukan hasil pengukuran. Uji di perangkat nyata dilakukan di setiap gate.
- Nilai acuan self-test mengabaikan hambatan udara. Di stasiun sungguhan, udara yang ikut berputar akan sedikit memperkecil pergeseran Coriolis, terutama untuk jatuhan dari tempat tinggi.
- Koreksi pada dokumen konsep: benda yang dijatuhkan tertinggal melawan arah putaran (bukan searah), dan pergeseran saat melompat sekitar 1 cm (bukan 3 cm). Kedua file konsep sudah diperbarui.
