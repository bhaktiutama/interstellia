# Rencana P: Performa muat dan tersendat (sebelum VR)

Per 9 Oktober 2026 · Status: P0-P4 dikerjakan (lihat Status implementasi), menunggu ukur `?prof=1` dan uji visual pemilik di GTX 1060 dan M1; P5-P6 menunggu data itu. Berlaku untuk Copper Corn Station, Millar's World, dan Gargantua (menu utama dan halaman detail fisika menyusul). Dikerjakan sebelum rencana VR (`docs/app/rencana-vr.md`).

## Status implementasi

| Tahap | Status | Isi | Hasil sandbox (SwiftShader) |
| --- | --- | --- | --- |
| P0 | Selesai | `shared/prof.js` (`PROFKIT`, hanya `?prof=1`, panel kiri bawah + tombol Salin hasil), `tools/ukur_muat.py` (`--cek`, `--json`) | Fase frame pertama dihitung per tick rAF (Copper punya beberapa loop rAF dalam satu tick) |
| P1 | Selesai | Copper `warmShaders()` (scene dan `farScene` dengan target HDR yang sama dengan `postBegin()`, semua material layar penuh `FS_MATS`), `warmFrame()` (bayangan, impostor oktahedral, scene, efek layar; keadaan `ADAPT` / `TAA` / `SSR` dikembalikan), bar 96-98,5% per program + "Pemanasan GPU" | Frame pertama: 96 program, sekitar 11,4 s -> 0 program, 77-98 ms. Halaman bisa dipakai: sekitar 24 s -> 16,2-17,2 s |
| P2 | Selesai | Millar: bar progres di kartu awal (pilihan dan Mulai aktif setelah siap), `millarWarm()` lewat `shared/warm.js` (`WARMKIT.compile`), sisi lensa `GCUBE` satu per langkah + `SKYCUBE` penuh saat muat, render pemanasan (bayangan, dunia, efek layar, adegan orbit bila sinematik akan diputar) | Frame pertama: 9 program, 8,9 s -> 0 program, 30-31 ms. F pertama: 1 program -> 0 |
| P3 | Selesai | Gargantua: 13 program dikirim semua dulu, status dicek sekali (`checkPrograms()`), `KHR_parallel_shader_compile` diaktifkan; pesan galat sama. Layar muat tidak dibuat (siap 0,28 s di sandbox; dibuat bila ukur GTX 1060 menunjukkan perlu) | Siap 0,86 s -> 0,28 s, tunggu program 166 ms -> 14 ms |
| P4 | Selesai | Copper `warmLater()`: varian target lain (P mode Mati = kanvas sRGB) dikompilasi di latar belakang 1,5 s setelah siap. Millar `warmPresets()`: material pemegang per preset (define dari `presetDefs()`, uniform dibagi) menahan program di cache. Keduanya hanya bila ada kompilasi paralel | Copper P, 8, 1, C, 7, N, P, Q: 0 program baru. Millar Q x5 (satu putaran preset) dan F: 0 program baru (sebelumnya Q 5-10 per tekan) |
| P5 | Belum | Sisa CPU muat Copper | Menunggu angka P0 GPU asli |
| P6 | Belum | FPS saat bermain | Menunggu angka P0 GPU asli |

Koreksi akar masalah setelah ditelusuri: 76 dari 96 program frame pertama Copper bukan objek yang terlewat, melainkan varian lain dari material yang sama. Kunci program three.js memuat ruang warna keluaran dan tone mapping, yang bergantung pada target render aktif: prakompilasi lama berjalan tanpa target (kanvas, sRGB), sedangkan dunia digambar ke target HDR (linear). Sisanya: bayangan 9, efek layar 10, `farScene` 3, bake impostor 1. Millar tidak terkena karena `outputColorSpace` sudah linear.

Catatan sandbox: tanpa `KHR_parallel_shader_compile` kompilasi latar belakang P4 tidak dijalankan otomatis (dipaksa di `tools/ukur_muat.py` lewat `pre`), dan waktu menunggu program pindah ke saat tombol ditekan. Di GPU dengan ekstensi itu (Chrome di GTX 1060 dan M1 kemungkinan punya; terlihat di panel `?prof=1`) kompilasi selesai di latar belakang.

Aturan: tanpa mengurangi yang sudah ada. Tiap perbaikan hanya memindahkan atau mempercepat kerja, tidak menurunkan preset, efek, objek, atau detail. Tampilan harus identik (diuji piksel per piksel dengan waktu dibekukan, pola `tools/uji_jendela_gedung.py`).

## Ringkasan

- Penyebab "berhenti lama di 100%" di Copper terukur: bar menunjukkan 100% pada 12,0 s, lalu frame pertama memblokir halaman selama 11,4 s. Dalam frame itu 96 dari 195 program shader baru dikompilasi, karena prakompilasi sekarang hanya meliput objek yang terlihat di `scene` (bukan pass post, peta bayangan, bake impostor, atau objek tersembunyi). Profil CPU: 60,0% waktu muat adalah menunggu shader selesai dikompilasi (`onFirstUse` three.js 11,17 s dari 18,63 s).
- Millar dan Gargantua punya pola serupa. Millar tidak punya bar progres: kartu Mulai sudah tampil tetapi halaman beku 1,0 s + 7,1 s, lalu beku lagi 5,8 s setelah Mulai (sinematik orbit). Saat bermain, ganti preset (Q) mengompilasi 5-6 program dan kamera (F) pertama kali 1 program dengan jeda 9,5 s. Copper juga tersendat saat pertama kali memakai P, 8 (kokpit), C (motor), 7 (terminal).
- Rencana: (P0) alat ukur bersama agar Bhakti bisa mengukur di GTX 1060 dan M1; (P1-P3) semua program dikompilasi paralel di balik bar progres sebelum tombol Mulai, frame pertama "dipanaskan" di balik layar muat; (P4) varian preset dan mode dikompilasi di latar belakang saat bermain; (P5-P6) sisa CPU muat dan FPS setelah ada data GPU asli.

## Data (sandbox)

Diukur dengan Chromium headless + SwiftShader (GPU perangkat lunak), 960 x 540, three.js 0.186.1, satu halaman berjalan sendiri. Skrip ukur: pembungkus `WebGL2RenderingContext.linkProgram` / `getProgramParameter`, `PerformanceObserver` long task, pembungkus `requestAnimationFrame`, profil CPU lewat CDP.

Penting: SwiftShader bukan GPU asli. Jumlah program dan urutan kejadian dapat dipercaya. Lama tiap jeda tidak bisa dipakai untuk GTX 1060 atau M1. Di Windows, Chrome mengompilasi shader lewat ANGLE ke D3D11, dengan biaya yang berbeda dan belum diukur.

### Copper: linimasa muat

| Waktu | Kejadian |
| --- | --- |
| 0,06-0,37 s | Memuat three.js |
| 0,48-2,55 s | Kota, sungai, ladang (2,06 s) |
| 2,57-4,53 s | Peta tinggi tanah (1,96 s) |
| 5,07-9,07 s | Pohon (4,00 s; 2,56 s di antaranya bake impostor per template, kebanyakan menunggu kompilasi) |
| 9,07-11,91 s | Daun, audio, perabot, spaceport, pejalan kaki, mesin ladang (2,84 s) |
| 11,91-12,03 s | "Menyiapkan shader" (0,12 s) |
| 12,03 s | Bar 100% "Siap" |
| 12,08-23,48 s | Frame pertama memblokir halaman 11,40 s (layar Siap belum tergambar) |
| 23,48 s | Halaman bisa dipakai |

Program shader Copper: 195 total; 99 sebelum 100%, 96 di frame pertama, 0 sesudahnya selama 15 s berdiri di spawn.

Profil CPU muat Copper sampai halaman bisa dipakai (sampel 18,63 s):

| Fungsi (inklusif) | ms | Keterangan |
| --- | --- | --- |
| `onFirstUse` (three.js, menunggu program selesai dikompilasi) | 11.170 | 60,0% dari total |
| `frame()` pertama | 8.925 | Termasuk `shadowPass` 2.186 ms, `octBake` 932 ms, `postEnd` 189 ms (hampir semuanya menunggu kompilasi) |
| Loop mesh per template pohon (baris sekitar 9.175) | 2.563 | Bake impostor memicu kompilasi |
| `stepTraffic` (self) | 333 | Pra-simulasi lalu lintas |
| `wrapS` (self) | 261 | Peta tinggi |
| Lain-lain | sisanya | Masing-masing di bawah 160 ms |

### Millar dan Gargantua: linimasa muat

| Experience | Kejadian | Waktu |
| --- | --- | --- |
| Millar | Skrip modul (kartu Mulai sudah terlihat, halaman beku) | long task 1,04 s mulai 0,25 s |
| Millar | Frame pertama (9 program baru + semua sisi cubemap langit `SKYCUBE` dan lensa `GCUBE` dirender sekaligus) | long task 7,10 s (1,29-8,40 s) |
| Millar | Klik Mulai, sinematik kedatangan (adegan orbit pertama kali) | long task 5,78 s |
| Millar | Program total | 43: 33 di `renderer.compile()` sinkron, 9 di frame pertama, 1 sesudahnya |
| Gargantua | Skrip (13 program dikompilasi sinkron di `program()`, status langsung dicek) | long task 0,89 s |
| Gargantua | Program saat bermain (Q x3, P x2, F, V x3) | 0 baru |

### Tersendat saat bermain (program baru per tombol)

| Experience | Tombol | Program baru | Catatan |
| --- | --- | --- | --- |
| Copper | P (efek layar), tiap tekan | 1 | Mode post berikutnya |
| Copper | 8 (kokpit shuttle) | 9 | Kokpit, lambung, layar |
| Copper | C (naik motor) | 5 | Model motor, dasbor, lampu depan |
| Copper | 7 (terminal) | 3 | |
| Copper | N, Q, M, V, Y, I, 0, 1 | 0 | |
| Millar | Q (ganti preset), tiap tekan | 5, 5, 5, 6 | `defines` laut / gelombang / langit berubah + `makeOcean()` / `makeRipple()` / `makeShadow()` |
| Millar | F (kamera rangefinder pertama kali) | 1 | Long task 9,5 s (kedalaman `POST.hdr.depthTexture` dibuat, komposit dikompilasi ulang) |
| Millar | N, P, M | 0 | |

### Akar masalah (dari kode)

| Temuan | Lokasi | Akibat |
| --- | --- | --- |
| Prakompilasi Copper hanya `renderer.compileAsync(scene, camera)` + `farScene`, dibatasi 12 s | Akhir file, "Menyiapkan shader" | Material pass layar penuh (`fsPass(mat)` menukar material di `fsScene`), material kedalaman bayangan (`depthMat`, `vegMaterial`, `castAlpha`), bake impostor (`octBake`), dan objek tersembunyi (kokpit, motor, terminal) tidak ikut, karena `compile` hanya menelusuri objek terlihat di scene yang diberikan |
| Loop `frame()` Copper dimulai langsung setelah "Siap" | `requestAnimationFrame(frame)` di akhir | Layar Siap baru tergambar setelah frame pertama selesai, jadi halaman terlihat beku di 100% |
| Millar memanggil `renderer.compile()` sinkron untuk 4 scene, tanpa bar progres | Akhir file | Halaman beku tanpa tanda progres; pass post `pass(mat)` juga tidak ikut |
| Millar `updateGCube()` / `updateSkyCube()`: frame pertama merender semua sisi | `GCUBE.pending = GCUBE.faces.slice()` | Kerja GPU frame pertama besar (lensa Gargantua `gSteps` sampai 320 langkah per piksel) |
| Millar `applyPreset()` mengubah `defines` lalu `needsUpdate` | `applyPreset()` | Program lama dilepas, program baru dikompilasi saat itu juga |
| Gargantua `program()` memanggil `getShaderParameter(COMPILE_STATUS)` dan `getProgramParameter(LINK_STATUS)` tepat setelah kompilasi | `program()` | Kompilasi menunggu satu per satu. `SCENE_FS` (ray tracer, loop `MAX_ITER` 600) kemungkinan paling mahal di D3D11 (perlu diukur di P0) |
| Tiap pembaruan kode mengubah teks shader | Semua | Inferensi: cache shader Chrome tidak terpakai pada muat pertama setelah update, padahal itulah yang selalu diuji pemilik. Jadi jeda di GTX 1060 bisa lebih besar daripada yang dialami pengguna yang membuka ulang |

## Keputusan desain

1. Kompilasi paralel dengan `KHR_parallel_shader_compile` (`renderer.compileAsync`) untuk semua program, sebelum tombol Mulai. Bar 96% -> 100% mengikuti jumlah program yang selesai (bukan langkah tetap). Bila ekstensi tidak ada, tetap kompilasi di tahap muat (sinkron) dengan bar bergerak per program, tidak di frame pertama.
2. Daftar pemanasan per experience (`WARM`): scene utama dan tambahan (`farScene`, `skyScene`, `gScene`, `orbScene`), semua material pass layar penuh (didaftarkan saat dibuat), material kedalaman / bayangan / bake, dan objek tersembunyi (dikompilasi dalam konteks scene sasaran: `compileAsync(objek, kamera, sceneSasaran)` yang ada di three.js 0.186.1). Objek tersembunyi dinyalakan sementara lalu dikembalikan persis.
3. Frame pemanasan: satu sampai dua frame penuh dirender di balik layar muat (bar "Pemanasan GPU" 98-100%), baru tombol Mulai / layar Siap ditampilkan. Loop `frame()` tetap sama; yang berubah hanya kapan layar Siap tampil.
4. Varian saat bermain dikompilasi di latar belakang setelah Mulai (satu varian per detik saat idle, `requestIdleCallback`): preset Millar, mode P, kamera K. Program dijaga tetap di cache three.js dengan material pemegang tersembunyi, agar tidak dilepas dan dikompilasi ulang saat dipakai.
5. Uji identik: setiap tahap membandingkan render sebelum dan sesudah (waktu, awan, matahari dibekukan, 0 piksel berbeda) di beberapa lokasi, plus semua uji lama per experience tetap lulus.

## Tahap

| Tahap | Isi | File dan fungsi | Effort | Model | Thinking |
| --- | --- | --- | --- | --- | --- |
| P0 | Alat ukur bersama `shared/prof.js` (`window.PROFKIT`, aktif hanya dengan `?prof=1`): tanda tahap muat (dari `bootStep`), program per fase (muat / frame pertama / saat bermain per tombol), waktu menunggu program, long task, 120 frame pertama, tombol "Salin hasil" (JSON). Skrip sandbox `tools/ukur_muat.py` (dari skrip ukur rencana ini) sebagai uji regresi: program di frame pertama dan per tombol harus 0 setelah P1-P4. Bhakti mengukur di GTX 1060 (Chrome Windows) dan M1 sebelum P1, hasil dicatat di rencana ini | `shared/prof.js`, `tools/ukur_muat.py`, satu baris `<script>` per experience | Medium | Sonnet 5.5 | medium |
| P1 | Copper: daftar `WARM` lengkap (pass post `fsPass`, GTAO, SSR, sunrays, kabut lampu, TAA, kamera K, bayangan dan sunline termasuk `shUnroll` / `castAlpha`, bake impostor dan oktahedral, kokpit / lambung shuttle, motor, terminal, peta 3D), `compileAsync` paralel dengan bar per program, bake impostor pohon menunggu programnya siap, frame pemanasan di balik layar muat. Target: 0 program baru di frame pertama dan saat tombol P, 8, C, 7 (sekarang 96 / 1 / 9 / 5 / 3) | Akhir file (blok "Menyiapkan shader"), `fsPass()`, `shadowPass()`, `sunShadowPass()`, `octBake()`, loop template pohon, `SHUTTLE`, `MOTO`, `TERM` | High | Opus 5.5 | high (banyak material `onBeforeCompile`, kerangka berputar di `shUnroll`) |
| P2 | Millar muat: bar progres seperti Copper (`bootStep`), kartu Mulai aktif setelah siap, `compileAsync` paralel menggantikan `renderer.compile()` sinkron, material `pass()` dan kamera K masuk `WARM`, semua sisi `SKYCUBE` dan `GCUBE` dirender di tahap muat (satu sisi per langkah agar bar bergerak), adegan orbit sinematik dipanaskan (render kecil sekali) | Akhir file, `pass()`, `updateGCube()`, `updateSkyCube()`, `renderOrbit()`, `#start` | Medium | Sonnet 5.5 | medium |
| P3 | Gargantua muat: layar muat sederhana dengan bar, 13 program dikompilasi sekaligus lalu status dicek setelah `COMPLETION_STATUS_KHR` (tidak satu per satu), frame pemanasan. Pesan error kompilasi tetap sama | `program()`, `compile()`, objek `P`, awal `frame()` | Low | Sonnet 5.5 | low |
| P4 | Tersendat saat bermain: kompilasi latar belakang varian preset Millar (5 preset x 5-6 program), kamera K Millar (kedalaman + komposit dibuat saat idle setelah Mulai, bukan saat F), mode P Copper; material pemegang agar program tetap di cache. Target: 0 program baru saat Q dan F di Millar | Millar `applyPreset()`, `makePost()`, `makeOcean()`, `makeRipple()`, `makeShadow()`; Copper `POST_MODES` | High | Opus 5.5 | high (cache program three.js, urutan dispose) |
| P5 | Copper sisa CPU muat (ukur ulang setelah P1; sekarang sekitar 7,5 s sampel CPU di luar menunggu shader, termasuk idle 1,1 s): kota 2,06 s, peta tinggi 1,96 s, pra-simulasi lalu lintas dan pejalan kaki. Hanya perubahan berhasil identik (sidik jari FNV-1a dunia seperti 20c dan 25j). Opsi besar (Web Worker, cache IndexedDB) diputuskan setelah angka P0 | Blok kota, `TER`, `stepTraffic`, `stepPeds` | Medium | Sonnet 5.5 | medium |
| P6 | FPS saat bermain berdasar ukuran GPU asli dari P0 (`GPUT` Copper dan Millar per pass, Gargantua timer query baru): titik uji tetap per experience, optimasi hanya yang hasilnya identik; opsi berkompromi visual tidak dikerjakan tanpa persetujuan | Tergantung data | High | Opus 5.5 | high |

Urutan: P0 lalu ukur di GTX 1060 dan M1, lalu P1 (masalah terbesar dan paling sering terlihat), P2, P3, P4, P5, P6. Commit dan push per tahap; Bhakti menguji muat dan FPS setelah P1, P2, P4.

Rencana ini disusun pada tingkat satu di atas tahap terberat (P1, P4, P6 High).

## Verifikasi per tahap

| Cek | Cara | Syarat lulus |
| --- | --- | --- |
| Program di frame pertama | `tools/ukur_muat.py` | 0 (Copper sekarang 96, Millar 9) |
| Program saat tombol | `tools/ukur_muat.py` (tombol per experience seperti tabel di atas) | 0 |
| Tampilan identik | Render sebelum dan sesudah, waktu / awan / matahari dibekukan, beberapa lokasi dan preset | 0 piksel berbeda |
| Uji lama | `tools/qc_load.py`, `tools/uji_millar.py`, `tools/uji_misi_gargantua.py`, uji Copper | Lulus semua |
| GPU asli | `?prof=1` di GTX 1060 dan M1, muat pertama setelah update dan muat ulang | Lama dari 100% sampai halaman bisa dipakai dicatat sebelum dan sesudah |

## Risiko

| Risiko | Penanganan |
| --- | --- |
| Total waktu muat bisa tetap lama walau tidak beku (kompilasi tetap harus terjadi) | Yang dijanjikan: bar bergerak jujur dan tidak beku. Waktu total turun hanya bila kompilasi paralel benar-benar paralel di GPU tersebut; diukur di P0 / P1 |
| Pemanasan objek tersembunyi mengubah keadaan (visible, layer, material) | Simpan dan kembalikan keadaan persis; uji identik |
| Program cadangan (P4) menambah memori GPU | Ukur jumlah program dan memori lewat `renderer.info.programs`; batasi ke varian yang bisa dipilih pemain |
| `KHR_parallel_shader_compile` tidak ada di sebagian GPU | Jalur cadangan sinkron tetap di tahap muat dengan bar per program |
| Waktu SwiftShader tidak mewakili GPU asli | Keputusan besar (P5 opsi besar, P6) menunggu angka P0 dari GTX 1060 dan M1 |

## Batasan

- Semua angka berasal dari sandbox SwiftShader, satu kali jalan per experience. Lama jeda di GTX 1060 dan M1 belum diketahui; yang pasti adalah jumlah program dan kapan program dikompilasi.
- Pengaruh cache shader Chrome (muat ulang tanpa perubahan kode) belum diukur; dicatat di P0.
- Menu utama (`index.html`) dan halaman detail fisika (belum ada, baru bahan `docs/cooper-station/detail/fisika-coriolis.md`) tidak termasuk tahap ini, sesuai permintaan fokus experience.
