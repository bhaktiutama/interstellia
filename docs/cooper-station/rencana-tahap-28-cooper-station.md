# Rencana Tahap 28 Copper Corn Station: iklan, reklame, plang toko, dan sudut LCD cyberpunk

Per 16 Oktober 2026 · disusun atas permintaan Bhakti · nomor tahap 28 (nomor 27 dipakai warna daun di main)

## Ringkasan

- Kota dan suburban terasa monoton karena tidak ada iklan, reklame, logo merek, atau papan nama perusahaan. Papan toko yang ada (deret bata gaya 12) hanya berisi "huruf" kotak acak, toko di gedung lain hanya pita abu-abu, dan suburban tidak punya toko sama sekali.
- Rencana: satu atlas merek fiktif bersama, lalu semua toko tanpa kecuali diberi plang merek. Kota mendapat reklame atap, logo puncak menara, dan panel iklan halte. Suburban mendapat minimarket berplang, billboard tiang, dan iklan dinding. Ditambah satu sudut LCD besar bergaya cyberpunk di alun-alun New York.
- Status: 28a-28f dikerjakan 16 Oktober 2026 tanpa uji visual (atas permintaan Bhakti: diuji sendiri di akhir). Saklar `?iklan=0` memberi kota sebelum tahap 28 persis, `?neon=0` tanpa sudut LCD.

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

1. Pertahankan yang ada: `?iklan=0` = kota sebelum tahap 28 persis (pola `?ragam=0`, `?mobil=lama`). Generator acak sendiri `r27()` agar urutan acak lama tidak bergeser.
2. Semua merek fiktif buatan sendiri: tidak ada merek dunia nyata, tidak ada judul, logo, atau huruf film. Tema ekonomi stasiun: pangan hidroponik, logistik orbit, wahana, asuransi radiasi, kopi, klinik, minuman, bank, tur Saturnus, toko sepeda, laundry, roti.
3. Satu atlas merek `BRAND` (kanvas 2048 x 4096 dibuat saat muat dari tabel `BRANDS`: nama, warna, bentuk logo primitif, gaya huruf, varian terang dan gelap) dipakai semua jenis papan: satu tekstur, sedikit draw call, tanpa aset luar.
4. Plang di dunia game memakai bahasa distrik, tidak dalam bahasa Indonesia dan tidak ikut bahasa UI (permintaan Bhakti 16 Oktober): merek global berbahasa English, merek lokal berbahasa distriknya (`DISTRICT_LANG`, tabel di bawah). Di distrik berbahasa lokal sekitar 60% toko memakai merek lokal dan 40% merek global; distrik English hanya merek global.
5. Papan 3D lewat pola `FURN.kinds` (radius, `updateFurniture()`, tanpa loop baru per frame) dengan atribut indeks sel atlas per instance; menyala malam lewat `BUILD_U.uNight`; siang dicahayai `patchLit`.
6. Kepadatan ikut `cityDensity()` / `districtAt()`: pusat megacity padat, distrik astronom sedang, suburban jarang dan kecil, ladang dan hutan nol.
7. Aturan P1 muat: material layar penuh baru lewat `fsMat()`, objek baru ikut `warmFrame()`; `tools/ukur_muat.py cooper-station --cek` tetap 0 program baru di frame pertama.
8. Aturan GPU: tidak ada `normalize()` vektor nol, `pow()` bilangan negatif, atau `sqrt()` di luar rentang di shader baru (NaN di M1).

## Cakupan plang: semua toko punya plang

Toko yang ada di kode = lantai dasar bertoko di `BUILD_FS`, lapak pasar, dan kafe trotoar. Aturan tahap 28: tiap toko = satu plang merek dari atlas, tanpa kecuali.

| Jenis | Sekarang | Sesudah tahap 28 |
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
| 28a | Atlas merek `BRAND` + tabel `BRANDS` (48 merek fiktif: 19 global English + 29 lokal dalam 13 bahasa, logo primitif kanvas, varian terang / gelap, sel 256 x 128, mipmap) + halaman pratinjau `docs/cooper-station/iklan/pratinjau-merek.html` untuk disetujui Bhakti sebelum dipasang | blok baru setelah `RAGAM_DET` | Medium | Sonnet 5.5 | medium |
| 28b | Semua lantai toko memakai atlas: gaya 12 per modul (nama merek menggantikan huruf hash, menyala malam seperti `neon`), gaya 2 / 11 / lain per toko 1-3 etalase, gaya 13 papan perusahaan di lobi; dari jauh plang memudar ke warna rata-rata sel (tanpa kedip) | `BUILD_FS` blok 22a dan sekitar 4355, sampler `uBrand` di `BUILD_U` | High (shader gedung bersama, rawan NaN M1) | Opus 5.5 | high |
| 28c | Kota: reklame atap (rangka besi + panel, menyala malam, di atap gedung rendah pusat dekat arteri), logo puncak menara kaca dan kantor > 60 m (satu merek per gedung, menyala), blade sign `RAGAM_DET` diberi logo, panel iklan berlampu di halte bus dan halte trem, papan lapak pasar, nama kafe di payung | `RAGAM_DET`, halte 24d, `STOP_LIGHT`, `KACA`, `MARKET`, `VIBE`, `FURN.kinds` | Medium | Sonnet 5.5 | medium |
| 28d | Suburban dan distrik astronom: minimarket / warung di sudut simpang permukiman (bangunan kecil baru di lahan kosong, rumah lama tetap), billboard tiang tunggal di tepi boulevard dan jalan lingkar (jarang, jarak min 300 m), iklan dinding pudar di sisi buta bata, poster di pagar proyek; pasar tani: papan koperasi tani | `fillHomes()` (titik baru saja), `BLVD`, `MARKET`, kolider `addCollider()` | Medium | Sonnet 5.5 | medium |
| 28e | Sudut LCD cyberpunk New York (rinci di bawah) | blok baru `NEON` setelah `buildSite`, `LIGHT_GLSL` (cahaya layar), `postEnd` | High; cahaya ke tanah xhigh | Opus 5.5 | high / xhigh |
| 28f | Preset dan biaya: radius per preset (Ultra 400 m sampai Hemat papan statis tanpa animasi dan tanpa cahaya layar) lewat `PRESET_HOOKS`, uji `tools/uji_iklan.py`, CLAUDE.md, ukur muat | `PRESETS`, `tools/` | Medium | Sonnet 5.5 | medium |

Urutan: 28a dulu (pratinjau merek disetujui), lalu 28b dan 28c, 28d, 28e, terakhir 28f. 28e bisa dikerjakan paralel setelah 28a karena memakai atlas yang sama.

## 28e Sudut LCD cyberpunk (rinci)

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
| Atlas merek | 32 MB GPU, sekitar 43 MB dengan mipmap | 2048 x 4096 x 4 byte; mipmap + 1/3 |
| Papan 3D | +5-8 draw call | satu InstancedMesh per jenis papan |
| LCD | 1 target 512 x 384 + 1 pass prosedural, hanya saat dekat | 28e |
| Shader gedung | 1 sampel tekstur tambahan per piksel lantai toko | 28b |

Angka sebenarnya diukur di 28f dengan `GPUT` dan `tools/ukur_muat.py`; FPS di GTX 1060 dan M1 menunggu uji Bhakti.

## Uji (`tools/uji_iklan.py`)

- Atlas tanpa sel kosong; semua merek punya nama dan warna.
- Semua modul toko gaya 2, 11, 12 dan lantai toko gedung lain mendapat indeks merek (tidak ada toko tanpa plang).
- Papan 3D tidak di jalan, dek jembatan, air, atau kolider (`colAt`, `onRoad`, `inWater`).
- Kepadatan per distrik: ladang dan hutan 0.
- `?iklan=0` identik dengan sebelum tahap 28 (sidik jari seperti `uji_pohon.py`).
- LCD tanpa nilai tidak valid siang, malam, hujan.
- 0 program shader baru di frame pertama dan saat tombol (`ukur_muat.py --cek`).

## Keputusan Bhakti (16 Oktober 2026)

| Pertanyaan | Keputusan |
| --- | --- |
| Lokasi LCD | alun-alun New York |
| Huruf | merek fiktif; boleh huruf Jepang dan Mandarin dekoratif (terutama neon dan LCD) |
| Bahasa plang | English atau bahasa lain sesuai distrik, jangan bahasa Indonesia |
| Konten LCD | ilusi 3D anamorfik |
| Kepadatan iklan suburban | jarang |

## Status

| Tahap | Status |
| --- | --- |
| 28a | dikerjakan (revisi bahasa distrik): modul bersama `shared/brand.js` (`window.BRANDKIT`: 48 merek `BRANDS` dengan `lang` dan `local`, `DISTRICT_LANG`, `pick(u, use, district)`, `draw(canvas)` atlas 2048 x 4096, `cell(i, kind)`, warna rata-rata per sel) + pratinjau `docs/cooper-station/iklan/pratinjau-merek.html` (kelompok per bahasa, contoh deret toko per distrik); belum dipasang di game, menunggu persetujuan merek. Gambar: `iklan/pratinjau-merek.png`, `iklan/malam-tokyo.png`, `malam-kairo.png`, `malam-delhi.png`, `malam-galileo.png` |
| 28b | dikerjakan: `BUILD_FS` define `IKLAN`, atribut per gedung `aLang` (baris bahasa dari distrik), tekstur `uBrand` (atlas), `uBrandPool` (64 kolom per bahasa, baris toko lalu kantor), `uBrandInfo` (latar, rata-rata plang, rata-rata neon); gaya 12 plang per modul, gaya 2 / 11 / lain per toko 1-3 etalase dengan fasia warna merek, gaya 13 papan perusahaan; setengah plang menyala neon malam; lod eksplisit + pudar ke warna rata-rata dari jauh |
| 28c | dikerjakan: material papan `signMat` (atlas per instance lewat instanceColor = merek, jenis sel, nyala), reklame atap 8 x 4 m (`ikRoof` / `ikRoofS`), logo puncak menara > 60 m (`ikLogo`), plang tegak di papan menonjol 22c (`ikBlade`), panel iklan halte bus (`ikHalte`), papan lapak pasar (`ikPasar`), papan A kafe (`ikKafe` / `ikKafeS`). Halte trem dan nama di payung kafe belum |
| 28d | dikerjakan: billboard tiang 9 m dua muka 6 x 3 m di tepi arteri permukiman (jarak >= 300 m, `ikTiang` / `ikTiangS`), minimarket 7 x 5 m di sudut simpang permukiman dengan plang fasia dan pilon logo (`ikKios`, `ikPilon`, jarak >= 400 m). Iklan dinding pudar dan papan koperasi tani belum |
| 28e | dikerjakan: `IKLAN.lcd`, layar melengkung di sudut gedung dekat alun-alun (dua muka 10 m + busur jari-jari 8 m, 2,5 m di depan dinding, y 7-30 m; cadangan satu muka datar), isi 3D anamorfik per piksel dari titik pandang tengah alun-alun (4 klip 9 s: kubus, bola memantul, Saturnus bercincin, papan merek berayun; ruang maya berkisi neon di balik layar, pita glitch saat ganti), kisi subpiksel RGB dari dekat, ticker LED English di bawah layar, 10 papan neon tegak di gedung sekitar, cahaya layar `uL_Neon` / `uL_NeonCol` di `nightLight()` dan shader tanah. Tanpa render target (isi dihitung langsung di shader layar). Suara belum |
| 28f | dikerjakan: radius papan per preset (Ultra / Tinggi 1, Sedang 0,8, Rendah 0,6, Hemat 0,45; `PRESET_HOOKS`), Hemat layar diam tanpa cahaya layar, uji `tools/uji_iklan.py` (ditulis, belum dijalankan), CLAUDE.md |
| 28g | revisi dari 4 foto Bhakti (dikerjakan tanpa uji): tulisan plang tidak lagi terbalik di muka -z / +x; toko lantai dasar selebar 1-6 etalase (batas acak per etalase, dulu 1 jendela 1 usaha) dengan tiga gaya papan (fasia penuh + plang, kotak plang, huruf neon di latar gelap) dan ukuran beragam; deret bata gaya 12 ukuran papan per modul beragam, 35% tanpa papan latar; toko bersebelahan tidak bermerek sama (tabel merek berlangkah 29); reklame atap pindah ke tepi depan atap yang menghadap jalan dan dinaikkan 1,5 m; LCD dipilih dengan uji garis pandang dari tengah alun-alun (gedung di tepi alun-alun, 7 titik layar harus terlihat), bila tidak ada: layar berdiri sendiri di tepi alun-alun searah pandangan awal ke menara ikon |
| 28h | revisi Bhakti (LCD jadi datar): layar LCD selalu melengkung di siku (dua muka + busur). Hanya gedung di diagonal alun-alun (tinggi >= 19 m, sisi >= 14 m) yang dipakai; uji pandang dilonggarkan (busur tengah wajib terlihat, >= 5 dari 7 titik). Bila tidak ada: menara LCD sudut berdiri sendiri (kaca gelap 8-12 m x 26 m) di pojok alun-alun yang searah pandangan awal ke menara ikon. Layar datar dihapus. Dikerjakan tanpa uji |

## Bahasa plang per distrik

| Distrik | Bahasa plang lokal | Merek lokal (fiktif) |
| --- | --- | --- |
| New York, Sagan, Chandrasekhar, Iowa, di luar distrik | English | hanya merek global (19) |
| Tokyo | Jepang | 空ラーメン, ネオン堂, 星喫茶 |
| Shanghai | Mandarin | 环星电器, 土星茶, 土星面馆 |
| Kairo, Al-Battani, Taman Nil | Arab | مقهى الحلقة, صيدلية المحور, مخبز النيل |
| Delhi, Punjab | Hindi | चक्र चाय, तारा मिठाई |
| Tsiolkovsky | Rusia | ОРБИТА ХЛЕБ, АПТЕКА ОСЬ |
| Ukraina | Ukraina | ЗОРЯНА КАВА, ПОЛЕ АГРО |
| Kepler | Jerman | KEPLER APOTHEKE, BÄCKEREI ORBIT |
| Galileo | Italia | CAFFÈ ANELLO, TRATTORIA ORBITA |
| Copernicus | Polandia | PIEKARNIA ORBITA, KWIACIARNIA GWIAZDA |
| Hypatia | Yunani | ΦΟΥΡΝΟΣ ΤΡΟΧΙΑ, ΚΑΦΕΝΕΙΟ ΔΑΚΤΥΛΙΟΣ |
| Pampas | Spanyol | PANADERÍA LA ÓRBITA, PARRILLA EL ANILLO |
| Taman Mekong | Vietnam | PHỞ VÀNH ĐAI, CÀ PHÊ SAO |
| Ulugh Beg | Uzbek | NON UYI, CHOYXONA YULDUZ |

Catatan font: huruf Arab dan Hindi memakai font sistem (Windows: Segoe UI / Tahoma, Nirmala UI / Mangal; Mac: Geeza Pro, Kohinoor / Devanagari Sangam). Di sandbox tampil benar (FreeSerif); di GTX 1060 dan M1 belum dicek.
