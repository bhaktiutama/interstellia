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
| Baru: dek pandang menara ikon | (versi pertama, diganti di 18b-2) Dek 22 x 22 m di atap tingkat teratas (185,5 m) dengan lift. Tombol dek di panel Lokasi. B lempar bola, G jatuhkan bola ke luar pagar |

Hasil uji lempar bola versi pertama (`tools/uji_menara.py`, dek 185,5 m):

| Kasus | Belokan titik jatuh | Keterangan |
| --- | --- | --- |
| Jatuh dari dek (187,0 m) | 94,68 m | sama dengan hitungan analitik kerangka inersia (94,68 m), waktu jatuh 7,23 s |
| Jatuh dari 20 m di tanah | 2,72 m | pembanding |
| g lokal di dek | 0,8145 g | = 1 - h/R |

## 18b-2: revisi kedua setelah uji Bhakti

| Temuan | Perbaikan |
| --- | --- |
| Pelat dek 22 x 22 m di atap merusak bentuk menara | Pelat, pagar lebar, dan rumah lift dihapus. Dek pindah ke teras yang sudah ada di atap tingkat 4 (lebar 16 m, 175 m), keliling tingkat puncak (lebar 10 m). Lebar teras 3 m, hanya ditambah pagar di tepi. Tidak ada lantai baru |
| Lift tidak perlu | E di depan lobi = langsung di teras depan dek. E di mana saja di dek = langsung ke depan lobi. State `tlift` dihapus |
| Bayangan hitam di sebagian dinding, hilang saat didekati, membesar saat dijauhi | Penyebab: peta bayangan sunline diproyeksikan searah "atas" di posisi pemain. Pada gedung berjarak d, atas lokal miring d/R, jadi gedung jauh tampak condong dan atapnya menutupi dinding yang menghadap pemain (gedung 12 m pada 60 m: gelap di bawah 7,8 m). Perbaikan: setelah tinggi penghalang diketahui, sampel diulang di kolom yang benar-benar dilewati sinar radial lokal. Berlaku juga untuk faktor atap dan bayangan gedung tinggi di tanah |

Uji lempar bola dari dek baru:

| Kasus | Nilai | Sumber |
| --- | --- | --- |
| Jatuh dari 176,5 m (dek 175 m + tangan 1,5 m) | belok 85,67 m, waktu jatuh 6,96 s | hitungan analitik kerangka inersia; simulasi dicek oleh `tools/uji_menara.py` (selisih di bawah 5%) |
| g lokal di dek | 0,825 g | 1 - h/R |

## 18b-3: bayangan naik turun di dinding gedung dan rumah

Temuan Bhakti: bayangan gelap di kaca gedung tinggi dan dinding rumah naik turun saat didekati, tidak di semua gedung.

| Item | Isi |
| --- | --- |
| Sumber | Dua peta bayangan: sunline (`SUNSH`) dan cincin lampu end cap (`SHADOW`, kuat saat senja, cahaya keemasan dari arah end cap). Keduanya dirender dari arah di posisi pemain. Karena stasiun melengkung, arah "atas" dan arah ke cincin cap di gedung yang jauh ke samping berbeda, jadi bayangannya bergeser tiap kali pemain bergerak ke samping |
| Terukur sebelum perbaikan | Pemain pindah 40 m ke samping: 9,9% titik dinding berubah untuk bayangan sunline, 12,6% untuk bayangan cincin cap, 13,9 sampai 15,6% titik berubah terang lebih dari 30%. Pindah 40 m searah sumbu: di bawah 1% |
| Perbaikan | Kedua peta dirender dalam koordinat silinder terbuka: tiap titik dipindah ke bidang datar dengan busur dan jarak dari sumbu tetap. Di koordinat ini arah atas lokal dan arah ke cincin cap sama di sepanjang keliling, jadi bayangan tidak lagi bergantung pada posisi pemain. Koreksi 18b-2 digantikan cara ini |
| Uji | `tools/uji_cahaya_lanjut.py`: titik dinding yang berubah saat pemain pindah 40 m (keliling dan sumbu, siang dan senja) harus di bawah 2% |

## Catatan teknis

- Loop lama tetap dijalankan tanpa membangun apa pun, supaya urutan `rnd()` / `U()` / `pick()` untuk rumah pertanian dan seterusnya tidak bergeser. Kompleks baru memakai generator acak sendiri (benih 20260928).
- Jumlah bangunan bertambah sekitar 7.000 kotak (termasuk blok atas, unit atap, tangki, rak pipa). Perlu dicek FPS di GTX 1060 dan M1.
