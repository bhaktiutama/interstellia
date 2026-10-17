# Rencana Tahap 28 Copper Corn Station: manusia tidak kotak-kotak

Per 17 Oktober 2026 · disusun atas permintaan Bhakti ("enhance manusia biar tidak kotak-kotak seperti Roblox") · Status: 28a dan 28b selesai (17 Oktober 2026), menunggu persetujuan bentuk dari blokout sebelum 28c

> Revisi 17 Oktober 2026: hasil generator prosedural (28b) dinilai tidak bagus. Tahap 28c dan seterusnya diganti rencana model GLB: `docs/cooper-station/rencana-tahap-28-glb-cooper-station.md`. Bagian 28a (ukur, saklar `?orang=lama`) tetap berlaku.

## Ringkasan

- Penyebab langsung: pejalan kaki Copper dibangun dari 17 `BoxGeometry` (204 segitiga, 408 titik) yang diputar kaku per bagian. Komentar kodenya sendiri: "model orang: kotak-kotak" (`experiences/cooper-station/index.html` baris 14389-14407). Tidak ada leher, bahu, pinggang, pergelangan, wajah, atau jari, dan kotak saling tembus atau bercelah di lutut dan siku.
- Rencana: ganti dengan generator bentuk loft halus (cara yang sama dengan mobil tahap 26) dalam 3 tingkat detail (dekat ~1.460 segitiga, menengah ~390, jauh ~80), sendi dihaluskan dengan kulit dua tulang di vertex shader, tanpa atribut instance baru dan tanpa mengubah simulasi pejalan kaki. Saklar `?orang=lama` = model kotak sekarang persis.
- Hasil ukur 28a mengubah asumsi biaya: orang yang benar-benar tergambar hanya 0 sampai 331 per lokasi di Ultra (bukan sampai 4.000), jadi model baru menambah sekitar 130 ribu segitiga (2-3% dari 3,3-5,9 juta segitiga adegan). Anggaran segitiga per tingkat boleh lebih longgar dari rencana awal (lihat Hasil 28a dan 28b di bawah).

## Asumsi yang perlu dikonfirmasi

"Manusia" saya baca sebagai pejalan kaki, pengunjung, pemain dan penonton baseball di Copper (semuanya memakai satu model yang sama). Astronaut orang pertama di Millar sudah bukan kotak sejak M6f (satu mesh berkulit, `docs/millar/rencana-m6-millar.md`), hanya sarung tangan, sepatu, dan ransel di Millar yang masih berbasis kotak. Bila yang dimaksud astronaut Millar, rencana ini perlu diganti (lihat pertanyaan 1).

## Kondisi sekarang (dari kode)

| Aspek | Sekarang | Lokasi | Kekurangan |
| --- | --- | --- | --- |
| Geometri | 17 kotak: 5 per sisi (paha, betis, sepatu, lengan, tangan) + badan, pinggul, leher, kepala, rambut atas, rambut belakang, tas. 17 x 24 = 408 titik, 17 x 12 = 204 segitiga | `index.html` 14390-14411 | semua sudut 90 derajat, normal datar per muka, siluet persegi |
| Bahu dan pinggang | badan 0,38 x 0,56 x 0,22 m dan pinggul 0,36 x 0,14 x 0,20 m, dua kotak ditumpuk | 14399 | tidak ada bahu, pinggang menyempit, atau pinggul |
| Sendi | tiap bagian diputar kaku di pivot: lutut y 0,48, pinggul y 0,9, bahu y 1,44; leher dan pergelangan tidak ada | `VS` 14440-14443 | kotak betis dan paha berpotongan atau berjarak saat menekuk |
| Kepala | kotak 0,19 x 0,23 x 0,21 m + dua kotak rambut (warna `uHair`) | 14400 | tanpa dagu, hidung, telinga; rambut seperti topi kotak |
| Tangan dan kaki | tangan kotak 0,09 x 0,10 x 0,10 m; sepatu kotak 0,12 x 0,08 x 0,25 m, warna gelap bila `position.y < 0.09` | 14397, 14395, 14452 | tanpa jari atau ibu jari, tanpa sol, tumit, atau ujung sepatu |
| Warna dan cahaya | warna rata per bagian (`uShirt` 14, `uPants` 8, `uSkin` 6, `uHair` 6), cahaya `vegLight()` per titik | `VS` 14451-14454 | muka kotak 4 titik = gradasi datar; tanpa AO di ketiak, bawah dagu, antara kaki |
| Variasi | hanya warna dan skala `aJ.x` (anak 0,6x dengan proporsi dewasa) | `aI`, `aJ` | semua orang bentuk sama; anak tampak seperti dewasa mengecil |
| Pose | 3 pose: jalan (`sin(fase)`), berdiri (napas lengan 0,05 rad), duduk (paha -1,5 rad, lutut 1,5 rad, turun 0,38 m) | `VS` 14433-14439 | tanpa putaran badan, kepala selalu lurus, lengan lurus kaku |
| Jumlah | 13.094 orang di dunia (`analisa-optimasi...md`), `PEDS.max` 4.000 tergambar, radius 300 / 250 / 180 / 120 / 80 m per preset | 14164, 14716 | jumlah tergambar per jarak belum pernah dicatat |

Pemakai model yang sama (harus tetap benar setelah ganti): pejalan kaki jalur, pengunjung air mancur (`VIS`), orang duduk di bangku, kafe, terminal, halte, pasar, pemain dan penonton baseball (`BASEBALL.people`, disisipkan di `updatePeds()`), payung (`PEDS.umbMesh`, tangan di `H = (0,25, 1,44 - 0,61 cos(arm), ...)`), bayangan (`castAlpha`).

## Prinsip

1. Pertahankan yang ada: kerangka lama tidak berubah. Pivot pinggul y 0,9, lutut 0,48, bahu (x +-0,25; y 1,44), tinggi total sekitar 1,76 m, lebar bahu dalam +-15% dari kotak lama, pose duduk (turun 0,38 m), posisi tangan untuk payung. Dengan begitu jarak trotoar, bangku, bola baseball, dan payung tidak perlu disentuh.
2. Tanpa atribut instance baru: `aP`, `aI`, `aJ` tetap 4 float; CPU `stepPeds()` dan `updatePeds()` tidak berubah biayanya. Variasi baru diturunkan dari hash `aP.xy` di shader.
3. Satu sumber bentuk: generator di `shared/orang.js` (`window.PEDKIT`, skrip biasa, jalan dari file://) dipakai game dan halaman blokout, seperti `CARKIT` tahap 26. Rumus kulit tulang di shader punya kembaran JS di `PEDKIT.pose()` untuk uji (ubah bersama).
4. Desain orisinal dan prosedural: tanpa aset luar, tanpa GLB, tanpa meniru tokoh atau pakaian nyata. Tidak memakai GLTFLoader (aturan proyek).
5. Detail hanya dekat (LOD), bayangan memakai bentuk tingkat menengah, model lama tetap sebagai cadangan lewat `?orang=lama`.
6. Realisme dari bentuk dan sendi yang halus, bukan dari derau: siluet bulat, bahu dan pinggang, jari tersusun, sendi tidak berlubang.

## Desain bentuk (28b)

Generator `PEDKIT.shape(level)` membangun tiap bagian dari loft penampang (irisan elips dengan geseran depan-belakang), normal dari `computeVertexNormals()` pada titik bersama, jadi mulus tanpa lipatan kecuali yang disengaja (sol sepatu, tepi rambut).

| Bagian | Bentuk | Segitiga dekat (L0) | Menengah (L1) | Jauh (L2) |
| --- | --- | --- | --- | --- |
| Kepala dan leher | elipsoid 12 x 10 dengan rahang, dagu, hidung kecil, dua telinga (L0); bola 8 x 6 (L1); prisma 6 sisi (L2) | 280 | 60 | 12 |
| Rambut | cangkang di atas kepala; dua gaya (pendek, panjang diikat) sebagai bagian terpisah | 120 | 30 | (menyatu dengan kepala) |
| Badan (bahu, dada, pinggang, pinggul) | loft 8 irisan x 12 sisi, bahu lebar, pinggang menyempit, pinggul | 260 | 80 | 16 |
| Lengan (atas dan bawah) x2 | loft 9 irisan x 8 sisi, runcing ke pergelangan, siku menonjol | 220 | 72 | (menyatu dengan badan) |
| Tangan x2 | telapak + ibu jari + satu blok jari (sarung tangan), tanpa lima jari | 140 | 12 | 0 |
| Kaki (paha, betis) x2 | loft 9 irisan x 10 sisi, betis menonjol di belakang, lutut | 260 | 80 | 28 |
| Sepatu x2 | loft sepanjang telapak: tumit, lengkung, ujung bulat, sol terpisah | 120 | 32 | 8 |
| Tas | kotak membulat + tali bahu, hanya bila `aJ.z >= 0,5` (cara lama `CLIP_AWAY`) | 60 | 20 | 0 |
| Total | | sekitar 1.460 | sekitar 390 | sekitar 80 |

Angka segitiga di tabel adalah anggaran desain awal. Hasil 28b (diukur): L0 2.496, L1 746, L2 240 segitiga, anggaran dilonggarkan menjadi 2.500 / 750 / 250 karena hasil 28a (lihat di bawah). Nilai lama: 204 segitiga per orang.

Sendi (kulit dua tulang di vertex shader): atribut per titik baru `aSk` (tulang A, tulang B, bobot) menggantikan pemilihan tulang dari `aPart`. Rantai tulang hanya `rotX` seperti sekarang: pinggul, lutut (paha lalu betis), bahu, siku, ditambah leher (kepala mengangguk dan menoleh). Posisi titik = campuran bobot dari transformasi dua tulang; normal diputar dengan transformasi yang sama (sudah dilakukan kode lama untuk `n`). Bobot halus di sekitar sendi (lutut 10 cm, siku 8 cm, pinggul 12 cm, bahu 10 cm), bobot 1 di tengah ruas. `aPart` tetap ada untuk warna (kulit, kemeja, celana, rambut, tas, sepatu).

AO yang dipanggang sekali saat bangun: nilai 0..1 per titik (atribut `aAo`), lebih gelap di ketiak, antara paha, bawah dagu, di bawah rambut, belakang lutut, dalam kerah. Dihitung dari jarak titik ke bagian lain pada pose tegak, tanpa biaya per frame.

Halaman blokout: `docs/cooper-station/orang/blokout-orang.html` (putar kamera, pilih L0 / L1 / L2, geser sudut sendi, pose jalan / berdiri / duduk, dewasa dan anak, warna acak, tampilan wireframe, penghitung segitiga dan indeks kotak). Berhenti di sini sampai Bhakti setuju bentuknya.

## Variasi per orang (28e), tanpa atribut baru

Semua dari `hash(aP.xy)` di shader, bentuk dasar sama.

| Variasi | Cara | Biaya |
| --- | --- | --- |
| Bahu dan pinggul (badan ramping, tegap, berisi) | skala sumbu x per tinggi: `mix(pinggul, bahu, smoothstep(0.95, 1.40, y))`, faktor 0,9 sampai 1,12 | nol atribut |
| Anak | `aJ.x < 0,8` (anak sekarang 0,6x): kepala diperbesar 1,0 + 0,6 (1 - skala) di pivot leher, tungkai relatif lebih pendek | satu cabang |
| Gaya rambut | dua cangkang rambut (pendek, panjang); yang tidak terpilih dibuang `CLIP_AWAY` seperti tas | nol atribut |
| Lengan baju | lengan bawah berwarna kulit (pendek) atau kemeja (panjang) dari hash | nol |
| Pakaian tambahan (usulan, pertanyaan 4) | jaket (kerah + panjang pinggul), rok / gaun (kerucut dari pinggang ke lutut), topi | bagian geometri opsional, dibuang bila tidak terpilih |

## Gerak organik (28f)

Semua di vertex shader, tidak ada pose baru yang menambah atribut.

| Gerak | Cara |
| --- | --- |
| Putaran badan saat berjalan | bahu berputar berlawanan dengan pinggul, +-0,12 rad (`rotY` pada badan atas) |
| Kepala | menoleh pelan (hash + `uTime`), mengangguk sedikit mengikuti langkah |
| Bahu | naik-turun 1 cm mengikuti ayun lengan |
| Berdiri | berat pindah antar kaki (pinggul miring 0,03 rad), lengan menggantung rileks, napas pada dada |
| Duduk | paha mendatar, betis ke bawah, badan sedikit condong, tangan di paha |
| Sendi lutut tidak lurus penuh | sudut minimum 0,06 rad |

## Tingkat detail (28d)

Tiga `InstancedBufferGeometry` (L0, L1, L2) dengan atribut instance dipisah per band. `updatePeds()` memilah kandidat berdasarkan jarak ke pemain, tiap orang punya histeresis 4 m (`p.lod`) agar tidak berkedip di batas. Payung (`PEDS.umbMesh`) tidak berubah. Bayangan: orang dekat dan menengah memakai geometri L1 di pass bayangan (`castAlpha`), jauh tidak membayangi seperti sekarang bila itu perilaku lama (cek di 28a).

Usulan radius per preset (disesuaikan setelah uji FPS Bhakti di GTX 1060 dan M1):

| Preset | L0 (dekat) | Maks L0 | Batas L1 ke L2 |
| --- | --- | --- | --- |
| Ultra | 30 m | 400 | 90 m |
| Tinggi | 25 m | 300 | 80 m |
| Sedang | 18 m | 200 | 60 m |
| Rendah | 12 m | 80 | 45 m |
| Hemat (M1) | mati | 0 | 35 m |

## Tahapan

| Tahap | Isi | Effort | Model | Thinking | File dan fungsi yang disentuh |
| --- | --- | --- | --- | --- | --- |
| 28a | Dasar dan saklar: sidik jari FNV-1a geometri lama (dipakai uji `?orang=lama`), saklar `?orang=lama`, catat jumlah orang tergambar per band jarak (0-12, 12-30, 30-90, > 90 m) di 6 lokasi (plaza Cooper, New York, pasar, air mancur, baseball, terminal) dan biaya GPU `GPUT`; cek apakah bayangan orang jauh sudah mati | Medium | Sonnet 5.5 | medium | blok model orang `index.html` 14389-14471, `PEDS`, `GPUT`, skrip ukur baru di `tools/` |
| 28b | Generator `PEDKIT.shape(level)` (loft, bobot tulang `aSk`, AO `aAo`, id warna), kembaran JS `PEDKIT.pose()`, dan halaman blokout untuk persetujuan; belum dipasang di game | High | Opus 5.5 | high | `shared/orang.js` baru, `docs/cooper-station/orang/blokout-orang.html` baru |
| 28c | Pasang model baru tingkat L1 saja (semua orang): vertex shader kulit dua tulang, warna dari `aPart`, `aAo`, `vegLight()` per titik; kerangka lama tetap, payung dan duduk diuji; model lama tetap bila `?orang=lama` | High | Opus 5.5 | high | `VS` / `FS` dan geometri di blok 14389-14471, `PEDS.mesh`, `warmFrame()` |
| 28d | Tiga band LOD (L0, L1, L2), pemisahan buffer instance di `updatePeds()`, histeresis, radius per preset, bayangan dari L1, baseball dan pengunjung ikut | High | Opus 5.5 | high | `updatePeds()` 14672-14714, `applyPedsPreset()`, `castAlpha`, `BASEBALL.people` |
| 28e | Variasi per orang (bentuk badan, anak, rambut, lengan baju, pakaian tambahan bila disetujui) | Medium | Sonnet 5.5 | medium | `VS`, `PEDKIT.shape()` |
| 28f | Gerak organik (putaran badan, kepala, bahu, pose berdiri dan duduk lebih alami) | Medium | Sonnet 5.5 | medium | `VS`, `PEDKIT.pose()` |
| 28g | Cahaya dan material: AO dipanggang, normal halus, sol sepatu dan kulit sedikit berbeda kekasaran, tepi terang tipis dari jauh agar siluet terbaca di kabut pagi | Medium | Sonnet 5.5 | high (shader, aturan GPU di bawah) | `VS` / `FS` pejalan kaki, `vegLight()` hanya dibaca |
| 28h | Uji dan ukur: `tools/uji_orang.py` baru, lembar kontak PNG `docs/cooper-station/orang/lembar-orang.png` (alat `tools/lembar_orang.py`), `uji_pejalan_kaki.py`, `uji_air_mancur.py`, `uji_trotoar.py`, `ukur_muat.py cooper-station --cek` tetap lulus | Medium | Sonnet 5.5 | medium | `tools/` |
| Mekanis | Entri `CLAUDE.md` (peta kode PEDS, riwayat tahap 28), `docs/cooper-station/rencana-tahap-28...md` status, kamus bila ada teks panel baru | Low | Haiku 4.5 | low | dokumen |

Urutan: 28a, 28b (berhenti, minta persetujuan bentuk), 28c, 28d, lalu 28e dan 28f (bisa bersamaan), 28g, 28h. Rencana ini disusun oleh model satu tingkat di atas tahap terberat (High); pengerjaan tiap tahap memakai model pada kolom Model.

## Hasil 28a (selesai 17 Oktober 2026)

Alat: `tools/ukur_orang.py` (jumlah tergambar per band jarak, segitiga, biaya CPU, sidik jari geometri); acuan `tools/uji_orang_lama.json`; saklar `?orang=lama` (`PEDS.lama`, belum berpengaruh karena model baru belum dipasang).

| Temuan | Nilai |
| --- | --- |
| Model lama | 204 segitiga, 408 titik; sidik jari FNV-1a posisi 76810e35, normal 79c6605, bagian a2d6de05, indeks e0652f65 |
| Orang di dunia | 14.242 (spawn, sandbox); `PEDS.max` 4.000 tidak pernah mendekati |
| Pass bayangan | orang ikut (layer 2, `castAlpha`) untuk semua instance, termasuk yang jauh |
| Biaya CPU `updatePeds()` | 0,005-0,375 ms per panggilan (sandbox, tidak mewakili GPU asli) |

Orang tergambar per lokasi, band [0-12 m, 12-30 m, 30-90 m, > 90 m] (Ultra, jam 15.00 simulasi):

| Lokasi | Jumlah | Band |
| --- | --- | --- |
| Cooper (spawn) | 2 | 0 / 0 / 0 / 2 |
| New York | 331 | 6 / 7 / 23 / 295 |
| Pasar | 120 | 9 / 28 / 2 / 81 |
| Air mancur | 324 | 4 / 8 / 23 / 289 |
| Baseball | 283 | 3 / 11 / 28 / 241 |
| Spaceport | 277 | 2 / 21 / 53 / 201 |

Sedang: 0-113 orang; Hemat: 0-37 orang (radius 80 m). Segitiga adegan penuh Ultra 3,3-5,9 juta (diukur lewat `renderer.info`).

Dampak ke rencana: dugaan "4.000 orang tergambar" salah; anggaran segitiga dilonggarkan, dan tingkat L0 sampai 30 m hampir selalu di bawah 40 orang. Pengukuran satu jam simulasi (15.00); jam ramai dan pasar belum dibandingkan.

## Hasil 28b (selesai 17 Oktober 2026)

| Item | Hasil |
| --- | --- |
| Generator | `shared/orang.js` (`window.PEDKIT`, tanpa three.js, jalan di Node dan browser): `shape(level)`, `pose()` kulit dua tulang, `poseOf()`, `edgeStats()`, `old` (model kotak lama untuk banding), palet sama dengan game |
| Segitiga | L0 2.496 (1.321 titik), L1 746 (419), L2 240 (138) |
| Bentuk | loft penampang elips / persegi membulat: badan dengan bahu, pinggang, pinggul dan kerah; kepala dengan rahang, hidung, dua telinga, rambut pendek (rambut panjang opsional); lengan atas dan bawah runcing dengan telapak, jari satu blok, ibu jari; paha, betis menonjol di belakang, lutut; sepatu dengan sol; tas samping opsional |
| Kerangka | 11 tulang, pivot sama dengan model lama (pinggul 0,90, lutut 0,48, bahu 1,44); tinggi 1,786 m, setengah lebar 0,30 m (lama 0,30) |
| Indeks kotak | lama 66,7%; L0 6,8%, L1 25,3%, L2 37% |
| AO | dipanggang per titik (pangkal paha, ketiak, bawah dagu, belakang lutut, dasar sepatu) |
| Uji | `tools/uji_orang_bentuk.cjs` (Node, tanpa browser): 19 pemeriksaan lulus (segitiga, nilai valid, bobot, ukuran, indeks kotak, 8 pose tanpa nilai tidak valid, sambungan rapat, tepi tidak robek) |
| Blokout | `docs/cooper-station/orang/blokout-orang.html` (model lama + L0 + L1 + L2 berjajar, pose jalan / berdiri / duduk, fase, kamera depan / samping / belakang / atas / wajah / tangan / kaki, kerangka, lengan panjang, rambut panjang, tas, warna acak); tiga tangkapan: `blokout-depan.png`, `blokout-dekat.png`, `blokout-belakang.png` |

Kelemahan yang saya lihat di blokout (tolong dinilai):

- Tangan masih lonjong seperti sarung tangan tanpa jari terpisah (sesuai batasan rencana); dari jauh wajar, dari dekat terlihat polos.
- Wajah polos (hidung dan telinga saja), tanpa mata atau mulut; siluet sudah manusia.
- Bahu dan tangan: lengan agak menggantung terpisah dari badan di pose berdiri (celah 1-5 cm di pinggang); bahu masih sedikit miring tajam.
- Pangkal badan bawah (panggul) tampak membulat seperti kantong dari depan; tersembunyi bila celana lebih longgar.
- Kulit dua tulang meregang di depan lutut saat duduk (1,57x), tepi di garis lipat terlihat seperti lipatan; jalan dan berdiri tidak.
- Warna rata per bagian dengan AO; kain, lipatan baju, dan kerah belum ada (28g).
- Dinilai dari tangkapan SwiftShader; bentuk dan cahaya di GPU asli belum dilihat.

Yang dipasang di game: belum ada. Berikutnya (28c) menunggu persetujuan Bhakti atas bentuk blokout ini.

## Uji dan ukuran keberhasilan

| Pemeriksaan | Ambang (usulan, belum diukur) |
| --- | --- |
| Indeks kotak = persen tepi bersama (tanpa tutup ujung tersembunyi) yang sudut antar-normalnya > 50 derajat | model lama 66,7% (diukur: 12 dari 18 tepi per kotak); hasil 28b L0 6,8%, L1 25,3%, L2 37%; batas uji L0 <= 8%, L1 <= 30%, L2 <= 45% (sisa tepi keras L0 adalah sol sepatu, ujung jari, hidung, telinga) |
| Segitiga per orang | L0 <= 2.500, L1 <= 750, L2 <= 250 (dilonggarkan setelah 28a) |
| Geometri valid | 0 NaN / Infinity, normal tidak nol, bobot tulang dijumlah 1, AO 0..1 |
| Ukuran | tinggi 1,70-1,80 m, lebar bahu dalam +-15% model lama, telapak di y = 0 |
| Kulit di sendi | jalan dan berdiri: tepi terpanjang <= 1,3x pose ikat; duduk (lutut 86 derajat): <= 1,7x, batas kulit dua tulang linear (hasil 28b: 1,27x dan 1,57x di L0); sambungan berimpit tetap rapat di semua pose |
| `?orang=lama` | sidik jari geometri sama dengan 28a, piksel identik dengan sebelum tahap 28 |
| Payung | titik tangan model baru dalam 3 cm dari titik `H` payung di jalan dan duduk |
| Render | tanpa nilai tidak valid atau titik menyala di 5 preset x pagi / siang / malam |
| Muat | `ukur_muat.py cooper-station --cek`: 0 program baru di frame pertama dan saat tombol (semua mesh L0 / L1 / L2 dan varian kedalaman ikut `warmFrame()`) |
| Biaya CPU | `updatePeds()` rata-rata tidak naik lebih dari 25% dari nilai 28a |

Lembar kontak (`lembar-orang.png`, satu gambar untuk dibaca di ponsel): 12 orang dekat dari depan dan samping, 6 fase langkah, duduk, anak, tiga jarak (10 m, 40 m, 120 m), dibanding model lama di baris atas. Tangkapan layar lain tidak diulang (aturan proyek).

## Anggaran dan risiko

Berdasarkan ukur 28a (Ultra, jam 15.00 simulasi, sandbox): orang tergambar per lokasi 2 sampai 331, di dalam 30 m paling banyak 37, di luar 90 m paling banyak 295. Perkiraan model baru di lokasi terpadat (New York): 13 x 2.496 + 23 x 746 + 295 x 240 = 0,12 juta segitiga, dibanding 331 x 204 = 0,07 juta sekarang. Tambahan sekitar 0,05 sampai 0,13 juta segitiga di semua lokasi ukur, 1-3% dari segitiga adegan (3,3-5,9 juta di Ultra). Ini turunan dari ukur, bukan ukur FPS: biaya vertex shader kulit dan `vegLight()` per titik tetap diuji pemilik di GTX 1060 dan M1.

| Risiko | Tingkat | Penanganan |
| --- | --- | --- |
| Biaya vertex naik (kulit dua tulang + `vegLight()` per titik pada titik lebih banyak) | rendah menurut hitungan segitiga, belum diuji FPS | band LOD, maks L0 per preset, ukur `GPUT` di 28a dan 28d, Hemat tanpa L0 |
| Meletup saat berpindah band | sedang | histeresis 4 m, ukuran dan warna sama antar band, bila masih tampak: pita dither 6 m seperti mobil tahap 26 |
| Bayangan tidak cocok dengan bentuk | rendah | bayangan dari L1 untuk dekat dan menengah |
| Pivot atau tinggi berubah sehingga duduk, payung, bola baseball bergeser | sedang | prinsip 1 (kerangka lama tetap) dan uji titik tangan / duduk |
| NaN di Apple M1 dari shader baru (sandbox SwiftShader tidak memperlihatkannya) | sedang | aturan GPU di bawah; uji akhir di M1 oleh Bhakti |
| Wajah tampak aneh dari dekat (lembah tak wajar) | sedang | tanpa mata dan mulut modelan; hidung, dagu, telinga saja; siluet halus |
| Jumlah program shader bertambah (3 mesh x varian kedalaman) | rendah | semua ikut `warmFrame()`, cek `ukur_muat.py --cek` |

Aturan GPU untuk shader baru: tidak ada `normalize()` dari vektor yang bisa nol (bobot nol, normal nol di tutup), tidak ada `pow()` dari bilangan negatif, `sqrt()` dan `acos()` dijepit, bobot tulang dibagi dengan penjumlah yang dijaga > 1e-5.

## Batasan (tidak dikerjakan di tahap ini)

- Wajah detail, ekspresi, mata dan mulut bermodel, jari lima terpisah (tangan hanya telapak, ibu jari, dan satu blok jari).
- Rambut berhelai, kain atau rok yang disimulasikan, bayangan diri orang pada dirinya sendiri.
- Aset motion capture, GLB pihak ketiga, GLTFLoader (aturan proyek dan lisensi).
- Orang menghindari pemain, pejalan kaki di dalam trem dan lift (belum ada sejak 12b-3).
- Mengubah kepadatan, jalur, atau jadwal orang.
- Astronaut Millar (lihat asumsi di atas); bila diminta, jadi rencana M7 terpisah: sarung tangan, sepatu, ransel, dan helm jadi bentuk mulus, kulit CPU yang ada dipertahankan.

## Pertanyaan untuk pemilik

1. Apakah "manusia" yang dimaksud pejalan kaki di kota Copper, atau astronaut di Millar's World? Rencana ini menganggap Copper.
2. Gaya: realistis sederhana (proporsi 7,5 kepala, wajah hanya siluet hidung dan dagu) atau agak stilisasi? Usul: realistis sederhana.
3. Batas biaya: boleh jumlah segitiga orang naik sekitar 30-50% di Ultra dan Tinggi, dengan Hemat (M1) tanpa tingkat dekat? Angka ini diputuskan setelah 28a.
4. Variasi pakaian tambahan (jaket, rok / gaun, topi) mau ikut di 28e, atau cukup variasi warna, badan, dan rambut?
5. Anak-anak: tetap sekitar 8% di taman (sekarang), atau perlu lebih banyak setelah mereka punya proporsi sendiri?

## File utama

| File | Tahap |
| --- | --- |
| `experiences/cooper-station/index.html`: blok model orang (14389-14471), `updatePeds()` (14672), `applyPedsPreset()` (14715), `PEDS` (14164), `BASEBALL.people`, `PEDS.umbMesh` | 28a, 28c-28g |
| `shared/orang.js` (baru, `window.PEDKIT`) | 28b-28f |
| `docs/cooper-station/orang/blokout-orang.html`, `docs/cooper-station/orang/lembar-orang.png` (baru) | 28b, 28h |
| `tools/uji_orang.py`, `tools/lembar_orang.py` (baru); `uji_pejalan_kaki.py`, `uji_air_mancur.py`, `uji_trotoar.py`, `ukur_muat.py` (tetap lulus) | 28a, 28h |
| `CLAUDE.md` (peta kode Pejalan kaki 12b-3, riwayat tahap 28) | Mekanis |

## Verifikasi

```
CHROMIUM=/opt/pw-browsers/chromium THREE_LOCAL=<scratchpad> python3 tools/uji_orang.py
python3 tools/uji_pejalan_kaki.py
python3 tools/uji_air_mancur.py
python3 tools/uji_trotoar.py
python3 tools/ukur_muat.py cooper-station --cek
python3 tools/uji_bahasa.py
python3 tools/qc_load.py
```

Pemilik menguji visual dan FPS di GTX 1060 dan MacBook M1. Sandbox SwiftShader tidak memperlihatkan NaN atau selisih FPS GPU asli, jadi 28c, 28d, dan 28g wajib dicek pemilik: tidak ada titik putih atau berkedip di orang, tidak ada meletup antar band jarak, FPS di pusat kota dan plaza tidak turun berarti dibanding model kotak (`?orang=lama` untuk banding).
