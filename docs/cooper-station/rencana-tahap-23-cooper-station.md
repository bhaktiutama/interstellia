# Rencana Tahap 23 Copper Corn Station: pantulan air, air sungai, air mancur, jembatan, berenang, payung, merpati

Per 7 Oktober 2026 · Bhakti

## Ringkasan

- Genangan, sungai, danau, dan kolam air mancur kini memantulkan gedung dan pohon di sekitar (pantulan ruang layar), bukan seluruh silinder.
- Permukaan air sungai tidak lagi berulang: dua skala riak, variasi makro, arus searah sungai, kekasaran ikut angin.
- Air mancur: percik di bibir kolam dan kaki pancuran, cincin riak, kabut tipis. Jembatan 3D di tiap persilangan jalan dan sungai. Pemain bisa masuk air (mengarung dan berenang). Pejalan kaki berpayung atau berteduh saat hujan. Merpati melipat sayap saat mendarat dan bergerombol.

Catatan: nomor 22 sudah dipakai keragaman kota (rencana-tahap-22), jadi tahap ini menjadi 23. Dibangun di atas V0-V5 (TAA, GTAO, kabut V4).

Status: 23a sampai 23g selesai, menunggu uji visual dan FPS Bhakti (GTX 1060, M1).

## Keluhan dan penyebab

| No | Keluhan (foto) | Penyebab di kode |
| --- | --- | --- |
| 1 | Genangan hanya memantulkan silinder (foto 1, 2) | Pantulan tanah basah memakai `farEnv()`: hanya daratan seberang, end cap, sunline. Gedung dekat tidak ada di sumber pantulan |
| 2 | Orang tidak bereaksi pada hujan | `stepPeds()` tidak membaca `RAIN.k` |
| 3 | Sungai menabrak jalan, tanpa jembatan | `onBridge()` hanya mengecat jalan di atas air pada kanvas lahan; tidak ada dek, pagar, atau pilar 3D |
| 4 | Pemain tidak bisa masuk air | `inWater()` dipakai sebagai penghalang di `stepGround()` |
| 5 | Air terlalu seragam (foto 3) | Normal riak satu skala, arah tetap, tanpa variasi makro |
| 6 | Merpati sayap terkembang, sendiri-sendiri | Pose burung sama saat terbang dan diam; titik kawanan tersebar |
| 7 | Air mancur tidak realistis (foto 5) | Tidak ada percik; kolam memantulkan `farEnv()` (silinder penuh) |

## Tahapan

| Tahap | Butir | Isi | Effort | Model | Thinking | Fungsi |
| --- | --- | --- | --- | --- | --- | --- |
| 23a | 1, 7 | Pantulan ruang layar (SSR) untuk air dan genangan, gagal = `farEnv()` lama; mati di Rendah dan Hemat | High | Opus 5.5 (orkestrator) | high | `POST`, `postEnd()`, shader tanah, air sungai, kolam |
| 23b | 5 | Air sungai dan danau tidak berulang | High | Opus 5.5 (orkestrator) | high | shader air, `RIVER` |
| 23c | 7 | Percik, cincin riak, kabut air mancur | Medium | Opus 5.5 subagent | medium | `FOUNT` |
| 23d | 3 | Jembatan 3D di tiap persilangan | Medium-High | Opus 5.5 subagent (geometri) + orkestrator (`groundH`) | medium / high | `onBridge()`, `RIVER`, `COL` |
| 23e | 4 | Mengarung dan berenang | High | Opus 5.5 (orkestrator) | high | `stepGround()`, `player.state` `swim` |
| 23f | 2 | Payung dan berteduh saat hujan | Medium | Opus 5.5 subagent | medium | `stepPeds()`, `updatePeds()`, `VIS` |
| 23g | 6 | Merpati melipat sayap, bergerombol | Medium | Opus 5.5 subagent | medium | `BIRDS` |
| 23h | revisi foto | Revisi air dari foto Bhakti: jagung di atas danau, bintang di bawah layar saat berenang, riak sungai tidak ikut alur, riak danau seperti arus | High | Opus 5.5 | high | tekstur ladang, `waterNear()`, `SWIM`, shader air |
| 23i | revisi Bhakti | Pipa pompa sungai ke gudang utilitas, traktor tidak masuk danau, pagar dek pandang kabel + condong di pagar | High | Opus 5.5 | high | `PIPE`, `inPipeRoute()`, `UTIL_PLAN.foot`, `f.lake`, `deckLean()` |
| - | - | Kamus English, label panel, CLAUDE.md | Low | Opus 5.5 subagent | low | `I18N.en` |

## Aturan

- Pertahankan yang ada: bila SSR tidak menemukan pantulan, hasil sama dengan sebelumnya.
- Tidak menambah suite uji di tahap ini; tiap commit cukup `tools/qc_load.py`.
- Visual dan FPS diuji Bhakti di GTX 1060 dan M1.

## Hasil dan penyederhanaan

| Tahap | Catatan |
| --- | --- |
| 23a | Sumber pantulan = frame sebelumnya (setengah resolusi). Objek di luar layar tidak terpantul (kembali ke farEnv) |
| 23d | Jalan lingkar za 2500 sejajar sungai di dua tempat: dek di sana sepanjang sekitar 650 m (jalan layang di atas sungai). Dekat akuaduk Skyway alur naik kembali ke tinggi 0. Lompat dari dek ke sungai: pendaratan langsung ke tinggi air (belum jatuh bertahap) |
| 23e | Air sungai diwakili permukaan mesh alur; dalam air dihitung dari jarak ke tepi (tanpa kamera bawah air) |
| 23f | Teduhan hanya kanopi kafe dan atap halte (pintu gedung belum); yang tidak mendapat teduhan membuka payung dan tetap duduk |
| 23g | Merpati tidak menghindari orang atau benda selain kolam; tanpa miring saat belok di udara |
| 23h | Lihat bagian Revisi 23h di bawah |

## Revisi 23h (dari foto Bhakti)

| Keluhan | Penyebab | Perbaikan |
| --- | --- | --- |
| Jagung tumbuh di atas danau | Tekstur petak ladang (`uFieldTex`) tidak dikosongkan di danau; danau za 4.300 dan 5.600 ada di zona ladang | Elips danau + 12 m dikosongkan di tekstur ladang (jagung, gandum, dan warna petak tidak lagi di air) |
| Saat berenang bagian bawah layar hitam berbintang | Mata perenang 0,25 m di atas air, ayunan kayuhan +-5 cm, bidang dekat kamera 0,25 m: permukaan air tepat di bawah kamera terpotong, tembus ke luar silinder | Mata 0,3 m di atas air, bidang dekat 0,1 m selama di air (`SWIM.eye`, `SWIM.near`, `waterNear()`), kembali 0,25 m saat keluar |
| Riak sungai jadi garis lurus panjang, tidak ikut alur | Pola digeser arus x waktu sampai 3.600 s; arus berbeda di tikungan dan tepi, jadi pola tertarik makin panjang | Peta aliran dua fase (geser maksimal 5 s, dua lapis berselang dicampur); arus 0,75 m/s di tengah, 0,15 m/s di tepi; arah gelombang diukur dari arah arus |
| Riak danau terlalu kasar, seperti arus | Gelombang danau sama dengan sungai: panjang 7 m, kemiringan sampai sekitar 0,3 | Danau: gelombang 1,8 m ke bawah, kemiringan sekitar 4x lebih kecil, petak licin seperti kaca diselingi tiupan angin |

Fisika sungai di silinder O'Neill: permukaan air diam = silinder sejari (potensial sentrifugal), jadi sungai yang mengelilingi keliling pada jari-jari tetap tidak punya turunan. Sungai melingkar penuh (panjang alur 6.662 m) hanya bisa mengalir dengan pompa: kemiringan Manning (n 0,03, penampang 82 m2, jari-jari hidrolik 2,0 m) untuk 0,5-0,6 m/s = 0,9-1,3 x 10^-4, beda tinggi 0,6-0,85 m per keliling, daya pompa sekitar 340-590 kW (efisiensi 70%). Coriolis untuk arus mendatar di lantai silinder selalu tegak (arus searah putaran 1,2% lebih berat pada 0,6 m/s), tidak mendorong ke tepi seperti di Bumi.

## Revisi 23i (pipa pompa, traktor, dek pandang)

| Butir | Perbaikan |
| --- | --- |
| Pipa pompa sungai | Pompa di gudang utilitas (za 6.488, sisi -s promenade Skyway). Pipa isap mengambil air 135 m di hulu akuaduk (muka -4 m) dan menyusuri tepi utara sungai; pipa dorong mengisi alur atas akuaduk (muka 0). Dua pipa baja diameter 3,6 m di atas pelana beton tiap 9 m, sepanjang promenade antara bangku dan barisan pohon (4,2 dan 4,3 km). Di bawah jalan pipa masuk tanah lewat dinding beton (11 persilangan per pipa). Kolider di sepanjang pipa, pohon tidak ditanam di jalurnya, tampil di peta |
| Traktor masuk danau | 17 petak ladang yang bersinggungan dengan danau (+15 m) tidak lagi dipakai mesin ladang |
| Dek pandang terhalang pagar | Pagar kabel: tiang 5 cm tiap 2 m, pegangan 1,1 m, 5 kabel baja 1,2 cm (dulu tiang 8 cm dan 3 palang setinggi 1,2 m). Condong di pagar: dekat pagar (< 1,3 m), menghadap keluar, dan menunduk = mata bergeser 0,85 m ke luar dan turun 0,15 m |

Fisika pompa (pipa baja, kekasaran 0,045 mm, Darcy-Weisbach): debit sungai 45 m3/s, kecepatan di pipa 4,42 m/s, faktor gesek 0,009, rugi gesek kedua pipa 21,1 m, rugi lokal 3,3 m, angkat statis 4 m; tinggi total 28,4 m, daya sekitar 15,7 MW (efisiensi 80%). Pompa yang dipasang langsung di sungai cukup sekitar 3,0 MW, jadi 80% daya habis di pipa sepanjang 8,5 km.

Batasan: tanjakan alur di hulu dan hilir akuaduk tampak sebagai batu kering (belum ada air terjun di hilir); kemiringan alur 1 x 10^-4 di sepanjang keliling tidak terlihat.
