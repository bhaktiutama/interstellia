# Analisa performa: best practice three.js dan WebGPU, perubahan, banding A/B

Cabang: `perf/optimasi-threejs` (dari `main` 4196396). Alat: `tools/bandingkan_perf.py` (banding A/B), `tools/uji_performa.py` (uji fungsi).

## 1. Ringkasan

- Kode sudah menerapkan hampir semua best practice three.js yang bisa diukur (bagian 3). Celah yang ditemukan hampir semuanya di jalur muat, bukan di loop per frame; 7 perubahan kode dan 1 alat ukur dikerjakan (bagian 4), semuanya tanpa menurunkan kualitas atau fungsi.
- WebGPU: tidak dimigrasikan. `WebGPURenderer` three.js tidak menjalankan `ShaderMaterial` GLSL, dan proyek ini memakai 260 program GLSL kustom di Copper saja (bagian 5). Padanan WebGL2 dari praktik WebGPU yang relevan sudah ada atau dikerjakan.
- Hasil banding A/B (bagian 2) dan daftar aset eksternal yang membebani (bagian 6) ada di dokumen ini. Beban terbesar: three.js 2,12 MB dari CDN (satu-satunya dependensi jaringan luar), peta Jupiter 14k (13,8 MB di jaringan, sekitar 553 MB di memori GPU), dua lagu tema 13,1 MB.

## 2. Hasil banding A/B

### 2.1 Metode

- `tools/bandingkan_perf.py --a <main> --b <cabang>`: kedua salinan disajikan lewat server HTTPS lokal dengan gzip (seperti GitHub Pages); `cdn.jsdelivr.net` dipetakan ke server lokal yang menyajikan three.js 0.186.1; bandwidth dibatasi CDP 20 Mbps dengan RTT 40 ms untuk semuanya (pembagian bandwidth nyata antar berkas).
- Chromium headless dengan SwiftShader (tanpa GPU). A = `main` 4196396, B = cabang ini. Median dari 4 ulangan (Copper, Millar, detail Copper; urutan A / B ditukar tiap ulangan agar yang pertama tidak selalu "dingin") atau 3 ulangan (menu, Gargantua, detail Gargantua dan Millar).
- `modul_mulai` = waktu modul experience mulai jalan (`window.__stationBoot`); `siap` = flag siap experience (`__stationReady`, `__millarReady`, Gargantua `__gargantua` + `#boot` tersembunyi, `__detailReady`); `dcl` = `DOMContentLoaded` selesai.

### 2.2 Halaman yang diubah

| halaman | metrik | A (main) | B (cabang) | selisih |
| --- | --- | --- | --- | --- |
| Copper | modul experience mulai jalan (ms) | 1.743 | 739 | -57,6% |
| Copper | DOMContentLoaded (ms) | 1.792 | 792 | -55,8% |
| Copper | siap bermain (ms, SwiftShader) | 28.476 | 25.386 | -10,8% (3,1 detik) |
| Copper | rentang siap, 4 ulangan (ms) | 25.657 - 29.290 | 24.805 - 26.400 | |
| Copper | byte terkirim (gz) / berkas | 4.134.206 / 26 | 4.135.652 / 26 | +0,0% |
| Millar | siap (ms) | 6.966 | 6.566 | -5,7% (dalam derau) |
| Millar | byte / berkas | 583.131 / 12 | 583.721 / 12 | +0,1% |

### 2.3 Kontrol: halaman yang tidak diubah (batas derau pengukuran)

| halaman | metrik | A | B | selisih |
| --- | --- | --- | --- | --- |
| menu | siap (ms) | 227 | 216 | -4,9% |
| Gargantua | siap (ms) | 665 | 727 | +9,3% |
| detail Copper | DOMContentLoaded (ms), 4 ulangan | 168 | 197 | +17,4% |
| detail Copper | siap (ms) | 266 | 242 | -9,2% |
| detail Gargantua | siap (ms) | 412 | 398 | -3,4% |
| detail Millar | siap (ms) | 209 | 214 | +2,2% |

Halaman yang tidak disentuh bergeser sampai 17% hanya karena derau, jadi selisih di bawah sekitar 15% pada halaman kecil dan di bawah sekitar 10% pada Copper tidak boleh dibaca sebagai perbaikan. Yang jelas di atas derau: `modul_mulai` Copper (-58%, tiap ulangan B 705-781 ms lawan A 1.660-1.950 ms) dan `siap` Copper (median -3,1 detik; rentang A dan B sedikit tumpang tindih).

### 2.4 Mikro-benchmark dan bukti terpisah

| Pengukuran | Sebelum | Sesudah |
| --- | --- | --- |
| Profil V8 muat Copper: `fluffAtlas()` waktu sendiri | 4.518 ms (16,3% dari 27,8 s), baris `getImageData` | tidak masuk 30 fungsi teratas |
| Pembangkitan dua atlas rumput (kanvas 1536 x 512 x 3, 2 atlas, via `fluffAtlas`) | 1.776 ms | 62 ms |
| Benchmark baca-balik tiga kanvas 1536 x 512, dua kali | 326-781 ms | 33-47 ms |
| Selisih nilai atlas rumput (kanal RGBA, 3.145.728 nilai): jenis rumput | | 37.529 beda (1,19%), 1.918 beda > 32 (0,06%), maks 116 |
| Selisih nilai atlas gandum | | 105.358 beda (3,35%), 6.844 beda > 32 (0,22%), maks 120 |
| Segitiga vs kuad layar penuh (641 x 359, target float, 920.476 nilai) | | selisih maks 1,8e-5 (di bawah resolusi 8-bit dan half-float) |

Selisih atlas hanya di piksel tepi siluet (anti-alias raster CPU vs GPU), bukan perubahan bentuk. Di GPU asli, penghematan P-A1 lebih kecil daripada di sandbox (baca-balik kanvas akselerasi di SwiftShader sangat lambat); angkanya tidak diukur di GPU asli.

### 2.5 Yang tidak berubah atau tidak terukur

- Byte terkirim sama (perubahan tidak mengecilkan berkas; yang berubah urutan dan paralelisme unduhan).
- FPS dan ms per frame: SwiftShader menghasilkan 0,17 fps (Copper) dan 2 fps (Millar), sehingga selisih `task_ms_frame` (-19%, -26%) tidak bermakna. Heap JS Copper: median setelah muat 92,7 MB (A) lawan 72,5 MB (B), tetapi setelah bermain 47,1 lawan 54,6 MB; angka ini mengikuti waktu pemulungan memori, bukan perubahan nyata. Tidak ada klaim FPS atau memori.
- Memori GPU: tidak diukur. Millar tidak lagi meminta buffer stensil pada kanvas (`getContextAttributes().stencil === false`); penghematan memori belum terukur.

### 2.6 Uji regresi (di cabang ini, SwiftShader)

| Uji | Hasil |
| --- | --- |
| `tools/uji_performa.py` (baru) | 14 pemeriksaan lulus, termasuk data besar gagal dimuat (halaman tetap siap, jalur cadangan) dan `file://` |
| `tools/uji_orang.py` | LOLOS (17 ember, `?orang=lama` sidik jari sama) |
| `tools/uji_planet.py` | LULUS; Saturnus identik dengan komit 24b174e: 0 nilai berbeda di 9 render langit jauh |
| `tools/uji_vr.py` | LOLOS (termasuk Copper VR, yang memakai `fsPass`) |
| `tools/uji_pejalan_kaki.py` | exit 0, tanpa kegagalan |
| `tools/uji_rumput_bukit.py` | satu dari tiga jalan di cabang ini gagal pada pemeriksaan jumlah rumpun (0 + 0); dua jalan berikutnya memberi 5.249 + 16.101, sama dengan `main`. Dugaan: waktu tunggu tetap 3 detik di SwiftShader saat mesin sibuk; belum dibuktikan |
| `tools/uji_millar.py` | satu kegagalan (`Jkosong`, tombol J) yang sama persis di `main`: sudah ada sebelum cabang ini (uji belum mengikuti lagu tema bawaan) |
| Tangkapan layar Copper Ultra di bukit, `main` vs cabang | dibandingkan mata: tidak ada artefak dari segitiga layar penuh atau atlas rumput baru |

## 3. Best practice three.js: status di kode ini

Status: ADA = sudah ada sebelum cabang ini (bukti di kolom bukti), BARU = dikerjakan di cabang ini, TIDAK = tidak dikerjakan (alasan di kolom bukti), N/A = tidak berlaku.

| No | Praktik | Status | Bukti / catatan |
| --- | --- | --- | --- |
| 1 | Batasi device pixel ratio | ADA | `CONFIG.dprMax` (2; 0,85 di ponsel) dan `applyPixelRatio()` Copper; Gargantua `renderScale` |
| 2 | Resolusi dinamis saat FPS turun | ADA | Copper `dynScale` / `CONFIG.dynRes`; Millar `POSTKIT.dynRes`; Gargantua `renderScale` turun otomatis |
| 3 | `antialias: false` bila ada post-processing, AA lewat TAA / FXAA | ADA | ketiga experience; TAA di Ultra (`shared/post.js`) |
| 4 | `powerPreference: 'high-performance'` | ADA | ketiga experience |
| 5 | Tanpa buffer stensil / depth yang tak terpakai | BARU (Millar) | Copper `stencil: false`, Gargantua `depth: false, stencil: false`; Millar kini `stencil: false` (diuji `uji_performa.py`) |
| 6 | Target render HDR setengah resolusi untuk AO, SSR, lampu, sunrays, bloom | ADA | `POST_R.ao/ssr/lamp/ray/down/up` (w >> 1) |
| 7 | Satu segitiga layar penuh, bukan kuad | BARU (Copper) | Millar sudah segitiga; Copper `fsQuad` kini 3 vertex (bagian 4, P-A5) |
| 8 | Instancing untuk objek berulang | ADA | 61 baris `InstancedMesh` di Copper; impostor pohon satu draw (`IMPM`) |
| 9 | Gabung geometri statis per material | ADA | `mergeByMaterial`, `shadowProxy` |
| 10 | Frustum culling, bola batas, `enableCull` | ADA | `enableCull`, `SHP` memilih penghalang bayangan per kotak kamera |
| 11 | Mesh kosong tidak dikirim ke GPU | ADA | D1: `K.mesh.visible = c > 0` |
| 12 | LOD (mesh, impostor, orang, mobil) | ADA | `updateTreeLOD`, impostor oktahedral, 3 tingkat detail orang, mobil dekat per preset |
| 13 | Layers untuk memisahkan pass (bayangan, alfa) | ADA | `layers.set/enable` 19x Copper |
| 14 | `renderOrder`, `depthWrite: false` untuk transparan | ADA | 20 dan 31 pemakaian di Copper |
| 15 | Prakompilasi semua program sebelum bermain | ADA | `WARMKIT.compile`, `warmShaders()`, `?prof=1` `--cek` (0 program baru di frame pertama) |
| 16 | Kompilasi paralel (`KHR_parallel_shader_compile`) | ADA | `shared/warm.js`; Gargantua `checkPrograms()` |
| 17 | Bagikan material / program, hindari varian | ADA | `fsMat()` terdaftar di `FS_MATS`; `patchLit` memakai satu pola |
| 18 | Tekstur: mipmap, anisotropi dibatasi | ADA | `anisotropy` 4-8 (hanya `landTex` memakai maksimum GPU) |
| 19 | Tanpa mipmap untuk target yang tak membutuhkannya | ADA | `generateMipmaps: false` 13x Copper, 5x Millar |
| 20 | Ruang warna benar (sRGB / linear) | ADA | `colorSpace` 24x Copper |
| 21 | Atlas dan tekstur array untuk mengurangi pergantian tekstur | ADA | atlas daun, `WebGLArrayRenderTarget` impostor |
| 22 | Pembacaan balik GPU secara asinkron | ADA | `readRenderTargetPixelsAsync` (adaptasi mata, autofokus, tinggi ombak); Gargantua PBO + fence |
| 23 | Pembacaan balik kanvas 2D lewat raster CPU | BARU | `willReadFrequently` untuk atlas rumput (P-A1). `landCanvas` sengaja tidak diubah (keputusan pemilik: 9,4% piksel tepi berbeda) |
| 24 | Dekode gambar besar di luar thread utama | BARU | `img.decode()` peta Jupiter (P-A6) |
| 25 | Dekode base64 besar secara native | BARU | lagu tema `fetch('data:...')` (P-A7) |
| 26 | Unduh data besar paralel, tidak memblokir modul | BARU | data orang 3,5 MB dan rumput dimuat async, ditunggu di titik pakai (P-A2) |
| 27 | `preconnect` + `modulepreload` untuk dependensi CDN | BARU | three.module.js dan three.core.js (P-A3) |
| 28 | Muat malas aset berat yang tidak selalu dipakai | ADA | Jupiter hanya bila dipilih, motor saat dibutuhkan, lagu satu per satu |
| 29 | Kuantisasi dan kompresi mesh | ADA | `siapkan_orang.mjs`: meshoptimizer + kuantisasi; normal int8 |
| 30 | Tekstur terkompresi GPU (KTX2 / Basis, BC7, ASTC) | TIDAK | peta Jupiter dan semua tekstur lain tetap RGBA8 di GPU. Butuh encoder `basisu` / `toktx` yang tidak ada di lingkungan ini; ini peluang terbesar sisa untuk memori GPU (bagian 6) |
| 31 | Pembaruan matriks: `matrixAutoUpdate = false` untuk objek statis | ADA sebagian | 16 pemakaian di Copper; Millar 0 (adegan Millar kecil, tidak diukur sebagai masalah) |
| 32 | Hindari alokasi objek per frame | ADA sebagian | pemulung memori (GC) kurang dari 1% waktu thread utama selama bermain (profil V8: Copper 0,45%, Millar 0,15%); `new Vector3` di fungsi per frame tidak diubah tanpa bukti masalah |
| 33 | Pembersihan memori: `dispose` target dan geometri yang diganti | ADA | target dipakai ulang lewat `setSize`; ganti planet = muat ulang halaman (memori GPU bersih) |
| 34 | Jeda saat tab tersembunyi | ADA (peramban) | `requestAnimationFrame` berhenti sendiri di tab tersembunyi; audio sengaja tetap berjalan |
| 35 | Gambar hanya saat terlihat (halaman statis) | ADA | halaman detail: `IntersectionObserver`, `o.req()`; menu: paralaks hanya saat gulir |
| 36 | Pendengar input pasif bila tidak memanggil `preventDefault` | ADA | `{ passive: true }` pada gulir menu; pendengar `wheel` / `touchmove` di kanvas memanggil `preventDefault` (`{ passive: false }` eksplisit), jadi tidak bisa pasif |
| 37 | Bayangan: hanya penghalang yang terlihat, pembaruan jarang | ADA | `SHP`, `shpBegin/End`, `treeShadowSet()` (D4), peta dekat dan jauh |
| 38 | Alat ukur bawaan | ADA | `PROFKIT` (`?prof=1`), `GPUT` (timer query), `tools/ukur_draw_call.py`, HUD draw call |
| 39 | Kompresi HTTP (gzip / brotli) untuk berkas teks dan base64 | N/A di repo | diatur server. Uji A/B memakai gzip; base64 mp3 / JPEG hampir tidak mengecil |
| 40 | Cache lintas kunjungan (Service Worker) | TIDAK | butuh http(s) dan menambah kompleksitas; aplikasi dipakai juga dari `file://` |
| 41 | Web Worker / OffscreenCanvas untuk pekerjaan berat | TIDAK | nol pemakaian. Kandidat: pembangunan dunia saat muat, `stepPeds`, `stepTraffic`. Perombakan besar dengan risiko regresi tinggi, butuh uji di GTX 1060 dan M1 |
| 42 | UBO / `UniformsGroup` untuk uniform yang dipakai banyak program | TIDAK | belum ada bukti uniform upload menjadi penghambat; butuh ukur di GPU asli |
| 43 | Build three.js minify (`.min.js`) | TIDAK | selisih gzip kecil dibanding risiko (impor `three.core.js` harus dipetakan ulang); lihat bagian 6 |
| 44 | Context `alpha: false` agar kanvas tidak di-blend peramban | TIDAK | three.js membuat konteks `alpha: true`; mengganti berpotensi mengubah warna piksel berdaya alfa < 1 (kualitas) |
| 45 | Format HDR 4 B per piksel (R11G11B10F) bukan RGBA16F | TIDAK | presisi lebih rendah (tanpa alfa, mantisa 5-6 bit) dan AO / jarak memakai kanal lain: risiko kualitas |
| 46 | Buffer kedalaman logaritmik Millar diganti reversed-Z (`logarithmicDepthBuffer: true` menulis `gl_FragDepth` dan mematikan early-Z di GPU) | TIDAK | kandidat GPU terbesar Millar, tetapi menyentuh semua shader kustom (laut, wahana, gelombang) dan pembacaan kedalaman di komposit; tidak bisa diverifikasi tanpa GPU asli |

## 4. Perubahan yang dikerjakan

| ID | Berkas | Perubahan | Verifikasi |
| --- | --- | --- | --- |
| P-A1 | `experiences/cooper-station/index.html` `fluffAtlas()` | kanvas atlas rumput / gandum dibuat dengan `willReadFrequently: true` (tiga `getImageData` per atlas, dua atlas) | mikro-benchmark; selisih piksel atlas (bagian 2.2) |
| P-A2 | Copper | `orang.data.js` (3,5 MB) dan `rumput.data.js` dimuat sebagai skrip async di awal; modul menunggu `window.__dataP.rumput` / `.orang` tepat sebelum dipakai (jalur cadangan `?rumput=lama`, `?orang=lama`, gagal muat tetap berlaku) | `uji_performa.py`; A/B |
| P-A3 | Copper, Millar | `<link rel="preconnect">` dan dua `<link rel="modulepreload">` (three.module.js, three.core.js) | `uji_performa.py`; A/B |
| P-A4 | Millar | `stencil: false` pada `WebGLRenderer` | `getContextAttributes().stencil === false` |
| P-A5 | Copper `fsQuad` | segitiga layar penuh (3 vertex, uv 0 / 2) untuk sekitar 20 pass layar penuh | uji piksel terpisah: selisih maksimum 1,8e-5 pada nilai float (bagian 2.2) |
| P-A6 | Copper Jupiter | `img.decode()` sebelum membuat tekstur (JPEG hingga 14.400 x 7.200 didekode di luar thread utama) | `uji_performa.py` Jupiter 4k |
| P-A7 | `shared/music.js` | dekode base64 lagu dengan `fetch('data:...')` (cadangan loop lama) | lagu terdekode jadi blob, durasi 219,96 s |
| P-A8 | `tools/` | `bandingkan_perf.py` (A/B dengan server HTTPS gzip dan bandwidth CDP), `uji_performa.py` | dijalankan untuk dokumen ini |

## 5. Best practice WebGPU: padanan dan keputusan

Keputusan: tetap WebGL2. Alasan: (a) `WebGPURenderer` three.js memakai `NodeMaterial` / TSL; `ShaderMaterial` GLSL tidak didukung, sedangkan Copper memakai 260 program GLSL (diukur `tools/ukur_muat.py`: 146 saat muat + 114 saat bermain) dan 117 penanda `glsl` di sumbernya; Millar 29; Gargantua memakai WebGL2 mentah dengan satu shader pelacak sinar besar. Menulis ulang semuanya tanpa mengubah tampilan tidak bisa dibuktikan di lingkungan tanpa GPU asli. (b) `three.webgpu.js` 2,28 MB menambah beban unduh. (c) Perangkat uji pemilik (GTX 1060, M1) belum tentu mendukung WebGPU di peramban yang dipakai.

| No | Praktik WebGPU | Padanan di kode ini | Status |
| --- | --- | --- | --- |
| 1 | Buat pipeline asinkron (`createRenderPipelineAsync`) dan pemanasan | `KHR_parallel_shader_compile` + `WARMKIT` | ADA |
| 2 | Gunakan ulang bind group, kurangi `setBindGroup` | kurangi pergantian program / material: D1-D8, impostor satu draw, gabung per material | ADA |
| 3 | Render bundle untuk adegan statis | tidak ada padanan WebGL2 | N/A |
| 4 | Culling dan draw tidak langsung di GPU (compute + indirect) | culling CPU `SHP`, `enableCull` | TIDAK (butuh WebGPU) |
| 5 | Compute shader untuk simulasi (boid, pejalan kaki, kulit) | FFT laut Millar di GPU (IFFT Stockham di fragment); kulit orang di vertex shader; boid, pejalan, lalu lintas tetap CPU | sebagian |
| 6 | Unggah buffer berkelompok (`writeBuffer`, `mappedAtCreation`) | `InstancedBufferAttribute` diperbarui sekali per frame | ADA |
| 7 | Pembacaan balik asinkron (`mapAsync`) | `readRenderTargetPixelsAsync`, PBO + fence di Gargantua | ADA |
| 8 | Timestamp query untuk profil GPU | `GPUT` (`EXT_disjoint_timer_query_webgl2`), HUD ms GPU | ADA |
| 9 | Tekstur terkompresi (BC7 / ASTC / ETC2) dan mip di GPU | belum (butuh encoder) | TIDAK |
| 10 | Format HDR hemat bandwidth (`rg11b10ufloat`) | `RGBA16F` dipertahankan demi presisi | TIDAK |
| 11 | MSAA 4x native | TAA (Ultra) dan FXAA; MSAA di target HDR setengah-float mahal | TIDAK |
| 12 | Minta `limits` / fitur sesuai kebutuhan | `capabilities.maxTextureSize` membatasi resolusi Jupiter | ADA |

## 6. Aset eksternal yang membebani

Ukuran dari `git ls-files` / `wc -c` pada `main`; "gz" diukur `gzip -9` pada berkas yang sama. Memori GPU dihitung dari dimensi (RGBA8, + sepertiga untuk mipmap).

| Aset | Asal | Ukuran | Kapan dimuat | Beban | Catatan |
| --- | --- | --- | --- | --- | --- |
| three.js 0.186.1 (`three.module.js` 662.772 B + `three.core.js` 1.458.113 B) | cdn.jsdelivr.net (pihak ketiga, MIT) | 2.120.885 B (gz 417.103 B) | awal Copper dan Millar, memblokir mulai modul | satu-satunya dependensi jaringan luar; halaman tidak jalan tanpa internet | kini `modulepreload` (P-A3). Self-host sebagai ES module tidak bisa dari `file://`. Gargantua dan menu tidak memakainya |
| Peta Jupiter 14k | Bjorn Jonsson, data NASA Cassini + Juno | 13.802.277 B | hanya Jupiter + pilihan 14k | memori GPU sekitar 553 MB (14.400 x 7.200 x 4 B + mip); dekode JPEG besar | dekode kini asinkron (P-A6). Pilihan terbesar yang paling mahal; bawaan 8k |
| Peta Jupiter 8k | sama | 5.285.158 B | Jupiter bawaan | memori GPU sekitar 179 MB | |
| Peta Jupiter 4k | sama | 1.481.990 B | Jupiter pilihan 4k | sekitar 45 MB GPU | |
| Lagu tema 1 dan 2 | karya pemilik proyek, mp3 base64 | 6.314.392 B dan 6.818.484 B | satu lagu saat pertama dibutuhkan | base64 + 33%; string 6-7 MB tertahan sampai dekode | dekode kini native (P-A7) |
| `orang.data.js` | Quaternius via poly.pizza (CC BY / CC0) | 3.516.792 B | awal Copper | skrip terbesar saat muat | kini async (P-A2) |
| `motor.data.js` | Sketchfab, Alexios Apokaukos (CC BY 4.0) | 3.112.306 B | saat motor dibutuhkan | | sudah dimuat malas |
| `rumput.data.js` | FluffyGrass (MIT) | 160.519 B | awal Copper | kecil | kini async (P-A2) |
| Blob wahana (`gx01`, `pr11`, `ks07`) | proyek sendiri | 371.704 B, 363.858 B, 205.745 B | hanya wahana terpilih (Gargantua / Millar) | | |
| Foto menu (`menu.webp` x3) | proyek sendiri | 428.046 B, 301.152 B, 183.128 B | menu, awal | 0,89 MB total menu | sudah webp |
| Diagram SVG detail (24 berkas) | dibangkitkan `tools/diagram_detail_*.py` | 1.242.912 B | `loading="lazy"` di halaman detail | | sudah malas; satu berkas 330 KB (`gg-04`) |
| Font | tidak ada (system-ui, monospace) | 0 | | | tanpa font web |

Peluang yang tidak dikerjakan: KTX2 / Basis untuk peta Jupiter (turun beberapa kali lipat di memori GPU, butuh `basisu`), `three.*.min.js` lewat jsDelivr dengan petakan ulang `three.core.js` di importmap (hemat sekitar puluhan KB gz dan waktu parse), Service Worker untuk cache lintas kunjungan.

## 7. Batas dan ketidakpastian

- Semua ukuran waktu di sandbox memakai SwiftShader (GPU perangkat lunak). FPS dan ms per frame tidak mewakili GTX 1060 / M1; yang andal: byte, jumlah berkas, urutan muat, waktu pembangunan dunia di CPU, jumlah program dan draw call. Dampak ke FPS nyata belum terukur dan perlu uji pemilik (HUD draw call dan ms GPU).
- Perubahan P-A1 (raster CPU untuk atlas) tidak identik bit per bit dengan raster GPU di tepi anti-alias (bagian 2.2); keputusan pemilik untuk `landCanvas` (tidak diubah) tetap dihormati.
- WebGPU tidak diuji: tidak ada GPU maupun peramban WebGPU di lingkungan ini.
