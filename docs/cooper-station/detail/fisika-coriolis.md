# Fisika Copper Corn Station: ke mana benda melenceng?

Bahan halaman detail experience Copper Corn Station (dibuka dari menu utama). Satu file per topik di `docs/<id>/detail/`. Angka dihitung dari R 1.000 m, omega 0,09905 rad/s (periode 63,4 s, 1 g di lantai) dan uji fisika di kode (`TESTS`, `tools/uji_menara.py`).

## Ringkasan

- Begitu dilepas, benda bergerak lurus. Lantai di bawahnya terus berputar.
- Kalau kecepatan keliling benda lebih kecil daripada lantai di bawahnya, lantai menyalip, jadi benda mendarat melawan arah putaran. Ini yang terjadi pada bola yang dijatuhkan dari gedung.
- Kalau kecepatan keliling benda lebih besar, benda mendahului lantai dan mendarat searah putaran. Ini yang terjadi pada air mancur.
- Lemparan mendatar melawan putaran lebih jauh karena benda itu menjadi lebih ringan.

## 1. Bola dijatuhkan dari gedung: melawan putaran

| | Bola di dek 175 m | Lantai di bawahnya |
| --- | --- | --- |
| Jari-jari | 825 m | 1.000 m |
| Kecepatan keliling | 0,09905 x 825 = 81,7 m/s | 0,09905 x 1.000 = 99,05 m/s |

Bola hanya membawa 81,7 m/s, sedangkan lantai bergerak 99,05 m/s. Selama 6,92 s bola jatuh, lantai menyalip, jadi bola mendarat 85,7 m melawan putaran. Dari 100 m, bola melenceng 33,3 m.

Di dek pandang (tombol G), bola dilepas di luar podium menara. Dilepas ke arah melawan putaran, bola melenceng menjauhi menara dan sampai di tanah. Dilepas ke arah searah putaran, bola melenceng ke belakang dan menabrak menara.

## 2. Air mancur: searah putaran

Air keluar dari nosel di lantai dengan kecepatan keliling 99,05 m/s, sama dengan lantai. Saat naik, air masuk ke jari-jari yang lebih kecil. Di sana, untuk ikut berputar cukup kecepatan yang lebih kecil, padahal air masih membawa 99,05 m/s. Akibatnya air mendahului lantai dan mendarat searah putaran.

| Kasus | Waktu terbang | Melenceng |
| --- | --- | --- |
| Lempar tegak 20 m/s | 3,92 s | +10,46 m (searah putaran) |
| Lompat tegak 2 m/s | 0,41 s | +0,011 m (searah putaran) |

Jadi yang membedakan air mancur dan bola jatuh adalah titik awalnya. Air mancur mulai dari lantai dengan kecepatan penuh lalu naik. Bola jatuh mulai dari atas dengan kecepatan yang lebih kecil.

## 3. Lempar mendatar: melawan putaran lebih jauh

Berat yang terasa bergantung pada kecepatan keliling total: g' = (omega R + v)^2 / R. Lemparan melawan putaran mengurangi kecepatan keliling itu, jadi bola lebih ringan, jatuh lebih lambat, dan terbang lebih jauh.

| Lempar mendatar 20 m/s | Kecepatan keliling total | Berat yang terasa |
| --- | --- | --- |
| Searah putaran | 119,05 m/s | 1,445 g, lebih berat dan lebih pendek |
| Melawan putaran | 79,05 m/s | 0,637 g, lebih ringan dan lebih jauh |

Ini efek yang sama dengan motor: pada 150 km/h, 2,02 g searah putaran dan 0,34 g melawan putaran.

## Aturan praktis

| Gerak benda | Arah melenceng |
| --- | --- |
| Naik (menjauhi lantai) | Searah putaran |
| Turun (menuju lantai) | Melawan putaran |
| Mendatar searah putaran | Lebih berat, jatuh lebih cepat |
| Mendatar melawan putaran | Lebih ringan, terbang lebih jauh |
| Searah sumbu (ke end cap) | Tidak melenceng ke samping dan berat tidak berubah |

## Coba sendiri di Copper Corn Station

| Tempat | Cara |
| --- | --- |
| Air mancur Coriolis | Tombol 9 |
| Dek pandang menara 175 m | Panel atau E di lobi menara, lalu G (jatuhkan) dan B (lempar) |
| Di mana saja | Panel Fisika: lempar dan jatuhkan bola dengan kecepatan, sudut, dan tinggi pilihan; HUD menulis jarak dan arah melenceng |
| Motor di jalan cincin | Tombol C, lalu bandingkan berat terasa searah dan melawan putaran |
