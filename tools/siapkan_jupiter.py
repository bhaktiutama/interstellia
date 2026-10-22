"""Olah peta global Jupiter NASA (Cassini ISS, PIA07782, domain publik) menjadi experiences/cooper-station/assets/jupiter.data.js.
Pemakaian: python3 tools/siapkan_jupiter.py PIA07782.jpg [lebar=3072] [mutu=82]
Unduh sumber: https://assets.science.nasa.gov/content/dam/science/psd/photojournal/pia/pia07/pia07782/PIA07782.jpg
Peta silindris sederhana (lebar = 360 derajat bujur, tinggi = 180 derajat lintang, baris pertama = kutub utara).
Keluaran: window.JUPITER_MAP = { w, h, jpg: <base64> } (butuh pillow)."""
import base64, io, sys
from PIL import Image
src = sys.argv[1]; w = int(sys.argv[2]) if len(sys.argv) > 2 else 3072; q = int(sys.argv[3]) if len(sys.argv) > 3 else 82
im = Image.open(src).convert('RGB'); h = w // 2
im = im.resize((w, h), Image.LANCZOS)
buf = io.BytesIO(); im.save(buf, 'JPEG', quality=q, optimize=True, progressive=False)
b = base64.b64encode(buf.getvalue()).decode()
out = 'experiences/cooper-station/assets/jupiter.data.js'
open(out, 'w').write('/* Peta global Jupiter: NASA/JPL/Univ. Arizona, Cassini ISS PIA07782 (domain publik), diolah tools/siapkan_jupiter.py */\nwindow.JUPITER_MAP = { w: %d, h: %d, jpg: "%s" };\n' % (w, h, b))
print(out, w, h, len(buf.getvalue()) // 1024, 'KB jpeg', len(b) // 1024, 'KB base64')
