"""Olah peta global Jupiter NASA menjadi experiences/cooper-station/assets/jupiter.data.js.
Sumber sekarang: Hubble OPAL 2015, STScI-01EVT28CB7CN0CEYRV56WP1S6A (NASA, ESA, A. Simon / GSFC, OPAL Team), peta silindris 3600 x 1598 piksel yang
hanya mencakup lintang -80 sampai +80 derajat; kutub diisi dari baris tepi yang diburamkan (peta Cassini PIA07782 sebelumnya penuh 180 derajat).
Pemakaian: python3 tools/siapkan_jupiter.py sumber.tif [lebar=3600] [mutu=86] [lintang=80]
Unduh sumber: https://assets.science.nasa.gov/dynamicimage/assets/science/missions/hubble/releases/2015/10/STScI-01EVT28CB7CN0CEYRV56WP1S6A.tif?w=3600
Keluaran: window.JUPITER_MAP = { w, h, jpg: <base64> } dengan h = w / 2, baris pertama = kutub utara (butuh pillow dan numpy)."""
import base64, io, sys
import numpy as np
from PIL import Image, ImageFilter
Image.MAX_IMAGE_PIXELS = None
src = sys.argv[1]; w = int(sys.argv[2]) if len(sys.argv) > 2 else 3600; q = int(sys.argv[3]) if len(sys.argv) > 3 else 86; lat = float(sys.argv[4]) if len(sys.argv) > 4 else 80.0
h = w // 2
im = Image.open(src).convert('RGB')
hs = round(h * 2 * lat / 180)                                       # tinggi bagian bermiliki data setelah diskala ke lebar w
im = im.resize((w, hs), Image.LANCZOS)
pad = h - hs; top = pad // 2; bot = pad - top
a = np.asarray(im).astype(np.float32)
def tgt_color(rows):                                                # warna acuan kutub: rata-rata pita 6-14% dari tepi (bagian tepi sumber memudar jadi krem terang)
    return rows[int(0.06 * hs):int(0.14 * hs)].mean(axis=(0, 1))
def fade_edge(blk, tgt, n):                                         # 6% baris tepi data dicampur ke warna acuan (krem pudar sumber diganti)
    k = np.clip(1 - np.arange(n) / n, 0, 1)[:, None, None] ** 1.5
    return blk * (1 - 0.85 * k) + tgt * 0.85 * k
nE = int(0.06 * hs)
tU, tD = tgt_color(a), tgt_color(a[::-1])
a[:nE] = fade_edge(a[:nE], tU, nE); a[-nE:] = fade_edge(a[-nE:][::-1], tD, nE)[::-1]
def cap(row_block, n, tgt):                                         # isi kutub: baris tepi, diburamkan horizontal, memudar ke warna acuan
    r = row_block.mean(axis=0, keepdims=True)
    strip = Image.fromarray(np.repeat(r, 8, axis=0).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(40))
    r = np.asarray(strip).astype(np.float32)[4:5]
    k = np.linspace(0, 1, n)[:, None, None]
    return r * (1 - 0.5 * k) + tgt * 0.5 * k
cu = cap(a[:6], top, tU)[::-1]; cd = cap(a[-6:], bot, tD)
full = np.concatenate([cu, a, cd], axis=0).clip(0, 255).astype(np.uint8)
im2 = Image.fromarray(full)
buf = io.BytesIO(); im2.save(buf, 'JPEG', quality=q, optimize=True)
b = base64.b64encode(buf.getvalue()).decode()
out = 'experiences/cooper-station/assets/jupiter.data.js'
open(out, 'w').write('/* Peta global Jupiter: NASA, ESA, A. Simon (GSFC) dan Tim OPAL, Hubble 2015 (STScI-01EVT28CB7CN0CEYRV56WP1S6A), diolah tools/siapkan_jupiter.py */\nwindow.JUPITER_MAP = { w: %d, h: %d, jpg: "%s" };\n' % (w, h, b))
im2.resize((900, 450)).save('/tmp/jupiter_prev.png')
print(out, w, h, len(buf.getvalue()) // 1024, 'KB jpeg', len(b) // 1024, 'KB base64; baris data', hs, 'kutub', top, bot)
