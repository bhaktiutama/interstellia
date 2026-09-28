# Rencana Tahap 17 Copper Corn Station: orbit, gerhana, dan pencahayaan

Per 28 September 2026 · Bhakti · gambar penjelasan: artifact "Gerhana Saturnus dan Sinar End Cap"

## Ringkasan

- **17a (selesai):** sumbu stasiun dimiringkan ulang agar sinar Matahari masuk lewat end cap B dengan sudut landai 25 derajat, dan stasiun lewat bayangan Saturnus sekali tiap orbit (gerhana sekitar 2,8 jam).
- **17b dan 17d (selesai):** kaca, air, jalan basah, dan mobil memantulkan daratan seberang (bukan langit biru) dan awan yang sedang lewat; ambient siang ikut warna daratan; material cat, logam, dan kaca berkilap dengan Fresnel.
- **17c, 17e, 17f (selesai):** adaptasi mata, lampu jalan dan trem menerangi objek saat malam, bayangan sunline real-time di sekitar pemain (termasuk mobil dan pejalan kaki).
- Kota, ladang, dan fitur lain tidak berubah.

## 17a: orbit dan gerhana Saturnus (selesai)

| Item | Sebelum | Sesudah |
| --- | --- | --- |
| Kemiringan sumbu dari normal orbit (`ORBIT.axisTiltDeg`) | 40 derajat | 65 derajat (25 derajat dari bidang orbit) |
| Arah Matahari (`SUN_DIR`) | 68,19 derajat dari sumbu, 1,29 derajat dari bidang orbit | 25 derajat dari sumbu +z, tepat di bidang orbit |
| Jangkauan sinar dari end cap B | 800 m | 4.289 m |
| Bayangan pohon 20 m | 8 m | 43 m |
| Saturnus dari sumbu selama orbit | 50 sampai 130 derajat | 25 sampai 155 derajat |
| Gerhana | geometrinya terjadi, efek tidak ada | 2,78 jam per orbit 37,57 jam, dengan efek |
| Penumbra (masuk dan keluar) | - | sekitar 36 s (diameter sudut Matahari 0,0557 derajat + sekitar 240 km atmosfer) |

Yang dibuat:

| Bagian | Isi |
| --- | --- |
| `ECL` + `updateEclipse()` | Faktor `ECL.k` (1 terang, 0 gerhana total) dari posisi stasiun terhadap Saturnus pepat, dihitung tiap frame di `updateFar()` |
| Cahaya | `uL_SunI` = 0,12 x `ECL.k` (sinar lewat end cap dan sunrays ikut padam), silau Matahari (`uK`) padam |
| Saturnus | Cangkang cahaya tepi atmosfer (hamburan maju, jingga) saat Matahari di belakang Saturnus; cincin sudah bercahaya dari belakang lewat shader lama |
| Dermaga | Dermaga di end cap A kini secara fisika ada di bayangan stasiun, jadi cahaya dermaga dipertahankan dengan arah lama sebagai lampu sorot (tampilan spaceport tidak berubah), meredup ke 30% saat gerhana |
| Tombol I | `jumpToEclipse()`: lompat ke 2 menit (waktu orbit) sebelum gerhana berikutnya. Juga tombol di panel (`) |
| Notifikasi | 10 menit sebelum, saat mulai, saat selesai (hanya bila kecepatan orbit 1x atau 100x) |
| HUD | Baris fase orbit menampilkan "gerhana dalam X j Y mnt" atau "gerhana" |
| Uji | `tools/uji_gerhana.py` |

Lama gerhana per kecepatan orbit (tombol T):

| Kecepatan | Satu orbit | Gerhana |
| --- | --- | --- |
| 1x | 37,6 jam | 2,8 jam |
| 100x | 22,5 menit | 1,7 menit |
| 1.000x | 2,3 menit | 10 detik |
| 10.000x | 13,5 detik | 1 detik |

Cara melihat: tekan I, lalu 1 (rumah Cooper, dekat end cap B) dan lihat ke kaca end cap, atau V (kamera luar). Saturnus tampak berputar mengelilingi kaca end cap sekali tiap 63,4 detik karena stasiun berputar.

## 17b dan 17d: pantulan daratan seberang dan kilap material (selesai)

Masalah yang ditemukan Bhakti: kaca gedung tinggi memantulkan biru seperti langit Bumi. Di dalam silinder tidak ada langit; di atas kepala ada daratan seberang 2 km. Kode lama memakai warna kabut (biru muda) sebagai "langit".

| Warna (linear, jam 13.00) | R | G | B |
| --- | --- | --- | --- |
| Kabut (dulu dipakai sebagai pantulan) | 0,420 | 0,538 | 0,711 |
| Rata-rata peta daratan | 0,312 | 0,352 | 0,140 |
| Ambient siang lama | 0,17 | 0,20 | 0,25 |
| Ambient siang baru (kecerahan sama) | 0,178 | 0,208 | 0,139 |

Yang dibuat:

| Bagian | Isi |
| --- | --- |
| `farEnv(P, Rd, rough, lineK)` di `LIGHT_GLSL` | Sinar pantul dihitung sampai kena dinding silinder (ambil warna dari peta daratan x cahaya di sana) atau end cap (ruang gelap, cincin lampu keemasan, Matahari lewat kaca), lalu dikabutkan sesuai panjang sinar. Sunline = garis terang saat sinar lewat dekat sumbu. Kekasaran mengaburkan (mip peta, garis melebar) |
| Uniform baru | `uL_Land` (peta daratan), `uL_FarLight` (cahaya di daratan seberang), `uL_FarAvg`, `uL_FogCol`, `uL_FogD`, `uL_Night` (kota seberang menyala samar saat malam), diisi di `updateLighting()` |
| Kaca gedung | `sky = farEnv(...)` menggantikan warna kabut; tambahan biru ke arah atas dihapus |
| Jalan basah, air | Memantulkan daratan seberang; kilau sunline di air tetap memakai hitungan lama |
| Mobil | Cat (clearcoat tipis) dan kaca memantulkan daratan seberang, per verteks |
| Ambient siang | 70% warna daratan + 30% udara, luminans sama dengan nilai lama (0,197) |
| 17b: `specMat(m, kekasaran, F0, logam, kaca)` | Material dasar bertanda mendapat pantulan `farEnv` x Fresnel Schlick; logam mewarnai pantulan; kaca bening menaikkan alpha mengikuti Fresnel. Hemat energi: difus dikurangi sebesar bagian yang dipantulkan |
| Material bertanda | Trem (badan, strip, atap, rangka kursi, tiang kuning, baja, kaca), halte, lift, hub, rumah Cooper (atap seng, kaca, truk, krom), lapangan baseball (baja, aluminium), kaca terminal, tiang bendera, tiang lampu jalan, air mancur |
| Uji | `tools/uji_pantulan.py` |

Catatan: cat yang dilihat tegak lurus hanya memantul sekitar 4%, jadi kilap paling terlihat di sudut miring, pada logam, dan pada kaca. Pantulan tidak memperhitungkan objek dekat selain siluet gedung seberang yang sudah ada (14c).

### Revisi: awan ikut terpantul

| Bagian | Isi |
| --- | --- |
| Peta tutupan awan | Kanvas kedua 512 x 1024 digambar bersama bayangan awan (tiap 0,25 sampai 1,5 s), memakai jejak awan sebenarnya (tidak dipanjangkan seperti bayangan), `uL_Cloud` |
| `farEnv` | Sinar pantul memotong lapisan awan (jari-jari R - 340 m) dua kali: dekat daratan seberang dan di atas pemandang. Warna awan saat ini (`uL_CloudCol`, sama dengan awan yang terlihat) ditumpuk dengan kabut sesuai jarak |
| Hasil | Awan yang hanyut, terbentuk, dan menghilang ikut terlihat di kaca gedung, air, jalan basah, logam, dan mobil |

## 17c, 17e, 17f: pencahayaan lanjutan (selesai)

| Tahap | Isi | Biaya GPU (perkiraan) |
| --- | --- | --- |
| 17c | Adaptasi mata: rata-rata log luminans layar (192 titik, tengah lebih berbobot) di target 1x1, dihaluskan terhadap waktu di GPU (tanpa baca balik). Revisi setelah uji Bhakti (tidak terasa): eksposur x (0,16 / L)^0,6, dibatasi 0,45 sampai 2,2 (dulu ^0,45, 0,6-1,8). Ke terang sekitar 0,6 s, ke gelap sekitar 2,5 s. Revisi kedua (masih tidak terasa): interior dulu hanya 2x lebih gelap karena ambient dan cincin lampu tetap masuk; kini atap dekat di atas kepala (dari peta bayangan sunline, penghalang di bawah 12-40 m) juga menghalangi ambient 75%, cincin lampu 60%, sinar Matahari 80%. Terukur: siang di luar x1,10, dalam rumah Cooper x2,06 (2,8x lebih gelap), terminal x2,20 (5x lebih gelap), malam x2,2. Tombol "Adaptasi mata" di panel Grafik menampilkan pengali saat ini, atau "butuh efek layar" di preset Rendah dan Hemat (efek layar dan bayangan mati, jadi adaptasi tidak berjalan). `ADAPT`, `lumMat`, `POST_R.lum` | Sangat rendah |
| 17e | `nightLight(p, n)` di `LIGHT_GLSL`: kolam cahaya lampu jalan (`lampPoolL`, salinan `lampPool` tanah) dan trem (`tramPoolL`) menerangi gedung, perabot, pohon, rumput, mobil, pejalan kaki. Muka atas penuh, dinding setengah, hilang di atas 18 m | Rendah |
| 17f | Bayangan sunline: peta kedalaman ortografis 2048 piksel, 300 x 300 m di sekitar pemain, dilihat dari arah sumbu (`SUNSH`, `sunShadowPass()`). Tajam ke arah keliling, kabur searah sumbu sepanjang 0,75 x tinggi penghalang (cari penghalang 7 titik + PCF 8 titik; vegetasi 3 + 3). Bayangan tajuk panggang memudar di area ini agar tidak dobel. Mobil dan pejalan kaki kini ikut membuat bayangan. Mati di preset Rendah dan Hemat, saat malam, di lift/hub, dan di kamera luar | Sedang |

Catatan 17e: lampu tidak terhalang atap (tidak ada bayangan lampu), dan sorot lampu depan mobil belum menerangi objek (hanya aspal, seperti sebelumnya).

## Catatan

- Siang dan malam di dalam stasiun tetap dari sunline. Matahari di Saturnus hanya sekitar 1% terang di Bumi, jadi gerhana paling terasa saat melihat keluar.
- Petak sinar Matahari kini lebih luas dan berputar tiap 63,4 detik seperti mercusuar lambat. Bila mengganggu, kaca end cap bisa dibuat agak buram.
- Belum dicek di layar asli (GTX 1060 dan M1). Uji otomatis di SwiftShader tidak memperlihatkan NaN khas M1.
