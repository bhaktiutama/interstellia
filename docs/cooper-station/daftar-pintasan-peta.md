# Daftar usulan pintasan peta: tempat ikonik dan fisika (Copper Corn Station)

Status: kelompok A selesai (penanda D H A U W J K B di peta, tab Fisika). Kelompok B tidak dibangun (keputusan Bhakti).

## Ringkasan

- Pintasan peta saat ini ada 14: rumah Cooper, bukit, jagung, gandum, Skyway, baseball, terminal, kokpit, air mancur Coriolis, hutan, lift, pusat New York, Pasar New York, dan pasar tani.
- Usulan kelompok A berisi 8 tempat yang sudah ada di dunia tetapi belum punya pintasan. Bisa langsung dibuat.
- Usulan kelompok B berisi 8 tempat yang belum ada dan perlu dibangun dulu. Masing-masing menunjukkan satu hukum fisika silinder berputar.

## A. Sudah ada di dunia, belum ada pintasan

Huruf penanda di peta: A1 = D, A2 = H, A3 = A, A4 = U, A5 = W, A6 = J, A7 = K, A8 = B. Angka A1 dikoreksi ke 85,7 m (uji dek pandang 23j, `tools/uji_menara.py`).

| No | Tempat | Fisika yang terlihat | Angka |
| --- | --- | --- | --- |
| A1 | Dek pandang menara ikon (175 m) | g turun dengan ketinggian; bola dijatuhkan melenceng ke belakang putaran | g 0,825; jatuh 6,92 s; melenceng 85,7 m |
| A2 | Hub nol-g di sumbu (ujung lift) | Tanpa berat di sumbu; benda melayang | g 0 |
| A3 | Akuaduk Skyway + pipa pompa (23i) | Sungai melingkar tidak punya turunan, jadi airnya harus dipompa | angkat 4 m, debit 45 m3/s, sekitar 15,7 MW |
| A4 | Rumah pompa di kompleks utilitas | Ujung pipa isap dan pipa dorong | 2 pipa diameter 3,6 m, panjang 4,2 dan 4,3 km |
| A5 | Danau terbesar (s 4.100, za 5.600) | Muka air diam mengikuti lengkung silinder, bukan bidang datar | lebar 440 m, melengkung 24 m |
| A6 | Jalan cincin struktur (lintasan motor) | Berat terasa naik saat melaju searah putaran, turun saat melawan | 150 km/h: 2,02 g searah, 0,34 g melawan |
| A7 | Dermaga spaceport (despun, end cap A) | Dermaga tidak ikut berputar; sandar ke stasiun yang berputar | putaran 63,4 s |
| A8 | Tepi end cap B (jendela sinar) | Sinar Matahari masuk 25 derajat dari sumbu; gerhana Saturnus tiap orbit | jangkauan sinar 4,3 km; gerhana 2,78 jam |

## B. Belum ada, perlu dibangun

| No | Tempat usulan | Fisika yang ditunjukkan | Angka / catatan |
| --- | --- | --- | --- |
| B1 | Bandul Foucault di museum sains (pusat New York) | Di lantai silinder, bidang ayun tidak berputar seperti di Bumi (sumbu putar sejajar lantai); yang terlihat adalah tegangan tali yang berubah bila diayun searah keliling | laju presesi 0 |
| B2 | Velodrom / lintasan lari melingkar | Pelari atau pesepeda searah putaran lebih berat, melawan putaran lebih ringan; papan g langsung | 10 m/s: 1,21 g dan 0,81 g |
| B3 | Menara jatuh bebas (drop tower) 60 m | Kapsul jatuh lurus di kerangka inersia, tampak melengkung dari dalam | jatuh 3,66 s, melenceng 14,8 m |
| B4 | Air terjun di hilir akuaduk | Air jatuh melenceng ke belakang putaran (Coriolis) | tinggi 4 m: jatuh 0,91 s, melenceng 0,24 m |
| B5 | Observatorium di distrik astronom | Bintang di lantai kaca berputar sekali tiap 63,4 s; Saturnus dan Matahari | periode 63,4 s |
| B6 | Taman bermain fisika (ayunan, jungkat-jangkit, trampolin) | Periode ayunan dan tinggi lompatan bergantung pada g dan arah | lompat tegak 2 m/s: 0,41 s |
| B7 | Pembangkit dan radiator panas | Panas stasiun dibuang lewat radiator di lambung luar | perlu angka daya stasiun |
| B8 | Stasiun trem pusat dan terminal bus | Tempat penting (transportasi), bukan fisika | 3 jalur bus, 72 halte sudah ada |

## Catatan

- Angka A1 dihitung dari lintasan lurus di kerangka inersia (R 1.000 m, omega 0,09905 rad/s), sama dengan cara uji dek pandang.
- Angka A3 dan A4 dihitung untuk pipa baja (kekasaran 0,045 mm, Darcy-Weisbach) dengan angkat statis 4 m dan efisiensi pompa 80%.
- Angka B2, B3, dan B4 dihitung dengan cara yang sama (B2: g' = (omega R + v)^2 / R) dan dihitung ulang saat dibangun.
- Tombol angka 0-9 sudah terpakai. Pintasan baru cukup berupa penanda huruf di peta, seperti N, P, dan T.

## Hasil kelompok A (peta)

| Bagian | Isi |
| --- | --- |
| Penanda | 8 penanda cyan (D, H, A, U, W, J, K, B) di peta 2D dan hologram; klik = pindah. H langsung ke hub nol-g, K = hub lalu kapsul ke dermaga despun (berakhir di kokpit), D = dek pandang |
| Lokasi tujuan | `SPOTS.aqueduct`, `pump`, `lake`, `ring`, `capB`; diuji tidak di dalam collider atau air |
| Kolom samping | Tab Tempat, Fisika, Distrik, Legenda (tab diingat di localStorage `cooperStation.mapTab`); baris lebih rapat, legenda dua kolom |
| Hologram 3D | Kanvas 2D (tanpa konteks WebGL kedua): silinder tembus pandang, zona berwarna, cincin struktur, Skyway, rel trem, sungai, danau, lift, sumbu, dermaga, penanda, posisi pemain; sisi jauh lebih redup; berputar pelan, seret = putar, klik ganda = sudut awal |
| Sorot | Arahkan mouse ke baris tempat atau distrik (atau ke penanda di peta 2D): silinder berputar sampai tempat itu di sisi dekat, penanda berkedip dengan cincin dan nama; peta 2D ikut memberi cincin berkedip |
