# Rencana: pilihan wahana (Kestrel, Petrel, GX-01) di Gargantua dan Millar's World

Per 22 Oktober 2026 · Status: dikerjakan W1-W7 (lihat bagian Status, uji menunggu pemilik di GTX 1060 dan M1) · Pemilik: Bhakti

## Ringkasan

- Tiga wahana bisa dipilih pemain di kedua experience: **KS-07 Kestrel** (v5, satu kursi), **PR-11 Petrel** (dua awak, baru, baru berupa blokout), **GX-01 Ambang** (kokpit pod kaca, dari v3).
- Kondisi sekarang: Millar hanya KS-07 v5 (`KS = KESTREL.buildV5()`, kokpit `CK = KESTREL.buildCockpitV5()`), Gargantua hanya GX-01 (data `window.__GX01`, dibuat `tools/siapkan_wahana_gx.mjs`). Kedua experience menanam satu wahana di puluhan tempat, jadi pekerjaan utama adalah membuat wahana menjadi data yang bisa ditukar.
- Satu kontrak "deskriptor wahana" (field yang sama dengan keluaran `buildV5`) dipakai kedua experience. Hasilnya: 6 kombinasi (3 wahana x 2 experience), 4 builder baru atau dipindah ke `shared/`, 1 pembuat aset Gargantua yang digeneralisasi.
- Urutan disarankan: kontrak + Petrel di `shared/` (W1-W3), GX-01 ke `shared/` dengan keluaran identik (W4), Millar (W5), Gargantua (W6), pemilih dan uji (W7). Tiap langkah bisa dipasang sendiri tanpa merusak yang lain.
- Risiko terbesar: keseimbangan misi Millar untuk wahana besar (GX-01 27,5 m vs gelombang), dan Petrel belum punya kipas angkat, tangga, serta kokpit. Keduanya ada di bagian Risiko.

## Status (22 Oktober 2026)

Dikerjakan dengan keputusan: kunci bersama `lazarus.ship` (saran 1a), Petrel diberi 4 kipas angkat (saran 2a), nama tampil KS-07 Kestrel / PR-11 Petrel / GX-01 Ambang, Copper tidak disentuh.

| Langkah | Hasil | Berbeda dari rencana |
| --- | --- | --- |
| W1 kontrak + registri | `shared/armada.js` (`window.FLEET`: `current`, `set`, `mountPicker`, `build`) | Nosel dan kipas berbentuk `[x, y, z, radius]` (Millar membaca radius) |
| W2 Petrel | `shared/petrel.js` `buildPetrel`: palet putih krem lapuk + karat + garis salem, kotor dan gosong per titik, atap kaca di atas kokpit, 4 kipas angkat (2 per pod), 4 nosel, 3 kaki + tangga, `low` di pod | Bentuk dasar blokout dipertahankan; cincin badan depan sedikit dilebarkan agar pelapis kokpit v5 muat |
| W3 kokpit Petrel | `buildCockpitPetrel` = kokpit v5 dengan `offset` z -1,45 (geometri v5 tidak diubah, jadi `ksCanopy` di shader tetap cocok) | Tanpa kursi kopilot hiasan (kokpit satu kursi) |
| W4 GX-01 | `FLEET.build('gx01')` membongkar blob `gx01.data.js` (badan = id 0, kaca = id 1, interior = id >= 2, tongkat dan tuas dari `parts`, layar dari `screens`) + kaki dari segitiga `buildV3` di bawah y -2,45 m | Kode pod TIDAK dipindah ke `shared/gx01.js` dan `gx01.data.js` tidak dibuat ulang (lebih aman: keluaran GX-01 tidak berubah). Millar memuat blob dari `../gargantua/assets/gx01.data.js` lewat `<script>` sinkron bila `?ship=gx01` |
| W5 Millar | `KS` = deskriptor terpilih, `CK = KS.cockpit`; kokpit generik `KS_COCKG` untuk GX-01; profil terbang `KS.fly` mengalikan `CONFIG.fly`, kamera belakang dan orbit menurut `size`, plasma orbit `KS.orb`; teks "KS-07" diganti nama wahana di `t()`; pemilih `#shipPick` di kartu mulai | Ganti wahana = simpan `lazarus.ship` lalu muat ulang (bukan bangun ulang adegan) |
| W6 Gargantua | `tools/siapkan_wahana.mjs` membuat `shared/wahana/ks07.data.js` dan `pr11.data.js` (`window.__SHIPDATA`); `SHIP.data`, kamera luar `data.chase`, kanopi generik uniform `uCan`, teks GX-01 diganti `SHIPNAME` di `txt()`, kontrol `Vessel` di tab Misi | KS-07 dan Petrel tanpa HUD kanopi, label tombol, panel kaca, tongkat dan tuas bergerak (data opsional tidak dibuat) |
| W7 pemilih, teks, uji | Kamus ('Wahana', 'Vessel'), `tools/uji_wahana.mjs`, `tools/uji_wahana.py` | Tanpa gambar kecil di pemilih (tombol teks, tooltip = ukuran) |

Belum: gambar kecil wahana, tab Lainnya Millar dan panel Gargantua sudah memakai muat ulang tetapi tanpa dialog konfirmasi, KS-07 / Petrel di Copper (di luar rencana).

Hasil uji (SwiftShader, 22 Oktober 2026): `tools/uji_wahana.mjs` lulus (kontrak 3 wahana + 3 blob); `tools/uji_wahana.py` lulus untuk ks07, pr11, gx01 di Millar dan Gargantua (kolisi, kokpit, lepas landas dan lolos gelombang, tertelan, mendarat, kedatangan, plasma orbit, V di misi). `tools/uji_misi_gargantua.py` 129 dari 130 dan `tools/uji_millar.py` 129 pemeriksaan lulus; satu pemeriksaan gagal di masing-masing (musik dari file, tombol J), tidak terkait wahana dan belum dibandingkan dengan komit sebelum pekerjaan ini. Belum diuji di GTX 1060 dan M1.

## Dasar (apa yang ada di kode sekarang)

| Item | Millar | Gargantua |
| --- | --- | --- |
| Sumber geometri | `KESTREL.buildV5(THREE)` di `shared/kestrel.js`, three.js | `window.__GX01` (base64: pos int16, nrm int8, col, mat id), dibuat `tools/siapkan_wahana_gx.mjs` dari `buildV3` + pod kaca |
| Kokpit | `KESTREL.buildCockpitV5` (geo, stick, throttle, stickAt, throttleAt, screens, eye); pilot tubuh `bodySeat()` + `SEAT_OFF` dari `CK.eye` | Dalam blob: `eye`, `screens`, `labels`, `panels`, `hud`, `ind`; kepala pilot `CKP`; bayangan kanopi `gxCanopy()` di shader (khusus pod GX-01) |
| Tabrakan dan darat | `KS.low`, `KS.pads`, `KS.door`, `KS.belly`, `KS.legs` (tangga), `SHIP.padDrop` | Tidak ada pendaratan |
| Terbang | `FLY`, `CONFIG.fly` (climb 40, fwd 60, acc 14, yawRate 0,9, ...), kipas `KS.fans`, nosel `KS.nozzles` | Fisika misi geodesik, wahana hanya titik; kamera luar `SHIP.chase [0, 7.5, 40]` |
| Orbit dan plasma | `orbShip` + plasma dari `KS.geo` (inflate) | Tidak ada |
| Teks | Nama KS-07 di HUD, kartu, kamus `I18N` | 36 tempat bertuliskan GX-01 (toast, MFD, kartu akhir, kamus `ID`) |
| Konvensi warna | `shipMat` membaca warna titik: kaca = biru lebih besar dari merah, `uMatte`, kotor dan gosong per titik | Id material di blob (0 badan, 1 kaca, 2 panel, 3 LED, 4 logam, 5 karet, 6 kain, 7 plastik) |

Ukuran wahana (dari dokumen konsep dan blokout, satuan m):

| Wahana | Panjang | Lebar | Tinggi mendarat | Awak | Sumber |
| --- | --- | --- | --- | --- | --- |
| KS-07 v5 | 10,8 | 10,1 | sekitar 4 | 1 | `docs/app/konsep-ks07-v5.md` |
| PR-11 Petrel | sekitar 19 | sekitar 13,8 | sekitar 9,3 | 2 | `docs/app/konsep-petrel-pr11.md` |
| GX-01 (v3) | 27,5 | 9,9 | sekitar 7,5 | 2 + kargo | `buildV3().size`, `docs/app/konsep-ks07-v3.md` |

## Kontrak deskriptor wahana

Satu objek dari builder, field mengikuti keluaran `buildV5` (yang sudah dipakai Millar), jadi kode Millar yang ada tetap jalan.

| Field | Isi | Dipakai oleh |
| --- | --- | --- |
| `geo`, `glass`, `legs` | Badan, kaca (terpisah, penanda warna biru), kaki + tangga (ditarik saat terbang) | Millar render, orbit, plasma |
| `PAD_Y`, `pads[]`, `belly`, `low[]`, `door`, `size` | Tapak, kolisi pemain, titik naik, ukuran | `placeShip`, `shipPush`, HUD jarak |
| `nav`, `nozzles[]`, `fans[]` | Lampu nav, nosel, kipas angkat (titik semburan air) | `updateShip`, `updateFly`, orbit |
| `eye`, `cockpit` | Mata pilot + `buildCockpit*` (geo, stick, throttle, stickAt, throttleAt, screens) | `bodySeat`, `flyCamera`, MFD |
| `fly` | Profil terbang: pengali climb, fwd, acc, yawRate, spool, tinggi aman | `CONFIG.fly` per wahana |
| `id`, `name`, `callsign`, `thumb` | Id (`ks07`, `pr11`, `gx01`), nama tampil, nama panggil, gambar kecil | Pemilih, HUD, kamus |
| `blob(opts)` (hanya dipakai alat olah Node) | Bentuk data Gargantua: `pos nrm col mat eye screens labels panels hud ind canopy chase` | `tools/siapkan_wahana.mjs` |

Registri: `shared/armada.js` memasang `window.FLEET = { ks07, pr11, gx01 }` (skrip biasa, jalan dari file://), tiap entri `build(THREE)` dan `cockpit(THREE)` malas (dibangun saat dipilih, bukan saat muat).

## Langkah

Effort mengikuti tabel di `CLAUDE.md`.

| No | Langkah | Isi | File dan fungsi | Effort | Model | Thinking |
| --- | --- | --- | --- | --- | --- | --- |
| W1 | Kontrak + registri | Tulis kontrak di atas, `shared/armada.js`, adaptor KS-07 v5 (tanpa mengubah `buildV5`) | `shared/armada.js` baru, `shared/kestrel.js` (tidak diubah) | Medium | Sonnet 5.5 | medium |
| W2 | Petrel ke `shared/` | Ubah blokout menjadi `buildPetrel(THREE)`: loft badan, pod, dek, blok saluran, pendorong terpisah, tiang; palet putih lapuk + karat per titik; kaca terpisah (penanda biru); kaki + tangga terpisah (`legs`); tambah dua kipas angkat di perut pod (blokout belum punya); `low`, `belly`, `door`, `nav`, `nozzles`, `fans`, `size` | `shared/petrel.js` baru; helper `mergeColored` dari `kestrel.js`; lapisan kotor v5 diekstrak menjadi fungsi bersama tanpa mengubah keluaran v5 (cek hash keluaran `buildV5` sebelum dan sesudah) | High | Opus 5.5 | high |
| W3 | Kokpit Petrel | `buildCockpitPetrel`: kursi pilot depan + kursi kopilot (hiasan), 3 layar MFD, tongkat dan tuas; pelapis dalam mengikuti penampang badan (pola `buildCockpitV5`) | `shared/petrel.js` | High | Opus 5.5 | high |
| W4 | GX-01 ke `shared/` | Pindahkan kode pod kaca, konsol, layar, HUD, panel dari `tools/siapkan_wahana_gx.mjs` ke `shared/gx01.js` (`buildGX`: badan + kaki asli untuk Millar, varian kaki dilipat untuk Gargantua; `buildCockpitGX`); alat olah memanggil modul. Syarat: `gx01.data.js` hasil baru identik byte demi byte dengan yang sekarang | `shared/gx01.js` baru, `tools/siapkan_wahana_gx.mjs` | High | Opus 5.5 | high |
| W5 | Millar: wahana bisa ditukar | Lihat tabel W5 di bawah | `experiences/millar/index.html` | High | Opus 5.5 | xhigh untuk fisika terbang dan kolisi |
| W6 | Gargantua: wahana bisa ditukar | Lihat tabel W6 di bawah | `experiences/gargantua/index.html`, `tools/siapkan_wahana.mjs`, `assets/*.data.js` | High | Opus 5.5 | high |
| W7 | Pemilih, teks, kamus, uji | Pemilih di kartu mulai Millar dan tab Misi Gargantua, gambar kecil, `lazarus.ship`, `?ship=`, kamus I18N dan ID, uji lintas wahana | `index.html` (menu, deskripsi kartu), kedua experience, `tools/uji_*` | Medium | Sonnet 5.5 | medium |

### W5: titik sentuh di Millar

Semua rujukan `KS` dan `CK` di `experiences/millar/index.html` dibuat `let` dan diisi `setShipModel(id)`, yang membangun ulang mesh, kolisi, kokpit, dan adegan orbit.

| Area | Rujukan sekarang (cari dengan nama) | Perubahan |
| --- | --- | --- |
| Mesh wahana | `KS.geo / glass / legs / nav`, `shipMat`, `shipGlassMat` | Bangun dari deskriptor terpilih; material tetap, warna titik mengikuti konvensi |
| Kolisi dan HUD | `placeShip()`, `shipPush()`, `KS.low`, `SHIP.padDrop`, `shipDist()` | `low`, `pads`, `belly`, `door` dari deskriptor |
| Tangga dan pintu | `missionAction()` (E di tangga), `KS.door` | Pintu per wahana; Petrel dan GX-01 memakai tangga sendiri di `legs` |
| Kokpit | `CK`, `COCKPIT`, `cockpitUpdate()`, `drawMfdFlight/Scan/Status`, `SEAT_OFF`, `bodySeat()` | Kokpit per wahana; posisi tongkat dan tuas dari `stickAt`, `throttleAt`; layar MFD sebanyak `screens` |
| Terbang | `CONFIG.fly`, `updateFly()`, `KS.fans` (semburan), `flyEngulfed()` memakai `KS.belly` | Profil `fly` per wahana dikalikan ke `CONFIG.fly`; titik semburan dari `fans` |
| Orbit dan plasma | `orbShip`, `ORB.plasma` (`inflate(KS.geo, ...)`), partikel dari `KS.geo` | Ikut geometri terpilih; jumlah partikel dibatasi per jumlah verteks |
| Sinematik | `cineArriveWorld()`, `cineDepartWorld()`, jarak kamera | Skala kamera dari `size` |
| Audio | `flyAudio()` | Nada mesin per wahana (tinggi nada, jumlah nosel) |
| Pilihan | `start()`, `#presetPick`, `#modePick` | Tambah `#shipPick`; ganti wahana hanya di layar mulai atau mode Jelajah (tidak di tengah misi) |

### W6: titik sentuh di Gargantua

| Area | Rujukan sekarang | Perubahan |
| --- | --- | --- |
| Data | `SHIP.data = window.__GX01`, `assets/gx01.data.js` | `window.__SHIP[id]`; berkas dimuat malas lewat `<script>` yang dibuat saat dipilih; `SHIP.ready` false sampai termuat |
| Alat olah | `tools/siapkan_wahana_gx.mjs` | `tools/siapkan_wahana.mjs --ship=gx01|ks07|pr11`; skrip lama tetap ada dan memanggil `--ship=gx01` |
| Kokpit data | `screens`, `labels`, `panels`, `hud`, `ind`, `eye` | Dibuat dari kokpit tiap wahana; format blob tidak berubah |
| Bayangan kanopi | `gxCanopy(vP, L)` di `SHIP_FS` (angka pod GX-01 tertanam) | Parameter kanopi jadi uniform dari `data.canopy`; nilai GX-01 sama persis; wahana lain memakai kanopi gelembung (Petrel) atau kaca sekat (Kestrel) |
| Kamera luar | `SHIP.chase = [0, 7.5, 40]` | `data.chase` dari `size` (panjang x 1,45 mundur, x 0,27 naik, mengikuti rasio GX-01) |
| Skema layar tengah | `buildSkema` dari segitiga badan (K5) | Ikut data wahana |
| Dampak kaca | `GLASS` dikumpulkan dari mat id 1 | Ikut data wahana |
| Teks | 36 tempat "GX-01" | `SHIP.name` dan `SHIP.callsign`; kunci kamus memakai `{ship}` |
| Skenario | `SCEN`, kartu akhir "AMBANG" | Nama panggil per wahana; fisika tidak berubah (wahana adalah titik; hanya tampilan dan kokpit) |

## Pilihan untuk pemilik

| No | Pertanyaan | Pilihan | Disarankan |
| --- | --- | --- | --- |
| 1 | Penyimpanan pilihan | a. Satu kunci bersama `lazarus.ship` untuk semua experience, seperti `lazarus.lang` · b. Satu kunci per experience | a |
| 2 | Petrel di Millar perlu kipas angkat | a. Tambah dua kipas di perut pod (menyentuh blokout) · b. Terbang hanya dengan nosel | a |
| 3 | Nama tampil | KS-07 Kestrel, PR-11 Petrel, GX-01 Ambang | Sesuai usulan |
| 4 | Keseimbangan misi Millar untuk GX-01 | a. Profil terbang berat, misi sama · b. Beri catatan tingkat kesulitan di pemilih | b |
| 5 | Wahana di Copper Corn Station | Di luar rencana ini (Copper tetap KS-07 v5). Bisa dijadikan tahap lanjutan memakai kontrak yang sama | Tunda |

## Uji

| Uji | Tempat | Isi |
| --- | --- | --- |
| Kontrak builder | `tools/uji_wahana.mjs` baru (Node + three.js `THREE_LOCAL`) | Tiap wahana: field wajib ada, tanpa NaN, normal valid, ukuran dalam 5% dari `size`, kaca terpisah, `legs` di bawah `PAD_Y + 0,3` |
| Keluaran lama tidak berubah | sama | Hash keluaran `buildV5` sebelum dan sesudah W2; `gx01.data.js` identik setelah W4 |
| Millar per wahana | `tools/uji_millar.py` | Kolisi dan tangga, lepas landas, lolos gelombang bisa dicapai (simulasi `simStep`), orbit + plasma tanpa nilai tidak valid, kokpit tergambar (MFD), 5 preset |
| Gargantua per wahana | `tools/uji_misi_gargantua.py` kelompok 11 baru | Blob dimuat, kokpit dan MFD tergambar, render GX-01 identik dengan commit sebelum W6 (0,000%), tanpa nilai tidak valid, teks nama berganti |
| Kamus | `tools/uji_millar.py` (kamus English), `tools/uji_misi_gargantua.py` (kamus ID) | Semua kunci baru ada |

Pemilik menguji visual dan FPS di GTX 1060 dan M1; SwiftShader tidak memperlihatkan NaN di M1 (aturan `CLAUDE.md`).

## Risiko dan batasan

| Risiko | Penjelasan | Penanganan |
| --- | --- | --- |
| Keseimbangan Millar | Misi dirancang untuk v5 (10,8 m, lincah). GX-01 27,5 m jauh lebih besar dan lamban. Belum diukur apakah lolos dari gelombang masih mungkin | Uji simulasi per wahana di W5 sebelum dipasang; profil `fly` disetel sampai lolos mungkin dengan margin yang sama (inferensi, perlu diukur) |
| Petrel belum lengkap | Blokout tanpa kipas angkat, tangga, interior, kaca terpisah | W2 dan W3 menambahkannya; bentuk luar bisa direvisi pemilik sebelum W2 |
| Ukuran berkas | `gx01.data.js` sekarang 371.704 byte. Dua blob baru menambah ukuran repo | Muat malas, hanya wahana terpilih |
| Konvensi warna shader | `shipMat` Millar memakai warna titik sebagai penanda (kaca biru, matte). Builder baru yang salah warna tampil salah | Uji kontrak memeriksa penanda kaca; palet Petrel dibuat mengikuti `buildV5` |
| Bayangan kanopi Gargantua | `gxCanopy` hanya akurat untuk pod GX-01; wahana lain bisa terlihat terlalu terang atau gelap di dalam kokpit | Parameter kanopi per wahana; nilai kasar dulu, dirapikan setelah dilihat pemilik |
| Rujukan film | Petrel dibuat dari gambar stok, bukan kendaraan film yang dikenal. Aturan `CLAUDE.md` tetap berlaku | Tidak ada logo, nomor, atau stiker yang disalin |
| Pengukuran | Estimasi waktu kerja tidak diberikan karena belum ada ukuran kecepatan di proyek ini; hanya label effort |  |
