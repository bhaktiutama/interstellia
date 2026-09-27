# CLAUDE.md - Aplikasi multi-experience (nama kerja: Lazarus)

Kumpulan experience 3D bertema perjalanan antarbintang, dipanggil dari menu utama (`index.html`). Proyek penggemar, tidak berafiliasi dengan studio film mana pun. Pemilik proyek: Bhakti; diuji di PC GTX 1060 dan MacBook M1.

## Struktur repo

| Path | Isi |
| --- | --- |
| `index.html` | Menu utama. Nama aplikasi dan daftar experience ada di konstanta `APP` dan `EXPERIENCES` |
| `experiences/<id>/index.html` | Satu experience = satu halaman HTML mandiri, plus `preview.jpg` (16:9) untuk kartu menu |
| `experiences/cooper-station/` | Silinder O'Neill di orbit Saturnus (paling lengkap, lihat bagian di bawah) |
| `experiences/gargantua/` | Lubang hitam berputar (WebGL mandiri) |
| `docs/app/` | Dokumen tingkat aplikasi (penamaan, arsitektur) |
| `docs/<id>/` | Konsep dan rencana per experience |
| `tools/qc_load.py` | Cek halaman termuat tanpa error |
| `tools/uji_spaceport.py` | Uji Cooper Station 12a: pintu terminal, gerbang B1 ke kokpit, sandar otomatis |
| `tools/uji_lalu_lintas.py` | Uji Cooper Station 12b-1: peron trem, lalu lintas 30 menit tanpa tabrakan |
| `tools/uji_pohon.py` | Uji Cooper Station 12b-2: jenis pohon, suasana daun, daun jatuh per preset |
| `shared/` | (belum ada) kode bersama akan dipindahkan ke sini bertahap |

## Aturan aplikasi

- Menambah experience: buat `experiences/<id>/index.html` + `preview.jpg`, lalu tambahkan entri di `EXPERIENCES` (ready: true). Tiap experience wajib punya tautan kembali ke `../../index.html`.
- Tiap experience tetap halaman terpisah (memori GPU bersih saat pindah). Kode bersama dipindah ke `shared/` bertahap, jangan membongkar Cooper Station sekaligus.
- Rencana experience berikutnya: Planet Ombak (dunia air, dilatasi waktu), Penerbangan Kestrel (shuttle KS-07 dari Cooper Station). Usulan nama: `docs/app/penamaan.md`.
- Jangan memakai judul film, logo, huruf judul, musik, cuplikan, atau desain kendaraan film.

# Experience: Cooper Station

Simulasi silinder O'Neill yang mengorbit Saturnus. Satu file HTML (`experiences/cooper-station/index.html`), three.js, bisa dijelajahi berjalan kaki. Dibangun bertahap.

## Aturan kerja

- Bahasa: Indonesia untuk teks UI, komentar kode, dokumen, dan balasan.
- Satu file: semua kode Cooper Station ada di `experiences/cooper-station/index.html` (CSS + JS modul). Tidak ada build step, tidak ada addon three.js.
- three.js 0.186.1 dari importmap `https://cdn.jsdelivr.net/npm/three@0.186.1/build/three.module.js`.
- "Pertahankan yang ada": fitur lama tidak boleh hilang atau berubah tanpa diminta.
- Uji: pemilik proyek yang menguji visual dan FPS. Cukup cek halaman termuat tanpa error (lihat `tools/`). Jangan menghabiskan waktu dengan screenshot berulang.
- Hak cipta: jangan meniru desain kendaraan/musik film (Endurance, Ranger, musik Interstellar). Desain pesawat orisinal (shuttle "Kestrel" KS-07).
- Dokumen rencana ditulis sebagai file .md di `docs/<id>/` (pemilik membaca di ponsel).
- Format laporan: ringkasan dulu, tabel, tanpa em dash.

## Angka dasar

| Item | Nilai |
| --- | --- |
| Radius R | 1.000 m |
| Panjang L | 8.000 m (HALF_L 4.000) |
| Putaran | omega 0,09905 rad/s, periode 63,4 s, 1 g di tanah, kecepatan tepi 99,05 m/s |
| Koordinat | sumbu = world Z; za = z + 4.000 (jarak dari end cap A); s = theta x R (busur keliling) |
| Kerangka | dalam stasiun = kerangka berputar; kamera luar (V) dan pesawat = kerangka inersia (scene.rotation.z = omega t) |
| Dua scene | farScene (1 unit = 1.000 km: Saturnus, bintang, Matahari) + scene utama |

## Peta kode (cari dengan nama)

| Area | Nama penting |
| --- | --- |
| Konfigurasi | `CONFIG`, `HALF_L`, `R`, `CIRC`, `ART` (arteri keliling tiap 241,7 m), `ART_Z` (250 m), `ROAD`, `CITY`, `PARKZ`, `FARMS`, `RINGS_Z`, `nearRing()` |
| Cahaya | `LIGHT_GLSL` / `stationLight()`, `LIGHT.uniforms` (uL_Sunline, uL_SunDir, uL_CapI), `patchLit()` untuk MeshBasicMaterial, `updateLighting()` |
| Bayangan | `SHADOW`, pass layer 1; alpha caster layer 2 (`ALPHA_CASTERS`) |
| Tanah | heightmap `TER` (half-float, sama CPU/GPU), `groundH(s, za)`, `groundMat` (uLand, uFieldTex, uCloudTex, uShadeTex, lampPool) |
| Vegetasi | `VEG_COMMON`, `TREES` (LOD + impostor, 16 template: oak, elm, poplar, maple, birch, pine, willow, bunga), `TREE_KINDS`, `GRASS`, `CORN` |
| Suasana daun (12b-2) | `LEAF` (mode Hijau/Campur/Gugur), `leafColorFor()`, `applyLeafMode()`, atribut `aLeafC` + `LEAF_RECOLOR`, `WIND` + `updateWind()` (uniform `uWind`), `FALL` (daun jatuh GPU) + `updateFallSources()`, `uLitterTex` (serakan daun) |
| Bangunan | `building(type, s, za, w, d, h, color, elev, collider, style, front)`, gaya 0-11, `BUILD_U.uNight`, varying flat (perbaikan GTX 1060) |
| Kolisi | `COL`, `addCollider(s, za, hs, hz)` (AABB di bidang s-za), `LATE_COLLIDERS` |
| Awan/cuaca (11a) | `WEATHER` (mode auto/cerah/berawan/mendung, cover, ov), `CLOUD`, `updateClouds(dt)`, `cycleWeather()` (N) |
| Sunrays (11b) | `RAYS`, `rayMat` (ray-march setengah resolusi + berkas layar), dipakai di `postEnd()` |
| Perabot kota (11c) | `FURN` (bench, bin, hydrant, planter, signal, cabinet, mailbox, zebra), LOD per radius, `updateFurniture()` |
| Spaceport (11d) | `PORT`, `DOCK` (grup despun), `SHIPS` (player, ai, cargo, tug), `COCKPIT`, `TERM` (terminal; posisi didefinisikan di bagian plaza), `portBoard()`, `stepPort()`, `updateFlightCamera()`, `portKey()`, `portMouse()` |
| Spaceport rapi (12a) | `TERM.gate`, `portStartTrip()`, `PORT.trip` (perjalanan otomatis 5x dari gerbang B1), `DGUIDE` + `updateDockGuide()` (kotak target, garis arah), `dockData()`, `drawCockpitScreen()`, `portClank()`, `AUDIO.shipBus` (eng, engTone, rcs, cab, cabHum), `PORT.thr` / `PORT.rcs` / `PORT.turn` |
| Post | `POST`, `postBegin()`, `postEnd()`: HDR, SSAO, bloom 6 tingkat, ACES, FXAA |
| Audio | `AUDIO`, `startAudio()`, `updateAudio(dt)` (semua disintesis) |
| Preset | `PRESETS` (Ultra/Tinggi/Sedang/Rendah/Hemat; Hemat untuk MacBook M1), `applyPreset(i)`, turun otomatis bila FPS < 30 selama 4 s, tersimpan di localStorage, `?preset=hemat` |
| Lalu lintas | `TRAFFIC` (gambar di GPU, posisi dari simulasi CPU `stepTraffic()` model IDM, atribut `aSim`), `SIG` + `sigState(k, m, axis, t)` (lampu lalu lintas), `XING` + `updateCrossings()` + `XVIS` (perlintasan trem, palang, bel), `LAMP` |
| Trem | `TRAM`, `TRAM_CAR`, `TRAM_SEATS`, `tram` |
| Lift/hub | `LIFT`, `HUB`, `CABIN`, `enterLift()`, `stepFloat()` |
| Lokasi | `SPOTS` + `teleport(key)`: cooper, hill, corn, wheat, skyway, baseball, spaceport |
| Uji | `window.__station` mengekspor objek penting untuk skrip uji |

## Status pemain (`player.state`)

`ground`, `air`, `lift`, `float` (hub nol-g), `tram`, `pod` (kapsul terowongan ke dermaga), `ship` (di shuttle; `ext.active` dan `ext.flight` true). `PORT.trip` true = sedang perjalanan otomatis dari gerbang B1 (lift dan kapsul 5x, E = langsung ke kokpit).

## Tombol

W A S D, Shift, Space, B, G, L, T, E, M, V, [ ], Z (kecepatan waktu), N (cuaca), O, X, R, H, 1-8 (lokasi; 8 = kokpit shuttle), K, Q, P, U, J, / atau F1. Di pesawat: W/S, A/D, R/F, Z/C, mouse, Shift, X, V, E, L.

## Riwayat tahap

| Tahap | Isi |
| --- | --- |
| 1-3 | Silinder, fisika berjalan dan bola di kerangka berputar, Saturnus dan orbit |
| 4-4d | Kota, sungai, ladang, cincin struktur, lambung tebal, utilitas luar |
| 5 | Awan, sunline, end cap |
| 6-6b | Realisme: bukit, rumput 3D, jagung, pohon prosedural, seluruh stasiun |
| 7-8 | Bangunan detail kota, rumah Cooper |
| 9 | Post-processing, audio |
| 10-10f | Trem berinterior, mobil, lampu jalan, preset, kamera luar, lift dan hub, baseball |
| 11a-11d | Cuaca dinamis, sunrays, perabot kota, spaceport dan shuttle |
| 12a | Gerbang B1 terminal ke kokpit, pintu terminal bisa dilewati (hanggar lama di dalam terminal dihapus), suara shuttle, panduan sandar |
| 12b-1 | Halte trem pindah dari simpang, lampu lalu lintas merah-kuning-hijau, mobil antre (simulasi CPU), perlintasan trem berpalang dan bel, preset Hemat |
| 12b-2 | 8 jenis pohon, suasana daun Hijau/Campur/Gugur, daun jatuh tertiup angin, serakan daun, angin global |

Rencana berikutnya: `docs/cooper-station/rencana-tahap-12b-cooper-station.md` (12b-2 sampai 12b-5), lalu `rencana-tahap-12-cooper-station.md` (12c, 12d).
