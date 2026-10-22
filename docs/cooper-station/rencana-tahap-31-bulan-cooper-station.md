# Rencana tahap 31 Copper Corn Station: bulan Saturnus dan Jupiter

Per 22 Oktober 2026 · Status: K1-K8 dikerjakan (K5, K7, Hyperion, Amalthea menyusul pada hari yang sama); menunggu uji visual dan FPS pemilik · Pemilik: Bhakti · Bergantung pada tabel `PLANET` dari `rencana-tahap-30-jupiter-cooper-station.md` (langkah J1)

## Ringkasan

- Tambah bulan sungguhan yang mengorbit planet pilihan: **Saturnus** Mimas, Enceladus, Tethys, Dione, Rhea, Titan, Iapetus (Hyperion opsional); **Jupiter** Io, Europa, Ganymede, Callisto (Amalthea opsional). Posisi dari periode orbit NASA, skala sebenarnya, rotasi sinkron (muka yang sama menghadap planet).
- Fakta penting untuk ekspektasi: pada skala sebenarnya bulan tampak kecil dari stasiun. Terbesar saat konjungsi terdekat (batas bawah, planar): Enceladus 1,31 derajat, Tethys 1,75 derajat (Saturnus, orbit 260.000 km); Io 0,77 derajat (Jupiter, orbit 150.000 km). Bulan Bumi dari Bumi sekitar 0,5 derajat (nilai umum). Di luar konjungsi kebanyakan bulan 0,05 sampai 0,2 derajat, jadi hampir titik. Rencana ini menambah titik terlihat, tombol lompat ke konjungsi, dan segmen tur supaya bulan benar-benar dilihat.
- Render: bulan = anak grup planet di `farScene`, satu shader bola bersama dengan jenis permukaan prosedural (tanpa aset baru), terminator, cahaya pantulan planet, dan bayangan planet (bulan ikut gerhana). Opsi B: tekstur NASA domain publik lewat `tools/siapkan_bulan.py`.
- Urutan: data dan mekanik (K1), shader (K2), jenis khusus (K3), tampil jauh dan LOD (K4), bayangan bulan di planet (K5, opsional), UI dan tur (K6, K7), uji (K8). K1 bisa mulai begitu J1 selesai; K5 paling akhir.

## Status (22 Oktober 2026)

Keputusan pemilik: permukaan **prosedural** dulu, skala sebenarnya, tanpa Hyperion dan Amalthea, bayangan bulan di planet ditunda.

| Langkah | Hasil |
| --- | --- |
| K1 data dan mekanik | `PLANETS[*].moons` (angka NASA), `moonLocal()`, `MOONS.list` (M0 acak tetap, w = 2 pi / periode NASA), rotasi sinkron `mesh.rotation.y = -M` |
| K2 shader | `MOON_FS` Lambert + terminator, cahaya pantulan planet `uPl`, gerhana bulan `uK` dari `sunVisAt()` (rumus `updateEclipse()`) |
| K3 jenis khusus | Jenis 0 batu, 1 es (retakan), 2 Ganymede (gelap dan terang), 3 Io (belerang, bercak gelap), 4 Enceladus (garis kutub selatan), 5 Titan (kabut tepi jingga), 6 Iapetus (belahan depan gelap, perlu verifikasi arah) |
| K4 titik saat kecil | `MOONS.pts` additive, kecerahan = fase x akar(albedo) x gerhana, memudar di atas 1,5 sampai 4 piksel |
| K6 UI | HUD `hMoon` (bulan terdekat, jarak, sudut), tombol panel tab Waktu per bulan = `jumpToMoon(i)` (pemindai konjungsi langkah 60 s), kamus |
| K8 uji | `tools/uji_planet.py` |
| K5 bayangan bulan di planet | Selesai (22 Oktober 2026): `moonShadow(P)` di `SAT_COMMON` (silinder dari tiap bulan ke arah Matahari, penumbra selebar cakram Matahari pada jarak bulan, antumbra bila bulan lebih kecil dari cakram Matahari), uniform `uMoonS[8]` (xyz kerangka planet, w jari-jari dalam 1.000 km) dan `uMoonN`, diisi `updateMoons()`; `?bulan=0` = `uMoonN` 0 = shader lama persis |
| K7 tur | Selesai: titik tur `ext: 'moon'` "Bulan dari stasiun" (23 titik, 352 s): `tourMoonK()` memindai 1,5 hari orbit (langkah 60 s) untuk bulan dengan sudut terbesar yang sisi terangnya menghadap stasiun (fase >= 0,5, tidak di bayangan planet); kamera luar 3 km dari stasiun ke arah bulan, FOV menyempit ke 12 x sudut bulan (3-25 derajat, `TOUR.zoom`, `updateFov` menunggu), orbit dibekukan di konjungsi; `clock.sim` dimajukan ke kelipatan periode putaran supaya fase putaran stasiun tetap sama (rencana penutup lewat celah Skyway bergantung pada fase), lompatan di balik layar gelap |
| Hyperion dan Amalthea | Selesai: Saturnus 8 bulan (Hyperion R 139 km, periode NASA, `ecc: true` = periode Kepler dikecualikan dari uji), Jupiter 5 bulan (Amalthea R 83 km = jari-jari rata-rata bola; bentuk asli lonjong 250 x 146 x 128 km) |

Hasil uji (SwiftShader): `tools/uji_planet.py` lulus: 7 / 4 bulan, posisi kembali setelah 1 periode NASA, periode Kepler dalam 0,5% dari NASA, rotasi sinkron, jarak konjungsi hasil pemindai di antara |a - r| dan a + r (nyata: Enceladus 22.543 km, 1,28 derajat; Tethys 35.299 km, 1,72 derajat; Io 271.863 km, 0,77 derajat), gerhana bulan (Mimas, Io), bulan tergambar tanpa nilai tidak valid. Belum diuji visual dan FPS di GTX 1060 dan M1.

## Data

Sumber: NASA NSSDCA Saturnian Satellite Fact Sheet dan Jovian Satellite Fact Sheet (diambil 21 Oktober 2026). Jari-jari "~" = rata-rata tiga sumbu dari tabel NASA, dihitung oleh pengambil data. Periode di kolom 4 dihitung dari `2 pi sqrt(a^3 / GM)` sebagai pemeriksaan terhadap angka NASA.

### Saturnus (stasiun di 260.000 km)

| Bulan | a (km) | Jari-jari (km) | Periode NASA (hari) | Periode Kepler (hari) | Inklinasi (derajat) | Albedo geometrik | Jarak min (km) | Sudut di jarak min (derajat) | Sudut di jarak maks (derajat) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mimas | 185.520 | ~199 | 0,9424 | 0,944 | 1,53 | 0,6 | 74.480 | 0,31 | 0,051 |
| Enceladus | 238.020 | ~252 | 1,3702 | 1,371 | 0,00 | 1,0 | 21.980 | 1,31 | 0,058 |
| Tethys | 294.660 | ~530 | 1,8878 | 1,889 | 1,86 | 0,8 | 34.660 | 1,75 | 0,109 |
| Dione | 377.400 | ~561 | 2,7369 | 2,738 | 0,02 | 0,7 | 117.400 | 0,55 | 0,101 |
| Rhea | 527.040 | ~763 | 4,5175 | 4,518 | 0,35 | 0,7 | 267.040 | 0,33 | 0,111 |
| Titan | 1.221.870 | 2.575 | 15,9454 | 15,948 | 0,33 | 0,22 | 961.870 | 0,31 | 0,199 |
| Hyperion (opsional) | 1.500.930 | ~139 | 21,2766 | 21,712 (eksentrik, Kepler melenceng) | 0,43 | 0,3 | 1.240.930 | 0,01 | 0,009 |
| Iapetus | 3.560.850 | ~735 | 79,3302 | 79,341 | 14,72 | 0,05 / 0,5 (dua belahan) | 3.300.850 | 0,03 | 0,022 |

### Jupiter (stasiun di 150.000 km, usulan tahap 30)

| Bulan | a (km) | Jari-jari (km) | Periode NASA (hari) | Periode Kepler (hari) | Inklinasi (derajat) | Albedo geometrik | Jarak min (km) | Sudut di jarak min (derajat) | Sudut di jarak maks (derajat) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Amalthea (opsional) | 181.400 | 125 x 73 x 64 (dimensi penuh) | 0,4982 | 0,499 | 0,38 | 0,09 | 31.400 | 0,30 (bila bola 83 km) | 0,029 |
| Io | 421.800 | 1.821,5 | 1,7691 | 1,770 | 0,04 | 0,62 | 271.800 | 0,77 | 0,365 |
| Europa | 671.100 | 1.560,8 | 3,5512 | 3,552 | 0,47 | 0,68 | 521.100 | 0,34 | 0,218 |
| Ganymede | 1.070.400 | 2.631,2 | 7,1546 | 7,155 | 0,18 | 0,44 | 920.400 | 0,33 | 0,247 |
| Callisto | 1.882.700 | 2.410,3 | 16,6890 | 16,691 | 0,19 | 0,19 | 1.732.700 | 0,16 | 0,136 |

Catatan tabel:

- Jarak min = `|a - r_stasiun|` dan maks = `a + r_stasiun` dengan stasiun dan bulan sebidang dan lingkaran. Ini batas: bidang orbit stasiun dimiringkan terhadap bidang khatulistiwa planet (`ORBIT.tiltDeg` 15 derajat di Saturnus), sehingga jarak sebenarnya terdekat lebih besar. Nilai tepat dihitung oleh uji K8 dengan memindai waktu.
- Sudut = `2 atan(R / d)`. Amalthea memakai radius 83 km hanya untuk perkiraan sudut (bentuknya lonjong).
- Periode Kepler cocok dengan NASA dalam 0,3% untuk semua selain Hyperion (orbit eksentrik); kode memakai periode NASA.

## Rancangan

| Topik | Keputusan |
| --- | --- |
| Kerangka | Bulan menjadi anak grup `saturn` (nama grup tetap, berlaku untuk planet apa pun) sehingga ikut rotasi dan kemiringan planet; posisi lokal `a (cos M, sin(inc) sin M, sin M cos(inc))` di bidang khatulistiwa (XZ lokal), `M = M0 + 2 pi t / P` |
| Waktu | `clock.orbit` (detik simulasi, ikut `ORBIT_SPEEDS` dan tombol T) seperti `orbitPhase()`; `M0` acak tetap per bulan (benih) supaya tidak semua sejajar saat mulai, dengan satu "konjungsi pemandu" tetap agar tur bisa merencanakan |
| Rotasi | Sinkron: `spin = M` (muka yang sama ke planet). Hyperion: jungkir balik pelan (opsional) |
| Skala | Sebenarnya. Tidak ada pembesaran bulan |
| Tampil jauh | Di bawah sekitar 1,5 piksel dipakai sprite titik dengan kecerahan `albedo x R^2 / d^2` (batas bawah supaya tetap terlihat), seperti `glareMat` Matahari. Sudut piksel dari FOV kamera jauh |
| Pencahayaan | Terminator Lambert dari `uSunL` (arah Matahari di kerangka lokal planet, tetap), cahaya pantulan planet kecil (arah ke pusat planet, `uSatCol`), gelap tepi ringan; ikut gerhana: bulan di bayangan planet meredup (uji sinar-ellipsoid seperti `updateEclipse()`, per bulan di CPU, lalu uniform `uK`) |
| Permukaan | Prosedural per jenis (noise 3D, kawah): `rock` (kawah padat, Callisto, Mimas dengan kawah besar), `ice` (putih, retak cokelat, Europa, Tethys, Dione, Rhea), `ganymede` (belahan terang dan gelap), `io` (belerang kuning, bercak gelap), `enceladus` (putih terang, garis harimau di kutub selatan), `titan` (bola jingga halus berkabut: cangkang tepi seperti `limbMat`), `iapetus` (dua belahan: depan gelap albedo 0,05, belakang terang 0,5; muka depan = arah gerak orbit, dari NASA dua nilai albedo, asal-usul tampilan perlu diverifikasi), `small` (Hyperion, Amalthea: bola dipepat dan kasar) |
| Mutu sumber | Opsi A prosedural (usulan, tanpa aset). Opsi B tekstur NASA domain publik 1024 x 512 JPEG base64 di `assets/bulan.data.js` lewat `tools/siapkan_bulan.py` (cara sama dengan `siapkan_rumput.py`), lisensi di `assets/KREDIT.md`; tampil lebih meyakinkan saat konjungsi, dengan harga ukuran berkas |
| Biaya | 8 bola maksimal per planet: 8 draw call kecil di `farScene`; segmen bola per jarak (LOD) |

## Langkah

Effort mengikuti tabel di `CLAUDE.md`.

| No | Langkah | Isi | File dan fungsi | Effort | Model | Thinking |
| --- | --- | --- | --- | --- | --- | --- |
| K1 | Data dan mekanik | `MOONS` di tabel `PLANET` (nama, a, R, P NASA, inklinasi, albedo, jenis); `moonLocal(m, t)`, `moonDir(m, out)` (arah ke stasiun, jarak, sudut); tanpa render dulu | `experiences/cooper-station/index.html`: blok TAHAP 3 dekat `saturnDirInertial()`, `PLANET` dari J1; ekspor di `window.__station` | Medium | Sonnet 5.5 | medium |
| K2 | Shader bulan dasar | Satu `ShaderMaterial` bola: terminator, pantulan planet, gelap tepi, kawah prosedural, uniform `uType`, `uAlb`, `uK`; mesh per bulan di `saturn.add(...)`; tidak merusak `renderOrder` cincin dan `limb` | blok shader dekat `planet` / `rings` / `limb` | High | Opus 5.5 | high (rawan NaN: jangan `normalize()` vektor nol, jangan `pow()` negatif, aturan di `CLAUDE.md`) |
| K3 | Jenis khusus | Titan (kabut), Enceladus (garis harimau, opsional semburan titik), Io, Iapetus dua belahan, Ganymede, bentuk kecil Hyperion dan Amalthea | shader K2 + `MOON_TYPES` | Medium | Sonnet 5.5 | medium |
| K4 | Tampil jauh dan LOD | Sprite titik saat < 1,5 piksel; segmen bola per jarak; frustum culling; tidak bergantung ukuran jendela | pembuat mesh bulan, `updateFar()` | Medium | Sonnet 5.5 | medium |
| K5 | Bayangan bulan di planet (opsional) | Uniform array posisi dan radius bulan; di shader planet uji sinar-bola ke Matahari (bayangan bulat kecil saat transit); transit Titan atau Io | `SAT_U`, fragmen shader planet (J2 untuk Jupiter) | High | Opus 5.5 | high |
| K6 | UI dan HUD | Baris HUD "bulan terdekat" (nama, jarak km, sudut, fase); panel tab baru atau baris di Grafik: daftar bulan, tombol "Lompat ke konjungsi {bulan}" (pemindai waktu seperti `jumpToEclipse()`), saklar label nama bulan di kamera luar (V); teks lewat `t()` dan `I18N.en` | `LABUI`, `labTab`, `uiLabel`, `jumpToMoon(id)` baru, `hEl`, `I18N.en` | Medium | Sonnet 5.5 | medium |
| K7 | Tur | Segmen baru di `TOUR`: kamera luar mengejar konjungsi terdekat bulan terbesar (caption fakta: nama, jarak, sudut); tur lama tidak berubah bila bulan dimatikan | `tourKeys()`, `stepTour()`, `tourOutroPlan()` | Medium | Sonnet 5.5 | medium |
| K8 | Uji | Lihat bagian Uji | `tools/uji_bulan.py` baru, `tools/uji_gerhana.py`, `tools/uji_bahasa.py` | Medium | Sonnet 5.5 | medium |

Opsi B (tekstur NASA): `tools/siapkan_bulan.py` + `assets/bulan.data.js` + `assets/KREDIT.md`, tambahan Medium (Sonnet 5.5, medium) setelah K3.

## Uji

| Uji | Isi | Kriteria |
| --- | --- | --- |
| Mekanik | Posisi tiap bulan setelah 1 periode NASA kembali ke titik awal; jarak ke pusat planet = `a` | Galat < 0,01 derajat |
| Sudut tampak | Konjungsi terdekat per bulan hasil pemindai vs rumus `2 atan(R/d)` | Galat < 1% |
| Sinkron | Normal muka bulan yang menghadap planet tetap menghadap planet sepanjang orbit | Galat < 0,1 derajat |
| Gerhana bulan | Bulan masuk bayangan planet meredup mulus, keluar menyala; tanpa nilai tidak valid | Kecerahan turun ke < 5% di umbra |
| Tanpa NaN | Render bulan dekat (lompat konjungsi) dan jauh, 5 preset | 0 nilai tidak valid, 0 titik > 50 |
| Planet identik | Bulan dimatikan (`?bulan=0` atau saklar): render sama dengan sebelum tahap 31 | 0 piksel berbeda |
| Bahasa | Kunci baru di `I18N.en` | `tools/uji_bahasa.py` lulus |
| Performa | Draw call dan waktu frame `GPUT` dengan dan tanpa bulan | Tambah draw call <= 9; waktu frame dicatat |

Pemilik menguji visual dan FPS di GTX 1060 dan M1.

## Pilihan untuk pemilik

| No | Pertanyaan | Pilihan | Disarankan |
| --- | --- | --- | --- |
| 1 | Sumber permukaan | a. Prosedural (tanpa aset) · b. Tekstur NASA domain publik (+ aset base64) | a dulu, b bila hasil kurang meyakinkan |
| 2 | Skala bulan | a. Sebenarnya (kebanyakan tampak kecil) · b. Ada saklar "perbesar bulan" (pembesaran sudut, ditandai jelas sebagai tidak nyata) | a, dengan lompat konjungsi dan tur |
| 3 | Bulan kecil | Hyperion dan Amalthea: a. Sertakan · b. Lewati | b pada versi pertama |
| 4 | Bayangan bulan di planet (K5) | a. Sertakan · b. Tunda | b (kerja besar, nilai visual sedang) |

## Risiko dan batasan

| Risiko | Penjelasan | Penanganan |
| --- | --- | --- |
| Harapan visual | Dengan skala sebenarnya bulan jarang terlihat besar; tanpa titik terlihat dan lompat konjungsi fitur ini nyaris tidak terasa | Sprite titik (K4), tombol konjungsi (K6), tur (K7) |
| Jarak sebenarnya lebih jauh | Tabel memberi batas bawah bidang sama; konjungsi nyata lebih jauh sehingga sudut puncak lebih kecil dari yang tertulis | Hitung dengan pemindai di K8 dan tulis nilai nyata di dokumen setelah implementasi |
| Iapetus dua belahan | Orientasi belahan gelap (muka depan) berasal dari pengetahuan umum, bukan dari lembar fakta yang diambil | Verifikasi sebelum K3 |
| Sensitivitas NaN | Shader baru di M1 | Aturan NaN di `CLAUDE.md`, uji, dan pemeriksaan pemilik |
| Ketergantungan | Perlu `PLANET` dari tahap 30 (J1); tanpa itu hanya Saturnus yang bisa dikerjakan | K1 menunggu J1 |
| Pengukuran | Estimasi waktu kerja tidak diberikan | Hanya label effort |
