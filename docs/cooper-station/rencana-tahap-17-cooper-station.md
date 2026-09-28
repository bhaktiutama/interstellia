# Rencana Tahap 17 Copper Corn Station: orbit, gerhana, dan pencahayaan

Per 28 September 2026 · Bhakti · gambar penjelasan: artifact "Gerhana Saturnus dan Sinar End Cap"

## Ringkasan

- **17a (selesai):** sumbu stasiun dimiringkan ulang agar sinar Matahari masuk lewat end cap B dengan sudut landai 25 derajat, dan stasiun lewat bayangan Saturnus sekali tiap orbit (gerhana sekitar 2,8 jam).
- **17b-17f (rencana):** peningkatan realisme pencahayaan dari usulan sebelumnya.
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

## 17b-17f: pencahayaan (rencana, belum dikerjakan)

| Tahap | Isi | Biaya GPU (perkiraan) |
| --- | --- | --- |
| 17b | Specular dan Fresnel di `stationLight()`, kekasaran per material lewat `userData` | Rendah |
| 17c | Adaptasi mata (eksposur otomatis dari mip bloom terkecil) | Sangat rendah |
| 17d | Ambient dua arah khas silinder: pantulan dari daratan seberang di atas kepala | Hampir nol |
| 17e | Lampu jalan, mobil, trem menerangi objek saat malam (bukan hanya tanah) | Rendah sampai sedang |
| 17f | Bayangan sunline di dekat pemain: tajam ke arah keliling, kabur ke arah sumbu | Sedang (mati di Hemat) |

## Catatan

- Siang dan malam di dalam stasiun tetap dari sunline. Matahari di Saturnus hanya sekitar 1% terang di Bumi, jadi gerhana paling terasa saat melihat keluar.
- Petak sinar Matahari kini lebih luas dan berputar tiap 63,4 detik seperti mercusuar lambat. Bila mengganggu, kaca end cap bisa dibuat agak buram.
- Belum dicek di layar asli (GTX 1060 dan M1). Uji otomatis di SwiftShader tidak memperlihatkan NaN khas M1.
