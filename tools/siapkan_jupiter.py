"""Olah peta global Jupiter menjadi experiences/cooper-station/assets/jupiter-<4k|8k|14k>.data.js (satu berkas per lebar; tiga pilihan resolusi di Copper: python3 tools/siapkan_jupiter.py sumber.jpg 4096 / 8192 / 14400).
Sumber sekarang: "20180511_jupiter_map_css_plus_juno_bj.jpg" (The Planetary Society, Bjorn Jonsson; mosaik Cassini ISS + Juno JunoCam, 14400 x 7200,
silindris penuh 180 derajat). Sebelumnya: Hubble OPAL 2015 (3600 x 1598, lintang +-80, kutub diisi) dan Cassini PIA07782 (3601 x 1801).
Pemakaian: python3 tools/siapkan_jupiter.py sumber.jpg [lebar=8192] [mutu=84] [lintang=90]   (lintang < 90 = peta tanpa kutub, diisi alat olah)
Unduh sumber: https://planetary.s3.amazonaws.com/web/assets/pictures/20180511_jupiter_map_css_plus_juno_bj.jpg
Lebar 8192 (bukan 14400): 14400 x 7200 butuh sekitar 550 MB memori GPU dengan mipmap, 8192 x 4096 sekitar 180 MB.
Keluaran: window.JUPITER_MAP = { w, h, jpg: <base64> } dengan h = w / 2, baris pertama = kutub utara (butuh pillow dan numpy)."""
import base64, io, sys
import numpy as np
from PIL import Image, ImageFilter
Image.MAX_IMAGE_PIXELS = None
src = sys.argv[1]; w = int(sys.argv[2]) if len(sys.argv) > 2 else 8192; q = int(sys.argv[3]) if len(sys.argv) > 3 else 84; lat = float(sys.argv[4]) if len(sys.argv) > 4 else 90.0
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
if pad > 0:
    a[:nE] = fade_edge(a[:nE], tU, nE); a[-nE:] = fade_edge(a[-nE:][::-1], tD, nE)[::-1]
def cap(row_block, n, tgt):                                         # isi kutub: baris tepi, diburamkan horizontal, memudar ke warna acuan
    r = row_block.mean(axis=0, keepdims=True)
    strip = Image.fromarray(np.repeat(r, 8, axis=0).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(40))
    r = np.asarray(strip).astype(np.float32)[4:5]
    k = np.linspace(0, 1, n)[:, None, None]
    return r * (1 - 0.5 * k) + tgt * 0.5 * k
cu = cap(a[:6], top, tU)[::-1] if top > 0 else a[:0]; cd = cap(a[-6:], bot, tD) if bot > 0 else a[:0]
full = np.concatenate([cu, a, cd], axis=0).clip(0, 255).astype(np.uint8)
im2 = Image.fromarray(full)
buf = io.BytesIO(); im2.save(buf, 'JPEG', quality=q, optimize=True)
b = base64.b64encode(buf.getvalue()).decode()
tag = '%dk' % round(w / 1024)                                      # 4096 -> 4k, 8192 -> 8k, 14400 -> 14k
out = 'experiences/cooper-station/assets/jupiter-%s.data.js' % tag
open(out, 'w').write('/* Peta global Jupiter: Bjorn Jonsson (data NASA/JPL Cassini ISS dan Juno JunoCam), The Planetary Society, diolah tools/siapkan_jupiter.py */\nwindow.JUPITER_MAP = { w: %d, h: %d, jpg: "%s" };\n' % (w, h, b))
im2.resize((900, 450)).save('/tmp/jupiter_prev.png')
print(out, w, h, len(buf.getvalue()) // 1024, 'KB jpeg', len(b) // 1024, 'KB base64; baris data', hs, 'kutub', top, bot)
