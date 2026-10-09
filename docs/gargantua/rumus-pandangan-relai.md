# Rumus pandangan relai 22 rs (G9)

Satuan: rs = 1, c = 1, M = 0,5. Kode: `relViewInit()`, `relUpdate()`, `relImage()`, `imageDir()`, `rayPhi()`, `drawRelayView()` di `experiences/gargantua/index.html`; uji `tools/uji_misi_gargantua.py` kelompok 9.

## Ringkasan

- V saat misi kini berputar: kamera luar, kokpit, relai. Pandangan relai = ray tracer yang sama dengan kamera di relai 22 rs, menghadap lubang hitam.
- Wahana 20 m dari jarak 1e9 sampai 6e9 km tidak mungkin terlihat sebagai benda (sudut sekitar 1e-8 rad). Yang tampil adalah cahaya pulsa wahana (G4): titik bercahaya dengan warna dan terang mengikuti faktor frekuensi, di posisi citra lensa yang dihitung dengan persamaan sinar yang sama dengan shader.
- Relai melihat masa lalu wahana (cahaya tertunda): gambar melambat, memerah, padam, dan membeku tepat sebelum horizon. Suar E muncul sebagai kilat ketika cahayanya tiba; suar dari dalam horizon tidak pernah tiba.

## 1. Posisi dan gerak relai

| Item | Rumus / nilai |
| --- | --- |
| Arah relai | revisi 8 Oktober: selalu di atas piringan, elevasi 20 derajat (seperti pandangan film); azimut = proyeksi mendatar arah awal wahana + 120 derajat (jatuh dari kutub: sumbu x). Versi pertama memakai tanda x . n untuk sisi, padahal x selalu tegak lurus n, jadi relai jatuh di bawah piringan |
| Jarak | 22 rs, ditahan tetap selama misi (orbit relai 2 pi sqrt(r³ / M) = 917 rs/c = 10,4 hari; misi 1 sampai 150 rs/c) |
| Kecepatan (untuk aberasi) | orbit melingkar searah putaran piringan: L = sqrt(M r² / (r - 1,5)) = 3,436, dx/dtau = L / r; kerangka rain dari `rainOf()` |
| Arah kamera | otomatis ke garis bagi antara pusat lubang hitam dan citra wahana (dihaluskan), FOV 70 derajat, jadi keduanya di layar; seret = manual, klik ganda = otomatis lagi |
| Posisi bebas (revisi 2) | seret kiri = relai berpindah di bola 22 rs (azimut bebas, elevasi -85 sampai 85 derajat, juga di bawah piringan); seret kanan / Ctrl + seret = arah pandang; roda = zoom FOV 25-100 derajat; klik ganda = posisi, FOV, dan arah awal. Jarak tetap 22 rs, jadi jam relai dan waktu tiba (model G4) tidak berubah; citra dihitung ulang dari posisi baru, jejak dibangun ulang dari log setelah seret dilepas (`relPlace()`) |
| Warna jejak | ungu muda di atas garis gelap lebar, beda dari piringan (jingga-putih), suar (cyan), dan relai (hijau) |
| Jam relai | sqrt(1 - 1,5 / 22) = 0,9653 (sama dengan G4) |

## 2. Citra wahana (gambar primer)

Shader menelusuri sinar mundur dari kamera dengan x'' = -1,5 h² x / r^5, laju datar 1 di kamera, h = |x x v| tetap (persamaan Binet persis untuk Schwarzschild). Dalam bentuk orbit, u = 1/r:

- u'' = -u + 1,5 u²
- awal di relai: u0 = 1/22, u' = cot(psi) / r0, h = r0 sin(psi), psi = sudut dari arah pusat
- integral pertama (laju 1 di relai, bukan di tak hingga): u'² = 1/h² + u³ - u0³ - u²

Batas analitik dari integral pertama:

| Batas | Syarat |
| --- | --- |
| Tertangkap horizon | 1/h² - u0³ < 4/27 |
| Periapsis tepat di r_e | 1/h² = ue² - ue³ + u0³ |

Titik pancar x_e (posisi wahana saat cahaya berangkat) dan relai menentukan satu bidang dan sudut Dphi di antara keduanya. Sudut sapu sinar sampai r_e naik monoton di tiap cabang:
1. cabang masuk: psi dari 0 sampai titik singgung (periapsis tepat di r_e), atau sampai batas tangkap bila r_e < 1,5,
2. cabang keluar (lewat periapsis, titik di belakang lubang hitam): psi dari titik singgung turun ke batas tangkap.
Cabang dipilih dengan membandingkan Dphi terhadap sudut sapu di titik singgung (Dphi <= itu = cabang masuk), lalu bisection 42 langkah di cabang itu. Sinar yang hampir menyinggung r_e (u maks >= ue (1 - 1e-6)) dihitung sampai periapsis. Bila r_e > 22 (wahana lolos menjauh): satu cabang keluar dari psi 180 derajat.

Revisi 8 Oktober: versi pertama memilih cabang dengan mencoba ujung cabang masuk; di dekat titik singgung hasilnya kadang kosong, lalu bisection jatuh ke cabang salah. Citra melompat antara posisi benar dan 50-80 derajat dari pusat, terlihat sebagai garis tegak (jatuh lurus) dan zigzag (susur searah arus). Sekarang: jatuh lurus dari 22 rs sudut citra turun monoton (57,5 ke 26,6 derajat dari pusat), susur searah arus lompatan antar sampel paling besar 2,5 derajat, 200 titik acak selisih sinar paling besar 2,4e-5 rs.

Uji: sinar dari arah hasil diintegrasikan ulang 3D melewati titik pancar dengan selisih 6e-9 sampai 1,8e-6 rs (11 titik: depan, samping, tepat di belakang lubang hitam, r 1,01 sampai 60).

## 3. Arah di layar (aberasi relai)

Shader (kerangka relai -> kerangka rain): n_p = -dir, p_r = n_p + v (gamma + gamma² / (gamma + 1) v . n_p), n_r = p_r / |p_r|, vel0 = norm(-n_r + beta r_hat).

Balikan:
- n_r = beta r_hat - k vel0, k = beta c + sqrt(beta² c² - beta² + 1), c = r_hat . vel0
- n_p = norm(n_r + v (-gamma + gamma² / (gamma + 1) v . n_r))
- arah layar dir = -n_p

## 4. Terang, warna, dan piringan

- Faktor frekuensi = `relSeen().rate` (G4: Doppler x dilatasi, turun e tiap 2 rs/c waktu relai di dekat horizon). Warna `relColor(rate)`, terang rate² (sama dengan jendela relai). Cincin tipis tetap digambar agar posisinya terlihat walau cahayanya padam.
- Sinar yang menembus bidang piringan di rIn..rOut sebelum tiba = citra di balik piringan (kekeruhan 0,9): titik diredupkan dan diberi label.

## 5. Waktu, horizon, dan suar

- Waktu relai TR = T + Tx (G4). Keadaan wahana yang terlihat = `relSeen(TR)` (kini juga memberi posisi x hasil interpolasi log).
- Waktu tiba tetap model radial G4 (`relArrive()`); tunda tambahan karena relai tidak tepat di atas wahana (beda lintasan beberapa rs/c) diabaikan.
- Suar E: tiba saat TR >= `F.arr`. Kilat cyan di citra titik tembak, warna inti mengikuti faktor frekuensi saat tembak. Suar dari dalam horizon: `F.arr` tak hingga, tidak pernah tampil.

| Pertanyaan | Jawaban |
| --- | --- |
| Toast "melewati horizon" muncul saat titik masih di r 3,47 | Benar. Toast memakai jam wahana; titik di pandangan relai adalah cahaya tertunda. Saat wahana melewati horizon, cahaya terbaru yang tiba di relai berangkat dari r 3,47. Relai tidak pernah melihat wahana lewat: citra makin lambat, merah, dan padam di luar horizon. Di pandangan relai toast kini berbunyi demikian, dan di bawah titik muncul "sudah di dalam horizon" |
| Suar muncul di posisi terakhir yang terlihat atau di posisi saat E ditekan | Keduanya sama. Kilat muncul di posisi saat E ditekan. Cahaya suar dan pulsa wahana dari saat yang sama menempuh jalan yang sama, jadi saat kilat tiba, titik wahana yang terlihat relai tepat berada di posisi itu (uji: selisih tau 0, selisih posisi 1,8e-15 rs) |

- Penanda "sekarang": lingkaran putus-putus di citra posisi wahana saat ini (cahayanya belum tiba). Jarak antara penanda itu dan titik wahana = tunda cahaya. Di dalam horizon penanda hilang (tidak ada sinar yang keluar).
- Jejak dibangun dari log sejak awal misi (cahaya yang sudah tiba): sekitar 200 titik, dicicil paling banyak 4 citra per frame. Revisi 3 (9 Oktober), lihat bagian 6.
- Kartu akhir misi tidak lagi menutup layar: bawaan di kanan (12 px dari tepi, lebar maks 500 px, tengah tegak) supaya pandangan relai yang masih berjalan terlihat, latar tembus, kepala bisa diseret, x menutup, tombol "Ringkasan misi" di atas membukanya lagi. Pandangan relai tetap berjalan (waktu relai lanjut, suar yang masih di jalan tetap tiba).

## 6. Jejak di sudut pandang rendah (revisi 3)

Masukan Bhakti: relai dipindah hampir sejajar piringan, jejak tampak bergerigi / kotak.

| Sebab | Bukti (susur melawan arus, relai 4,6 derajat) |
| --- | --- |
| Jejak diambil tiap 3 entri log tanpa pengisian. Dekat lubang hitam lensa kuat dan sudut pandang rendah, jadi titik berurutan terpisah jauh di layar dan tergambar sebagai tali busur lurus | lompatan antar titik jejak sampai 6,1 derajat (di r 2,27) |
| Log relai juga renggang menurut sudut: entri disatukan selama tau < 0,05 dan r hampir tetap, padahal di orbit hampir melingkar wahana berpindah sudut | entri berurutan pun melompat sampai 2,5 derajat |

Perbaikan:

| Bagian | Isi |
| --- | --- |
| `relLog()` | entri baru juga dibuat bila arah posisi berubah > 0,5 derajat dari entri sebelumnya (cos > 0,99996). `relSeen()` dan model waktu tiba G4 tidak berubah, hanya interpolasi lebih halus |
| `relUpdate()` | titik tetap diambil tiap stride entri; bila citra melompat > 0,8 derajat dari titik sebelumnya (cos < 0,9999), titik tengah (indeks pecahan, posisi diinterpolasi linear di log) disisipkan lewat tumpukan sampai lompatan <= 0,8 derajat atau selisih indeks < 0,05 |
| Biaya | paling banyak 4 citra per frame. SwiftShader (CPU): 2,5 sampai 4,1 ms per frame selama jejak dibangun (80 sampai 89 frame), lalu 0 |

Hasil (uji kelompok 9, relai 4,6 derajat):

| Skenario | Titik jejak | Lompatan maks |
| --- | --- | --- |
| Susur melawan arus | 286 | 0,81 derajat |
| Susur searah arus | 269 | 0,80 derajat |
