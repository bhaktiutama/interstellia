# Rencana Tahap 32 Copper Corn Station: tekstur jarak dekat (fasad, trotoar, aspal)

Per 26 Oktober 2026 · disusun atas permintaan Bhakti dari 3 foto (gedung dan trotoar, aspal, tembok bata) · status: rencana, belum dikerjakan

## Ringkasan

- Masalah utama bukan resolusi tekstur, tetapi semua permukaan terlihat **baru, rata, dan bersih**: tanpa pelapukan, tanpa kedalaman (nat, ambang, lis hanya warna), dan pertemuan bahan terputus tajam (dinding langsung ke rumput, aspal langsung ke trotoar).
- Dua cacat yang jelas dan murah diperbaiki dulu: papan nama toko berisi balok seperti barcode (32b) dan aspal kehijauan di tepi jalan (32c, penyebab sudah ditemukan di kode).
- Semua tetap prosedural di shader (tanpa tekstur foto, tanpa addon), di belakang saklar `?tekstur=lama` yang membuat tampilan identik dengan sebelum tahap 32.

## Temuan dari foto

| Foto | Temuan | Penyebab di kode (`experiences/cooper-station/index.html`) |
| --- | --- | --- |
| 3 Tembok bata | Papan nama toko berisi balok hitam / terang seperti barcode | Pasti: `glyph` di `BUILD_FS` gaya 12 (blok "22a: deret toko") = pita `fract(u / 0.3)` dinyalakan acak per 0,3 m, bukan huruf |
| 2 Aspal | Aspal di dekat tepi rumput berubah kehijauan | Pasti: klasifikasi tanah memakai warna `uLand` (`landCanvas` 2.048 x 2.608, sekitar 3,07 m per piksel) yang disaring bilinear; piksel tepi jalan bercampur rumput, jadi `base` kehijauan dan `asphM` / `vegM` bercampur sepanjang sekitar 3 m |
| 2 Aspal | Tidak ada jejak ban, aus marka, tambalan, retak; butir agregat lemah | Shader tanah blok "jalan dan ladang dari dekat": hanya `grainN(P * 18)`, `vnoise(P / 2.5)`, noda `mdNoiseD`; marka `roadMarks()` sempurna |
| 1 Trotoar | Petak 3 m seragam, sambungan rata, tanpa retak / noda, tanpa gelap di dekat dinding | Blok "15c: trotoar kota" + petak `tid = floor(P / 3.0)` dengan `tv` 0,94-1,06 saja |
| 1 Rumah | Papan dinding tanpa bayangan bawah papan, dinding langsung masuk rumput, jendela tanpa ambang menonjol, pintu persegi gelap | `BUILD_FS` `mat == 1.0` hanya `lines(y, 0.2, 0.012)` gelap 22%; tidak ada plint |
| 3 Bata | Bata dan nat rata, warna per bata sedikit, tanpa noda turun di bawah ambang; kaca etalase hampir hitam; lis datar | `mat == 4.0` (gaya 12 sudah punya warna acak per bata dan noda kecil); `shopM` etalase gelap |
| 1 Tiang | Abu-abu polos tanpa alas | Geometri tiang lampu `LAMP` |

## Prinsip

- Pertahankan yang ada: tampilan jauh (> 60 m) dan semua preset tidak berubah kecuali yang disebut. Detail baru memudar dengan jejak piksel `fp` / `fwU` / `fwY` seperti pola yang sudah ada.
- Detail mahal hanya Ultra dan Tinggi lewat `uL_Detail` (pola V1); perbaikan cacat (32b, 32c) berlaku di semua preset.
- Shader aman untuk M1: tanpa `normalize()` vektor nol, tanpa `pow()` negatif, tanpa `sqrt()` / `asin()` di luar rentang.
- Saklar `?tekstur=lama` (`TEKS.lama`) = define yang mematikan semua cabang baru; uji membandingkan piksel dengan dan tanpa saklar terhadap commit induk.

## Langkah

| Langkah | Isi | File / fungsi | Effort | Model | Thinking |
| --- | --- | --- | --- | --- | --- |
| 32a | Saklar `?tekstur=lama` (define `TEKS_LAMA` di shader tanah dan `BUILD_FS`), titik foto acuan tetap (6 lokasi: rumah foto 1, arteri foto 2, deret bata foto 3, pusat NY, permukiman, boulevard), uji identik dengan induk | `TEKS`, `groundMat`, material gedung, `tools/uji_tekstur.py` baru | Medium | Sonnet 5.5 | medium |
| 32b | Papan nama berhuruf asli: atlas kanvas 1.024 x 256 berisi 32 kata pendek ID + EN (TOKO, ROTI, KOPI, DELI, BAKERY, APOTEK, BOOKS, 24H, nomor gedung), dipilih per toko dari `hb2`; huruf disampel dengan `textureGrad` dan memudar ke rata-rata saat `fwU` besar; neon malam memakai alfa huruf yang sama | `BUILD_FS` blok 22a (`glyph`, `neon`), uniform sampler baru di material gedung, `warmShaders()` | Medium | Sonnet 5.5 | medium |
| 32c | Aspal tanpa rona hijau: tepi jalan dari geometri analitik (lebar arteri `dS` / `dZ`, boulevard, `sidewalkD()` yang sudah ada), bukan dari warna peta; `base` aspal diganti warna aspal tetap di dalam jalan; tepi aspal ke rumput / trotoar tajam satu piksel (`lineAA`), bukan campuran 3 m | Shader tanah: klasifikasi `asphM` / `vegM` / `grayM`, juga jalan `roadZ()` dan `ROAD_DETOURS` | High | Opus 5.5 | high |
| 32d | Aspal hidup: 2 jalur ban gelap per lajur (lebih licin di `mdRough`), marka aus dan berbintik (lebih aus di jalur ban), tambalan persegi gelap, retak halus jarang, tutup saluran bulat di dekat simpang, talang gelap 0,4 m di tepi kerb | Shader tanah blok aspal, `roadMarks()` | Medium | Sonnet 5.5 | medium |
| 32e | Trotoar: lebar petak 1,5-3 m per ruas (hash per blok), sambungan potong yang lebih dalam (gelap + tonjolan `mdG`), retak jarang, noda bundar (permen karet, tetes air), gelap kotor 0,3-0,8 m di sisi dinding dan rumput, kerb dengan sisi tegak palsu (garis terang + bayangan di sisi jalan) | Shader tanah blok 15c, `SIDEWALK_GLSL` (jangan ubah `sidewalkD()` agar JS `SIDEWALK.d` tetap sama) | Medium | Sonnet 5.5 | medium |
| 32f | Pelapukan fasad (semua gaya): kaki dinding gelap dan kotor 0-1,2 m, noda turun di bawah tiap ambang jendela (mengikuti kolom jendela yang sudah dihitung), variasi warna per bata / per papan, nat bata tenggelam dan papan dinding dengan bayangan bawah papan lewat normal palsu dari turunan layar, lumut tipis di sisi teduh dekat tanah, debu di atas lis | `BUILD_FS` setelah warna dinding dasar (`mat` 1 / 3 / 4, gaya 12 dan 13), uniform `uWeather` dari `CONFIG` | High | Opus 5.5 | high (BUILD_FS besar, rawan NaN di M1) |
| 32g | Jendela dan pintu: ambang dan bingkai menonjol (bayangan palsu di bawah ambang dan sisi bingkai menurut arah cahaya `uL_SunDir`), pintu berpanel dengan pegangan, kaca etalase gaya 12 tidak hitam pekat (ruang toko sederhana memakai cara `kI` 14c atau pantulan ngarai 21e), lis dan pita batu dengan bayangan bawah | `BUILD_FS` blok jendela, 14c, 22a | Medium | Sonnet 5.5 | medium |
| 32h | Pertemuan bahan: plint beton 0,4 m di kaki rumah dan gedung (di shader, tanpa geometri), garis rumput ke trotoar dibuat tidak rata (tanah terbuka 0,1-0,3 m), alas tiang lampu (kerucut kecil di geometri `LAMP`) | `BUILD_FS`, shader tanah, rumput `CLIP_AWAY`, geometri tiang | Medium | Sonnet 5.5 | medium |
| 32i | Uji dan ukur: tanpa nilai tidak valid di 5 preset siang / malam / hujan, `?tekstur=lama` identik, papan nama berhuruf (sampel piksel), tidak ada piksel kehijauan di dalam jalan (sampel rona di 6 lokasi), waktu GPU `GPUT` sc sebelum / sesudah, `tools/ukur_muat.py cooper-station --cek` (atlas huruf tanpa program baru di frame pertama) | `tools/uji_tekstur.py`, CLAUDE.md (peta kode, riwayat) | Medium | Sonnet 5.5 | medium |

Urutan kerja: 32a, 32b, 32c (cacat, langsung terlihat), lalu 32d, 32e, 32f, 32g, 32h, lalu 32i. 32f boleh dipecah: 32f-1 kaki dinding dan noda turun (Medium), 32f-2 normal palsu nat dan papan (High).

## Perkiraan biaya

| Item | Perkiraan | Dasar |
| --- | --- | --- |
| Memori | Atlas huruf 1.024 x 256 RGBA dengan mipmap sekitar 1,4 MB | Ukuran tekstur |
| Muat | Tanpa program shader baru (hanya cabang di program yang sudah ada); atlas kanvas di bawah 20 ms | Perkiraan, diukur di 32i |
| Waktu GPU | Belum diketahui. Shader tanah dan `BUILD_FS` mendapat beberapa noise per piksel di bawah 60 m; diukur dengan `GPUT` di 32i dan di GTX 1060 / M1 oleh Bhakti | Tidak bisa diukur bermakna di SwiftShader |

## Keputusan untuk Bhakti

| Pertanyaan | Usulan bawaan |
| --- | --- |
| Seberapa kotor kota? Copper stasiun yang dirawat, jadi pelapukan ringan sampai sedang | Ringan di pusat (mega), sedang di permukiman dan kawasan tani; satu pengali `CONFIG.weather` untuk disetel saat uji |
| Bahasa papan nama | Campur ID dan EN (kota antarbangsa), tanpa merek nyata |
| Pelapukan di Hemat / Rendah | Mati (hanya 32b dan 32c yang berlaku di semua preset) |

## Batasan

- Diagnosis berasal dari 3 foto, satu waktu, satu cuaca. Distrik lain (menara kaca, pasar, tani) belum dilihat dan mungkin punya masalah lain.
- Penyebab 32b dan 32c pasti dari kode; penilaian "rata" dan "bersih" adalah penilaian visual dari foto.
- Hasil akhir dinilai Bhakti di GPU asli; sandbox hanya memeriksa error, nilai tidak valid, dan keidentikan saklar.
