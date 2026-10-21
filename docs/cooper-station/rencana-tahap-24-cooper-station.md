# Rencana Tahap 24 Copper Corn Station: jembatan, bangku, terminal, mobil dan bus, halo lampu, tombol menu

Per 7 Oktober 2026 · Bhakti

## Ringkasan

- Revisi dari 5 foto Bhakti setelah uji tahap 23 (6 masalah).
- Simpang dekat jembatan terbuka, bangku dan tempat sampah tidak lagi di jalan, terminal mengikuti lengkung silinder.
- Mobil bervariasi (6 jenis) dan ada bus kota dummy (3 jalur, 24 bus, 72 halte).
- Halo lampu malam alami (hanya kuat saat hujan, kabut pagi, mendung). Tombol kembali ke menu utama saat bermain.

Status: 24a sampai 24f selesai, menunggu uji visual dan FPS Bhakti (GTX 1060, M1).

## Keluhan dan penyebab

| No | Foto | Keluhan | Penyebab di kode |
| --- | --- | --- | --- |
| 1 | 1 | Pagar jembatan memotong jalan simpang dekat jembatan; mobil lewat, pemain tertahan | Blok dek `// 23d:` (`BRIDGE_G`): sandaran dan `addCollider` dipasang di tiap ruas 5 m bila tanah 6 m di luar tepi < -0,2. Jalan lingkar dan jalan simpang yang bertemu dek dekat ujungnya ikut tertutup. Tebing galian bisa memakan tepi jalan simpang |
| 2 | 2 | Bangku dan tempat sampah di tengah jalan dekat sungai | `FURN` langkah 6 "tepi sungai": bangku tiap 30 m di `riverZ(s) +- (W/2 + 10)`, hanya menghindari arteri keliling. Jalan lingkar za 2500 dan dek tidak dicek |
| 3 | 3 | Pintu masuk samping terminal pendek, tenggelam | `TERM` (w 120 m) dibangun datar; ujung 60 m dari pusat turun relatif tanah sebesar sagitta 60^2 / 2000 = 1,8 m |
| 4 | 4 | Mobil seragam (kotak), belum ada bus | `TRAFFIC`: satu geometri sedan 4,4 m untuk semua instance, beda hanya cat; `PARKED` juga seragam |
| 5 | 5 | Halo lampu jalan bulat terang walau tidak berkabut | V4 C2 `lampFogMat`: `sig0` 0,004 terlalu besar untuk udara bersih, plus halo bulat x 2,5 yang selalu ada saat malam |
| 6 | - | Tidak ada tombol kembali ke menu utama saat bermain | Tautan `menuLink` hanya ada di layar muat |

## Tahapan

| Tahap | Isi | Effort | Model | Thinking |
| --- | --- | --- | --- | --- |
| 24a | Simpang jembatan terbuka: sandaran, kolider, trotoar dek tidak dipasang di mulut jalan; galian tidak memakan jalan | High (TER / groundH) | Opus 5.5 orkestrator | high |
| 24b | Bangku, tempat sampah, orang bangku tidak di jalan atau dek | Medium | Opus 5.5 subagent | medium |
| 24c | Terminal ditekuk mengikuti lengkung silinder | Medium | Opus 5.5 subagent | medium |
| 24d-1 | Variasi mobil tanpa draw call baru (sedan, hatchback, SUV, van, pickup, taksi) | Medium | Opus 5.5 subagent | medium |
| 24d-2 | Bus kota dummy, 3 jalur, halte, peta | Medium | Opus 5.5 subagent | medium |
| 24e | Halo lampu alami | Medium (shader cahaya) | Opus 5.5 orkestrator | high |
| 24f | Tombol kembali ke menu utama (HUD, panel, bantuan) | Low | Opus 5.5 subagent | low |
| - | Dokumen ini, CLAUDE.md | Low | Opus 5.5 subagent | low |

Urutan kerja: 24f, 24e, 24a, 24b, 24c, 24d-1, 24d-2.

## Hasil

| Tahap | Commit | Hasil |
| --- | --- | --- |
| 24f | 436f15c | Tombol "← Menu" kiri atas HUD (HUD digeser 32 px ke bawah), tautan di panel Lainnya dan di bantuan, semua ikut `?lang=` lewat kelas `.menuHref` |
| 24e | 13fe59f | `ATMO.sig0` 0,004 -> 0,0006, `sigOv` 0,005 -> 0,002; halo bulat x `uHaloK` = min(1, kabut / `ATMO.haloRef` 0,01); halo lebih lebar dan lembut (pangkat 4, Gauss /5, x1,6) |
| 24a | e1f27c5 | Penyebab utama: `otherAt()` memakai `bridgeAt()` yang mengembalikan dek pertama (dek arteri itu sendiri), jadi persilangan dengan dek jalan lingkar za 2500 tidak terdeteksi. Kini `bridgeIn(B, s, za, m)` per dek dan `mouth()` membuka trotoar, sandaran, kolider bila 3 m di luar tepi ada dek lain atau jalan rata tanah (`onRoad()` global). Ruas sandaran yang menghadap jalan 21 -> 0; tidak ada arteri atau jalan lingkar yang termakan alur |
| 24b | fcf635e | Bangku tepi sungai dicari 8-16 m dari tepi air, bebas jalan dan dek; perabot (kecuali lampu lalu lintas dan zebra) tidak di dek. Bangku di jalan dekat sungai 33 -> 0, tempat sampah 21 -> 0 |
| 24c | 96daa6f | `bendSub()` (pecah segitiga sampai lebar x 4 m) + `bendCyl()` menekuk terminal; lantai dan dasar dinding 0-0,08 m di atas tanah sampai kedua ujung (dulu tenggelam sampai 1,8 m) |
| 24d-1 | b192f06 | `CAR_TYPES` (sedan 33%, hatchback 22%, SUV 18%, van 8%, pickup 8%, taksi 11%), `carRemap()`, atribut `aPart` / `aBody`, panjang per mobil `c.len` di IDM, `aBody` di daftar `SHP.cars` dyn; mobil parkir satu geometri per jenis (11 mesh, berbagi 2 material, digambar dalam 260 m) |
| 24d-2 | c7a3bd8 | `BUS` (3 jalur za 500 / 1250 / 1750, 4 bus per arah = 24 bus, 72 halte tiap sekitar 520 m), bus jenis ke-7 di mesh lalu lintas yang sama, berhenti 15-25 s; halte `busStop` / `busStopC` / `busStopG` di `FURN.kinds`; peta dan legenda "Rute bus dan halte" |

## Penyederhanaan dan batasan

| Hal | Catatan |
| --- | --- |
| Halte bus | Pejalan kaki tidak menghindari halte (bisa menembus) |
| Jalur bus | Hanya di arteri melingkar, bukan arteri keliling |
| Mobil parkir | 11 mesh (satu per jenis dan material) |
| Sandaran jembatan | Dibuka per ruas 5 m, celah bisa sedikit lebih lebar dari jalan |
| Jalan lokal | Jalan lokal yang terpotong alur sungai tetap berpagar (buntu) |
| Uji | Visual dan FPS (GTX 1060, M1) oleh Bhakti; tiap commit cukup cek muat |
