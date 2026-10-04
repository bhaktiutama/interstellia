# Rencana M6 Millar's World: Tubuh orang pertama (astronaut)

Per 4 Oktober 2026 · Status: M6a, M6a-2, dan M6b selesai, M6c-M6e belum. Butir 5 M5c (kaki dan lengan terlihat saat menunduk) dialihkan ke sini.

## Context

Pemilik meminta tubuh orang pertama di Millar's World, mengacu pada foto terlampir: astronaut berpakaian putih tebal berhelm, badan condong ke depan, lengan ditekuk di samping, kaki berjalan di air setinggi mata kaki sampai lutut, percikan di sekitar tulang kering, langit kelabu berkabut. Pengerjaan bertahap: low poly dulu untuk prototipe, lalu mendekati realisme dengan sumber daya minimum.

Kondisi saat ini (hasil telusur kode `experiences/millar/index.html`):

| Fakta | Lokasi |
| --- | --- |
| Tubuh hanya untuk bayangan: `SHD.body` (kotak, bola, silinder) di layer 3, `colorWrite:false`, kamera utama hanya melihat layer 0 | L1606-1626 |
| `updateShadow()` menaruh tubuh di `seabed(P.x, P.z)` (tidak ikut lompat), tampil bila `P.view===0 && !FLY.on && !CINE.on && !SWEEP.on`, ayun kaki dari `BOB.phase` dan `BOB.amp` | L1628-1647 |
| `P.y` = tinggi mata, `CONFIG.eye` 1,7 m, near plane 0,1 m, FOV 70, pitch dibatasi 1,45 rad | L1678, L173, L340, L1831 |
| Air sudah menusuk kaki secara fisik: `footstep()` (kaki di `P + kanan*0,13 + maju*0,45`), `headBob()` (semburan tulang kering, riak V), kedalaman istirahat 0,5-0,85 m (setinggi paha) | L1869-1904 |
| Laut opak, tanpa pantulan planar; kaki yang terendam cukup dipotong uji kedalaman | L1135 |
| Material wahana `shipMat` (vertex color, `uWater` garis basah, cahaya Gargantua, bayangan, kabut) bisa jadi patokan; `uWater` wahana bersama, tubuh butuh salinan sendiri | L1524-1566 |
| Geometri vertex color + `KESTREL.mergeColored(THREE, parts)` sudah dipakai wahana dan pecahan | `shared/kestrel.js:13`, L2084-2091 |
| Tidak ada geometri manusia di `shared/kestrel.js`; rencana M5c butir 5 (`rencana-m5-millar.md:77`) hanya menyebut "kaki dan lengan terlihat saat menunduk" sebagai opsional | - |

Keputusan desain:

1. Satu kelompok tubuh bersama untuk tampilan dan bayangan (layer 0 + 3), menggantikan `SHD.body` yang hanya bayangan. Pose bayangan dan tampilan tidak boleh berbeda.
2. Material sendiri turunan `shipMat` (`makeSuitMat()` dengan `uWater` dan `uMatte` sendiri), bukan MeshLambert, supaya cahaya Gargantua, kabut, dan suasana (`MOOD`) ikut otomatis.
3. Kepala dan helm tidak dirender oleh kamera orang pertama (kamera ada di dalam kepala, near 0,1 m). Mesh kepala punya layer sendiri: saat `P.view===0` hanya layer 3 (bayangan), saat tampilan drone 60 m / 1,5 km (V) layer 0 + 3 sehingga tubuh utuh terlihat dari atas.
4. Tubuh mengikuti `P.x, P.z, P.yaw` (stabil), bukan offset goyang kamera (`BOB.dx`). Kaki mendarat di titik yang sama dengan `footstep()`, supaya riak dan percikan keluar dari kaki yang terlihat.
5. Desain pakaian orisinal (putih kusam, aksen jingga, ransel tipis, helm bulat). Tidak meniru pakaian film; foto hanya acuan suasana (postur, air setinggi lutut, percikan). Foto tidak dimasukkan ke repo (aturan CLAUDE.md: tanpa cuplikan film).
6. Tombol baru tidak dipakai: semua huruf sudah terpakai (`docs/app/tombol.md`). Pengaturan "Tubuh" masuk panel kontrol (`) sebagai baris LAB baru **di akhir** daftar (uji `uji_millar.py:275` mengharuskan indeks 4 = gerak kepala), tersimpan di `localStorage millar.body`, pola `cycleBob()`.
7. Anggaran: M6a 300-450 segitiga, M6d paling banyak 3.000 segitiga, Hemat paling banyak 600; satu draw call tubuh + satu visor.

## Kelompok menurut effort dan model

| Tahap | Isi | Effort | Model | Alasan | Risiko |
| --- | --- | --- | --- | --- | --- |
| M6a | Prototipe low poly: tubuh tampil saat menunduk, panel Tubuh, uji dasar | Medium | Sonnet 5.5 | Geometri baru, bahan turunan, layer; banyak titik sambung tapi lokal | Sedang |
| M6b | Gerak: langkah, lengan, lompat, condong, selaras riak dan percikan | Medium | Sonnet 5.5 | Mengikuti `BOB` dan `footstep()` yang sudah ada | Rendah |
| M6c | Bayangan sendiri tanpa artefak, garis basah, busa di garis air | High | Opus 5.5 | Shader dan peta bayangan Gargantua: tubuh menerima bayangan dari peta yang memuat dirinya (self-shadow) | Tinggi |
| M6d | Helm: bingkai visor, pantulan, uap napas, tetes air | Medium | Sonnet 5.5 | Lapisan layar atau cangkang BackSide, tidak menyentuh pipa cahaya | Sedang |
| M6e | Menuju realistis: detail pakaian, LOD per preset, kotor basah, kokpit | Medium | Sonnet 5.5 | Detail berbasis vertex color, tanpa tekstur besar | Rendah |
| Mekanis | Entri `I18N.en`, teks panel dan bantuan, dokumen, `CLAUDE.md`, `rencana-m5-millar.md` | Low | Haiku 4.5 | Langkah mekanis dari tiap tahap | Rendah |

Rencana ini disusun oleh model satu tingkat di atas tahap terberat (M6c High). Tahap dikerjakan berurutan; commit dan push per tahap.

## M6a. Prototipe low poly (Medium)

**Tujuan:** saat pemain menunduk, terlihat dada, perut, paha, tulang kering, sepatu dan sebagian lengan; di air, kaki terendam terpotong permukaan laut.

**Bentuk (satuan m, asal di telapak kaki, +y atas, -z depan, tinggi total 1,78 m dengan mata di 1,70):**

| Bagian | Bentuk | Ukuran | Segitiga |
| --- | --- | --- | --- |
| Badan | kotak membulat 8 sisi | 0,42 x 0,60 x 0,26, y 1,10-1,50 | 60 |
| Ransel | kotak | 0,36 x 0,50 x 0,18, di punggung | 12 |
| Paha dan betis (x2) | silinder 6 sisi, dua ruas | r 0,085 / 0,065, panjang 0,45 + 0,45, sendi lutut | 2 x 48 |
| Sepatu (x2) | kotak | 0,13 x 0,10 x 0,30 | 2 x 12 |
| Lengan atas dan bawah (x2) | silinder 6 sisi, siku ditekuk | r 0,055 / 0,045, 0,30 + 0,28 | 2 x 48 |
| Sarung tangan (x2) | kotak | 0,09 x 0,06 x 0,14 | 2 x 12 |
| Kepala dan helm | bola 10 x 8, layer terpisah | r 0,15 di y 1,68 | 160 |

Warna vertex: putih kusam `[0.30,0.30,0.29]` (palet wahana), aksen jingga `[0.45,0.20,0.07]` di bahu dan sabuk, sepatu abu gelap.

**Langkah:**

1. `buildBody(THREE)` baru: tiap bagian sebagai `Mesh` terpisah (pivot sendi) memakai `KESTREL.mergeColored` per bagian; grup `BODY.group`. Letakkan di `experiences/millar/index.html` dekat blok `SHD` (L1606), sebab kode kecil dan khusus Millar; angkat ke `shared/` hanya bila Copper memakai.
2. `makeSuitMat()`: salin vertex dan fragment `shipMat` (L1526-1566), uniform `{...shipU, uWater:{value:0}, uMatte:{value:1}}`.
3. `updateBody()` dipanggil di samping `updateShadow()`: posisi `(P.x, max(seabed, P.y - CONFIG.eye), P.z)`, `rotation.y = P.yaw`, kepala diatur layer menurut `P.view`. Tampil bila `BODY.level>0 && P.view===0 && !FLY.on && !CINE.on && !SWEEP.on` (kondisi sama dengan L1638); tampilan V tetap tampil.
4. Geser badan 0,10 m ke belakang dari sumbu mata supaya dada tidak memotong near plane; uji pitch -90 derajat.
5. Hapus pembuatan `SHD.body`; `updateShadow()` memakai `BODY.group` (layer 0 + 3 kecuali kepala di pass bayangan tetap ikut).
6. Panel: `BODY.level` Mati / Bayangan / Tampil (default Tampil), `cycleBody()` mengikuti `cycleBob()` (L1720), baris LAB baru di akhir, `localStorage millar.body`, entri `I18N.en`, baris bantuan `buildHelp()`, ekspor `BODY`, `cycleBody`, `updateBody` di `window.__millar` (L2883).

**Uji baru (blok 5m di `tools/uji_millar.py`, setelah blok 5l):** segitiga tubuh <= 450 dan <= 600 di Hemat; semua posisi dan normal terbatas (pola L212-217); tidak ada NaN atau titik > 50 di `POST.hdr` (pola L248-251); menunduk (pitch -70 derajat) selisih piksel tubuh Tampil vs Mati > 1,5% area, menatap horizon (pitch 4 derajat) selisih = 0; tubuh tersembunyi saat `FLY.on`, `CINE.on`, `SWEEP.on`; kepala tidak di layer 0 saat `P.view===0`, di layer 0 saat `P.view===1`; bayangan tetap ada (jumlah piksel peta bayangan SHD > 0); LAB indeks 4 tetap gerak kepala.

## M6b. Gerak dan selaras air (Medium)

1. Ayun kaki dan lengan dari `BOB.phase`, `BOB.amp` (rumus `updateShadow` L1640-1642 dipindah ke `updateBody()`), tambah lutut menekuk (betis tertinggal 40%) dan siku ditekuk makin dalam saat lari (`BOB.run`).
2. Titik telapak kaki sama dengan sumber riak `footstep()` (`P + kanan*CONFIG.walk.legs*sd + maju*0,45`); ekspor `bodyFootAt(side)` dan jadikan sumber tunggal bagi `footstep()` dan `headBob()` agar percikan keluar dari sepatu yang terlihat.
3. Lompat: tubuh naik mengikuti `P.y`, kaki ditekuk saat di udara, pegas mendarat `BOB.y/vy`.
4. Condong badan 6-10 derajat ke depan saat melangkah di air dalam (foto: postur condong) dan mengikuti pitch menunduk (tulang belakang) sampai 20 derajat.
5. Yaw badan tertinggal pada belok cepat (maks 25 derajat, kembali 0,25 s) supaya tubuh terasa punya massa.

**Uji baru:** jarak sepatu terhadap titik `footstep` < 0,05 m; kaki kiri dan kanan berlawanan fase; ayun nol saat diam; badan ikut `P.y - CONFIG.eye` saat lompat (galat < 0,02 m); tidak ada nilai tidak valid saat 600 langkah simulasi (`stepPlayer`).

## M6c. Cahaya, bayangan, garis basah (High)

**Masalah:** peta bayangan Gargantua (`SHD`, layer 3) memuat tubuh itu sendiri, sehingga tubuh yang menerima `shadowAt(vW + n*bias, ...)` menggelapkan dirinya (jerawat bayangan).

**Perbaikan:**
1. Bias normal lebih besar untuk material tubuh (`shadowAt(w, biasM)` sudah menerima parameter bias, L444-457); uji 0,25-0,40 m terhadap jerawat.
2. Tubuh menerima bayangan wahana dan gelombang tetapi tidak dirinya sendiri: pecah bagian "penerima" (hanya ujung kaki dan sepatu menerima bayangan tubuh, badan tidak).
3. `uWater` tubuh = `waterHere(STATE.visT)` tiap frame; garis basah di paha menggelap dan mengkilap (sama dengan wahana).
4. Cincin busa di garis air pada tiap kaki: pita mendatar kecil (2 x 8 segitiga, tanpa tekstur) di permukaan air, berskala dengan kecepatan; memakai `waterHere()`.
5. Kabut dan ambient mengikuti `MOOD` (Mendung, Senja) otomatis dari `uAmb`, `uShK`; uji tiga suasana.

**Uji baru:** luminans rata-rata badan di bawah sinar vs bayangan berbeda > 20%; tidak ada jerawat (varians luminans pada badan < ambang); NaN nol di 5 preset (`applyPreset(i)`, pola L457-464) dan di Hemat; `normalize()` tidak pernah pada vektor nol (aturan CLAUDE.md untuk Apple M1).

## M6d. Helm dan visor (Medium)

1. Bingkai visor: lapisan layar (CSS atau kanvas) tipis di tepi pandangan, melengkung, redup di tepi, tanpa menutup tengah.
2. Pantulan visor: kilau tipis dari `skyL` pada tepi atas bila menghadap Gargantua (uniform arah sudah ada di `U`).
3. Uap napas: embun halus yang mengembang saat berlari, hilang saat diam (alfa maks 0,12).
4. Tetes air di visor setelah cipratan besar atau sapuan (`SWEEP`, `sfxSplash`), mengering 6-10 detik.
5. Napas dan getar suit di audio (`AUDIO` disintesis, mengikuti tombol U).
6. Pengaturan di panel: Visor Mati / Tipis / Penuh, `localStorage millar.visor`.

**Uji baru:** piksel tengah layar tidak berubah oleh visor (selisih < 0,5%); visor mati saat `FLY.on`, `CINE.on`, mode foto (F); alfa embun <= 0,12.

## M6e. Menuju realistis dengan sumber daya minimum (Medium)

| Item | Cara | Biaya |
| --- | --- | --- |
| Detail pakaian | sambungan, selang, panel dada, ransel berbentuk lebih rinci, semua vertex color | +1.500 segitiga |
| Kotor dan basah | warna vertex diperkotor oleh tinggi (paha lebih gelap), jelaga ringan seperti wahana | 0 (hitung saat bangun) |
| LOD per preset | `PRESETS.bodyDetail` 0 / 1 / 2 (Hemat 0: 450, Rendah 1: 1.200, Sedang ke atas 2: 3.000) | satu draw call |
| Kokpit | pilot terlihat dari tampilan belakang V (FLY) dan lengan di tongkat dan tuas (`stickAt`, `throttleAt` dari `buildCockpitV5`) | +400 segitiga |
| Tangga dan pintu | lengan menjangkau tangga saat E di tangga (`missionAction()`) dan saat ambil blackbox tahan E | animasi saja |
| Tersapu | tubuh jatuh berputar saat `SWEEP.on` (kamera tetap), opsional | rendah |

**Uji baru:** jumlah segitiga per preset di bawah anggaran; waktu `updateBody()` < 0,1 ms rata-rata di 600 frame; FPS Hemat tidak turun lebih dari 3% dibanding Mati.

## Yang tidak dikerjakan

| Item | Alasan |
| --- | --- |
| Tekstur peta besar atau PBR penuh | Melanggar anggaran sumber daya; vertex color cukup |
| Model GLB pihak ketiga | Perlu skrip olah dan kredit lisensi; desain orisinal lebih aman |
| Replika pakaian atau helm film | Aturan hak cipta proyek |
| Cermin tubuh di permukaan laut | Laut tanpa pantulan planar; biaya tinggi |
| Tombol keyboard baru | Semua huruf terpakai; cukup panel kontrol |

## File utama

| File | Tahap |
| --- | --- |
| `experiences/millar/index.html`: `SHD` (L1606), `updateShadow()` (L1628), `shipMat` (L1526), `footstep()` / `headBob()` (L1869), `cycleBob()` (L1720), `LAB` (L1742), `buildHelp()` (L1763), `I18N.en` (L256), `window.__millar` (L2883), `PRESETS` (L214) | M6a-M6e |
| `shared/kestrel.js`: `mergeColored`, `buildCockpitV5` | M6a, M6e |
| `tools/uji_millar.py` (blok 5m baru; blok 6 tambah tubuh per preset) | semua |
| `docs/millar/rencana-m5-millar.md` (butir 5 di M5c dialihkan ke M6) | dokumentasi |
| `CLAUDE.md` (baris Millar: `BODY`, `updateBody()`, `cycleBody()`, `makeSuitMat()`; tidak lagi `SHD.body`) | dokumentasi |
| `docs/app/tombol.md` (catatan: Tubuh hanya di panel) | dokumentasi |

## Verifikasi

```
CHROMIUM=/opt/pw-browsers/chromium THREE_LOCAL=<scratchpad> python3 tools/uji_millar.py
python3 tools/uji_bahasa.py
python3 tools/qc_load.py
```

Uji Millar sekarang 72 pemeriksaan; semua harus tetap lulus dan blok 5m menambah pemeriksaan di atas. Tangkapan layar terbatas: satu menunduk, satu horizon, satu tampilan V per tahap (aturan CLAUDE.md: jangan berulang). Pemilik menguji visual dan FPS di GTX 1060 dan MacBook M1; sandbox SwiftShader tidak memperlihatkan NaN atau jerawat bayangan GPU, jadi M6c wajib diuji pemilik.

## Status

| Tahap | Status |
| --- | --- |
| M6a | Selesai 4 Oktober 2026 (lihat catatan di bawah) |
| M6a-2 | Selesai 4 Oktober 2026 (revisi setelah uji pemilik, lihat bagian di bawah) |
| M6b | Selesai 4 Oktober 2026 (lihat bagian di bawah) |
| M6c | Belum |
| M6d | Belum |
| M6e | Belum |

## Catatan M6a (selesai 4 Oktober 2026)

| Hal | Hasil |
| --- | --- |
| Segitiga | 416 (anggaran 450), 10 mesh, satu material, nilai tidak valid 0 |
| Tubuh terlihat | menunduk 70 derajat: 44-67% piksel berbeda dari Mati; horizon: 0% |
| Lapisan | kepala di layer 3 saja (orang pertama), layer 0 + 3 di drone; badan 0 + 3; mode Bayangan layer 3 saja |
| Tersembunyi | saat terbang, sinematik, tersapu, dan Mati |
| Kaki | telapak di dasar laut (0,000 m), ikut lompat (1,200 m dari 1,2 m); `uWater` tubuh = `waterHere()` |
| Panel | baris Tubuh di akhir `LAB`, gerak kepala tetap indeks 4, tersimpan di `millar.body` |
| Uji Millar | 78 pemeriksaan lulus (blok 5m baru) |

Penyimpangan dari rencana: dada digeser jadi 0,40 x 0,50 x 0,28 m (depan 0,11 m di depan mata, atas di y 1,45) agar terlihat mulai menunduk sekitar 55 derajat. Kaki dan lengan baru terlihat di tepi saat berjalan; posisi telapak 0,45 m di depan (selaras `footstep()`) dikerjakan di M6b. Bias bayangan tubuh sementara 0,3 m / 0,4 (lebih besar dari wahana), penyetelan benar di M6c. Uji `bayangan Gargantua` (5l) tipis ambangnya (5-11% lebih gelap per jalan, ambang 7%), sudah ada sebelum M6a; di 5l tubuh dimatikan agar terisolasi.

## Revisi M6a-2 (selesai 4 Oktober 2026): tubuh terbaca sebagai manusia

Uji pemilik atas M6a: dada berupa lempengan datar (45-67% layar), tanpa kaki, perut, dan tangan, hitam keabuan, pose sama untuk semua keadaan. Acuan pose: pandangan orang pertama menunduk (perut, paha, kaki di depan, tangan di sudut) dan lari (tangan ke sisi). Hanya pose dan komposisi yang diacu; gambar tidak disimpan di repo.

| Perubahan | Isi |
| --- | --- |
| Proporsi | Badan loft elips 8 sisi (dada di belakang atau tepat di bawah mata, perut dan pinggul mencuat), ransel, sabuk, pinggul z -0,04, kaki di depan saat menunduk, lengan dengan manset dan tangan jingga, sepatu dengan pergelangan (telapak tetap mendatar), anggota badan tertutup di ujung |
| Warna | Putih suit `[0.74,0.74,0.72]`, kain dalam abu-abu, aksen jingga (sebelumnya putih 0,30: hitam keabuan) |
| Pose `bodyPose()` | Menunduk (`dn` dari `P.pitch`), langkah (`BOB.phase`, `BOB.amp`), lari (`BOB.run` baru), udara; semua parameter di `CONFIG.body`; peredaman 0,12 s; pinggul turun mengikuti kaki yang paling terulur agar kaki menapak |
| FOV lari | +6 derajat (`CONFIG.walk.fovRun`), kembali tepat 70 saat diam; `BOB.run` dibulatkan ke 0 di bawah 0,004 |

| Uji | Hasil |
| --- | --- |
| Segitiga | 624 (batas 650) |
| Menunduk 60 derajat | 18,9% piksel beda dari Mati (5-40%), terang rata-rata 0,187 (> 0,12), kedua sepatu dan tangan di bingkai, horizon 0% |
| Lari | kaki beda z 1,47 m (> 0,8), tangan 0,32 m dari sumbu (> 0,30), salah satu tangan di bingkai |
| Udara | tangan 0,55 m dari sumbu (> 0,45) |
| Pose halus | perubahan sendi terbesar 0,316 rad per frame (< 0,35) |
| FOV | lari 75,9-76,0, diam 70,000 |
| Uji Millar | 81 pemeriksaan |

Keterbatasan: sepatu terlihat memendek karena sudut pandang dari atas (perspektif), ujung jingga baru jelas saat melangkah; tangan belakang saat lari keluar dari bingkai (wajar, satu tangan terlihat). Anggaran Hemat 600 segitiga belum dipenuhi (624), diselesaikan lewat LOD di M6e. Uji `bayangan Gargantua` (5l) tetap tipis ambangnya dan gagal sesekali, bukan karena tubuh (tubuh dimatikan di blok itu). Dari M6b, ayun gerak, lutut, lompat, dan condong sudah masuk di sini; sisanya: sumber riak ke telapak, yaw badan tertinggal, busa garis air.

## Gabungan dengan main (4 Oktober 2026)

Cabang M6 digabung dengan `main` (kepala `9dabedb`) yang sudah memuat M5 kelompok 1-3 (pusat laut = kamera, suara langkah diseret, plasma mengikuti wahana, pola laut dari ketinggian, percikan lari dengan mahkota air tiap langkah, gelombang tembok). Konflik hanya di `CLAUDE.md` dan satu baris kamus `I18N.en`, keduanya diselesaikan dengan mempertahankan kedua sisi. Uji Millar gabungan: 87 pemeriksaan lulus.

Catatan untuk M6b: `footstep()` baru (M5c) menaruh percikan, riak, dan mahkota air 0,15 m di depan titik tengah (`P + kanan * CONFIG.walk.legs * sd + maju * 0,15`), bukan 0,45 m. Telapak `BODY.feet` saat menunduk ada di sekitar 0,3-0,5 m di depan. Penyelarasan M6b harus menyatukan keduanya: satu fungsi `bodyFootAt(side)` sebagai sumber bagi `footstep()`, `headBob()`, dan telapak yang terlihat.

## M6b (selesai 4 Oktober 2026): percikan keluar dari sepatu yang terlihat

| Perubahan | Isi |
| --- | --- |
| Satu sumber posisi kaki | `bodyLegs()` (sudut paha, lutut, turun pinggul dari `BODY.pose`, `BOB`, `CONFIG.body`), `bodyFootAt(sd)` (pusat sepatu di dunia), `bodyLegAt(sd, depth)` (titik kaki memotong muka air); dipakai `bodyPose()`, `footstep()`, dan `headBob()` (tonjolan haluan, cekung belakang, semburan tulang kering) |
| Fase sinkron | Ayun kaki `sd * cos(BOB.phase)`: kaki yang menapak saat fase melewati kelipatan pi = kaki terdepan. Mendarat tidak lagi membalik `BOB.side`; air dangkal (< 0,05 m) tetap membalik agar irama tidak bergeser |
| Jangkauan telapak | `CONFIG.body.reachWalk` 0,25 m dan `reachRun` 0,45 m (sudut paha dari `asin(reach / 0,9)`); sebelumnya 0,5 m saat jalan |
| Yaw badan | `BODY.yaw` mengejar `P.yaw` dengan konstanta 0,25 s, tertinggal paling banyak 0,44 rad (25 derajat) |
| Pose tetap dihitung | `updateBody()` menghitung pose sebelum cabang visible, jadi percikan tidak bergantung pada pilihan panel Tubuh |

| Uji (blok 5n) | Hasil |
| --- | --- |
| Pusat sepatu vs `bodyFootAt` (6 fase x tegak / menunduk x 2 kaki) | selisih terbesar 0,002 m (< 0,08) |
| Fase langkah | 12 dari 12 persilangan: kaki yang menapak = kaki terdepan (air dalam, setelah mendarat, air dangkal) |
| Mendarat | `BOB.side` tetap, langkah +1 |
| Jangkauan | jalan 0,350 m, lari 0,551 m (reach + ujung sepatu 0,07 m) |
| Titik kaki di air | tepat 50,0% dari telapak ke pinggul pada kedalaman 0,45 m |
| Yaw tertinggal | 0,44 rad lalu 0,001 rad setelah 1,5 s |
| Uji Millar | 94 pemeriksaan lulus (uji M5c disesuaikan: titik tonjolan dan semburan memakai kaki yang terlihat) |

Dampak yang diterima: saat menunduk (`dn` 1) sepatu terlihat sekitar 0,5 m di depan dan percikan keluar di sana; saat menatap lurus sekitar 0,3 m (reach 0,25 m + ujung sepatu). Busa garis air tidak dibuat terpisah (cincin buih M5c sudah ada); dipertimbangkan ulang di M6c bila masih kurang.

