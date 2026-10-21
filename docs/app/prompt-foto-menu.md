# Prompt foto menu: versi Realistis dan Kartun

Untuk generator gambar AI luar. Hasilnya dipakai sebagai gaya foto di menu (prototipe `docs/app/menu-infografis-v3.html`, pemilih gaya Poles / Realistis / Kartun / Asli).

## Ringkasan
- Pakai mode gambar-ke-gambar (img2img, "edit with reference", "image prompt") dengan foto acuan dari `docs/app/menu/asli/`.
- Komposisi wajib sama: penanda di halaman memakai posisi persen, jadi objek tidak boleh bergeser dan rasio aspek harus sama.
- Prompt ditulis dalam English (generator paling paham English); terjemahan singkat ada di bawah tiap prompt.

## Pengaturan
| Item | Realistis | Kartun |
| --- | --- | --- |
| Foto acuan | `docs/app/menu/asli/<nama>.webp` | sama |
| Kekuatan ubah (denoise / strength) | 0,35 - 0,5 | 0,55 - 0,7 |
| Kunci komposisi (bila ada) | ControlNet depth + canny, bobot 0,6 - 0,8 | ControlNet canny / lineart, bobot 0,7 - 0,9 |
| Ukuran keluaran | sama dengan acuan atau kelipatannya | sama |

Ukuran acuan: cooper 1202 x 835, gargantua 1164 x 893, millar 1535 x 940.

Bila objek bergeser atau wahana berubah bentuk: turunkan kekuatan ubah 0,1 atau naikkan bobot ControlNet.

## Aturan (wajib)
- Jangan menulis judul film, nama studio, nama sutradara, atau nama kendaraan film di prompt. Proyek ini orisinal.
- Bentuk wahana harus tetap seperti di foto (GX-01 dan KS-07 desain sendiri).
- Jangan menambah orang, teks, logo, atau objek baru.

## Prompt negatif (pakai untuk semua)
```
text, letters, logo, watermark, signature, ui, extra objects, extra spacecraft, people, characters, changed spacecraft shape, deformed geometry, duplicated structures, blurry, low resolution, jpeg artifacts, oversaturated, frame border
```

## 1. Copper Corn Station (`cooper`)

### Realistis
```
Photorealistic cinematic photograph from inside a giant rotating O'Neill cylinder space habitat, looking along the central axis. A dense city with skyscrapers, residential blocks, green parks, patchwork farm fields and a winding river wrap all around the inner wall and curve overhead into a tunnel. A thin bright line of light runs along the central axis toward a distant circular end cap. Natural soft daylight, atmospheric haze increasing with distance, realistic materials, concrete, glass and vegetation detail, shot on a full-frame cinema camera, 24mm wide lens, subtle film grain, high dynamic range, sharp focus, same composition as the reference image.
```
ID: foto sinematik dari dalam silinder O'Neill, kota, ladang, dan sungai melingkar ke atas, garis cahaya di sumbu menuju end cap, kabut makin jauh, komposisi sama.

### Kartun
```
Stylized cel-shaded animation illustration from inside a giant rotating cylinder space habitat, looking along the central axis. A colorful city with tall towers, small houses, green parks, patchwork farm fields and a winding blue river wrap around the inner wall and curve overhead into a tunnel. A bright line of light runs along the axis toward a distant round end cap. Clean ink outlines, flat color fills with two-step shading, soft gradients in the sky, warm friendly palette, hand-painted background art style of a feature animation film, same composition as the reference image.
```
ID: ilustrasi animasi cel-shaded, garis tinta rapi, warna rata dengan dua tingkat bayangan, palet hangat, komposisi sama.

## 2. Gargantua (`gargantua`)

### Realistis
```
Photorealistic cinematic space photograph. A small dark angular spacecraft flies low over the glowing golden accretion disk of a supermassive spinning black hole. Behind it, the disk's light is gravitationally lensed into a bright arc over and under a perfectly black circular shadow, with a thin photon ring. Hot orange streaks of plasma and embers rush past, dense starfield in the black sky. Physically based lighting from the disk, realistic metal hull with panel detail lit warm from below, volumetric glow, deep blacks, anamorphic lens, subtle film grain, IMAX-style space cinematography, same composition as the reference image.
```
ID: foto sinematik luar angkasa, wahana kecil gelap menyusur rendah di atas piringan akresi emas, cahaya piringan melengkung di atas dan di bawah bayangan hitam, garis bara, bintang, komposisi sama.

### Kartun
```
Stylized cel-shaded animation illustration. A small dark angular spacecraft glides low over the swirling golden disk of a giant black hole. The disk light bends into a glowing arc over and under a pure black round shadow with a thin bright ring. Orange streaks and sparks zip past, sparkling stars in a deep navy sky. Bold ink outlines, flat color shapes with simple glow effects, graphic swirl patterns in the disk, dramatic but friendly feature animation art style, same composition as the reference image.
```
ID: ilustrasi animasi, wahana di atas piringan berpusar emas, lengkung cahaya di sekitar bayangan hitam, percikan oranye, garis tinta tebal, komposisi sama.

## 3. Millar's World (`millar`)

### Realistis
```
Photorealistic cinematic photograph seen through the curved visor of an astronaut helmet, standing in a vast shallow pale ocean with no land. On the horizon a colossal wall of water, a giant tidal wave hundreds of meters tall, stretches across the whole view with white foam streaks falling from its face. Above it, a huge black hole with a bright lensed ring hangs in an overcast cream-grey sky. On the right, a dark matte landed spacecraft stands on thin legs in the water with a small red light. Diffuse overcast light, realistic water surface with small choppy waves and reflections, faint condensation on the visor edges, shot on a cinema camera, 35mm lens, subtle film grain, same composition as the reference image.
```
ID: foto sinematik lewat visor helm, laut dangkal pucat, tembok gelombang raksasa di cakrawala dengan buih, lubang hitam bercincin di langit mendung, wahana gelap bertiang di kanan, komposisi sama.

### Kartun
```
Stylized cel-shaded animation illustration seen through the rounded frame of an astronaut helmet visor. A calm pale shallow ocean stretches to the horizon, where an enormous wall of water, a giant wave, spans the whole view with white foam streaks. A huge black hole with a glowing ring floats in a soft cream sky. On the right, a dark spacecraft stands on thin legs in the water with a tiny red light. Clean ink outlines, flat muted colors with two-step shading, painterly sky gradient, simple stylized wave patterns, feature animation background art style, same composition as the reference image.
```
ID: ilustrasi animasi lewat bingkai visor, laut pucat tenang, tembok gelombang besar, lubang hitam bercincin di langit krem, wahana gelap bertiang, warna redup rata, komposisi sama.

## Mengirim hasil
- Nama file: `cooper`, `gargantua`, `millar` (webp, jpg, atau png), dipisah per gaya: realistis dan kartun.
- Kirim di percakapan. Saya simpan di `docs/app/menu/real/` dan `docs/app/menu/kartun/`, dikonversi ke webp kualitas 90 dan diskalakan ke ukuran acuan, lalu tombol gayanya di v3 aktif dengan sendirinya.
- Cek sebelum kirim: posisi lubang hitam, wahana, sumbu, dan cakrawala sama dengan foto acuan. Kalau bergeser, penanda di halaman akan meleset.
