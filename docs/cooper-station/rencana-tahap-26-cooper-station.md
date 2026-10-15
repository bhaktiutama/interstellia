# Rencana Tahap 26 Copper Corn Station: mobil lebih detail dan bermaterial seperti mobil sungguhan

Per 14 Oktober 2026 · disusun atas permintaan Bhakti

## Ringkasan

- Sekarang mobil = 6 kotak (bodi, kabin, 2 kotak roda per poros, 2 strip lampu) ditambah 6 kotak khusus (bak pickup, lampu taksi, bus). Tidak ada lengkung, list, atau garis bodi. Mobil lalu lintas dicahayai per titik (4 titik per muka kotak), mobil parkir per piksel.
- Poin "depan dan belakang terlihat acak dari dekat" kemungkinan besar berasal dari detail material V1 (`matDetail`) yang ikut aktif di cat mobil parkir: kekasaran cat 0,3 memberi kekuatan detail penuh (petak 0,6 m, noda 14 cm, tonjolan 2,5 cm, gelap sampai 12%). Ini dugaan dari kode, belum dilihat di layar; cek cepat: buka dengan `?detail=0`.
- Rencana: 26a perbaiki cat dulu (cepat), 26b generator bentuk mobil bersama (loft lengkung, list, garis bahu, lengkung roda) dengan halaman blokout untuk disetujui, lalu pasang di mobil parkir dan mobil lalu lintas dekat (LOD), dan material per piksel seperti mobil sungguhan (cat clearcoat, kaca, krom, plastik, karet, velg, lampu, celah panel). Status: rencana saja, belum ada kode yang diubah.

## Kondisi sekarang (dari kode)

| Aspek | Sekarang | Lokasi | Kekurangan |
| --- | --- | --- | --- |
| Geometri | 12 kotak `BoxGeometry` per mobil (6 dasar + 6 di `CAR_EXTRA`), 288 titik, 144 segitiga; bagian yang tidak dipakai jenis itu diciutkan jadi satu titik | `TRAFFIC` geometri (`index.html` baris 9825-9842), `CAR_EXTRA` 9802 | semua sudut siku, tanpa kap miring, kaca depan miring, lengkung roda, bumper, spion, list |
| Jenis bodi | 7 jenis (sedan, hatchback, SUV, van, pickup, taksi, bus) dari satu geometri sedan yang direntang per bagian | `CAR_TYPES` 9791, `carRemap()` (JS) 9808, kembaran di `CAR_VS` 9919-9933 | jenis hanya beda ukuran kotak, siluet tetap kotak |
| Cahaya mobil lalu lintas | dihitung per titik di `CAR_VS` (`vegLight`, `farEnv`), `CAR_FS` hanya menulis `vCol` | 9907-9978 | muka besar (depan, belakang, samping) = 4 titik, gradasi lebar, pantulan kabur, tidak mungkin ada detail di dalam muka |
| Material mobil parkir | `paintMat` = `specMat(..., 0.3, 0.05)`, `trimMat` = `specMat(..., 0.08, 0.05)` untuk kaca, roda, dan lampu sekaligus | 11613 | cat terkena `matDetail` (lihat bawah); ban dan kaca sama licinnya (0,08), ban jadi berkilap seperti kaca |
| Detail material V1 | `patchLit` memanggil `matDetail(..., smoothstep(0.1, 0.3, uSpec.x), ...)` untuk semua `specMat` bukan kaca; aktif di Ultra dan Tinggi (`uL_Detail`) | 1528, `matDetail()` 1461, `PRESET_HOOKS` 11209 | cat kekasaran 0,3 = kekuatan 1: petak kasar/licin 0,6 m, noda 14 cm, tonjolan normal 2,5 cm, kotor menggelapkan sampai 12%. Untuk aspal dan beton benar, untuk cat mobil tampak acak |
| Bayangan | mobil lalu lintas lewat `castAlpha` + `SHP.cars` (geometri pengganti per pass), mobil parkir: badan ikut pass bayangan, kaca/roda/lampu tidak | 9982, 14728, 11620 | - |
| Jumlah | 3.455 mobil lalu lintas (analisa optimasi) + 24 bus (24d); 4.814 mobil parkir (22d), dikirim dalam radius 260 m lewat `updateFurniture()` | `docs/cooper-station/analisa-optimasi-dan-usulan-cooper-station.md`, `rencana-tahap-22` | - |

Catatan biaya sekarang (turunan, bukan ukur): semua 3.479 instance lalu lintas diproses di vertex shader tiap frame (buang jarak 900 m dilakukan di shader), 3.479 x 288 = 1,00 juta titik per frame untuk pass utama. Karena itu geometri detail tidak boleh dipasang ke semua instance (lihat LOD di 26e).

## Dugaan penyebab "material acak" di depan dan belakang

| Dugaan | Bukti di kode | Cara cek | Keyakinan |
| --- | --- | --- | --- |
| H1 `matDetail` di cat mobil parkir | `paintMat` kekasaran 0,3 = kekuatan penuh; trim 0,08 = 0 (karena itu hanya bagian bercat yang acak) | buka `?detail=0`, atau preset Sedang (detail mati); bila acak hilang = H1 | tinggi untuk mobil parkir |
| H2 bayangan per piksel di muka tegak (PCF 16 sampel dengan derau per piksel di peta dekat 17f) | bayangan peta dekat sengaja memakai derau putih per piksel di tepi bayangan | lihat apakah acak hanya di tepi bayangan dan ikut berkedip saat kamera bergerak | sedang, hanya di tepi bayangan |
| H3 mobil lalu lintas | cahaya per titik, tidak bisa menghasilkan pola acak | - | rendah; bila yang dimaksud mobil yang melaju, keluhan kemungkinan "datar dan kotak", bukan acak |

Pertanyaan 1 di bawah meminta konfirmasi mobil mana yang dimaksud.

## Prinsip

1. Pertahankan yang ada: ukuran tiap jenis (`h`, `bt`, `ct`, `af`, `ar`, `ws`, `wx` di `CAR_TYPES`) tetap, jadi panjang IDM, kolider mobil parkir, sorot lampu, dan simulasi lalu lintas tidak berubah. Saklar `?mobil=lama` = mobil sebelum tahap 26 persis (pola sama dengan `?pohon=lama`, `?ragam=0`).
2. Satu sumber bentuk: satu generator dipakai mobil parkir dan mobil lalu lintas dekat, jadi keduanya selalu sama.
3. Realisme datang dari bentuk dan pantulan yang halus, bukan dari derau. Cat mobil sungguhan licin: yang membuatnya tampak nyata adalah pantulan tajam lapisan bening (clearcoat), perubahan warna di sudut miring, garis celah panel, dan list. Tidak ada pola acak per piksel di cat.
4. Detail hanya dekat (LOD): mobil jauh tetap kotak lama (sudah cukup dari jauh dan murah).
5. Desain orisinal, prosedural, tanpa aset dari luar dan tanpa meniru merek atau model mobil tertentu.

## Desain bentuk (26b)

Generator `carShape(t)` membangun tiap jenis dari loft penampang: 16-20 irisan sepanjang mobil, tiap irisan = setengah penampang 10-12 titik dicerminkan.

| Detail yang diminta | Cara membuat | Keterangan |
| --- | --- | --- |
| Lengkung, tidak kotak | sudut denah dibulatkan (lebar mengecil di irisan depan/belakang), tepi atap dan bahu dibulatkan 2-3 titik, kap dan bagasi miring, kaca depan miring 55-62 derajat dari tegak (sedan), atap sedikit cembung | profil samping per jenis = daftar titik kontrol (z, tinggi) di tabel `CAR_SHAPE`, bukan kode per jenis |
| Kabin menyempit ke atas (tumblehome) | titik kaca samping condong ke dalam 8-15 cm | seperti mobil sungguhan, tidak dinding tegak |
| Garis bodi / garis bahu | lipatan tajam sepanjang sisi setinggi bahu (normal diduplikasi di lipatan, sudut lipat > 30 derajat dibiarkan tajam) | memberi garis kilap memanjang di samping |
| List | list jendela (krom atau hitam per mobil), list samping pintu (pita plastik tipis), list bumper, bingkai gril | geometri pita tipis untuk list samping; bingkai jendela dan celah panel di shader (26d) |
| Lengkung roda | tepi bawah samping naik melengkung di atas tiap roda, dinding dalam lengkung gelap | roda tidak lagi kotak menempel |
| Bumper depan/belakang | loft terpisah sedikit menonjol, bagian bawah plastik hitam | |
| Roda | 4 silinder (12-16 sisi) per mobil: ban, dinding ban, velg | dulu satu kotak per poros |
| Pelengkap | spion, gagang pintu, gril berlubang, wadah plat, lampu depan/belakang dengan bentuk (bukan strip), antena (sebagian) | gagang dan gril sebagian di shader bila geometri terlalu mahal |
| Jenis | sedan, hatchback, SUV (rel atap), van, pickup (bak dari loft), taksi (lampu atap), bus (kaca pita, pintu, kaca depan besar) | ukuran tetap dari `CAR_TYPES` |

Anggaran awal: <= 2.000 segitiga per mobil dekat (bodi sekitar 800, roda 4 x 120, sisanya pelengkap). Angka ini target, diukur di 26g.

Halaman blokout untuk disetujui sebelum dipasang: `docs/cooper-station/mobil/blokout-mobil.html` (7 jenis berjajar, putar kamera, pilih warna dan saklar material), seperti blokout KS-07 di `docs/app/kestrel/`. Generator ditaruh di `shared/mobil.js` (`window.CARKIT`, skrip biasa, jalan dari file://) agar halaman blokout dan Copper memakai kode yang sama (pola `shared/kestrel.js`). Lihat pertanyaan 4.

## Desain material (26d)

Material dihitung per piksel di shader mobil dekat (mobil parkir lewat `patchLit` + `specMat`, mobil lalu lintas dekat lewat shader sendiri yang memakai `stationLight`, `nightLight`, `farEnv`, `ssrRefl` dari `LIGHT_GLSL`). Bagian ditandai atribut per titik (id bahan).

| Bahan | Warna dasar | Kekasaran | F0 / logam | Ciri yang membuat nyata |
| --- | --- | --- | --- | --- |
| Cat solid | warna `PAINT` | dasar 0,45 + clearcoat 0,04 | clearcoat F0 0,04 | dua lapis: difus berwarna + pantulan tajam daratan seberang dan lampu di lapisan bening, Fresnel kuat di sisi miring |
| Cat metalik | warna `PAINT` (sebagian warna diberi tanda metalik) | dasar 0,35 + clearcoat 0,04 | logam 0,6 di lapisan dasar | "flop": lebih terang menghadap langsung, lebih gelap di sudut miring. Tanpa kilau butiran acak (sesuai poin 3) |
| Kaca | 0,02-0,04, sedikit kehijauan/keabuan | 0,02 | 0,04 | pantulan tajam, sedikit tembus ke kabin gelap (bayangan kursi sederhana dari gradasi, opsional) |
| Krom (list, gagang, gril sebagian) | 0,9 | 0,08 | logam 1 | memantulkan warna lingkungan |
| Plastik hitam (bumper bawah, list samping, spion sebagian) | 0,03 | 0,6 | 0,04 | kusam, tidak berkilap |
| Ban | 0,025 | 0,85 | 0,04 | kusam (dulu berkilap seperti kaca), dinding ban sedikit lebih terang |
| Velg | 0,55 (perak) atau 0,08 (hitam) | 0,3 | logam 1 | jari-jari dari pola sudut di shader, ikut berputar bila mobil melaju (26f) |
| Lampu depan | lensa bening di atas reflektor terang | 0,05 | 0,04 | menyala malam (seperti sekarang, `uNight`) |
| Lampu belakang | merah tembus | 0,1 | 0,04 | menyala malam dan saat rem (`aSim.y`, seperti sekarang) |
| Plat nomor | putih / kuning, bingkai hitam, garis huruf samar | 0,4 | 0,04 | tanpa nomor yang bisa dibaca (tidak perlu) |

Detail di shader (dari koordinat lokal mobil, bukan koordinat dunia):

- Celah panel 4-5 mm: pintu, kap, bagasi, tutup tangki. Posisi per jenis di tabel. Garis dihaluskan dengan `fwidth` dan memudar 20-30 m agar tidak berkedip.
- Bingkai jendela (list krom atau hitam) dari koordinat kabin.
- Kotor halus dan teratur, bukan acak: debu tipis di bawah 0,35 m dan di dalam lengkung roda (gradasi tinggi), banyaknya per mobil dari benih (bersih sampai agak berdebu), tidak berbeda per piksel.
- `matDetail` tidak dipakai di cat dan kaca mobil. Boleh dipakai sangat lemah di ban dan plastik (amt <= 0,3) bila Bhakti mau, karena di sana tekstur kasar memang nyata.

Aturan GPU (M1): tidak ada `normalize()` dari vektor yang bisa nol, tidak ada `pow()` bilangan negatif, `sqrt()` dan `acos()` dijepit. Sudut velg dari `atan()` dengan dua argumen yang dijaga tidak keduanya nol.

## Tahapan

| Tahap | Isi | Effort | Model | Thinking | File dan fungsi yang disentuh |
| --- | --- | --- | --- | --- | --- |
| 26a | Perbaikan cepat mobil parkir: konfirmasi H1 (`?detail=0`), cat tanpa `matDetail` (tanda baru `userData.spec.noDetail` atau kekuatan 0 untuk mobil), cat clearcoat (kekasaran 0,05, F0 0,04), `trimMat` dipecah: kaca 0,02, ban dan roda 0,85, lampu 0,1. Bentuk belum berubah | Medium | Sonnet 5.5 | medium | `PARKED` (`paintMat`, `trimMat`, `trimGeos`), `specMat()`, `patchLit()` (hanya membaca tanda baru) |
| 26b | Generator bentuk `CARKIT.shape(t)` (loft, lipatan tajam dengan normal duplikat, roda silinder, bumper, spion, list, id bahan per titik) + tabel `CAR_SHAPE` + halaman blokout untuk persetujuan Bhakti | High | Opus 5.5 | high | `shared/mobil.js` baru, `docs/cooper-station/mobil/blokout-mobil.html` baru; `CAR_TYPES` hanya dibaca |
| 26c | Mobil parkir memakai bentuk baru dalam radius dekat (usul 120 m), kotak lama 120-260 m; satu InstancedMesh per jenis untuk dekat; badan ikut bayangan, pelengkap kecil tidak | Medium | Sonnet 5.5 | high | `PARKED`, `FURN.kinds` (jenis baru `r26car*`), `updateFurniture()`, `warmFrame()` / `FS_MATS` bila ada material baru |
| 26d | Material per piksel seperti tabel di atas (clearcoat, metalik flop, kaca, krom, plastik, karet, velg, lampu, plat, celah panel, bingkai jendela, kotor teratur) | High | Opus 5.5 | xhigh (shader rawan NaN di M1) | shader mobil dekat baru (`CAR_NEAR_VS` / `CAR_NEAR_FS` atau `patchLit` dengan blok mobil), `LIGHT_GLSL` hanya dipakai, tidak diubah |
| 26e | Mobil lalu lintas dekat: tiap frame mobil dalam radius dekat disalin dari simulasi ke InstancedMesh per jenis (cara `shpCars()`), mobil yang sama disembunyikan di mesh kotak lama lewat atribut baru (bukan `aSim.z`, karena sorot lampu memakai `aSim` yang sama); rem dan lampu malam tetap; bayangan: mobil dekat memakai bentuk baru di pass bayangan, `SHP.cars` melewati mobil dekat; peralihan dekat/jauh dengan dither 10 m agar tidak meletup | High | Opus 5.5 | high | `TRAFFIC`, `CAR_VS` (atribut sembunyi), `SHP` / `shpCars()`, `castAlpha`, `updateTraffic()` |
| 26f | Variasi: velg 3 model, list krom / hitam per mobil, rel atap SUV, antena, plat putih / kuning, roda berputar sesuai jarak tempuh, bus dengan pintu dan kaca depan besar | Medium | Sonnet 5.5 | medium | `shared/mobil.js`, shader mobil dekat |
| 26g | Uji dan ukur: `tools/uji_mobil.py` baru (tanpa NaN / Infinity di geometri, normal tidak nol, ukuran tiap jenis = `CAR_TYPES`, `?mobil=lama` identik dengan sidik jari tersimpan, jumlah segitiga per jenis), `uji_lalu_lintas.py` dan `uji_boulevard.py` tetap lulus, `ukur_muat.py cooper-station --cek` 0 program baru saat main, ukur draw call dan segitiga | Medium | Sonnet 5.5 | medium | `tools/uji_mobil.py` baru, `window.__station` (ekspor `CARKIT`, jumlah dekat) |

Urutan: 26a dulu karena murah dan langsung menjawab poin 3. 26b berhenti di blokout sampai Bhakti setuju dengan bentuknya. 26c dan 26d bisa dikerjakan bersama (mobil parkir lebih mudah diuji karena diam). 26e terakhir karena menyentuh simulasi dan bayangan.

## Radius LOD per preset (usulan, disesuaikan setelah uji FPS Bhakti)

| Preset | Mobil dekat (bentuk baru) | Material per piksel | Catatan |
| --- | --- | --- | --- |
| Ultra | 150 m | penuh (celah panel, metalik, velg) | |
| Tinggi | 120 m | penuh | |
| Sedang | 80 m | tanpa celah panel dan kotor | |
| Rendah | 40 m | sederhana (clearcoat saja) | |
| Hemat (M1) | mati, kotak lama | material lama | bisa dinaikkan bila M1 kuat |

## Anggaran dan risiko

| Item | Perkiraan | Dasar | Keyakinan |
| --- | --- | --- | --- |
| Segitiga per mobil dekat | <= 2.000 (sekarang 144 termasuk bagian yang diciutkan) | target desain 26b | sedang, diukur di 26g |
| Jumlah mobil dalam 120 m | belum diketahui | perlu diukur di pusat kota (paling padat) dan di boulevard | data belum ada |
| Draw call baru | sekitar 7 jenis x (utama + bayangan) untuk lalu lintas + 7 untuk parkir | satu InstancedMesh per jenis | sedang; bisa dikurangi dengan satu mesh + atlas jenis bila perlu |
| Biaya CPU penyalinan tiap frame | kecil (ratusan mobil, cara sama dengan `shpCars()`) | `shpCars()` sudah melakukan hal serupa untuk 3.479 mobil per pass | sedang |
| Waktu muat | bertambah sedikit (7 geometri dibangun sekali) | | belum diukur |

Risiko:

- Meletup saat mobil berpindah dari kotak ke bentuk baru: dikurangi dengan dither 10 m dan ukuran sama persis (kotak lama sedikit lebih besar dari bentuk bulat, jadi bentuk baru tidak boleh lebih besar dari kotak agar kolider dan antrean tetap benar).
- Bayangan tidak cocok bentuk (kotak di pass bayangan, bulat di layar): ditangani di 26e dengan bentuk baru di pass bayangan untuk mobil dekat.
- NaN di M1 dari shader baru: aturan GPU di atas; sandbox SwiftShader tidak memperlihatkan NaN, jadi uji akhir di M1 oleh Bhakti.
- Celah panel dan list tipis berkedip dari jauh: dipudarkan menurut jarak, TAA Ultra membantu.

## Batasan

- Tidak ada interior lengkap (kursi, dasbor) di mobil lalu lintas dan parkir; kaca gelap dengan sedikit tembus. Bisa ditambah nanti bila diminta.
- Tidak ada animasi pintu, setir, atau pengemudi.
- Bus tetap kendaraan dummy dari 24d (bentuk saja yang membaik).
- Tidak ada merek, logo, atau bentuk mobil nyata tertentu yang ditiru.

## Pertanyaan untuk pemilik

1. Yang terlihat acak dari dekat di depan dan belakang itu mobil parkir (diam di jalan lokal) atau mobil yang melaju? Mohon coba buka dengan `?detail=0`: bila acaknya hilang, penyebabnya `matDetail` (H1) dan 26a menyelesaikannya.
2. Gaya mobil: sedan dan SUV modern umum (garis tegas, lampu sipit) atau lebih membulat dan klasik? Usul: modern umum, sesuai kota stasiun.
3. List jendela: campuran krom dan hitam per mobil (usul), atau semua hitam?
4. Generator di `shared/mobil.js` (dipakai halaman blokout dan Copper, seperti `shared/kestrel.js`) atau tetap di dalam `index.html` Copper sesuai aturan satu file? Usul: `shared/mobil.js`.
5. Boleh mulai dari 26a langsung (perbaikan cat), lalu 26b berhenti di blokout untuk dilihat dulu?

## Hasil

### Hasil 26a

Perbaikan cepat material mobil, bentuk belum berubah. Semua di belakang `MOBIL.lama` (`?mobil=lama` = persis sebelum 26a).

- `MOBIL` (dekat `CAR_TYPES`): `{ lama }`, tempat field tahap berikutnya (26c: `near` per preset).
- `specMat(m, r, f0, metal, glass, noDetail)`: argumen baru `noDetail` (`userData.spec.noDetail`). `patchLit()` melewati `matDetail` bila true dan menambah `NoDet` ke `customProgramCacheKey`, jadi material lain tidak berubah.
- Mobil parkir: cat = clearcoat (kekasaran 0,05, F0 0,04, tanpa `matDetail`). `trimMat` dipecah per bahan: `splitGeos[t]` {glass, tire, lamp}; `glassMat` (0,02; F0 0,04), `tireMat` (0,85; F0 0,02), `lampMat` (0,1; F0 0,04). Kind FURN baru per jenis: `r22carT/W/L` (sedan) dan `r24carT/W/L<t>`. Draw call +2 per jenis yang berada dalam radius.
- Mobil lalu lintas (`CAR_VS`): cat memantul lebih tajam (farEnv kekasaran 0,25 jadi 0,08, Fresnel 0,04 + 0,6 Fc); roda (aKind 2) tetap tanpa pantulan. Dipilih lewat string bersyarat `${MOBIL.lama ? ...}` saat membangun shader, bukan uniform.
- Belum diuji visual (hanya `node --check`). H1 (`?detail=0`) belum dikonfirmasi oleh pemilik.

### Hasil 26b

Generator bentuk mobil detail di `experiences/cooper-station/index.html` (bukan `shared/`, tanpa halaman blokout, sesuai jawaban pemilik), tepat setelah `carPick()` dan sebelum `TRAFFIC`. Belum dipasang ke mobil mana pun (26c, 26e). `?mobil=lama` = `CARGEO` null, generator tidak dijalankan.

- `CAR_MAT`: id bahan (0 cat, 1 kaca, 2 list, 3 plastik hitam, 4 ban, 5 velg, 6 lampu depan, 7 lampu belakang, 8 plat, 9 lampu atap taksi, 10 papan tujuan bus, 11 putih bus, 12 gelap (dalam lengkung roda, gril), 13 krom).
- `CAR_SHAPE` (+ `CS_SEDAN`, dipakai ulang hatchback dan taksi): tabel per jenis. Bodi bawah = loft 23-27 irisan (ujung membulat 4, tiap lengkung roda 7, pangkal kaca depan dan belakang; tanpa irisan di bagian lurus) x setengah penampang 9 titik (ambang menyempit, garis bahu tajam, bahu membulat 3 ruas, atas cembung), muka depan dan belakang berkolom (gril, lampu, bumper). Kabin = cincin mendatar dari sabuk ke atas kaca (kolom W, A, S1, B, S2, C, Q, R menentukan kaca / pilar / list per baris), tepi atap membulat, atap cembung. Roda 14 sisi (bus 16): tapak, bahu, dinding ban, velg cekung.
- `carShape(t)`: BufferGeometry ber-indeks: `position`, `normal` (sudut lipat per kelompok: bodi 28 derajat, kabin dan roda 50, lain 40; garis bahu terpisah sekitar 34 derajat), `aMat`, `aUV2` (cat 0 / 11 = (z, y) lokal; kaca = (u sepanjang kolom jendela, v ke atas) 0..1; ban / velg = (r / jari-jari, jarak ke dalam / lebar ban); lain = (u, v) 0..1 per bagian), `aWheel` (titik roda: x muka luar ban bertanda, y pusat 0,3 ws, z poros af / -ar, jari-jari 0,3 ws; titik lain 0). `userData` = { type, tris, verts, seams }.
- `CARGEO[t]`: dibangun sekali saat muat (tanpa angka acak; sekitar 55 ms untuk 7 jenis di Node). Diekspor di `window.__station` bersama `CAR_SHAPE`, `CAR_MAT`, `carShape`, `MOBIL`.
- Arah: +x = kiri pengemudi = sisi trotoar (lalu lintas di lajur kiri, dari `CAR_VS`: `Rt = cross(up, F)` = arah offset lajur). Pintu bus dan pintu geser van di sisi +x.
- `seams` per jenis (untuk celah panel 26d): `door` z celah pintu tegak (bawah bodi sampai sabuk), `hood` [z belakang kap, setengah lebar], `trunk` [z depan tutup bagasi atau null = pintu belakang tegak, setengah lebar, y bawah di muka belakang], `fuel` [z, y, sisi], `slide` (van) [z0, z1], `busDoor` [[z0, z1], ...].

| Jenis | Titik | Segitiga | Batas (anggaran) |
| --- | --- | --- | --- |
| sedan | 1.535 | 1.584 | 2.000 |
| hatchback | 1.505 | 1.564 | 2.000 |
| SUV (rel atap) | 1.686 | 1.640 | 2.000 |
| van | 1.574 | 1.616 | 2.000 |
| pickup (bak) | 1.566 | 1.584 | 2.000 |
| taksi (lampu atap) | 1.555 | 1.594 | 2.000 |
| bus | 1.672 | 1.792 | 2.600 |

Cek geometri (skrip Node sementara, bukan suite uji): tanpa NaN / Infinity, semua normal satuan, lilitan cocok dengan normal, tanpa segitiga tanpa luas, semua di dalam kotak lama (setengah lebar <= 0,93 wx kecuali spion 0,975 wx, |z| <= h - 0,004, tinggi <= ct; taksi 1,60, bus 3,10). Kaca depan sedan sekitar 58 derajat dari tegak, tumblehome 10 cm (van 8, bus 4).

Catatan untuk tahap berikut: bodi terbuka di bawah (tanpa lantai, tidak terlihat dari mata) dan atas bodi di bawah kabin tidak dibuang, jadi material harus `FrontSide`; spion keluar 2,5 cm dari kolider mobil parkir (0,95 wx), sesuai aturan; belum ada material atau shader (26c / 26d), jadi belum perlu masuk `warmShaders()`. Antena dan variasi velg ditunda ke 26f.

### Hasil 26c

Mobil parkir memakai bentuk detail (`CARGEO`) dalam radius dekat, kotak lama di luarnya. `?mobil=lama` dan preset Hemat (radius 0) = persis seperti sebelum 26c (tidak ada mesh yang digambar, jalur `updateFurniture()` lama).

- `MOBIL.near` (radius sekarang) dan `MOBIL.nearR` [150, 120, 80, 40, 0] per preset (Ultra, Tinggi, Sedang, Rendah, Hemat). `applyCarNearPreset(i)` didaftarkan lewat `PRESET_HOOKS`, memaksa `updateFurniture()` mengirim ulang di frame berikutnya.
- `carNearMat({ traffic, depth })` (setelah `CARGEO`, sebelum `TRAFFIC`): `ShaderMaterial` bersama, di-cache per varian. Per piksel: `stationLight + nightLight` (bayangan sunline dan cap ikut) x warna dasar, pantulan `farEnv` dengan Fresnel Schlick (rumus `SPEC_GLSL`, logam mewarnai pantulan), sedikit gelap dekat tanah (`ao` dari y lokal), kabut three.js. Semua sifat bahan dari satu fungsi GLSL `carSurf(id, paint, seed, uv, lp, wh)` yang mengembalikan struct `CarS` (base, rough, f0, metal, emis); `main()` tidak tahu soal bahan. Tabel 26c: cat clearcoat 0,08 (seperti 26a), kaca gelap 0,02, list krom atau hitam per mobil dari `fract(seed x 13,7)`, plastik 0,6, ban 0,85, velg perak logam, lampu depan / belakang, plat, lampu atap taksi (id 9, menyala malam), papan bus (10), putih bus (11), krom (13). `aUV2` dan `aWheel` sudah diteruskan ke `carSurf` (belum dipakai).
- Define: `CAR_PARKED` (posisi dari `instanceMatrix`, warna dan benih dari atribut instance `aCarCol` / `aCarSeed`), `CAR_TRAFFIC` (disiapkan: lampu depan dan belakang menyala malam; posisi dari `aLane` / `aMove` / `aSim` masih TODO 26e, sementara sama dengan parkir), `DEPTH_ONLY` (varian kedalaman lewat `shUnroll`, belum dipakai: mobil parkir membuat bayangan lewat layer 1 + `depthMat` override seperti kind cat lama; 26e memakainya untuk `castAlpha`).
- `CAR_NEAR` (diekspor, bersama `carNearMat`): `meshes[t]` satu `InstancedMesh` per jenis (kapasitas = jumlah mobil parkir jenis itu, `PARKED.types`; taksi = jenis 5 sendiri), `count[t]`, `total`, `begin(s, za)` / `isNear(ps, pz)` / `add(K, i)` / `end()`. Geometri per jenis membungkus atribut `CARGEO[t]` (dipakai bersama, tanpa salinan) plus `aCarCol` dan `aCarSeed`. Mesh `visible = count > 0`; `layers.enable(1)` agar ikut pass bayangan (cap, sunline jauh, sunline dekat).
- Pemilahan di `updateFurniture()` (tiap 20 m berpindah, tanpa kerja per frame baru): kind cat mobil parkir (`r22carP`, `r24carP<t>`) membawa `carNear` {ty, sd}; kind kaca / roda / lampu (`r22carT/W/L`, `r24car...`) membawa `carSkip`. Uji jarak sama (`lodShift(MOBIL.near)`, pusat dan radius ikut lensa K10, selalu himpunan bagian dari radius 260 m). Mobil dekat: cat -> `CAR_NEAR.add`, kaca / roda / lampu dilewati. Tidak ada dobel. Benih per mobil = hash indeks (`seedOf`, tanpa generator acak, urutan acak lama tidak berubah).
- Prakompilasi: mesh dekat ada di `scene` sejak muat (count 0, visible true) sehingga `renderer.compile` di `warmShaders()` membuat programnya; varian kedalaman bayangan memakai `depthMat` yang sudah ada. Setelah muat `visible` mengikuti count. Cek memuat (Chromium headless SwiftShader, bukan suite): Ultra, Sedang, Hemat, `?mobil=lama` termuat tanpa galat konsol; Ultra di pusat kota 124 mobil dekat (jenis [42, 26, 17, 10, 10, 19, 0]), Sedang 47, Hemat dan lama 0. Tangkapan layar: bentuk, pantulan, taksi dengan lampu atap tampil benar.
- Draw call baru: sampai 7 (satu per jenis yang punya mobil dekat, di sini 6) di pass utama, dan sampai 7 di tiap pass bayangan (cap, sunline jauh, sunline dekat); kind kotak lama tetap digambar untuk cincin 150-260 m. Segitiga: sekitar 1,6 rb per mobil dekat (124 mobil = sekitar 200 rb di pass utama, dikali tiga pass bayangan karena belum diseleksi SHP).
- Keputusan: lampu depan dan belakang mobil parkir TIDAK menyala malam (mobil diam; hanya taksi dengan lampu atap yang menyala); `CAR_TRAFFIC` menyalakannya. Mengubahnya = mengganti `#ifdef CAR_TRAFFIC` di `carSurf` (id 6 dan 7). Peralihan kotak ke bentuk detail terjadi di tepi radius (150 m di Ultra) tanpa dither; ukuran bentuk detail tidak melebihi kotak lama.
- Ditunda: 26d (clearcoat berlapis, metalik, celah panel dari `seams`, bingkai jendela, velg dan roda berputar, kotor teratur, plat) di dalam `carSurf`; 26e (posisi `CAR_TRAFFIC`, lampu rem, `castAlpha` dan `SHP.cars`, dither peralihan); 26g (ukur segitiga bayangan, pertimbangkan seleksi SHP untuk mobil dekat atau bayangan dari bodi saja). Belum diuji di GPU asli (M1, GTX 1060).

### Hasil 26d

Material per piksel seperti mobil sungguhan di shader mobil dekat (`CN_VS` / `CN_FS`, isi `carSurf()`), tanpa derau per piksel: semua detail dari posisi lokal, `aUV2`, `aWheel`, dan benih per mobil. `LIGHT_GLSL`, `SPEC_GLSL`, material lain, dan `?mobil=lama` tidak berubah.

| Bahan | Isi 26d |
| --- | --- |
| Cat (0, putih bus 11) | dua lapis: difus warna + lapisan bening (F0 0,04, kekasaran 0,04, farEnv tajam), difus dikurangi Fresnel lapisan bening. Metalik dari benih dan warna (perak / abu-abu 80%, putih 20%, warna lain 45%; taksi dan bus solid): flop 0,35 (miring) sampai 1,1 (menghadap) + pantulan dasar berwarna (logam 0,55, kekasaran 0,35, farEnv kedua) |
| Celah panel | `carSeams(ty, lp, ln, fw)` dibangkitkan dari `CAR_SHAPE[t].seams`: pintu, kap, bagasi / pintu belakang, tutup tangki, pintu geser van + relnya, pintu bus. Lebar 4,4 mm, disaring kotak terhadap lebar piksel per sumbu (turunan layar posisi lokal dihitung sekali di awal `main()`, di alur seragam), pudar 20-30 m |
| Kotor | `cnDirt()`: bawah 0,4 m + lingkar di atas lengkung roda (belakang roda lebih kotor), banyak 0..0,65 per mobil (kuadrat benih: kebanyakan bersih); menaikkan kekasaran, mengurangi lapisan bening. Tanpa derau |
| Kaca (1) | kehijauan atau keabuan per mobil, kabin gelap dengan siluet kursi berparalaks `cnSeat()` (sinar pandang dipotong bidang kursi), bingkai tegak list 2 cm di tepi u kaca samping (lebar dalam meter dari Jacobian layar aUV2), frit hitam kaca depan / belakang, pilar kaca bus tiap 1,45 m, bingkai daun pintu bus, kaca spion = cermin, kaca gelap belakang 60% SUV / van |
| List (2) | krom atau hitam satin per mobil (`cnList()`, aturan benih sama dengan 26c; bus hitam) |
| Plastik (3), gelap (12), krom (13) | plastik kusam 0,6 + debu; gril depan berbilah 2,5 cm (rata-rata saat jauh); krom 0,88 / 0,07 |
| Ban (4) | tapak 0,014 dengan 2 alur keliling, dinding 0,03 dengan pita tulisan rata, kekasaran 0,78-0,88, debu dinding |
| Velg (5) | perak (logam) atau hitam mengilap (35%) per mobil, 5 atau 6 jari-jari meruncing dari sudut (`atan` dengan x = 1 di pusat), diputar `spin`, cakram rem diam di celah, alur bibir, tutup tengah |
| Lampu depan (6) | lensa (lapisan bening) di atas reflektor krom, rumah gelap di tepi, garis DRL di tengah, sekat sel 7,5 cm; `CAR_TRAFFIC`: lampu malam + DRL siang |
| Lampu belakang (7) | merah dengan garis LED per ruas; `CAR_TRAFFIC`: malam (0,2 + 2 uNight) + rem (2,5 x brake), rata-rata sama dengan `CAR_VS` agar tidak meletup di batas LOD |
| Plat (8) | putih atau kuning (30%, bukan bus), bingkai 6 mm, 7 tanda 7 ruas samar dari benih, pudar menjadi rata-rata di atas 3-8 mm per piksel |
| Papan bus (10) | tanda LED 7 ruas (16 tanda), rata-rata pancaran sama dengan 26c |

- Model lapisan di `main()`: dasar = difus x (1 - logam) + farEnv kabur x Fresnel (F0 = mix(f0, warna, logam), jadi logam gelap tidak menjadi cermin terang); lapisan bening opsional di atasnya. farEnv dihitung hanya untuk lapisan yang ada: cat solid 1x, cat metalik dan lampu 2x, bahan lain 1x. Hasil dijepit 0..64.
- Struct baru: `CarIn` (masukan carSurf), `CarS` ditambah `cc` / `ccR`, `CarT` per jenis dari `carT(ty)`. JS: `CN_SEATS` (kursi per jenis), `carTypeGLSL()` (membangkitkan `CarT` / `carT()` / `carSeams()` dari `CAR_TYPES` dan `CAR_SHAPE`), `CN_Q` (uniform `uCarQ`).
- `carShape()` menambah atribut `aCarType` (jenis per titik, 4 byte per titik) agar konstanta per jenis tersedia di semua mesh yang membungkus `CARGEO[t]` (parkir dan 26e).
- Varying dipadatkan: `vI0` (bahan, benih, jenis, rem) dan `vI1` (mata di koordinat lokal mobil, putar roda) flat, `vLN` normal lokal.
- Kualitas lewat uniform (bukan define, jadi ganti preset tanpa program baru): `CN_Q` diisi `applyCarNearPreset()` [2, 2, 1, 0, 0]. 2 = penuh (Ultra, Tinggi); 1 = Sedang tanpa celah panel, kotor, siluet kursi; 0 = Rendah: cat clearcoat, metalik hanya flop, kaca polos, velg polos, tanpa tanda plat.
- Masukan untuk 26e (di `CN_VS`, cabang `CAR_TRAFFIC`): `IM` = rangka mobil (rotasi + translasi dari aLane / aMove / aSim dan groundFrame), `brake` = aSim.y (0..1), `spin` = jarak tempuh / (0,3 ws) dalam rad (sebaiknya dibungkus 2 pi di CPU; shader juga memakai mod). `CAR_PARKED` = 0 untuk keduanya. Lampu depan / belakang / kabin bus menyala hanya di `CAR_TRAFFIC`.
- Biaya per piksel (perkiraan, belum diukur): cat penuh +sekitar 150-250 operasi (celah panel, kotor) di atas 26c, cat metalik + satu farEnv (sekitar 60-80 operasi + 1-3 tekstur); kaca + Jacobian dan paralaks kursi sekitar 80 operasi; velg + atan / sin sekitar 50. Bagian terberat tetap `stationLight` (bayangan sunline) seperti 26c. Hanya piksel mobil dalam radius dekat.
- Cek (Chromium headless SwiftShader, bukan suite): Ultra termuat tanpa galat konsol, varian `CAR_TRAFFIC` (dipasang sementara ke mobil parkir) terkompilasi dan menyala malam (DRL, lampu malam, garis LED belakang), Sedang dan Rendah tanpa galat. Tangkapan layar: celah pintu dan kap, velg berjari-jari, siluet kursi, frit, plat, lampu tampil benar. Render SwiftShader dengan 268 mobil dekat sekitar 2,5 menit per frame (perangkat lunak, bukan ukuran GPU).
- Belum yakin: kekuatan pantulan cat di layar asli (lingkungan silinder terang merata, cat putih tampak datar), siluet kursi mungkin terlalu jelas atau samar, garis celah bisa berkedip ringan di Tinggi (FXAA, tanpa TAA) pada 15-25 m, kekuatan debu. Belum diuji di M1 / GTX 1060.

### Hasil 26e

Mobil lalu lintas dekat memakai bentuk detail (`CARGEO`) dan material per piksel (`carNearMat({ traffic: true })`), kotak lama di luar radius. `?mobil=lama` = program dan jalur persis seperti sebelum 26e (string shader kosong, tidak ada mesh baru); radius 0 (Hemat) = tidak ada mobil dekat, `aNear` semua 0.

- `TERRAIN_GLSL` + `GROUND_FRAME_GLSL` (sebelum `VEG_COMMON`): `hAt` / `terrainH` / `groundFrame` dipindah ke dua konstanta dan disisipkan kembali di tempat semula; teks `VEG_COMMON` hasil akhir identik (dicek). Dipakai juga `CN_VS` cabang `CAR_TRAFFIC`.
- `CN_VS` `CAR_TRAFFIC`: atribut instance `aCnP` (s, za titik mobil, arah depan di bidang s-za; dihitung CPU dengan rumus `CAR_VS`) dan `aCnT` (putar roda rad, pudar 0..1, rem 0..1); `IM` = kolom `cross(up, F)`, `up`, `F`, `groundFrame()` (sama dengan `CAR_VS`). Warna = `aCarCol` (dari `aPaint`, taksi kuning ikut), benih = `aCarSeed` (hash indeks mobil, `c.sd`). Varian kedalaman: mobil dengan pudar < 0,5 dibuang (bayangan tanpa dither).
- `CN_FS`: `flat varying vFade`; di pita peralihan `discard` bila `ign(gl_FragCoord) >= vFade` (setelah turunan layar dihitung). `vFade = 1` di dalam radius penuh: tanpa dither.
- Kotak lama: atribut instance baru `aNear` (`TRAFFIC.aNear`, juga dipasang di `beamGeo` tetapi diabaikan untuk `aKind` 7, jadi sorot lampu tetap). `CAR_VS` (string `NEAR_VS_A` / `NEAR_VS_B`): `aNear > 0,999` dibuang, pass kedalaman `aNear >= 0,5` dibuang; `CAR_FS` (`NEAR_FS` / `NEAR_FS_B`): `discard` bila `ign < aNear` (komplementer dengan `CN_FS`). `SHP.cars.dyn` menambah `aNear` (wajib disalin, bukan dipakai bersama) dan `shpCars()` melewati mobil dengan `aNear >= 0,5`.
- `TRAFFIC.near` (diekspor lewat `TRAFFIC`): `meshes[t]` satu `Mesh` per jenis (InstancedBufferGeometry membungkus atribut `CARGEO[t]` + `aCnP`, `aCnT`, `aCarCol`, `aCarSeed`; kapasitas = jumlah mobil jenis itu), `count[t]`, `total`, `band` 10 m, `idx` / `nIdx` (mobil bertanda `aNear` frame ini). Mesh di `realGroup` (tersembunyi di kamera luar seperti `TRAFFIC.cars`), `castAlpha` dengan `carNearMat({ traffic: true, depth: true })` (layer 2, tiga pass bayangan, tanpa SHP), ada sejak muat dengan 0 instance agar `warmShaders` / `warmFrame` mengompilasi.
- `updateTrafficNear()` (diekspor; dipanggil `worldStep()` setelah `updatePeds()`, jadi setelah `stepTraffic`, `updateCamera`, `updateReal`): kosongkan tanda lama, lalu untuk tiap lajur yang garis tengahnya dalam radius (pusat dan radius `lodShift(MOBIL.near)` dari `VU.uEyeSZ`, ikut lensa K10) mobil `on` dengan jarak < r masuk mesh jenisnya, pudar f = min(1, (r - d) / 10). Unggah hanya rentang terpakai + `aNear` (4 byte x 3.479) bila ada perubahan.
- `stepTraffic()`: putar roda `c.sp += v h / (0,3 ws)` per mobil (`c.iw`), dibungkus 2 pi di akhir langkah.
- `applyCarNearPreset()`: radius kini bergantung pada `CARGEO` (bukan `CAR_NEAR.mat`), jadi lalu lintas dekat tetap jalan walau mobil parkir mati (`?ragam=0`).
- Cek (Chromium headless SwiftShader, bukan suite): Ultra, Hemat, `?mobil=lama` termuat tanpa galat konsol; Ultra di spawn 24 mobil lalu lintas dalam 150 m, `?mobil=lama` tanpa `TRAFFIC.near`. Radius 25 m di arteri: bentuk baru tepat di tempat kotak lama dengan arah depan sama (lampu depan malam di ujung yang sama dengan kotak), tanpa kotak dobel; pita (f 0,5): kotak dan bentuk baru berselang-seling per piksel; lampu malam menyala.
- Biaya (perkiraan, belum diukur di GPU asli): CPU per frame satu putaran sekitar 150 lajur + mobil di lajur yang lolos (puluhan sampai ratusan), di bawah 0,1 ms; unggah beberapa KB. Draw call baru: sampai 7 di pass utama + sampai 7 per pass bayangan (cap, sunline jauh, sunline dekat), jadi sampai 28. Segitiga sekitar 1,6 rb per mobil dekat di pass utama dan tiap pass bayangan.
- Belum yakin: varian kedalaman `CAR_TRAFFIC` baru terkompilasi di `warmFrame()` bila pass bayangan berjalan saat muat (pola sama dengan `ALPHA_CASTERS` lain, belum dicek dengan `tools/ukur_muat.py --cek`); dither di Tinggi tanpa TAA bisa tampak berbintik di pita 10 m; bayangan berganti bentuk sekaligus di tengah pita; mobil yang melaju di tepi radius bergantian masuk / keluar pita tiap frame (tanpa histeresis, tetapi pudar kontinu jadi tidak meletup). Belum diuji di M1 / GTX 1060.

### Hasil 26f

Variasi tambahan mobil dekat (parkir dan lalu lintas), hampir semua di shader dari benih per mobil; tanpa draw call baru. `?mobil=lama` tidak terpengaruh (`CARGEO` null).

- Velg model ketiga di `carSurf` (bahan 5): `wm` dari `cnH(seed, 8)` 0 lima jari-jari (35%), 1 enam (35%), 2 turbin (30%): 10 bilah tipis yang melengkung (puntiran 1,1 jari-jari di sudut bahan), tetap berputar dengan `spin`.
- Atap dua warna: `cnTone(seed, ty)` (hanya sedan, hatchback, SUV): 10% atap hitam mengilap (di atas `T.yT`), 10% seluruh kabin di atas bawah kaca hitam (pilar ikut, di atas `T.yG0`); tepi disaring selebar piksel vertikal. Spion (bahan baru 14) hitam 40% atau selalu hitam bila atap dua warna, selain itu warna bodi.
- Sunroof: 15% sedan dan SUV, persegi panjang sudut bulat (`cnBox`) di atap dari `T.zRf` / `T.zRr` / `T.W`, bingkai hitam 1,4 cm, kaca gelap, tepi anti alias, pudar 80-140 m. `CarT` bertambah `yT`, `zRf`, `zRr` (dibangkitkan `carTypeGLSL()`).
- Antena sirip hiu: geometri baru (bahan 15 `sirip`, 10 segitiga) di `carShape` untuk sedan, hatchback, SUV (`S.fin`; taksi tidak, lampu atap). Ada pada 70% mobil: di `CN_VS` titik diciutkan ke nol bila `fract(sin(...)) > 0,7` (hash sama dengan `cnH(seed, 45)`); warna hitam 50% atau mengikuti atap dua warna, selain itu warna bodi.
- Agar sirip muat di bawah `ct`, atap sedan (juga taksi) dan hatchback diturunkan 4,5 cm lewat `gh.ry` (sedan 1,405, hatchback 1,435) dan tinggi kaca samping `rows[1]` diturunkan (sedan 1,33, hatchback 1,36); lampu atap taksi y0 1,40 menjadi 1,39. Ukuran jenis (`CAR_TYPES`) tidak berubah. Tinggi maks terukur: sedan 1,442 (ct 1,45), hatchback 1,470 (1,48), SUV 1,798 (1,80), taksi 1,60 (lampu atap).
- Gril: bilah krom gril (bahan 13 dengan normal ke depan) kini mengikuti `cnList()` mobil (krom atau hitam satin); gagang pintu tetap krom.
- Rendah (`uCarQ` 0) tanpa atap dua warna, sunroof, dan spion/sirip hitam. Segitiga: sedan 1.594, hatchback 1.574, SUV 1.650, van 1.616, pickup 1.584, taksi 1.594, bus 1.792 (anggaran 2.000 / 2.600).
- Cek: `node --check`; satu muat headless (SwiftShader) Ultra tanpa galat konsol/kompilasi GLSL; geometri tanpa NaN. Belum dilihat di layar (atap dua warna, sunroof, sirip belum ditangkap), belum diuji di M1 / GTX 1060.
