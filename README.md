# Lazarus (nama kerja)

Kumpulan experience 3D bertema perjalanan antarbintang, dipanggil dari satu menu utama. Proyek penggemar untuk belajar fisika dan grafis 3D, tidak berafiliasi dengan studio film mana pun.

## Experience

| Experience | Status | Isi |
| --- | --- | --- |
| Stasiun Cooper | Siap | Silinder O'Neill 8 km di orbit Saturnus: kota, ladang, trem, lift ke sumbu nol-g, spaceport, shuttle yang bisa diterbangkan |
| Gargantua | Siap | Lubang hitam berputar dengan piringan akresi |
| Planet Ombak | Rencana | Dunia air dekat lubang hitam |
| Penerbangan Kestrel | Rencana | Shuttle KS-07 ke cincin Saturnus |

## Menjalankan

- Buka `index.html` di browser (Chrome/Edge/Safari terbaru), pilih experience. Butuh internet (three.js dari cdn.jsdelivr.net).
- Atau aktifkan GitHub Pages (Settings > Pages > branch `main`, folder root).

## Struktur

| Path | Isi |
| --- | --- |
| `index.html` | Menu utama |
| `experiences/` | Satu folder per experience |
| `docs/app/` | Dokumen aplikasi, termasuk usulan nama |
| `docs/cooper-station/` | Konsep, tahapan, rencana tahap 11 dan 12 |
| `tools/qc_load.py` | Cek halaman termuat tanpa error |
| `tools/uji_spaceport.py` | Uji spaceport Cooper Station (pintu, gerbang, sandar) |
| `tools/uji_lalu_lintas.py` | Uji lalu lintas Cooper Station (lampu, perlintasan trem) |
| `tools/uji_pohon.py` | Uji pohon dan suasana daun Cooper Station |
| `tools/uji_pejalan_kaki.py` | Uji pejalan kaki Cooper Station |
| `tools/uji_burung.py` | Uji burung Cooper Station |
| `tools/uji_suasana.py` | Uji suasana Cooper Station |
| `tools/uji_hujan.py` | Uji hujan dan air mancur Coriolis |
| `tools/uji_ladang_foto_tur.py` | Uji siklus tanam, mesin ladang, mode foto, tur sinematik |
| `CLAUDE.md` | Konteks proyek untuk Claude Code |

Riwayat Cooper Station per tahap ada di git log.
