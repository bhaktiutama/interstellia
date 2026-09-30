# Rencana M3 Millar's World: Shuttle KS-07 v3 dan Misi Radar

Per 30 September 2026 · Status: M3a, M3b, dan M3c selesai (lihat bagian "Status"), berikutnya M3d naik dan lolos

## Ringkasan

- Model shuttle: KS-07 v3 (hibrida, `docs/app/konsep-ks07-v3.md`), dipilih pemilik. Dipasang lewat modul bersama `shared/kestrel.js`; Copper Corn Station tetap memakai model lama sampai tahap M3e.
- Misi: pakai radar untuk menemukan 3 pecahan pesawat misi sebelumnya (salah satunya membawa blackbox), ambil barang di tiap lokasi, kembali ke shuttle, lepas landas, dan lolos dari gelombang raksasa. Seluruh misi bisa diselesaikan di bawah 5 menit, dengan gelombang tiba tepat di menit ke-5.
- Tahap: M3b model v3, M3c misi radar, M3d naik dan lolos, M3e Copper memakai v3. Pandangan orbit dan sinematik kedatangan tetap di M4.

## Alur permainan (mode Misi)

| Langkah | Yang dilakukan pemain | Yang terjadi |
| --- | --- | --- |
| 1. Tiba | Berdiri di samping KS-07, hitung mundur 5:00 mulai | Laut tenang, gelombang 37,5 km di balik cakrawala |
| 2. Buka radar | M (tombol peta di Copper) | Layar radar genggam: sapuan 2 s, jangkauan 250 m, tanda 3 sinyal. Makin dekat, makin tepat |
| 3. Ke lokasi | Berjalan atau lari di air (Shift) | Suar kuning berkedip di tiap pecahan terlihat dari sekitar 150 m; blackbox berbunyi ping yang makin cepat saat mendekat |
| 4. Ambil barang | Tahan E 2 s di dekat barang | Barang masuk daftar (1/3, 2/3, 3/3) |
| 5. Ulangi | Sampai 3 lokasi | Keadaan laut naik saat gelombang mendekat, arus surut 20 s terakhir |
| 6. Kembali | Ke pintu KS-07, E naik | Masuk kokpit |
| 7. Lolos | E lepas landas, naik di atas puncak gelombang (1,2 km) | Gelombang lewat di bawah: selamat. Masih di air atau terlalu rendah: tersapu, misi gagal |
| 8. Hasil | Layar ringkasan | Waktu planet terpakai, waktu di luar (hari dan tahun), barang, tombol ulangi (posisi baru) |

## Angka waktu (dari kode)

| Item | Nilai | Dasar |
| --- | --- | --- |
| Kecepatan lari di air | sekitar 1,7 m/s | 4,2 m/s x (1 - 0,9 x kedalaman 0,66 m) = 0,41 dari `stepPlayer()` |
| Kecepatan jalan di air | sekitar 0,6 m/s | 1,5 m/s x 0,41 |
| Batas waktu | 5:00 (300 s) | Permintaan pemilik |
| Jarak awal gelombang | 37,5 km | 300 s x 125 m/s |
| Panjang rute (shuttle, 3 lokasi, kembali) | 250-330 m, diacak tiap percobaan | Rute terpendek dihitung saat memilih lokasi |
| Waktu lari rute | 150-195 s | 330 m / 1,7 m/s |
| Ambil barang | 3 x 2 s | Tahan E |
| Membaca radar, belok, ragu | sekitar 20 s | Perkiraan |
| Naik, lepas landas, naik ke 1,3 km | sekitar 45 s | Pintu 5 s, lepas landas 5 s, naik rata-rata 37 m/s |
| Total perkiraan | 225-270 s | Sisa 30-75 s |
| Waktu di luar untuk 5 menit planet | sekitar 213 hari (0,58 tahun) | 1 jam = 7 tahun |

Semua angka jadi parameter di `CONFIG.mission` (batas waktu, jangkauan lokasi, panjang rute, laju naik), dan ada pilihan tingkat: Santai 7:00, Normal 5:00, Sulit 4:00.

## Radar

| Hal | Rancangan |
| --- | --- |
| Tombol | M buka/tutup (sama dengan peta di Copper). Bisa berjalan saat radar terbuka |
| Tampilan | Lingkaran di bawah tengah layar, arah pandang di atas, sapuan berputar 2 s, cincin 50 m |
| Sinyal | Tiap sapuan memperbarui titik sinyal dengan galat 5% jarak + 2 m (jauh = kabur, dekat = tepat). Di luar 250 m: panah di tepi dengan jarak kira-kira |
| Warna | Pecahan kuning, blackbox jingga berkedip, shuttle putih, sudah diambil = abu |
| Suara | Bip sapuan; blackbox mengirim ping sendiri (makin cepat dan makin keras saat dekat, arah kiri/kanan) |

## Lokasi pecahan (desain orisinal)

| Lokasi | Isi | Barang |
| --- | --- | --- |
| Pecahan 1 | Panel lambung bengkok setengah terendam, kantong apung jingga | Modul data navigasi |
| Pecahan 2 | Kaki pendarat patah dan tangki silinder | Modul data sensor |
| Pecahan 3 | Potongan kabin terbesar, antena patah | Blackbox |

Semua pecahan punya suar kuning berkedip dan riak di sekitarnya. Posisi diacak tiap percobaan: 50-130 m dari shuttle, jarak antarlokasi minimal 40 m, rute terpendek 250-330 m.

## Tahapan

| Tahap | Isi | Yang diuji pemilik |
| --- | --- | --- |
| M3a Shuttle mendarat | Selesai (model lama v1, lihat status) | - |
| M3b KS-07 v3 | `KESTREL.buildV3(THREE)` di modul bersama (loft segi delapan, tanpa addon), Millar memakai v3: 4 kaki, pintu dan tangga di sisi luar lengan kiri, tabrakan kaki dan blok belakang, lampu navigasi dan strobo, riak di kaki. Copper tetap v1 | Tampilan v3 di laut mendung, skala |
| M3c Misi radar | Pilihan mode Misi / Jelajah di layar awal, 3 lokasi pecahan acak, radar M, ping blackbox, ambil barang dengan E, HUD tujuan dan hitung mundur, gelombang tiba tepat di batas waktu, tingkat Santai / Normal / Sulit | Keterbacaan radar, apakah 5 menit pas |
| M3d Naik dan lolos | E di pintu = naik, kokpit, E = lepas landas vertikal (semburan air, suara mesin), kendali terbang tombol pesawat Copper (W/S, A/D, R/F, mouse, Shift), lolos bila di atas puncak saat gelombang lewat, gagal bila tersapu, layar hasil dan ulangi | Ketegangan lepas landas, layar hasil |
| M3e Copper memakai v3 | Model v3 di dermaga, cincin sandar di punggung badan tengah, posisi mata kokpit, uji spaceport | Dermaga Copper |
| M4 (konsep) | Pandangan orbit, sinematik kedatangan | Keseluruhan |

## Keputusan (dipakai pilihan yang disarankan, masih bisa diganti)

| No | Pertanyaan | Pilihan | Dipakai |
| --- | --- | --- | --- |
| 1 | Isi 3 lokasi | a. 3 pecahan, blackbox ada di pecahan ketiga (disarankan) · b. 3 pecahan + blackbox terpisah (4 lokasi) | a |
| 2 | Urutan lokasi | a. Bebas (disarankan) · b. Harus berurutan | a |
| 3 | Gagal (tersapu) | a. Layar hasil "gagal" + ulangi dengan posisi baru (disarankan) · b. Kembali ke titik awal, waktu jalan terus | a |
| 4 | Tombol radar | a. M (seperti peta di Copper, disarankan) · b. Radar kecil selalu tampil | a |
| 5 | Mode Jelajah | a. Tetap ada (perilaku sekarang, G panggil gelombang) (disarankan) · b. Dihapus | a |

## Catatan teknis

| Hal | Keputusan |
| --- | --- |
| Modul bersama | Skrip biasa (bukan modul ES) yang memasang `window.KESTREL`, dimuat dengan `<script src="../../shared/kestrel.js">` sebelum skrip modul (modul ES tidak bisa diimpor dari file://) |
| Model lama | `KESTREL.build()` (v1) tetap ada dan identik untuk Copper sampai M3e |
| Material di Millar | Shader sendiri agar cahaya, kabut, dan lengkung planet sama dengan laut |
| Waktu gelombang | Mode Misi memasang muka gelombang di 37,5 km saat mulai dan mematikan G; mode Jelajah tetap seperti sekarang |

## Risiko

| Risiko | Penanganan |
| --- | --- |
| 5 menit terlalu ketat atau terlalu longgar | Semua angka di `CONFIG.mission`, tingkat Santai / Normal / Sulit; uji otomatis menjalankan rute terpendek dengan kecepatan lari dan memeriksa sisa waktu |
| Radar membingungkan | Galat mengecil saat dekat, suar kuning terlihat dari 150 m, ping blackbox |
| Pemain tersesat jauh | Panah shuttle di tepi radar, jarak shuttle di HUD |

## Status M3a

Selesai 30 September 2026.

| Bagian | Isi |
| --- | --- |
| Modul bersama | `shared/kestrel.js`: `KESTREL.build(THREE)` (geometri shuttle, sama persis dengan Copper tahap 11d), `KESTREL.gear(THREE, padDrop)` (kaki pendarat), `mergeColored`, profil `W` / `HT` / `HB` |
| Copper | `SHUTTLE = window.KESTREL.build(THREE)`; sidik jari 8 mesh shuttle pemain dan AI sama persis sebelum dan sesudah, uji spaceport lulus (pintu, gerbang B1, lepas sandar, sandar otomatis) |
| Posisi | 30 m dari titik awal, 60 derajat ke kanan dari arah pandang awal (ekor terlihat di tepi kanan, arah datang gelombang tetap terbuka) |
| Kaki pendarat | Hidung + dua utama, tabung atas, batang teleskop krom, kerah kuning, penopang diagonal, tapak lebar 1,5 m; tapak tertinggi menyentuh dasar laut |
| Shading | Langit mendung dari atas, pantulan laut dari bawah, pantulan cubemap langit dengan Fresnel, jendela kokpit mengilap, bagian dekat muka air lebih gelap dan basah, kabut, ikut lengkung planet |
| Lampu | Merah (kiri), hijau (kanan), strobo putih berkedip tiap 1,3 s |
| Air | Riak dan buih kecil di kaki tiap 0,6-0,9 s bila di dekat pemain |
| HUD | Baris "Shuttle KS-07" (jarak) |

Perbaikan lama yang ditemukan saat pengecekan: cincin laut jauh (70 m sampai cakrawala) punya urutan segitiga terbalik sejak R1, sehingga dibuang backface culling. Dari tampilan jalan kaki hampir tidak terlihat (yang tampak adalah langit di bawah cakrawala), tetapi dari drone laut hanya berupa lingkaran 70 m. Kini laut jauh tergambar sampai cakrawala.

Uji: `tools/uji_millar.py` kini 50 pemeriksaan, semua lulus, termasuk: sidik jari geometri KS-07 sama dengan Copper, celah tapak ke dasar laut 0,00-0,04 m, perut 1,55 m di atas muka air rata-rata (mata 0,95 m), pemain yang berjalan ke kaki tertahan di 1,07 m dari pusat tapak (batas 1,05 m), normal laut jauh ke atas, render dengan shuttle di layar tanpa nilai tidak valid atau titik menyala. Copper: `tools/uji_spaceport.py` lulus tanpa error.

Belum: gelombang raksasa melewati shuttle tanpa efek (shuttle tertutup dinding air lalu tampak lagi); ditangani di M3b bersama lepas landas.

## Status M3b

Selesai 30 September 2026.

| Bagian | Isi |
| --- | --- |
| Modul bersama | `KESTREL.buildV3(THREE)`: geometri disalin dari blokout v3 (satu geometri berwarna, 18.276 titik, normal datar per sisi), ditambah pintu awak dan tangga di sisi luar lengan kiri. Mengembalikan tapak 4 kaki, pintu, lampu navigasi, kotak bagian rendah, ukuran. `build()` v1 tetap ada dan identik untuk Copper |
| Millar | Shuttle diganti v3. Sisi berpintu menghadap titik awal (pintu 25 m dari titik awal), hidung ke arah datangnya gelombang, tapak di dasar laut, bawah lengan dan badan tengah 2,06 m di atas muka air rata-rata (bisa dilewati), blok belakang menahan pemain (bawahnya lebih rendah dari kepala) |
| Lampu | Merah di ujung lengan kiri, hijau di kanan, strobo di atas blok belakang |
| Copper | Tidak berubah: sidik jari 8 mesh shuttle sama persis, halaman termuat tanpa error |
| Kartu menu | `preview.jpg` dibuat ulang dengan v3 |

Uji: `tools/uji_millar.py` kini 53 pemeriksaan, semua lulus, termasuk: v1 di modul bersama tetap sama dengan Copper, v3 tanpa nilai tidak valid, celah tapak 0,00-0,05 m, kaki menahan pemain di 1,25 m, 0 langkah di bawah blok belakang, pintu di sisi yang menghadap titik awal, render dengan shuttle tanpa nilai tidak valid atau titik menyala.

Belum: stensil KS-07 (tekstur tulisan) belum dipasang di game; gelombang masih melewati shuttle tanpa efek (M3d).

## Status M3c

Selesai 30 September 2026.

| Bagian | Isi |
| --- | --- |
| Layar awal | Pilihan Mode (Misi / Jelajah) dan Tingkat misi (Santai 7:00, Normal 5:00, Sulit 4:00), tersimpan di localStorage `millar.mode` / `millar.level` |
| Lokasi | 3 pecahan diacak tiap percobaan: 50-130 m dari KS-07, antarlokasi minimal 40 m, rute terpendek (titik awal, 3 lokasi, pintu) 250-330 m |
| Pecahan | Desain orisinal lander misi sebelumnya: panel lambung bengkok + kantong apung jingga, tangki rebah + kaki patah, potongan kabin + antena patah. Tiap pecahan punya tiang suar kuning berkedip, barang dengan LED hijau berkedip, riak di sekitarnya, dan menahan pemain |
| Radar (M) | Lingkaran di bawah tengah layar, arah pandang di atas, cincin tiap 50 m, jangkauan 250 m, sapuan 2 s dengan klik halus. Titik sinyal diperbarui saat disapu, galat 5% jarak + 2 m (terukur 14,6 m di 200 m, 3,5 m di 15 m). Di luar jangkauan: panah di tepi + jarak kira-kira. Kuning = pecahan, jingga berkedip = blackbox, abu = sudah diambil, putih = KS-07 |
| Ping blackbox | Bip 1,45 kHz, selang 0,35-3 s dan makin keras saat dekat, arah kiri/kanan dari pandangan |
| Ambil | Tahan E 2 s dalam 3,2 m dari barang (petunjuk + batang kemajuan), bip naik saat berhasil |
| Naik | Setelah 3 barang: E di pintu KS-07 (3,5 m) = misi berhasil. Lepas landas menyusul di M3d |
| Gelombang | Diletakkan agar tiba tepat di batas waktu; G dimatikan di mode Misi. Tersapu = misi gagal |
| HUD | Baris "Misi" (barang / kembali ke KS-07) dan "Gelombang tiba" (hitung mundur, merah di menit terakhir) |
| Layar hasil | Berhasil / gagal, waktu planet, waktu di luar, barang, tingkat, sisa waktu; tombol Ulangi (posisi baru) dan Mode Jelajah |
| Panel ` | Radar nyala/mati, mulai ulang misi |

Uji: `tools/uji_millar.py` kini 58 pemeriksaan, semua lulus, termasuk: 200/200 benih lokasi memenuhi syarat (rute 254-330 m), gelombang tiba dalam 300,0 s di tingkat Normal, galat radar mengecil saat dekat, simulasi pemain berlari menyusuri rute terpendek 311 m + ambil 3 barang + naik = 207 s (ditambah cadangan lepas landas 45 s tetap di bawah 300 s), tersapu = layar hasil gagal. Uji fisika lama kini dijalankan di mode Jelajah.

Catatan: simulasi rute memakai laut saat gelombang masih jauh; di permainan nyata ombak membesar dan arus surut menarik pemain di 20 s terakhir, jadi sisa waktu sebenarnya lebih kecil. Angka mudah disetel di `CONFIG.mission`.

Berikutnya M3d: naik, lepas landas, dan lolos dari gelombang (serta pilihan wahana kecil v5, `docs/app/konsep-ks07-v5.md`).
