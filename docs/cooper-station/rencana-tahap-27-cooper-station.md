# Rencana Tahap 27 Copper Corn Station: pohon jarak dekat dengan warna daun natural

Per 15 Oktober 2026 · disusun atas permintaan Bhakti · status: rencana saja, belum ada kode game yang diubah

## Ringkasan

- Masalah utama warna: daun di game kira-kira 2x lebih jenuh daripada foto contoh (median saturasi 0,70 sampai 0,76 berbanding 0,33 sampai 0,36). Rona sudah cocok (median 90 sampai 95 derajat berbanding 85 sampai 96), jadi yang diperbaiki adalah kejenuhan dan keseimbangan kanal biru, bukan warna dasarnya.
- Pendekatan: satu tahap penyetelan warna di shader daun (uniform dan tabel per jenis, bisa diatur langsung saat berjalan), dipakai juga oleh impostor agar peralihan LOD tidak patah. Fokus kualitas hanya untuk pohon di dalam radius mesh dekat (`TREES.lodD`, 130 m di Ultra), terutama di bawah 60 m.
- Urutan: ukur dan beku baseline (27a), saklar dan uniform (27b), warna (27c), cahaya tajuk (27d), variasi (27e), tepi daun dan pangkal batang (27f dan 27g), uji (27h). Semua di belakang saklar `?daun=lama` yang membuat tampilan identik dengan sebelum tahap 27.

## Data ukur (dihitung dari dua gambar yang Anda kirim)

Metode: piksel hijau dipilih dengan rona 55 sampai 165 derajat, saturasi > 0,12, nilai > 0,08, lalu diambil persentil 10 / 50 / 90. Gambar acuan = lembar pohon yang Anda kirim (baris oak, elm, dan beech sampai hickory). Gambar game = tiga pohon besar di tangkapan layar gameplay.

| Besaran | Foto contoh | Game (3 pohon besar) | Selisih |
| --- | --- | --- | --- |
| Rona median (derajat) | 85 sampai 96 | 90 sampai 95 | Cocok |
| Saturasi median | 0,33 sampai 0,36 | 0,69 sampai 0,76 | Game sekitar 2x lebih jenuh |
| Saturasi p10 / p90 | 0,18 sampai 0,19 / 0,50 sampai 0,58 | 0,30 sampai 0,36 / 0,93 sampai 1,00 | Game punya piksel hampir jenuh penuh |
| Nilai (kecerahan) median | 0,33 | 0,40 sampai 0,44 | Game sedikit lebih terang |
| Nilai p90 | 0,58 sampai 0,59 | 0,75 sampai 0,78 | Sorotan game jauh lebih terang |
| Sisi gelap (25% terendah): saturasi | 0,39 sampai 0,41 | 0,78 sampai 0,92 | Bayangan game terlalu jenuh |
| Sisi terang (25% tertinggi): saturasi, nilai | 0,24 sampai 0,31, 0,56 sampai 0,57 | 0,37 sampai 0,41, 0,73 sampai 0,78 | Sorotan game terlalu terang |
| Rona p90 (derajat) | 136 sampai 144 (hijau kebiruan di bayangan) | 105 sampai 112 | Game tidak punya hijau kebiruan |
| RGB median | [67 83 56] dan [72 84 52] | [52 102 27], [61 110 22], [69 113 30] | Biru game 22 sampai 30, foto 52 sampai 56 |

Kesimpulan data: foto contoh adalah hijau zaitun kusam dengan kanal biru yang cukup (abu-abu kehijauan), sedangkan game hijau terang hampir tanpa biru. Itu yang membuat tampak "kartun". Warna sasaran akhir diambil dari kolom foto contoh.

Batasan: foto contoh adalah gambar ilustrasi, bukan foto lapangan, dan hanya satu gambar. Tangkapan game satu kali, di satu waktu dan cuaca yang tidak saya ketahui. Crop kasar bisa memuat sedikit piksel bukan daun (misalnya rumput). Angka dipakai sebagai arah dan tolok awal, kalibrasi akhir lewat uji visual Anda (27h).

## Diagnosis di kode (hubungan data dengan penyebab)

Yang pasti dari kode, yang lain adalah dugaan yang harus dibuktikan di 27a.

| Hal | Lokasi di `experiences/cooper-station/index.html` | Penilaian |
| --- | --- | --- |
| Warna dasar atlas daun `hsl(rona, 38-63%, 26-46%)` | `leafTex` baris sekitar 7885 sampai 7940, `leafTex2` baris 7942 | Pasti: saturasi dasar sudah 38 sampai 63%, lebih tinggi dari target (S 0,33). |
| Translusensi `lc *= 1 + vBack * lfK * 0.9 * lc / max(max(lc.r, lc.g), 1e-3)` | `LEAF_FS` baris sekitar 9035 | Dugaan kuat: pembagian oleh kanal terbesar mengarahkan warna ke jenuh. Kamera gameplay di bawah tajuk (seperti tangkapan layar), jadi `vBack` besar dan sorotan menjadi lime. |
| Cahaya `vLight` dari `vegLight()` | baris 8217 | Cahaya stasiun dan sunline berwarna. Bayangan tajuk datang dari `aAo` per titik dan peta bayangan, tanpa pendinginan warna di bagian gelap. |
| `vTint` per kartu `mix(vec3(0.9,1.0,0.85), vec3(1.1,1.05,0.8), hh)` | `LEAF_VS` | Variasi kecil dan condong kuning: menurunkan biru. |
| Impostor memakai `leafRecolor` + `vLight` lain | `IMP_FS` baris 9080, bake `BAKE` di `LEAF_VS` | Penyetelan warna harus ikut ke sini, kalau tidak pohon jauh dan dekat beda tone. |
| Tepi daun kasar | alpha test `tx.a < mix(0.5, 0.3, ...)` di `LEAF_FS` | Dugaan: tanpa TAA (hanya Ultra) tepi tampak bergerigi. Belum diperiksa preset yang dipakai. |
| Pangkal batang menempel ke rumput | `makeTree()` dan `T.bark` MeshBasicMaterial | Tidak ada bayangan kontak atau pelebaran akar: terlihat dari tangkapan layar, belum dilacak ke kode. |

## Prinsip

1. Tampilan lama tidak berubah tanpa diminta: semua perubahan di belakang saklar `?daun=lama` (pola sama dengan `?pohon=lama`, `?v4=0`). Dengan saklar, shader dan hasilnya identik.
2. Jangan menyentuh urutan RNG `trr` di pembuat atlas: tekstur kulit dan jagung ikut urutan itu. Penyetelan warna dilakukan di shader (uniform), bukan dengan mengubah isi atlas.
3. Aturan shader proyek: tanpa `normalize()` vektor yang bisa nol, tanpa `pow()` basis negatif, tanpa `sqrt()` dan `asin()` di luar rentang (NaN di Apple M1). Penyetelan warna hanya memakai `mix`, `dot`, `clamp`, `max`.
4. Lingkup dekat: hanya mesh dekat (`T.bark`, `T.leaf`) yang boleh mengubah geometri. Impostor hanya mendapat penyetelan warna yang sama.
5. Warna harus bertahan di beberapa kondisi (siang, mendung, malam, mode Hijau / Campur / Gugur), bukan hanya satu jam.

## Tahapan

| Tahap | Isi | File dan fungsi | Effort | Model | Thinking |
| --- | --- | --- | --- | --- | --- |
| 27a | Baseline dan alat ukur: `tools/ukur_warna_pohon.py` (Playwright, 6 titik kamera tetap dekat pohon, jam dan cuaca dibeku, preset Ultra). Hitung persentil H / S / V piksel daun, simpan ke `tools/uji_warna_pohon_lama.json`, simpan PNG sebelum. Tabel sasaran dari data ukur di atas. | skrip baru, `window.__station` (kamera, waktu, cuaca) | Medium | Sonnet 5.5 | medium |
| 27b | Saklar `?daun=lama` dan uniform `uLeafGrade` (vec4: pengali saturasi, pengali nilai, angkat netral, kekuatan pendinginan bayangan) dengan nilai awal yang membuat hasil identik. Nilai bisa diubah dari konsol (`__station.LEAFG`) agar penyetelan tidak perlu muat ulang. | `LEAF_FS`, `IMP_FS`, objek `VU` / uniform, `window.__station` | Medium | Sonnet 5.5 | medium |
| 27c | Penyetelan warna: kurangi saturasi sekitar setengahnya (`mix(luma, c, k)`), angkat kanal biru dan netral di bagian gelap (hijau zaitun, bayangan kebiruan), turunkan sorotan. Tabel `grade` per jenis di `TREE_SPECIES` (atribut `aGrade`, pola seperti `aFlex` 25g): misal oak dan konifer lebih gelap, honey locust dan walnut lebih kuning. Warna musim (`LEAF_PAL`) disetel terpisah agar maple dan birch tetap hidup tapi tidak neon. | `LEAF_FS`, `IMP_FS`, `TREE_SPECIES`, `LEAF_PAL`, bagian `makeTree()` (atribut) | High | Opus 5.5 | high (konsistensi LOD dan aturan NaN) |
| 27d | Cahaya tajuk: terjemahan translusensi diganti campuran ke kuning pucat tak jenuh (bukan `lc / max(...)`), bagian gelap didinginkan ke warna ambient, sorot tepi daun terang halus. Selaraskan `vLight` pada bake `BAKE` supaya impostor dan mesh dekat sama. | `LEAF_VS`, `LEAF_FS`, `vegLight()` (tanpa mengubah `LIGHT_GLSL`) | High | Opus 5.5 | high |
| 27e | Variasi alami jarak dekat: variasi kecerahan per kartu daun dilebarkan, rona per pohon digeser kecil, skala per pohon sekitar 8% dan rotasi, supaya tiga pohon sejenis tidak terlihat sama. | `LEAF_VS` (`vTint`), `updateTreeLOD()` (skala instance), `leafColorFor()` | Medium | Sonnet 5.5 | medium |
| 27f | Tepi daun: periksa dulu penyebab tepi bergerigi (preset, TAA mati, ambang alpha). Bila perlu ganti ke alpha-to-coverage atau lunakkan ambang alpha. Tidak mengubah biaya shader banyak. | `LEAF_FS`, jalur TAA (`taaBegin()`), pengaturan renderer | Medium | Sonnet 5.5 | high bila menyentuh TAA |
| 27g | Pangkal batang: gelap bergradasi dan sedikit pelebaran akar (vertex color di bawah sekitar 0,6 m), cakram bayangan kontak instance hanya untuk pohon dekat. Kulit sedikit lebih gelap dan kusam agar selaras dengan daun. | `makeTree()` (batang), `T.bark`, instance baru di `updateTreeLOD()` | Medium | Sonnet 5.5 | medium |
| 27h | Uji dan kalibrasi: `tools/uji_pohon_warna.py` (persentil dalam rentang sasaran, `?daun=lama` identik dengan baseline, tanpa NaN atau Infinity, jumlah draw call sama, preset Hemat sampai Ultra), foto sebelum dan sesudah di 6 titik dan 3 kondisi (siang, mendung, malam). Bhakti menguji visual dan FPS di GTX 1060 dan M1, nilai uniform disetel dari hasilnya. | skrip baru, `tools/uji_pohon.py` tetap lulus | Medium | Sonnet 5.5 | medium |

Urutan kerja: 27a, 27b, 27c, lalu uji visual Anda. Bila warna sudah terasa benar, lanjut 27d. 27e, 27f, 27g bisa berurutan atau dipisah sesuai prioritas. Tahap High dikerjakan model High, tahap mekanis (skrip uji, entri tabel) diserahkan ke model lebih ringan sesuai aturan pemakaian di `CLAUDE.md`.

## Target hasil (diukur di 27a dan 27h)

| Besaran | Sekarang (game) | Target (mendekati foto contoh) |
| --- | --- | --- |
| Saturasi median daun | 0,69 sampai 0,76 | sekitar 0,33 sampai 0,45 |
| Saturasi sisi gelap | 0,78 sampai 0,92 | sekitar 0,40 sampai 0,55 |
| Nilai p90 (sorotan) | 0,75 sampai 0,78 | sekitar 0,60 sampai 0,68 |
| Kanal biru median (0 sampai 255) | 22 sampai 30 | sekitar 45 sampai 55 |
| Rona median | 90 sampai 95 | tetap 85 sampai 96 |

Catatan: sasaran tengah sengaja sedikit di atas foto contoh karena game memakai cahaya stasiun, bloom, dan ACES, sehingga angka gambar jadi tidak sama dengan foto lapangan. Angka akhir ditetapkan setelah Anda menguji secara visual di 27c.

## Risiko dan hal yang perlu dijaga

| Risiko | Penjagaan |
| --- | --- |
| Pohon dekat dan impostor berbeda tone saat berpindah LOD | `uLeafGrade` dan `aGrade` dipakai di `LEAF_FS` dan `IMP_FS`, diuji di 27h dengan foto di batas radius LOD |
| Hasil bagus di siang tapi aneh di mendung, malam, atau saat adaptasi mata berubah | Uji tiga kondisi, penyetelan berupa pengali (bukan nilai absolut) agar ikut cahaya |
| Biaya shader di pohon rapat (hutan 14a) | Hanya operasi `mix` / `dot`, tanpa tekstur tambahan; ukur draw call dan waktu GPU (`GPUT`) di 27h |
| NaN di Apple M1 | Aturan prinsip 3, uji nilai tidak valid di 27h; SwiftShader sandbox tidak menampakkan NaN, jadi pemeriksaan kode wajib |
| Mengubah tampilan yang sudah disukai | Saklar `?daun=lama` dan nilai bisa disetel dari konsol |
| Ruang lingkup melebar ke kota jauh (LOD gedung abu-abu) | Di luar tahap ini; dicatat sebagai usulan terpisah |

## Pertanyaan yang menentukan arah (mohon dijawab sebelum 27c)

1. Apakah mode Campur dan Gugur (kuning, jingga, merah) ikut dibuat lebih kusam seperti foto contoh, atau tetap hidup seperti sekarang dan hanya hijau yang disetel?
2. Preset grafis apa yang dipakai pada tangkapan layar tadi dan target utamanya (Ultra di GTX 1060, atau Hemat di M1)? Ini menentukan apakah 27f (tepi daun) bergantung pada TAA yang hanya aktif di Ultra.
3. Apakah foto contoh sudah menjadi acuan satu-satunya untuk tone, atau ada foto lapangan lain yang lebih disukai?
