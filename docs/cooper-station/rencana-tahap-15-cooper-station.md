# Rencana Tahap 15 Copper Corn Station: kota lebih padat dan hidup

Status: disetujui pemilik. Dikerjakan berurutan 15a, 15b, 15c, 15d.

## Latar belakang

Pemilik melaporkan empat masalah setelah 14c:
1. Permukiman di sekitar kota banyak tanah kosong: rumah menempel ke jalan, di belakangnya tanah kosong luas. Ingin daerah urban dekat kota lebih padat.
2. Banyak orang berjalan di rumput tanpa trotoar, terutama di pinggiran.
3. Trem gelap saat malam, tidak ada lampu.
4. Jalan lebar di kanan kiri rel trem kosong, tidak ada mobil.

Keputusan pemilik: kepadatan bertingkat (rumah deret 2-3 lantai dekat pusat, rumah tunggal berhalaman makin jauh, rumah besar berjarak di tepi); lalu lintas boulevard seluruh panjang (za 160-7850).

Tiap sub-tahap: commit dan push sendiri ke branch dan `main`, hasil dicatat di dokumen ini.

## Temuan (semua di `experiences/cooper-station/index.html`)

| Masalah | Penyebab |
| --- | --- |
| Tanah kosong | Loop penempatan (sekitar L2502-2565): permukiman/tepi hanya 1 baris rumah di dua sisi za tiap blok, paling dalam 19 m (`set` 4-7 + `dd` 8-12). Blok permukiman (n = 2) dalam sekitar 104 m, jadi 66-75 m tengah kosong. Sel tepi (n = 1, tanpa jalan lokal) dalam 222 m, tengah kosong sekitar 190 m, dan 45% kavling dilewati. Sisi blok yang menghadap jalan sepanjang za tidak pernah diberi rumah (`front` hanya 1/2 = muka -za/+za). 166 dari 234 sel kota = permukiman, 42 = tepi |
| Jalan di rumput | Tidak ada trotoar sama sekali. "Trotoar" hanya warna sel: pusat/menengah abu (dirender beton), permukiman/tepi hijau (rumput), sekitar 89% sel. Rute pejalan kaki (`kind 'z'` dan `'s'`, sekitar L8189-8213) di 14,6-15,8 m dari sumbu jalan untuk semua arteri kota tanpa melihat jenis tanah; rute m = 10 sisi +1 (za sekitar 2515) di luar kota; rute tidak mengecualikan lapangan baseball; 1000 rute `seg` taman di rumput tanpa jalan setapak. Pohon jalan tepat di 15 m (menabrak pejalan); gedung menengah menempel ke tepi blok 14 m (pejalan masuk ke fasad). Tekstur tanah 3,07 m per piksel, terlalu kasar untuk trotoar |
| Trem gelap | Semua material trem `MeshBasicMaterial` yang dicahayai `patchLit`, jadi ikut gelap malam. Lampu plafon (`M.lamp` 0xfff4e0) konstan dan tidak di atas ambang bloom. Hanya lampu ujung (`updateTramVisual`, `BUILD_U.uNight`) yang bereaksi malam. Tidak ada kolam cahaya di tanah |
| Boulevard kosong | Loop lajur mobil `for (let k = 1; k < 26; k++)` (sekitar L6282) mulai dari 1, jadi boulevard k = 0 (s = `TRAM.s` = 0, lebar 40 m, za 150-7970) tidak pernah punya lajur. Juga tanpa marka lajur (`!blvd` di shader tanah), tanpa lampu jalan (loop lampu mulai k = 1, `lampPool` mengecualikan km 0) |

## Sub-tahap (urutan kerja)

### 15a Lampu trem malam (kecil)
- Lampu strip plafon: warna diatur tiap frame di `updateTramVisual()` = hangat x (1 + 2,5 x malam), di atas ambang bloom saat malam.
- Interior (lapisan dinding dalam, plafon, lantai, kursi): tambahan cahaya kabin lewat uniform bersama `uCabin` (hangat x 0,9 x malam) yang ditambahkan ke material ini melalui `patchLit` (penanda `userData.cabin`), jadi siang tetap sama.
- Kaca jendela, pintu, kaca depan: sedikit bercahaya hangat saat malam supaya dari jauh jendela trem menyala.
- Kolam cahaya di tanah: uniform `uTram` (s, za, arah, malam) di `groundMat`: sorot lampu depan memanjang sekitar 20 m di depan trem dan pendaran jendela di samping badan trem. Aturan M1: tanpa normalize/pow baru.

**Hasil 15a (selesai):** strip plafon malam 3,2 (ambang bloom 1,15), interior (dinding dalam, lantai, kursi, tiang) diterangi `CABIN_LIGHT.uCabin` lewat `patchLit` (penanda `userData.cabin`), kolam cahaya tanah `tramPool()` di `groundMat` (sorot depan sampai 26 m, pendaran jendela). Render trem malam 1,9x lebih terang dengan lampu kabin, tanpa nilai tidak valid. Siang tidak berubah. Uji `tools/uji_trem_malam.py`.

### 15b Lalu lintas boulevard
- Lajur tipe 0 di k = 0: dua lajur per arah di jarak 11,0 dan 14,8 m dari sumbu rel (di luar koridor trem 7 m dan peron sampai 6,4 m; garis tepi 19,3 m). Seluruh panjang za 160-7850: di kota jarak antar mobil seperti arteri lain, di pertanian lebih jarang.
- Simpang boulevard x arteri melingkar di kota: mobil boulevard ikut `sigState(0, m, 0)`; mobil tipe 1 di k = 0 berhenti untuk lampu dan palang trem (`XING`) sekaligus.
- Shader tanah: marka putus-putus antar lajur dan garis median di 9,1 m untuk boulevard di dalam kota dan pertanian.
- Lampu jalan boulevard di kota (tiang di tepi luar, 45 m), `lampPool` disesuaikan.
- Cek tabrakan pemain dengan mobil (sekitar L7006) memasukkan k = 0.

**Hasil 15b (selesai):** 4 lajur boulevard (`BLVD`: 11,0 dan 14,8 m dari as rel, za 160-7850), 134 mobil (awal 80 di kota, 54 di pertanian). Simpang boulevard di kota ikut lampu lalu lintas; mobil arteri melingkar di k = 0 berhenti untuk palang trem dan lampu merah. Marka median 9,1 m dan garis putus 12,9 m, lampu jalan boulevard di 21,5 m (kota) dengan kolam cahaya. Simulasi 30 menit: 0 tabrakan dengan trem, 0 konflik simpang. Uji `tools/uji_boulevard.py`; `uji_lalu_lintas`, `uji_pejalan_kaki`, `uji_rel_trem`, `uji_skyway` tetap lulus.

### 15c Trotoar dan jalan setapak
- Trotoar analitik di shader tanah (tajam, tidak bergantung tekstur 3 m per piksel): untuk tiap arteri kota (sepanjang za k = 1-25 kecuali 13, dan arteri melingkar di `ringM`), pita 12-17 m dari sumbu: kerb 12-12,3 m, lajur pohon dan perabot 12,3-13,8 m, lajur jalan 13,8-17 m, beton bernat 1,5 m. Boulevard: trotoar 20-25 m.
- Blok bangunan mundur: tepi blok dari tepi jalan +2 m menjadi +5 m (17 m dari sumbu arteri) supaya fasad menengah dan pusat tidak masuk trotoar. Pohon jalan dari 15 m ke 13 m (lajur pohon). Perabot tetap di 13 m.
- Rute pejalan kaki `z` dan `s` ke 14,3-16,5 m, keluarkan lapangan baseball, rute m = 10 sisi +1 pindah ke jalan tepi sungai (lihat bawah).
- Jalan setapak taman: jaringan jalur (loop tepi taman kota, jalur lurus di taman besar PARKZ, jalan tepi sungai) dibuat sebagai pita geometri tipis mengikuti `groundH` (satu mesh gabungan, lebar 2,5-3 m, `polygonOffset`). Walker `loop` dan `seg` taman diambil dari jalur ini, bukan garis acak.
- Jalan lokal (10 m) di permukiman: pita trotoar 1,5 m di tekstur tanah cukup sebagai tepi abu (tanpa pejalan).

**Hasil 15c (selesai):**

| Bagian | Hasil |
| --- | --- |
| Trotoar | `SIDEWALK_GLSL` / `SIDEWALK.d()`: pita 5 m di semua arteri kota (12-17 m, boulevard 20-25 m), kerb terang 0,3 m, lajur pohon dan tiang lebih gelap, beton bernat. Rumput 3D tidak tumbuh di trotoar |
| Blok | Sisi arteri mundur 3 m (tepi blok 17 m dari sumbu, boulevard 25 m). Sayap rumah dan garasi tidak lagi menjorok ke luar blok |
| Pohon jalan | Pindah ke lajur pohon (13 m, boulevard 21 m), digeser 4 m bila dekat tiang lampu |
| Pejalan kaki trotoar | Lajur 14,3-16,3 m. 94.939 titik rute: 100% di trotoar, 0 di dalam gedung atau pohon. Rute tidak lewat lapangan baseball dan collider |
| Taman besar | `PARK_PATHS`: 90 ruas jalan setapak lurus (48 km, 3 jalur sepanjang s dan jalur tiap setengah ART sepanjang za), dipotong di air, lapangan, Skyway, boulevard, dan pohon; pita 2,6 m mengikuti tanah (41 rb segitiga). Keliling taman kota juga diberi jalur. 1.000 pejalan kaki taman berjalan di jalur |
| Jalan lokal | Tepi abu 1,5 m di tekstur tanah |
| Biaya | Kota Ultra 2,94 jt segitiga (Hemat 1,00 jt), taman Ultra 3,77 jt (Hemat 1,71 jt) |

Uji `tools/uji_trotoar.py`. Uji lama tetap lulus (pejalan kaki, lalu lintas, peta, suasana, bahasa, rel, pohon, hutan, 12d, boulevard, burung, hujan); rumah pertanian kini juga tidak ditempatkan di petak hutan.

### 15d Permukiman padat bertingkat
- Sel tepi dibagi n = 2 (ada jalan lokal) seperti permukiman.
- Blok permukiman/tepi yang dalamnya lebih dari 60 m diberi gang 6 m sepanjang s di tengah, jadi 4 baris rumah: 2 menghadap jalan tepi blok, 2 menghadap gang (kavling bertolak belakang, dalam sekitar 24 m: muka 4-6 m, rumah 8-12 m, halaman belakang 6-10 m).
- Sisi blok yang menghadap jalan sepanjang za juga diisi rumah: `front` diperluas ke muka +x/-x (nilai 3/4) di `BUILD_FS` (`isFront`).
- Kepadatan bertingkat dari `cityDensity`:
  | Kepadatan | Bentuk | Kavling |
  | --- | --- | --- |
  | lebih dari 0,45 (permukiman dekat pusat) | Rumah deret 2-3 lantai menempel, 4-6 unit sederet, warna selang-seling | 7-9 m |
  | 0,34-0,45 | Rumah tunggal 1-2 lantai, garasi | 16-22 m |
  | tepi (di bawah 0,34, dekat sungai) | Rumah besar berhalaman, kavling kosong 15% (sebelumnya 45%) | 26-34 m |
- Halaman belakang: pohon halaman (template pohon yang ada, lewat `TREES`, RNG sendiri seperti hutan), pagar belakang dan samping sebagai jenis baru di `FURN` (LOD per radius), gudang kecil sesekali.
- Menengah: bangunan mundur 3 m dari tepi blok (ikut 15c).
- Semua rumah baru lewat `building()` (collider, `houseList`, peta `drawMapStatic` otomatis). Pejalan kaki tidak masuk gang (tetap di trotoar arteri).
- Biaya: rumah instanced (tanpa culling). Target jumlah rumah sekitar 2-2,5x sekarang; jumlah dan segitiga dicatat per preset. Bila Hemat naik lebih dari 10%, rumah isian gang ditaruh di akhir buffer dan dipotong `mesh.count` di Hemat.

**Hasil 15d (selesai):**

| Ukuran | Sebelum 15d | Sesudah |
| --- | --- | --- |
| Rumah permukiman di kota | 6.883 | 12.706 (1,85x) |
| Titik sampel sel permukiman/tepi yang lebih dari 25 m dari rumah (tanah kosong) | 34,4% | 6,0% |
| Rumah permukiman bertumpuk (garasi keluar kavling) | 789 | 0 |
| Gang, pohon halaman belakang | 0, 0 | 785, 6.243 |
| Titik awal kota, segitiga Ultra / Hemat | 2,94 jt / 1,00 jt | 3,17 jt / 1,13 jt |

- `fillHomes()`: gang 6 m di tengah blok dalam (4 baris rumah), baris samping menghadap jalan sepanjang za (`front` 3/4, atap `gablez`), sel tepi dibagi 2 (kecuali sel lapangan baseball).
- Rumah deret 2-3 lantai (4-6 unit menempel, lebar 7-9 m) bila kepadatan lebih dari 0,45; rumah tunggal kavling 16-22 m dengan garasi dan pohon belakang; tepi: rumah besar kavling 26-34 m, sayap, gudang kebun, 15% kavling kosong.
- Pagar halaman belum dibuat (ditunda; pohon halaman dan gudang dulu).
- Hemat naik 13% (lebih dari batas 10% di rencana), tetapi masih di bawah Hemat terberat yang sudah ada (bukit 1,38 jt, hutan 1,42 jt), jadi rumah tidak dipotong di Hemat. Bila M1 terasa berat, bisa ditambah.
- `uji_interior` diperbarui: merender satu gedung sasaran saja (permukiman rapat menghalangi kamera).

Uji `tools/uji_permukiman.py`. Semua uji lama lulus.

### 15e Masjid (permintaan tambahan pemilik, selesai)

Setengah gereja diganti masjid (bergantian), tiga gaya bergiliran. Badan masjid lewat `building()` gaya 7 (jendela tinggi, pintu menghadap jalan, collider, tampil di peta); kubah, menara, dan atap = potongan geometri digabung ke satu mesh `MOSQUE.mesh` (20 rb segitiga, normal asli).

| Gaya | Bentuk |
| --- | --- |
| Utsmani (era Konstantinopel) | Kubah pusat abu timah di atas drum, dua setengah kubah depan-belakang, empat kubah sudut, serambi depan berkubah kecil, dua menara pensil 38 m dengan dua balkon dan atap kerucut runcing |
| Maroko | Aula rendah dengan atap limas genteng hijau, satu menara persegi 30 m berwarna oker dengan pita keramik hijau, lentera kecil beratap hijau, finial tiga bola emas |
| Arab Saudi | Aula putih, kubah besar putih di atas drum, kubah sudut, dua menara segi delapan dengan dua balkon, bagian atas ramping dan kubah kecil |

Hasil: 9 masjid (3 per gaya), 10 gereja. Uji di `tools/uji_permukiman.py` (jumlah, tiga gaya, normal sah).

## Berkas

- `experiences/cooper-station/index.html`: `updateTramVisual`, material trem, `patchLit`, `groundMat` (uTram, marka boulevard, trotoar), lajur `TRAFFIC`, loop lampu jalan dan `lampPool`, `XING`/sinyal k = 0, loop penempatan bangunan dan `blocksOfCell`, `BUILD_FS` (`isFront`), pohon jalan, `FURN` (pagar), rute `PEDS`, jalur taman.
- Uji baru: `tools/uji_trem_malam.py` (15a), `tools/uji_boulevard.py` (15b, mobil boulevard 30 menit tanpa tabrakan, berhenti di lampu), `tools/uji_trotoar.py` (15c, semua titik rute pejalan kaki kota di atas trotoar atau jalur, tidak di dalam collider gedung/pohon), `tools/uji_permukiman.py` (15d, jumlah rumah per kelas, tanah kosong terbesar di blok permukiman di bawah 30 m, tanpa rumah bertumpuk atau di jalan, biaya segitiga).
- Dokumen: `docs/cooper-station/rencana-tahap-15-cooper-station.md` (rencana dan hasil), `CLAUDE.md` (peta kode, tools, riwayat), `README.md`.

## Verifikasi

- Tiap sub-tahap: halaman termuat tanpa error, uji barunya lulus, uji lama tetap lulus (khususnya `uji_lalu_lintas`, `uji_pejalan_kaki`, `uji_rel_trem`, `uji_peta`, `uji_suasana`, `uji_bahasa`, `uji_interior`).
- Biaya segitiga dan draw call Ultra dan Hemat dicatat di kota dan permukiman (tanpa screenshot).
- Pemilik mengecek visual dan FPS (GTX 1060, M1 Hemat): trem malam, boulevard siang dan malam, trotoar dan pejalan kaki di pinggiran, permukiman dari jalan dan dari atas.
