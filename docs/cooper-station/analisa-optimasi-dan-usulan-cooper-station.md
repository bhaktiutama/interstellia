# Analisa optimasi dan usulan pengembangan Copper Corn Station

Per 28 September 2026 · sebelum mulai Millar's World · sumber: `experiences/cooper-station/index.html` (11.297 baris, 797 KB) dibaca seluruhnya, ditambah pengukuran di Chromium headless (cara ukur di bagian 8)

## Ringkasan

- **Banyak yang bisa dioptimasi tanpa mengubah visual.** Di titik spawn siang (Ultra) satu frame mengirim 6,36 juta segitiga dan 1.114 draw call. Sekitar 70% draw call (784) berasal dari 6 grup kecil yang tidak digabung dan tidak di-cull (lapangan baseball saja 445 call untuk 2.528 segitiga), jagung dekat dan tengah menyumbang 1,37 juta segitiga (21%) padahal tidak ada jagung di kota, dan dua pass bayangan memakan 45% segitiga karena menggambar objek seluruh stasiun.
- **Waktu muat 6,2-6,6 s terukur**, sekitar 60% di dua bagian: peta tinggi tanah (2,3-2,7 s) dan bagian kota (1,4 s, 70% di antaranya satu baca-balik kanvas lahan 21 MB). Keduanya bisa dipercepat dengan hasil identik. Saat bermain ada baca-balik piksel sinkron tiap 0,4 s (hujan) yang terukur menunggu GPU menyelesaikan satu frame penuh.
- **Enhancement prioritas**: alat ukur GPU per pass di HUD (supaya optimasi diukur di GTX 1060 dan M1), mode efek layar ringan untuk Hemat (warna sama dengan Ultra), simpan sesi, impostor pohon multi-sudut. Sebelum Millar's World: pindahkan post-processing, bahasa, layar muat, preset, dan audio ke `shared/` sebagai script klasik (modul ES tidak jalan dari file://).

## 1. Optimasi tanpa mengubah visual (urut prioritas)

Semua butir di tabel ini menghasilkan gambar yang sama; yang berubah hanya jumlah kerja CPU/GPU. "Perkiraan" = hasil hitung dari data, belum diukur setelah diubah.

| No | Temuan (data) | Usulan | Hasil (perkiraan) | Beban |
| --- | --- | --- | --- | --- |
| O1 | 6 grup kecil menyumbang 784 dari 1.114 draw call per frame di spawn: lapangan baseball 445 (173 mesh, `frustumCulled = false`, ikut 2 pass bayangan walau 900 m lebih dari pemain), trem 158, kabin lift 56, menara lift 51, rumah Cooper 42, hub nol-g 32 | Gabung bagian statis per material (cara yang sudah dipakai rumah Cooper dan trem), hitung bounding sphere lalu nyalakan frustum culling. Kamera bayangan otomatis membuang grup di luar kotak bayangannya | 600-750 draw call lebih sedikit per frame di spawn. Hemat CPU (three.js + driver) paling terasa di M1 | rendah |
| O2 | `CORN.near` (386.715 segitiga) dan `CORN.mid` (69.908) digambar di 3 pass di semua lokasi uji, termasuk kota. Jumlah instance tetap; tanaman yang bukan di ladang jagung baru dibuang di vertex shader (`isCorn`) | Seperti `MEADOW.active`: `instanceCount = 0` bila tidak ada petak `f.corn` dalam radius `cornMid + 20 m` (cek CPU tiap 1 s atau tiap pindah 20 m) | -1,37 juta segitiga per frame (21%) di kota (di titik hutan uji ada petak jagung dalam 110 m, jadi tetap aktif) | rendah |
| O3 | Pass bayangan hanya meliput 640 x 640 m (cincin cap) dan 300 x 300 m (sunline), tetapi menggambar semua instance stasiun: mobil 248.760, peralatan atap 175.260, gedung sekitar 300 ribu segitiga per pass. Total kedua pass 2,86 juta segitiga dan 563 draw call | (a) Pecah InstancedMesh besar (gedung, peralatan atap, tiang lampu, perabot, props) per sektor (mis. 26 kolom arteri x 4 pita za) supaya frustum culling jalan; beri margin karena shader bayangan membuka silinder (`shUnroll`). (b) Mobil: kirim hanya mobil dalam radius 900 m ke buffer instance (cara `updatePeds`) | Pass bayangan turun dari 2,86 juta ke kurang dari 1 juta segitiga. Pass utama juga turun (sektor di belakang kamera dibuang) | sedang |
| O4 | Rumput: bulir (`aHead`) rumput biasa dan kedelai dikempiskan ke satu titik, tetapi tetap menjalankan seluruh `GRASS_VS` (tinggi tanah 4 texelFetch, `vegLight` dengan 7 sampel bayangan). Bulir = 53% vertex rumput dekat (56 dari 105) dan 62% rumput jauh (32 dari 52) | `if (aHead > 0.5 && !headOn) { CLIP_AWAY }` sebelum `groundFrame` | Kerja vertex rumput biasa turun 53% (dekat) dan 62% (jauh). Di kota: `grass.near` 281.547 + `grass.far` 432.012 segitiga | sangat rendah |
| O5 | Shader gedung (`BUILD_FS`) menghitung `farEnv` (pantulan, 2-3 baca tekstur, atan, exp) di setiap piksel dinding dan atap, padahal hanya dipakai kaca dan ruangan maya. Muka bawah (`n.y < -0.9`) keluar setelah semua cahaya dihitung | Hitung `sky` hanya bila `max(winM, shopM) > 0`; pindah early-out muka bawah ke awal | GPU: pantulan hanya di piksel kaca (tidak bisa diukur di sandbox) | rendah |
| O6 | `patchLit` menghitung normal instance dengan `transpose(inverse(mat3(instanceMatrix)))` per vertex. Semua matriks instance di kode = rotasi x skala (tanpa shear) | Pakai cara `BUILD_VS`: `mat3(instanceMatrix) * (normal / (s * s))`, s = panjang kolom. Hasil matematis sama | Lebih murah untuk tiang lampu (4.228 x 108 vertex), peralatan atap (14.605 x 24), props, rangka lift | rendah |
| O7 | Baca-balik piksel sinkron saat bermain: `updateRain` memanggil `getImageData` kanvas awan tiap 0,4 s (terukur menunggu 4,8-5,4 s di sandbox = satu frame GPU penuh, tanda CPU menunggu GPU). `startAudio` membaca kanvas lahan 2048 x 2608 penuh saat tombol Mulai. `updateAdaptLabel` memakai `readRenderTargetPixels` tiap 0,25 s saat panel terbuka | Tutupan awan di posisi pemain dihitung di CPU dari `CLOUD.groups` (rumus gumpalan yang sama dengan `drawShadow`); data lahan dibaca sekali saat muat dan dipakai bersama `FAR.land` dan langkah kaki; `readRenderTargetPixelsAsync` untuk label adaptasi | Jeda periodik hilang. Besaran jeda di GPU asli belum diukur (lihat bagian 9) | rendah |
| O8 | Muat, peta tinggi tanah 2,3-2,7 s. Rinci: pijakan rata bangunan 513-579 ms (sebagian besar untuk sekitar 2.900 modul utilitas di za 6.400-6.900, padahal di pita itu tanah dipaksa 0), loop zona rata 882-964 ms (per sampel: 2 `wrapS`, `riverZ` 2 sinus, 3 danau, 2 konversi half float), konversi half float kedua untuk tekstur (3,1 juta nilai) | Lewati bangunan yang seluruh jangkauan pijakannya ada di baris ber-amplitudo 0; faktor per kolom (boulevard, Skyway, `riverZ`) dihitung sekali per kolom; simpan nilai half float dari loop untuk `heightTex`; keluarkan fungsi hash dari `vnoise` (closure per panggilan). Semua identik | 2,3-2,7 s menjadi sekitar 1 s | rendah |
| O9 | Muat, penempatan pohon 570 ms: `ok()` di hutan kecil bukit memindai seluruh bangunan za > 2.550 (ribuan, termasuk modul utilitas) dan `fieldList.find` (886 petak) untuk setiap kandidat | Grid spasial untuk bangunan dan petak (predikat sama) | 570 ms menjadi sekitar 150 ms | rendah |
| O10 | Muat, `FAR.land` membaca kanvas lahan penuh (`getImageData` 2048 x 2608): 957-981 ms, 70% dari bagian "Kota, sungai, ladang" | Buat konteks kanvas lahan dengan `willReadFrequently: true` (raster di CPU, baca-balik murah), satu salinan data dipakai `FAR.land` dan `surfaceAt`. Perlu satu cek visual cepat tekstur tanah karena jalur raster berganti | Hampir 1 s lebih cepat di sandbox (di GPU asli kemungkinan lebih kecil) + tidak ada jeda saat Mulai | rendah |
| O11 | Kode GLSL ganda: `lampPool` = `lampPoolL`, `tramPool` = `tramPoolL` (komentar "ubah keduanya bersama") | Shader tanah memakai versi `...L` dari `LIGHT_GLSL` | Identik; risiko salah edit hilang | sangat rendah |
| O12 | Kamera luar (`updateExteriorCamera`) dan kendaraan perawatan (`updateCrawlers`) memakai dt tetap 1/60: di 30 FPS orbit 2x lebih lambat, di 144 Hz 2,4x lebih cepat | Pakai dt frame nyata | Kecepatan sama di semua FPS (koreksi bug kecil) | sangat rendah |
| O13 | CPU kecil lain: `CLOUD.drawShadow` 1,68 ms + unggah 2 tekstur kanvas (512 x 1.024 RGBA, 2 MB masing-masing) tiap 1,5 s; closure per mobil per langkah di `stepTraffic`; `FARM.dust.filter` dan `arr.set([...])` tiap frame; peta M digambar ulang tiap frame walau diam | Peta awan dirender di GPU (render target); hapus alokasi per frame; peta digambar ulang hanya saat berubah | Kecil (di bawah 1 ms per frame) | rendah |

Urutan kerja yang disarankan: O2, O4, O11, O12 (satu sesi), lalu O1, O5, O6, O7, lalu O8-O10 (muat), terakhir O3 (paling besar tapi paling banyak menyentuh kode).

## 2. Optimasi dengan sedikit kompromi visual (opsional, perlu keputusan Bhakti)

| Usulan | Dampak visual | Hasil |
| --- | --- | --- |
| LOD jarak peralatan atap (kotak 1,5-4 m) dan tiang lampu di pass utama, misalnya di atas 800 m | Kotak 2 m di 800 m sekitar 2 piksel di 1080p: bintik atap sedikit berkurang | -175 ribu dan -152 ribu segitiga di pass utama |
| Pejalan kaki jauh (di atas 80 m) memakai model 3 kotak | Siluet sama, lengan dan kaki tidak berayun dari jauh | Vertex per orang dari 408 menjadi sekitar 72 |
| Mesh tanah 16 m untuk potongan di atas 1,5 km | Kontur bukit seberang sedikit lebih kasar | Sebagian dari 942.368 segitiga tanah |
| Bayangan cincin cap diperbarui tiap 2 frame | Bayangan mobil dan orang dari cahaya cap tertinggal 1 frame | -1 pass bayangan per 2 frame |

## 3. Data pendukung

### 3.1 Segitiga dan draw call per frame (Ultra, 5 lokasi)

| Lokasi | Pass utama | Bayangan cincin cap | Bayangan sunline | Total |
| --- | --- | --- | --- | --- |
| Spawn kota, 11.00 | 3.507.992 tri / 531 call | 1.444.127 / 287 | 1.411.335 / 276 | 6.363.488 tri / 1.114 call |
| Spawn kota, 22.00 | 3.467.648 / 528 | tidak ada | tidak ada | 3.467.682 / 548 |
| Puncak bukit, 11.00 | 4.188.284 / 517 | 1.508.215 / 264 | 1.440.399 / 260 | 7.136.932 / 1.060 |
| Hutan lebat, 11.00 | 3.226.953 / 473 | 1.901.611 / 269 | 1.707.179 / 261 | 6.835.777 / 1.023 |
| Ladang jagung, 11.00 | 2.499.128 / 439 | 1.443.903 / 256 | 1.360.211 / 251 | 5.303.276 / 966 |

Kolom Total juga memuat 17 pass layar penuh (34 segitiga) dan 2-3 draw call scene jauh (Saturnus, bintang). Pass bayangan mati di malam hari (cahaya di bawah ambang 0,15).

### 3.2 Objek terbesar per pass (spawn kota, 11.00)

| Objek | Segitiga per pass | Pass | Catatan |
| --- | --- | --- | --- |
| Mesh tanah (58 potongan) | 937.664 | utama | Dari dalam silinder hampir seluruh tanah terlihat |
| `grass.far` | 432.012 | utama | 62% vertex = bulir kempis (O4) |
| `corn.near` | 386.715 | 3 pass | Tidak ada jagung di kota (O2) |
| `grass.near` | 281.547 | utama | 53% vertex = bulir kempis (O4) |
| Mobil (3.455 unit x 72) | 248.760 | 3 pass | Di atas 900 m dibuang di vertex shader (O3b) |
| Peralatan atap (14.605 kotak) | 175.260 | 3 pass | Seluruh stasiun (O3a) |
| Tiang lampu jalan (4.228) | 152.208 | utama | Tanpa bayangan |
| Kotak instance lain (8 InstancedMesh) | 98.064 | utama | Rangka lift, jari-jari end cap, rel dan peron, jembatan Skyway, dan lain-lain |
| Gedung `flat` / `hip` / `silo` / `gable` / `gablez` | 80.370 / 63.658 / 58.272 / 54.544 / 45.822 | 3 pass | 20.995 gedung seluruh stasiun (O3a) |
| `corn.mid` | 69.908 | 3 pass | (O2) |
| Mesh gabungan terbesar (masjid, fasilitas, atau lapak pasar) | 50.216 | utama | Sudah satu mesh |

Di puncak bukit bertambah `meadow.mid` 724.545 dan `meadow.near` 360.255 segitiga (rumput tinggi, sudah dimatikan otomatis bila jauh dari bukit).

### 3.3 Draw call grup kecil (spawn kota, 11.00)

| Grup | Pass utama | Bayangan cap | Bayangan sunline | Jumlah | Segitiga (utama) |
| --- | --- | --- | --- | --- | --- |
| Lapangan baseball | 173 | 136 | 136 | 445 | 2.528 |
| Trem | 74 | 42 | 42 | 158 | 2.924 |
| Kabin lift | 28 | 14 | 14 | 56 | 336 |
| Menara lift | 27 | 12 | 12 | 51 | 11.718 |
| Rumah Cooper | 16 | 13 | 13 | 42 | 5.488 |
| Hub nol-g | 32 | 0 | 0 | 32 | 10.448 |
| Total | 350 | 217 | 217 | 784 | 33.442 |

### 3.4 Waktu muat (2 run, container ini)

| Bagian | Run 1 | Run 2 | Isi terberat |
| --- | --- | --- | --- |
| Total sampai "Siap" | 6.573 ms | 6.247 ms | |
| Peta tinggi tanah | 2.685 ms | 2.317 ms | pijakan rata 579 / 513 ms, loop zona rata 964 / 882 ms, konversi half float dan lapak pasar sekitar 0,6-0,8 s |
| Kota, sungai, ladang | 1.362 ms | 1.402 ms | `getImageData` kanvas lahan (`FAR.land`) 957 / 981 ms, isi blok kota 172 / 154 ms |
| Pohon | 966 ms | 966 ms | templat dan penempatan 570 / 574 ms, peta bayangan tajuk 279 / 308 ms |
| Jalan dan lalu lintas | 352 ms | 335 ms | simulasi awal 30 s mobil |
| Pejalan kaki | 272 ms | 300 ms | 13.094 orang, simulasi awal 20 s |
| Mesh tanah | 260 ms | 277 ms | 942.368 segitiga |
| Mesin ladang (termasuk aset motor) | 159 ms | 160 ms | |

Run pertama sebelum cache hangat: 8.583 ms.

### 3.5 CPU per frame di 60 Hz (rata-rata 240 panggilan, dt 1/60 s)

| Fungsi | ms per frame |
| --- | --- |
| `stepTraffic` (3.455 mobil, IDM) | 0,634 |
| `stepPeds` (11.641 pejalan, jauh bergiliran 1 dari 10) | 0,520 |
| `stepBirds` + `updateBirds` | 0,155 |
| `updateClouds` | 0,094 |
| `updatePeds` (212 orang digambar di spawn) | 0,062 |
| `updateFurniture`, `physicsStep` x2, `updateCamera`, `updateLighting` | masing-masing di bawah 0,02 |
| `CLOUD.drawShadow` (tiap 1,5 s) | 1,675 per panggilan |

Simulasi total sekitar 1,5 ms per frame: CPU simulasi bukan hambatan. Yang berat adalah jumlah draw call (bagian 3.3) dan kerja GPU (bagian 3.1).

### 3.6 Ukuran dunia

| Item | Jumlah |
| --- | --- |
| Mesh di scene / tanpa frustum culling | 632 / 456 |
| InstancedMesh / total instance aktif | 99 / 73.225 |
| Material / program shader | 252 / 162 |
| Gedung / kotak peralatan atap | 20.995 / 14.605 |
| Pohon / collider / petak ladang | 22.008 / 44.685 / 886 |
| Mobil / pejalan kaki | 3.455 / 13.094 |
| Heap JavaScript setelah muat | 188 MB |

## 4. Usulan enhancement fungsi

| Usulan | Isi | Beban |
| --- | --- | --- |
| Alat ukur GPU (prioritas) | `EXT_disjoint_timer_query_webgl2`: ms GPU per pass (utama, 2 bayangan, SSAO, bloom, sunrays) di HUD lengkap. Dasar ukur sebelum dan sesudah optimasi di GTX 1060 dan M1 | rendah |
| Simpan sesi | Posisi, jam, cuaca, motor yang diparkir, preset; tombol "Lanjutkan" di layar mulai | rendah |
| Tantangan fisika | Misi singkat: kenai sasaran dengan lemparan Coriolis, jatuhkan bola dari dek ke lingkaran, tebak titik jatuh hujan. Skor dan penjelasan | sedang |
| Kompas dan minimap di HUD | Arah sumbu, arah putaran, distrik, halte terdekat | rendah |
| Stik game | Gamepad API untuk jalan dan motor (sudah diusulkan di tahap 19) | rendah |
| Sepeda | Pakai kerangka motor, bisa masuk jalan setapak taman dan hutan (tahap 19) | rendah |
| Foto resolusi tinggi | Render 2x lalu simpan PNG, dan time-lapse jam stasiun | sedang |
| Pengaturan kendali | Sensitivitas mouse, balik sumbu Y, slider FOV | rendah |
| Tur diperbarui | Titik tur untuk motor (berat terasa), dek menara (lempar bola), gerhana | rendah |
| Kabin masinis trem | Dari usulan tahap 19 | sedang |

## 5. Usulan enhancement visual

| Usulan | Isi | Beban |
| --- | --- | --- |
| Efek layar "Ringan" untuk Hemat dan Rendah (prioritas) | Sekarang Hemat dan Rendah mematikan post sama sekali, jadi tanpa tone mapping ACES dan bloom: warna berbeda dari Ultra. Mode ringan: HDR + eksposur + ACES + bloom 3 tingkat, tanpa SSAO, sunrays, FXAA, adaptasi | rendah |
| Bayangan kontak murah untuk Hemat | Bayangan bawah mobil, orang, dan pohon (cakram gelap) saat peta bayangan mati | rendah |
| Impostor pohon multi-sudut | 8 arah (atau oktahedral) dipanggang saat muat, supaya pohon jauh tidak tampak seperti kartu yang ikut berputar | sedang |
| Payung saat hujan | Sebagian pejalan kaki membuka payung, sebagian berteduh di halte dan kafe | rendah |
| Neon dan papan iklan orisinal di megacity | Malam di New York, Tokyo, Shanghai lebih hidup; lampu toko mengikuti jam | sedang |
| Awan bertepi terang | Hamburan tepi (silver lining) dari sunline dan lapisan awan kedua | sedang |
| Pantulan air dekat | Pantulan gedung dan pohon di sungai dan danau di dekat pemain (pass tambahan kecil, Ultra saja) | tinggi |
| Variasi kendaraan | Bus, truk, van di lalu lintas | sedang |
| Bayangan diri dan spion | Dari usulan tahap 19 | rendah / sedang |

## 6. Persiapan sebelum Millar's World

| Langkah | Isi | Alasan |
| --- | --- | --- |
| Pindahkan ke `shared/` | Bahasa (`t`, `setLang`, `translateDom`), layar muat dan pilihan preset, post-processing (HDR, bloom, ACES, FXAA, adaptasi mata), mesin audio sintesis, alat ukur GPU | Dipakai ulang Millar's World dan Penerbangan Kestrel; sesuai aturan "dipindah bertahap" |
| Bentuk file `shared/` | Script klasik (`<script src="../../shared/post.js">`) yang mendaftar ke satu objek global, misalnya `window.LZ`. Three.js tetap dari importmap | `import` modul ES lokal diblokir browser saat halaman dibuka dari file:// (origin null); script klasik tetap jalan |
| Laut untuk Millar's World | Gelombang Gerstner atau FFT di GPU, busa, pantulan langit, gelombang raksasa dengan kurva tinggi analitik; preset Hemat dirancang sejak awal (laut penuh layar = beban fragment besar) | Pelajaran dari Cooper: biaya terbesar ada di shader layar penuh |
| Lubang hitam di langit | Pakai ulang shader experience Gargantua sebagai latar langit | Konsistensi antar experience |
| Dilatasi waktu | Faktor dihitung dari massa dan spin lubang hitam serta orbit planet (bukan angka dari film); jam ganda di HUD: waktu planet dan waktu stasiun | Tema fisika aplikasi |
| Shuttle Kestrel | Model dan fisika terbang (`SHIPS`, `PORT`, panduan sandar) dipindah ke `shared/` untuk Penerbangan Kestrel dan pendaratan di Millar's World | Kode sudah ada dan teruji |
| Selesaikan O1, O2, O4 dulu | Tiga optimasi termurah, hasil identik | Performa Cooper tetap jadi acuan saat pindah experience |

## 7. Usulan tahap 20

| Sub-tahap | Isi | Uji |
| --- | --- | --- |
| 20a | O2, O4, O11, O12 + alat ukur GPU | segitiga dan draw call sebelum/sesudah (skrip profil), `tools/qc_load.py`, uji lama |
| 20b | O1, O5, O6, O7 | idem + cek visual Bhakti |
| 20c | O8, O9, O10 (muat) | waktu muat, `TER.h` dan `heightTex` sama persis (checksum) |
| 20d | O3 (sektor instance) | pass bayangan, `tools/uji_cahaya_lanjut.py` |
| 20e | Efek layar Ringan, simpan sesi, lalu `shared/` | uji semua experience dari file:// |

## 7b. Hasil tahap 20a (29 September 2026)

Dikerjakan: O2, O4, O11, O12, alat ukur GPU, ditambah satu bug yang ditemukan saat mengerjakan O11.

| Butir | Hasil |
| --- | --- |
| O2 jagung | Spawn kota siang: 6.363.488 menjadi 4.993.749 segitiga per frame (-21,5%); draw call 1.114 menjadi 1.108. Bukit, hutan, ladang jagung: tidak berubah (ada petak jagung dalam jangkauan) |
| O4 bulir rumput | Jumlah segitiga yang dikirim sama (dihitung dari indeks), kerja vertex shader bulir yang tidak dipakai hilang (53% vertex rumput dekat, 62% rumput jauh) |
| O11 | `lampPool` / `tramPool` di shader tanah dihapus, memakai `lampPoolL` / `tramPoolL` |
| Bug 17e | `THREE.UniformsUtils.merge` menyalin `uTram`, jadi `uL_Tram` tidak pernah diperbarui dan trem malam tidak pernah menerangi objek (hanya tanah). Kini satu objek uniform bersama: dinding, pohon, orang di dekat trem ikut terang di malam hari seperti rencana 17e. Material trem sendiri dikecualikan (`userData.noTramLight`, define `NO_TRAM_LIGHT`), jadi tampilan trem sama seperti sebelumnya |
| O12 | Kamera luar dan kendaraan perawatan memakai dt nyata: yaw orbit otomatis 2 s = 0,07 rad di 30, 60, dan 144 FPS (dulu bergantung FPS) |
| Uji | `qc_load` tanpa error; `uji_bahasa`, `uji_rumput_bukit`, `uji_trem_malam`, `uji_hujan`, `uji_hutan`, `uji_ladang_foto_tur`, `uji_spaceport`, `uji_cahaya_lanjut` semua OK |
| Alat ukur GPU | Baris HUD lengkap: GPU total, bayangan, scene, post (ms, dihaluskan). Aktif hanya saat HUD lengkap. Didukung juga di SwiftShader (angkanya waktu render perangkat lunak, tidak bermakna); di GTX 1060 dan M1 menunjukkan ms nyata |

## 7c. Hasil tahap 20b (29 September 2026)

Dikerjakan: O1, O5, O6, O7.

| Butir | Hasil |
| --- | --- |
| O1 grup kecil | `mergeByMaterial()` menggabung lapangan baseball, kabin lift, hub, lobi menara lift per material; `enableCull()` menyalakan frustum culling untuk keenam grup (juga rumah Cooper dan trem) dengan bola batas +120 m (aman untuk pergeseran koordinat silinder terbuka di pass bayangan) |
| Draw call per frame (Ultra, 11.00) | Spawn kota: 1.108 menjadi 505 (-54%). Lapangan baseball: 1.001 menjadi 251 (-75%) |
| Segitiga per frame | Spawn kota: 4.994.638 menjadi 4.963.667; lapangan baseball: 4.191.023 menjadi 4.151.927 (objek di luar pandangan dibuang) |
| O5 shader gedung | Pantulan `farEnv` hanya di piksel kaca, muka bawah keluar sebelum cahaya |
| O6 normal instance | `inverse()` per vertex diganti rumus rotasi x skala (hasil sama) |
| O7 baca-balik | Tutupan awan untuk suara hujan dari `cloudCoverAt()` (selisih dengan piksel kanvas rata-rata 0,0004, maksimum 0,0101, 0,007 ms per panggilan); data lahan dibaca sekali saat muat (`FAR.landData`) dan dipakai langkah kaki dan motor, tidak dibaca ulang saat tombol Mulai; label adaptasi mata membaca asinkron |
| Uji | `qc_load` tanpa error; `uji_cahaya_lanjut`, `uji_spaceport`, `uji_hujan`, `uji_trem_malam`, `uji_gerak`, `uji_suasana`, `uji_bahasa`, `uji_ladang_foto_tur`, `uji_pantulan`, `uji_interior` OK. `uji_menara`: 2 butir gagal ("bola belum mendarat" dalam 30 s waktu nyata). Uji itu bergantung kecepatan frame SwiftShader: di dek, waktu simulasi hanya maju 0,031-0,034 s per detik nyata di 20a dan 20b (sama), dan versi 20a juga pernah gagal/lolos bergantian. Belum dipastikan tuntas (pengujian dihentikan atas permintaan); mohon dicek di PC |
| Cek visual otomatis | Render beku (jam, awan, vegetasi, objek bergerak disembunyikan) di 5 sudut (lapangan baseball, spawn, dekat lift, rumah Cooper, dek menara), 192.000 nilai warna per sudut. 20a vs 20b: 25-682 nilai berbeda di piksel stabil; 20a vs 20a (derau metode): 202-4.883. Tidak ada perubahan yang terdeteksi di atas derau |

## 7d. Hasil tahap 20c (29 September 2026)

Dikerjakan: O8, O9. O10 dicoba lalu dibatalkan.

| Butir | 20b | 20c |
| --- | --- | --- |
| Muat total | 7.259 ms | 4.190 ms (-42%) |
| Peta tinggi tanah | 2.426 ms | 854 ms |
| Pohon | 1.526 ms | 513 ms |
| Kota, sungai, ladang | 1.406 ms | 1.335 ms (O10 dibatalkan) |
| Sidik data dunia (peta tinggi, tekstur tinggi, 22.008 pohon, 44.685 collider, kanvas lahan) | | sama persis dengan 20b |

O10 (`willReadFrequently` pada kanvas lahan) sempat memangkas bagian kota ke 626 ms, tetapi raster CPU membuat 9,4% piksel kanvas berbeda (51% di antaranya selisih 1/255, 4.479 piksel lebih dari 10/255, maksimum 46) di tepi anti-alias. Kanvas ini menentukan jalan, trotoar, dan rumput di shader, jadi dibatalkan. Alternatif yang masih identik: hitung `FAR.land` dari salinan kanvas yang diperkecil di GPU, atau tunda pembacaan data lahan ke saat pertama dibutuhkan.

## 7e. Hasil tahap 20d (29 September 2026)

Dikerjakan: O3, dengan cara lain dari usulan awal. Bukan memecah InstancedMesh per sektor, tetapi memilih instance per pass bayangan: hanya gedung, peralatan atap, dan mobil yang jatuh di kotak kamera bayangan yang digambar. Uji dilakukan di koordinat silinder terbuka yang sama dengan shader (`shUnroll`), jadi yang dibuang memang tidak menyentuh peta bayangan.

Segitiga pass bayangan per frame (Ultra, 11.00; cap + sunline):

| Lokasi | 20c | 20d | Perubahan |
| --- | --- | --- | --- |
| Spawn kota | 980.742 + 947.638 = 1.928.380 | 274.628 + 223.974 = 498.602 | -74% |
| Lapangan baseball | 1.070.980 + 965.140 = 2.036.120 | 389.912 + 240.482 = 630.394 | -69% |
| Bukit | 1.503.157 + 1.430.389 = 2.933.546 | 776.115 + 703.087 = 1.479.202 | -50% |
| Hutan | 1.891.601 + 1.697.169 = 3.588.770 | 1.164.299 + 969.867 = 2.134.166 | -41% |
| Ladang jagung | 1.438.845 + 1.355.153 = 2.793.998 | 724.127 + 628.113 = 1.352.240 | -52% |

Draw call pass bayangan turun 2-8 per frame. Pass utama tidak berubah.

| Butir | Isi |
| --- | --- |
| Gedung dan peralatan atap (7 InstancedMesh, 35.600 instance) | Bola batas tiap instance dihitung sekali saat muat. Pilihan per pass dibuat dengan cadangan 16 m dan hanya dihitung ulang bila kamera bayangan bergeser lebih dari 12 m (geser pemain + putaran arah cahaya cap x 1.500 m). Matriks terpilih disalin ke atribut pengganti; selama pass, `instanceMatrix` dan `count` mesh ditukar lalu dikembalikan |
| Mobil (3.455) | Dipilih tiap frame dari posisi simulasi (`aSim`, data yang sama dengan yang dibaca `CAR_VS`), dengan geometri pengganti per pass. Spawn kota: 70 mobil di pass cap, 15 di pass sunline (dulu 3.455 di keduanya) |
| Identik | Render beku dengan pemilihan nyala vs mati di halaman yang sama: 0 dari 518.400 nilai (RGBA 480 x 270) berbeda per lokasi di 6 lokasi siang (spawn, lapangan baseball, pusat New York, pasar, Skyway, dek menara), dan 0 selama 16 langkah jalan 4 m di 3 titik (termasuk dekat end cap A, tempat arah cahaya cap berubah paling cepat). Kontrol: dengan cadangan sengaja dibuat -60 m, 5 dari 6 lokasi langsung berbeda (306-1.248 nilai), jadi uji ini memang peka |
| Uji | `qc_load` tanpa error |
| Sisa terbesar | Jagung 3D dekat (`CORN.near`, 2.667 instance x 145 = 386.715 segitiga per pass) di hutan, bukit, dan ladang. Posisinya dihitung di shader dari posisi mata, jadi perlu cara lain (mis. uji jarak ke petak jagung per pass, seperti `cornGate()`) |

Kode: `SHP` + `shpBegin()` / `shpEnd()` dipanggil di `shadowPass()` dan `sunShadowPass()`; `SHP.on = false` mematikan pemilihan (untuk perbandingan).

## 8. Cara ukur

| Item | Nilai |
| --- | --- |
| Browser | Chromium headless 1194 (Playwright 1.56), SwiftShader (GL perangkat lunak), jendela 640 x 360 |
| Preset | Ultra, turun otomatis dimatikan |
| Lokasi | spawn kota (11.00 dan 22.00), puncak bukit, hutan lebat, ladang jagung |
| Instrumen | Salinan halaman di scratchpad (file repo tidak diubah): waktu per fungsi di `frame()`, pembungkus `renderer.renderBufferDirect` untuk segitiga dan draw call per objek dan per pass, penanda waktu di bagian muat |
| CPU per frame | Fungsi dipanggil langsung 240 kali dengan dt 1/60 s |
| Baca-balik | `getImageData` 1 piksel kanvas awan tepat setelah `requestAnimationFrame`, 8 kali |

## 9. Batasan

- Waktu GPU (ms) tidak bisa diukur di SwiftShader; yang andal di sini: jumlah segitiga, draw call, waktu JavaScript, waktu muat relatif. Karena itu alat ukur GPU diusulkan pertama.
- Segitiga = segitiga yang dikirim (termasuk instance yang dibuang di vertex shader), jadi mencerminkan kerja vertex, bukan piksel.
- Jeda `getImageData` 4,8-5,4 s adalah waktu satu frame SwiftShader; itu membuktikan CPU menunggu GPU, tetapi besarnya di GTX 1060 dan M1 belum diketahui (kemungkinan sekitar satu frame GPU, 2,5 kali per detik).
- Angka muat dari CPU container ini; di PC dan M1 angka mutlak berbeda, proporsinya kemungkinan mirip.
- Semua "perkiraan" di bagian 1 dan 2 adalah hitungan dari data di atas, belum diukur setelah perubahan.
- Tidak ada perubahan kode di analisa ini; visual belum dibandingkan dengan screenshot (sesuai aturan kerja, uji visual oleh Bhakti).
