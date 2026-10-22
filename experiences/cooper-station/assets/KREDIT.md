# Kredit aset

| File | Isi | Sumber dan lisensi |
| --- | --- | --- |
| `motor.data.js` | Model motor café racer V-twin (tahap 19c) | "moto guzzi v-twin" oleh Alexios Apokaukos (https://sketchfab.com/Alexios_Apokaukos), https://sketchfab.com/3d-models/moto-guzzi-v-twin-923c2932481141c8a1966d427a5d3b30, lisensi CC BY 4.0 (http://creativecommons.org/licenses/by/4.0/) |
| `orang.data.js` | Model orang pejalan kaki (tahap 28, dibuat oleh `tools/siapkan_orang.mjs`) | "Ultimate Modular Men Pack" dan "Ultimate Modular Women Pack" oleh Quaternius (https://quaternius.com), via Poly Pizza (https://poly.pizza), lisensi CC BY / CC0 (atribusi wajib): Ultimate Modular Women Pack by Quaternius [CC-BY] via Poly Pizza; Ultimate Modular Men Pack by Quaternius via Poly Pizza |
| `rumput.data.js` | Rumput fluffy (tahap 29, dibuat oleh `tools/siapkan_rumput.py`): mesh rumpun 3 tingkat detail, tekstur alfa `grass.jpeg`, `perlinnoise.webp`, dan algoritma shader `GrassMaterial.ts` | FluffyGrass oleh Ebenezer (https://github.com/thebenezer/FluffyGrass), lisensi MIT, Copyright (c) 2023 Ebenezer. Teks lisensi: izin diberikan secara gratis untuk memakai, menyalin, mengubah, dan mendistribusikan dengan syarat pemberitahuan hak cipta dan izin ini disertakan; perangkat lunak disediakan apa adanya tanpa jaminan apa pun |
| `jupiter.data.js` | Peta global Jupiter (tahap 30, dibuat oleh `tools/siapkan_jupiter.py`) | "Cassini's Best Maps of Jupiter (Cylindrical Map)", PIA07782, NASA/JPL/University of Arizona, dari gambar kamera sudut sempit Cassini ISS saat terbang lintas Jupiter Desember 2000. Domain publik (materi NASA tanpa batasan hak cipta; kredit tetap dicantumkan): https://science.nasa.gov/photojournal/cassinis-best-maps-of-jupiter-cylindrical-map/. Diubah: diperkecil dari 3601 x 1801 ke 3600 x 1800, JPEG mutu 84 |

Perubahan dari sumber (dibuat ulang dengan `python tools/siapkan_motor.py sumber.glb`):

- Tekstur warna dasar diperkecil (128-1024 piksel, JPEG; rem PNG). Peta normal, kekasaran-logam, tangen, dan warna verteks dibuang.
- Geometri dipindah ke kerangka motor halaman, mesh ganda dibuang, dikelompokkan menjadi badan, bagian depan (ikut kemudi), dan standar samping.
- Di halaman ditambahkan: dial speedometer, lampu depan dan belakang yang menyala, pengendara (tangan, kaki, bayangan tubuh).

Tangki memakai livery dengan logo elang Moto Guzzi dari model sumber (merek dagang milik pemiliknya). Proyek ini proyek penggemar non-komersial, tidak berafiliasi dengan Moto Guzzi.

Perubahan dari paket Quaternius (tahap 28, `node tools/siapkan_orang.mjs`):

- Karakter terpilih digabung per karakter, satuan dan sumbu dibakar ke meter y-atas, bentuk disederhanakan menjadi 3 tingkat detail, warna titik dan kelas warna (kulit, rambut, baju, celana, sepatu) dikemas ulang, animasi dibakar ke tekstur (klip Walk, Idle, Wave, Interact) ditambah klip duduk dan payung buatan sendiri.
- Berkas GLB sumber tidak ada di repo.

Perubahan dari FluffyGrass (tahap 29): mesh dikonversi ke data base64 dan diskalakan 5x seperti sumbernya; shader diport ke vertex shader instancing Copper (penyebaran lewat sel dan peta lahan, tinggi tanah silinder, warna dari peta lahan dengan rasio palet sumber, cahaya stasiun `vegLight()`); tekstur alfa dan noise dipakai apa adanya.

Teks lisensi MIT sumber:

```
MIT License

Copyright (c) 2023 Ebenezer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
