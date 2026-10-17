# Rencana Gargantua: planet Millar mengorbit dan suasana Kelam

Per 17 Oktober 2026 · Bhakti · Revisi 1 (dari 2 foto contoh)

## Ringkasan

- **Planet Millar (foto 1):** bola gelap kecil mengorbit Gargantua, ikut dijejak sinar di `SCENE_FS` (terlihat dibelokkan lensa, bisa muncul dua kali, menutupi piringan), disinari piringan dari satu sisi, angka orbit dan dilatasi waktu di HUD. Ukuran diperbesar (ukuran nyata < 0,01 piksel, lihat Angka).
- **Suasana Kelam sebagai tampilan bawaan (foto 2):** palet piringan krem-putih ke karat (kurang jenuh), lembar debu gelap menyerap cahaya di depan dan di sekitar piringan, asap redup di luar tepi piringan, nebula gelap di langit, bintang lebih jarang, eksposur dan vinyet lebih kelam. Tombol N = Kelam / Klasik.
- **Tampilan lama tetap utuh:** `?mood=klasik` dan `?millar=0` (atau N dan panel) memberi render identik dengan sekarang, pola sama dengan `uV4` (0 = perilaku lama persis). Uji lama memakai saklar ini.

Urutan kerja: MK1 Millar di shader, MK2 Millar di CPU / HUD / panel, MK3 palet dan grade Kelam, MK4 lembar debu, MK5 langit gelap, MK6 saklar dan bawaan, MK7 uji, MK8 bahasa dan dokumen. Tiap kelompok berhenti untuk diuji pemilik di GTX 1060 dan M1.

Cara menjalankan di sesi baru: "jalankan kelompok 1 dari `docs/gargantua/rencana-millar-dan-suasana-kelam.md`".

## Apa yang dibaca dari foto

| Foto | Ciri | Dibuat dengan |
| --- | --- | --- |
| 1 | Planet kecil gelap di ruang gelap dekat sisi piringan, tepi samar tersinari | Bola dijejak sinar, albedo rendah, cahaya dari arah piringan dalam, pinggir atmosfer tipis |
| 1 | Planet tampak di depan piringan terang | Bola menutup sinar (komposit depan ke belakang bersama piringan) |
| 2 | Warna putih krem di inti, peach, coklat karat di luar; hampir tanpa jingga jenuh | Palet baru `moodRamp()` menggantikan `filmRamp()` saat Kelam |
| 2 | Gumpalan debu gelap menutup bagian bawah piringan depan, tepi gumpalan tersinari karat | Lembar debu penyerap tipis bertumpuk di atas dan di bawah bidang piringan |
| 2 | Piringan tampak tebal dan berasap, tepi luar berkabut | Lembar debu melebar sampai sekitar 2x `rOut`, emisi lemah dari hamburan cahaya piringan |
| 2 | Cincin foton tipis tajam di tepi bayangan | Sudah muncul dari ray tracer; hanya dicek tidak tertutup debu (debu mulai di r >= 3,5 rs) |
| 2 | Langit hitam pekat, nebula debu samar, bintang jarang | `sky()`: awan gelap skala besar menyerap bintang, kerapatan bintang turun |

## Angka (rs = 1, M = 0,5, satuan waktu rs/c)

| Item | Nilai | Derivasi |
| --- | --- | --- |
| Dilatasi orbit lingkaran Schwarzschild | dt/dtau = 1 / akar(1 - 1,5 rs / r) | Rumus orbit lingkaran Schwarzschild |
| Dilatasi di ISCO r = 3 rs | 1,414x | 1 / akar(0,5); sama dengan nilai Kerr a = 0 di `tools/uji_detail_millar.cjs` |
| Dilatasi di r = 4 rs | 1,265x | 1 / akar(0,625) |
| Dilatasi di r = 14 rs | 1,058x | 1 / akar(0,89286) |
| Angka film 61.362x | Butuh Kerr hampir ekstrem, 1 - a sekitar 1,33e-14 | `docs/millar/detail/`, `tools/diagram_detail_millar.py`; tidak bisa di Schwarzschild |
| Periode orbit (koordinat) r = 4 rs | 71,1 rs/c | 2 pi akar(r^3 / M) |
| Periode orbit r = 14 rs | 465,5 rs/c, sekitar 155 s di layar pada kecepatan 1 | `CONFIG.timeScale` 3 satuan per detik |
| Rasio radius planet nyata / rs | sekitar 2,8e-5 | R_P 8.282 km (`CONFIG` Millar) / rs 2,95e8 km (1e8 massa Matahari) |
| Planet nyata di layar | sekitar 0,0015 piksel radius | Jarak kamera 22 rs, FOV 55 derajat, tinggi 1.080 px |
| Radius tampil | 0,06 rs (diperbesar sekitar 2.100x), panel 0,02-0,3 (revisi; awalnya 0,2 rs terlalu besar) | Foto 1: radius planet sekitar 1,2% tinggi gambar |

Yang ditampilkan di HUD: r orbit, periode, dilatasi Schwarzschild dari rumus di atas, plus catatan "angka film butuh Kerr hampir ekstrem" dan "ukuran planet diperbesar". Tidak ada angka 61.362x yang dihitung dari spin di ray tracer ini (spin di shader adalah pendekatan berlabel, bukan Kerr).

## Kelompok menurut effort, model, dan thinking

| Kelompok | Tahap | Isi | Effort | Model | Thinking | File dan fungsi | Risiko |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | MK1 | Bola Millar di loop sinar `SCENE_FS`: uniform `uPl` (pusat xyz, radius w), `uPlOn`, uji potong segmen-bola antara `prev` dan `pos` tiap langkah, urutan dengan perpotongan piringan di langkah yang sama (bandingkan parameter t), warna planet `shadePlanet()` (albedo laut 0,06, pita awan fbm, cahaya dari arah lubang hitam + dari bidang piringan, pinggir atmosfer), `state = 3` saat kena | High | Opus 5.5 | xhigh | `SCENE_FS` `main()`, fungsi baru `planetHit()` / `shadePlanet()` | NaN M1 di akar diskriminan dan `normalize`; langkah besar (dt sampai 2,5) tetap aman karena uji potong memakai tali busur |
| 1 | MK2 | Orbit di CPU: `MILLAR` (on, r, inc, rad, ph), posisi Kepler omega = akar(M / r^3) dengan jam yang sama dengan piringan, uniform tiap frame, preset orbit "Dekat piringan" r 13 / kemiringan 6 derajat dan "Film" r 4 di bidang piringan, panel tab Piringan bagian Millar, baris HUD `drawDash()`, localStorage `gargantua.millar`, `?millar=0`; mati saat misi (`MIS.on`) | Medium | Sonnet 5.5 | medium | `CONFIG`, `UI`, `drawDash()`, loop frame | Rendah |
| 2 | MK3 | Palet Kelam `moodRamp()` (putih krem, peach, karat, coklat tua), uniform `uMood`; mode fisika tetap benda hitam, hanya debu dan langit ikut; grade di `COMPOSITE_FS` (eksposur 0,85, vinyet 0,55, hitam lebih dalam, kejenuhan turun) | Medium | Sonnet 5.5 | medium | `SCENE_FS` `shadeDisk()`, `COMPOSITE_FS`, `CONFIG.post` | Rendah |
| 2 | MK4 | Lembar debu: 2 sampai 4 bidang tipis y = +-h (h 0,25-0,9 rs, makin jauh makin tebal mengikuti r), r 3,5 sampai sekitar 24 rs, kerapatan fbm skala besar berputar Kepler (trik dua fase `uFlowPeriod` seperti `diskDensity()`), serap (trans *= 1 - a) + emisi hamburan lemah dari Tn piringan setempat, warna karat; tepi radial dan tepi kerapatan halus (pelajaran G3a: batas lempeng tebal tampak sebagai lingkaran, jadi tidak ada batas tajam), sisi bawah depan lebih pekat seperti foto 2 | High | Opus 5.5 | high | `SCENE_FS` loop sinar (uji silang bidang seperti piringan), fungsi baru `dustSheet()` | Biaya GPU (fbm per silang per lembar); tampak berlapis bila jarak lembar terlalu besar; harus dinilai di GPU asli |
| 2 | MK5 | Langit Kelam di `sky()`: awan molekul gelap skala besar menyerap bintang dan pita galaksi, debu coklat samar, kerapatan bintang turun sekitar 40% | Medium | Sonnet 5.5 | medium | `sky()`, `starLayer()` | Rendah |
| 3 | MK6 | Saklar: N = Kelam / Klasik (`cycleMood()`, localStorage `gargantua.mood`, `?mood=klasik`), Kelam bawaan; jumlah lembar per kualitas (Rendah 1, Sedang 2, Tinggi 3, Ultra 4 di `CONFIG.presets` `dust`), resolusi adaptif tetap; saat misi lembar debu dekat wahana diredam agar tidak bertabrakan dengan `drawDust()` | Medium | Sonnet 5.5 | medium | `CONFIG.presets`, penangan tombol, `UI` | Rendah |
| 3 | MK7 | Uji di `tools/uji_misi_gargantua.py` (kelompok baru): `uMood` 0 dan `uPlOn` 0 = render identik dengan sebelum perubahan (dibanding commit dari riwayat git), tanpa nilai tidak valid di semua kualitas dan kamera preset 1-4, planet menutup piringan (piksel pusat planet gelap), citra kedua planet di sisi seberang lubang hitam ada saat planet di belakang, dilatasi HUD = rumus; uji lama diberi `?mood=klasik&millar=0` bila membandingkan tampilan bawaan; `tools/ukur_muat.py gargantua --cek` | Medium | Sonnet 5.5 | medium | `tools/uji_misi_gargantua.py` | Rendah |
| 3 | MK8 | Kamus `ID` (sumber English), bantuan, `docs/app/tombol.md` (N di Gargantua), CLAUDE.md, Status di dokumen ini | Low | Haiku 4.5 | low | `ID`, `buildUI()`, dokumen | Rendah |

Tambahan opsional (tidak dikerjakan tanpa diminta):

| Usulan | Isi | Effort |
| --- | --- | --- |
| O1 | Bayangan planet di piringan (titik gelap kecil ikut orbit) | Medium |
| O2 | Planet dan debu di hero `experiences/gargantua/detail.html` (`heroPaint()`) | Medium |
| O3 | Foto menu `menu.webp` dan `preview.jpg` baru dari tampilan Kelam | Low |
| O4 | Waktu tunda cahaya per citra planet (citra kedua menunjukkan posisi lebih lama) | High |

## Keputusan yang perlu dari Bhakti

| Pertanyaan | Usulan bawaan |
| --- | --- |
| Orbit bawaan planet | "Dekat piringan" r 13 rs, kemiringan 6 derajat (tampak di atas piringan seperti foto 1); "Film" r 4 rs di bidang piringan sebagai pilihan |
| Radius tampil planet | 0,2 rs |
| Planet saat misi | Disembunyikan (uji misi tetap identik) |
| Kelam di mode fisika (Doppler) | Debu dan langit ikut, palet piringan tetap benda hitam |
| Lembar debu saat misi terbang rendah | Diredam dalam 2 rs dari wahana |

## Batasan

- Ukuran planet bukan skala nyata; tanpa pembesaran planet tidak terlihat (0,0015 piksel).
- Ray tracer Schwarzschild: dilatasi planet paling besar 1,414x di ISCO. Angka film 61.362x hanya bisa dijelaskan dengan Kerr hampir ekstrem dan dicatat sebagai teks, bukan dihitung.
- Waktu tempuh cahaya ke tiap citra planet diabaikan (posisi planet satu per frame untuk semua citra).
- Lembar debu adalah pendekatan visual (bidang tipis bertumpuk), bukan volume fisika. Biaya FPS belum diukur; target dinilai Bhakti di GTX 1060 dan M1 sebelum MK6 menjadikannya bawaan.

## Status

| Tahap | Status |
| --- | --- |
| MK1 | Selesai 17 Oktober 2026 (belum diuji): `shadePlanet()` dan uji potong tali busur di loop `SCENE_FS` (`uPlOn`, `uPl`, `uPlR`, `uPlN`; piringan di belakang planet dilewati) |
| MK2 | Selesai 17 Oktober 2026 (belum diuji): `MILLAR` / `millarState()` / `millarSave()`, uniform di `drawScene()`, baris HUD (r, periode, jam Millar, catatan Kerr), panel tab Piringan bagian Planet Millar, kamus `ID`, `?millar=0`, localStorage `gargantua.millar`; fase awal 2,25 rad = kiri depan pada kamera Film |
| MK2 revisi | 17 Oktober 2026, dari tangkapan layar Bhakti (planet terlalu besar, Gargantua tampak kecil): radius tampil bawaan 0,2 -> 0,06 rs (sekitar 2.100x radius nyata), panel 0,02-0,3, disimpan sebagai `rad2` (nilai lama diabaikan) |
| Lain | 17 Oktober 2026: bantuan (?) bertab seperti Copper (Dasar, Misi, Grafik dan suara, Kamera dan foto, VR; `HELP`, `helpTab()`, localStorage `gargantua.helpTab`; baris misi yang panjang dipecah per tombol); klik kiri saat kursor terkunci di kokpit = lepas kursor seperti Copper (`freedAt`, klik lagi = kunci; klik layar MFD tetap ganti halaman) |
| MK3 | Selesai 17 Oktober 2026 (belum diuji): `moodRamp()` di mode film, kontras gumpalan `0,45 + 0,85 pat`, grade di `COMPOSITE_FS` (eksposur x0,85, kejenuhan 0,78, hitam -0,012, vinyet +0,15); uniform `uMood` |
| MK4 | Selesai 17 Oktober 2026 (belum diuji): lembar debu kerucut y = k abs(xz), k +-0,06 / +-0,14 (`dustK()`, `dustG()`, `dustPat()`, `shadeDust()`), jendela 4-6 sampai 17-25 rs, dua lintasan sebelum / sesudah piringan dalam satu langkah, jumlah lembar `CONFIG.presets` `dust` (Rendah 1, Sedang 2, Tinggi 3, Ultra 4) |
| MK4b | 17 Oktober 2026 (belum diuji), revisi tangkapan layar Bhakti (debu tampak melayang terpisah dari piringan, celah 0,6 rs di 10 rs): lembar dirapatkan k +-0,02 / +-0,05 / +-0,10 (celah 0,2 rs di 10 rs), tiga tingkat `lv` (dekat mulai dari rIn + 0,3, pendar piringan Tn x 0,42 / 0,16 / 0,04, kerapatan 0,55 / 0,70 / 0,60), jumlah lembar Rendah 2, Sedang 4, Tinggi 4, Ultra 6 |
| MK5 | Selesai 17 Oktober 2026 (belum diuji): `sky()` bintang 40% lebih jarang, awan molekul gelap menyerap 88%, tepi debu coklat samar |
| MK4c | 17 Oktober 2026, revisi tangkapan layar Bhakti (debu terlalu halus): `dustPat()` derau billow 5 oktaf + pembelokan domain, frekuensi 2,5x, ambang lebih tajam, bayangan sendiri (satu sampel 0,35 rs ke arah lubang hitam, `lit = exp(-3,2 x kerapatan)`) |
| MK4d | 17 Oktober 2026, revisi tangkapan layar Bhakti (pola blok bergaris menyebar seperti bendera Jepang, FPS sangat rendah): kerapatan debu dipanggang ke tekstur kutub `DMAP` 768 x 192 RGBA8 (phi berulang, r 3-26 rs, kanal r g b = tingkat dekat / tengah / jauh) oleh `DUSTMAP_FS` / `dustBake()` paling sering tiap 0,1 satuan waktu; `shadeDust()` kini 2 baca tekstur (`uDustTex` unit 7) ganti 3 x 6 derau per silang; lembar bawah membaca phi + 2,3 rad; tiap oktaf diputar matriks ortonormal `ROT` (kisi derau tidak lagi sejajar arah radial dan cincin = penyebab pola blok). Ukur SwiftShader kualitas Tinggi 320 x 200: Kelam / Klasik 2,1x -> 1,5x waktu frame (angka absolut sandbox tidak stabil; FPS GPU asli menunggu uji Bhakti) |
| MK4e | 17 Oktober 2026, revisi tangkapan layar Bhakti (pola baji / goresan masih ada): tiga sebab ditemukan dengan render debu saja: (1) lembar dalam satu langkah sinar digabung menurut nomor, bukan jarak (goresan lurus di batas langkah) -> kini diurutkan `ts[6]` bersama piringan; (2) oktaf derau 4-5 lebih halus dari texel (gerigi) -> panggang maks 3 oktaf, tekstur 1024 x 512 half float; (3) ambang tajam sebelum interpolasi bilinear -> tekstur menyimpan derau mentah, ambang di `dustTex()`; punggung billow dibulatkan `sqrt(x^2 + 0,05)` di 2 oktaf kasar. Klasik tetap sama (urutan baru = urutan lama bila tidak ada debu) |
| MK4f | 17 Oktober 2026, revisi uji Bhakti (FPS turun 60 -> 30 setelah MK4e): pengurutan MK4e (array 6, pemilihan 7 x 6) jalan di SETIAP langkah sinar; kini uji silang 6 lembar dengan vec3 (`tu` / `tl`, 2 length per langkah), pengurutan hanya bila langkah menembus lembar, langkah tanpa debu = jalur lama, tanpa array berindeks dinamis; pembelokan domain panggang 1 derau (bukan 3). Ukur SwiftShader Tinggi 320 x 200: Kelam / Klasik 1,65x (MK4e) -> 1,15x; FPS GPU asli menunggu uji Bhakti |
| MK6 | 17 Oktober 2026: `MOOD`, tombol N `cycleMood()`, Kelam bawaan dan juga saat misi (debu memudar 0,5-2 rs dari kamera saat `uFall`), jumlah lembar per kualitas, baris N di bantuan, `docs/app/tombol.md` |
| MK7 | 17 Oktober 2026: kelompok MK di `tools/uji_misi_gargantua.py`; uji lama memakai `?mood=klasik&millar=0`, panel 46 kontrol |
| MK8 | 17 Oktober 2026: CLAUDE.md, `docs/app/tombol.md` |
