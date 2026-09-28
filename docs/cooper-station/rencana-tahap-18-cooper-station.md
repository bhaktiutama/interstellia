# Rencana Tahap 18 Copper Corn Station: kompleks utilitas

Per 28 September 2026 · Bhakti

## Ringkasan

- **18a (selesai):** pita utilitas (za 6.400-6.900, satu keliling penuh) diganti dari 4 baris gudang berjarak 100-150 m menjadi kompleks padat seperti mozaik kotak.
- Modul berdempetan, dipisah lorong 2,5-4,5 m; jalan servis dan rak pipa menyatukan kompleks.
- Bagian lain stasiun tidak berubah (urutan angka acak bersama dijaga).

## Isi

| Bagian | Isi |
| --- | --- |
| Jalan servis | 1 jalan keliling di tengah pita (10 m), 2 jalan sekunder (7 m) di 125 m dari tengah, jalan silang tiap 70-130 m |
| Blok | Tiap blok dipecah berulang (BSP) menjadi modul 8-60 m; lorong 2,5-4,5 m |
| Modul | Gudang dan hanggar 6-20 m (12% setinggi 24-30 m), 45% diberi blok atas bertangga, 50% diberi 1-2 unit atap |
| Gugus tangki | 10% modul: 2x2 sampai 3x3 tangki di atas alas beton |
| Cerobong | 6% modul kecil: cerobong 30-48 m di atas alas 5 m |
| Rak pipa | Di atas tiap jalan servis keliling, tinggi 6,5 m, tiang tiap 30 m |
| Dihindari | Koridor trem, promenade Skyway, air dan sungai |

Hasil uji: 2.888 modul, 1.155 tangki, 165 segmen rak pipa, tanpa tumpang tindih, tidak ada di Skyway (`tools/uji_cahaya_lanjut.py`).

## 18b: revisi setelah uji Bhakti (Ultra)

| Temuan | Perbaikan |
| --- | --- |
| Atap lengkung pasar terangkat | Jari-jari 12 m (dulu 12,5 m, melebihi setengah kedalaman gedung 24 m), dasar 0,3 m masuk dinding (6,2 m), lisplang di kedua sisi panjang, salinan bernormal terbalik agar terlihat dari bawah dan dalam |
| Gereja tanpa pintu | Pintu gaya 7 di muka depan badan tertutup menara; kini menara juga berpintu di muka -za |
| Gereja, masjid, pasar tanpa halaman keras | Pelataran beton (`PAL.plaza`) di depan sampai jalan dan pinggiran 2,5 m sekeliling tapak; pasar: pelataran gedung dan lantai beton di area lapak. Rumput di sisa blok tetap |
| Jendela rumah Cooper tampak gelap dari dalam | Dinding dan plester kini berlubang jendela sungguhan (`holeWall`), kusen berupa bingkai, kaca bening transparan (tetap memantul di sudut miring). Dari dalam terlihat luar yang terang |
| Bayangan hitam di dinding gedung (Ultra) | Sampel PCF bayangan sunline diberi bobot Lambert terhadap arah elemen garis sunline (dinding hanya diuji terhadap separuh garis di depannya); atap dihitung dari titik yang digeser 1 m searah normal, jadi dinding luar tidak lagi dianggap di bawah atap |
| Baru: dek pandang menara ikon | Dek 22 x 22 m di atap tingkat teratas (185,5 m), pagar, rumah lift. Aksi E di depan lobi = lift 22 s naik; E di depan pintu rumah lift = turun. Tombol "Dek pandang menara (185 m)" di panel Lokasi. B lempar bola, G jatuhkan bola ke luar pagar |

Hasil uji lempar bola (`tools/uji_menara.py`):

| Kasus | Belokan titik jatuh | Keterangan |
| --- | --- | --- |
| Jatuh dari dek (187,0 m) | 94,68 m | sama dengan hitungan analitik kerangka inersia (94,68 m), waktu jatuh 7,23 s |
| Jatuh dari 20 m di tanah | 2,72 m | pembanding |
| g lokal di dek | 0,8145 g | = 1 - h/R |

## Catatan teknis

- Loop lama tetap dijalankan tanpa membangun apa pun, supaya urutan `rnd()` / `U()` / `pick()` untuk rumah pertanian dan seterusnya tidak bergeser. Kompleks baru memakai generator acak sendiri (benih 20260928).
- Jumlah bangunan bertambah sekitar 7.000 kotak (termasuk blok atas, unit atap, tangki, rak pipa). Perlu dicek FPS di GTX 1060 dan M1.
