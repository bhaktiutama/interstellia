# CLAUDE.md - Aplikasi multi-experience (nama: Interstellia)

Kumpulan experience 3D bertema perjalanan antarbintang, dipanggil dari menu utama (`index.html`). Proyek penggemar, tidak berafiliasi dengan studio film mana pun. Pemilik proyek: Bhakti; diuji di PC GTX 1060 dan MacBook M1.

## Struktur repo

| Path | Isi |
| --- | --- |
| `index.html` | Menu utama. Nama aplikasi dan daftar experience ada di konstanta `APP` dan `EXPERIENCES` |
| `experiences/<id>/index.html` | Satu experience = satu halaman HTML mandiri, plus `preview.jpg` (16:9) untuk kartu menu |
| `experiences/cooper-station/` | Silinder O'Neill di orbit Saturnus (paling lengkap, lihat bagian di bawah) |
| `experiences/gargantua/` | Lubang hitam berputar (WebGL mandiri) |
| `experiences/millar/` | Millar's World versi realistis (R1, R1b, R2, R3, R4): R4 gelombang raksasa `US` (profil rapat) / `ZS` / `ARC` (panjang busur, koordinat pola dinding), `wavePosD()` (tonjolan air meluncur), `SPRAY` (3 semburan + 2 kabut), arus air surut `currentAt()` (GLSL dan JS, `CONFIG.current`, peta aliran dua fase lewat `surfS()`), tersapu `SWEEP` (`CONFIG.sweep`, bawah air `uUnder` di `M_COMP`), keadaan laut `seaStateTarget()` / `U.uChopK` (ombak angin 0,6x jauh -> 1,5x dekat gelombang raksasa, `CONFIG.seaState`), R3 pemain di air: riak `RIP` / `M_RIP` / `updateRipple()` / `ripSource()` (grid ikut pemain, kanal buih jejak), cipratan `SPL` / `spawnSplash()` / `stepSplash()`, langkah `footstep()`, gerak kepala `BOB` / `headBob()` (tombol B), inersia air `CONFIG.walk`, kedalaman dari FFT `probeOcean()` / `waterHere()`, ombak FFT `OCEAN` / `makeOcean()` / `updateOcean()` (spektrum `oceanSpectrum()` di CPU, `M_SPEC` + IFFT Stockham `M_BFLY` + `M_ASM` + buih `M_FOAM` di GPU, kaskade `fftN` / `fftL` per preset, `FFT_GLSL` di `seaMat()`, kaustik `CAUST`; Hemat = Gerstner), `PRESETS` + `applyPreset()` (5 preset seperti Cooper, `?preset=`, localStorage `millar.preset`), `MOODS` / `updateMood()` (Otomatis/Mendung/Senja, tombol N), langit `SKY_FS` ke cubemap `SKYCUBE` (satu sisi per frame, awan volumetrik `STEPS` atau 2D `LAYERS`; cerah = awan pecah merata, bukan lubang), Gargantua lensa gravitasi `GARG_FS` ke cubemap `GCUBE` (porting dari experience Gargantua; `LENS` jarak pengamat dari radius bayangan, preset `g*`, `updateGCube()`), laut `seaMat()` dekat/jauh + ombak angin `CHOP` / `applyChop()` (Gerstner), gelombang raksasa `waveMat` + `spray` / `mist`, post `POST` / `postRender()` (bloom, ACES, FXAA, grain), `GPUT`. Angka di `CONFIG`; rumus gelombang, dasar laut, dan ombak ada di GLSL (`COMMON`) dan kembaran JS (ubah bersama); tidak ada daratan (dasar laut selalu terendam). `simStep()` / `stepPlayer()` untuk uji, `window.__millar`, `window.__millarReady`. `prototipe.html` = prototipe low poly lama (tanpa kartu menu) |
| `docs/app/` | Dokumen tingkat aplikasi (penamaan, arsitektur) |
| `docs/<id>/` | Konsep dan rencana per experience |
| `tools/qc_load.py` | Cek halaman termuat tanpa error |
| `tools/uji_millar.py` | Uji Millar's World R1 + R1b + R2 + R3 + R4: urutan tersapu, kerapatan muka gelombang, arus dan seretan, gelombang dekat tanpa nilai tidak valid, keadaan laut, riak, cipratan, langkah, inersia, kamus English, lensa Gargantua (radius bayangan, busur terbelokkan), ombak FFT (IFFT GPU = DFT CPU, tinggi signifikan, Hemat Gerstner), tanpa daratan, 1,3 g dan lompat 77%, gelombang 125 m/s, jam dilatasi, tersapu, 5 preset tanpa nilai tidak valid atau titik menyala (`THREE_LOCAL`, `CHROMIUM` opsional untuk sandbox) |
| `tools/uji_spaceport.py` | Uji Copper Corn Station 12a: pintu terminal, gerbang B1 ke kokpit, sandar otomatis |
| `tools/uji_lalu_lintas.py` | Uji Copper Corn Station 12b-1: peron trem, lalu lintas 30 menit tanpa tabrakan |
| `tools/uji_pohon.py` | Uji Copper Corn Station 12b-2: jenis pohon, suasana daun, daun jatuh per preset |
| `tools/uji_pejalan_kaki.py` | Uji Copper Corn Station 12b-3: pejalan kaki menyeberang hanya saat lampu jalan, biaya CPU, preset Hemat |
| `tools/uji_burung.py` | Uji Copper Corn Station 12b-4: kawanan burung, merpati terbang saat didekati, siklus hari |
| `tools/uji_suasana.py` | Uji Copper Corn Station 12b-5: kafe, lampu untaian, bendera, suara kota, tidak ada normal nol (NaN) |
| `tools/uji_hujan.py` | Uji Copper Corn Station 12c: angka fisika hujan dan air mancur Coriolis, hujan, tanah basah, angin |
| `tools/uji_rel_trem.py` | Uji Copper Corn Station 13a: koridor rel trem bebas tiang, pohon, collider |
| `tools/uji_skyway.py` | Uji Copper Corn Station 13b-13c: mobil melintasi jembatan Skyway, akuaduk, tombol 5 di atas kaca |
| `tools/uji_peta.py` | Uji Copper Corn Station 13d: peta besar, penanda, zoom, klik = pindah, legenda dua bahasa |
| `tools/uji_hutan.py` | Uji Copper Corn Station 14a: hutan lebat (jumlah, tinggi, jalan setapak, tombol 0, pakis per preset, biaya) |
| `tools/uji_rumput_bukit.py` | Uji Copper Corn Station 14b: rumput tinggi bukit aktif di bukit, mati di kota, radius per preset |
| `tools/uji_interior.py` | Uji Copper Corn Station 14c: ruangan di balik jendela per preset, tanpa nilai tidak valid siang dan malam |
| `tools/uji_trem_malam.py` | Uji Copper Corn Station 15a: lampu kabin dan strip plafon trem malam, kolam cahaya tanah |
| `tools/uji_boulevard.py` | Uji Copper Corn Station 15b: mobil boulevard samping rel trem, 30 menit tanpa tabrakan trem dan konflik simpang |
| `tools/uji_trotoar.py` | Uji Copper Corn Station 15c: rute pejalan kaki di trotoar dan jalan setapak taman, tidak di gedung atau pohon |
| `tools/uji_permukiman.py` | Uji Copper Corn Station 15d: jumlah rumah, tanah kosong permukiman, rumah tidak bertumpuk atau di trotoar |
| `tools/uji_distrik.py` | Uji Copper Corn Station 16: distrik (sel kota, nama, halte, notifikasi), fasilitas, peta |
| `tools/uji_bahasa.py` | Uji M3: kamus English lengkap (teks statis dan `t()`), label berganti bahasa tanpa muat ulang |
| `tools/uji_gerhana.py` | Uji Copper Corn Station 17a: Matahari 25 derajat dari sumbu di bidang orbit, lompat ke gerhana, lama gerhana dan penumbra, sinar padam, cahaya tepi Saturnus |
| `tools/uji_pantulan.py` | Uji Copper Corn Station 17b + 17d: pantulan daratan seberang (arah atas hijau, ke end cap berkabut, sunline), tanpa nilai tidak valid, ambient warna daratan, material berkilap |
| `tools/uji_cahaya_lanjut.py` | Uji Copper Corn Station 17c + 17e + 17f + 18a + 18b-2: adaptasi mata (siang, terminal, malam), lampu malam menerangi objek, bayangan sunline (tajam keliling, lembut searah sumbu, dinding gedung jauh tidak gelap, bayangan tidak bergeser saat pemain pindah), awan terpantul, kompleks utilitas padat tanpa tumpang tindih |
| `tools/uji_menara.py` | Uji Copper Corn Station 18b: dek pandang menara (teras 175 m), E naik-turun langsung, pagar dek, jatuhkan bola dari dek vs hitungan analitik dan vs di tanah, pintu menara gereja, atap pasar menempel, kaca bening rumah Cooper |
| `tools/uji_ladang_foto_tur.py` | Uji Copper Corn Station 12d: siklus tanam, mesin ladang, mode foto (kembali normal saat keluar), tur sinematik |
| `tools/uji_gerak.py` | Uji Copper Corn Station 19a-19c: gerak kepala jalan/lari/mendarat, FOV, motor (model aset termuat, kecepatan normal dan sport 150 km/h, getaran, belok miring, rem, berat terasa, tabrakan, air, turun, parkir), lampu depan malam |
| `tools/uji_air_mancur.py` | Uji Copper Corn Station 21a-1: tidak ada orang, pohon, atau merpati di kolam air mancur; pengunjung datang dan pergi, kelompok mengobrol bubar dan berkumpul lagi (30 menit), jalur tidak menembus pohon |
| `tools/uji_kaca_cooper.py` | Uji Copper Corn Station 21b: kaca jendela rumah Cooper bening dari dalam (alpha kecil, paling tinggi 0,35 walau miring), pantulan daratan dari luar tetap, tanpa nilai tidak valid |
| `tools/uji_gedung_malam.py` | Uji Copper Corn Station 21c: menara kaca malam dari 800 m tidak terang rata (sebaran per blok dan lantai), faktor jam kantor / hunian, siang tidak berubah, tanpa nilai tidak valid |
| `tools/siapkan_motor.py` | Olah model motor GLB sumber (Sketchfab, CC BY 4.0) menjadi `experiences/cooper-station/assets/motor.data.js` (butuh numpy, pillow) |
| `experiences/cooper-station/assets/` | Aset data (bukan kode): `motor.data.js` (model motor, base64) + `KREDIT.md` (sumber dan lisensi) |
| `shared/` | (belum ada) kode bersama akan dipindahkan ke sini bertahap |

## Aturan aplikasi

- Menambah experience: buat `experiences/<id>/index.html` + `preview.jpg`, lalu tambahkan entri di `EXPERIENCES` (ready: true). Tiap experience wajib punya tautan kembali ke `../../index.html`.
- Tiap experience tetap halaman terpisah (memori GPU bersih saat pindah). Kode bersama dipindah ke `shared/` bertahap, jangan membongkar Copper Corn Station sekaligus.
- Rencana experience berikutnya: Millar's World (dunia air, dilatasi waktu; konsep `docs/millar/konsep-millar.md`, prototipe low poly `docs/millar/prototipe-low-poly-millar.md`, rencana versi realistis R1-R5 `docs/millar/rencana-realistis-millar.md`, R1 sampai R4 selesai), Penerbangan Kestrel (shuttle KS-07 dari Copper Corn Station). Usulan nama: `docs/app/penamaan.md`.
- Jangan memakai judul film, logo, huruf judul, musik, cuplikan, atau desain kendaraan film.
- Bahasa aplikasi: Indonesia dan English (Jepang dan Mandarin ditunda). Semua halaman berbagi pilihan lewat localStorage `lazarus.lang` dan `?lang=id|en`, dan tautan antarhalaman meneruskan `?lang=`. Menu utama: teks di `APP`, `EXPERIENCES` (field `en`) dan `TXT`. Gargantua: sumber English, kamus `ID`, fungsi `txt()`.

# Experience: Copper Corn Station

Simulasi silinder O'Neill yang mengorbit Saturnus. Satu file HTML (`experiences/cooper-station/index.html`), three.js, bisa dijelajahi berjalan kaki. Dibangun bertahap.

## Aturan kerja

- Bahasa: Indonesia untuk komentar kode, dokumen, dan balasan. Teks UI ditulis dalam bahasa Indonesia sebagai sumber, lalu diterjemahkan lewat kamus `I18N` (M3). Teks UI baru wajib lewat `t('...')` (atau label `uiLabel`) dan diberi entri di `I18N.en`; `tools/uji_bahasa.py` memeriksa kelengkapannya.
- Satu file: semua kode Copper Corn Station ada di `experiences/cooper-station/index.html` (CSS + JS modul). Tidak ada build step, tidak ada addon three.js (GLTFLoader juga tidak: model dari luar diolah dulu dengan skrip di `tools/`). Aset data di `experiences/cooper-station/assets/` dimuat lewat `<script>` biasa (base64) agar jalan dari file://; aset pihak ketiga wajib dicantumkan di `assets/KREDIT.md` dan tab Tentang.
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
| Orbit (17a) | radius 260.000 km, periode 37,57 jam; sumbu 65 derajat dari normal orbit; Matahari di bidang orbit, 25 derajat dari sumbu +z (masuk lewat end cap B); gerhana 2,78 jam per orbit |
| Dua scene | farScene (1 unit = 1.000 km: Saturnus, bintang, Matahari) + scene utama |

## Peta kode (cari dengan nama)

| Area | Nama penting |
| --- | --- |
| Konfigurasi | `CONFIG`, `HALF_L`, `R`, `CIRC`, `ART` (arteri keliling tiap 241,7 m), `ART_Z` (250 m), `ROAD`, `CITY`, `PARKZ`, `FARMS`, `RINGS_Z`, `nearRing()` |
| Cahaya | `LIGHT_GLSL` / `stationLight()`, `LIGHT.uniforms` (uL_Sunline, uL_SunDir, uL_CapI), `patchLit()` untuk MeshBasicMaterial, `updateLighting()` |
| Pantulan dan kilap (17b, 17d) | `farEnv(P, Rd, rough, lineK)` di `LIGHT_GLSL` (daratan seberang dari `uL_Land`, end cap, sunline, kabut; tidak ada langit biru), uniform `uL_FarLight` / `uL_FarAvg` / `uL_FogCol` / `uL_FogD` / `uL_Night`, `FAR.land` (rata-rata warna daratan, ambient siang), `specMat(m, rough, f0, metal, glass)` + `SPEC_GLSL` di `patchLit()` (21b: glass = 2 jendela rumah, satu bidang normal keluar, sisi penonton dari `dot(litN, V)`, bukan `gl_FrontFacing` yang terbalik di lintasan BackSide) (uniform per material `uSpec`, `userData.specU`); awan terpantul dari `uL_Cloud` (`CLOUD.mapTex`, digambar di `CLOUD.drawShadow()`) + `uL_CloudCol` |
| Cahaya lanjut (17c, 17e, 17f) | 17c `ADAPT` + `lumMat` + `POST_R.lum` (adaptasi mata di `postEnd()`, uniform `tAdapt` di `compMat`); 17e `nightLight(p, n)`, `lampPoolL()` / `tramPoolL()` di `LIGHT_GLSL` (20a: juga dipakai shader tanah, salinan lama dihapus), `uL_Tram` = `groundMat.uniforms.uTram` (satu objek, dipasang ulang setelah `UniformsUtils.merge`; material trem `userData.noTramLight` tidak disinari cahaya trem); 17f `SUNSH` + `sunShadowPass()`, `sunlineShadow(p, n, roof)` / `sunShCover(p)`; 18b-3: kedua peta bayangan (`SHADOW` dan `SUNSH`) dirender dalam koordinat silinder terbuka: `SHU` + `SH_UNROLL_VS` (`shUnroll()` di `depthMat.onBeforeCompile` dan material kedalaman `vegMaterial`), penerima `shUnrollP(p, th0)` dengan `uL_ShadowTh` / `uL_SunShTh`; material kedalaman baru wajib lewat `shUnroll`, `SUNSH_CHEAP` di `VEG_COMMON`, mobil dan pejalan kaki `castAlpha` |
| Bayangan | `SHADOW`, pass layer 1; alpha caster layer 2 (`ALPHA_CASTERS`) |
| Tanah | heightmap `TER` (half-float, sama CPU/GPU; 20c: `TER.hh` = nilai half float langsung untuk `heightTex`, faktor per kolom dihitung sekali, pijakan bangunan dilewati di baris amplitudo 0), `groundH(s, za)`, `groundMat` (uLand, uFieldTex, uCloudTex, uShadeTex, lampPool) |
| Vegetasi | `VEG_COMMON`, `TREES` (LOD + impostor, 16 template: oak, elm, poplar, maple, birch, pine, willow, bunga), `TREE_KINDS`, `GRASS`, `CORN` |
| Suasana daun (12b-2) | `LEAF` (mode Hijau/Campur/Gugur), `leafColorFor()`, `applyLeafMode()`, atribut `aLeafC` + `LEAF_RECOLOR`, `WIND` + `updateWind()` (uniform `uWind`), `FALL` (daun jatuh GPU, mendarat dan diam di tanah) + `updateFallSources()`; serakan daun tekstur `uLitterTex` dihapus di revisi 20d |
| Pejalan kaki (12b-3) | `PEDS` (list, walk, near), `stepPeds()` (simulasi CPU, jauh bergiliran), `updatePeds()` (pilih dalam radius, atribut aP/aI/aJ), `pedAct()` (kepadatan per jam), `sigQ()`, `applyPedsPreset()` lewat `PRESET_HOOKS`, `cyclePeds()`; 21a-1 pengunjung plaza `kind: 'visit'` (`VIS` fount / groups, `stepVisit()` keadaan loop / in / stay / out, `visPathOK()`, `rectPoint()`, acak sendiri `visRnd()`) |
| Burung (12b-4) | `BIRDS` (flocks boids, vees formasi V, groups merpati), `stepBirds()`, `updateBirds()`, `applyBirdsPreset()`, `toggleBirds()` |
| Suasana (12b-5) | `VIBE` (kafe, lampu untaian, sepeda terdaftar sebagai kind di `FURN`; bendera `VIBE.flags`; layang-layang), `updateVibe()`, audio `AUDIO.crowd` / `AUDIO.car` / `AUDIO.carHum`, kabut pagi di `updateLighting()` |
| Hujan dan Coriolis (12c) | `RAIN` (k kekuatan, wet, vlat), `updateRain()` (20b: awan di atas pemain dari `cloudCoverAt(s, za)`, bukan `getImageData`), `rainSheltered()`, uniform `uWet` di `groundMat`, `FOUNT` (air mancur, `FOUNT_TEXT`; 21a-1: lokasi `FOUNT.s` / `FOUNT.za` / `FOUNT.block` dihitung di blok pohon, zona larangan `FOUNT.clear` 7 m, `fountDist()`, `fountPush()`), `SPOTS.fountain` (tombol 9), `WIND.base` mengikuti `WEATHER.ov` |
| Ladang, foto, tur (12d) | `wheatStage()` (VEG_COMMON dan shader tanah), `uCropT`, `clock.totalH`, `f.per`, `farmStage(f)`, `FARM` + `updateFarm()` (mesin panen, traktor, debu); `PHOTO` + `togglePhoto()` / `savePhoto()` / `applyPhoto()`, DOF di `compMat` (uDof, uFocus); `TOUR` + `tourKeys()` / `startTour()` / `stepTour()` / `stopTour()`, `player.state` 'tour' |
| Baseball | `BALLPARK`, `FIELD` (home plate), `ballparkModel()` (dibangun datar lalu ditekuk ke lengkung silinder), `BASEBALL` + `stepBaseball()` (pemain dan penonton disisipkan ke buffer `PEDS` di `updatePeds()`, bola) |
| Rel dan Skyway (13a-c) | `inTramCorridor()`, `treeSkipped` (pohon yang ditolak tetap memakai angka acak), `RING_LAMP_S`, `SKY_ROADS`, `onSkyRoad()`, `SKYX` (akuaduk, `flow`), lantai kaca jendela `glass` / `glassMat` |
| Peta (13d, 16f) | `MAPV` (zoom, cx = za, cy = s, layers dist/fac, fac), `MAP_MARKS` (key, name, at, go; N/P/T fasilitas), `FAC_ICON` / `FAC_NAME` / `facilityList()`, `goDistrict(D)`, `drawMapStatic()` (latar 4000 x 3142), `drawMap()` (vektor tiap frame), `mapZoomAt()`, `mapCenterMe()`, `mapGo()`, `buildMapLegend()` |
| Hutan (14a) | `FOREST` (s0, s1, z0, z1, trailW, k, fernR, list, mesh), `forestTrail(za)`, `inForest()`, pohon `t.forest` (langkah 4 di blok TREES, RNG sendiri), `TREES.forestLod` + uniform `uLodF` / `uForest` (impostor lebih dekat), `updateForest()` (kabut, pakis), `applyForestPreset()`, `SPOTS.forest` (tombol 0) |
| Rumput bukit (14b) | `MEADOW_GLSL` (`meadowMask(h)`, `meadowGust(P, off)`, dipakai rumput 3D dan shader tanah; uniform `uWindSlow`, `uGustOff` diintegrasikan di `updateWind()`: jangan pakai fase waktu x kecepatan angin), `MEADOW` (near, mid, nearR, midR, active), `MEADOW_VS`, `applyMeadowRadii()`, uniform `uMeadowOn` (rumput pendek disembunyikan di bukit), `tuftGeo(..., heads)` |
| Trotoar dan jalan setapak (15c) | `SIDEWALK_GLSL` (`sidewalkD(P, art)`, di shader tanah dan rumput) = `SIDEWALK.d(s, za)` di JS (ubah keduanya bersama), `PARK_PATHS` (runs, mesh pita), `colAt(s, za, m)`; tepi blok arteri 17 m dari sumbu |
| Fasilitas kota (16c-e) | `blockRect(c, a, b)`, `CITY_BLOCKS`, `reserveSite(type, target, minW, minD, extra)` + `SITE_AT` / `SITES`, `buildSite(site)` (menara, alun, balai, ...), `LANDMARK` (menara ikon 221 m, beacon), `MARKET` (list, stalls, aisles) + `marketStalls()` / `buildMarket()`, `buildCivic()` (taman distrik, sekolah, rs); potongan geometri fasilitas ikut `MOSQUE.parts` (penanda `g` = ikut tinggi tanah, digabung ke `MOSQUE.meshG` setelah `TER`) |
| Utilitas (18a) | `UTIL` (za0 6.400, za1 6.900), `UTIL_PLAN` (modules, silos, pipes); blok "18a" setelah loop lama gudang (loop lama hanya menghabiskan angka acak): generator acak sendiri, `split()` BSP, `module()` (gudang bertingkat, tangki, cerobong, unit atap), rak pipa di atas jalan servis |
| Dek pandang (18b) | `DECK` (s, za, h 175, half 8, inner 5, podD; teras keliling atap tingkat 4, diisi di `buildSite('menara')`), `player.deck`, `onDeck()` (cincin), `deckClamp()` (di `stepGround`), `towerJump(up)` (aksi E `tower` / `towerdown`, langsung tanpa lift), `goDeck()` (tombol panel), pendaratan di dek di `stepAir`, `dropBall` dari luar pagar |
| Distrik (16) | `DISTRICTS` (name, kind mega/astro/taman/tani, k0-k1, z0-z1, c), `districtAt(s, za)`, `HUD_DIST` (notifikasi saat pindah distrik), `homeDensity()` |
| Masjid (15e) | `MOSQUE` (list, mesh, names), `mosque(s, za, kind)` 0 Utsmani / 1 Maroko / 2 Saudi, `buildMosqueMesh()`; menggantikan setiap gereja kedua |
| Permukiman (15d, 16a) | `fillHomes(s0, z0, s1, z1, d, sparse)` (gang, 4 baris, baris samping; tingkat dari `homeDensity()`: deret / tunggal / berhalaman / besar / desa, ambang 0,47 / 0,33 / 0,21 / 0,07), `YARD_TREES` (ditanam di blok pohon), `GANGS`; `front` 3/4 = muka -s/+s di `BUILD_FS` |
| Bangunan | `building(type, s, za, w, d, h, color, elev, collider, style, front)`, gaya 0-11, `BUILD_U.uNight`, 21c: nyala jendela bertingkat di `BUILD_FS` (`litB`, lantai / blok 4 bay / jendela `onF` `onBk` `on0`, rata-rata per tingkat `ax` / `ax4` / `ayF`), `BUILD_U.uLitT` (faktor jam kantor / hunian dari `updateLighting()`), lampu mahkota, lampu penanda atap (`BUILD_U.uTime` = `groundMat.uniforms.uTime`), varying flat (perbaikan GTX 1060) |
| Interior jendela (14c) | Di `BUILD_FS` blok "14c" (ruangan = bay x lantai, sinar dari varying `vDirO` di `BUILD_VS`, arah kamera ke titik dalam ruang objek berskala), `kI` (campur dengan kaca lama lewat `detail`), `BUILD_U.uInterior`, `applyInteriorPreset()` (mati di Rendah dan Hemat) |
| Grup kecil (20b) | `mergeByMaterial(G)` (gabung anak langsung per material; lewati transparan, InstancedMesh, `userData.keep`), `enableCull(G, pad)` (frustum culling, bola batas +pad m untuk pass bayangan); dipakai lapangan baseball, kabin lift, hub, lobi menara lift, rumah Cooper, trem. Grup baru yang banyak mesh kecil sebaiknya ikut |
| Pemilihan bayangan (20d) | `SHP` (stat = gedung kota + peralatan atap dengan bola batas per instance, cars = geometri pengganti mobil per pass, margin 16 m, redo 12 m), `shpBegin(pass, cam, th0, za, phi)` / `shpEnd()` di `shadowPass()` dan `sunShadowPass()` (tukar `instanceMatrix`/`count` dan `TRAFFIC.cars.geometry` selama pass), `shpIn()` / `shpBox()` (uji kotak kamera di koordinat `shUnroll`), `SHP.on = false` untuk perbandingan. InstancedMesh statis besar baru yang membuat bayangan bisa didaftarkan ke `SHP.stat` |
| Kolisi | `COL`, `addCollider(s, za, hs, hz)` (AABB di bidang s-za), `LATE_COLLIDERS` |
| Awan/cuaca (11a) | `WEATHER` (mode auto/cerah/berawan/mendung, cover, ov), `CLOUD`, `updateClouds(dt)`, `cycleWeather()` (N) |
| Sunrays (11b) | `RAYS`, `rayMat` (ray-march setengah resolusi + berkas layar), dipakai di `postEnd()` |
| Perabot kota (11c) | `FURN` (bench, bin, hydrant, planter, signal, cabinet, mailbox, zebra), LOD per radius, `updateFurniture()` |
| Spaceport (11d) | `PORT`, `DOCK` (grup despun), `SHIPS` (player, ai, cargo, tug), `COCKPIT`, `TERM` (terminal; posisi didefinisikan di bagian plaza), `portBoard()`, `stepPort()`, `updateFlightCamera()`, `portKey()`, `portMouse()` |
| Spaceport rapi (12a) | `TERM.gate`, `portStartTrip()`, `PORT.trip` (perjalanan otomatis 5x dari gerbang B1), `DGUIDE` + `updateDockGuide()` (kotak target, garis arah), `dockData()`, `drawCockpitScreen()`, `portClank()`, `AUDIO.shipBus` (eng, engTone, rcs, cab, cabHum), `PORT.thr` / `PORT.rcs` / `PORT.turn` |
| Orbit dan gerhana (17a) | `ORBIT` (axisTiltDeg), `SUN_AXIS_DEG`, `SUN_DIR`, `orbitPhase()`, `saturnDirInertial()`, `ECL` (k, phiC, half, dockLight) + `updateEclipse()` (dipanggil di `updateFar()`), `eclipseIn()`, `jumpToEclipse()` (tombol I), cangkang cahaya tepi `limbMat` di blok Saturnus, silau `glareMat` (uK) |
| Post | `POST`, `postBegin()`, `postEnd()`: HDR, SSAO, bloom 6 tingkat, ACES, FXAA |
| Audio | `AUDIO`, `startAudio()`, `updateAudio(dt)` (semua disintesis) |
| Preset | `PRESETS` (Ultra/Tinggi/Sedang/Rendah/Hemat; Hemat untuk MacBook M1), `applyPreset(i)`, turun otomatis bila FPS < 30 selama 4 s, tersimpan di localStorage, `?preset=hemat` |
| Lalu lintas | `TRAFFIC` (gambar di GPU, posisi dari simulasi CPU `stepTraffic()` model IDM, atribut `aSim`), `SIG` + `sigState(k, m, axis, t)` (lampu lalu lintas), `BLVD` (15b: lajur boulevard k = 0, lampu di 21,5 m; simpang k = 0 = palang trem + lampu), `TRAFFIC.beams` (sorot lampu depan malam, `aKind` 6-7 di `CAR_VS`), `XING` + `updateCrossings()` + `XVIS` (perlintasan trem, palang, bel), `LAMP` |
| Trem | `TRAM`, `TRAM_CAR`, `TRAM_SEATS`, `tram`, `TRAM_PARTS` (lights, cabinLamp, doors), `updateTramVisual()`; malam (15a): `CABIN_LIGHT.uCabin` (material `userData.cabin` di `patchLit`), `tramPool()` + uniform `uTram` di `groundMat`; lampu halte `STOP_LIGHT` (strip, pool) di `updateTraffic()` |
| Lift/hub | `LIFT`, `HUB`, `CABIN`, `enterLift()`, `stepFloat()` |
| Lokasi | `SPOTS` + `teleport(key)`: cooper, hill, corn, wheat, skyway, baseball, spaceport, fountain, forest, nyc, market, farmmarket |
| Panel dan HUD (M2) | `labEl`, `toggleLab()`, `labTab(id)` (data-ltab / data-lpane), `LABUI`, `setLabText()` (juga notifikasi `#toast`), `setHudMode(compact)` (kelas `x` = baris HUD lengkap) |
| Bahasa (M3) | `LANGS`, `LANG` (cur, labels, hooks), `t(src, vars)`, `fmtN()`, `fmtInt()`, `uiLabel(id, fn, html)`, `translateDom()`, `setLang(c)`, kamus `I18N.en` (kunci = teks Indonesia persis), pilihan di `.langPick`, `?lang=en`, localStorage `lazarus.lang` |
| Layar muat dan bantuan (M1) | `BOOT`, `BOOT_W` (bobot progres terukur), `bootStep(frac, label)`, `startEl`, `helpEl` + `toggleHelp()` / `helpTab()`, `showHint()`, pilihan preset `#presetPick` |
| Gerak kepala (19a) | `BOB` (level, phase, steps, amp, run, y/vy pegas mendarat), `BOB_LEVELS`, `headBob(dt)` (dipanggil di awal `updateCamera()`), `lookBasis(up, tan, dPitch)` + `rollBasis(r)`, `updateFov(dt)` (lari dan motor; diam = tepat `CONFIG.fov`, tidak jalan saat mode foto), `cycleBob()` / `bobLabel()`; suara langkah = `BOB.steps` berubah (`AUDIO.lastSteps`) |
| Motor (19b, 19c) | `MOTO` (on, parked, s, za, h, hd, v, yaw, steer, lean, pitch, look, gFelt, gear, rpm, sy suspensi, vMax / vSport pembatas 60 / 150 km/h), sub-mode state `ground`; fisika `stepMoto(dt)` (dekat `stepGround`), `motoMount()` / `motoDismount()` / `motoPark()` / `toggleMoto()` (C), `motoCrash()`, `motoHorn()` (Space); kamera `motoCamera()` (getaran ikut `BOB.level`, mata `MOTO_V.eye`); model `MOTO.mesh` (kelompok body, frontG = front + riderF berputar di `MOTO_V.axis` lewat `MOTO_V.axle`, rider, stand, shadow = layer 1 saja), 19c: `motoLoadGLB()` / `motoBuildGLB()` (aset `assets/motor.data.js`, `MOTO_V.glb`, `MOTO_V.credit`; gagal = motor sederhana), pembuat geometri `mkBox` / `mkEll` / `mkRod` / `mkMerge`, `MOTO_MT`, `motoMatrix(m, lean, pitch)`, `motoVisual()` (tiap frame di `updateCamera`), dial `drawDial()` (model aset) / dasbor `drawDash()` (`MOTO_V.dashTex`), suara `motoAudio()` / `motoStartSound()` / `motoHornSound()` / `motoThud()`; lampu depan = uniform `uL_Head` / `uL_HeadDir` / `uL_HeadG` di `LIGHT`, `headPoolL()` (tanah, juga pantulan aspal basah) dan `headSpotL()` (di `nightLight`), `motoPrompt()`, panel tab Gerak (`labMoto`, `labBob`), tombol sentuh `btnMoto` |
| Ukur GPU (20a) | `GPUT` (EXT_disjoint_timer_query_webgl2), `gpuBegin(key)` / `gpuEnd()` / `gpuFrameEnd()` di `frame()`: sh bayangan, sc scene, po post; baris HUD `hGpu*`, aktif saat HUD lengkap |
| Uji | `window.__station` mengekspor objek penting untuk skrip uji |

## Status pemain (`player.state`)

`ground` (`player.deck` true = di dek pandang menara; `MOTO.on` true = naik motor, fisika `stepMoto`), `air`, `lift`, `float` (hub nol-g), `tram`, `pod` (kapsul terowongan ke dermaga), `ship` (di shuttle; `ext.active` dan `ext.flight` true), `tour` (tur sinematik, pemain dibekukan). `PORT.trip` true = sedang perjalanan otomatis dari gerbang B1 (lift dan kapsul 5x, E = langsung ke kokpit).

## Tombol

W A S D, Shift, Space, B, G, L, T, E, M, V, [ ], Z (kecepatan waktu), N (cuaca), O, X, R, H, 0-9 (lokasi; 8 = kokpit shuttle, 9 = air mancur Coriolis, 0 = hutan lebat), K, Q, P, U, J, F (mode foto, Enter simpan PNG), Y (tur sinematik), I (lompat ke gerhana Saturnus), C (naik / turun motor), ` (panel kontrol), / atau F1. Di pesawat: W/S, A/D, R/F, Z/C, mouse, Shift, X, V, E, L. Di motor: W gas, S rem / mundur, A/D belok, Shift sport, Space klakson, O gas terus, mouse menoleh, C atau E turun (di bawah 10 km/h).

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
| 12b-3 | Pejalan kaki: trotoar, taman, terminal, halte, bangku; menyeberang di zebra saat lampu jalan |
| 12b-4 | Burung: kawanan boids, formasi V di bawah awan, merpati di plaza; revisi tongkol jagung, daun jatuh diam di tanah, pohon baru lebih tinggi |
| 12b-5 | Suasana: kafe trotoar, lampu untaian plaza, bendera dan umbul-umbul, sepeda, layang-layang, suara kota, kabut pagi; perbaikan NaN normal di ujung daun jagung (titik menyala) |
| 12c | Hujan miring 8 derajat oleh Coriolis, tanah basah dan genangan, suara hujan, angin mengikuti cuaca, air mancur Coriolis dengan plakat |
| 12d | Siklus tanam gandum 96 jam, mesin panen dan traktor dengan debu, mode foto (F, DOF, simpan PNG), tur sinematik dengan penjelasan fisika (Y) |
| 12d+ | Pertandingan baseball siang, pagar dan papan skor lapangan mengikuti lengkung silinder, perbaikan NaN layang-layang (kilau seperti komet), klik mouse = kunci / lepas kursor |
| 13a-13d | Rel trem bersih, jembatan jalan dan akuaduk di Skyway (mobil satu keliling penuh), tombol 5 di atas lantai kaca, peta besar M dengan penanda dan klik = pindah |
| 14a | Hutan lebat 5.222 pohon 22-35 m dengan jalan setapak, semak dan pakis, kabut hutan, tombol 0, penanda peta, titik tur |
| 14b | Rumput tinggi di bukit dengan pita gelombang angin (dekat 3D, jauh di shader tanah), merunduk di sekitar pemain |
| 14c | Interior jendela: ruangan berkedalaman di balik jendela gedung dekat (perabot, tirai, lampu malam), kaca memantulkan langit dan gedung seberang makin kuat dengan jarak, mati di Rendah dan Hemat |
| 15a-15e | Trem menyala malam, mobil di boulevard samping rel, trotoar dan jalan setapak taman, permukiman padat bertingkat (gang, rumah deret, pohon halaman), setengah gereja diganti masjid (Utsmani, Maroko, Saudi) |
| 16a-16f | Gradasi kepadatan permukiman (deret sampai desa), 14 distrik kota (megacity dan astronom) + zona luar kota bernama, pusat New York dengan menara ikon 221 m, balai distrik, 15 pasar, taman distrik, sekolah, rumah sakit, peta dengan distrik dan ikon fasilitas |
| 17a | Sumbu stasiun dimiringkan ulang: sinar Matahari masuk end cap B 25 derajat (jangkauan 4,3 km), gerhana Saturnus tiap orbit (sinar padam, cahaya tepi atmosfer, notifikasi, tombol I) |
| 17b, 17d | Kaca gedung, air, jalan basah, dan mobil memantulkan daratan seberang (bukan langit biru), ambient siang ikut warna daratan, kilap dan Fresnel untuk cat, logam, dan kaca |
| 17c, 17e, 17f | Awan ikut terpantul, adaptasi mata (tombol di panel Grafik), lampu jalan dan trem menerangi objek saat malam, bayangan sunline real-time dekat pemain (tajam keliling, lembut searah sumbu; mobil dan pejalan kaki ikut) |
| 18a | Kompleks utilitas padat: mozaik modul berdempetan (gudang bertingkat, tangki, cerobong, unit atap), jalan servis, rak pipa |
| 18b | Atap pasar menempel dinding, pintu menara gereja, halaman beton gereja/masjid/pasar, jendela rumah Cooper tembus pandang (lubang dinding sungguhan), bayangan dinding tidak lagi hitam atau naik turun (peta bayangan sunline dan cincin cap dalam koordinat silinder terbuka), dek pandang di teras tingkat 4 menara ikon (175 m, E langsung naik-turun) dan uji lempar bola |
| 19a, 19b | Gerak kepala saat jalan dan lari (langkah, ayun, napas, hentakan mendarat, FOV lari; panel Gerak: Mati/Halus/Normal), motor POV (setang, dasbor, spion, miring di tikungan, suspensi, berat terasa searah/melawan putaran), lampu depan malam menerangi tanah dan objek, suara mesin dan klakson |
| 19c | Model motor diganti café racer V-twin (aset CC BY 4.0, diolah `tools/siapkan_motor.py`, dial speedometer berjarum), sport sampai 150 km/h, getaran motor diredam (aspal dan tanah) |
| 20a | Optimasi tanpa ubah visual: jagung 3D hanya bila ada petak jagung dekat (`cornGate()`), bulir rumput tak terpakai dibuang di vertex shader, kode kolam cahaya tanah tidak ganda, kamera luar ikut dt nyata, alat ukur GPU di HUD; perbaikan trem malam menerangi objek (uniform `uL_Tram` tersalin) |
| 20b | Draw call turun 54% di spawn (grup kecil digabung per material + frustum culling), pantulan gedung hanya di kaca, normal instance tanpa `inverse()`, tanpa baca-balik piksel sinkron saat bermain (awan dihitung di CPU, data lahan dibaca sekali `FAR.landData`, label adaptasi asinkron) |
| 20c | Muat lebih cepat dengan dunia identik: peta tinggi tanah (faktor per kolom, half float disimpan langsung, pijakan utilitas dilewati), penempatan pohon bukit memakai grid spasial, `vnoise` tanpa closure; muat 7,3 s menjadi 4,2 s di sandbox. Kanvas lahan `willReadFrequently` dicoba lalu dibatalkan (9,4% piksel berbeda di tepi anti-alias) |
| 20d | Pass bayangan hanya menggambar gedung, peralatan atap, dan mobil yang jatuh di kotak kamera bayangan (diuji di koordinat silinder terbuka): segitiga bayangan spawn 1,93 juta menjadi 0,50 juta per frame, hasil render identik (0 nilai berbeda di 6 lokasi dan saat berjalan). Revisi: serakan daun tekstur di bawah pohon berwarna dihapus atas permintaan (mozaik kotak, tercampur bayangan, menyala di bawah lampu malam); daun jatuh 3D tetap |
| 21a-1 | Air mancur: tidak ada lagi orang diam di dalam kolam, 8 pengunjung datang ke tepi kolam (berdiri atau duduk di bibir kolam) lalu pergi, kelompok mengobrol di plaza bubar dan berkumpul lagi tiap 3-8 menit, merpati menjauh dari kolam; dunia lain identik |
| 21b | Kaca jendela rumah Cooper benar-benar bening dari dalam (dulu hampir pejal dari kedua sisi, memantulkan silinder); dari dalam hanya memantulkan ruangan redup, dari luar tetap memantulkan daratan seberang |
| 21c | Gedung malam dari jauh tidak lagi terang rata atau putih: lampu menyala per lantai dan per blok kantor, warna kantor putih / hunian hangat, jumlah lampu ikut jam, lantai mesin gelap, lobi terang, lampu mahkota di sebagian menara > 120 m, lampu merah berkedip di atap gedung > 90 m; siang tidak berubah |

Tahap 12, 13, dan 14 selesai (rencana: `docs/cooper-station/rencana-tahap-13-14-cooper-station.md`). Tahap 15 selesai: `docs/cooper-station/rencana-tahap-15-cooper-station.md` (15a lampu trem, 15b lalu lintas boulevard, 15c trotoar, 15d permukiman padat, 15e masjid). Tahap 16 selesai: `docs/cooper-station/rencana-tahap-16-cooper-station.md`. Tahap 17: `docs/cooper-station/rencana-tahap-17-cooper-station.md` (17a sampai 17f selesai). Tahap 18: `docs/cooper-station/rencana-tahap-18-cooper-station.md` (18a kompleks utilitas, 18b revisi bangunan dan dek pandang selesai). Tahap 19: `docs/cooper-station/rencana-tahap-19-cooper-station.md` (19a gerak kepala, 19b motor dan lampu depan, 19c model café racer, 150 km/h, getaran diredam selesai; berisi usulan lanjutan). Analisa optimasi (terukur per pass dan waktu muat) dan usulan sebelum Millar's World: `docs/cooper-station/analisa-optimasi-dan-usulan-cooper-station.md`. Tahap 21: `docs/cooper-station/rencana-tahap-21-cooper-station.md` (21a-1 orang di kolam, 21b kaca rumah Cooper, 21c gedung malam selesai; sisa 21a-2 semburan dan 21a-3 riak air; 21a air mancur: orang tidak terjebak, semburan dan riak air; 21b kaca rumah Cooper dari dalam; 21c gedung kaca malam tidak putih rata).

Catatan muat (M1): modul memakai `await bootStep(...)` di tingkat atas di antara bagian besar. Bagian baru ditambah di tingkat atas modul (bukan di dalam fungsi) dan diberi titik jeda bila berat; `window.__stationReady` baru true setelah shader dikompilasi.

Catatan GPU: geometri buatan sendiri yang memakai material dasar (dicahayai `patchLit`) wajib punya atribut normal (`computeVertexNormals()`); shader cahaya kini juga dijaga. Di shader jangan `normalize()` vektor yang bisa nol, jangan `pow()` bilangan yang bisa negatif, jangan `sqrt()`/`asin()` di luar rentang (NaN di Apple M1 disebar bloom jadi titik putih berkedip). Sandbox uji (SwiftShader) tidak memperlihatkan NaN.
