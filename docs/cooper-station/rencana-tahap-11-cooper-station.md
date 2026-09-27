# Rencana Tahap 11: Copper Corn Station

Status: usulan, belum dikerjakan. Semua yang sudah ada tetap dipertahankan.

## Ringkasan

- 6 fitur dibagi ke 4 sub-tahap (11a sampai 11d), diurutkan dari yang paling murah dan paling terlihat.
- Awan dinamis, bayangan awan, dan sunrays saling bergantung, jadi dikerjakan bersama di 11a dan 11b.
- Stasiun pesawat angkasa paling besar dan dikerjakan terakhir (11d), dengan desain pesawat orisinal (bukan tiruan pesawat dari film).

## Kondisi sekarang (titik awal)

| Fitur | Sudah ada | Kekurangan |
| --- | --- | --- |
| Awan | 45 gugus, billboard lembut, warna mengikuti jam | Diam di tempat, bentuk tidak berubah |
| Bayangan awan | Ada, tapi dipanggang sekali saat load (tekstur statis) | Tidak ikut bergerak bila awan bergerak |
| Sunrays | Belum ada | - |
| Kursi jalan | Belum ada (hanya bangku di halte dan tribun baseball) | - |
| Tempat sampah | Belum ada | - |
| Spaceport | Hanggar kotak di za 150-250, batang dermaga di luar end cap A, lift ke hub nol-g | Belum ada terminal, dermaga, dan pesawat |

## 11a. Awan dinamis + bayangan awan ikut bergerak

| Item | Rencana |
| --- | --- |
| Gerak | Awan hanyut pelan terbawa sirkulasi udara stasiun, sekitar 1-3 m/s. Arah utama sepanjang sumbu, dengan pusaran kecil |
| Bentuk | Tiap gugus berubah perlahan (noise waktu), terbentuk dan menghilang dalam beberapa menit, jadi langit tidak pernah sama |
| Tampilan | Billboard berlapis dengan tekstur noise, sisi bawah lebih gelap, tepi terang saat senja (cahaya cincin lampu end cap) |
| Bayangan | Tekstur bayangan dihitung ulang dari posisi awan terbaru, kecil (512 x 1024) dan diperbarui tiap beberapa detik, bukan dipanggang sekali |
| Fisika | Bayangan tetap lembut dan memanjang searah sumbu, karena sumbernya sunline berbentuk garis (sudah dihitung di tahap 6: sekitar 16% lebih gelap) |
| Kontrol | Tombol di panel Waktu dan simulasi: cerah, berawan, mendung |

Biaya: rendah. Pembaruan tekstur bayangan berjalan di CPU tiap beberapa detik.

## 11b. Sinar sunrays (berkas cahaya)

Dua sumber cahaya yang bisa menghasilkan berkas:

| Sumber | Bentuk berkas | Cara |
| --- | --- | --- |
| Sunline (sumbu) | Tirai cahaya turun dari sumbu, terputus-putus di celah antar-awan | Ray-march setengah resolusi di sepanjang garis pandang, cek apakah awan menghalangi titik itu dari sumbu (pakai data awan 11a) |
| Sinar Matahari asli lewat kaca end cap | Satu berkas miring dari end cap, berputar tiap 63,4 detik mengikuti rotasi stasiun | Metode yang sama, sumbernya arah Matahari |
| Cincin lampu end cap (senja) | Berkas keemasan dari ujung silinder | Opsional, mengikuti intensitas lampu |

- Hanya aktif di preset Ultra dan Tinggi.
- Kekuatan berkas diatur oleh kabut dan jam: paling jelas pagi dan senja.
- Biaya: sedang, satu pass layar setengah resolusi (8-16 sampel per piksel).

## 11c. Kursi dan tempat sampah di kota dan taman

| Objek | Lokasi | Kepadatan (rencana) |
| --- | --- | --- |
| Bangku jalan | Trotoar jalan arteri di kelas pusat dan menengah | Tiap 40-60 m per sisi, dekat persimpangan dan halte |
| Bangku taman | Sepanjang jalur taman kota, taman sungai (za 2.600-3.200), promenade Skyway, tepi danau | Tiap 25-40 m, menghadap pemandangan (sungai, danau, jendela Skyway) |
| Tempat sampah | Trotoar pusat kota dan menengah, samping bangku taman, halte trem | Tiap 50-80 m, selalu 1 di dekat bangku halte |
| Tambahan kecil | Pot bunga di pusat kota, lampu taman pendek | Opsional |

- Model: bangku kayu berangka besi, tempat sampah silinder logam dengan tutup. Masing-masing 1 InstancedMesh (1 draw call per jenis).
- LOD: model lengkap di dekat pemain, di atas sekitar 300 m disembunyikan (terlalu kecil untuk terlihat).
- Kolisi kotak kecil, supaya tidak bisa ditembus.
- Biaya: rendah.

## 11d. Stasiun pesawat angkasa (spaceport)

Prinsip fisika: pesawat harus berlabuh di sumbu, bukan di tepi silinder. Tepi silinder bergerak 99,05 m/s (ω x R = 0,09905 x 1.000 m), sedangkan sumbu nyaris diam. Itu sebabnya dermaga ada di end cap A, di luar kaca, pada poros yang sama dengan hub nol-g.

| Bagian | Rencana |
| --- | --- |
| Dermaga luar (despun) | Cincin dermaga di ujung batang dermaga yang tidak ikut berputar, dengan 4 port sandar, lampu penuntun, dan lengan penjepit. Terlihat dari hub dan dari kamera luar |
| Pesawat | 2-3 desain orisinal: shuttle antar-orbit, kapal kargo, kapal tunda kecil |
| Lalu lintas | Pesawat datang dari angkasa, menyesuaikan rotasi, sandar, bongkar muat, lalu berangkat. Siklus beberapa menit, lampu navigasi berkedip |
| Terminal dalam | Gedung terminal kaca di plaza spaceport (za 150-250), dekat lobi lift. Ada papan jadwal keberangkatan, ruang tunggu, dan jendela ke dermaga |
| Hub nol-g | Pintu dermaga di hub dibuat bisa dilewati: dari hub melayang ke ruang sandar dan melihat pesawat dari dekat |
| Shortcut | Tombol 7: terminal spaceport. Kamera luar diberi fokus tambahan: dermaga |

- Biaya: sedang. Pesawat berupa beberapa mesh detail dengan LOD (jauh = model sederhana).
- Butuh keputusan desain: bentuk pesawat (lihat pertanyaan di bawah).

## Urutan dan uji

| Urutan | Sub-tahap | Yang kamu uji |
| --- | --- | --- |
| 1 | 11a awan dinamis + bayangan | Gerak awan, bayangan ikut bergerak, FPS |
| 2 | 11b sunrays | Berkas saat pagi dan senja, FPS di preset Ultra |
| 3 | 11c kursi + tempat sampah | Kepadatan di kota dan taman |
| 4 | 11d spaceport | Dermaga, pesawat sandar, terminal |

## Keputusan yang perlu kamu pilih

1. Kepadatan awan default: cerah, berawan sedang, atau mendung?
2. Gaya pesawat: industri realistis (NASA/SpaceX), futuristik ramping, atau campuran?
3. Pesawat hanya dilihat dari luar, atau bisa dimasuki seperti trem?

## Catatan

- Angka kepadatan objek dan jumlah sampel sunrays masih rencana awal. Akan disesuaikan setelah uji FPS di GTX 1060 dan M1.
- Desain pesawat dibuat orisinal. Pesawat dari film (Endurance, Ranger) tidak akan ditiru.
