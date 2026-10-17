# Rencana Tahap 28 (revisi GLB) Copper Corn Station: orang dari model GLB

Per 17 Oktober 2026 · disusun atas permintaan Bhakti (hasil generator prosedural 28b dinilai tidak bagus; pakai paket "Ultimate Modular Men / Women Pack" GLB) · Status: 28G0, 28G1, dan 28G2 selesai (17 Oktober 2026); berikutnya 28G3 (perilaku) dan seterusnya

## Ringkasan

- Kedua paket cocok dipakai: 21 berkas GLB (11 pria, 10 wanita; satu karakter wanita ganda), tiap karakter 5.200-11.100 segitiga, tanpa tekstur (warna bahan datar + warna titik), kerangka 62 tulang yang identik untuk semua pria dan identik untuk semua wanita, 24 animasi per berkas (Walk, Idle, Wave, Interact, Run, dll.; tidak ada animasi duduk). Karena kerangka dibagi, satu tekstur animasi per jenis kelamin cukup untuk semua karakter.
- Pendekatan: karakter diolah offline menjadi data ringkas (cara yang sama dengan motor `tools/siapkan_motor.py`), diturunkan ke 3 tingkat detail (sekitar 3.000 / 700 / 160 segitiga), animasi dibakar ke tekstur, dan dikulit di vertex shader pejalan kaki yang sudah ada. Tanpa GLTFLoader (aturan proyek), simulasi dan atribut instance pejalan kaki tidak berubah.
- Lisensi terkonfirmasi (17 Oktober 2026, dari halaman unduhan via Poly Pizza): CC-BY atau CC0, boleh dipakai di proyek pribadi maupun komersial dengan atribusi wajib: "Ultimate Modular Women Pack by Quaternius [CC-BY] via Poly Pizza" dan "Ultimate Modular Men Pack by Quaternius via Poly Pizza". Kredit sudah ditambahkan di `experiences/cooper-station/assets/KREDIT.md`; tab Tentang menyusul di 28G6.

## Isi paket (diukur dari berkas)

| Item | Nilai |
| --- | --- |
| Berkas | 11 pria, 10 wanita (Animated Woman ada dua salinan dengan warna berbeda), 1,3-2,0 MB per berkas, 32 MB tidak terkompresi |
| Segitiga per karakter | 5.240-11.100 (rata-rata sekitar 6.700), titik sekitar 2x segitiga (normal datar per muka) |
| Struktur | 4-5 mesh (Legs, Feet, Body, Head, kadang topi atau aksesori), 9-18 primitif, 4-11 bahan warna datar, atribut POSITION, NORMAL, COLOR_0, TEXCOORD_0, JOINTS_0, WEIGHTS_0; tanpa tekstur gambar |
| Kerangka | 62 tulang (akar, pinggul, tulang belakang, leher, kepala, bahu, lengan, pergelangan, 5 jari x 2 sisi, kaki, tumit, ujung kaki); semua pria identik (selisih matriks bind 0), semua wanita identik dengan satu sama lain tetapi berbeda dari pria |
| Animasi (24 per berkas) | Walk 1,33 s, Idle 1,67 s, Idle_Neutral 1,67 s, Wave 1,67 s, Interact 1,25 s, Run 0,79 s, Death, Roll, Kick, Punch, Sword, Gun, Hit. Tidak ada animasi duduk |
| Tinggi | 1,83-1,97 m (topi Adventurer pria 2,59 m dan Witch 2,05 m termasuk topi) |
| Unit | simpul mesh berskala 100 dan diputar -90 derajat di sumbu x (keluaran FBX), perlu dibakar ke satuan meter, y ke atas |
| Gaya | low poly bergaya kartun, tampak berfaset karena normal datar, wajah bermata dan alis, jari terpisah |

Yang tidak cocok untuk kota sipil: Swat, Soldier (senjata, perlengkapan militer), Sci Fi Character (pistol), King, Medieval, Witch (fantasi). Pratinjau semua karakter sudah saya kirim sebagai dua gambar di percakapan.

## Kondisi sekarang yang dipertahankan (dari 28a dan kode)

Model lama 17 kotak (204 segitiga), simulasi CPU `stepPeds()`, atribut instance `aP` (s, za, arah, fase langkah), `aI` (baju, celana, kulit, pose), `aJ` (skala, tinggi lantai, tas, payung), payung `PEDS.umbMesh`, pemain dan penonton baseball, pengunjung air mancur, duduk di bangku, kafe, terminal. Ukur 28a (Ultra): orang tergambar 2-331 per lokasi, di dalam 30 m paling banyak 37, di luar 90 m paling banyak 295; segitiga adegan 3,3-5,9 juta. Alat: `tools/ukur_orang.py`, sidik jari model lama `tools/uji_orang_lama.json`, saklar `?orang=lama`.

## Desain

### Jalur data (offline, `tools/siapkan_orang.mjs`, Node)

| Langkah | Isi |
| --- | --- |
| Baca GLB | parser GLB sendiri (JSON + biner), tanpa three.js; sumber di folder di luar repo (`--src`), keluaran yang di-commit hanya data olahan |
| Gabung | tiap karakter: semua mesh digabung menjadi satu, node 100x dan putaran -90 derajat dibakar ke meter y-atas, posisi, normal, warna titik, JOINTS_0 dan WEIGHTS_0 |
| Kelas warna | tiap titik diberi kelas dari mesh dan nama bahan: kulit (Skin, Skin_Darker), rambut (Hair, Eyebrows), mata, baju atas (mesh Body bukan kulit), celana (mesh Legs), sepatu (mesh Feet), tetap (topi, aksesori). Dipakai shader untuk mewarnai ulang dari palet `uShirt`, `uPants`, `uSkin`, `uHair` bila karakter diberi izin (`recolor`) |
| Tingkat detail | penyederhanaan `meshoptimizer` (npm, `simplifyWithAttributes`; bobot tulang, warna, kelas ikut dihitung): L0 sekitar 3.000, L1 sekitar 700, L2 sekitar 160 segitiga; normal datar dihitung ulang |
| Kemas | posisi int16 terkuantisasi per kotak batas, normal int8 x 3, tulang uint8 x 4, bobot uint8 x 4, warna RGB + kelas 4 byte; sekitar 22 byte per titik |
| Animasi | tiap klip dicuplik 20 fps, matriks kulit akhir (global x invers bind) per tulang disimpan sebagai kuaternion + translasi (2 texel RGBA32F); satu tekstur per jenis kelamin, satu baris per frame: 124 texel lebar x sekitar 300 baris |
| Klip buatan sendiri | dibakar dari Walk / Idle_Neutral dengan menimpa sudut tulang: Duduk (pinggul turun sampai paha mendatar di tinggi bangku, lutut 90 derajat), Duduk_Payung, Jalan_Payung dan Diam_Payung (lengan kanan terangkat memegang payung), Ngobrol (Idle ditambah menoleh dan gerak tangan, opsional). Wave dan Interact dipakai apa adanya |
| Keluaran | `experiences/cooper-station/assets/orang.data.js` (base64, dimuat lewat `<script>` biasa agar jalan dari file://) + `assets/KREDIT.md` + tab Tentang |

Perkiraan ukuran: sekitar 195 KB per karakter (3 tingkat detail), 13 karakter sekitar 2,5 MB, animasi sekitar 0,25 MB per jenis kelamin; total 3-4 MB base64 (tambahan pada halaman yang sudah memuat lagu 13 MB). Diukur di 28G1; tuas bila terlalu besar: kurangi jumlah karakter, L0 2.400 segitiga, animasi 15 fps.

### Karakter terpilih (usulan, pertanyaan 2)

| Jenis kelamin | Karakter | Dipakai di |
| --- | --- | --- |
| Pria | Business Man, Casual Character, Hoodie Character, Farmer, Worker, Beach Character | pusat kota, umum, taman, ladang dan utilitas, plaza |
| Pria (opsional) | Astronaut | spaceport, terminal, distrik astronom |
| Wanita | Suit, Animated Woman (dua warna), Worker, Adventurer, Punk | pusat kota, umum, utilitas, taman, anak muda |

Sekitar 12-13 model. Karakter dengan senjata atau tema fantasi dikecualikan.

### Pemasangan di game

| Aspek | Rancangan |
| --- | --- |
| Muat | `ORANG.load()` di langkah muat: decode base64, bangun geometri dan tekstur animasi; gagal = model kotak lama (otomatis) |
| Mesh | satu `InstancedBufferGeometry` per (karakter, tingkat detail); yang tidak punya instance tidak digambar (`visible = false`). Sekitar 13 x 3 = 39 mesh, tiap frame hanya yang berisi; usulan menekan draw call: L2 satu mesh per jenis kelamin (karakter umum, diwarnai palet) sehingga maksimum sekitar 13 x 2 + 2 = 28 draw, ditambah bayangan. Diputuskan dari ukur di 28G2 |
| Pembagian instance | `updatePeds()` memilah kandidat ke ember (model, tingkat detail) menurut `p.model` (tetap per orang, dari hash) dan jarak dengan histeresis 4 m; atribut `aP`, `aI`, `aJ` sama persis, tanpa atribut baru per instance |
| Vertex shader | gantikan putaran kaku: pilih klip dari `pose` (jalan, berdiri, duduk) dan payung, frame dari fase `aP.w` (jalan) atau `uTime` dan hash (diam), ambil 4 tulang x 2 texel (L0 campur dua frame, L1 dan L2 satu frame), posisi dan normal dikulit, lalu `groundFrame` dan `vegLight()` seperti sekarang |
| Warna | kelas titik memilih warna dasar karakter atau palet (`recolor`); warna titik asli dipertahankan sebagai variasi tona (agar kesan faset dan bayangan lukis tetap) |
| Payung | `PEDS.umbMesh` mengambil posisi tulang Wrist.R dari tekstur animasi yang sama (tambah satu atribut `bF` fase dan klip di mesh payung), menggantikan rumus sudut lengan |
| Duduk | klip Duduk disetel agar tinggi pinggul sama dengan `yOff` -0,38 m model lama (bangku dan kursi tidak berubah) |
| Anak | skala 0,6 seperti sekarang; kepala diperbesar di shader dengan bobot tulang kepala (proporsi anak) |
| Sinkron langkah | kecepatan putar frame dari `v` sehingga kaki tidak meluncur; panjang langkah klip Walk diukur di 28G1 dan disesuaikan dengan `p.ph += v / 1,45` |
| Bayangan | varian kedalaman memakai bentuk L1 untuk orang dekat dan menengah (`castAlpha`), jauh seperti sekarang |
| Kompilasi | semua program (utama dan kedalaman) ikut `warmFrame()`; cek `ukur_muat.py --cek` |
| Preset | radius L0 / L1 per preset (usulan: Ultra 30 / 90 m, Tinggi 25 / 80, Sedang 18 / 60, Rendah 12 / 45, Hemat tanpa L0 dan 35 m) dan jumlah karakter per preset |

### Anggaran (turunan dari ukur 28a, bukan ukur FPS)

| Lokasi (Ultra) | Band [0-12, 12-30, 30-90, > 90 m] | Segitiga orang sekarang | Perkiraan model GLB |
| --- | --- | --- | --- |
| New York | 6 / 7 / 23 / 295 | 0,07 juta | 13 x 3.000 + 23 x 700 + 295 x 160 = 0,10 juta |
| Pasar | 9 / 28 / 2 / 81 | 0,02 juta | 37 x 3.000 + 2 x 700 + 81 x 160 = 0,13 juta |
| Spaceport | 2 / 21 / 53 / 201 | 0,06 juta | 23 x 3.000 + 53 x 700 + 201 x 160 = 0,14 juta |

Tambahan 0,03-0,11 juta segitiga, di bawah 3% dari adegan. Biaya vertex lebih penting daripada segitiga: sekitar 6.000 titik x 16 pengambilan texel x paling banyak 37 orang dekat, dan `vegLight()` per titik; tuas: `vegLight()` per instance untuk L1 dan L2, L0 lebih sedikit.

## Tahapan

| Tahap | Isi | Effort | Model | Thinking | File dan fungsi yang disentuh |
| --- | --- | --- | --- | --- | --- |
| 28G0 | (selesai 17 Oktober 2026: lisensi dan KREDIT.md; seleksi karakter pakai usulan sampai Bhakti mengubahnya) Lisensi dan seleksi: konfirmasi lisensi dan sumber, pilih karakter, putuskan lokasi berkas sumber (di luar repo), `assets/KREDIT.md` | Low | Haiku 4.5 | low | `assets/KREDIT.md`, dokumen |
| 28G1 | (selesai 17 Oktober 2026, lihat Hasil 28G1) Alat olah `tools/siapkan_orang.mjs` (gabung, bakar satuan, kelas warna, LOD dengan `meshoptimizer`, kuantisasi, tekstur animasi, klip duduk dan payung), `orang.data.js`, uji Node `tools/uji_orang_data.cjs`, halaman pratinjau yang memutar data hasil olahan (karakter, LOD, klip, palet) untuk persetujuan; ukur ukuran berkas dan panjang langkah | High | Opus 5.5 | high | `tools/siapkan_orang.mjs` baru, `experiences/cooper-station/assets/orang.data.js` baru, `docs/cooper-station/orang/pratinjau-orang.html` baru |
| 28G2 | (selesai 17 Oktober 2026, lihat Hasil 28G2) Pasang di game: `ORANG.load()`, geometri dan tekstur animasi, vertex shader kulit, ember (model, LOD), ganti model kotak, `?orang=lama` penuh, `warmFrame()` | High | Opus 5.5 | high (shader rawan NaN di M1) | blok model orang `index.html` (sekitar 14389-14471), `updatePeds()`, `applyPedsPreset()`, `PEDS` |
| 28G3 | Perilaku: klip per keadaan (jalan, berdiri, duduk, payung, Wave untuk pengunjung, Interact untuk pasar), sinkron langkah, payung dari tulang tangan, baseball, anak | Medium | Sonnet 5.5 | high | `VS`, `PEDS.umbMesh`, `BASEBALL.people`, `VIS` |
| 28G4 | Distribusi karakter per zona, warna ulang dari palet, tinggi acak, pembagian jenis kelamin | Medium | Sonnet 5.5 | medium | pembuatan `PEDS.list` (atribut `p.model`), `look()` |
| 28G5 | Bayangan (L1), `vegLight()`, radius per preset, ukur draw call dan FPS di sandbox, tuas biaya | Medium | Opus 5.5 | high | `castAlpha`, `applyPedsPreset()` |
| 28G6 | Uji dan dokumen: `tools/uji_orang.py`, uji lama tetap lulus, `ukur_muat.py --cek`, lembar kontak, KREDIT dan tab Tentang, `CLAUDE.md`, hapus kode prosedural 28b bila disetujui | Medium | Sonnet 5.5 | medium | `tools/`, dokumen |

Urutan: 28G0, 28G1 (berhenti, minta persetujuan tampilan dan ukuran), 28G2, 28G3 dan 28G4, 28G5, 28G6. Rencana disusun oleh model satu tingkat di atas tahap terberat (High).

## Hasil 28G1 (selesai 17 Oktober 2026)

Alat `tools/siapkan_orang.mjs` (Node, three.js + GLTFLoader + `meshoptimizer` hanya di alat), keluaran `experiences/cooper-station/assets/orang.data.js`, pembaca `shared/orang_data.js` (`window.ORANGKIT`: `decode()`, `skin()` kulit CPU kembaran shader), uji `tools/uji_orang_data.cjs`, pratinjau `docs/cooper-station/orang/pratinjau-orang.html` (memutar data olahan yang sama dengan yang akan dipasang: 13 karakter, 3 tingkat detail, 8 klip, palet kota, kerangka, penanda tangan payung) dan tiga tangkapan (`pratinjau-jalan.png`, `pratinjau-lod.png`, `pratinjau-duduk.png`).

| Item | Hasil |
| --- | --- |
| Ukuran | `orang.data.js` 3,52 MB (biner 2,63 MB), di bawah batas 4,5 MB |
| Karakter | 13 (7 pria: Business Man, Casual, Hoodie, Farmer, Worker, Beach, Astronaut; 6 wanita: Suit, Animated Woman A dan B, Worker, Adventurer, Punk) |
| Segitiga | L0 2.992-3.000 (sumber 5.240-10.558), L1 692-700, L2 153-160; galat meshoptimizer 0,0014-0,003 / 0,007-0,010 / 0,020-0,027 (relatif terhadap ukuran model) |
| Animasi | 20 fps; pria 244 frame, wanita 308 frame; klip: Jalan, Diam, Lambai, Interaksi, Duduk, Jalan_Payung, Diam_Payung, Duduk_Payung; galat skala matriks tulang < 2e-5 (matriks kulit tegar, kuaternion + translasi cukup) |
| Langkah | Jalan pria 1,235 m per siklus (0,93 m/s kaki tumpu), wanita 1,443 m (0,87 m/s); game memakai 1,45 m per siklus, jadi frame diputar dari jarak tempuh dengan pengali stride (pria 1,17x lebih cepat) |
| Duduk | pinggul turun 0,430 m (pria), 0,472 m (wanita); lama 0,38 m. Pinggul duduk di 0,53 m, sesuai bangku 0,45-0,5 m. Kaki menapak (pergelangan kembali ke tinggi berdiri), tangan di pangkuan |
| Payung | tangan kiri ke depan: tinggi 1,14 m, depan 0,33 m, samping 0,21 m (pria), ayun selama berjalan 7-13 cm (model lama: 0,99 / 0,42 / 0,25) |
| Uji | `uji_orang_data.cjs` 53 dari 53 lulus (nilai valid, bobot 1, tulang < 62, normal satuan, tinggi, kuaternion satuan, loop Jalan mulus, tinggi duduk, langkah, tangan payung, kulit 13 x 3 x 8 tanpa nilai tidak valid, bentuk L1 dan L2 mengikuti L0: rata-rata 1,0-3,0 cm dan 2,3-6,0 cm) |

Temuan teknis yang mengubah rancangan:

- Nama tulang di GLTFLoader tanpa titik (`FootL`, bukan `Foot.L`).
- Tulang `Foot.L/R` dan `PT.L/R` bergaya IK (induknya Root, bukan betis), dan paha adalah anak `Body` bukan `Hips`: klip duduk menggeser `Body` dan memindahkan pergelangan ke ujung betis.
- Tulang tanpa trek animasi menyimpan timpaan frame sebelumnya; pose diam dikembalikan sebelum tiap cuplikan.
- Penyederhanaan meshoptimizer macet (hanya 2 segitiga dibuang) tanpa flag `Permissive`, karena model tersusun dari banyak titik terbelah; dengan flag itu target tercapai.
- Matriks dunia mesh = skala 100 dan putaran -90 derajat di x, dibakar ke titik bind (meter y-atas); matriks tulang akhir = `meshWorld x bindInv x tulang x bind x meshWorld^-1`.

Perbaikan setelah laporan Bhakti (kepala "noleh kanan kiri cepat", 17 Oktober 2026): gerak memang glitch di versi pertama. Penyebab: alat olah mengembalikan semua tulang ke pose diam sebelum tiap cuplikan, padahal mixer three.js hanya menulis nilai yang berubah dari nilai terakhir yang ia terapkan, sehingga tulang yang dikembalikan paksa tetap di pose diam (kepala menoleh sekitar 28 derajat pada frame pertama Diam dan Duduk, dan loncat 26-38 derajat di 2 frame tiap setengah siklus Jalan). Perbaikan: tidak ada pengembalian paksa; timpaan buatan (duduk, payung) dibatalkan dari snapshot hasil mixer. Pencegahan: alat olah membandingkan kulit hasil bakar dengan kulit three.js (galat maks 0 cm) dan uji baru memeriksa perubahan arah kepala per frame di 13 karakter x 8 klip (terbesar 3,3 derajat, batas 10); uji kini 54 dari 54. Tangan payung sekarang stabil (ayun 3-9 cm).

Kelemahan dan hal yang perlu dinilai Bhakti di pratinjau:

- L2 (160 segitiga) kasar (kepala runcing, tangan hilang); dimaksudkan untuk di atas 90 m.
- L1 (700) kehilangan fitur wajah; terbaca dari 30-90 m.
- Gaya tetap berfaset kartun seperti paket aslinya; warna titik membuat kesan tambalan tonal.
- Klip duduk dan payung buatan sendiri: lengan duduk agak lurus ke depan, tangan payung di sekitar pinggang, bukan di tangkai payung nyata; payung sendiri belum dipasang.
- Pratinjau dirender CPU di SwiftShader; kinerja shader GPU (kulit tekstur animasi) baru diuji di 28G2.
- Pesan `computeBoundingSphere ... NaN` muncul sekali di konsol halaman pratinjau; data dan hasil kulit diuji tanpa NaN (0 dari seluruh titik), jadi penyebabnya di halaman pratinjau (belum dicari).

Kredit: baris `orang.data.js` di `experiences/cooper-station/assets/KREDIT.md` dan teks atribusi di pratinjau. Berkas GLB sumber tidak di-commit. Alat butuh `THREE_LOCAL`, `MESHOPT_LOCAL`, `--men`, `--women` (lihat kepala berkas).

## Hasil 28G2 (selesai 17 Oktober 2026)

Model GLB terpasang di Copper (`experiences/cooper-station/index.html`): tag skrip `shared/orang_data.js` dan `assets/orang.data.js`, blok model orang lama dibungkus `if (!PEDS.newModel)` (cadangan otomatis bila data gagal dimuat atau `?orang=lama`), blok baru `else` (tekstur animasi per jenis kelamin `uAnim` RGBA32F 124 texel lebar, 39 `InstancedBufferGeometry` = 13 karakter x 3 tingkat, material per karakter dengan `uRec` / `uLum`, vertex shader kulit 4 tulang dengan campuran dua frame), `updatePedsNew()` (ember per (karakter, tingkat) menurut `p.model` dan jarak ke mata, histeresis 4 m), `PEDS.lodR` per preset, payung memakai titik tangan GLB.

| Item | Hasil |
| --- | --- |
| Atribut instance | `aP`, `aI`, `aJ` sama dengan model lama; simulasi pejalan kaki, kelompok, baseball, payung tidak berubah; model per orang dari generator acak sendiri (`p.model` 0..12), baseball dari hash posisi |
| Warna | warna titik asli (sRGB8 -> linear di shader); baju atas / celana / kulit / rambut diganti palet kota hanya untuk karakter yang diberi izin (`recolor`) dengan kecerahan titik asli dipertahankan |
| Langkah | fase jalan dikali `1,45 / strideM` (pria 1,235 m, wanita 1,443 m per siklus) agar kaki tidak meluncur; diam dan duduk memakai `uTime` dan hash posisi |
| Payung | klip Payung dipilih bila payung terbuka (`aJ.w > 0`); titik pegang di shader payung: berdiri (0,215; 1,14; 0,35), duduk (0,22; 0,68; 0,30); lengan loncat ke pose payung saat payung mulai terbuka (campuran dua klip ditunda ke 28G3) |
| Radius tingkat detail | Ultra 30 / 90 m, Tinggi 25 / 80, Sedang 18 / 60, Rendah 12 / 45, Hemat tanpa L0 dan 35 m |
| Kompilasi | satu ember dibiarkan terlihat di `warmFrame()`; `ukur_muat.py cooper-station --cek` lulus (0 program baru di frame pertama dan saat tombol) |
| Ukur (Ultra, sandbox) | orang tergambar 117 (pasar) / 331 (New York) / 275 (spaceport) / 282 (baseball); tingkat [L0, L1, L2] pasar [37, 2, 78], New York [13, 23, 295], spaceport [16, 59, 200]; segitiga orang 0,10-0,125 juta (lama 0,02-0,07 juta); ember digambar 27-36 (draw call adegan 659 / 1.033 / 748 / 663, model lama menambah 1) |
| Uji | `tools/uji_orang.py` baru: 11 dari 11 lulus (termasuk `?orang=lama` = sidik jari lama persis); `uji_pejalan_kaki.py` lulus; `uji_air_mancur.py` dan `uji_trotoar.py` gagal pada 1 dan 2 pemeriksaan yang sama persis di kode sebelum tahap 28 (diukur di worktree commit sebelumnya), jadi bukan akibat tahap ini; `qc_load.py` tanpa error |
| Tampilan | tangkapan layar game: orang berjalan berpakaian gelap dengan bayangan di jalan; wanita memegang payung hitam dengan tangkai di tangan |

Belum dicek: orang duduk di bangku (klip duduk teruji di pratinjau dan data, bukan tangkapan layar di game), FPS di GPU asli (draw call naik sekitar 30, titik per orang dekat sekitar 6.000), NaN di Apple M1, `vegLight()` per titik pada orang dekat.

Alat bantu sandbox: `/opt/pw-browsers/chromium_headless_shell-1248` ditautkan ke chromium 1194 yang ada agar skrip uji bawaan (`python tools/uji_*.py`) jalan; bukan bagian repo.

## Uji dan ukuran keberhasilan

| Pemeriksaan | Ambang (usulan, belum diukur) |
| --- | --- |
| Data olahan | tanpa NaN / Infinity, bobot tulang dijumlah 1 (+- 0,01), indeks tulang 0-61, normal tidak nol, tinggi 1,55-1,95 m, telapak di y = 0 |
| Segitiga per tingkat | L0 <= 3.000, L1 <= 750, L2 <= 180 |
| Kulit setelah penyederhanaan | di pose Walk dan Duduk, titik hasil L0 vs hasil model asli (rata-rata jarak <= 1,5 cm, maks <= 6 cm) dan tidak ada tepi > 1,5x |
| Animasi | frame pertama = terakhir (mulus), kaki tidak meluncur (<= 6 cm per langkah pada kecepatan 1,4 m/s), duduk: pinggul di tinggi `yOff` model lama +- 3 cm |
| Payung | titik tangan model baru dalam 3 cm dari titik pegang payung di jalan, diam, duduk |
| Ukuran berkas | `orang.data.js` <= 4,5 MB (usulan) |
| Muat | `ukur_muat.py cooper-station --cek` 0 program baru; waktu decode data dicatat |
| `?orang=lama` | sidik jari dan piksel identik dengan sebelum tahap 28 (`tools/uji_orang_lama.json`) |
| Uji lama | `uji_pejalan_kaki.py`, `uji_air_mancur.py`, `uji_trotoar.py`, uji baseball dalam `uji_ladang_foto_tur.py` tetap lulus |
| Render | tanpa nilai tidak valid di 5 preset x pagi / siang / malam |

## Risiko

| Risiko | Tingkat | Penanganan |
| --- | --- | --- |
| Lisensi tidak jelas atau bukan CC0 | tinggi sampai dikonfirmasi | 28G0 sebelum commit apa pun; tanpa lisensi yang jelas rencana ini berhenti |
| Gaya kartun berfaset tidak serasi dengan kota yang realistis | sedang | dinilai di pratinjau 28G1 sebelum dipasang; opsi normal halus untuk L0 dan L1; warna titik tetap |
| Ukuran halaman bertambah 3-4 MB | rendah-sedang | tuas di atas; diukur di 28G1 |
| Penyederhanaan merusak kulit (jari, ketiak, topi) | sedang | atribut bobot ikut dihitung, uji jarak ke model asli, jari boleh hilang di L1 dan L2 |
| Draw call naik (sekitar 28 + bayangan, dulu 2) | sedang | L2 per jenis kelamin, ember kosong tidak digambar, ukur di 28G5 |
| Biaya vertex shader (16 pengambilan texel per titik, `vegLight()` per titik) | sedang | L0 hanya <= 30 m dan maks per preset, ukur GPU asli oleh pemilik |
| Kaki meluncur atau langkah tidak sinkron | sedang | panjang langkah klip diukur, laju frame dari `v` |
| Duduk dan payung tidak pas dengan bangku dan tangan | sedang | klip buatan dengan sasaran angka (tinggi pinggul, titik tangan) dan uji |
| NaN di M1 | sedang | aturan GPU proyek: tanpa `normalize()` vektor nol (kuaternion dijaga), tanpa `pow()` negatif; uji akhir di M1 oleh Bhakti |

## Batasan

- Tidak ada pakaian ganti atau modul tubuh yang dicampur acak antar karakter di game (hanya karakter utuh dan warna ulang).
- Wajah tanpa ekspresi dan tanpa sinkron bibir; jari hanya ikut klip yang ada.
- Orang tidak menghindari pemain, belum ada orang di dalam trem dan lift.
- Tidak ada animasi kegiatan baru selain klip paket dan klip buatan di atas (tanpa duduk makan, membaca ponsel, dll.).
- Astronaut Millar tidak diubah. Catatan: `Astronaut.glb` ada di paket pria dan bisa dipertimbangkan nanti untuk kru atau penumpang, tetapi tubuh orang pertama Millar (IK, kulit CPU) tidak ikut rencana ini.
- Berkas sumber GLB tidak di-commit (32 MB); yang masuk repo hanya `orang.data.js` hasil olahan.

## Status kode prosedural 28b

`shared/orang.js` (PEDKIT), `docs/cooper-station/orang/blokout-orang.html`, `tools/uji_orang_bentuk.cjs` digantikan jalur GLB. Dibiarkan sampai tampilan GLB disetujui di 28G1, lalu dihapus di 28G6 (usulan) atau dijadikan cadangan bila paket GLB tidak jadi dipakai. Alat ukur 28a (`tools/ukur_orang.py`, `tools/uji_orang_lama.json`, `PEDS.lama`) tetap dipakai.

## Pertanyaan untuk pemilik

1. Dari mana paket ini diunduh dan apa lisensinya? Apakah boleh memakai model olahan dan mencantumkannya di repo dan tab Tentang (kredit pembuat)? Bila ada berkas lisensi atau halaman sumbernya, mohon kirim isi atau tautannya.
2. Karakter yang dipilih (daftar usulan di atas): ada yang wajib masuk atau wajib keluar? Astronaut mau ikut di spaceport?
3. Gaya: tetap berfaset seperti di paket (usulan), atau normal dihaluskan agar lebih lembut?
4. Warna ulang: izinkan baju dan celana diganti dari palet kota (lebih beragam, tetapi mengubah desain asli), atau pertahankan warna asli karakter? Usul: warna ulang hanya untuk Casual, Hoodie, Beach, Worker.
5. Tambahan 3-4 MB data di halaman Copper boleh?
6. Berkas sumber GLB: tidak di-commit (usulan) dan Anda menyimpan zip-nya, atau perlu masuk repo di folder terpisah?

## Verifikasi

```
node tools/siapkan_orang.mjs --src <folder GLB> --out experiences/cooper-station/assets/orang.data.js
node tools/uji_orang_data.cjs
CHROMIUM=/opt/pw-browsers/chromium THREE_LOCAL=<scratchpad> python3 tools/uji_orang.py
python3 tools/uji_pejalan_kaki.py
python3 tools/uji_air_mancur.py
python3 tools/uji_trotoar.py
python3 tools/ukur_muat.py cooper-station --cek
python3 tools/uji_bahasa.py
python3 tools/qc_load.py
```

Pemilik menguji visual dan FPS di GTX 1060 dan MacBook M1; 28G2 dan 28G5 wajib dicek di sana (sandbox SwiftShader tidak memperlihatkan NaN atau selisih FPS GPU asli).
