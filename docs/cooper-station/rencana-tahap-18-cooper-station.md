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

## Catatan teknis

- Loop lama tetap dijalankan tanpa membangun apa pun, supaya urutan `rnd()` / `U()` / `pick()` untuk rumah pertanian dan seterusnya tidak bergeser. Kompleks baru memakai generator acak sendiri (benih 20260928).
- Jumlah bangunan bertambah sekitar 7.000 kotak (termasuk blok atas, unit atap, tangki, rak pipa). Perlu dicek FPS di GTX 1060 dan M1.
