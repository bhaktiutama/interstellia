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
| 25d-25j | Belum dikerjakan | - |

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

Batasan 25a: FPS dan waktu muat belum diukur di GTX 1060 atau M1. Geometri pohon tidak berubah, jadi pohon tampil sama seperti sebelumnya; uji visual cukup memastikan tidak ada bagian lain yang ikut berubah.
