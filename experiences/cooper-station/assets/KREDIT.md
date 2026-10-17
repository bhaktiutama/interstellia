# Kredit aset

| File | Isi | Sumber dan lisensi |
| --- | --- | --- |
| `motor.data.js` | Model motor café racer V-twin (tahap 19c) | "moto guzzi v-twin" oleh Alexios Apokaukos (https://sketchfab.com/Alexios_Apokaukos), https://sketchfab.com/3d-models/moto-guzzi-v-twin-923c2932481141c8a1966d427a5d3b30, lisensi CC BY 4.0 (http://creativecommons.org/licenses/by/4.0/) |
| `orang.data.js` | Model orang pejalan kaki (tahap 28, dibuat oleh `tools/siapkan_orang.mjs`) | "Ultimate Modular Men Pack" dan "Ultimate Modular Women Pack" oleh Quaternius (https://quaternius.com), via Poly Pizza (https://poly.pizza), lisensi CC BY / CC0 (atribusi wajib): Ultimate Modular Women Pack by Quaternius [CC-BY] via Poly Pizza; Ultimate Modular Men Pack by Quaternius via Poly Pizza |

Perubahan dari sumber (dibuat ulang dengan `python tools/siapkan_motor.py sumber.glb`):

- Tekstur warna dasar diperkecil (128-1024 piksel, JPEG; rem PNG). Peta normal, kekasaran-logam, tangen, dan warna verteks dibuang.
- Geometri dipindah ke kerangka motor halaman, mesh ganda dibuang, dikelompokkan menjadi badan, bagian depan (ikut kemudi), dan standar samping.
- Di halaman ditambahkan: dial speedometer, lampu depan dan belakang yang menyala, pengendara (tangan, kaki, bayangan tubuh).

Tangki memakai livery dengan logo elang Moto Guzzi dari model sumber (merek dagang milik pemiliknya). Proyek ini proyek penggemar non-komersial, tidak berafiliasi dengan Moto Guzzi.

Perubahan dari paket Quaternius (tahap 28, `node tools/siapkan_orang.mjs`):

- Karakter terpilih digabung per karakter, satuan dan sumbu dibakar ke meter y-atas, bentuk disederhanakan menjadi 3 tingkat detail, warna titik dan kelas warna (kulit, rambut, baju, celana, sepatu) dikemas ulang, animasi dibakar ke tekstur (klip Walk, Idle, Wave, Interact) ditambah klip duduk dan payung buatan sendiri.
- Berkas GLB sumber tidak ada di repo.
