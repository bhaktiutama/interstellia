# Rencana UI seragam: Copper, Gargantua, Millar

Per 26 Oktober 2026. Status: inventaris selesai, rencana menunggu keputusan Bhakti (bagian D). Belum ada kode yang diubah.

## Ringkasan

- Tiap experience punya CSS UI sendiri (Copper baris 10-222, Gargantua 7-143, Millar 10-118). Hanya kartu mulai Copper dan Millar yang sudah sama persis (rencana `rencana-menu-mulai.md` U1). Sisanya beda token warna, material panel, font, radius, letak kotak petunjuk tombol, toast, nama kelas tombol H, dan perilaku panel.
- Saat muat ada tiga perilaku berbeda: Copper menampilkan HUD kiri dan panel kanan di belakang kartu mulai yang tembus, Millar tidak menampilkan apa pun selain kartu (kelas `body.pre`), Gargantua menutup layar dengan layar hitam pejal tanpa kartu mulai lalu langsung jalan.
- Usulan: satu berkas bersama `shared/ui.css` (token + komponen) dan `shared/ui.js` kecil (toast, petunjuk tombol, sembunyikan UI), dipasang bertahap UI1-UI8, satu experience per langkah.

## A. Inventaris token desain

Sumber: blok `<style>` tiap `experiences/<id>/index.html`.

| Token | Copper | Gargantua | Millar |
| --- | --- | --- | --- |
| Teks (ink) | `#d9dde3` | `#cfd3da` | `#dfe3ea` |
| Teks redup (muted) | `#8b929c` | `#7d838f` | `#8a919c` |
| Aksen | `#e8b765` | `#f0a45a` (tab aktif tetap memakai latar `rgba(232,183,101,0.18)` = aksen Copper: campur) | `#e8b765` |
| Peringatan | `#e7806b` | tidak ada | `#ff9d7a` |
| Latar panel | `rgba(12,14,18,0.72)` | `rgba(10,11,15,0.62)` | `rgba(12,14,18,0.58)` |
| Garis tepi | `rgba(255,255,255,0.10)` | `rgba(255,255,255,0.09)` | `rgba(255,255,255,0.12)` |
| Blur panel | tidak ada (solid tembus) | `blur(14px) saturate(120%)` + bayangan `0 10px 40px` | `blur(10px)` |
| Font dasar | mono 12px / 1,45 | mono 11px / 1,4 | mono 12px / 1,45 |
| Font kartu | kartu mulai system-ui 13px; bantuan, peta, plakat mono | tidak ada kartu mulai; bantuan dan kartu akhir mono | kartu mulai system-ui 13px; hasil misi system-ui 14px; bantuan mono |
| Radius | HUD, panel, menu 8; kartu 10; tombol 6 | panel 10; kartu 10; tombol 6 | `.panel` 10 tetapi HUD 8; bantuan dan hasil 12; tombol 6 |
| Judul kotak | aksen, huruf besar, 10,5px, spasi .08em | warna teks, huruf besar, 10px, spasi .14em | HUD: aksen 10,5px .08em; panel: muted, huruf biasa, .06em |
| Judul seksi panel | `.ptitle` aksen 11px .06em | `.sec` muted 9,5px .16em dengan garis atas | tidak ada |
| Slider | bawaan peramban + `accent-color` | jalur tipis 2px + kenop 10px (khusus) | bawaan + `accent-color` |
| Tombol panel | pad 6px, `<kbd>` di kiri | pad 4px 6px, `<kbd>` di kiri | pad 5px 8px, `<kbd>` di kanan (flex space-between) |

## B. Inventaris komponen

| Komponen | Copper | Gargantua | Millar |
| --- | --- | --- | --- |
| Tombol menu | `#menuBtn` kiri atas 12px, latar panel | `#menuLink` kiri atas 12px, z-index 20 | `#back` kiri atas 12px, kelas `.panel` (dengan blur) |
| HUD kiri | `#hud` DOM grid, klik judul = ringkas / lengkap | `#dash` digambar di kanvas (`drawDash()`), gaya mirip Copper, tidak digambar di layar < 640px | `#hud` DOM `.panel` + `h1` |
| Panel kontrol | `#lab` kanan atas 12px, lebar 300, terbuka saat muat (desktop), kepala diklik / ` = ciutkan | `#ui` kanan atas 16px, lebar 272, terbuka, diciutkan saat misi | `#lab` kanan atas 60px, lebar 290, tersembunyi (`hidden`), tombol Tutup |
| Tab panel | `#labTabs` | `#uiTabs` | `#labTabs` (gaya disalin) |
| Panel ponsel (< 640px) | lembar bawah, tab di bawah | lebar penuh di bawah tombol menu, tab di bawah | tidak ada aturan khusus |
| Petunjuk tombol gerak | `#hint` tengah bawah 24px, kotak panel satu baris (`nowrap` + elipsis), muncul 6 s setelah Mulai lalu pudar | `#hint` teks polos tanpa kotak, kanan bawah, 10px, opasitas 0,35, selalu tampil; plus `#caption` kiri bawah; petunjuk misi digambar di kanvas tengah bawah | `#keys` kotak `.panel` kanan bawah, maks 350px, 3 baris terbungkus, selalu tampil, hilang di < 640px |
| Notifikasi | `#toast` tengah atas 12px, kotak panel bergaris | `#toast` 30% dari atas, tanpa garis, latar 0,7 | `#msg` 30% dari atas, kotak panel bergaris, 14px |
| Bantuan | kartu solid `#14171c`, layar gelap 0,66, bertab 7, tautan menu di kepala | kartu kaca 0,62 blur, layar 0,45, bertab (`HELP`) | kartu kaca 0,86 blur, layar 0,35, satu tabel tanpa tab |
| Kartu mulai | `#start` (U1) bahasa, planet, wahana, kualitas | tidak ada | `#start` (U1) bahasa, kualitas, suasana, wahana, mode, tingkat |
| Layar muat | bilah di kartu mulai, persen | layar hitam pejal `#boot` z-index 40, judul GARGANTUA, bilah | bilah di kartu mulai, persen (`mBoot`) |
| Kartu hasil | tidak ada | `#mend` kaca, kanan, bisa diseret dan ditutup | `#result` tengah, kaca 0,86, system-ui |
| Kelas tombol H | `.hidden-ui` | `#ui.hidden` + `body.hideUI` + `.overlay-text.hidden` | `body.hide` |
| Kotak galat `#err` | latar `rgba(30,8,6,0.95)` | `rgba(20,0,0,0.92)` | `rgba(30,0,0,0.92)`, tanpa garis |

## C. Inventaris perilaku

| Perilaku | Copper | Gargantua | Millar |
| --- | --- | --- | --- |
| Saat muat terlihat | kartu mulai tembus + HUD kiri + panel kanan terbuka di belakangnya; tombol menu disembunyikan (`:has(#start)`) | hanya layar hitam muat | hanya kartu mulai (`body.pre` menyembunyikan HUD, tombol menu, petunjuk) |
| Setelah muat | tunggu Mulai, lalu kunci kursor + petunjuk 6 s + tawaran tur | langsung jalan, tanpa pilihan | tunggu Mulai, sinematik bila dipilih |
| Panel awal | terbuka (desktop), tertutup (ponsel) | terbuka | tersembunyi |
| ` (backtick) | ciutkan / buka | buka / ciutkan | tampil / sembunyi + lepas kursor |
| H | sembunyikan HUD, petunjuk, toast, panel, tombol menu | sembunyikan panel, keterangan, petunjuk, kotak kanvas, tombol menu | sembunyikan semua `.panel` |
| Mode foto F | `body.photo` menyembunyikan HUD, panel, tombol | `body.photo` opasitas 0 | `body.photo .panel` opasitas 0 |
| Tur / sinematik | `body.tour` sembunyikan UI | tidak ada | `body.cine` pita hitam + UI opasitas 0 |
| Bahasa | kartu mulai + tab Lainnya | panel (sumber teks English) | kartu mulai + tab Lainnya |

Sudah seragam dan tidak perlu disentuh: overlay kamera rangefinder (`shared/camera.js`), menu VR (`shared/vr.js`), lagu tema (`shared/music.js`), daftar tombol (`tombol.md`).

## D. Keputusan yang perlu Bhakti pilih

| No | Pertanyaan | Pilihan | Saran |
| --- | --- | --- | --- |
| D1 | Material kotak mengambang (HUD, panel, menu, toast, petunjuk) | a) kaca tembus + blur; b) tembus tanpa blur (seperti Copper sekarang); c) solid | a) `rgba(12,14,18,0.72)` + `blur(12px)`, garis 0,10, radius 8. Preset Hemat mematikan blur (kelas `ui-lite`) karena `backdrop-filter` di atas kanvas WebGL menambah biaya komposit tiap frame (belum diukur di M1) |
| D2 | Material kartu (mulai, bantuan, hasil, kartu akhir) | sama dengan D1 atau lebih pekat | kartu U1 yang sudah ada: `rgba(12,14,18,0.82)` + blur 12, layar belakang 0,45, radius 10 |
| D3 | Font | a) mono untuk semua; b) mono untuk instrumen (HUD, panel, petunjuk, toast), system-ui untuk kartu bacaan (mulai, bantuan, hasil) | b), sudah dipakai kartu mulai; bantuan ikut system-ui karena berisi kalimat panjang |
| D4 | Aksen | a) `#e8b765` semua; b) tiap experience punya aksen sendiri | a). Gargantua `#f0a45a` diganti, termasuk warna di kanvas `drawDash()` |
| D5 | Saat muat | a) hanya kartu mulai (pola Millar); b) kartu + UI di belakang (pola Copper) | a) semua UI permainan muncul setelah Mulai. Gargantua mendapat kartu mulai (U5 lama): bahasa, kualitas, Mulai |
| D6 | Petunjuk tombol gerak | a) satu baris tengah bawah, muncul sementara (Copper); b) kotak kanan bawah tetap (Millar); c) teks polos (Gargantua) | a) dengan perbaikan: kotak tengah bawah, maks 2 baris terbungkus (lebar `min(640px, 100vw - 32px)`), tampil 8 s setelah Mulai dan saat ganti konteks (naik wahana, mulai misi), daftar lengkap di bantuan (?) |
| D7 | Panel kontrol awal | a) terbuka; b) diciutkan (kepala saja); c) tersembunyi | b) kepala panel terlihat di kanan atas, ` atau klik kepala membuka; status terakhir diingat per experience |
| D8 | Bantuan bertab di Millar | ya / tidak | ya, tab Dasar, Terbang, Misi, Kamera, Grafik dan suara |
| D9 | HUD Gargantua di kanvas | a) tetap kanvas, warna dan font dari token CSS; b) pindah ke DOM | a), karena kotak relai dan corong juga di kanvas; hanya warna, font, radius disamakan |

## E. Langkah

| Langkah | Isi | File | Effort | Model | Thinking |
| --- | --- | --- | --- | --- | --- |
| UI1 | `shared/ui.css`: token (`--ui-ink`, `--ui-muted`, `--ui-accent`, `--ui-warn`, `--ui-panel`, `--ui-card`, `--ui-line`, `--ui-blur`, `--ui-r`, `--ui-font`, `--ui-font-read`) + komponen berkelas umum: `.ui-box`, `.ui-menu`, `.ui-hud`, `.ui-panel` (kepala, tab, seksi, baris, slider, tombol + kbd), `.ui-card` + `.ui-overlay`, `.ui-help` (tab, tabel), `.ui-toast`, `.ui-keys`, kartu mulai U1 dipindah ke sini, aturan `body.ui-pre`, `body.ui-hide`, `body.photo`, lembar bawah ponsel < 640px, `ui-lite` | `shared/ui.css` (baru) | Medium | Sonnet 5.5 | medium |
| UI2 | `shared/ui.js` (`window.UIKIT`, skrip biasa seperti modul shared lain): `toast(html, s)`, `keys(text, s)` (petunjuk sementara), `hide(on)` (tombol H satu kelas), `panel(el, key)` (ciut / buka + localStorage), `tokens()` (baca warna CSS untuk kanvas) | `shared/ui.js` (baru) | Medium | Sonnet 5.5 | medium |
| UI3 | Copper memakai UI1-UI2: HTML diberi kelas umum, CSS lokal yang ganda dihapus, `.hidden-ui` -> `ui-hide`, `body.ui-pre` saat kartu mulai, bantuan font baca; peta, plakat, foto, kartu tur memakai `.ui-card` / `.ui-box` | `experiences/cooper-station/index.html` | Medium | Sonnet 5.5 | medium |
| UI4 | Millar memakai UI1-UI2: `#back` / `#hud` / `#lab` / `#keys` / `#msg` / `#help` / `#result`, `body.pre` -> `ui-pre`, `body.hide` -> `ui-hide`, panel dari tersembunyi menjadi ciut, bantuan bertab (D8), petunjuk sementara | `experiences/millar/index.html` | Medium | Sonnet 5.5 | medium |
| UI5 | Gargantua memakai UI1-UI2: `#menuLink` / `#ui` / `#help` / `#toast` / `#hint` / `#caption`, kelas H tunggal, slider dari token, `drawDash()` / `boxBtn` / `#mobView` / `#mend` membaca `UIKIT.tokens()` | `experiences/gargantua/index.html` | Medium | Sonnet 5.5 | medium |
| UI6 | Gargantua kartu mulai (D5): `#boot` hitam diganti `#start` U1 (bahasa, kualitas, Mulai), `main()` selesai muat lalu menunggu Mulai, audio dibuat saat klik Mulai | `experiences/gargantua/index.html` | Medium | Sonnet 5.5 | medium |
| UI7 | Uji `tools/uji_ui.py` (Playwright, `THREE_LOCAL`, `CHROMIUM` opsional): gaya terhitung sama di ketiga experience (font, latar, garis, radius tiap komponen), selama kartu mulai tidak ada HUD / panel / tombol menu terlihat, petunjuk di tengah bawah, toast di tengah atas, H menyembunyikan semua, tanpa gulir mendatar di 375px, tanpa error | `tools/uji_ui.py` (baru) | Medium | Sonnet 5.5 | medium |
| UI8 | Dokumen: CLAUDE.md (baris `shared/ui.*`, kelas baru), `tombol.md` (perilaku H, `, ?), `rencana-menu-mulai.md` (U5 selesai lewat UI6) | dokumen | Low | Haiku 4.5 | low |

Urutan: UI1 dan UI2 dulu, lalu satu experience per langkah (UI3, UI4, UI5) agar tiap langkah bisa diuji Bhakti sendiri. UI6 setelah UI5.

## F. Risiko dan batasan

- "Pertahankan yang ada": pemindahan CSS bisa menggeser elemen yang dipakai uji lama (`tools/uji_*.py` mencari id, bukan kelas). Id dipertahankan; hanya kelas dan CSS yang berubah.
- `backdrop-filter` di atas kanvas WebGL penuh layar: biaya komposit belum diukur di GTX 1060 dan M1. Karena itu ada `ui-lite` (D1). Sandbox SwiftShader tidak memberi angka FPS yang bermakna.
- Gargantua teks sumbernya English (`txt()`), Copper dan Millar Indonesia (`t()`). Rencana ini tidak menyamakan sistem kamus, hanya tampilan.
- Di luar cakupan: halaman detail (`detail.html`), menu utama `index.html`, layar MFD dan HUD kokpit di kanvas, overlay kamera (sudah bersama).
- Copper "satu file" tetap berlaku untuk kode experience; CSS bersama dimuat lewat `<link>` relatif seperti skrip `shared/` lain dan jalan dari file://.
