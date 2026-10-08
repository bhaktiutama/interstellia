# Rencana Tahap 25 Copper Corn Station: pohon beragam dan realistis

Per 7 Oktober 2026 · disusun atas permintaan Bhakti

## Ringkasan

- Sekarang ada 8 jenis pohon prosedural (16 template). Gambar acuan memuat sekitar 28 jenis unik dengan bentuk tajuk, jenis daun, dan kulit yang jauh lebih beragam.
- Rencana: ubah jenis pohon dari cabang kode per nama menjadi tabel data, tambah 13 jenis (total 21) dari 4 keluarga daun (lebar utuh, majemuk, jarum, sisik), lalu tambah kulit bertekstur, goyang daun per jenis, dan palet musim per jenis.
- Urutan dari yang murah dan langsung terlihat (jenis dengan bentuk yang sudah ada) ke yang berat (shader daun jarum dan sisik). Status: rencana saja, belum ada kode yang diubah.

## Gambar acuan dan kondisi sekarang

Gambar acuan adalah katalog 30 label (ilustrasi stok, tidak disalin; hanya daftar jenis dan keragaman bentuk yang dipakai sebagai acuan). Label ganda: Eastern Cottonwood muncul dua kali, Beech dan European Beech, Aspen dan Quaking Aspen.

| Aspek | Gambar acuan | Sekarang (8 jenis) | Kekurangan |
| --- | --- | --- | --- |
| Jumlah jenis | sekitar 28 unik | 8 (oak, elm, poplar, maple, birch, pine, willow, bunga) | 13 jenis sasaran belum ada |
| Bentuk tajuk | kolom (arborvitae, poplar, aspen), kerucut (fir, hemlock, cedar), kubah (oak, walnut, beech, basswood), vas (elm, ash), menjuntai (willow) | kubah (oak, maple, bunga), vas (elm), kolom (poplar), kerucut sempit (pine), menjuntai (willow), ramping (birch) | kerucut lebar dan kolom sisik belum ada |
| Jenis daun | lebar utuh (beech, aspen, cottonwood), berlekuk (oak, maple), majemuk menyirip (ash, walnut, hickory, locust), jarum (fir, hemlock, pine), sisik (arborvitae, redcedar) | kartu daun berlekuk dari atlas 4 kolom (indeks 0 sampai 3, `uv x 0,25`) untuk semua jenis; jarum hanya kartu pinus | daun majemuk, jarum dengan geometri sendiri, dan sisik belum ada |
| Warna | hijau tua, biru-hijau (silver fir), kuning-hijau (honey locust), jingga (beech, aspen), merah (cherry) | palet per jenis di `leafColorFor()` untuk mode Hijau, Campur, Gugur | biru-hijau dan hijau gelap konifer belum ada |
| Kulit | putih bergaris (birch), abu-abu halus (beech), beralur (ash), bersisik (pine, cedar) | satu warna per jenis (`K.bark`), dikali 0,85 sampai 1,0 menurut tinggi, tanpa tekstur | kulit tidak punya ciri jenis |
| Goyang | daun bulat tangkai pipih (aspen) bergetar, daun lain kaku | goyang sama untuk semua jenis, dari angin global `uWind` | tidak ada parameter goyang per jenis |

## Yang sudah ada di kode

- `TREE_KINDS` (`experiences/cooper-station/index.html` baris 7873): parameter per jenis (trunk, kids, spread, lenR, leafLevel, cards, card, atlas, up, upL, bark).
- `makeTree()` (baris 7884): membangun batang dan cabang rekursif, daun sebagai kartu 4 titik, dua geometri (kulit dan daun), lalu impostor `OCT` dipanggang sekali per template (baris 8273 dan seterusnya).
- Kekhususan per jenis ditulis langsung dengan nama jenis di beberapa baris `makeTree()` (contoh baris 7914, 7930, 7936, 7937, 7940). Jenis baru harus lewat cabang kode baru jika tetap begini.
- Template dibuat di baris 8108 (16 template, 2 bentuk per jenis). Pohon kota 11.587 (12b-2), hutan 5.222 (14a).
- Warna daun per jenis di `leafColorFor()` (baris 8414), palet di `LEAF_PAL` (baris 8411).

## Prinsip

1. Fitur lama tidak berubah. Delapan jenis dan 16 template yang ada tetap identik. Jenis baru dan perubahan bentuk diatur lewat saklar, misalnya `?pohon=lama` untuk perbandingan (pola sama seperti `?ragam=0` dan `?v4=0`).
2. Jenis baru = satu baris tabel data, bukan cabang kode baru.
3. Bentuk tajuk datang dari arsitektur cabang (cabang utama tunggal untuk fir dan pinus, cabang sejajar untuk oak dan maple, cabang menjuntai untuk willow dan hemlock), bukan dari satu kubah yang dipaksa.
4. Semua bentuk dan tekstur dibuat sendiri (prosedural). Tidak ada aset dari gambar stok.

## Jenis baru yang diusulkan (13 jenis, total 21)

Ciri daun, kulit, dan warna di tabel ini adalah ciri umum jenis tersebut yang dipakai sebagai acuan bentuk. Ini bukan data ukur. Target tinggi dewasa per jenis belum ditetapkan dan perlu referensi sebelum tahap 25b.

| Keluarga | Jenis | Bentuk tajuk | Daun | Kulit | Warna |
| --- | --- | --- | --- | --- | --- |
| Konifer jarum | Silver fir, balsam fir | kerucut rapat | jarum pendek di cabang datar | abu-abu halus | hijau gelap, biru-hijau (fir) |
| Konifer jarum | Eastern hemlock | kerucut, ujung menjuntai | jarum kecil berderet dua sisi | abu-abu | hijau gelap |
| Konifer sisik | Arborvitae | kolom | sisik pipih, semprot datar | halus | hijau kekuningan |
| Konifer sisik | Eastern redcedar | kerucut sempit | sisik pipih | merah-cokelat mengelupas | hijau gelap |
| Majemuk | Ash (European, black, white) | vas | majemuk 5 sampai 11 anak daun | abu-abu beralur | kuning (musim gugur) |
| Majemuk | Walnut | kubah | majemuk besar | gelap | kuning-cokelat |
| Majemuk | Bitternut hickory | kubah | majemuk | abu-abu | kuning-cokelat |
| Majemuk halus | Black locust | terbuka | anak daun kecil, berduri | cokelat beralur | kuning |
| Majemuk halus | Honey locust | terbuka, cabang halus | daun ganda halus | cokelat | kuning-hijau |
| Lebar utuh | European beech, beech | kubah rapat | lebar utuh bertepi halus | abu-abu halus | jingga-perunggu |
| Lebar utuh | Chestnut | kubah | memanjang bergerigi | retak | kuning |
| Lebar utuh | Basswood | kubah rapat | berbentuk hati | halus | kuning |
| Bulat bergoyang | Quaking aspen | kolom sempit | bulat, tangkai pipih | putih-keperakan | kuning-jingga |

Catatan: "Poplar" (sudah ada) dan Eastern cottonwood dianggap satu keluarga. Cottonwood tidak dibuat jenis baru. Buckthorn, Eve's necklace, dan cherry tidak masuk tahap ini (cherry sudah dekat dengan `bunga`).

## Tahapan

| Tahap | Isi | Effort | Model | Thinking | Perkiraan file dan fungsi |
| --- | --- | --- | --- | --- | --- |
| 25a | Saklar `?pohon=lama`. Tabel data `TREE_SPECIES` menggantikan `TREE_KINDS` dan cabang `kindName ===`. Uji: 8 jenis lama menghasilkan geometri identik | Medium | Sonnet 5.5 | medium | `TREE_KINDS`, `makeTree()`, template di baris 8108 |
| 25b | Enam jenis dengan bentuk yang sudah ada (aspen, beech, basswood, chestnut, ash, walnut) lewat parameter saja, dengan palet musim sendiri. Tinggi target dari referensi | Medium | Sonnet 5.5 | medium | `TREE_SPECIES`, `leafColorFor()`, `LEAF_PAL` |
| 25c | Atlas daun dari 4 ke 12 kolom (hati, lonjong bergerigi, bulat, lebar utuh, berlekuk) dibuat di canvas. Palet per jenis dan per mode Hijau, Campur, Gugur | Medium | Sonnet 5.5 | medium | atlas daun (canvas), `LEAF_PAL`, `leafColorFor()` |
| 25d | Daun majemuk: kartu anak daun di sepanjang tangkai untuk ash, walnut, hickory, black locust, honey locust. Geometri CPU, tanpa GLSL baru. Jumlah vertex dicatat | Medium | Sonnet 5.5 | medium | `makeTree()` (pembuat daun), `TREE_SPECIES` |
| 25e | Konifer jarum dan sisik: silver fir, balsam fir, hemlock, arborvitae, redcedar. Geometri semprot dan shader daun untuk jarum dan sisik (normal, translusensi dari bawah tajuk). Impostor ikut | High (shader kustom) | Opus 5.5 orkestrator | xhigh (normalize dan pow di shader, risiko NaN di M1) | `LEAF_VS`, `LEAF_FS`, `makeTree()`, `OCT_FS` |
| 25f | Kulit bertekstur per jenis: birch putih bergaris dengan lentisel gelap, beech halus, ash beralur, pinus bersisik. Tekstur canvas dari uv yang sudah ada (`buv`), warna `K.bark` tetap sebagai pengali | Medium | Sonnet 5.5 | medium | `makeTree()` (kulit), material kulit, atlas kulit |
| 25g | Goyang daun per jenis: atribut `aFlex` per daun, aspen dan poplar tertinggi, konifer terendah. Nilai di `TREE_SPECIES` | High (shader daun) | Opus 5.5 subagent | high | `LEAF_VS`, atribut daun di `makeTree()` |
| 25h | Distribusi per zona: jalan kota, taman, tepi air, bukit, permukiman, hutan. Jenis per zona dari hash posisi, dengan batas maksimal per jenis per distrik | Medium | Sonnet 5.5 | medium | `add()` penempatan, zona dan distrik, `FOREST`, `YARD_TREES` |
| 25i | Anggaran dan profil: waktu muat (bake impostor), memori atlas, draw call, FPS di GTX 1060 dan M1. Preset Hemat dan Rendah tanpa template mahal (`TREES.forestLod`, `lodD`) | High (profil GPU) | Opus 5.5 orkestrator | high | `octBake()`, `OCT`, `PRESETS`, `applyForestPreset()` |
| 25j | Uji `tools/uji_pohon.py` diperluas: jumlah jenis, tanpa NaN, tanpa template kosong, mode `?pohon=lama` identik, warna musim | Medium | Sonnet 5.5 | medium | `tools/uji_pohon.py` |
| - | Dokumen ini, CLAUDE.md (peta kode dan riwayat) | Low | Haiku 5.5 | low | `CLAUDE.md`, `docs/cooper-station/` |

Urutan kerja: 25a, 25b, 25c, 25d, 25f, 25e, 25g, 25h, 25i, 25j. Kulit (25f) didahulukan sebelum shader daun agar uji visual bisa dilakukan sebelum shader baru. 25i dikerjakan setelah isi jenis final, karena angka anggaran berubah tiap jenis ditambah.

Gerbang uji: setiap tahap diuji Bhakti secara visual di GTX 1060 dan M1 sebelum tahap berikutnya. Sandbox uji (SwiftShader) tidak menilai realisme daun, dan tidak mengukur FPS.

## Anggaran dan risiko

| Hal | Perhitungan | Catatan |
| --- | --- | --- | --- |
| Template | 16 sekarang, 21 jenis x 2 bentuk = 42 template | Target 42, diukur di 25i |
| Atlas impostor Ultra | `OCT.N` 8 x `OCT.cell` 128 = 1.024 px per sisi, RGBA 4 byte = 4 MB per atlas | Jika satu atlas per template (perlu dicek di `octBake()`): 16 x 4 MB = 64 MB sekarang, 42 x 4 MB = 168 MB rencana |
| Impostor preset lain | 256 x 256 px per template, 4 byte = 256 KB per template | 42 template = sekitar 10,5 MB |
| Bake saat muat | satu template per frame lewat `octStep()` | Bertambah 26 frame di Ultra, belum diukur |
| Kolom daun | 4 kolom sekarang, 12 kolom rencana | Tekstur daun tetap satu atlas |

Risiko utama: memori atlas Ultra dan jumlah draw call. Kedua hal baru bisa dipastikan dari 25i. Jika memori terlalu besar, opsi: template bentuk kedua hanya di Ultra dan Tinggi, atau atlas dibagi per keluarga.

## Batasan dan penyederhanaan

| Hal | Catatan |
| --- | --- |
| Biologi | Bentuk dan ciri terinspirasi jenis nyata. Stasiun O'Neill di orbit Saturnus tidak mengklaim ekologi nyata |
| Sumber visual | Gambar acuan dipakai sebagai daftar jenis, tidak disalin. Semua bentuk dibuat prosedural |
| Simulasi | Tidak ada pertumbuhan, persaingan cahaya, atau tanah per pohon. Realisme dari bentuk, daun, kulit, goyang, dan warna |
| Jauh | Pohon jauh tetap impostor 256 px (atau 1.024 px Ultra). Detail jarum tidak terlihat di jarak jauh |
| Campuran di kota | Konifer belum dipastikan boleh di kota (lihat pertanyaan K2) |
| Pengukuran | Tidak ada angka FPS atau waktu muat yang diukur dalam rencana ini |

## Pertanyaan untuk pemilik

| No | Pertanyaan | Bawaan jika tidak dijawab |
| --- | --- | --- |
| K1 | Semua 13 jenis, atau dimulai dari 6 jenis di 25b saja? | Semua 13 jenis, bertahap per tahap |
| K2 | Konifer boleh di kota, atau hanya di taman, hutan, bukit, dan tepi air? | Hanya di taman, hutan, bukit, dan tepi air |
| K3 | Musim tetap tiga mode di "Suasana daun", atau ditambah musim berjalan? | Tetap tiga mode |

## Hasil

| Tahap | Status | Hasil |
| --- | --- | --- |
| 25a | Selesai, menunggu uji visual Bhakti | `TREE_KINDS` jadi `TREE_SPECIES` dengan nilai bawaan `TREE_DEF` (jit0, tpos, clMode, leader, crown). Cabang `kindName ===` di `makeTree()` hilang. Saklar `?pohon=lama` disiapkan (belum berefek, jenis baru di 25b). Uji: sidik jari FNV-1a dari 16 template (indeks, atribut, dan ukuran per template) sama dengan sebelum perubahan, 0 field berbeda, dengan dan tanpa `?pohon=lama`. Review terpisah: 336 pohon (16 template asli dan 40 benih tambahan per jenis) dibandingkan bit per bit dengan kode HEAD, 0 beda. `tools/qc_load.py` tanpa error; `tools/uji_pohon.py` 7 cek lolos |
| 25b | Selesai, menunggu uji visual Bhakti | 6 jenis baru (aspen, beech, basswood, chestnut, ash, walnut), 2 bentuk per jenis = template 16-27 di belakang template lama. Sebagian oak dan elm diganti per zona dari hash posisi sendiri `hsh3`: kota basswood 18%, ash 14%, beech 8%; taman beech 12%, chestnut 10%, basswood 8%, walnut 8%, ash 6%, aspen 6%; luar kota walnut 12%, ash 10%, aspen 10%, chestnut 8%, beech 6% (persen dari oak dan elm yang tersisa). Posisi, skala dasar, dan kolisi tetap. Halaman Cooper, promenade Skyway, dan hutan 14a tidak diganti. Warna musim per jenis dari field `fall`. `?pohon=lama` = 16 template, identik dengan sebelum 25a (0 beda) |
| 25c | Selesai, menunggu uji visual Bhakti | Atlas daun kedua `leafTex2` (2.048 x 1.024 px, 4 x 2 sel 512 px, RNG sendiri) untuk 6 jenis 25b: bulat bertangkai (aspen), lonjong tepi rata (beech), hati (basswood), lonjong bergerigi (chestnut), majemuk 9 anak daun (ash), majemuk 15 anak daun (walnut); 2 sel dicadangkan untuk konifer 25e. Indeks atlas jenis 4-9; UV kartu daun atlas >= 4 dihitung ke sel 4 x 2, rumus atlas 0-3 tidak berubah. Warna musim beech ditambah perunggu (`LEAF_PAL.perunggu`). Gambar atlas: `docs/cooper-station/gambar/atlas-daun-25c.webp` |
| 25d | Selesai, menunggu uji visual Bhakti | Daun majemuk sebagai geometri: tiap posisi kartu pada jenis majemuk diganti 4-6 tangkai daun (pita 2 ruas, 6 verteks, separuh ujung merunduk, helai hampir mendatar) bertekstur satu daun majemuk utuh. Sel atlas 4 dan 5 digambar ulang jadi 4 daun majemuk tunggal per setengah sel (ash / hickory 9 anak daun, black locust 17 anak daun kecil, walnut 17 anak daun, honey locust daun ganda halus). Ash dan walnut beralih ke tangkai daun; 3 jenis baru: hickory, black locust, honey locust (template 28-33, ditambah di akhir daftar zona: pilihan 25b tetap). Tanpa GLSL baru. Gambar: `docs/cooper-station/gambar/pohon-majemuk-25d.webp` |
| 25e | Selesai, menunggu uji visual Bhakti | 4 konifer (total 21 jenis): fir (mewakili silver fir dan balsam fir), hemlock, arborvitae, redcedar, template 34-41. Semprot jarum (fir, hemlock) dan sisik (arborvitae, redcedar) digambar di sel cadangan 6-7 atlas kedua, dipasang dengan pita tangkai 25d (`frond.roll` memutar helai; arborvitae tegak). Mesin cabang kerucut / kolom dengan pengali panjang cabang `clK` (bawaan 1, jenis lama identik). Penempatan K2: tidak di jalan kota; taman 10% dan luar kota 14% dari oak / elm tersisa; hutan 14a: 40% pinus jadi fir (22%) atau hemlock (18%) dengan tinggi mutlak tiap pohon tetap. Tanpa GLSL baru. Gambar: `docs/cooper-station/gambar/konifer-25e.webp` |
| 25f | Selesai, menunggu uji visual Bhakti | Tekstur kulit per jenis `BARK_TEX` (7 kanvas 128 x 256 px, RNG sendiri, ukuran ulangan sama dengan kulit lama): putih berlentisel dan bercak hitam (birch), putih keabuan bermata wajik (aspen), halus berbintik (beech, fir), alur silang wajik (ash, walnut, hickory, chestnut, black locust), lempeng pipih beretak (pinus, hemlock, honey locust), serat mengelupas (redcedar, arborvitae), lentisel mendatar (pohon bunga). Field `barkT` per jenis; oak, elm, poplar, maple, willow, basswood tetap memakai kulit lama. Warna `K.bark` dan UV tidak berubah. Gambar: `docs/cooper-station/gambar/kulit-25f.webp` |
| 25g | Selesai, menunggu uji visual Bhakti | Goyang daun per jenis: atribut `aFlex` per verteks daun (x = pengali goyang angin, y = getar cepat 11-13 rad/s), nilai dari field `flex`. Aspen 1,6 / 1,0 (bergetar), poplar 1,4 / 0,6, willow 1,5, honey locust 1,3 / 0,2, birch 1,2 / 0,3, jenis majemuk 1,1-1,2 / 0,15, oak dan chestnut 0,8, beech 0,9, konifer 0,3-0,6, lainnya 1. Di `LEAF_VS` dibungkus `#ifdef LEAF_FLEX` (daun, bayangan, bake); `?pohon=lama` tanpa define dan tanpa atribut = shader lama |
| 25h | Selesai, menunggu uji visual Bhakti | Penahan angin luar kota dipilih per sel 80 m (satu ruas barisan seragam): poplar 40%, pinus 20%, redcedar 15%, aspen 10%, fir 10%, arborvitae 5%. Batas pangsa satu jenis per distrik 30% (di luar hutan 14a); kelebihan diganti jenis lain dari daftar zona pohon itu, urut hash posisi (113 pohon dipindah). Halaman Cooper, promenade Skyway, hutan tidak diganti |
| 25i | Selesai (sandbox), FPS menunggu Bhakti | Diukur: waktu muat, draw call, segitiga, memori. Dua penghematan tanpa ubah gambar: (1) mesh kulit dan daun dekat tanpa pohon disembunyikan (`visible = false`, hemat persiapan program per pass); (2) bake impostor oktahedral memakai satu target ber-depth bersama `OCT.bake` lalu disalin ke tekstur per template tanpa depth: Ultra 392 -> 232 MB untuk 42 template (cara lama `?octkopi=0`; hasil identik byte per byte di 7 template yang diuji). Preset Hemat dan Rendah tidak perlu diubah |
| 25j | Belum dikerjakan | - |
| 25k | Selesai, menunggu uji visual Bhakti | Tajuk padat (revisi dari 3 foto Bhakti: pinus acak, tajuk kurus dan jarang, belum seperti referensi). Semua 21 jenis kini dibangun dari amplop tajuk per kelompok bentuk: oval (oak, maple, birch, aspen, beech, basswood, chestnut, ash, hickory, black locust), kubah (walnut, pohon bunga), vas (elm), payung (honey locust), kolom (poplar, arborvitae), kerucut (pinus, fir, hemlock, redcedar), juntai (willow). Gugus daun mengisi amplop (70% di kulit luar, 30% di dalam), cabang utama dari batang ke dalam amplop, AO atas terang / dalam dan bawah gelap lewat atribut (tanpa shader baru). Pita tangkai (25d) dan semprot (25e) diganti gugus daun penuh di atlas kedua 4 x 3. Gambar: `docs/cooper-station/gambar/tajuk-padat-25k.webp` |

### Hasil terukur 25b (sandbox, di luar hutan 14a)

| Jenis | Jumlah pohon | Tinggi p10 / p50 / p90 (m) | hRel (perkiraan) |
| --- | --- | --- | --- |
| elm (pembanding) | 2.703 | 7,9 / 9,9 / 13,6 | 1,0 |
| basswood | 1.023 | 7,1 / 8,8 / 10,6 | 0,95 |
| ash | 943 | 7,4 / 9,0 / 13,3 | 0,95 |
| beech | 568 | 8,1 / 10,1 / 15,0 | 1,05 |
| walnut | 157 | 10,5 / 13,1 / 14,9 | 0,85 |
| aspen | 125 | 9,6 / 11,5 / 14,0 | 0,8 |
| chestnut | 123 | 10,5 / 13,3 / 15,7 | 0,9 |

Uji: `tools/uji_pohon.py` 14 jenis dan 6 cek tinggi jenis baru lolos; Campur 22,2% (sebelum 25b 22,3%), Gugur 64,6% (63,4%), Hijau 3,2%. `tools/qc_load.py` tanpa error. Geometri template 0-15 identik dengan sebelum 25a; yang berubah hanya panjang buffer warna per instance `aLeafC` oak dan elm, karena jumlah pohonnya berkurang.

Catatan 25b:
- hRel adalah perkiraan dari kisaran tinggi dewasa umum per jenis, bukan dari sumber terukur. Skala = hRel x rata-rata tinggi template elm / rata-rata tinggi template jenis itu.
- Walnut, aspen, dan chestnut tampak lebih tinggi dari elm. Penyebabnya, mereka banyak ditempatkan di taman dan luar kota, yang skala dasarnya lebih besar (kota 0,72 sampai 0,85, luar kota 0,8 sampai 1,25). Di zona yang sama, urutan tingginya mengikuti hRel.
- Kolisi batang pohon bukit dihitung dari template lama sebelum jenis diganti, sama seperti 12b-2. Bedanya beberapa sentimeter, sebab jari-jari batang template 0,2 sampai 0,4 m.
- Tambah 12 template berarti tambah mesh instanced (kulit, daun, impostor) dan 12 bake impostor oktahedral di Ultra. Draw call, waktu muat, dan FPS belum diukur (25i).
- Atlas daun masih 4 kolom. Bentuk daun jenis baru memakai kolom 0 dan 1 yang sudah ada; bentuk daun khas tiap jenis baru datang di 25c.

Catatan 25c:
- Berbeda dari rencana awal (satu atlas 4 -> 12 kolom): atlas lama tidak diubah, karena RNG penggambarnya (`trr`) juga dipakai tekstur kulit kayu dan jagung, dan mengubah ukuran atlas mengubah sampel tekstur 8 jenis lama. Jadi 8 jenis lama tetap memakai atlas lama (oak dan maple belum mendapat daun berlekuk baru); jenis 25b memakai atlas kedua.
- Uji: `?pohon=lama` identik dengan sebelum 25a (16 template, 0 beda); di mode bawaan template 0-15 identik, template 16-27 hanya berubah UV daun. `tools/uji_pohon.py` semua lolos (angka sama dengan 25b), `tools/qc_load.py` tanpa error.
- Warna musim tetap bekerja: kriteria hijau `LEAF_RECOLOR` (g - max(r, b) > 0,03 linear) dihitung untuk rentang warna atlas baru (rona HSL 70-120): selisih 0,055 sampai 0,11.
- Memori: atlas kedua 2.048 x 1.024 RGBA = 8 MB, sekitar 10,7 MB dengan mipmap. Belum diukur di GPU.

### Hasil terukur 25d (sandbox, di luar hutan 14a)

| Jenis | Jumlah pohon | Tinggi p10 / p50 / p90 (m) | Verteks daun per template | Segitiga daun per template |
| --- | --- | --- | --- | --- |
| oak (pembanding, kartu) | - | - | 1.056 | 528 |
| ash | 943 | 7,5 / 9,0 / 13,3 | 3.456 | 2.304 |
| walnut | 157 | 10,6 / 12,8 / 14,9 | 3.888 | 2.592 |
| hickory | 98 | 12,1 / 14,9 / 17,4 | 3.456 | 2.304 |
| black locust | 71 | 10,6 / 12,8 / 15,3 | 4.536 | 3.024 |
| honey locust | 452 | 6,1 / 7,8 / 9,9 | 3.780 | 2.520 |

Catatan 25d:
- Daun jenis majemuk 3,3 sampai 4,3 kali verteks oak per pohon dekat (hanya dalam radius LOD; jauh tetap impostor). Dampak FPS belum diukur (25i); bila berat, `frond.n` bisa diturunkan per preset.
- Uji: `?pohon=lama` identik dengan sebelum 25a (0 beda); template 0-15 di mode bawaan identik (selain panjang `aLeafC` karena jumlah oak dan elm berkurang lagi: elm 2.703 -> 2.379). Jumlah pohon 6 jenis 25b tidak berubah. `tools/uji_pohon.py` 17 jenis dan 9 cek tinggi lolos; Campur 22,2%, Gugur 65,0%. `tools/qc_load.py` tanpa error.
- Ukuran tangkai daun dibesarkan sekitar 3 kali ukuran nyata (0,75-1,25 m) supaya tajuk terisi dengan jumlah verteks wajar; dari dekat sekali daun tampak besar.
- Bentuk tajuk dicek dengan render adegan bake tiap template di sandbox (bukan uji visual di GPU nyata).

### Hasil terukur 25e (sandbox)

| Jenis | Jumlah pohon (di hutan) | Tinggi p10 / p50 / p90 (m) | Verteks daun per template | Segitiga daun per template |
| --- | --- | --- | --- | --- |
| pine (pembanding, kartu) | - | - | 816 | 408 |
| fir | 591 (530) | 21,0 / 27,9 / 33,5 | 5.760 | 3.840 |
| hemlock | 485 (449) | 22,4 / 28,1 / 33,2 | 5.328 | 3.552 |
| arborvitae | 35 (0) | 7,2 / 8,5 / 9,6 | 2.808 | 1.872 |
| redcedar | 47 (0) | 9,0 / 11,2 / 12,7 | 4.896 | 3.264 |

Catatan 25e:
- Berbeda dari rencana: tidak ada GLSL baru. Shader daun sudah punya translusensi dari bawah tajuk (`vBack`) dan normal tajuk (`aCn`); semprot konifer cukup memakai pita tangkai 25d. Risiko NaN baru di M1 nol karena tidak ada shader yang diubah.
- Uji: `?pohon=lama` identik dengan sebelum 25a (0 beda). Template 0-33 identik dengan 25d (kecuali black locust yang dirapatkan di akhir 25d). `tools/uji_pohon.py` 21 jenis, konifer tidak di jalan kota (0 pohon), semua cek lolos; Campur 22,2%, Gugur 64,4%. `tools/uji_hutan.py` lolos (5.222 pohon, tinggi 22-35 m, jalan setapak kosong). `tools/qc_load.py` tanpa error.
- Titik terendah daun semua konifer -0,41 m dari dasar template (sama seperti jenis lama). Hemlock sempat -1,7 m (cabang bawah menjuntai masuk tanah, diperbesar 1,9x di hutan); cabang terbawah dinaikkan.
- Konifer memakai 5 sampai 7 kali verteks daun pinus kartu (816). Di hutan, pohon dalam 70 m (Ultra) memakai mesh penuh: sekitar 980 fir dan hemlock di hutan, sebagian kecil yang dekat. Dampak FPS belum diukur (25i).
- Fir dari samping berbentuk kerucut sempit rapat, belum selebar fir dewasa di alam; bisa dilebarkan lewat `clK`.

Catatan 25f:
- Jenis lama yang tampilannya berubah di mode bawaan: birch (dulu alur abu-abu, kini putih berlentisel), pinus (lempeng), pohon bunga (lentisel). Ini memang isi rencana 25f; `?pohon=lama` tetap memakai kulit lama untuk semua jenis (dicek: 16 template, 1 tekstur kulit yang sama).
- Mode bawaan memakai 8 tekstur kulit (lama + 7 baru), masing-masing 128 x 256 px (128 KB, sekitar 170 KB dengan mipmap): total tambahan sekitar 1,2 MB memori GPU.
- Geometri tidak berubah (`?pohon=lama` 0 beda); `tools/uji_pohon.py` semua lolos, `tools/qc_load.py` tanpa error.
- Tekstur dicek lewat pratinjau dan render batang dari dekat di sandbox; detail lentisel dan lempeng lebih kecil dari 1 piksel layar pada jarak lebih dari sekitar 30 m (mipmap menghaluskannya).

### Hasil terukur 25g (sandbox)

Uji goyang: adegan bake satu template dirender pada uTime 0 dan 0,37 s dengan angin 0,3, dihitung bagian piksel tajuk yang berubah (bukan amplitudo dalam meter; urutan yang diuji).

| Jenis | flex | Piksel berubah, bawaan | Piksel berubah, `?pohon=lama` |
| --- | --- | --- | --- |
| aspen | 1,6 / 1,0 | 14,6% | - |
| elm | 1 / 0 | 9,1% | 9,1% |
| poplar | 1,4 / 0,6 | 6,7% | 5,7% |
| oak | 0,8 / 0 | 4,1% | 5,3% |
| fir | 0,35 / 0 | 2,1% | - |

Catatan 25g:
- Amplitudo goyang di puncak tajuk (tinggi >= 12 m dari dasar template): 5 cm x flex saat tenang, (5 + 20 x hembusan) cm x flex saat berangin; getar cepat 3,5 cm x getar x (0,4 + hembusan).
- Shader hanya menambah sin / cos dikali konstanta (tanpa normalize, pow, sqrt): tidak ada jalur NaN baru untuk M1. `tools/qc_load.py` tanpa error atau peringatan kompilasi.
- Elm (flex 1) sama persis di kedua mode, jadi jalur baru setara dengan lama untuk pengali 1. `?pohon=lama` geometri 0 beda, atribut `aFlex` tidak ditambahkan.
- Tambahan memori: 2 float per verteks daun, 8 byte x 101.800 verteks daun di 42 template = 0,78 MB (dihitung dari sidik jari geometri).
- Gerak nyata hanya bisa dinilai di GPU (sandbox menilai dua bingkai diam).

### Hasil terukur 25h (sandbox, di luar hutan 14a)

| Zona / distrik | Pohon | Jenis | Terbanyak sebelum 25h | Terbanyak sesudah 25h |
| --- | --- | --- | --- | --- |
| zona luar kota | 5.030 | 17 | poplar 39,4% | poplar 24,8% |
| zona kota | 10.452 | 9 | maple 22,2% | maple 22,2% (tidak berubah) |
| zona taman | 927 | 18 | maple 19,2% | maple 19,2% |
| zona tepi air | 377 | 19 -> 20 | willow 43,2% | willow 43,2% |
| Iowa | 1.369 | 18 | poplar 33,8% | poplar 17,8% |
| Pampas | 1.214 | 18 | poplar 34,4% | poplar 20,7% |
| Punjab | 826 | 16 -> 17 | poplar 43,5% | poplar 29,9% |
| Ukraina | 414 | 17 | poplar 43,0% | poplar 30,0% |
| di luar distrik | 1.282 | 17 | poplar 44,1% | poplar 30,0% |
| 14 distrik kota | 422-1.129 | 9-10 | 19,5-26,4% | sama |

Catatan 25h:
- Tepi air tetap didominasi willow (43%), sengaja: willow memang pohon tepi sungai; batas 30% dihitung per distrik, bukan per zona, dan tidak ada distrik yang melampauinya.
- Di luar distrik, poplar tepat 30% karena sebagian besar adalah barisan poplar halaman Cooper yang tidak boleh diganti.
- Zona kota tetap 9 jenis (maple, birch, elm, oak, basswood, ash, beech, honey locust, pohon bunga); konifer tidak masuk kota (K2).
- Uji: `tools/uji_pohon.py` menambah cek "jenis terbanyak per distrik <= 30%" (lolos, 21 cek), Campur 22,3%, Gugur 63,9%. `?pohon=lama` 0 beda. `tools/qc_load.py` tanpa error.

### Hasil terukur 25i (sandbox SwiftShader, 640 x 360 px)

Waktu muat sampai `__stationReady` (3 kali berurutan per mode):

| Mode | Muat (s) | Rata-rata (s) |
| --- | --- | --- |
| `?pohon=lama` (16 template) | 5,58 / 5,76 / 5,62 | 5,65 |
| bawaan (42 template) | 5,90 / 6,02 / 5,91 | 5,94 (+0,29 s, +5%) |

Satu bingkai setelah teleport (10 bingkai tunggu), `renderer.info` dijumlah untuk semua pass (bayangan, adegan, post). Diukur sebelum penghematan 25i (penghematan tidak mengubah jumlah ini; lihat catatan).

| Preset, lokasi | Draw call lama -> baru | Segitiga per bingkai (juta) | Pohon mesh penuh | Segitiga pohon mesh penuh (juta) |
| --- | --- | --- | --- | --- |
| Ultra, Cooper | 379 -> 405 | 4,89 -> 4,88 | 3 | 0,00 -> 0,00 |
| Ultra, hutan | 278 -> 464 | 6,54 -> 7,28 | 256 | 0,34 -> 0,50 |
| Ultra, bukit | 484 -> 758 | 6,73 -> 7,27 | 78 | 0,11 -> 0,16 |
| Ultra, New York | 677 -> 711 | 4,04 -> 4,06 | 21 | 0,03 -> 0,03 |
| Hemat, Cooper | 102 -> 128 | 1,64 -> 1,63 | 2 | 0,00 -> 0,00 |
| Hemat, hutan | 136 -> 168 | 2,05 -> 2,07 | 28 | 0,04 -> 0,05 |
| Hemat, bukit | 336 -> 380 | 2,34 -> 2,36 | 26 | 0,04 -> 0,05 |
| Hemat, New York | 292 -> 319 | 1,95 -> 1,95 | 5 | 0,01 -> 0,01 |

Memori GPU tambahan (dihitung dari ukuran tekstur; depth buffer dianggap 4 byte per piksel, tergantung driver):

| Bagian | 16 template (lama) | 42 template (baru) |
| --- | --- | --- |
| Impostor oktahedral Ultra, sebelum 25i (1.024 px + mipmap + depth per template) | 149,3 MB | 392,0 MB |
| Impostor oktahedral Ultra, sesudah 25i (tanpa depth per template + satu target bake bersama 8 MB) | 93,3 MB | 232,0 MB |
| Impostor 256 px semua preset (0,58 MB per template) | 9,3 MB | 24,5 MB |
| Atlas daun kedua (25c) | - | 10,7 MB |
| Tekstur kulit (25f) | - | sekitar 1,2 MB |
| Atribut `aFlex` (25g) | - | 0,78 MB |

Catatan 25i:
- Biaya terbesar 25b-25h adalah draw call di Ultra di hutan dan bukit (+67% dan +57%): tiap template punya mesh impostor sendiri yang memuat semua pohonnya (`frustumCulled` mati), jadi 26 template baru = 26 draw call impostor lagi per pass, ditambah kulit dan daun dekat konifer di pass adegan dan bayangan. Di Hemat tambahannya 26-44 draw call dan segitiga hampir tetap: preset Hemat dan Rendah tidak diubah.
- Penghematan (1) tidak mengurangi angka draw call di tabel (three.js 0.186.1 sudah tidak memanggil gambar untuk mesh 0 instance), tetapi melewati persiapan program, uniform, dan atribut di CPU untuk template tanpa pohon dekat di tiap pass. Tidak bisa diukur di SwiftShader.
- Penghematan (2) dicek di satu halaman dengan uTime dibekukan: cara lama dan cara salin identik byte per byte untuk oak, poplar, pine, aspen, ash, fir, arborvitae. Antar pemuatan halaman atlas tidak sama persis karena bake terjadi saat daun bergoyang (uTime berbeda); itu juga berlaku sebelum 25i.
- Bila FPS Ultra di GTX 1060 turun terasa di hutan atau bukit, langkah berikut yang paling efektif: satu mesh impostor untuk semua template (atlas array, tanpa mengubah tampilan), atau `frond.n` lebih kecil di luar Ultra. Belum dikerjakan; perlu angka FPS dari Bhakti dulu.
- FPS dan waktu GPU belum diukur (sandbox tanpa GPU). Alat ukur GPU di HUD lengkap (20a, `GPUT`) bisa dipakai di GTX 1060: baris sh / sc / po, banding dengan `?pohon=lama`.

Batasan 25a: FPS dan waktu muat belum diukur di GTX 1060 atau M1. Geometri pohon tidak berubah, jadi pohon tampil sama seperti sebelumnya; uji visual cukup memastikan tidak ada bagian lain yang ikut berubah.

### Hasil terukur 25k (sandbox)

Penyebab tajuk jarang sebelum 25k: daun hanya di separuh luar ranting terakhir (celah antar ranting terlihat), pita tangkai sempit dan setengah transparan, bentuk tajuk hanya hasil cabang acak (tanpa siluet per jenis).

| Jenis | Kelompok | Tinggi template (m) sebelum -> sesudah | Verteks daun sebelum -> sesudah |
| --- | --- | --- | --- |
| oak | oval | 9,4 -> 9,9 | 1.056 -> 1.092 |
| elm | vas | 15,3 -> 14,5 | 800 -> 1.188 |
| poplar | kolom | 19,8 -> 19,3 | 616 -> 1.680 |
| maple | oval | 8,2 -> 8,3 | 1.344 -> 1.048 |
| birch | oval | 18,5 -> 18,6 | 672 -> 1.680 |
| pine | kerucut | 15,1 -> 15,6 | 816 -> 1.680 |
| willow | juntai | 10,3 -> 12,0 | 1.920 -> 1.008 |
| pohon bunga | kubah | 6,4 -> 6,5 | 1.056 -> 920 |
| aspen | oval | 20,7 -> 13,9 | 648 -> 1.656 |
| beech | oval | 9,8 -> 13,7 | 1.568 -> 1.452 |
| basswood | oval | 13,4 -> 14,2 | 1.344 -> 1.576 |
| chestnut | oval | 8,4 -> 11,8 | 1.152 -> 1.008 |
| ash | oval | 13,7 -> 14,0 | 3.456 -> 1.164 |
| walnut | kubah | 7,5 -> 12,2 | 3.888 -> 920 |
| hickory | oval | 16,8 -> 15,2 | 3.456 -> 1.436 |
| black locust | oval | 10,2 -> 12,8 | 4.536 -> 924 |
| honey locust | payung | 8,2 -> 10,9 | 3.780 -> 680 |
| fir | kerucut | 17,3 -> 16,1 | 5.760 -> 1.680 |
| hemlock | kerucut | 15,0 -> 15,3 | 5.328 -> 1.680 |
| arborvitae | kolom | 9,5 -> 9,1 | 2.808 -> 1.364 |
| redcedar | kerucut | 11,8 -> 11,3 | 4.896 -> 1.512 |
| total 42 template | | | 101.800 -> 54.696 |

Catatan 25k:
- Tinggi template 8 jenis lama dijaga (H = rata-rata tinggi 2 template lama), jadi tinggi dunia, `KSCALE`, dan hutan tidak bergeser; jenis baru diskalakan lewat `hRel` seperti sebelumnya (tinggi template tidak menentukan tinggi dunia).
- `?pohon=lama` identik dengan sebelum 25a (0 beda). `tools/uji_pohon.py` 21 cek lolos (Campur 22,3%, Gugur 63,9%, distrik <= 30%), `tools/uji_hutan.py` lolos (5.222 pohon, 22-35 m), `tools/qc_load.py` tanpa error.
- Verteks daun total turun 46% karena gugus besar menggantikan pita tangkai; draw call tidak berubah (jumlah template sama).
- Render grid memakai cahaya bake (datar, lebih gelap dari dalam game) dan warna musim dinolkan; pohon bunga tampil merah muda di dalam game.
- Willow: kubah dengan untaian tegak di 55% bawah tajuk; belum sehalus willow referensi.
- Referensi adalah ilustrasi lukisan; 25k mengejar siluet dan kepadatannya, bukan gaya lukisan.
