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
