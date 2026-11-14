#!/bin/bash
# Uji GPU lokal Interstellia (macOS). Klik ganda di Finder, atau dari Terminal: tools/uji_gpu_lokal.command --lengkap
# Butuh Python 3 (python3 --version; bila belum ada: xcode-select --install) dan internet.
cd "$(dirname "$0")/.." || exit 1
command -v python3 >/dev/null || { echo "Python 3 belum terpasang: jalankan xcode-select --install"; read -r; exit 1; }
python3 -m pip install --quiet --user --upgrade playwright pillow || { echo "Gagal memasang playwright"; read -r; exit 1; }
python3 -m playwright install chromium || { echo "Gagal mengunduh Chromium"; read -r; exit 1; }
python3 tools/uji_gpu_lokal.py "$@"
echo "Tekan Enter untuk menutup"; read -r
