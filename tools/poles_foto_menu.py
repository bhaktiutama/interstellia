"""Poles foto menu (docs/app/menu/asli/*.webp -> docs/app/menu/*.webp): lebih jernih, dramatis, sinematik.
Hanya olahan nada dan warna per piksel (clarity, penajaman, kurva S, split toning, bloom, vinyet, bahu highlight, butiran).
Tidak ada objek yang ditambah, dihapus, atau dipindah; ukuran gambar sama persis, jadi penanda SPOTS tetap valid.
Pakai: python tools/poles_foto_menu.py [nama ...]   (butuh: pip install numpy pillow)
Atur angka di PRESET lalu jalankan ulang; foto asli tidak pernah ditimpa."""
import pathlib, sys
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'docs/app/menu/asli'
DST = ROOT / 'docs/app/menu'

# Parameter per foto. clarity = kontras lokal (radius px), sharp = penajaman halus, curve = kekuatan kurva S,
# bp = titik hitam, sh / hl = warna bayangan / highlight (RGB, ditambahkan), sat = saturasi,
# bloom = (ambang, kekuatan, radius px), vig = kekuatan vinyet, grain = simpangan derau butiran,
# protect = 1 melindungi nada terang dari kurva S, knee = awal bahu highlight (lebih tinggi = cincin terang di langit pucat Millar tetap terpisah dari langit).
PRESET = {
    'cooper':    dict(clarity=(0.55, 22), sharp=0.55, curve=0.32, bp=0.025, sh=(-0.012, 0.000, 0.022), hl=(0.030, 0.014, -0.018),
                      sat=1.12, bloom=(0.82, 0.22, 14), vig=0.34, grain=0.010, knee=0.78),
    'gargantua': dict(clarity=(0.45, 26), sharp=0.40, curve=0.36, bp=0.030, sh=(-0.010, 0.004, 0.016), hl=(0.028, 0.010, -0.026),
                      sat=1.10, bloom=(0.72, 0.32, 18), vig=0.40, grain=0.010, knee=0.78),
    'millar':    dict(clarity=(0.60, 26), sharp=0.45, curve=0.30, bp=0.035, sh=(-0.020, 0.006, 0.022), hl=(0.012, 0.008, -0.004),
                      sat=0.96, bloom=(0.90, 0.12, 16), vig=0.28, grain=0.005, knee=0.90, protect=1),
}


def box(a, r):
    """Blur kotak radius r di dua sumbu (cumsum), tepi dipantulkan."""
    if r < 1:
        return a
    for ax in (0, 1):
        p = np.pad(a, [(r + 1, r) if i == ax else (0, 0) for i in range(a.ndim)], mode='reflect')
        c = np.cumsum(p, axis=ax)
        n = a.shape[ax]
        hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=ax)
        lo = np.take(c, np.arange(0, n), axis=ax)
        a = (hi - lo) / (2 * r + 1)
    return a


def blur(a, sigma):
    """Mendekati blur Gaussian dengan tiga blur kotak."""
    r = max(1, int(round(sigma * 0.85)))
    return box(box(box(a, r), r), r)


def lum(rgb):
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def poles(rgb, P, seed):
    L = lum(rgb)
    # 1. clarity: kontras lokal di nada tengah
    k, r = P['clarity']
    mid = np.clip(4 * L * (1 - L), 0, 1)
    rgb = rgb + (k * (L - blur(L, r)) * mid)[..., None]
    # 2. penajaman halus berambang (artefak kompresi kecil tidak ikut ditajamkan)
    L = lum(rgb)
    d = L - blur(L, 1)
    rgb = rgb + (P['sharp'] * d * smooth(0.004, 0.02, np.abs(d)))[..., None]
    # 3. titik hitam + kurva S
    rgb = np.clip((rgb - P['bp']) / (1 - P['bp']), 0, 1)
    s = rgb * rgb * (3 - 2 * rgb)
    # protect: kurva S tidak menyentuh nada terang (kurva S menekan beda antar highlight, cincin di langit pucat jadi pudar)
    rgb = rgb + P['curve'] * (s - rgb) * (1 - P.get('protect', 0) * smooth(0.55, 0.85, rgb))
    # 4. split toning + saturasi
    L = lum(rgb)[..., None]
    rgb = rgb + (1 - L) ** 2 * np.array(P['sh']) + L ** 2 * np.array(P['hl'])
    L = lum(rgb)[..., None]
    rgb = L + (rgb - L) * P['sat']
    # 5. bloom halus dari highlight
    thr, kb, rb = P['bloom']
    hi = np.clip(rgb - thr, 0, None)
    rgb = rgb + kb * np.stack([blur(hi[..., i], rb) for i in range(3)], -1)
    # 6. vinyet lembut
    h, w = L.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    rr = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2)) / np.sqrt(2)
    rgb = rgb * (1 - P['vig'] * smooth(0.45, 1.0, rr))[..., None]
    # 7. bahu highlight: nilai di atas knee ditekan lembut menuju 1 (tidak terpotong rata putih)
    k0 = P['knee']
    over = np.clip(rgb - k0, 0, None)
    rgb = np.where(rgb > k0, k0 + (1 - k0) * (1 - np.exp(-over / (1 - k0))), rgb)
    # 8. butiran film (benih tetap, hasil bisa diulang), paling kuat di nada tengah
    L = lum(np.clip(rgb, 0, 1))
    g = np.random.default_rng(seed).normal(0, P['grain'], L.shape) * (0.35 + np.clip(4 * L * (1 - L), 0, 1))
    rgb = rgb + g[..., None] * (1 - smooth(0.9, 1.0, rgb))
    return np.clip(rgb, 0, 1)


def stat(rgb):
    L = lum(rgb)
    clip = np.mean((rgb >= 0.999).any(-1) | (rgb <= 0.001).all(-1)) * 100
    return f'rata {L.mean():.3f}  p1 {np.percentile(L, 1):.3f}  p99 {np.percentile(L, 99):.3f}  terpotong {clip:.2f}%'


def main():
    names = sys.argv[1:] or list(PRESET)
    for n in names:
        im = Image.open(SRC / f'{n}.webp').convert('RGB')
        a = np.asarray(im, dtype=np.float32) / 255
        b = poles(a, PRESET[n], seed=sum(map(ord, n)))
        out = Image.fromarray((b * 255 + 0.5).astype(np.uint8))
        assert out.size == im.size
        out.save(DST / f'{n}.webp', quality=90, method=6)
        print(f'{n}: {im.size[0]}x{im.size[1]}')
        print(f'  asli   {stat(a)}')
        print(f'  poles  {stat(b)}')


if __name__ == '__main__':
    main()
