@echo off
echo === Uji GPU lokal Interstellia ===
cd /d "%~dp0.."
echo Folder repo: %CD%
where python >nul 2>nul
if errorlevel 1 goto nopy
echo [1/3] Memasang playwright dan pillow...
python -m pip install --upgrade playwright pillow
if errorlevel 1 goto gagal
echo [2/3] Mengunduh Chromium untuk Playwright...
python -m playwright install chromium
if errorlevel 1 goto gagal
echo [3/3] Menjalankan uji. Jendela Chrome akan terbuka, jangan dipakai selama uji.
python -u tools\uji_gpu_lokal.py %*
echo.
echo Selesai. Laporan ada di folder hasil-uji-gpu
pause
exit /b 0
:nopy
echo Python belum terpasang atau belum di PATH. Pasang dari https://www.python.org/downloads/ dan centang "Add python.exe to PATH".
pause
exit /b 1
:gagal
echo Langkah di atas gagal. Salin pesan galat di atas dan kirim ke Claude.
pause
exit /b 1
