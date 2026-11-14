@echo off
rem Uji GPU lokal Interstellia (Windows). Klik ganda, atau dari cmd: tools\uji_gpu_lokal.bat --lengkap
rem Butuh Python 3 (python.org, centang "Add to PATH") dan internet.
cd /d "%~dp0\.."
where python >nul 2>nul || (echo Python belum terpasang: https://www.python.org/downloads/ & pause & exit /b 1)
python -m pip install --quiet --upgrade playwright pillow || (echo Gagal memasang playwright & pause & exit /b 1)
python -m playwright install chromium || (echo Gagal mengunduh Chromium & pause & exit /b 1)
python tools\uji_gpu_lokal.py %*
pause
