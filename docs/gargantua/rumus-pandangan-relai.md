# Rumus pandangan relai 22 rs (G9)

Satuan: rs = 1, c = 1, M = 0,5. Kode: `relViewInit()`, `relImage()`, `imageDir()`, `rayPhi()`, `drawRelayView()` di `experiences/gargantua/index.html`; uji `tools/uji_misi_gargantua.py` kelompok 9.

## Ringkasan

- V saat misi kini berputar: kamera luar, kokpit, relai. Pandangan relai = ray tracer yang sama dengan kamera di relai 22 rs, menghadap lubang hitam.
- Wahana 20 m dari jarak 1e9 sampai 6e9 km tidak mungkin terlihat sebagai benda (sudut sekitar 1e-8 rad). Yang tampil adalah cahaya pulsa wahana (G4): titik bercahaya dengan warna dan terang mengikuti faktor frekuensi, di posisi citra lensa yang dihitung dengan persamaan sinar yang sama dengan shader.
- Relai melihat masa lalu wahana (cahaya tertunda): gambar melambat, memerah, padam, dan membeku tepat sebelum horizon. Suar E muncul sebagai kilat ketika cahayanya tiba; suar dari dalam horizon tidak pernah tiba.

## 1. Posisi dan gerak relai

| Item | Rumus / nilai |
| --- | --- |
| Arah relai | arah awal wahana diputar 120 derajat di bidang lintasan (`FUN.e1`, `FUN.e2`), lalu dimiringkan 20 derajat keluar bidang ke sisi tempat wahana berada (misi susur: sisi yang sama dengan wahana, jadi cahaya tidak tertutup piringan) |
| Jarak | 22 rs, ditahan tetap selama misi (orbit relai 2 pi sqrt(r³ / M) = 917 rs/c = 10,4 hari; misi 1 sampai 150 rs/c) |
| Kecepatan (untuk aberasi) | orbit melingkar: L = sqrt(M r² / (r - 1,5)) = 3,436, dx/dtau = L / r arah n x r_hat; kerangka rain dari `rainOf()` |
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

Titik pancar x_e (posisi wahana saat cahaya berangkat) dan relai menentukan satu bidang dan sudut Dphi di antara keduanya. Sudut sapu sinar sampai r_e naik monoton sepanjang jalur:
1. cabang masuk: psi dari 0 sampai periapsis = r_e (atau sampai batas tangkap bila r_e < 1,5),
2. cabang keluar (lewat periapsis, titik di belakang lubang hitam): psi turun ke batas tangkap.
Bisection 40 langkah sampai sudut sapu = Dphi. Bila r_e > 22 (wahana lolos menjauh): satu cabang keluar dari psi 180 derajat.

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

## 5. Waktu dan suar

- Waktu relai TR = T + Tx (G4). Keadaan wahana yang terlihat = `relSeen(TR)` (kini juga memberi posisi x hasil interpolasi log).
- Waktu tiba tetap model radial G4 (`relArrive()`); tunda tambahan karena relai tidak tepat di atas wahana (beda lintasan beberapa rs/c) diabaikan.
- Suar E: tiba saat TR >= `F.arr`. Kilat cyan di citra titik tembak, warna inti mengikuti faktor frekuensi saat tembak. Suar dari dalam horizon: `F.arr` tak hingga, tidak pernah tampil.
