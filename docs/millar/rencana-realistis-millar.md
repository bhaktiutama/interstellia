# Rencana Millar's World Versi Realistis

Per 29 September 2026 · Status: R1, R1b, R2, R3, dan R4 selesai (lihat bagian "Status"), berikutnya R5

## Ringkasan

- Arah baru dari pemilik: hanya laut, tanpa daratan yang muncul ke permukaan. Tone mengikuti foto acuan: langit mendung abu, laut abu kebiruan yang berombak kecil, kabut di cakrawala, gelombang raksasa gelap bergaris buih putih. Dibuat serealistik mungkin, dengan 5 preset kualitas seperti Copper Corn Station.
- Prototipe low poly dipakai sebagai kerangka (angka, gelombang, jam dilatasi, HUD, bahasa). Semua tampilannya diganti: laut FFT, langit awan mendung, pipeline post seperti Cooper.
- Urutan: R1 fondasi (preset, post, langit mendung), R2 laut realistis, R3 pemain di air, R4 gelombang raksasa realistis, R5 audio. Shuttle, misi, dan pandangan orbit tetap di M3 dan M4 konsep.

## Yang terlihat di foto acuan

Foto acuan hanya dipakai untuk warna dan suasana. Kendaraan dan pakaian di foto adalah desain film dan tidak ditiru (shuttle tetap KS-07 orisinal).

| Unsur | Yang terlihat | Cara meniru suasananya |
| --- | --- | --- |
| Langit | Mendung rata abu terang, tanpa matahari; satu foto promosi bernuansa senja keemasan | Lapisan awan tebal prosedural, cahaya menyebar dari atas; suasana senja jadi pilihan (keputusan 1) |
| Laut dekat | Abu kebiruan gelap, ombak kecil berpuncak tajam, kilau putih di puncak, buih kecil | Spektrum ombak angin (FFT), Fresnel ke warna langit, buih dari lipatan ombak |
| Laut jauh | Makin terang dan rata, menyatu dengan kabut di cakrawala | Kabut ketinggian + pantulan langit makin kuat di sudut rendah |
| Kedalaman | Air setinggi lutut sampai paha, dasar tidak terlihat jelas karena air keruh abu | Penyerapan warna per kedalaman; dasar laut samar, tidak pernah muncul |
| Di sekitar kaki | Cipratan putih dan riak melingkar | Simulasi riak lokal + partikel cipratan |
| Gelombang raksasa | Dinding abu gelap bertekstur halus, garis buih putih mengalir turun, kaki gelombang berkabut | Normal detail berskala besar, tekstur buih mengalir, kabut semburan di kaki dan puncak |

Ada dua jenis gelombang, jangan tertukar:

| Jenis | Tinggi | Asal | Di kode |
| --- | --- | --- | --- |
| Gelombang raksasa (tsunami goyangan planet) | sekitar 1.200 m, tidak berubah dari konsep | Konsep (film, Interstellar Wiki) | `CONFIG.wave.H` |
| Ombak angin sehari-hari di sekitar kaki | tinggi signifikan 0,35 m, panjang 0,9-6,5 m | Perkiraan dari foto acuan, bukan dari sumber | `CONFIG.chop.Hs`, bisa diatur |

Ombak angin dibatasi kedalaman air (0,4-0,8 m): di air sedangkal ini ombak pecah bila lebih tinggi dari sekitar 0,8 x kedalaman.

## Perubahan dari prototipe

| Bagian | Prototipe | Versi realistis |
| --- | --- | --- |
| Gaya | Low poly, warna per segi | Realistis, HDR, ACES, color grading dingin |
| Laut | Riak sinus di bawah 10 cm, grid 2 m | FFT (Tessendorf) 2-3 kaskade, ombak angin 0,35 m (gelombang raksasa tetap 1.200 m), grid LOD rapat (sekitar 10-25 cm di dekat kaki) |
| Dasar laut | Gosong pasir dan dasar yang muncul saat air surut | Selalu di bawah air (paling dangkal sekitar 0,15 m saat surut), samar lewat air keruh |
| Langit | Kubah bersegi, Gargantua jelas | Awan mendung prosedural; Gargantua sesuai keputusan 1 |
| Cahaya | Satu arah dari Gargantua | Cahaya langit menyebar (mendung), kilau lemah dari arah Gargantua, pantulan dari cubemap langit |
| Gelombang | Pita low poly, alur buih kasar | Muka rapat di dekat pemain, normal detail, buih mengalir, kabut kaki gelombang, partikel semburan |
| Air surut | Dasar laut terbuka | Air makin dangkal dan arus ke arah gelombang terasa; tidak ada daratan |
| Post | Tidak ada | Seperti Cooper: HDR, bloom, ACES, FXAA, ditambah grading, grain, vinyet |
| Kualitas | Satu setelan | 5 preset + turun otomatis |

## Preset kualitas

Nama dan perilaku sama dengan Copper Corn Station: Ultra, Tinggi, Sedang, Rendah, Hemat (untuk MacBook M1). Turun otomatis bila FPS di bawah 30 selama 4 s, tersimpan di localStorage, bisa dipaksa `?preset=hemat`.

Angka di bawah adalah titik awal desain, belum diukur. Angka final ditetapkan setelah diukur dengan alat ukur GPU (seperti `GPUT` di Cooper) di GTX 1060 dan M1.

| Setelan | Ultra | Tinggi | Sedang | Rendah | Hemat |
| --- | --- | --- | --- | --- | --- |
| Skala render (dpr) | 2,0 | 1,5 | 1,25 | 1,0 | 0,85 |
| Ombak | FFT 256, 3 kaskade | FFT 256, 2 kaskade | FFT 128, 2 kaskade | FFT 64, 1 kaskade | Gerstner 12 gelombang + peta normal |
| Grid laut (LOD) | 8 cincin, sel dekat 10 cm | 7 cincin, 15 cm | 6 cincin, 20 cm | 5 cincin, 30 cm | 5 cincin, 40 cm |
| Buih | Lipatan ombak + sisa buih memudar | Sama | Lipatan ombak saja | Dari tinggi ombak | Dari tinggi ombak |
| Pantulan | Cubemap langit 256, diperbarui bergilir | 256 | 128 | 64, statis | 64, statis |
| Awan | Ray-march 48 langkah | 32 langkah | 2 lapis 2D | 1 lapis 2D | 1 lapis 2D |
| Gargantua (bila tampak) | Shader lensa, cubemap bergilir | Sama | Dirender sekali saat muat | Gambar statis | Gambar statis |
| Riak di sekitar kaki | Simulasi 256 x 256 | 256 x 256 | 128 x 128 | 64 x 64 | Cincin riak sederhana |
| Cipratan | 4.000 partikel | 2.500 | 1.500 | 600 | 300 |
| Kabut semburan gelombang | Volumetrik ringan | Lembar lapis 6 | Lapis 4 | Lapis 2 | Lapis 2 |
| Kaustik dasar laut | Ya | Ya | Tidak | Tidak | Tidak |
| Post | Bloom 6 tingkat, grading, grain | Bloom 6 tingkat | Bloom 4 tingkat | Bloom 2 tingkat | Bloom 2 tingkat, tanpa grain |

Cadangan: bila browser tidak mendukung render ke tekstur float (`EXT_color_buffer_float` atau half float), FFT diganti Gerstner seperti Hemat.

## Tahapan

| Tahap | Isi | Yang diuji pemilik |
| --- | --- | --- |
| R1 Fondasi dan tone | Sistem preset (pilihan di layar awal, turun otomatis, `?preset=`), pipeline post (HDR, bloom, ACES, FXAA, grading dingin, grain, vinyet), langit mendung prosedural + cubemap pantulan, kabut ketinggian, alat ukur GPU di HUD. Laut sementara tetap versi prototipe tapi diberi warna dan kabut baru | Tone langit dan cakrawala mirip acuan, FPS tiap preset |
| R1b Lensa Gargantua | Porting shader ray tracing Schwarzschild dari `experiences/gargantua/` (lintasan cahaya dibelokkan, piringan akresi, Doppler) ke shader langit, dirender ke cubemap. Menggantikan Gargantua prosedural R1 (cincin utuh tanpa distorsi). Bagian atas dan bawah bayangan memperlihatkan belakang piringan yang terbelokkan, seperti di experience Gargantua | Bentuk sama dengan experience Gargantua, FPS tiap preset |
| R2 Laut realistis | FFT 2-3 kaskade di GPU, grid LOD mengikuti kamera (tidak "berenang"), shading: Fresnel, pantulan cubemap, hamburan di puncak ombak, penyerapan warna, buih; dasar laut selalu terendam, samar; kaustik di Ultra/Tinggi. Ombak ikut angin, tidak tergantung FPS | Laut dekat dan jauh mirip foto, tanpa NaN, FPS |
| R3 Pemain di air | Riak lokal (simulasi tinggi air di sekitar kaki), cipratan tiap langkah, jejak air, langkah berat 1,3 g, gerak kepala di air (pola `BOB` Cooper), kedalaman di HUD mengikuti ombak | Rasa berjalan di air setinggi lutut |
| R4 Gelombang raksasa | Muka gelombang beresolusi tinggi dekat pemain, normal detail berskala besar, buih mengalir turun, kabut di kaki dan puncak, air surut tanpa daratan (arus terlihat di permukaan), langit bergoyang, urutan tersapu (buih putih, kamera terguling, di bawah air, kembali) | Kesan skala dan ketegangan |
| R5 Audio | Disintesis: angin, gemericik ombak, langkah di air, gemuruh gelombang frekuensi rendah makin keras, getaran | Suasana |
| M3, M4 (konsep) | Shuttle KS-07 mendarat di air, misi suar, pandangan orbit, sinematik kedatangan | Alur permainan |

Tiap tahap ditutup dengan skrip uji di `tools/` (pola `uji_*.py`): halaman termuat tanpa error, angka fisika (1,3 g, lompat 77%, jam dilatasi, kecepatan gelombang), tidak ada nilai tidak valid di shader, preset bisa berganti.

## Risiko

| Risiko | Dampak | Penanganan |
| --- | --- | --- |
| FFT dan pantulan berat di M1 | FPS rendah di Hemat | Hemat memakai Gerstner dan cubemap statis; ukur sebelum menetapkan angka |
| NaN di shader air (normal, `pow`, `sqrt`) | Titik putih berkedip di M1, tidak terlihat di sandbox | Semua `normalize()` dijaga, uji nilai tidak valid seperti `uji_suasana.py` |
| Skala 0,1 m sampai 270 km | Z-fighting | Tetap depth logaritmik seperti prototipe |
| Sandbox tanpa GPU | Tampilan dan FPS tidak bisa dinilai di sini | Pemilik menilai visual; di sini hanya cek muat, angka, dan nilai tidak valid |

## Keputusan

Pemilik meminta mulai implementasi tanpa memilih; R1 memakai pilihan yang disarankan (1a + senja sebagai pilihan, 2 disimpan, 3 dan 4 seperti saran). Masih bisa diganti.

Daftar pilihan semula:

1. Langit dan Gargantua. Di foto acuan langit tertutup awan dan Gargantua tidak tampak, padahal di konsep Gargantua memenuhi langit.
   - a. Mendung dengan Gargantua samar menembus awan, dan sesekali ada celah awan yang memperlihatkannya (disarankan)
   - b. Mendung penuh, Gargantua tidak tampak (paling mirip foto)
   - c. Gargantua selalu jelas seperti prototipe
   - Tambahan: suasana "senja keemasan" seperti foto promosi dijadikan pilihan di panel (disarankan: ya, sebagai pilihan kedua)
2. Prototipe low poly: disimpan sebagai `experiences/millar/prototipe.html` tanpa kartu menu (disarankan), atau dihapus?
3. Interval gelombang: mode permainan 4-6 menit sebagai bawaan dengan opsi mode realistis (disarankan, sama dengan konsep)?
4. Tersapu: sampai shuttle ada di M3, kembali ke titik awal dengan penalti waktu seperti prototipe (disarankan)?

## Status R1

Selesai 29 September 2026. File: `experiences/millar/index.html`; prototipe low poly disimpan di `experiences/millar/prototipe.html` (tanpa kartu menu).

| Bagian | Isi |
| --- | --- |
| Preset | Ultra, Tinggi, Sedang, Rendah, Hemat; pilihan di layar awal, P untuk ganti, turun otomatis bila FPS < 30 selama 4 s, `?preset=hemat`, tersimpan di localStorage `millar.preset` |
| Post | HDR half float, MSAA 4x di Ultra/Tinggi, bloom 6/6/4/2/2 tingkat, ACES, grading pudar dingin, vinyet, grain (mati di Hemat), FXAA |
| Langit | Cubemap 512/384/256/192/128 diperbarui satu sisi per frame (per 2 frame di Rendah/Hemat). Awan volumetrik 48/32 langkah di Ultra/Tinggi, 2D dua lapis di Sedang, satu lapis di Rendah/Hemat |
| Gargantua | Samar di balik awan; suasana Otomatis membuka celah awan di sekitarnya sekitar 70 s tiap 5 menit. Bayangan, piringan (sisi kiri lebih terang), cincin terbelokkan, cincin foton. Masih prosedural, bukan lensa gravitasi |
| Suasana | Otomatis, Mendung, Senja (tombol N atau layar awal), berganti halus 2,5 s |
| Laut | Ombak angin Gerstner 16/16/14/12/10 gelombang + riak halus 12/8/6/4/2 di normal piksel, grid dekat 0,35-1,0 m sampai 70 m, cincin jauh sampai sekitar 285 km. Pantulan cubemap, Fresnel, air keruh dengan dasar laut samar, buih dari lipatan ombak, kabut ke warna cakrawala |
| Tanpa daratan | Dasar laut -0,42 sampai -0,78 m, air surut hanya 0,2 m: dasar tertinggi tetap di bawah air terendah (diuji 40.000 titik) |
| Gelombang raksasa | Tetap 1.200 m. Normal halus, tekstur dinding air, urat buih mengalir turun, kaki gelombang lebih gelap, semburan di puncak, kabut di kaki |
| Ukur GPU | Baris HUD "GPU (langit / scene / post)" bila browser mendukung `EXT_disjoint_timer_query_webgl2` |

Uji: `tools/uji_millar.py`, 14 pemeriksaan lulus di sandbox (kamus English, tanpa daratan, lompat 76,9%, 1,300 g, gelombang 125,00 m/s, 1 s = 17,04 jam di luar, tersapu +0,78 tahun, 5 preset tanpa nilai tidak valid dan tanpa titik menyala, `?preset=hemat`).

Perbaikan yang ditemukan saat uji: dengan MSAA, kedalaman air di segitiga kecil di cakrawala terekstrapolasi negatif sehingga warna meledak (titik merah menyala di garis cakrawala). Kedalaman kini dijepit di shader dan HDR dijepit sebelum ACES; uji memeriksa tidak ada piksel di atas 50.

Belum diukur: FPS dan waktu GPU di GTX 1060 dan M1 (sandbox tanpa GPU). Angka preset bisa berubah setelah diukur.

Catatan: Gargantua di R1 masih pengganti sementara (cincin prosedural, tidak terdistorsi). Porting lensa dari experience Gargantua ada di rencana (baris Gargantua di tabel preset) tapi tidak masuk daftar tahapan; kini dijadikan tahap R1b.

## Status R1b

Selesai 29 September 2026.

| Bagian | Isi |
| --- | --- |
| Lensa | Porting ray tracing Schwarzschild dari `experiences/gargantua/`: percepatan foton dari persamaan Binet, velocity Verlet dengan langkah adaptif, piringan tipis r 3-9 rs dengan aliran Kepler, suhu Novikov-Thorne, palet film, pergeseran merah gravitasi. Belakang piringan kini tampak sebagai busur di atas dan di bawah bayangan |
| Posisi pengamat | Jarak 16,08 rs dihitung dari radius bayangan 9 derajat: sin(alpha) = b_c / D x sqrt(1 - 1/D), b_c = 3 sqrt(3) / 2 rs. 6 derajat di atas bidang piringan, piringan dimiringkan 9 derajat di langit |
| Cubemap sendiri | `GCUBE`: rgb = cahaya piringan, alpha = latar yang terlihat (0 di bayangan). Hanya arah dalam sekitar 53 derajat dari Gargantua yang di-trace (3 sisi cubemap) |
| Per preset | Ultra 512 / 320 langkah dan Tinggi 384 / 240: piringan bergerak (satu sisi diperbarui tiap 3 frame). Sedang 384 / 200, Rendah 256 / 150, Hemat 256 / 120: di-trace sekali saat muat, piringan diam |
| Atmosfer | Tabir 10% dan awan tetap di depan Gargantua; bayangan tidak hitam pekat |
| Awan cerah | Dulu: celah awan berupa lubang yang selalu mengarah ke Gargantua. Kini: saat cerah, tutupan awan turun merata di seluruh langit, awan pecah bertepi tegas dan terbawa angin; Gargantua terlihat di sela awan yang lewat |

Uji: `tools/uji_millar.py` kini 16 pemeriksaan, semua lulus. Radius bayangan terukur 9,37 derajat (harapan 9, toleransi 0,8; selisih dari ukuran piksel dan langkah integrasi), pusat gelap, busur terbelokkan ada di atas bayangan, tidak ada nilai tidak valid; 5 preset tanpa titik menyala saat Gargantua terlihat (nilai HDR tertinggi 3,95-4,95).

Belum diukur: biaya GPU ray tracing di GTX 1060 dan M1. Bila Ultra/Tinggi berat, piringan bergerak bisa diperlambat (sisi diperbarui lebih jarang) atau langkah dikurangi.

## Status R2

Selesai 29 September 2026.

| Bagian | Isi |
| --- | --- |
| Spektrum | Dibuat sekali di CPU: spektrum arah angin (puncak 4,5 m, sebaran cos² searah angin, sedikit ke arah berlawanan, redaman kapiler di bawah 6 cm), dispersi air dangkal (kedalaman 0,6 m, g 12,75). Pita panjang gelombang tiap kaskade tidak tumpang tindih; semua dinormalisasi agar tinggi signifikan = `CONFIG.chop.Hs` (0,35 m) |
| GPU tiap frame | Evolusi waktu h(k,t) dan turunannya: 8 medan (tinggi, perpindahan horizontal x dan z, kemiringan x dan z, tiga suku Jacobian) dikemas jadi 4 bilangan kompleks di 2 tekstur (render ke banyak target sekaligus), lalu IFFT 2D Stockham radix-2 (baris lalu kolom), lalu tekstur perpindahan dan kemiringan ber-mipmap dan anisotropik |
| Kaskade | Ultra 3 x 256 (petak 37 / 8,3 / 1,9 m), Tinggi 2 x 256 (37 / 6,1 m), Sedang 2 x 128 (31 / 5,3 m), Rendah 1 x 64 (19 m), Hemat tetap Gerstner. Panjang petak tidak berkelipatan agar pengulangan tidak terlihat |
| Bentuk ombak | Puncak tajam lewat perpindahan horizontal (choppy, lambda 0,9); vertex dekat memakai mip sesuai ukuran sel grid (tanpa aliasing); normal per piksel dari kemiringan semua kaskade |
| Buih | Buih baru di lipatan ombak (Jacobian < 0,7) dari semua kaskade + buih sisa di kaskade pertama yang memudar (waktu paruh sekitar 1,7 s, e-fold 2,5 s) |
| Kaustik | Ultra dan Tinggi: cahaya di dasar laut dikalikan exp(-k x kedalaman x laplasian permukaan), dijepit halus. Lemah saat mendung (cahaya menyebar), kuat saat cerah |
| Cadangan | Browser tanpa render ke tekstur float memakai Gerstner seperti Hemat |

Uji: `tools/uji_millar.py` kini 24 pemeriksaan, semua lulus. Tinggi dari IFFT di GPU sama dengan DFT langsung di CPU dari spektrum yang sama (selisih maksimum 0,82 mm di 6 titik, dari presisi half float); tinggi signifikan terukur 0,350 m (Ultra) dan 0,360 m (Rendah) untuk target 0,35 m; Hemat tetap Gerstner; 5 preset tanpa nilai tidak valid atau titik menyala.

Perbaikan saat pengecekan visual: rumus kaustik awal (1/x dijepit keras) membuat petak bertepi tajam di dasar laut saat cerah; diganti bentuk halus. Kontras noise dasar laut diturunkan.

Catatan: kedalaman air di HUD dan kecepatan jalan masih memakai ombak Gerstner di CPU sebagai perkiraan (bukan hasil FFT; membaca balik tekstur GPU tiap frame akan memperlambat). Ombak yang terlihat dan angka HUD bisa sedikit berbeda di titik yang sama.

Belum diukur: waktu GPU FFT di GTX 1060 dan M1 (baris HUD "GPU (langit / FFT / scene / post)"). Ultra menjalankan sekitar 3 x 18 lintasan 256 x 256 per frame.

## Status R3 (+ keadaan laut)

Selesai 29 September 2026.

| Bagian | Isi |
| --- | --- |
| Keadaan laut | Permintaan pemilik: ombak angin kecil saat gelombang raksasa masih jauh, makin besar saat mendekat. Pengali tinggi 0,6 (>= 120 km) naik ke 1,5 (<= 4 km), kurva pangkat 1,5, berubah halus (4 s). Tinggi signifikan 0,21 m -> 0,53 m. Setelah gelombang lewat, laut tenang dua kali lebih cepat. Berlaku untuk FFT (buih ikut bertambah), Gerstner, dan kembaran JS. Baris HUD "Ombak angin" |
| Tanpa daratan | Dasar laut diturunkan (rata-rata -0,66 m, kisaran -0,48 sampai -0,84 m) agar lembah ombak terbesar tetap di atas dasar |
| Riak di kaki | Simulasi persamaan gelombang di grid yang ikut pemain (digeser per sel, tepi menyerap): Ultra/Tinggi 256 sel / 32 m, Sedang 128 / 24 m, Rendah dan Hemat 64 / 16 m. Kecepatan riak 1,2 m/s. Sumber: hentakan tiap langkah + dorongan kaki terus-menerus saat berjalan (jejak berbentuk V) |
| Jejak buih | Kanal buih di simulasi yang sama, memudar sekitar 4 s, ikut tergeser dengan dunia |
| Cipratan | Partikel air tiap langkah dan saat mendarat (lebih banyak), gravitasi 12,75, jatuh kembali ke air. Batas 4.000 / 2.500 / 1.500 / 600 / 300 butir |
| Langkah berat | Air menahan: kecepatan menuju sasaran dengan waktu tanggap 0,35 s, tidak bisa berbelok saat melompat. Makin dalam air, makin lambat (sudah ada) |
| Gerak kepala | Pola BOB Copper Corn Station: satu langkah tiap 0,72 m (lari 1,25 m), turun tajam tiap langkah, ayun kiri-kanan, sedikit miring, pegas hentakan saat mendarat. Tombol B: Mati / Halus / Normal |
| Kedalaman di HUD | Kini dari tinggi ombak FFT tepat di kaki (dibaca balik dari GPU tanpa menunggu, tiap 3 frame). Hemat tetap perkiraan Gerstner |

Beda dari rencana: Hemat memakai simulasi riak 64 x 64 (murah) alih-alih cincin riak sederhana, jadi tampilannya sama dengan Rendah.

Uji: `tools/uji_millar.py` kini 32 pemeriksaan, semua lulus, termasuk: pengali keadaan laut 0,60 / 0,93 / 1,32 / 1,50 untuk 150 / 60 / 20 / 4 km; tinggi signifikan FFT 0,208 m (jauh) -> 0,530 m (dekat), harapan 0,210 -> 0,525; cincin riak di 0,75 m setelah 1 s (grid kasar sedikit memperlambat riak dari 1,2 m/s); cipratan 96 butir lalu habis setelah 2 s; 3 langkah untuk 2,63 m (harapan 3,7); air menahan (0,18 m/s setelah 0,1 s, 0,75 m/s setelah 4 s); gerak kepala Mati = 0; kedalaman dari FFT terbaca.

Belum diukur: biaya simulasi riak dan cipratan di GTX 1060 dan M1 (masuk baris HUD "laut"). Tampilan riak dan cipratan perlu dinilai langsung (sandbox hanya beberapa FPS).

## Status R4

Selesai 29 September 2026.

| Bagian | Isi |
| --- | --- |
| Muka gelombang | Profil 86 titik (63 di muka, tiap 12-25 m), baris tiap 6 m di dekat pemain (dulu 37 titik dan 12 m) |
| Air meluncur | Tonjolan air sampai sekitar 16 m di muka yang meluncur turun 33 m/s (perpindahan vertex, normal ikut dihitung dari posisi tergeser) |
| Tekstur dinding | Dua skala (60 m dan 16 m) + ombak angin, dengan koordinat panjang busur profil (meter di permukaan) agar tidak meregang di kaki yang landai. Urat buih putih tak beraturan meluncur dengan kecepatan yang sama, air pecah bergolak di kaki, puncak lebih terang (air menipis), kaki lebih gelap |
| Semburan dan kabut | 3 lapis semburan di puncak (tertiup ke belakang, sampai sekitar 310 m) dan 2 lapis kabut di kaki, berupa gumpalan terpisah |
| Arus air surut | Air mengalir ke arah gelombang, paling kuat 1,6 m/s sekitar 2,5 km di depan muka, nol bila gelombang jauh. Terlihat: pola ombak terbawa arus (peta aliran dua fase) dan garis buih memanjang searah arus. Terasa: pemain terseret ke arah gelombang (35% kecepatan arus). Baris HUD "Arus" |
| Tersapu | Urutan 4,3 s: hantaman buih putih (0,5 s), kamera terguling di dalam air hijau-abu gelap dengan gelembung naik dan kilatan buih, lalu memutih, kembali ke titik awal dengan catatan waktu yang hilang (seperti sebelumnya) |

Perbaikan saat pengecekan visual: pola dinding memakai koordinat u lalu tinggi, keduanya meregang jadi garis tegak di kaki dan sinar memusat bila dilihat dari dekat; diganti panjang busur profil. Buih kaki hanya bergantung pada z sehingga membentuk kolom tegak; kini ikut panjang busur. Gelembung bawah air semula titik seragam dalam grid; kini ukuran dan posisi acak, dua lapis.

Uji: `tools/uji_millar.py` kini 39 pemeriksaan, semua lulus, termasuk: urutan tersapu (di bawah air penuh, kamera terguling 13,6 rad, 4,30 s), kerapatan muka, arus 0,00 m/s (gelombang 30 km) dan 1,60 m/s (2,5 km) dengan pemain terseret 1,12 m dalam 2 s, gelombang 1.500 m dan 350 m di depan tanpa nilai tidak valid atau titik menyala.

Belum diukur: biaya gelombang (mesh 31.600 titik dengan noise per vertex) dan peta aliran arus (dua kali ambil tekstur ombak di zona arus) di GTX 1060 dan M1.

Berikutnya R5: audio (angin, gemericik ombak, langkah di air, gemuruh gelombang frekuensi rendah yang makin keras, getaran).
