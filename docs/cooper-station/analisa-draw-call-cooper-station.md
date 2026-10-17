# Analisa draw call Copper Corn Station

Tanggal ukur: 2026-10-17. Kode: `experiences/cooper-station/index.html` (commit 2477895 di `main`). Alat: `tools/ukur_draw_call.py`.

## 1. Ringkasan

- Draw call nyata per frame (angka HUD) di Ultra: 279 (Rumah Cooper), 345 (hutan), 480 (pasar), 642 (puncak bukit), 799 (pusat New York). Di Hemat: 128, 336, 369. Tiga pass bayangan menyumbang 35% sampai 60% di Ultra karena pohon dekat, rumah Cooper, dan trem digambar ulang sekali per pass.
- Pemborosan terbesar ada pada pembagian mesh, bukan pada geometri: 42 impostor pohon = 42 draw di setiap lokasi (31% dari 128 draw di Hemat Rumah Cooper); trem 74 draw per pass padahal hanya 1 kereta (8 daun pintu x 5 mesh kecil, selalu digambar walau tidak terlihat); pohon dekat 2 draw per template per pass (bukit: 79 pohon di 26 template, rata-rata 3 pohon per draw); jembatan 2 draw per jembatan; 7 bidang air Skyway yang selalu digambar; 54 jenis perabot kota tetap dikirim ke three.js walau kosong.
- Perkiraan setelah 8 perbaikan di bagian 4: draw call nyata turun 16% sampai 31% di Ultra dan 37% sampai 41% di Hemat (tabel 4.1), tanpa perubahan visual. Ini hitungan dari data ukur, belum diimplementasikan; dampak ke FPS di GTX 1060 dan M1 belum terukur.

## 2. Cara ukur

| Item | Isi |
| --- | --- |
| Alat | `python tools/ukur_draw_call.py --preset ultra 1 2 tp:nyc 0` (Chromium headless, SwiftShader) |
| Yang dicatat | tiap panggilan `renderBufferDirect`: pass (dari render target), jumlah instance, draw GL nyata (selisih `renderer.info.render.calls`, sama dengan HUD), jumlah panggilan GL, baris `index.html` tempat objek dibuat (three.core.js ditambal di jalan) |
| Terkirim vs nyata | Terkirim = mesh yang diproses three.js. Nyata = yang jadi draw GL. Selisihnya mesh dengan 0 instance: three.js tetap memasang program dan uniform, lalu `renderInstances` keluar karena `primcount === 0` |
| Frame | median dari 8 frame; bake impostor oktahedral (target 1024, 128 draw per frame selama 42 frame pertama Ultra) dikeluarkan karena sementara |
| Batas | Jumlah draw dan panggilan GL dapat dipercaya. Waktu (ms) di SwiftShader tidak mewakili GPU asli, jadi tidak dipakai sebagai dasar |

## 3. Hasil

### 3.1 Per lokasi

| Preset | Lokasi | Terkirim | Draw GL nyata | Kosong | Panggilan GL |
| --- | --- | --- | --- | --- | --- |
| Ultra | Rumah Cooper (1) | 442 | 279 | 163 | 2.184 |
| Ultra | Puncak bukit (2) | 804 | 642 | 162 | 4.097 |
| Ultra | Hutan lebat (0) | 512 | 345 | 167 | 2.617 |
| Ultra | Pasar New York | 611 | 480 | 131 | 2.860 |
| Ultra | Pusat New York | 838 | 799 | 39 | 4.136 |
| Hemat | Rumah Cooper (1) | 193 | 128 | 65 | 1.215 |
| Hemat | Puncak bukit (2) | 434 | 369 | 65 | 2.602 |
| Hemat | Pusat New York | 353 | 336 | 17 | 2.246 |

Rata-rata sekitar 7,8 panggilan GL per draw nyata (VAO, 2 sampai 3 matriks, tekstur, program). Hemat tidak punya pass bayangan.

### 3.2 Per kategori, Ultra (draw nyata: pass utama + 3 pass bayangan; k = mesh kosong terkirim)

| Kategori | Rumah Cooper | Puncak bukit | Hutan | Pasar NY | Pusat NY |
| --- | --- | --- | --- | --- | --- |
| Pohon dekat (kulit + daun) | 6 + 18 | 52 + 156 | 28 + 84 | 26 + 78 | 22 + 66 |
| Impostor pohon | 42 | 42 | 42 | 42 | 42 |
| Trem | - | 74 | - | 0 + 42 | 74 + 126 |
| Perabot kota (FURN, 54 jenis) | 0 (k147) | 0 (k147) | 0 (k147) | 14 + 30 (k103) | 51 + 84 (k12) |
| Rumah Cooper (16 bahan) | 16 + 39 | 16 + 13 | 16 | - | - |
| Grup gabungan (baseball, kabin, hub, menara lift) | - | 16 | - | 0 + 6 | 9 + 6 |
| Lobi menara lift (mesh tembus pandang) | - | 26 | - | - | 26 |
| Jembatan (jalan + badan beton) | - | 32 | - | 4 + 9 | - |
| Air akuaduk Skyway | 7 | 7 | 7 | 7 | 7 |
| Terminal dan dermaga kecil | 1 | 23 | 1 | 1 + 6 | 52 + 6 |
| Potongan tanah | 4 + 17 | 39 + 10 | 24 + 16 | 9 + 18 | 5 + 13 |
| Gedung + atap (SHP.stat) | 8 + 11 | 8 + 5 | 8 + 3 | 8 + 18 | 8 + 18 |
| Efek layar penuh | 19 | 19 | 19 | 19 | 19 |
| Pejalan kaki | 2 (k8) | 0 (k8) | 0 (k8) | 16 + 42 (k4) | 9 + 21 (k4) |
| Mobil | 2 + 1 | 2 | 2 | 5 + 10 | 14 + 39 |
| Lainnya | 47 + 39 | 63 + 39 | 59 + 36 | 41 + 29 | 48 + 34 |
| Total nyata | 154 + 125 | 419 + 223 | 206 + 139 | 192 + 288 | 386 + 413 |

### 3.3 Per kategori, Hemat (hanya pass utama)

| Kategori | Rumah Cooper | Puncak bukit | Pusat NY |
| --- | --- | --- | --- |
| Impostor pohon | 42 | 42 | 42 |
| Trem | - | 74 | 74 |
| Terminal dan dermaga kecil | 1 | 23 | 52 |
| Lobi menara lift | - | 26 | 26 |
| Jembatan | - | 32 | - |
| Rumah Cooper (16 bahan) | 16 | 16 | - |
| Grup gabungan | - | 16 | 9 |
| Pohon dekat | 4 | 26 | 8 |
| Potongan tanah | 4 | 39 | 5 |
| Air Skyway | 7 | 7 | 7 |
| Gedung, mobil, perabot, lainnya | 54 | 68 | 113 |
| Total nyata | 128 | 369 | 336 |

## 4. Temuan dan usulan

Label effort mengikuti `CLAUDE.md`. Penghematan = draw nyata per frame (angka HUD), dihitung dari data di bagian 3.

| No | Temuan (bukti) | Usulan | Hemat | Effort | Model | Thinking | Risiko |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | 54 jenis `FURN.kinds` (dan ember lain) dikirim ke three.js walau `count = 0`: 131 sampai 167 mesh kosong per frame di Ultra (65 di Hemat), tiap pass bayangan mengulang | `updateFurniture()` (L13246): `K.mesh.visible = c > 0`, pola sama dengan mobil dekat (`m.visible = c > 0`, L13110) dan pohon dekat (25i). Ember lain yang `count`-nya diatur sendiri diperlakukan sama | 0 draw nyata; 130 sampai 165 mesh kosong per frame tidak diproses (CPU) | Low | Sonnet 5.5 | low | sangat rendah |
| D2 | Trem 74 draw di pass utama dan 42 per pass bayangan. 8 daun pintu x 5 mesh (L5596 x32, L5668 x16 = 48 draw) tidak ikut gabung per bahan karena bergerak; `tramMesh.traverse(o => o.frustumCulled = false)` (L5686) sehingga digambar walau tidak terlihat (bukit, Hemat bukit: 74 draw) | (a) daun pintu: 4 daun sisi peron (bergerak) jadi satu `InstancedMesh` per bahan (3 draw) dengan matriks diisi di `updateTramVisual()`, 4 daun sisi lain digabung ke `staticG`; (b) culling trem: `tramMesh.visible` dari uji bola batas terhadap kamera | (a) 44 di pass utama, 30 per pass bayangan; (b) sisa 30 saat di luar pandang | Medium | Sonnet 5.5 | medium | rendah (uji `uji_rel_trem.py`, `uji_lalu_lintas.py`; animasi buka-tutup diperiksa pemilik) |
| D3 | Grup yang sudah digabung per bahan masih digambar sekali per bahan di tiap pass bayangan walau `depthMat` sama: rumah Cooper 13 draw x pass (spawn 39 di bayangan), grup baseball, kabin, hub, menara lift (L3772) | Setelah `mergeByMaterial`, satu mesh bayangan gabungan (layer 1 saja, hanya bagian peneduh) dan mesh per bahan hanya di layer 0 | spawn 36; bukit 12; New York dan pasar sekitar 8 | Medium | Sonnet 5.5 | medium | rendah-sedang (bagian `noShadow` tidak boleh ikut) |
| D4 | Pohon dekat dikirim per template ke tiap pass bayangan walau peta dekat (kotak 40 m) hanya memuat sebagian. Template dalam radius 130 m vs dalam 40 m: bukit 26 vs 9, hutan 14 vs 11, New York 11 vs 4, pasar 13 vs 0 | Simpan batas (s, za) pohon dekat per template di `updateTreeLOD()`; di `shpBegin(pass)` sembunyikan template yang batasnya di luar kotak pass (+ margin 16 m seperti `SHP.margin`), pulihkan di `shpEnd()` | bukit 34; hutan 6; New York 14; pasar 26 | Medium | Sonnet 5.5 | medium | rendah |
| D5 | 42 impostor = 42 draw di setiap lokasi dan preset. Tiap template satu `InstancedMesh` dengan tekstur sendiri | Satu `InstancedMesh` impostor dengan atribut `aTpl` dan tekstur array 2D (`WebGLArrayRenderTarget` 256 x 256 x 42; oktahedral 1024 x 1024 x 42, memori sama dengan 42 target sekarang); `uSize`, `uLeafSp`, `uOct` jadi array uniform. Bukan atlas biasa: mip bocor antar sel | 41 di semua lokasi dan preset | High | Opus 5.5 | high | sedang (ubah `IMP_VS`, `IMP_FS`, `OCT_VS`, `OCT_FS`, `octBake`; uji M1 untuk NaN; mip array dibuat sekali di akhir bake) |
| D6 | Jembatan: 2 draw per jembatan (jalan `roadMat` L8268, badan beton instance L8305), 16 jembatan terlihat dari bukit = 32 draw | Gabung semua jembatan menjadi satu mesh jalan dan satu `InstancedMesh` beton (segitiga per jembatan kecil, hilangnya culling per jembatan tidak berarti) | bukit 30; pasar 11 | Low | Sonnet 5.5 | low | rendah (kolider tidak berubah) |
| D7 | Air akuaduk Skyway: 7 `Mesh` bidang terpisah, `frustumCulled = false` (L3634); 7 draw di setiap lokasi walau di luar pandangan (terbukti di Rumah Cooper) | Satu `InstancedMesh` (7 matriks) dengan culling normal; tekstur alir `SKYX.flow` tetap | 7 di semua lokasi dan preset | Low | Sonnet 5.5 | low | sangat rendah |
| D8 | Mesh kecil yang tidak ikut `mergeByMaterial` / `enableCull`: lobi menara lift (L3156 x12, L3183 x14, bahan tembus pandang yang dilewati karena `transparent`), bangku dan papan terminal (L13620 x8, L13634 x4), lampu dan strobo wahana (L13361, L13389) | Gabung per bahan termasuk bahan tembus pandang yang sama (kaca lobi, tidak saling tumpang), lalu `enableCull(G, pad)` (pola 20b) | bukit 30; New York 35 (Hemat sama) | Low | Sonnet 5.5 | low | rendah-sedang (urutan gambar kaca tembus pandang) |

### 4.1 Perkiraan hasil (draw nyata per frame)

| Preset | Lokasi | Sekarang | Perkiraan setelah D2-D8 | Turun |
| --- | --- | --- | --- | --- |
| Ultra | Rumah Cooper | 279 | sekitar 195 (D3 36, D5 41, D7 7) | 30% |
| Ultra | Puncak bukit | 642 | sekitar 445 (D2 44, D3 12, D4 34, D5 41, D6 30, D7 7, D8 30) | 31% |
| Ultra | Hutan lebat | 345 | sekitar 290 (D4 6, D5 41, D7 7) | 16% |
| Ultra | Pasar New York | 480 | sekitar 357 (D2 30, D3 8, D4 26, D5 41, D6 11, D7 7) | 26% |
| Ultra | Pusat New York | 799 | sekitar 559 (D2 135, D3 8, D4 14, D5 41, D7 7, D8 35) | 30% |
| Hemat | Rumah Cooper | 128 | sekitar 80 (D5 41, D7 7) | 37% |
| Hemat | Puncak bukit | 369 | sekitar 217 (D2 44, D5 41, D6 30, D7 7, D8 30) | 41% |
| Hemat | Pusat New York | 336 | sekitar 209 (D2 44, D5 41, D7 7, D8 35) | 38% |

Ini hitungan, bukan hasil implementasi. D2 di bukit dihitung konservatif (trem terlihat, 44 draw dihemat); bila trem di luar pandangan, culling menghemat 74.

### 4.2 Urutan pengerjaan yang disarankan

| Langkah | Isi | Alasan |
| --- | --- | --- |
| 1 | D1, D7, D8 | Effort Low, hampir tanpa risiko visual, dapat diverifikasi dengan `ukur_draw_call.py` |
| 2 | D6, D2 | Gabungan statis dan pintu trem; uji trem dan lalu lintas yang sudah ada |
| 3 | D3, D4 | Menyentuh pass bayangan (`shpBegin` / `shpEnd`); bandingkan gambar bayangan sebelum dan sesudah di 3 lokasi |
| 4 | D5 | Satu sesi tersendiri, menyentuh shader dan memori; uji pemilik di M1 sebelum digabung |

Setiap langkah: `tools/ukur_draw_call.py` sebelum dan sesudah, `tools/qc_load.py`, uji yang relevan (`uji_pohon.py`, `uji_rel_trem.py`, `uji_lalu_lintas.py`, `uji_orang.py`), lalu uji visual pemilik di GTX 1060 dan M1 (HUD: draw call, ms GPU).

### 4.3 Yang tidak disarankan (menurunkan kualitas)

| Opsi | Alasan ditolak |
| --- | --- |
| Memperbarui peta bayangan sunline tiap 2 frame | Bayangan mobil, orang, dan daun tertinggal 1 frame |
| Mengurangi tingkat bloom atau pass GTAO | 19 draw layar penuh murah di draw call; biayanya di GPU, bukan sasaran draw call |
| Satu peta bayangan dekat dan jauh digabung | Menghilangkan bayangan tajam 2 cm di dekat pemain (revisi V1) |
| Atlas biasa untuk impostor | Mip bocor antar sel, pohon jauh berwarna salah |

### 4.4 Sudah diperiksa dan bukan masalah

| Item | Hasil |
| --- | --- |
| Penelusuran graf scene (7 render per frame) | 726 objek, `traverseVisible` 0,02 sampai 0,05 ms; tidak perlu dioptimalkan |
| Pergantian program di pass bayangan | Material override `depthMat` hanya 2 sampai 3 program |
| Bake impostor oktahedral (128 draw per frame) | Sementara, 42 frame pertama Ultra; bukan kondisi tetap |
| Potongan tanah (4 sampai 49 draw) | Culling per potongan sudah aktif |
| Efek layar penuh (19 draw) | Setiap pass dipakai; biayanya di GPU |

## 5. Batas dan ketidakpastian

- Ukuran dilakukan di SwiftShader (CPU), 640 x 360 piksel. Jumlah draw, mesh kosong, dan panggilan GL deterministik; waktu dan FPS tidak. Dugaan bahwa pengiriman draw (CPU) menjadi penghambat di GTX 1060 dan M1 belum terbukti: hanya jumlahnya yang terukur, bukan waktunya.
- Angka penghematan D2 sampai D8 dihitung dari lokasi yang diukur (5 Ultra, 3 Hemat). Lokasi lain (ladang, Skyway, dermaga) tidak diukur. Posisi trem saat ukur memengaruhi angka D2.
- Uji "mesh `frustumCulled = false` yang berada di luar kerucut pandang" hanya meyakinkan untuk air Skyway; untuk mesh instance hasilnya tidak andal (bola batas instance kosong), jadi D2(b) dan temuan serupa perlu diverifikasi saat implementasi.
- Penggabungan bahan tembus pandang (D8) dan bayangan gabungan (D3) dapat mengubah tampilan sedikit bila tidak dicek; keduanya ditandai risiko rendah-sedang.
- Tidak ada perubahan kode game dalam tugas ini; hanya alat ukur dan dokumen ini.
