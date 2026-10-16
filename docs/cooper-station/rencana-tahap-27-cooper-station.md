# Rencana Tahap 27 Copper Corn Station: iklan, reklame, plang toko, dan sudut LCD cyberpunk

Per 16 Oktober 2026 · disusun atas permintaan Bhakti

## Ringkasan

- Kota dan suburban terasa monoton karena tidak ada iklan, reklame, logo merek, atau papan nama perusahaan. Papan toko yang ada (deret bata gaya 12) hanya berisi "huruf" kotak acak, toko di gedung lain hanya pita abu-abu, dan suburban tidak punya toko sama sekali.
- Rencana: satu atlas merek fiktif bersama, lalu semua toko tanpa kecuali diberi plang merek. Kota mendapat reklame atap, logo puncak menara, dan panel iklan halte. Suburban mendapat minimarket berplang, billboard tiang, dan iklan dinding. Ditambah satu sudut LCD besar bergaya cyberpunk di alun-alun New York.
- Status: rencana saja, belum ada kode yang diubah. Saklar `?iklan=0` (dan `?neon=0` untuk LCD) akan memberi kota sebelum tahap 27 persis.

## Kondisi sekarang (dari kode `experiences/cooper-station/index.html`)

| Ada | Lokasi | Kekurangan |
| --- | --- | --- |
| Papan toko gaya 12 (deret bata): warna per toko + "huruf" kotak dari hash, setengahnya menyala malam (`neon`, `neonC`) | `BUILD_FS` blok 22a (baris sekitar 4336-4356), emisi sekitar 4521 | huruf palsu, tidak ada nama atau logo |
| Lantai toko gaya 2, 11, dan gedung lain > 12 m: etalase tiap 2,6 m + pita kanopi abu-abu | `BUILD_FS` sekitar 4355-4358 | pita polos, tanpa plang |
| Papan nama menonjol `blade` di 30% muka bata | `RAGAM_DET` (sekitar 12407) | warna polos tanpa tulisan |
| Halte bus: tiang dengan papan warna | blok halte 24d (sekitar 12616) | tanpa panel iklan |
| Papan keberangkatan terminal, papan arah 12a, papan tujuan trem dan bus (CanvasTexture) | terminal sekitar 13091-13127, trem sekitar 5211 | hanya di terminal atau kendaraan |
| Lapak pasar (tenda warna), kafe trotoar (meja + payung) | `MARKET`, `VIBE` | tanpa nama |
| Menara ikon 221 m dan alun-alun New York | `buildSite('menara')`, `reserveSite('alun', { s: 45, za: 640 })` | tidak ada tanda merek di sekitarnya |
| Tidak ada sama sekali: reklame atap, billboard jalan, logo puncak menara, iklan halte, iklan dinding, toko suburban | - | sumber utama kesan monoton |

## Prinsip

1. Pertahankan yang ada: `?iklan=0` = kota sebelum tahap 27 persis (pola `?ragam=0`, `?mobil=lama`). Generator acak sendiri `r27()` agar urutan acak lama tidak bergeser.
2. Semua merek fiktif buatan sendiri: tidak ada merek dunia nyata, tidak ada judul, logo, atau huruf film. Tema ekonomi stasiun: pangan hidroponik, logistik orbit, wahana, asuransi radiasi, kopi, klinik, minuman, bank, tur Saturnus, toko sepeda, laundry, roti.
3. Satu atlas merek `BRAND` (kanvas 2048 x 2048 dibuat saat muat dari tabel `BRANDS`: nama, warna, bentuk logo primitif, gaya huruf, varian terang dan gelap) dipakai semua jenis papan: satu tekstur, sedikit draw call, tanpa aset luar.
4. Slogan dua bahasa lewat `t()` + `I18N.en` (`tools/uji_bahasa.py` tetap lulus). Nama merek tidak diterjemahkan.
5. Papan 3D lewat pola `FURN.kinds` (radius, `updateFurniture()`, tanpa loop baru per frame) dengan atribut indeks sel atlas per instance; menyala malam lewat `BUILD_U.uNight`; siang dicahayai `patchLit`.
6. Kepadatan ikut `cityDensity()` / `districtAt()`: pusat megacity padat, distrik astronom sedang, suburban jarang dan kecil, ladang dan hutan nol.
7. Aturan P1 muat: material layar penuh baru lewat `fsMat()`, objek baru ikut `warmFrame()`; `tools/ukur_muat.py cooper-station --cek` tetap 0 program baru di frame pertama.
8. Aturan GPU: tidak ada `normalize()` vektor nol, `pow()` bilangan negatif, atau `sqrt()` di luar rentang di shader baru (NaN di M1).

## Cakupan plang: semua toko punya plang

Toko yang ada di kode = lantai dasar bertoko di `BUILD_FS`, lapak pasar, dan kafe trotoar. Aturan tahap 27: tiap toko = satu plang merek dari atlas, tanpa kecuali.

| Jenis | Sekarang | Sesudah tahap 27 |
| --- | --- | --- |
| Gaya 12 deret bata (modul toko 3,2-5 m) | papan berwarna + huruf hash per modul | plang merek per modul (semua modul), setengahnya menyala malam seperti sekarang |
| Gaya 2 apartemen (lantai toko 3,6 m), gaya 11 podium (4,6 m), gedung lain > 12 m (4,4 m) | etalase 2,6 m + pita abu-abu | plang merek per toko; satu toko = 1-3 etalase 2,6 m agar plang tidak terlalu rapat |
| Gaya 13 batu (lobi kantor, bukan toko) | lobi | papan nama perusahaan di atas pintu lobi |
| Lapak pasar | tenda warna | papan kecil nama lapak di depan tenda |
| Kafe trotoar | meja + payung | nama kafe di payung dan papan A-frame |
| Suburban | tidak ada toko | minimarket / warung di sudut simpang permukiman, masing-masing berplang + pilon |
| Bukan toko (rumah, masjid, gereja, gudang utilitas) | - | tanpa iklan |
| Sekolah, rumah sakit, balai distrik | - | papan nama institusi saja, bukan iklan |

## Tahap

| Tahap | Isi | Fungsi / file disentuh | Effort | Model | Thinking |
| --- | --- | --- | --- | --- | --- |
| 27a | Atlas merek `BRAND` + tabel `BRANDS` (sekitar 24 merek fiktif, logo primitif kanvas, varian terang / gelap, sel 256 x 128, mipmap) + halaman pratinjau `docs/cooper-station/iklan/pratinjau-merek.html` untuk disetujui Bhakti sebelum dipasang | blok baru setelah `RAGAM_DET` | Medium | Sonnet 5.5 | medium |
| 27b | Semua lantai toko memakai atlas: gaya 12 per modul (nama merek menggantikan huruf hash, menyala malam seperti `neon`), gaya 2 / 11 / lain per toko 1-3 etalase, gaya 13 papan perusahaan di lobi; dari jauh plang memudar ke warna rata-rata sel (tanpa kedip) | `BUILD_FS` blok 22a dan sekitar 4355, sampler `uBrand` di `BUILD_U` | High (shader gedung bersama, rawan NaN M1) | Opus 5.5 | high |
| 27c | Kota: reklame atap (rangka besi + panel, menyala malam, di atap gedung rendah pusat dekat arteri), logo puncak menara kaca dan kantor > 60 m (satu merek per gedung, menyala), blade sign `RAGAM_DET` diberi logo, panel iklan berlampu di halte bus dan halte trem, papan lapak pasar, nama kafe di payung | `RAGAM_DET`, halte 24d, `STOP_LIGHT`, `KACA`, `MARKET`, `VIBE`, `FURN.kinds` | Medium | Sonnet 5.5 | medium |
| 27d | Suburban dan distrik astronom: minimarket / warung di sudut simpang permukiman (bangunan kecil baru di lahan kosong, rumah lama tetap), billboard tiang tunggal di tepi boulevard dan jalan lingkar (jarang, jarak min 300 m), iklan dinding pudar di sisi buta bata, poster di pagar proyek; pasar tani: papan koperasi tani | `fillHomes()` (titik baru saja), `BLVD`, `MARKET`, kolider `addCollider()` | Medium | Sonnet 5.5 | medium |
| 27e | Sudut LCD cyberpunk New York (rinci di bawah) | blok baru `NEON` setelah `buildSite`, `LIGHT_GLSL` (cahaya layar), `postEnd` | High; cahaya ke tanah xhigh | Opus 5.5 | high / xhigh |
| 27f | Preset dan biaya: radius per preset (Ultra 400 m sampai Hemat papan statis tanpa animasi dan tanpa cahaya layar) lewat `PRESET_HOOKS`, uji `tools/uji_iklan.py`, CLAUDE.md, ukur muat | `PRESETS`, `tools/` | Medium | Sonnet 5.5 | medium |

Urutan: 27a dulu (pratinjau merek disetujui), lalu 27b dan 27c, 27d, 27e, terakhir 27f. 27e bisa dikerjakan paralel setelah 27a karena memakai atlas yang sama.

## 27e Sudut LCD cyberpunk (rinci)

| Bagian | Rencana |
| --- | --- |
| Lokasi | Simpang di depan alun-alun New York (dekat menara ikon dan halte New York, tempat pemain tiba lewat `SPOTS.nyc` / peta). Satu gedung sudut 8-12 lantai dicadangkan lewat `reserveSite('neon', ...)` di blok bersebelahan alun-alun |
| Layar utama | LCD melengkung membungkus sudut gedung (dua muka + sudut melengkung radius 6 m), sekitar 30 m terbentang x 22 m tinggi, mulai di atas lantai 2 |
| Konten | Gaya 3D anamorfik (ilusi kotak menjorok, objek seolah keluar layar), titik pandang terbaik di tengah alun-alun. 5-6 klip 8-12 s berputar: logo merek berputar 3D, gelombang warna, Saturnus berputar, iklan tur wahana KS-07, minuman. GLSL prosedural + lapisan atlas `BRAND`, tanpa video atau aset luar |
| Render | Klip dirender ke target kecil 512 x 384 hanya bila pemain < 600 m dan layar di frustum, 30 fps; jauh = frame terakhir dibekukan |
| Pendamping | 6-10 papan neon vertikal sempit bertumpuk di muka gedung dan gedung sebelahnya (sebagian berkedip), ticker LED berjalan di atas lantai dasar (info stasiun dua bahasa: jam, cuaca, gerhana berikutnya dari `ECL`, jadwal trem), layar kecil di kanopi toko lantai dasar |
| Rupa LCD | Kisi subpiksel RGB terlihat < 15 m (pudar lewat `fwidth`, tanpa moire), sedikit scanline, pendar bloom malam; siang tetap terbaca (emisi, tidak dicahayai `patchLit`) |
| Cahaya ke sekitar | Warna rata-rata klip (dihitung CPU dari jadwal klip, uniform `uL_Neon` + `uL_NeonCol`) sebagai cahaya area persegi di `nightLight()` dan shader tanah (pola `lampPoolL()`): aspal, trotoar, gedung seberang ikut berwarna malam. Genangan dan aspal basah memantulkan layar tanpa kerja tambahan lewat `SSR` (23a). Halo di udara saat hujan / kabut lewat `lampFogMat` (`ATMO`) |
| Suara (opsional) | Dengung trafo neon + jingle lirih dekat layar lewat `AUDIO`, ikut tombol U |
| Saklar | `?neon=0`; Hemat: frame statis, tanpa cahaya layar |

## Biaya (perkiraan dari ukuran, belum diukur)

| Item | Perkiraan | Dasar |
| --- | --- | --- |
| Atlas merek | 16 MB GPU, sekitar 21 MB dengan mipmap | 2048 x 2048 x 4 byte; mipmap + 1/3 |
| Papan 3D | +5-8 draw call | satu InstancedMesh per jenis papan |
| LCD | 1 target 512 x 384 + 1 pass prosedural, hanya saat dekat | 27e |
| Shader gedung | 1 sampel tekstur tambahan per piksel lantai toko | 27b |

Angka sebenarnya diukur di 27f dengan `GPUT` dan `tools/ukur_muat.py`; FPS di GTX 1060 dan M1 menunggu uji Bhakti.

## Uji (`tools/uji_iklan.py`)

- Atlas tanpa sel kosong; semua merek punya nama dan warna.
- Semua modul toko gaya 2, 11, 12 dan lantai toko gedung lain mendapat indeks merek (tidak ada toko tanpa plang).
- Papan 3D tidak di jalan, dek jembatan, air, atau kolider (`colAt`, `onRoad`, `inWater`).
- Kepadatan per distrik: ladang dan hutan 0.
- `?iklan=0` identik dengan sebelum tahap 27 (sidik jari seperti `uji_pohon.py`).
- LCD tanpa nilai tidak valid siang, malam, hujan.
- 0 program shader baru di frame pertama dan saat tombol (`ukur_muat.py --cek`).

## Pertanyaan untuk Bhakti

1. Lokasi LCD di alun-alun New York setuju, atau pindah ke pusat megacity lain?
2. Merek fiktif saja (diusulkan) dan teks Latin saja, atau boleh huruf Jepang / Mandarin dekoratif di neon ala cyberpunk?
3. LCD memakai ilusi 3D anamorfik (rumit, terbaik dari satu titik) atau iklan datar beranimasi (lebih murah)?
4. Kepadatan iklan suburban: jarang (diusulkan) atau ramai seperti jalan raya Amerika?
