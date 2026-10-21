# Rumus peta corong lintasan (G8) dan arah partikel susur searah arus

Satuan: rs = 1, c = 1 (seperti seluruh misi Gargantua). Status: selesai 8 Oktober 2026. Rumus ditulis dulu, lalu kode `drawFunnel()`, `bhRadiant()`, `misGas()` di `experiences/gargantua/index.html`; uji `tools/uji_misi_gargantua.py` kelompok 8. Belum diuji di GTX 1060 dan M1.

## Ringkasan

- Peta corong = gambar ruang pada satu irisan waktu Eddington-Finkelstein masuk tetap, disematkan di ruang datar 3D: **z(r) = 2 sqrt(r)**. Berbeda dengan corong Flamm biasa, irisan ini menembus horizon sampai singularitas r = 0, dan sama dengan sumbu waktu diagram ruang-waktu G4 (tombol M).
- Posisi live dan jalur (riwayat + prakiraan) digambar di corong dengan r sebenarnya dan sudut di bidang lintasan. Jarak wajar sepanjang irisan dari singularitas: **l(r) = sqrt(r (r + 1)) + asinh(sqrt r)**.
- Susur searah arus: partikel kini datang dari arah tampak pusat lubang hitam (dulu 9-14 derajat di sampingnya, sedikit ke belakang). Susur melawan arus tidak berubah.

## 1. Irisan ruang yang dipakai

Metrik Schwarzschild dalam koordinat Eddington-Finkelstein masuk (v = waktu maju, sinar masuk v tetap):

ds² = -(1 - 1/r) dv² + 2 dv dr + r² dOmega²

Waktu irisan t~ = v - r (sama dengan `tv = T + Hin(r) - r` di diagram ruang-waktu G4). Dengan dv = dt~ + dr, pada t~ tetap (dt~ = 0):

dl² = -(1 - 1/r) dr² + 2 dr² + r² dOmega² = (1 + 1/r) dr² + r² dOmega²

Koefisien (1 + 1/r) selalu positif, jadi irisan bertipe ruang di mana-mana, juga di dalam horizon, sampai r = 0.

## 2. Penyematan (bentuk corong)

Ambil bidang lintasan (dOmega² = dphi²) dan sematkan sebagai permukaan putar di ruang datar 3D, jari-jari silinder rho = r, tinggi z(r):

dl² = (1 + (dz/dr)²) dr² + r² dphi²

Disamakan dengan irisan: (dz/dr)² = 1/r, jadi

| Rumus | Arti |
| --- | --- |
| z(r) = 2 sqrt(r) | tinggi permukaan di atas ujung singularitas |
| r = z² / 4 | jari-jari menyusut kuadratis ke bawah: corong menjadi jarum menuju singularitas (bentuk gambar acuan) |
| l(r) = integral 0..r sqrt(1 + 1/r') dr' = sqrt(r (r + 1)) + asinh(sqrt r) | jarak wajar sepanjang irisan dari singularitas |

Jauh dari lubang hitam z = 2 sqrt(r) tumbuh pelan dan kemiringannya 1/sqrt(r) menuju 0: lembar menjadi datar.

Pembanding Flamm (irisan Schwarzschild t tetap): z = 2 sqrt(r - 1), hanya r >= 1. Irisan itu tidak masuk ke dalam horizon (di sana r adalah waktu), jadi tidak bisa menggambar lintasan sampai singularitas. Di luar keduanya mirip: beda tinggi 9,381 vs 9,165 di 22 rs.

| r (rs) | z = 2 sqrt r | l dari singularitas (rs) | Flamm 2 sqrt(r - 1) |
| --- | --- | --- | --- |
| 0,6 (gerbang fiksi tesseract) | 1,549 | 1,693 | - |
| 1 (horizon) | 2,000 | 2,296 | 0 |
| 1,5 (bola foton) | 2,449 | 2,968 | 1,414 |
| 2 (orbit tak stabil) | 2,828 | 3,596 | 2,000 |
| 3 (ISCO, tepi dalam piringan) | 3,464 | 4,781 | 2,828 |
| 12 (tepi luar piringan) | 6,928 | 14,446 | 6,633 |
| 16 (awal susur) | 8,000 | 18,587 | 7,746 |
| 22 (relai, awal jatuh) | 9,381 | 24,744 | 9,165 |

## 3. Menaruh wahana di corong

- Ruang-waktu statis: semua irisan t~ sama bentuknya (simetri translasi waktu). Jadi satu corong tetap dipakai sepanjang misi, dan setiap titik lintasan ditaruh di (r, phi) miliknya. Riwayat = deretan posisi yang sudah dilewati, prakiraan = jalur tanpa dorongan (dari `misPredict()` / lintasan acuan tesseract).
- r = |x| penuh (koordinat Schwarzschild, juga jari-jari luas: keliling = 2 pi r tepat di corong).
- phi = atan2(x . e2, x . e1) di bidang lintasan. Basis: normal n = L / |L| di awal misi (L = x x dx/dtau); jatuh radial (L = 0) = bidang berisi sumbu putar dan arah awal; tesseract = basis peta orbit lama (`TES.rh0`, bidang bidikan). Dorongan yang memiringkan orbit tetap digambar (proyeksi ke bidang), seperti peta orbit tesseract.
- Horizon hanya lingkaran biasa di corong: permukaan halus, tidak ada yang terasa di sana. Yang berubah di horizon adalah arah kerucut cahaya, dan itu tampil di diagram ruang-waktu (M).
- Piringan: bila bidang lintasan hampir bidang piringan (|n . y| > 0,95, misi susur) digambar sebagai cincin rIn..rOut di corong; selain itu sebagai garis potong dua bidang (seperti peta orbit tesseract).
- Tampilan: perspektif dengan elevasi sekitar 28 derajat, azimut pelan mengikuti phi wahana agar wahana selalu di sisi depan. Bentuk sebenarnya (skala tegak sama dengan mendatar). Zoom otomatis mengikuti r wahana (sama dengan diagram ruang-waktu: Rv = 1,6 r + 1,5, dibatasi 3 sampai 24,5 rs), jadi saat dekat horizon jarum terlihat jelas.

## 4. Arah partikel saat susur searah arus

Sebelumnya: arah partikel = kecepatan gas relatif wahana (boost dari kerangka rain). Searah arus, kecepatan orbit wahana dan gas hampir sama, jadi yang tersisa hanya laju turun autopilot (vin 0,1 c ke dalam): gas mengalir keluar radial di kerangka wahana. Itu kecepatan benda bermassa, tidak ikut aberasi cahaya, sedangkan citra lubang hitam bergeser ke arah gerak wahana (v 0,24 sampai 0,56 c terhadap kerangka rain). Akibatnya titik pancar partikel ada di samping, sedikit di belakang, bukan di lubang hitam:

| r (rs) | Sumber partikel lama vs pusat lubang hitam yang tampak | Sumber partikel baru |
| --- | --- | --- |
| 11 | 9,3 derajat | 0,00 derajat |
| 8 | 10,3 derajat | 0,00 derajat |
| 4 | 13,5 derajat | 0,00 derajat |

Diukur di `tools/uji_misi_gargantua.py` kelompok 8 setelah terbang dengan autopilot (di atas 12,6 rs tidak ada debu, partikel tidak tampil). Laju gas relatif di jalur ini sekitar 0,1 c. Di kerangka pandang (hidung searah lintasan, pandang 35 derajat ke arah lubang hitam) sumber lama ada di samping dan sedikit di belakang.

Sekarang (distilisasi, hanya bila wahana searah putaran gas): arah datang = arah tampak pusat lubang hitam di kerangka wahana. Foton radial keluar dari arah lubang hitam punya arah n = r_hat di kerangka rain; wahana bergerak v (gamma) di kerangka itu. Aberasi:

p' = n + v_hat ((gamma - 1)(n . v_hat) - gamma |v|)

Arah gerak partikel = p' / |p'| (memancar menjauhi citra lubang hitam), jadi titik pancar = -p' / |p'| = pusat lubang hitam yang tampak. Laju partikel tetap |v gas relatif| dari fisika (0,10 sampai 0,12 c), jadi garis bara tetap pendek dan pelan. Arah ini dipakai garis bara, awan debu, dan titik tumbukan kaca. Melawan arus: arah tetap kecepatan gas relatif (sudah dari depan, searah piringan).

Catatan jujur: simpangan dari fisika murni sama dengan kolom tengah tabel (9-14 derajat). Dipilih supaya beda kedua arah susur jelas terlihat: melawan arus = arus deras dari depan searah piringan, searah arus = aliran pelan dari arah lubang hitam.
