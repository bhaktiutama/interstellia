# Rencana VR: Dukungan VR PC (Oculus Rift CV1, GTX 1060)

Per 9 Oktober 2026 · Status: rencana, belum dikerjakan. Berlaku untuk Gargantua, Millar's World, dan Copper Corn Station (urutan pengerjaan sama dengan urutan ini).

## Ringkasan

- Jalur teknis: WebXR `immersive-vr` di browser PC (Chrome / Edge) lewat runtime Oculus (OpenXR). Dukungan Rift CV1 di software PC Meta dan di WebXR Chrome tidak lagi pasti (lihat Risiko), jadi tahap pertama adalah uji kelayakan perangkat dengan halaman kecil tanpa three.js, sebelum kode experience disentuh.
- Anggaran GPU ketat: Rift CV1 butuh sekitar 380 juta piksel per detik pada 90 Hz, kira-kira 3,06x desktop 1080p 60 fps (turunan di bawah). Tiap experience mendapat preset `VR` sendiri dan target 90 Hz dengan cadangan 45 Hz (ASW). Gargantua dikerjakan pertama karena adegannya praktis di tak hingga: ray tracer cukup dihitung sekali untuk kedua mata.
- Logika bersama di modul baru `shared/vr.js` (`window.VRKIT`, pola sama dengan `CAMKIT`): tombol masuk VR buatan sendiri (tanpa addon three.js), sesi, kontroler Touch, panel menu di dunia, setelan kenyamanan. Aturan kenyamanan wajib: kamera tidak pernah digerakkan tanpa kepala (gerak kepala `BOB`, guncangan, FOV lari, sinematik dimatikan atau diganti di VR).

## Context

Permintaan pemilik: dukungan VR dari PC dengan Oculus Rift CV1 dan kartu grafis GTX 1060.

### Perangkat

| Item | Nilai | Sumber |
| --- | --- | --- |
| Layar | 2 x OLED 1.080 x 1.200 per mata, 90 Hz | Spesifikasi pabrikan (pengetahuan umum, belum diukur) |
| Target render bawaan | Sekitar 1.332 x 1.586 per mata pada densitas piksel 1,0 | Angka umum SDK Oculus; dibaca pasti di VR0 dari `framebufferWidth` / `framebufferHeight` |
| Pelacakan | 6DoF kepala + 2 kontroler Touch (sensor Constellation) | Spesifikasi pabrikan |
| Cadangan frame | ASW: runtime menggambar frame sisipan bila aplikasi hanya mencapai 45 fps | Fitur runtime Oculus; berlaku untuk aplikasi WebXR belum diverifikasi (VR0) |
| GPU | GTX 1060, kelas spesifikasi rekomendasi Rift saat rilis | Pengetahuan umum |

### Anggaran piksel dan waktu (turunan)

| Kasus | Piksel per frame | Frame per detik | Piksel per detik | Rasio vs 1080p 60 | Waktu per frame |
| --- | --- | --- | --- | --- | --- |
| Desktop 1.920 x 1.080 | 2.073.600 | 60 | 124,4 juta | 1,00x | 16,7 ms |
| Rift CV1, 2 x 1.332 x 1.586 | 4.225.104 | 90 | 380,3 juta | 3,06x | 11,1 ms |
| Rift CV1 dengan ASW | 4.225.104 | 45 | 190,1 juta | 1,53x | 22,2 ms |

Target kerja: GPU paling lama 9 ms per frame di 90 Hz (sisa sekitar 2 ms untuk kompositor runtime; angka sisa ini perkiraan) atau 20 ms di 45 Hz. FPS desktop ketiga experience di GTX 1060 belum pernah diukur (dokumen tahap hanya mencatat "menunggu uji FPS"), jadi preset `VR` di bawah adalah titik awal, bukan hasil ukur.

### Kondisi kode (hasil telusur)

| Fakta | Lokasi | Dampak untuk VR |
| --- | --- | --- |
| Copper dan Millar: three.js 0.186.1, loop `requestAnimationFrame(frame)`, `worldStep()` terpisah dari render | Copper `frame()` dekat akhir file, Millar `frame()` | Loop VR wajib lewat `renderer.setAnimationLoop()` (frame XR datang dari sesi); `worldStep()` dipakai ulang apa adanya |
| Gargantua: WebGL2 mentah, `drawScene()` + `drawPost()`, sinar dari `uCamFwd` / `uCamRight` / `uCamUp` x `uTanHalf` (frustum simetris) | `SCENE_FS` baris `vec3 dir = ...`, `frame()` | Frustum mata XR tidak simetris: arah sinar harus dari invers matriks proyeksi per mata |
| Gargantua: satuan rs = 1, `RS_M` = 2,954e11 m | `MIS_T`, `RS_M` | Paralaks IPD 0,063 m pada jarak 1 rs = 0,063 / 2,954e11 = 2,1e-13 rad, nol secara praktis: lubang hitam dan piringan cukup dirender sekali untuk kedua mata. Hanya wahana GX-01 (raster, `drawShip()`) yang perlu stereo sungguhan |
| three.js 0.186.1 `WebXRManager`: memakai `XRProjectionLayer` bila browser punya `XRWebGLBinding.createProjectionLayer`, selain itu `XRWebGLLayer`; satu target sisi-ke-sisi (kedua mata berdampingan), multiview tidak dipakai bawaan; `setFramebufferScaleFactor`, `setFoveation`, `setReferenceSpaceType` ada | Dibaca dari `three.module.js` 0.186.1 | Skala resolusi VR = `setFramebufferScaleFactor` sebelum sesi. Foveasi hanya berpengaruh di browser Quest, bukan Chrome PC (perlu verifikasi) |
| three.js `render()`: selama presenting, kamera yang diberikan selalu diganti `ArrayCamera` XR (kecuali saat pass output bawaan) | `WebGLRenderer.render` | Pipeline post buatan sendiri (Copper `postBegin()` / `postEnd()`, Millar `postRender()`) tidak otomatis benar di VR; lihat Keputusan desain 2 |
| Copper: dua scene, `farScene` dalam 1 unit = 1.000 km dirender dengan `farCam` lalu `clearDepth()` | `frame()`, blok Saturnus | Bila `farCam` lewat jalur XR bawaan, gerak kepala 0,3 m menjadi 300 km di `farScene`. `farCam` per mata harus memakai rotasi kepala saja |
| Copper: kerangka berputar `scene.rotation.z = OMEGA * clock.sim`, arah kamera dari `lookBasis(up, tan)` | `updateCamera()`, `lookBasis()` | Rig VR = induk kamera dengan basis `lookBasis` tanpa pitch; pose kepala ditambahkan di atasnya |
| Ketiga experience: HUD, panel `, bantuan, peta = DOM | Semua file | DOM tidak terlihat di headset. Perlu panel kanvas di dunia (pola MFD kanvas Gargantua dan Millar sudah ada) |
| Ketiga experience: gerak kamera tanpa kepala: `BOB` / `headBob()`, `FLY.head`, `PORT.head`, guncangan `viewBasis()` Gargantua, FOV lari, `CINE`, tur Y | Banyak tempat | Sumber mual utama di VR, dimatikan di mode VR (aturan kenyamanan) |
| Tiap experience halaman terpisah | Aturan aplikasi | Pindah halaman mengakhiri sesi XR. Masuk VR diulang per experience (klik tombol di monitor) |

## Keputusan desain

1. Satu modul bersama `shared/vr.js` (`window.VRKIT`, skrip biasa, tanpa three.js, jalan dari file://): deteksi `navigator.xr.isSessionSupported('immersive-vr')`, tombol "Masuk VR" / "Enter VR" buatan sendiri (bukan addon `VRButton`), siklus sesi, ruang acuan `local` (duduk) bawaan dan `local-floor` opsional, pemetaan kontroler, setelan kenyamanan, teks dua bahasa di `STR` sendiri, setelan di localStorage `lazarus.vr`. Tiap experience memasang adaptor seperti `CAMKIT.init(A)`.
2. Jalur render per mata di Copper dan Millar, dipilih di VR1 dari dua calon:

| Calon | Cara | Kelebihan | Kekurangan |
| --- | --- | --- | --- |
| A. Sisi-ke-sisi | `ArrayCamera` three menggambar kedua mata ke target HDR selebar framebuffer XR; semua pass post dibuat sadar mata (UV dijepit per separuh, matriks proyeksi per mata) | Satu set target post, cocok dengan cara three | Semua shader layar ditulis ulang (GTAO, SSR, sunrays, TAA, kabut lampu, kamera): bocor antar mata di tepi tengah, matriks tunggal salah |
| B. Loop per mata (usulan) | `renderer.xr.enabled = false` selama pass mata; kamera mata diisi dari `XRView` (matriks proyeksi + transform) di bawah rig; rantai post lama dijalankan utuh per mata ke target seukuran satu mata; hasil LDR disalin ke viewport mata di framebuffer XR dengan `gl.blitFramebuffer` | Shader post lama tidak berubah; `farCam` per mata mudah (rotasi saja) | Draw call adegan 2x (sama dengan calon A, karena `ArrayCamera` WebGL juga menggambar per kamera); biaya tetap tiap pass post 2x; riwayat TAA / SSR perlu 2 set |

Kriteria pilih di VR1: gambar benar di kedua mata (tanpa garis tengah, tanpa paralaks salah), waktu GPU per frame di GTX 1060, jumlah baris shader yang berubah. Bila B terbukti tidak bisa menyalin ke framebuffer XR (mis. karena lapisan proyeksi), pakai `XRWebGLLayer` langsung (three memakainya bila `createProjectionLayer` tidak ada).

3. Kerja yang tidak bergantung mata dijalankan sekali per frame: simulasi `worldStep()`, peta bayangan (`shadowPass()`, `sunShadowPass()`, `updateShadow()`), cubemap langit dan Gargantua Millar (`updateSkyCube()`, `updateGCube()`), FFT laut (`updateOcean()`), riak, impostor pohon (`octStep()`). Di Gargantua: ray tracer sekali ke target "siklop" yang mencakup gabungan frustum kedua mata, lalu tiap mata mengambil sampel menurut arah sinarnya; wahana GX-01 digambar per mata.
4. Eksposur sama untuk kedua mata: meter (`ADAPT` Copper, `M_LUM` Millar, `AE` Gargantua) dihitung dari satu mata (kiri) lalu dipakai keduanya. Efek layar yang berbeda antar mata (butiran, noda lensa, vinyet, DOF, visor M6d, aberasi kromatik) dimatikan di VR karena menimbulkan persaingan binokular; bloom tetap.
5. Antialias VR: MSAA 4x di target adegan (Millar sudah punya `msaa` per preset), TAA mati (TAA di VR mudah berbayang saat kepala bergerak cepat; dicoba ulang di VR8 bila GPU masih longgar).
6. Proyeksi milik headset: FOV dari `CONFIG.fov`, FOV lari, FOV motor, dan lensa kamera K tidak berlaku di VR. Mode foto F dan kamera rangefinder K dimatikan di VR tahap ini.
7. Kenyamanan (aturan wajib di semua experience):

| Sumber gerak | Desktop | VR |
| --- | --- | --- |
| Gerak kepala langkah `BOB` / `headBob()` / `bobDrop()` | Ada | Mati (tubuh tetap melangkah, kamera tidak diayun) |
| Guncangan (Gargantua `viewBasis()`, Millar `BOB.shX` / `BOB.shY`, `FLY.head`, Copper `PORT.head`) | Ada | Dipindah ke dunia: kokpit / wahana yang bergetar, bukan kamera; amplitudo maks 30% |
| Belok dengan stik | Mouse halus | Belok patah 30 derajat (pilihan 15 / 30 / 45, atau halus) |
| Gerak maju dengan stik | Ada | Ada, dengan vinyet terowongan saat bergerak (pilihan Mati / Tipis / Kuat) |
| Sinematik Millar `CINE`, tur Copper Y, Millar tersapu `SWEEP` | Kamera skrip | Titik pandang tetap atau pindah dengan layar gelap sebentar (fade 0,3 s); tersapu = fade gelap lalu muncul di posisi baru |
| Motor Copper 150 km/h, terbang KS-07 | Ada | Ada, kokpit / setang sebagai kerangka acuan tetap, vinyet otomatis di atas 40 km/h |

8. Kontroler Touch (pemetaan `xr-standard` lewat `XRInputSource.gamepad`), keyboard tetap jalan:

| Kontrol Touch | Jalan kaki | Kendaraan (shuttle, motor, GX-01) | Setara tombol desktop |
| --- | --- | --- | --- |
| Stik kiri | Gerak (W A S D) | Gas / rem / samping sesuai kendaraan | W A S D |
| Stik kanan | Belok patah; tekan = lari | Arah hidung (ganti mouse) | Mouse, Shift |
| Picu kanan | Aksi | Aksi / dorong | E (Gargantua: E suar) |
| Genggam kanan | Ambil (Millar tahan E) | Boost | E tahan, Shift |
| A | Lompat | Tampilan berikut | Space, V |
| B | Kembali / batal | Keluar kendaraan | R, Esc |
| X | Panel menu VR | Panel menu VR | ` |
| Y | Pusatkan ulang pandangan | Pusatkan ulang | (baru) |
| Stik kiri ditekan | Peta / radar | Peta / radar | M |

Tombol khusus Copper tetap di keyboard dan panel menu VR; tidak ada fungsi umum baru yang memakai huruf Copper (aturan `docs/app/tombol.md`). Tombol Oculus milik sistem.

9. Panel menu VR: satu kanvas 2D di dunia (sekitar 1,0 x 0,6 m, 1,2 m di depan saat dibuka, dibidik dengan sinar kontroler kanan) berisi: preset, kenyamanan (belok, vinyet, tinggi duduk), suara, bahasa, pusatkan ulang, keluar VR, kembali ke menu. HUD penting (jam dilatasi Millar, data misi Gargantua, distrik Copper) ditampilkan di layar MFD / dasbor yang sudah ada atau di pergelangan tangan kiri.
10. Layar monitor saat VR: salinan mata kiri ke kanvas halaman (perlu verifikasi di VR0 apakah Chrome PC menampilkan kanvas biasa selama sesi; bila tidak, tampilkan teks "Sedang di VR").

## Tahap

| Tahap | Isi | File dan fungsi | Effort | Model | Thinking |
| --- | --- | --- | --- | --- | --- |
| VR0 | Uji kelayakan perangkat: halaman `docs/app/vr/uji-webxr.html` tanpa three.js (cek `isSessionSupported`, masuk sesi, warna berbeda per mata, kubus pelacakan kepala dan kontroler, tampil `framebufferWidth` / `Height`, FPS sesi, nama tombol gamepad yang ditekan). Pemilik mencoba di Chrome dan Edge dengan runtime Oculus aktif sebagai runtime OpenXR; cadangan SteamVR sebagai runtime OpenXR | Halaman uji baru | Low | Sonnet 5.5 | low |
| VR1 | Inti `shared/vr.js`: tombol, sesi, ruang acuan, kontroler (sinar, aksi), panel menu VR kanvas, setelan kenyamanan, kamus dua bahasa; prototipe jalur render calon A vs B di halaman uji three.js kecil (adegan + bloom + satu efek kedalaman), ukur di GTX 1060 | `shared/vr.js`, `docs/app/vr/uji-jalur-render.html` | High | Opus 5.5 | high |
| VR2 | Gargantua: sesi WebGL2 mentah (`xrCompatible`, `XRWebGLLayer`), sinar dari invers proyeksi per mata di `SCENE_FS` (uniform baru, jalur desktop identik), ray tracer siklop sekali per frame, `drawShip()` per mata dengan matriks XR, bloom dan `AE` sekali, guncangan pindah ke wahana, MFD / `#dash` sebagai bidang di kokpit, Touch untuk misi (dorong, suar, autopilot O, membidik tesseract) | `SCENE_FS`, `viewBasis()`, `drawScene()`, `drawShip()`, `drawPost()`, `frame()` | High | Opus 5.5 | xhigh (shader relativitas, rawan NaN di frustum tidak simetris) |
| VR3 | Millar: `setAnimationLoop`, jalur render pilihan VR1 di `postRender()`, kerja sekali per frame (langit, laut, bayangan), preset `VR`, jalan kaki dengan stik (inersia air `CONFIG.walk` tetap), kokpit KS-07 v5 duduk (tongkat dan tuas `COCKPIT` mengikuti kontroler), tubuh M6: kepala disembunyikan, badan mengikuti arah kepala, visor mati, `CINE` dan tersapu versi fade | `frame()`, `worldStep()`, `fpCamera()`, `flyCamera()`, `postRender()`, `PRESETS`, `BODY` | High | Opus 5.5 | high |
| VR4 | Copper: rig di kerangka berputar (`lookBasis()` tanpa pitch + pose kepala), `farCam` per mata rotasi saja, jalur render pilihan VR1 di `postBegin()` / `postEnd()`, preset `VR` (lihat tabel), lift dan hub nol-g (6DoF penuh, cocok untuk VR), trem, motor, kokpit shuttle duduk, peta M sebagai panel kanvas, tur Y dan foto F mati | `frame()`, `updateCamera()`, `lookBasis()`, `postBegin()`, `postEnd()`, `PRESETS`, `PRESET_HOOKS`, `motoCamera()`, `updateFlightCamera()` | High | Opus 5.5 | xhigh (kerangka berputar) |
| VR5 | Tangan dan interaksi: model tangan / kontroler sederhana, Millar lengan tubuh M6 mengikuti kontroler (`armReach()` sudah ada), ambil barang dengan genggam, tongkat kokpit digenggam | `shared/vr.js`, Millar `BODY`, `COCKPIT` | Medium | Sonnet 5.5 | medium |
| VR6 | Menu utama dan dokumen: lencana "VR" per experience di `index.html` (`FEATS` / `KEYS`), `docs/app/tombol.md` bagian VR, `CLAUDE.md`, bantuan ? ketiga experience | `index.html`, `docs/app/tombol.md`, `CLAUDE.md` | Low | Haiku 4.5 | low |
| VR7 | Uji otomatis `tools/uji_vr.py`: `navigator.xr` tiruan disuntik lewat Playwright (tanpa headset), masuk sesi, render dua mata tanpa nilai tidak valid, jalur desktop identik dengan sebelum VR (dibanding commit sebelum VR2), aturan kenyamanan (kamera = pose kepala persis saat jalan) | `tools/uji_vr.py` | Medium | Sonnet 5.5 | medium |
| VR8 | Penyetelan di GTX 1060 oleh pemilik: ukur waktu GPU per pass (`GPUT` Copper / Millar, timer query Gargantua) dan grafik kinerja Oculus Debug Tool; turunkan / naikkan preset `VR`, skala framebuffer, coba TAA per mata | Preset `VR` ketiga experience | Medium | Sonnet 5.5 | medium |

Urutan: VR0 harus lulus sebelum VR1. Gargantua lebih dulu karena paling murah dan duduk (tanpa gerak dengan stik). Commit dan push per tahap; pemilik menguji di Rift CV1 setelah VR0, VR2, VR3, VR4.

Rencana ini disusun pada tingkat satu di atas tahap terberat (VR2 dan VR4 High dengan thinking xhigh).

## Preset VR awal (perkiraan, diukur di VR8)

| Experience | Dasar | Ubahan untuk VR |
| --- | --- | --- |
| Gargantua | `medium` (steps 200, octaves 4) | Skala render dari `setFramebufferScaleFactor` 0,8; ray tracer siklop sekali per frame; partikel 900; V4 hidup; eksposur dari target siklop |
| Millar | `Sedang` (atau `Rendah` bila VR8 di bawah 45 fps) | MSAA 4x, tanpa TAA dan butiran, cubemap langit satu sisi per frame tetap, bayangan `SHD_SIZE` tingkat Sedang, cipratan dikurangi, visor mati |
| Copper | `Rendah` (`dpr` diabaikan, skala dari framebuffer) | Tanpa GTAO, SSR, interior jendela, impostor oktahedral, sunrays ray-march; bayangan sunline tetap tetapi peta dekat `SUNSH.near` mati; lalu lintas 0,35; MSAA 4x |

Prinsip turun: pertama skala framebuffer (1,0 -> 0,7), lalu preset, lalu 45 Hz (ASW). Tidak pernah memakai resolusi dinamis yang berubah tiap frame tanpa uji (berkedip lebih terasa di VR).

## Risiko

| Risiko | Kemungkinan | Dampak | Penanganan |
| --- | --- | --- | --- |
| Software PC Meta tidak lagi menyediakan pemasangan Rift CV1 (laporan pengguna 2025: pilihan CV1 hilang dari aplikasi, solusi pengguna = pilih Rift S lalu colok CV1) | Sedang, sumber hanya forum | Rift tidak bisa dipakai sama sekali | VR0 lebih dulu; cadangan SteamVR + runtime Oculus |
| WebXR Chrome tidak jalan dengan Rift (laporan 2024 di Windows 10; sebagian pengguna memakai flag Chrome untuk memaksa runtime) | Sedang | Tidak ada sesi WebXR | VR0 mencoba Chrome, Edge, flag runtime, dan SteamVR sebagai runtime OpenXR. Bila semua gagal, rencana berhenti di VR0 dan dicatat |
| Copper tidak mencapai 45 fps stereo di GTX 1060 walau preset `VR` | Tinggi (desktop belum diukur; beban piksel 1,53x-3,06x desktop 1080p) | VR Copper tidak nyaman | VR4 setelah VR2 dan VR3 memberi angka ukur; bila kurang, Copper VR dibatasi area (mis. hub, dek, kokpit shuttle) atau ditunda |
| ASW tidak berlaku untuk aplikasi WebXR | Belum diketahui | Frame terlewat = gambar tersendat, bukan disisipkan | Diperiksa di VR0 dengan Oculus Debug Tool; bila tidak ada, target menjadi 90 Hz murni dengan preset lebih rendah |
| Perubahan jalur render merusak tampilan desktop | Sedang | Melanggar "Pertahankan yang ada" | Semua cabang VR di belakang `VRKIT.on`; `tools/uji_vr.py` membandingkan render desktop dengan commit sebelum tahap |
| NaN di shader per mata (frustum tidak simetris, `normalize()` vektor nol) | Sedang | Titik putih berkedip lewat bloom | Aturan Catatan GPU `CLAUDE.md`; uji nilai tidak valid di VR7 |

## Verifikasi

- VR0: pemilik melaporkan masuk sesi ya / tidak per browser, resolusi framebuffer, FPS sesi, dan apakah kanvas monitor tetap tampil.
- Tiap tahap: `tools/qc_load.py` dan uji experience yang disentuh tetap lulus (`tools/uji_misi_gargantua.py`, `tools/uji_millar.py`, uji Copper terkait); `tools/uji_vr.py` lulus.
- Pemilik menguji di Rift CV1: kenyamanan (tidak mual 10 menit), FPS dari Oculus Debug Tool, gambar kedua mata cocok (tidak ada garis tengah atau mata berbeda terang).

## Batasan

- Spesifikasi Rift CV1 dan ASW berasal dari pengetahuan umum, belum diukur di perangkat pemilik.
- Status dukungan CV1 di software Meta dan WebXR Chrome per Oktober 2026 tidak terkonfirmasi sumber resmi; hanya laporan forum pengguna.
- Perkiraan anggaran (9 ms / 20 ms GPU, sisa 2 ms kompositor) dan preset `VR` belum diukur.
- Di luar cakupan: Quest lewat Link / Air Link (kemungkinan jalan dengan jalur yang sama, tidak diuji), headset lain, kamera rangefinder di dalam VR, mode foto VR, Jepang dan Mandarin.
