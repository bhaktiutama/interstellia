# Rencana ray tracing (kajian ThreeRT)

Tanggal: 14 November 2026. Status: kajian, belum dikerjakan.

## Ringkasan

- ThreeRT (meshy-dev) **tidak bisa dipasang langsung** di Interstellia: path tracer-nya mesin native (Rust + wgpu, klien macOS / iOS tertutup), bukan library browser. File scene yang sama di browser hanya jalan sebagai three.js biasa, tanpa ray tracing.
- Yang memungkinkan: membuat ray tracing sendiri di WebGL2 untuk bagian terbatas. Usulan utama RT-A (path tracing di mode foto, satu kawasan kecil) dan RT-B (pantulan dan bayangan ray trace analitik ke kotak gedung kota Copper, real-time, Ultra saja).
- Effort: RT-A High (sekitar 5 langkah), RT-B High (sekitar 4 langkah). Port penuh ke ThreeRT = proyek baru, tidak disarankan.

## 1. Apa itu ThreeRT (dari README, ARCHITECTURE.md, ROADMAP.md)

| Hal | Isi | Sumber |
| --- | --- | --- |
| Bentuk | Path tracer real-time dengan API mirip three.js; mesin Rust + wgpu (Metal / Vulkan / lavapipe), scene ditulis TypeScript (`build()` mengembalikan `{ scene, camera }`) | README, ARCHITECTURE.md |
| Platform | Klien macOS 14+ Apple silicon dan iOS 17+ (gratis, kode tertutup); Linux Vulkan / lavapipe untuk node render. Windows tidak disebut | README, ARCHITECTURE.md |
| Browser | "the same file runs as plain three.js in any browser": di browser tidak ada ray tracing | README |
| Ray tracing | Ray query perangkat keras bila ada, BVH perangkat lunak bila tidak | README |
| Material | `MeshStandardMaterial` / `MeshPhysicalMaterial`, lampu three.js, `GLTFModel`, `SkyAtmosphere`; shading khusus lewat "material functions" WGSL. ShaderMaterial, onBeforeCompile, GLSL sendiri, InstancedMesh, render target, efek layar tidak disebut | ARCHITECTURE.md |
| Denoiser | Live: filter temporal + spasial (a-trous); OIDN di node render | ROADMAP.md, ARCHITECTURE.md |
| Resolusi live | Path tracing di 0,5 skala (640 x 360) lalu di-upscale, resolusi dinamis sering sekitar 0,57 | ROADMAP.md |
| Kinerja | Bistro malam 1280 x 720 di Apple M3 Max: 15,5 ms per frame (three.js WebGPU + SSGI + SSR + TRAA: 34,7 ms); three.js lebih cepat di scene kecil (sekitar 1 ms) | README |
| Batas yang diakui | Geometri dinamis dibangun ulang tiap frame (wgpu 30 tanpa refit), ghosting pada objek bergerak, memori Tokyo 16-18 GB, CPU stall | ROADMAP.md |
| Lisensi | MIT (proyek riset) | README |

Catatan: angka kinerja di atas dari GPU M3 Max dengan RT perangkat keras. Tidak ada angka untuk GPU tanpa RT perangkat keras (GTX 1060, M1); dokumen ThreeRT tidak memberikannya.

## 2. Kenapa tidak bisa dipakai langsung

| Syarat Interstellia | ThreeRT | Akibat |
| --- | --- | --- |
| Jalan di browser, juga dari file:// | Ray tracing hanya di klien native | Fatal |
| PC uji Windows + GTX 1060 | Windows tidak disebut; GTX 1060 tanpa inti RT | Fatal untuk PC utama |
| MacBook M1 | macOS 14+ Apple silicon didukung, tetapi M1 tanpa RT perangkat keras (jalur BVH perangkat lunak, tanpa angka kinerja) | Tidak pasti |
| Shader GLSL sendiri (`LIGHT_GLSL`, `BUILD_FS`, laut FFT Millar, `SCENE_FS` Gargantua; Copper 30 dan Millar 22 kemunculan `ShaderMaterial` / `onBeforeCompile`) | Hanya material standar + fungsi WGSL | Semua shader harus ditulis ulang |
| Simulasi di GPU lewat atribut instance (lalu lintas, pejalan kaki, pohon impostor) | InstancedMesh tidak disebut, BVH dibangun ulang tiap frame | Biaya tidak diketahui |
| Kerangka berputar (scene.rotation.z), dua scene (farScene + utama) | Tidak disebut | Harus dirancang ulang |
| Satu file HTML, tanpa build step | Rust, Node 24, Bun | Melanggar aturan proyek |

Kesimpulan: memakai ThreeRT = memindahkan aplikasi ke mesin lain dan meninggalkan browser. Tidak disarankan.

## 3. Efek ray tracing yang sebenarnya bisa didapat

| Efek | Sekarang (perkiraan rasterisasi) | Dengan ray tracing |
| --- | --- | --- |
| Pantulan kaca, air, genangan | SSR (`ssrRefl`, hanya yang ada di layar) + `farEnv` + model ngarai kota 21e | Gedung dan objek di luar layar ikut terpantul dengan benar |
| Bayangan | Peta bayangan `SHADOW` / `SUNSH` (resolusi terbatas, jarak terbatas) | Bayangan tajam di dekat, lembut di jauh, tanpa batas jarak peta |
| Cahaya pantul (GI) | GTAO + ambient warna daratan (`FAR.land`) | Dinding diterangi pantulan tanah dan gedung sebelah, interior rumah terang dari jendela |
| Lampu malam | `lampPoolL` / `nightLight` analitik, tanpa bayangan | Lampu membuat bayangan, cahaya memantul |

Gargantua sudah ray tracer (geodesik di `SCENE_FS`), jadi tidak ada keuntungan besar di sana. Millar langit mendung merata dan laut memantulkan cubemap, keuntungannya kecil. Keuntungan terbesar ada di Copper.

## 4. Usulan

### RT-A: path tracing di mode foto (offline, satu kawasan)

Saat kamera rangefinder menangkap foto (`camCapture()` sudah mengakumulasi subframe), sebuah path tracer WebGL2 menggambar kawasan kecil sekitar kamera (mis. radius 150 m) dari geometri pengganti, lalu hasilnya dicampur dengan langit / jauh dari render biasa.

| Langkah | Isi | Effort | Model | Thinking | File / fungsi |
| --- | --- | --- | --- | --- | --- |
| RT0 | Spike: path tracer mini di halaman uji `docs/app/rt/uji-pathtracer.html` (BVH JS dari kotak + segitiga, tekstur float, 1 sampel per frame), ukur di GTX 1060 dan M1 | High | Opus 5.5 | high | file baru |
| RT1 | Pengumpul geometri kawasan: gedung (`BUILD` kotak), rumah, pohon (kapsul + bola tajuk), tanah (`groundH`), di kerangka stasiun | High | Opus 5.5 | high | `shared/rt.js` baru, Copper `__station` |
| RT2 | Material pengganti: warna dasar, kekasaran, logam, kaca, emisif per kelas (bukan shader asli) | Medium | Sonnet 5.5 | medium | `shared/rt.js` |
| RT3 | Integrasi ke `camSub()` / `camFinish()`: sampel per subframe, cahaya Matahari lewat end cap (`uL_SunDir`), sunline, lampu malam | High | Opus 5.5 | xhigh | Copper `camCapture`, `CAMKIT` |
| RT4 | Denoiser sederhana (a-trous dengan normal + kedalaman) dan campuran tepi kawasan | High | Opus 5.5 | high | `shared/rt.js` |
| RT5 | Tombol di panel kamera, teks ID + EN, `?rt=0` | Low | Haiku 4.5 | low | Copper panel, `I18N.en` |

- Tampilan: foto dengan bayangan, pantulan, dan cahaya pantul benar di kawasan dekat. Bermain biasa tidak berubah.
- Berat: tidak mempengaruhi FPS saat bermain (hanya saat tangkap foto). Waktu tangkap naik dari sekarang menjadi beberapa detik sampai menit per foto; angka pasti menunggu RT0.
- Risiko: material pengganti tidak sama persis dengan shader asli, jadi batas kawasan bisa terlihat.

### RT-B: pantulan dan bayangan ray trace analitik ke gedung kota (real-time, Ultra)

Gedung kota Copper sebagian besar kotak (`building()`, `BUILD`). Kotak bisa dipotong sinar secara analitik lewat grid sel (DDA) di tekstur data, tanpa BVH segitiga. Dipakai untuk satu sinar pantul per piksel kaca / air dan satu sinar bayangan Matahari di luar jangkauan peta bayangan.

| Langkah | Isi | Effort | Model | Thinking | File / fungsi |
| --- | --- | --- | --- | --- | --- |
| RB0 | Spike: tekstur grid kotak gedung (koordinat s, za, tinggi), DDA di GLSL, ukur di GTX 1060 dan M1 | High | Opus 5.5 | xhigh | Copper, blok baru setelah `BUILD` |
| RB1 | Pantulan: ganti model ngarai 21e dan `farEnv` untuk kaca / genangan bila sinar mengenai kotak (warna gedung + jendela dari rumus `BUILD_FS`) | High | Opus 5.5 | xhigh | `LIGHT_GLSL`, `SPEC_GLSL`, `BUILD_FS` |
| RB2 | Bayangan jauh: gedung tinggi membayangi di luar kotak `SUNSH` | High | Opus 5.5 | xhigh | `sunlineShadow()` |
| RB3 | Preset (Ultra saja, setengah resolusi), `?rt=0`, teks panel | Low | Haiku 4.5 | low | `PRESETS`, `PRESET_HOOKS`, `I18N.en` |

- Tampilan: kaca gedung dan genangan memantulkan gedung seberang dengan benar (juga yang di luar layar), bayangan gedung tinggi terlihat jauh.
- Berat: tambahan per piksel kaca / air sebesar loop DDA (perkiraan, belum diukur): sebanding dengan `ssrRefl`. Harus diukur di RB0; di GTX 1060 mungkin hanya layak setengah resolusi.
- Risiko: shader `LIGHT_GLSL` dan kerangka berputar = otomatis High; loop di shader rawan NaN di M1 (aturan GPU di `CLAUDE.md`).

### Tidak disarankan

| Opsi | Alasan |
| --- | --- |
| Port ke ThreeRT | Lihat bagian 2: meninggalkan browser, Windows, dan semua shader |
| Path tracing real-time seluruh dunia di WebGL2 | Tanpa RT perangkat keras di WebGL / WebGPU; dunia Copper terlalu besar (kota, hutan 5.222 pohon, ribuan instance) |
| Pindah ke WebGPU sekarang | Standar WebGPU belum punya ray query; tidak memberi ray tracing perangkat keras |

## 5. Rekomendasi

1. Kerjakan RT0 dan RB0 dulu (spike + ukur di GTX 1060 dan M1), masing-masing satu langkah High. Putuskan lanjut atau berhenti dari hasil ukur.
2. Bila hanya satu: RT-B memberi perubahan yang terlihat saat bermain; RT-A memberi foto paling realistis tanpa risiko FPS.

## 6. Keterbatasan kajian

- Dokumen ThreeRT tidak memberi angka untuk GPU tanpa RT perangkat keras, Windows, atau dukungan InstancedMesh / ShaderMaterial; tabel bagian 2 menandai yang "tidak disebut", bukan "pasti tidak ada".
- ROADMAP.md hanya dibaca 100.000 karakter pertama dari sekitar 474.000.
- Semua perkiraan biaya RT-A dan RT-B adalah perkiraan sebelum ukur; angka nyata menunggu RT0 / RB0 di GPU asli.

Sumber: github.com/meshy-dev/ThreeRT (README.md, docs/ARCHITECTURE.md, docs/ROADMAP.md), dibaca 14 November 2026.
