# Rencana M6 Millar's World: Tubuh orang pertama (astronaut)

Per 4 Oktober 2026 · Status: M6a sampai M6f selesai (M6e sebagian, lihat bagian M6e di bawah). Butir 5 M5c (kaki dan lengan terlihat saat menunduk) dialihkan ke sini.

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
| Sambungan anggota badan (masukan pemilik setelah M6d) | kaki dan lengan tidak terlihat terputus: bahu, siku, pinggul, lutut, pergelangan disambung (bola sendi atau selongsong yang saling masuk, atau satu mesh berkulit sederhana) | +100 sampai +300 segitiga |
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
| M6c | Selesai 4 Oktober 2026, menunggu uji pemilik di GPU (lihat bagian di bawah) |
| M6d | Selesai 4 Oktober 2026 (lihat bagian di bawah) |
| M6d-2 | Selesai 4 Oktober 2026 (revisi sudut pandang setelah uji pemilik, lihat bagian di bawah) |
| M6e | Selesai 4 Oktober 2026, sebagian (tangga dan tersapu ditunda, lihat bagian di bawah) |
| M6f | Selesai 4 Oktober 2026: pakaian satu mesh berkulit (lihat bagian di bawah) |

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

## M6c (selesai 4 Oktober 2026): bayangan tubuh, basah yang ingat, busa garis air

Keputusan: tubuh tidak membayangi dirinya sendiri. Peta bayangan Gargantua 96 m berarti 4,7 cm per texel (Ultra) sampai 19 cm (Hemat), sedangkan paha dan lengan 12-18 cm, jadi bayangan diri hanya berupa jerawat dan bercak. Bentuk tubuh tetap terbaca dari arah cahaya (sisi yang membelakangi Gargantua gelap).

| Perubahan | Isi |
| --- | --- |
| Bayangan tubuh | `shadowBody()` di fragment `bodyMat`: salinan `shadowAt()` (sampel, tepi, kelembutan sama); tiap sampel merekonstruksi posisi dunia penghalang lewat `bodyU.uShMI` (invers `uShM`, diisi di `updateShadow()`), penghalang di dalam kapsul tubuh (sumbu tegak 1,8 m dari telapak, radius `CONFIG.body.selfR` 0,7 m) diabaikan. Bias kembali seperti wahana (0,1 / 0,15, sebelumnya sementara 0,3 / 0,4), jadi tepi bayangan wahana di tubuh tepat |
| Fragment aman | `bodyMat` dibangun dengan `swapGL()` yang melempar error bila teks `shipMat` yang ditukar berubah (dulu `replace` bisa gagal diam-diam) |
| Basah yang ingat | `BODY.wetH` (m di atas telapak) naik seketika ke muka air + cipratan (jalan +0,12 m `wetWalk`, lari +0,30 m `wetRun`), kering 0,01 m/s (`dryRate`, sekitar 50 s), tersapu = seluruh tubuh basah; batas bergerigi dari noise koordinat lokal tubuh. Dekat muka air tetap paling basah. Sebelumnya basah ikut muka air dunia: saat lompat kaki langsung kering |
| Busa garis air | Di shader laut dekat (bukan geometri, jadi menempel di permukaan ombak yang terlihat): cincin di sekitar dua titik `bodyLegAt(sd, kedalaman)`, tepi dalam di dalam kaki (tanpa celah air), lebar 4 cm diam sampai 15 cm lari, menumpuk di depan arah gerak. Hanya saat Tubuh Tampil, menapak, kedalaman 0,05-0,95 m (pudar 0,85-0,95); `uLegs`, `uLegK`, `uLegV`, peredaman 0,15 s `BODY.foamK`, pengali `CONFIG.body.foam` |
| Alat banding | `BODY.cast` false = tubuh tidak masuk peta bayangan (untuk uji) |

| Uji (blok 5p dan blok 6) | Hasil |
| --- | --- |
| `uShMI x uShM` | identitas, galat 5,7e-14 |
| Tanpa bayangan diri (piksel tubuh, tubuh di peta bayangan vs tidak) | beda 0,00% (masker 11,0%) |
| Bayangan KS-07 jatuh di tubuh | 24,6% lebih gelap (> 20%) |
| Basah (kedalaman 0,66 m) | diam 0,66, lari 1,08, lompat 1 s turun 0,010 m, 60 s kembali 0,66, tersapu 2,0 |
| Busa | titik = `bodyLegAt` (selisih 0), kekuatan 1 di air, 0 saat Mati / udara / terbang; render 3,35% piksel beda |
| NaN dan titik > 50, tubuh menunduk, 5 preset x 3 suasana | 0 |
| Uji Millar | 105 pemeriksaan lulus |

Uji M5c (percikan menyatu) sempat gagal sekali dengan tonjolan -200 mm (batas jepit riak): sisa riak uji lari sebelumnya. Blok itu kini mengosongkan grid riak dulu (`makeRipple()` diekspor). Satu tangkapan layar menunduk di air: cincin busa putih terlihat di garis air kedua paha.

Batasan: bagian wahana yang lebih dekat dari 0,7 m ke sumbu tubuh (mis. batang kaki pendarat) tidak membayangi tubuh; bayangan lengan di badan tidak ada.

Wajib dicek pemilik di GTX 1060 dan M1 (SwiftShader tidak memperlihatkan): tubuh tidak berkedip atau bergaris saat berjalan di bawah dan di samping KS-07; tidak ada titik putih; cincin busa menempel di kaki saat ombak (Ultra FFT dan Hemat Gerstner); garis basah turun pelan setelah lompat atau lari.

## M6d (selesai 4 Oktober 2026): helm dan visor

Semua efek visor ada di pass komposit `M_COMP` yang sudah ada (tanpa render target baru). Visor aktif hanya saat berjalan kaki orang pertama; mati saat terbang, sinematik, mode foto, dan tampilan drone (uniform `uVis` = 0, blok dilewati).

| Bagian | Isi |
| --- | --- |
| Bingkai | Superelips gelap di tepi. Tipis (bawaan) = hanya sudut; Penuh = bingkai helm jelas dengan garis tepi dalam terang tipis. Tengah layar tidak tersentuh |
| Kilau | Busur hangat tipis di tepi atas saat menghadap Gargantua (kuat 0,35 x cerah), di posisi x Gargantua di layar |
| Embun napas | Gumpalan di bawah tengah, alfa paling tinggi 0,12 (`CONFIG.visor.fogMax`), menebal saat hembusan; lelah `VISOR.ex` naik saat lari (6 s), hilang saat diam lama |
| Tetes air | Lensa kecil yang membalik gambar (sampel `tHdr` dibiaskan), tepi gelap dan titik kilap, jarang di tengah; dari `footstep()` (mendarat di air > 0,3 m: +0,3; lari di air > 0,2 m: kadang +0,06 x tenaga) dan tersapu (= 1); kering linear dalam 8 s, pola baru tiap basah dari kering |
| Suara | Napas pink noise bandpass (hembus 700 Hz lebih keras, tarik 1.400 Hz lebih pelan, fase sama dengan embun) dan dengung suit 92 + 184 Hz, langsung ke master (di dalam helm, tidak diredam bawah air), ikut U dan Visor Mati |
| Panel | Baris Visor (Mati / Tipis / Penuh) sebelum baris Tubuh, `millar.visor`; tanpa tombol baru |

| Uji (blok 5q) | Hasil |
| --- | --- |
| Tengah layar Penuh vs Mati | 0,00% piksel beda; sudut 100% |
| Mati saat terbang / sinematik / foto / drone | `uVis` 0 / 0 / 0 / 0 |
| Embun | lari 20 s maksimum 0,115; diam 30 s 0,0007 |
| Tetes | mendarat 0,30; kering dalam 9 s; tersapu 1,00; render basah 2,2% piksel beda |
| Kilau | menghadap Gargantua 0,35, membelakangi 0 |
| Napas dan suit | simpul audio ada |
| Uji Millar | 112 pemeriksaan lulus |

Satu tangkapan layar (Penuh, lari, basah): bingkai helm dan tetes yang membiaskan laut terlihat; embun belum tampak karena baru 4 s berlari.

Batasan: keluaran `M_COMP` 8 bit, jadi NaN di blok visor tidak terdeteksi uji; dijaga aturan GLSL (tanpa `normalize`, `pow` hanya dari nilai >= 0). Wajib dicek pemilik: tepi bingkai tanpa garis atau titik putih di GTX 1060 dan M1, tetes tidak menurunkan FPS, keras napas pas.

## M6d-2 (selesai 4 Oktober 2026): sudut pandang tubuh (High)

Masukan pemilik: saat menunduk, pangkal lengan dan bahu terlihat (sudut terlalu masuk ke badan); saat berjalan sambil menunduk, badan naik turun seolah lepas dari kepala; kaki dan lengan terlihat terputus (dialihkan ke M6e, butir pertama).

| Masalah | Penyebab | Perbaikan |
| --- | --- | --- |
| Bahu terlihat | Mata tepat di sumbu badan, pangkal lengan 10 cm di belakang mata; menunduk sampai 83 derajat tanpa gerak leher | Leher `fpCamera()`: menunduk membawa mata maju `neckF` 0,14 m dan turun `neckD` 0,05 m (smoothstep dari pitch 0,30-1,05 rad); pitch 0 tidak berubah |
| Badan lepas dari kepala | Kamera turun terdalam di tengah langkah (`BOB.dy`), badan turun terdalam saat kaki terbuka (geometri kaki): fase berlawanan, geser sekitar 6 cm; goyang samping dan getaran hanya di kamera | Satu sumber `bobDrop()` (fase dibalik: terdalam saat kaki menapak, seperti jalan sungguhan); badan atas = kamera tanpa leher (turun-naik, getaran `BOB.shX/shY`, goyang samping, roll) |
| Kaki harus tetap menapak | Pinggul kini ikut kepala | `bodyLegs()` IK dua ruas: target pergelangan maju (langkah, menunduk, udara) dan angkat (kaki mengayun, mulai halus); lutut tidak pernah lurus penuh (jangkauan 0,88 m); di luar jangkauan langkah dipendekkan, telapak tetap di dasar; jongkok lari `runDrop` 0,04 m |
| Halus / Mati | Kamera tidak turun-naik, pinggul tetap harus | Pinggul turun-naik penuh, badan atas tetap kaku ke kamera; paha masuk 6 cm ke badan menutup celah |

Uji baru (blok 5r):

| Pemeriksaan | Hasil |
| --- | --- |
| Pangkal kedua lengan dan 3 titik tepi tutup badan, pitch -0,9 / -1,2 / -1,45 x diam / jalan / lari | 0 titik terlihat, ndc.y tertinggi -1,72 (batas -1) |
| Badan atas relatif kamera, jalan / lari x Normal / Halus / Mati | geser terbesar 0,61 mm (batas 3 mm) |
| Telapak terendah tiap frame | 0,4 mm dari dasar, tidak ada di bawah dasar |
| Gerak kepala saat langkah terpicu | -33,8 mm (minimum -34,0 mm) |
| Pitch 0 diam | kamera tepat di posisi pemain |
| Uji lama | jangkauan jalan 0,36 m / lari 0,51 m, selisih kaki lari 0,76 m, sendi berubah paling banyak 0,188 rad per frame |

| Uji Millar | 117 pemeriksaan lulus |

Tangkapan layar menunduk 75 derajat sambil berjalan: bahu dan tutup badan tidak tampak; terlihat depan perut, paha, lengan bawah, tangan, dan sepatu.

Wajib dicek pemilik di GTX 1060 dan M1: rasa menunduk (mata maju 14 cm), rasa gerak kepala dengan fase baru (hentakan saat kaki menapak), badan tidak bergeser saat jalan dan lari sambil menunduk. Batasan: lengan atas yang terayun maju saat lari bisa tampak tipis di sudut bawah pada pitch maksimum (wajar, tertutup bingkai visor); di tingkat gerak kepala Mati langkah sedikit lebih pendek dari gerak maju (telapak bisa tampak sedikit tergelincir).

## M6e (selesai 4 Oktober 2026): menuju realistis dengan sumber daya minimum (Medium)

| Item | Hasil |
| --- | --- |
| Sambungan anggota badan | Sendi bola di bahu, siku, lutut, pergelangan (dan pinggul di detail 2) menutup celah saat menekuk; silinder anggota badan terbuka (ujungnya tertutup bola) |
| Tingkat detail per preset | `BODY_DETAIL` = [2, 2, 2, 1, 0] (Ultra, Tinggi, Sedang, Rendah, Hemat), `setBodyDetail(d)` dari `applyPreset()`; tiap bagian dibangun 3 kali saat muat lalu geometri ditukar, tetap 14 draw call |
| Segitiga | Hemat 408 (batas 450, dulu 624), Rendah 1.092 (batas 1.200), Sedang ke atas 2.988 (batas 3.000) |
| Detail pakaian | Rendah: unit kontrol dada, leher sepatu, sol gelap, bahu melengkung ke cincin leher. Sedang ke atas: tombol di unit dada, 2 selang, ransel bertingkat dengan tabung samping, saku paha, lipatan lutut dan siku, ibu jari, visor emas gelap dan cincin leher helm (helm hanya tampak di bayangan dan drone) |
| Kotor dan basah lama | Warna titik dihitung sekali saat muat: makin gelap ke bawah (sepatu 30% lebih gelap), bercak acak per titik, tanpa tekstur |
| Pilot di kokpit | Pandangan kokpit (V saat terbang): badan duduk menempel pada wahana, mata tepat di `CK.eye`, kaki ke pijakan, tangan kanan di tongkat, kiri di tuas gas lewat IK lengan `armReach()` (lengan diperbesar sampai 1,2x karena konsol lebar 0,8 m dari sumbu); lambung membayangi (kapsul abaikan bayangan diri dimatikan saat duduk); tampilan belakang tidak menampilkan pilot (kaca gelap) |
| Ambil barang | Tahan E di dekat barang misi: tangan kanan menjangkau barang (IK, 0,15 s), kembali saat dilepas |
| Ditunda | Tangan ke tangga saat E (naik ke wahana sekarang langsung; menunda naik mengubah alur misi), tubuh terguling saat tersapu (opsional) |

Uji baru (blok 5s):

| Pemeriksaan | Hasil |
| --- | --- |
| Segitiga per tingkat, nilai valid, 14 bagian, peta preset | 408 / 1.092 / 2.988, 0 tidak valid |
| Kotor: putih sepatu dibanding lengan atas | rasio 0,70 (batas 0,8) |
| Biaya `updateBody()` | 0,0042 ms rata-rata per frame (batas 0,1) |
| Pilot | tangan 2,5 / 2,3 cm dari tongkat / tuas, mata = kamera, lutut terlihat saat menunduk, tangan terlihat saat menoleh, render tanpa nilai tidak valid, tersembunyi di tampilan belakang |
| Ambil barang | tangan 0,52 -> 0,24 m dari barang saat tahan E, kembali 0,52 m |
| Per preset (blok 6) | detail sesuai preset, tubuh menunduk tanpa nilai tidak valid di 3 suasana |

Uji busa garis air: batas atas 5% -> 10%. Bukan karena busa berubah: kaki kini lebih gelap (kotor), jadi busa yang terlihat menembus air di atas kaki lebih kontras dan lebih banyak piksel melewati ambang beda (terbukti: tanpa tubuh beda 0%, detail 0 vs 2 berbeda). Uji ambil barang memulai misi (gelombang dan keadaan laut berpindah); posisi gelombang dan `uChopK` dikembalikan setelahnya supaya blok uji berikutnya tidak terpengaruh.

Tangkapan layar: menunduk 70 derajat sambil berjalan (unit dada, selang, lipatan siku, saku paha terlihat); kokpit (paha, lutut, sepatu ke pijakan, sarung tangan di tongkat).

Wajib dicek pemilik: FPS Hemat tidak turun dibanding tubuh Mati (tidak bisa diukur di sandbox), sendi tidak tampak berkedip di GTX 1060 / M1, posisi tangan di tongkat dan tuas wajar.

## M6f (selesai 4 Oktober 2026): pakaian satu mesh berkulit (High)

Masukan pemilik: kaki masih tidak menyatu dengan badan (pangkal paha tampak sebagai tabung dan bola terpisah di bawah perut); ingin kesan seperti foto astronaut di air. Kesan yang diambil: pakaian satu kulit, panggul dan celana lebar, panel dada dan bahu, sabuk, lipatan di sendi. Bentuk persis, logo, dan papan nama pakaian film tidak ditiru; foto tidak di-commit.

| Item | Hasil |
| --- | --- |
| Pakaian | Satu mesh (`BODY.suit`): badan dengan panggul lebar (setengah lebar 0,235 m) + kedua kaki dari dalam panggul sampai di dalam leher sepatu + kedua lengan dari dalam bahu sampai di dalam manset |
| Kulit | Tiap titik ikut 1-2 tulang dari pivot yang sudah ada (tulang panggul baru `BODY.pelvis` mengikuti pinggul), bobot halus: panggul ke paha 16 cm, lutut 14 cm, badan ke lengan atas 13 cm, siku 12 cm. Dihitung di CPU (`skinBody()`), bukan GPU seperti rencana: pass bayangan dan material turunan `shipMat` tidak perlu diubah, tanpa risiko NaN shader di M1 (normal nol memakai normal ikat) |
| Benda kaku | Helm, sepatu dengan leher sepatu, sarung tangan dengan manset, ransel / sabuk elips / unit dada lebih kecil dan terang (Rendah ke atas), panel dada dan bahu, kantong sabuk, selang (Sedang ke atas). Sendi bola M6e dihapus (tidak diperlukan lagi) |
| Lipatan | Pita warna gelap bergantian di lutut dan siku (Rendah ke atas) |
| Segitiga | Hemat 432, Rendah 980, Sedang ke atas 2.408; 7 bagian (dulu 14) |
| Tetap | Pose, IK kaki dan lengan, pilot duduk, kamera leher, bayangan tubuh, basah, busa, visor |

Uji baru (blok 5t), per tingkat detail di pose lari (dua fase), udara, dan duduk di kokpit: tepi segitiga terpanjang paling banyak 1,19x pose ikat (tidak robek), lingkar lutut 0,85x (tidak mengempis), titik berbobot penuh betis tepat di tulang (0,00 mm), tanpa nilai tidak valid. Biaya `updateBody()` dengan kulit 0,064 ms per frame di sandbox (batas 0,1).

| Uji Millar | 123 pemeriksaan lulus |

Tangkapan layar menunduk sambil lari: paha keluar dari panggul sebagai satu kain, siku melengkung.

Wajib dicek pemilik: kain di pinggul dan lutut saat lari dan duduk di kokpit, FPS Hemat. Berikutnya bila perlu: lipatan kain halus lewat noise normal di fragment (M6f-4 di rencana), bentuk panel dada lebih rinci.

### Revisi M6f-b (4 Oktober 2026): lubang di pangkal paha

Masukan pemilik: saat menunduk, di pangkal paha terlihat lubang (air tampak di dalamnya). Penyebab: ujung atas tabung paha terbuka dan cincin teratasnya (pusat 0,16 m dari tengah, jari-jari 0,085 m, tepi luar 0,245 m) lebih lebar dari panggul di ketinggian itu (sekitar 0,21 m), jadi bibir tabung yang bolong mencuat keluar dari badan. Hal yang sama di puncak bahu.

| Perbaikan | Hasil |
| --- | --- |
| Cincin atas paha digeser ke tengah dan diperkecil (pusat 0,085 / 0,12 / 0,15 m, jari-jari 0,06 / 0,08 / 0,094 m) | Seluruh pangkal paha di dalam panggul |
| Cincin atas lengan ke dalam bahu (pusat 0,20 / 0,22 m) | Bahu membulat |
| Ujung atas tabung kaki dan lengan ditutup | Tepi terbuka hanya di dalam sepatu dan manset |
| Segitiga | Hemat 432, Rendah 1.012, Sedang ke atas 2.452 |

Uji baru: titik tepi terbuka di luar sepatu / manset 0, titik pangkal paha di luar panggul 0. Uji Millar 124 pemeriksaan lulus.
