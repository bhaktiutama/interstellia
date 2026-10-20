# Rencana tahap 29: rumput fluffy, jalur taman, jalur trotoar, jembatan, kaca trem, gandum

Sumber: 5 foto uji Bhakti + permintaan mempelajari FluffyGrass. Analisa ini disusun dari pembacaan kode `experiences/cooper-station/index.html` (17.759 baris) dan render headless (Playwright + SwiftShader, pemuatan lokal three.js 0.186.1) yang mereproduksi 4 dari 6 masalah.

## Ringkasan

- Penyebab 6 masalah sudah ditemukan di kode. 5 jelas (rumput, jalur taman, trotoar, kaca trem, gandum). Jembatan: gejalanya terlihat di render, penyebab pastinya belum terbukti (lihat 29d, langkah pertama = diagnosis).
- FluffyGrass (MIT) bukan sekadar shader: kuncinya kartu rumpun bertekstur alfa (satu kartu memuat sekitar 13 helai), warna ujung bercak oleh noise dunia, tinggi oleh noise, angin sinus berfase noise. Teknik ini bisa dipakai sebagai lapisan menengah (6-45 m), tetapi aset teksturnya tidak disalin: dibuat prosedural sendiri.
- Urutan kerja yang disarankan: 29d (jembatan, kecil) -> 29e (kaca trem) -> 29c (pejalan trotoar) -> 29b (jalur taman) -> 29a (rumput fluffy) -> 29f (gandum, memakai infrastruktur 29a).

## 1. Bukti (reproduksi di sandbox)

| Masalah | Bukti reproduksi | Berkas |
| --- | --- | --- |
| Jalur taman | Pita beige lurus bertepi tajam, rumput tumbuh menembus pita | `img/tahap29-park2.png` |
| Kaca trem | Kabut keabuan menutup pandangan keluar, sisi seberang silinder terpantul | `img/tahap29-tram.png` |
| Jembatan | Satu sisi trotoar tanpa sandaran, jalur air biru menempel di tepi trotoar | `img/tahap29-bridge2.png` |
| Gandum | Helai pipih seragam, baris terlihat, bulir belum diperiksa dari dekat | `img/tahap29-wheat.png` |
| Trotoar pejalan | Tidak ada orang di bingkai uji (pejalan acak), dianalisa dari kode saja | (foto 2 Bhakti) |

Catatan metode: tangkapan layar 640 x 360 px, SwiftShader (bukan GPU asli), preset Ultra, sekitar 2 menit per sesi. Warna dan kecepatan di GTX 1060 dan M1 tidak terwakili.

## 2. Analisa per masalah

### 29a. Rumput fluffy (pendek dan panjang)

Kondisi sekarang:

| Item | Nilai | Sumber |
| --- | --- | --- |
| Rumput pendek dekat | rumpun 7 helai x 3 ruas, jarak sel 0,3 m, radius 11 m (Ultra), sekitar 4.224 instance (turunan: pi x 11^2 / 0,3^2) | `tuftGeo(7, 3, ...)`, `GRASS.near` |
| Rumput pendek jauh | rumpun 4 helai x 2 ruas, jarak 0,55 m, radius 38 m, sekitar 14.997 instance (turunan) | `GRASS.far` |
| Rumput tinggi bukit | 5 helai x 4 ruas (dekat, 0,32 m, 18 m) dan 9 helai x 3 ruas (0,85 m, 60 m) | `MEADOW.near` / `MEADOW.mid` |
| Warna | satu warna dari peta lahan, gradasi pangkal ke ujung, bercak kering `vnoise(P / 9)` | `GRASS_VS`, `MEADOW_VS` |

Penyebab tampilan "tidak natural" (foto 1): helai berdiri tunggal, tipis, seragam bentuk dan warna; permukaan lahan terlihat di antara rumpun; tidak ada massa rumpun yang saling menutup; tidak ada sentuhan translusensi cahaya belakang.

Yang dilakukan FluffyGrass (dibaca dari `src/GrassMaterial.ts` dan `src/main.ts` di repo, bukan dari halaman web):

| Teknik | Detail terukur | Dipakai di Copper? |
| --- | --- | --- |
| Kartu rumpun | 3 LOD: 132 / 64 / 32 vertex (66 / 32 / 16 segitiga) dari `grassLODs.glb` (10,6 KB); tekstur alfa `grass.jpeg` 2048 x 2048 px berisi sekitar 13 helai berbagai lengkung, ambang `step(0.1, alpha)` | tidak, rumpun sekarang = helai geometri |
| Jumlah | 8.000 instance (`grassCount`), disebar `MeshSurfaceSampler` berbobot warna titik, sejajar normal permukaan + putaran Y acak | sebar sudah ada (sel + peta lahan) |
| Warna | `mix(base, tip, uv.y)`, `tip = mix(tip1, tip2, noise.r)` dengan noise dunia: bercak dua warna ujung | belum |
| Tinggi | `exp(noise) * 0.5 * (1 - uv.y)` | sebagian (`vnoise(P / 5)`) |
| Angin | `sin(50 * dot(dir, uv) + noise.g * 5.5 + t) * 0.1 * (1 - uv.y)`, noise bergulir | ada, lebih kaya (`windAt`, `meadowGust`) |
| Bayangan | dibaca di fragment, digelapkan 0,5 | tidak perlu (rumput `noLight`, `vegLight`) |

Yang tidak diambil: material `MeshLambertMaterial` dengan `alphaTest` murni (di Copper tepi alfa akan berkedip di bawah FXAA, TAA hanya di Ultra), aset `grass.jpeg` / `grassLODs.glb` (kita buat sendiri, sesuai aturan aset proyek), `MeshSurfaceSampler`.

Rancangan 3 lapis:

| Lapis | Jarak | Isi | Perkiraan biaya (turunan) |
| --- | --- | --- | --- |
| A helai dekat | 0 - 6 m | helai geometri yang diperbaiki: 4 ruas, lengkung per helai, warna per helai (pangkal gelap, ujung terang, ujung kering), translusensi cahaya belakang, kepadatan naik | instance naik dari 4.224 ke sekitar 2.000 pada radius 6 m dengan jarak 0,2 m (sel 0,2 m: pi x 36 / 0,04 = 2.827) |
| B kartu rumpun | 6 - 45 m | 5 kartu radial berlengkung (sekitar 50 vertex) bertekstur alfa prosedural (kanvas, 3 varian), bercak warna ujung dari noise dunia, tinggi noise, angin `windAt` | jarak 0,9 m, radius 45 m: sekitar 7.854 instance x 50 vertex = 393 ribu vertex |
| C jauh | > 45 m | shader tanah (sudah ada), tambahkan variasi warna bercak yang sama agar transisi tidak terlihat | tanpa geometri |

Rumput tinggi bukit (`MEADOW`) memakai lapis B dengan kartu lebih tinggi 0,6-1,1 m dan pita angin yang sudah ada.

Risiko: tepi alfa berkedip (gunakan alfa terkoreksi mip + ambang bergantung jarak, dithering fade yang sudah ada, TAA di Ultra); overdraw di GTX 1060; NaN di M1 (jangan `normalize` vektor nol, jangan `pow` bilangan negatif, lihat catatan GPU di CLAUDE.md); varian `DEPTH_ONLY` untuk pass bayangan harus dibuat.

Penyakelaran: `?rumput=lama` = rumput sebelum 29a persis (konvensi proyek, mirip `?pohon=lama`).

### 29b. Rumput dan jalur orang di taman kota (foto 1)

Penyebab (`PARK_PATHS`, baris 14225-14265):

| Gejala | Penyebab di kode |
| --- | --- |
| Terlalu lurus | jalur = hasil `trace()` ruas lurus >= 30 m (arah s atau za) + persegi keliling blok + silang tengah; tidak ada kelengkungan |
| Tepi tajam, warna seragam | pita 2,6 m `MeshBasicMaterial` warna tunggal `0xb8ad94`, `polygonOffset`, tanpa tekstur, tanpa tepi lembut |
| Rumput menembus jalur | `GRASS_VS` hanya membuang rumput di trotoar (`sidewalkD`) dan ladang; tidak ada pengecualian untuk `PARK_PATHS` |
| Pejalan kaki di taman lurus | berjalan pada `PARK_PATHS.runs` sebagai segmen lurus (baris 14429) |

Rancangan:

1. Generator jaringan jalur: per taman, kurva Catmull-Rom melalui titik-titik yang digeser acak 3-8 m, percabangan Y, lengkung melingkar, cabang pendek ke bangku, satu jalur setapak sempit (desire path) memotong rumput. Lebar 1,8-3,2 m berubah sepanjang kurva. Titik dicek `colAt`, air, sungai, lapangan seperti `good()` sekarang, dan digeser menjauhi rintangan.
2. Medan jarak (SDF) jalur dalam satu tekstur R8: cakupan za 0 sampai 3.300 m, 2 m per piksel = 3.142 x 1.650 = sekitar 5,2 juta piksel (5,2 MB, turunan). SDF bersifat linear sepotong sehingga sampling bilinear 2 m masih akurat di tepi.
3. Pemakai SDF: shader tanah menggambar jalur (kerikil / paving, butiran `grainN`, tepi aus tidak beraturan dari `vnoise`, basah dan genangan `uWet`); `GRASS_VS` dan `MEADOW_VS` membuang atau memendekkan rumput dekat tepi (bagian dari fade 0,3 m); pita lama dihapus (tanpa z-fighting, mengikuti tanah persis, ikut bayangan dan lampu).
4. Pejalan kaki: jenis baru `kind: 'path'` mengikuti kurva (parameter panjang busur), memakai model lateral 29c.

Risiko: shader tanah adalah kode paling sensitif (aturan "otomatis High" di CLAUDE.md); tambah satu sampel tekstur per piksel, ukur dengan `GPUT`.
Penyakelaran: `?jalur=lama`.

### 29c. Jalur orang di trotoar kota terlalu lurus (foto 2)

Penyebab (kode setup `PEDS`, baris 14376-14480, dan `stepPeds`, baris 14853):

| Gejala | Penyebab |
| --- | --- |
| Berbaris satu garis | `lane()` memberi posisi lateral tetap `fix + side * (LW + (r() - 0.5) * 0.5)` = variasi +-0,25 m, lalu `p.s` / `p.za` hanya bergerak sepanjang satu sumbu |
| Dua arah di garis yang sama | `dir` acak, tidak ada lajur kanan / kiri, tidak ada penghindaran |
| Terlalu seragam | `v0 = 1,1 + 0,5 r` tetap seumur hidup, tidak pernah berhenti kecuali di zebra |
| Pantul di ujung | di `p.b` / `p.a` langsung `dir = -dir` (balik badan di tempat) |
| Heading kaku | `hd` hanya 0 / pi / +-pi/2 |

Trotoar lebar `SIDEWALK.w` = 5 m (baris 1984), jadi ruang lateral ada.

Rancangan (semua di `stepPeds`, tanpa mengubah urutan acak setup lama, generator acak sendiri seperti 22d / 23f):

| Perilaku | Aturan |
| --- | --- |
| Lajur | lajur kanan menurut arah, offset dasar +-0,7 m dari tengah, rentang lateral 0,4-2,2 m dari tepi bangunan |
| Goyang lateral | offset = dasar + noise 1D halus (panjang gelombang 8-20 m, amplitudo 0,15-0,35 m), heading mengikuti turunan |
| Kecepatan | v = v0 x (0,85-1,15) berubah pelan; berhenti 3-12 s sesekali (etalase, ponsel, ikat sepatu), perlambat di belokan |
| Kelompok | 15% berpasangan atau bertiga berdampingan (offset 0,6-0,8 m), anak tertinggal |
| Penghindaran | pada orang dalam 40 m dari mata: peta sel 4 m, dorongan lateral 0,5 m bila lawan arah < 3 m; maksimum 300 orang |
| Tujuan | di ujung potongan: belok ke jalur persimpangan (zebra) atau berbalik setelah jeda, bukan memantul seketika |

Uji (`tools/uji_pejalan_kaki.py` diperluas): simpangan baku posisi lateral >= 0,2 m selama 60 s, dua orang tidak lebih dekat dari 0,35 m, lajur dua arah terpisah >= 0,5 m, tidak menembus collider, biaya CPU `stepPeds` tidak naik > 20% dari baseline.

### 29d. Air di tepi jembatan (foto 3)

Yang terbukti di render: satu sisi trotoar jembatan tidak punya sandaran, dan jalur air biru terlihat menempel di tepi trotoar, tampak sejajar dengan permukaan trotoar (sekitar 1 m di bawahnya di layar), padahal air ada sekitar 4 m di bawah (`RIVER.depth = 4`).

Yang belum terbukti: kenapa sisi itu tanpa sandaran. Kandidat penyebab (inferensi, belum diuji):

| Kandidat | Bukti |
| --- | --- |
| K1: `deep(u, e)` salah (hanya sampel `hw + 1` m, +-6 m sepanjang; sandaran dilewati bila bantaran landai) | baris 8336 `if (!deep(u, e)) continue;` melewati sandaran, tetapi trotoar tetap dibuat |
| K2: `mouth()` salah baca persilangan | baris 8287-8292, tepi dibiarkan terbuka bila titik 3 m di luar ada di dek lain atau jalan |
| K3: sisi pelat (1,1 m) tidak terlihat dari mata di trotoar, sehingga tidak ada bidang vertikal yang menutup air | geometri: kotak pelat selebar `2 hw`, sisi menghadap luar tersembunyi dari kamera di dalamnya |
| K4: pantulan SSR trotoar pada air (`ssrRefl`) menghasilkan garis putih menempel tepi | citra: garis putih sejajar tepi trotoar |

Langkah pertama (Medium): ekspor `groundH0`, `BRIDGES`, `RIVER` ke `window.__station`, lalu sampel profil tinggi melintang di 3 jembatan (-16 sampai +22 m dari as) dan render 3 sudut (di trotoar, dari bawah, dari samping) dengan tampilan debug (air dimatikan, `hgC` diwarnai) untuk memilih antara K1-K4.

Perbaikan yang diusulkan (tergantung diagnosis): sandaran dan tepi beton di semua tepi yang bukan mulut persimpangan sungguhan; dinding tepi (fascia) turun sampai permukaan air; garis busa dan bayangan di bawah dek; SSR air diredam dekat tepi dek.

### 29e. Kaca trem: pantulan silinder, terlalu kuat (foto 4)

Penyebab (baris 5610, 5641, 5654, 5694; `SPEC_GLSL` baris 1510-1525):

| Gejala | Penyebab |
| --- | --- |
| Hanya pantulan silinder, tanpa awan atau gedung | kaca trem = `specMat(..., 0.03, 0.06, 0, true)` (`glass = 1`): pantulan hanya `farEnv`, tanpa `ssr`; sinar pantul dari dalam kabin menembus badan trem dan mengenai daratan seberang |
| Terlalu kuat sampai tidak bisa melihat keluar | `diffuseColor.a = mix(a, 1, Fr)` tanpa batas atas: pada sudut lihat miring sepanjang jendela samping (cosV kecil), Fresnel mendekati 1 dan kaca menjadi pejal; ditambah `DoubleSide` (dua lintasan) |
| Normal tidak konsisten | `PlaneGeometry(...).rotateY(Math.PI / 2)` dipakai untuk kedua sisi (sx = -1 dan +1), jadi normal selalu +x: untuk sisi kiri (sx = -1) normal menghadap ke dalam trem, sehingga deteksi sisi dalam / luar di `SPEC_GLSL` (glass = 2) tidak bisa dipakai apa adanya |

Perbaikan: pakai jalur `glass = 2` yang sudah ada untuk kaca rumah Cooper (stage 21b: dari dalam hanya memantulkan kabin redup, alpha maksimum 0,35), dengan normal diorientasikan keluar di setiap sisi (`rotateY(sx * pi / 2)`, kaca depan dan belakang per `ez`), kaca pintu `T.doorW` instance ikut. Dari luar: aktifkan `ssr` agar gedung dan pohon sekitar terpantul, `farEnv` tetap untuk awan dan daratan jauh. Alpha dari luar dibatasi 0,6.

Kriteria terukur (`tools/uji_trem_kaca.py` baru): dari kursi jendela, perbedaan rata-rata mutlak luminans area jendela antara render dengan dan tanpa kaca <= 35% (artinya >= 65% transmisi) pada 5 sudut pandang (0, 30, 60, 75, 85 derajat dari normal); tanpa nilai tidak valid.

### 29f. Tanaman gandum kurang meyakinkan (foto 5)

Penyebab (`tuftGeo`, `GRASS_VS` kind 1, baris 8768-8871):

| Gejala | Penyebab |
| --- | --- |
| Bulir seperti balok putih melayang | bulir = dua kartu bersilang selebar 1,8 cm (`e = 0,009`), tinggi 0,12 x `hf`, persegi panjang tanpa bentuk bulir dan tanpa sekam (awn) |
| Jarang | rumpun 7 helai tiap 0,3 m (hanya sekitar 78 helai per m^2, turunan: 7 / 0,09) padahal gandum nyata ratusan batang per m^2 (nilai pustaka, tidak diukur di proyek) |
| Pipih | helai satu bidang, satu warna `land * (0,9 + 0,2 h2)`, bulir hanya diterangkan `1,15` |
| Tanpa gelombang | angin per rumpun (`sway`), tanpa gelombang menjalar melintasi petak seperti `meadowGust` |

Rancangan (memakai infrastruktur kartu 29a):

1. Batang gandum khusus: batang + 2-3 daun berlengkung, rumpun 5-9 batang; jarak baris dari kanal arah baris yang sudah ada di peta petak (`fieldData().r`), jarak antarbaris 0,15-0,2 m, jitter.
2. Bulir: kerucut meruncing 8-14 vertex dengan spikelet berpasangan dan 4-6 sekam tipis; sedikit mengangguk saat masak; dua varian (berjanggut dan tidak).
3. Warna: batang keemasan pucat bergradasi, bulir madu lebih gelap, variasi per batang dan per petak; tahap hijau kebiruan berlilin; translusensi cahaya belakang.
4. Angin: gelombang menjalar melintasi petak (fase dari posisi dan angin), bulir mengangguk.
5. Lapis jauh: pola baris dan variasi warna di shader tanah (area gandum sudah berwarna menurut `wheatStage`), lapis menengah dari kartu bertekstur alfa gandum.
6. Siklus 96 jam (`wheatStage`, `uCropT`), mesin panen `FARM`, dan tunggul (`grow` 0,14) tetap bekerja.

## 3. Tabel effort

| Tahap | Isi | Berkas / fungsi disentuh | Effort | Model | Thinking |
| --- | --- | --- | --- | --- | --- |
| 29d-1 | Ekspor + diagnosis jembatan (profil tinggi, 3 sudut, tampilan debug) | `window.__station`, skrip `tools/` baru | Medium | Sonnet 5.5 | medium |
| 29d-2 | Sandaran, fascia, busa, SSR dekat tepi | `BRIDGE_G` blok (8275-8383), shader air tanah | Medium | Sonnet 5.5 | medium |
| 29e | Kaca trem jalur `glass = 2` + `ssr`, normal per sisi | `M.glass` (5610), planes (5641, 5654, 5694), `SPEC_GLSL` | High | Opus 5.5 | high |
| 29c | Model lateral, lajur, berhenti, kelompok, penghindaran | `stepPeds` (14853), `lane()` (14468), `walker()` (14376) | Medium | Sonnet 5.5 | medium |
| 29b-1 | Generator jaringan jalur melengkung | `PARK_PATHS` (14225-14265) | Medium | Sonnet 5.5 | medium |
| 29b-2 | SDF jalur + rendering di shader tanah + pembuangan rumput | `groundMat` (`TERRAIN`), `GRASS_VS`, `MEADOW_VS` | High | Opus 5.5 | xhigh (shader tanah, rawan NaN di M1) |
| 29a-1 | Atlas alfa prosedural, geometri kartu, lapis B | `tuftGeo`, `GRASS`, `MEADOW`, preset `Q` | High | Opus 5.5 | high |
| 29a-2 | Lapis A helai dekat, warna bercak, translusensi | `GRASS_VS`, `MEADOW_VS`, `vegLight` | High | Opus 5.5 | high |
| 29f | Gandum khusus (batang, bulir, baris, gelombang) | `GRASS_VS` kind 1, shader tanah gandum | High | Opus 5.5 | high |
| 29x | Uji + ukur: `tools/uji_tahap29.py`, `tools/ukur_draw_call.py` | `tools/` | Medium | Sonnet 5.5 | medium |

Bagian mekanis (entri kamus `I18N`, saklar `?rumput=lama` / `?jalur=lama`, dokumen) diserahkan ke Low.

## 4. Pengujian

| Uji | Isi |
| --- | --- |
| Termuat tanpa error | `tools/qc_load.py` di tiap tahap |
| `?rumput=lama`, `?jalur=lama` | identik dengan sebelum tahap 29 (sidik jari buffer seperti `tools/uji_pohon.py`) |
| Nilai tidak valid | baca balik buffer HDR di dekat rumput, jalur, kaca (SwiftShader tidak menampilkan NaN: periksa kondisi pembagi nol dan `pow` negatif lewat tinjauan kode) |
| Draw call dan vertex | `tools/ukur_draw_call.py`: rumput + kartu <= +4 draw call, vertex rumput <= +25% di Ultra; Hemat tidak berubah |
| FPS | pemilik menguji GTX 1060 dan M1 (sandbox tidak mewakili) |
| Trem | kriteria transmisi di 29e |
| Pejalan | kriteria simpangan lateral di 29c |

## 5. Risiko dan keputusan terbuka

| Item | Catatan |
| --- | --- |
| Jembatan | penyebab belum terbukti; 29d-1 menentukan |
| Lisensi | repo FluffyGrass berlisensi MIT (baris hak cipta 2023 Ebenezer); hanya teknik yang dipelajari, kode dan aset tidak disalin; tekstur dan geometri dibuat prosedural |
| Alfa berkedip | di preset non-Ultra tanpa TAA; mitigasi dengan alfa terkoreksi mip dan ambang jarak, atau batasi kartu ke Tinggi ke atas |
| Memori SDF | 5,2 MB (turunan); bisa dikurangi ke 4 m per piksel bila perlu |
| Urutan 29b-2 sebelum 29a | disarankan agar rumput tahu jalur sejak awal; tetapi 29a bisa jalan lebih dulu bila pemilik ingin hasil visual cepat |
| Preset | rumput fluffy (kartu) di Ultra dan Tinggi; Sedang kartu jarak lebih pendek; Rendah dan Hemat tetap rumput lama |

## 6. Cara mereproduksi (untuk sesi berikutnya)

1. `npm i three@0.186.1` di folder sementara, `pip install playwright`, gunakan Chromium bawaan `/opt/pw-browsers/chromium-1194/chrome-linux/chrome` lewat `executable_path`.
2. Muat `index.html` dengan rute `https://cdn.jsdelivr.net/**` ke folder `three/build`, tunggu `window.__stationReady`.
3. Sembunyikan `#start`, `#hud`, `#lab`, `#tourOffer`, lalu `SPOTS.zz = {s, za, heading, pitch}; teleport('zz')`; trem: set `player.state = 'tram'`, `player.seat`, `player.mode`.
4. Viewport 640 x 360, tunggu 4 s, tangkap layar.
