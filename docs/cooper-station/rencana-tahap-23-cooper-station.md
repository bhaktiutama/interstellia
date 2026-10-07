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
