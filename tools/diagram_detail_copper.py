# Bangkitkan diagram SVG untuk halaman detail Copper Corn Station (konsep docs/cooper-station/detail/konsep-halaman-detail.md).
# Pakai: python tools/diagram_detail_copper.py  (menulis docs/cooper-station/detail/gambar/cc-*.svg)
# Label English saja (satu gambar untuk kedua bahasa). Angka dari R 1.000 m, g 9,81 m/s^2 (sama dengan CONFIG);
# lintasan dan grafik dihitung dari rumus, bukan digambar tangan. Tanpa library luar.
import math, os, random, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'cooper-station', 'detail', 'gambar')
g = 9.81; R = 1000.0; W = math.sqrt(g / R)
W_, H_ = 960, 540
CU, CU2, TE, OR, INK, MU = '#d9bd62', '#f4dc8a', '#8fd3dc', '#f3a55a', '#e8ecf2', '#9aa2ae'
FONT = 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif'


# ------------------------------------------------------------------ dasar
def f1(v): return f'{v:.1f}'

def t(x, y, s, size=13, fill=INK, anchor='start', weight=400, extra=''):
    return f'<text x="{f1(x)}" y="{f1(y)}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" {extra}>{s}</text>'

def pts(P): return ' '.join(f'{f1(x)},{f1(y)}' for x, y in P)

def path(P): return 'M' + ' L'.join(f'{f1(x)} {f1(y)}' for x, y in P)

def tw(s, size): return len(s) * size * 0.56     # perkiraan lebar teks

def stars(seed, n=140, box=(0, 0, W_, H_), op=1.0):
    r = random.Random(seed); o = []
    for _ in range(n):
        x = box[0] + r.random() * box[2]; y = box[1] + r.random() * box[3]
        rr = 0.35 + r.random() ** 3 * 1.3
        o.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="{rr:.2f}" fill="#fff" opacity="{op * (0.15 + 0.6 * r.random()):.2f}"/>')
    return ''.join(o)

def defs(extra=''):
    return f'''<defs>
<radialGradient id="bg" cx="0.5" cy="0.35" r="0.85"><stop offset="0" stop-color="#141b29"/><stop offset="0.6" stop-color="#0a0e16"/><stop offset="1" stop-color="#05070b"/></radialGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="glow2" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="10"/></filter>
<filter id="shadow" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#000" flood-opacity="0.55"/></filter>
<linearGradient id="card" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity="0.08"/><stop offset="1" stop-color="#ffffff" stop-opacity="0.02"/></linearGradient>
<linearGradient id="bldg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#9aa6b8"/><stop offset="0.55" stop-color="#6c7789"/><stop offset="1" stop-color="#3c4452"/></linearGradient>
<linearGradient id="ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3d5a2c"/><stop offset="0.25" stop-color="#2a3a22"/><stop offset="1" stop-color="#11160f"/></linearGradient>
<marker id="a" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1L9 5L0 9z" fill="{INK}"/></marker>
<marker id="ac" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1L9 5L0 9z" fill="{CU}"/></marker>
<marker id="at" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1L9 5L0 9z" fill="{TE}"/></marker>
<marker id="ao" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1L9 5L0 9z" fill="{OR}"/></marker>
<marker id="tick" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M5 0V10" stroke="{INK}" stroke-width="1.6"/></marker>
{extra}
</defs>'''

def doc(no, title, sub, body, extra_defs='', h=H_, star_seed=None, star_op=0.55):
    s = stars(star_seed if star_seed is not None else no * 7, 150, (0, 0, W_, h), star_op)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W_} {h}" width="{W_}" height="{h}" font-family="{FONT}">
{defs(extra_defs)}
<rect width="{W_}" height="{h}" rx="18" fill="url(#bg)"/>
<g>{s}</g>
<rect x="0.5" y="0.5" width="{W_ - 1}" height="{h - 1}" rx="18" fill="none" stroke="#ffffff" stroke-opacity="0.08"/>
<rect x="32" y="30" width="22" height="3" rx="1.5" fill="{CU}"/>
{t(62, 35, f'COPPER CORN STATION · {no:02d}', 11, CU, 'start', 600, 'letter-spacing="2.6"')}
{t(32, 68, title, 25, INK, 'start', 650)}
{t(32, 92, sub, 13.5, MU)}
{body}
</svg>
'''

def pill(x, y, s, size=12.5, col=INK, anchor='start', bg='rgba(10,14,22,0.82)', bd='rgba(255,255,255,0.16)'):
    w = tw(s, size) + 20; h = size + 12
    x0 = x if anchor == 'start' else (x - w if anchor == 'end' else x - w / 2)
    return (f'<rect x="{f1(x0)}" y="{f1(y - h / 2)}" width="{f1(w)}" height="{f1(h)}" rx="{f1(h / 2)}" fill="{bg}" stroke="{bd}"/>'
            + t(x0 + w / 2, y + size * 0.36, s, size, col, 'middle', 500))

def callout(px, py, lx, ly, s, col=INK, size=12.5, anchor='start'):
    return (f'<path d="M{f1(px)} {f1(py)} L{f1(lx)} {f1(ly)}" stroke="{col}" stroke-opacity="0.55" stroke-width="1.2" fill="none"/>'
            f'<circle cx="{f1(px)}" cy="{f1(py)}" r="3" fill="{col}"/>' + pill(lx, ly, s, size, col, anchor))

def card(x, y, w, num, unit, lab, col=CU, h=66):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="url(#card)" stroke="#ffffff" stroke-opacity="0.10"/>'
            f'<text x="{x + 16}" y="{y + 34}" font-size="25" font-weight="700" fill="{col}">{num}<tspan font-size="13" font-weight="500" fill="{INK}" dx="4">{unit}</tspan></text>'
            + t(x + 16, y + 54, lab, 11.5, MU))

def foot(y, s):
    return f'<line x1="32" y1="{y - 18}" x2="{W_ - 32}" y2="{y - 18}" stroke="#ffffff" stroke-opacity="0.08"/>' + t(32, y, s, 12.5, MU)

def person(x, y, ang, s=1.0, col=INK, op=1.0):
    # orang kecil berdiri di (x, y), kepala ke arah ang (radian, arah layar)
    ux, uy = math.cos(ang), math.sin(ang); px, py = -uy, ux
    hip = (x + ux * 7 * s, y + uy * 7 * s); sh = (x + ux * 13 * s, y + uy * 13 * s)
    o = [f'<g opacity="{op}" stroke="{col}" stroke-width="{1.6 * s:.2f}" stroke-linecap="round" fill="none">',
         f'<path d="M{f1(x + px * 3 * s)} {f1(y + py * 3 * s)} L{f1(hip[0])} {f1(hip[1])} L{f1(x - px * 3 * s)} {f1(y - py * 3 * s)}"/>',
         f'<path d="M{f1(hip[0])} {f1(hip[1])} L{f1(sh[0])} {f1(sh[1])}"/>',
         f'<path d="M{f1(sh[0] + px * 3.5 * s - ux * 4 * s)} {f1(sh[1] + py * 3.5 * s - uy * 4 * s)} L{f1(sh[0])} {f1(sh[1])} L{f1(sh[0] - px * 3.5 * s - ux * 4 * s)} {f1(sh[1] - py * 3.5 * s - uy * 4 * s)}"/></g>',
         f'<circle cx="{f1(x + ux * 17 * s)}" cy="{f1(y + uy * 17 * s)}" r="{3.3 * s:.2f}" fill="{col}" opacity="{op}"/>']
    return ''.join(o)

def land_ring(cx, cy, r, seed, step=2.2, hmax=15):
    """Dinding dalam silinder: blok kota (menghadap sumbu), ladang, sungai, taman."""
    rnd = random.Random(seed); o = []
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r + 7}" fill="none" stroke="#1b2016" stroke-width="14"/>')
    a = 0.0
    while a < 360:
        A = math.radians(a); zone = (a + 20) % 120
        ux, uy = math.cos(A), math.sin(A); px, py = -uy, ux
        if zone < 55:      # kota
            hgt = 3 + rnd.random() ** 2 * hmax; wdt = 2.4 + rnd.random() * 2.2
            c = rnd.choice(['#aab4c4', '#8794a8', '#c3cad6', '#76839a', '#9fa9b8'])
        elif zone < 62:    # sungai
            hgt, wdt, c = 1.6, step * 1.6, '#3f86b8'
        elif zone < 75:    # taman: pohon bulat
            o.append(f'<circle cx="{f1(cx + ux * (r - 3.5))}" cy="{f1(cy + uy * (r - 3.5))}" r="{2.6 + rnd.random() * 1.6:.2f}" fill="{rnd.choice(["#4f7a35", "#5e8c3c", "#3f6a2c"])}"/>')
            a += step; continue
        else:              # ladang
            hgt, wdt = 1.8, step * 2.0
            c = rnd.choice(['#c9a24a', '#8fa83e', '#6f8f3a', '#d4b35a', '#a7b54a'])
        b0 = (cx + ux * r, cy + uy * r); b1 = (cx + ux * (r - hgt), cy + uy * (r - hgt))
        poly = [(b0[0] + px * wdt / 2, b0[1] + py * wdt / 2), (b0[0] - px * wdt / 2, b0[1] - py * wdt / 2),
                (b1[0] - px * wdt / 2, b1[1] - py * wdt / 2), (b1[0] + px * wdt / 2, b1[1] + py * wdt / 2)]
        o.append(f'<polygon points="{pts(poly)}" fill="{c}"/>')
        a += step
    return ''.join(o)

def arc_pts(cx, cy, r, a0, a1, n=60):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]

def spin_arrows(cx, cy, r, col=CU, n=2, span=50):
    o = []
    for k in range(n):
        a0 = math.radians(200 + k * 180); a1 = a0 + math.radians(span)
        o.append(f'<path d="{path(arc_pts(cx, cy, r, a0, a1))}" fill="none" stroke="{col}" stroke-width="2.4" marker-end="url(#ac)" filter="url(#glow)"/>')
    return ''.join(o)

def tower(x, base, top, w=14, col='url(#bldg)', deck=None):
    """Menara ikon bertingkat mundur (tampak samping), tegak di (x, base) sampai y top."""
    H = base - top; o = []
    tiers = [(1.0, 0.0, 0.42), (0.78, 0.42, 0.7), (0.56, 0.7, 0.9), (0.3, 0.9, 1.0)]
    for fw, h0, h1 in tiers:
        ww = w * fw
        o.append(f'<rect x="{f1(x - ww / 2)}" y="{f1(base - H * h1)}" width="{f1(ww)}" height="{f1(H * (h1 - h0) + 0.5)}" fill="{col}"/>')
    o.append(f'<line x1="{f1(x)}" y1="{f1(top)}" x2="{f1(x)}" y2="{f1(top - H * 0.08)}" stroke="#c3cad6" stroke-width="1.2"/>')
    o.append(f'<circle cx="{f1(x)}" cy="{f1(top - H * 0.08)}" r="1.8" fill="#ff5a4a" filter="url(#glow)"/>')
    return ''.join(o)

def cloud(x, y, s=1.0, op=0.35, col='#c9d3e2'):
    return (f'<g opacity="{op}" filter="url(#blur)"><ellipse cx="{f1(x)}" cy="{f1(y)}" rx="{f1(40 * s)}" ry="{f1(13 * s)}" fill="{col}"/>'
            f'<ellipse cx="{f1(x + 22 * s)}" cy="{f1(y - 7 * s)}" rx="{f1(24 * s)}" ry="{f1(12 * s)}" fill="{col}"/></g>')

def axes(x0, y0, w, h, xt, yt, xmax, ymax, xlab, ylab, xfmt=str, yfmt=str, right=None):
    o = []
    for v in xt:
        X = x0 + v / xmax * w
        o.append(f'<line x1="{f1(X)}" y1="{y0}" x2="{f1(X)}" y2="{y0 + h}" stroke="#fff" stroke-opacity="0.06"/>')
        o.append(t(X, y0 + h + 20, xfmt(v), 11.5, MU, 'middle'))
    for v in yt:
        Y = y0 + h - v / ymax * h
        o.append(f'<line x1="{x0}" y1="{f1(Y)}" x2="{x0 + w}" y2="{f1(Y)}" stroke="#fff" stroke-opacity="0.06"/>')
        o.append(t(x0 - 10, Y + 4, yfmt(v), 11.5, MU, 'end'))
    o.append(f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="#fff" stroke-opacity="0.25"/>')
    o.append(t(x0 + w / 2, y0 + h + 42, xlab, 12, MU, 'middle'))
    o.append(f'<text transform="translate({x0 - 46} {y0 + h / 2}) rotate(-90)" font-size="12" fill="{MU}" text-anchor="middle">{ylab}</text>')
    return ''.join(o)

def mapper(x0, y0, w, h, xmax, ymax, ymin=0.0):
    return lambda x, y: (x0 + x / xmax * w, y0 + h - (y - ymin) / (ymax - ymin) * h)

files = {}

# ================================================================== 01 stasiun sekilas
ex = f'''<radialGradient id="air" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fff2c2" stop-opacity="0.55"/><stop offset="0.25" stop-color="#6d8fb3" stop-opacity="0.32"/><stop offset="1" stop-color="#16263a" stop-opacity="0.9"/></radialGradient>
<linearGradient id="hull" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a4558"/><stop offset="0.35" stop-color="#202938"/><stop offset="0.65" stop-color="#2c3a2a"/><stop offset="0.85" stop-color="#4a6236"/><stop offset="1" stop-color="#1a2216"/></linearGradient>
<linearGradient id="capB" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffe7a8" stop-opacity="0.95"/><stop offset="1" stop-color="#f3a55a" stop-opacity="0.35"/></linearGradient>
<linearGradient id="beam" x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd98a" stop-opacity="0.55"/><stop offset="1" stop-color="#ffd98a" stop-opacity="0.04"/></linearGradient>
<linearGradient id="sunl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff6d6" stop-opacity="0.5"/><stop offset="1" stop-color="#fff6d6"/></linearGradient>
<radialGradient id="sun" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fff8e0"/><stop offset="0.3" stop-color="#ffd27a" stop-opacity="0.9"/><stop offset="1" stop-color="#f3a55a" stop-opacity="0"/></radialGradient>'''
b = []
cx, cy, r = 200, 275, 112
b.append(f'<circle cx="{cx}" cy="{cy}" r="{r + 26}" fill="none" stroke="#ffffff" stroke-opacity="0.05" stroke-width="1"/>')
b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#air)"/>')
b.append(land_ring(cx, cy, r, 11))
b.append(f'<circle cx="{cx}" cy="{cy}" r="{r + 15}" fill="none" stroke="{CU}" stroke-width="2.5" filter="url(#glow)"/>')
for k in range(12):   # rusuk struktur luar
    A = k * math.pi / 6
    b.append(f'<line x1="{f1(cx + (r + 15) * math.cos(A))}" y1="{f1(cy + (r + 15) * math.sin(A))}" x2="{f1(cx + (r + 21) * math.cos(A))}" y2="{f1(cy + (r + 21) * math.sin(A))}" stroke="{CU}" stroke-opacity="0.6" stroke-width="2"/>')
b.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="#fff6d6" filter="url(#glow2)"/>')
b.append(spin_arrows(cx, cy, r + 34))
for ang in (100, 220, 330):
    A = math.radians(ang)
    b.append(person(cx + (r - 18) * math.cos(A), cy + (r - 18) * math.sin(A), A + math.pi, 0.95, '#ffffff'))
Ar = math.radians(-38)
b.append(f'<line x1="{cx}" y1="{cy}" x2="{f1(cx + (r - 2) * math.cos(Ar))}" y2="{f1(cy + (r - 2) * math.sin(Ar))}" stroke="{INK}" stroke-width="1.3" stroke-dasharray="5 4" marker-end="url(#a)"/>')
b.append(pill(cx + 18, cy - 46, 'R = 1,000 m', 12.5, INK))
b.append(pill(cx - 10, cy + 22, 'sunline', 11.5, '#fff6d6', 'end'))
A0 = math.radians(90)
b.append(f'<line x1="{f1(cx + 22)}" y1="{f1(cy + r + 30)}" x2="{f1(cx - 60)}" y2="{f1(cy + r + 30)}" stroke="{TE}" stroke-width="2.5" marker-end="url(#at)" filter="url(#glow)"/>')
b.append(t(cx + 30, cy + r + 34, '99.05 m/s', 12.5, TE, 'start', 600))
b.append(t(40, 120, 'CROSS-SECTION', 11, MU, 'start', 600, 'letter-spacing="2"'))
# tampak samping berperspektif (berskala: 8.000 m = 440 px)
x0, x1, ay = 470, 910, 290; sc = (x1 - x0) / 8000; ry = R * sc; rx = ry * 0.36
b.append(t((x0 + x1) / 2, 132, 'SIDE VIEW · TO SCALE', 11, MU, 'middle', 600, 'letter-spacing="2"'))
b.append(f'<path d="M{x0} {f1(ay - ry)} L{x1} {f1(ay - ry)} A{f1(rx)} {f1(ry)} 0 0 1 {x1} {f1(ay + ry)} L{x0} {f1(ay + ry)} A{f1(rx)} {f1(ry)} 0 0 1 {x0} {f1(ay - ry)} Z" fill="url(#hull)" stroke="{CU}" stroke-width="1.6"/>')
for k in range(1, 8):   # cincin struktur tiap 1 km
    xk = x0 + k * 1000 * sc
    b.append(f'<path d="M{f1(xk)} {f1(ay - ry)} A{f1(rx)} {f1(ry)} 0 0 1 {f1(xk)} {f1(ay + ry)}" fill="none" stroke="{CU}" stroke-opacity="0.28"/>')
reach = 2 * R / math.tan(math.radians(25)); fx = x1 - reach * sc
b.append(f'<polygon points="{pts([(x1 + 4, ay - ry + 6), (x1 + 4, ay + ry * 0.2), (fx + 70, ay + ry), (fx, ay + ry)])}" fill="url(#beam)"/>')
b.append(f'<rect x="{x0}" y="{f1(ay - 1.6)}" width="{x1 - x0}" height="3.2" fill="url(#sunl)" filter="url(#glow)"/>')
b.append(f'<ellipse cx="{x0}" cy="{ay}" rx="{f1(rx)}" ry="{f1(ry)}" fill="#1c2431" stroke="{CU}" stroke-width="1.6"/>')
b.append(f'<rect x="{x0 - 46}" y="{ay - 5}" width="46" height="10" rx="2" fill="#5d6778"/><rect x="{x0 - 64}" y="{ay - 14}" width="20" height="28" rx="3" fill="#8794a8"/>')
b.append(f'<ellipse cx="{x1}" cy="{ay}" rx="{f1(rx)}" ry="{f1(ry)}" fill="url(#capB)" filter="url(#glow)"/>')
b.append(f'<circle cx="{x1 + 14}" cy="{f1(ay - ry - 40)}" r="30" fill="url(#sun)"/>')
b.append(f'<line x1="{x1 + 20}" y1="{f1(ay - ry - 28)}" x2="{f1(x1 - 6)}" y2="{f1(ay - ry - 28 + 26 * math.tan(math.radians(25)))}" stroke="{OR}" stroke-width="2" marker-end="url(#ao)"/>')
b.append(f'<line x1="{x0}" y1="{f1(ay - ry - 26)}" x2="{x1}" y2="{f1(ay - ry - 26)}" stroke="{INK}" stroke-opacity="0.7" marker-start="url(#a)" marker-end="url(#a)"/>')
b.append(pill((x0 + x1) / 2 - 20, ay - ry - 26, 'L = 8,000 m', 12.5, INK, 'middle'))
b.append(f'<line x1="{f1(fx)}" y1="{f1(ay + ry + 18)}" x2="{x1}" y2="{f1(ay + ry + 18)}" stroke="{OR}" marker-start="url(#tick)" marker-end="url(#tick)"/>')
b.append(t((fx + x1) / 2 - 30, ay + ry + 34, 'sunlit reach about 4.3 km', 12, OR, 'middle', 500))
b.append(callout(x0 - 54, ay + 14, x0 - 70, ay + ry + 58, 'End cap A: lift, hub, despun dock', INK, 12))
b.append(callout(x1 + 8, ay + 30, x1 + 18, ay + ry + 88, 'End cap B: glass, Sun at 25°', CU2, 12, 'end'))
cw = (W_ - 64 - 4 * 12) / 5
for i, (n, u, l, c) in enumerate([('1,000', 'm', 'radius', CU), ('8,000', 'm', 'length', CU), ('63.4', 's', 'one turn, 0.946 rpm', CU),
                                   ('99.05', 'm/s', 'floor speed', TE), ('37.57', 'h', 'orbit around Saturn', OR)]):
    b.append(card(32 + i * (cw + 12), 448, cw, n, u, l, c))
files['cc-01-station.svg'] = doc(1, 'The station at a glance', 'An O\'Neill cylinder orbiting Saturn: city, fields and river on the inside wall', '\n'.join(b), ex)

# ================================================================== 02 gravitasi dari putaran
ex = f'''<radialGradient id="air" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fff2c2" stop-opacity="0.45"/><stop offset="0.3" stop-color="#5a7ea6" stop-opacity="0.25"/><stop offset="1" stop-color="#16263a" stop-opacity="0.85"/></radialGradient>
<linearGradient id="wedge" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{CU}" stop-opacity="0.55"/><stop offset="1" stop-color="{TE}" stop-opacity="0.15"/></linearGradient>
<linearGradient id="edge" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{CU}"/><stop offset="1" stop-color="{TE}"/></linearGradient>
<linearGradient id="down" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0.05"/><stop offset="1" stop-color="#fff" stop-opacity="0.95"/></linearGradient>'''
b = []
cx, cy, r = 220, 300, 138
b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#air)"/>')
b.append(land_ring(cx, cy, r, 5))
b.append(f'<circle cx="{cx}" cy="{cy}" r="{r + 15}" fill="none" stroke="{CU}" stroke-width="2.5" filter="url(#glow)"/>')
b.append(spin_arrows(cx, cy, r + 32))
for k in range(12):
    A = k * math.pi / 6 + math.pi / 12
    xA, yA = cx + 34 * math.cos(A), cy + 34 * math.sin(A); xB, yB = cx + (r - 26) * math.cos(A), cy + (r - 26) * math.sin(A)
    b.append(f'<line x1="{f1(xA)}" y1="{f1(yA)}" x2="{f1(xB)}" y2="{f1(yB)}" stroke="#ffffff" stroke-opacity="0.8" stroke-width="2" marker-end="url(#a)"/>')
b.append(f'<circle cx="{cx}" cy="{cy}" r="6" fill="#fff6d6" filter="url(#glow2)"/>')
b.append(pill(cx, cy + r + 52, '"down" = away from the axis, everywhere', 12, INK, 'middle'))
b.append(t(cx, 132, 'NO PULL, ONLY A PUSH', 11, MU, 'middle', 600, 'letter-spacing="2"'))
# tangga gravitasi: tinggi 0 di lantai (bawah) sampai 1.000 m di sumbu (atas)
fy, ty_, lx0, wmax = 470, 140, 560, 300
k = (fy - ty_) / R
Y = lambda h: fy - h * k
b.append(f'<polygon points="{pts([(lx0, fy), (lx0 + wmax, fy), (lx0, ty_)])}" fill="url(#wedge)"/>')
b.append(f'<line x1="{lx0 + wmax}" y1="{fy}" x2="{lx0}" y2="{ty_}" stroke="url(#edge)" stroke-width="3" filter="url(#glow)"/>')
for i in range(1, 10):
    h = i * 100; w = wmax * (R - h) / R
    b.append(f'<line x1="{lx0}" y1="{f1(Y(h))}" x2="{f1(lx0 + w)}" y2="{f1(Y(h))}" stroke="#ffffff" stroke-opacity="0.12"/>')
for h in (0, 250, 500, 750, 1000):
    b.append(t(lx0 - 108, Y(h) + 4, f'{h:,} m', 11.5, MU, 'end'))
b.append(f'<rect x="{lx0 - 100}" y="{fy}" width="{wmax + 140}" height="16" fill="url(#ground)"/>')
b.append(f'<line x1="{lx0 - 100}" y1="{fy}" x2="{lx0 + wmax + 40}" y2="{fy}" stroke="{CU}" stroke-width="2" filter="url(#glow)"/>')
b.append(f'<line x1="{lx0 - 100}" y1="{ty_}" x2="{lx0 + wmax + 40}" y2="{ty_}" stroke="#fff6d6" stroke-width="2" stroke-dasharray="2 5" filter="url(#glow)"/>')
b.append(tower(lx0 - 64, fy, Y(221), 20))
b.append(f'<line x1="{lx0 - 82}" y1="{f1(Y(175))}" x2="{lx0 - 46}" y2="{f1(Y(175))}" stroke="{CU2}" stroke-width="2"/>')
b.append(cloud(lx0 - 50, Y(330), 0.8, 0.5)); b.append(cloud(lx0 + 150, Y(420), 0.9, 0.35))
b.append(f'<line x1="{lx0 - 24}" y1="{fy}" x2="{lx0 - 24}" y2="{ty_ + 6}" stroke="{TE}" stroke-width="1.6" stroke-dasharray="4 4"/>')
b.append(t(lx0 - 18, Y(640), 'lift', 11, TE))
b.append(person(lx0 + 40, ty_ + 26, math.radians(-60), 0.9, TE))
for h, lab, col in ((0, 'floor: 1 g', CU), (175, 'tower deck 175 m: 0.825 g', CU2), (500, 'halfway: 0.5 g', INK), (1000, 'axis hub: 0 g, you float', TE)):
    w = wmax * (R - h) / R
    px = lx0 + w; py = Y(h)
    if h == 1000: b.append(callout(lx0 + 2, py + 2, lx0 + 70, py + 30, lab, col, 12)); continue
    if h in (0, 175): b.append(callout(px, py, px - 36, py - 24, lab, col, 12, 'end')); continue
    b.append(callout(px, py, px + 26, py - 14, lab, col, 12))
b.append(pill(W_ - 32, 128, 'g(h) = ω² (R - h)', 13, CU2, 'end'))
files['cc-02-spin-gravity.svg'] = doc(2, 'Gravity from spin', 'The floor pushes you toward the axis; the higher you climb, the less it pushes', '\n'.join(b), ex)

# ================================================================== 03 Coriolis: bola dari dek
h0 = 176.5                                   # dek 175 m + tangan 1,5 m (PHYS.handH)
r0 = R - h0; v0 = W * r0
tf = math.sqrt(R * R - r0 * r0) / v0
ang_b = math.atan2(math.sqrt(R * R - r0 * r0), r0)
miss = (W * tf - ang_b) * R
N = 6
ex = '''<linearGradient id="earth" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4b6b33"/><stop offset="0.15" stop-color="#2e3b24"/><stop offset="1" stop-color="#0d110b" stop-opacity="0"/></linearGradient>
<linearGradient id="ballg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#8fd3dc"/></linearGradient>'''
b = []
# panel kiri: kerangka inersia, potongan silinder diperbesar (pusat di atas kanvas)
b.append(f'<rect x="32" y="116" width="436" height="330" rx="14" fill="url(#card)" stroke="#fff" stroke-opacity="0.08"/>')
b.append(t(50, 142, 'SEEN FROM OUTSIDE · INERTIAL', 11, MU, 'start', 600, 'letter-spacing="2"'))
s = 0.40; cx, cy = 140, -55
def P(a, rad): return cx + rad * s * math.sin(a), cy + rad * s * math.cos(a)
A0, A1 = math.radians(-14), math.radians(52)
b.append('<clipPath id="pl"><rect x="32" y="116" width="436" height="330" rx="14"/></clipPath><g clip-path="url(#pl)">')
inner = [P(A0 + (A1 - A0) * i / 80, R) for i in range(81)]
lower = [P(A1 - (A1 - A0) * i / 80, R + 70) for i in range(81)]
b.append(f'<polygon points="{pts(inner + lower)}" fill="url(#earth)"/>')
b.append(f'<path d="{path(inner)}" fill="none" stroke="{CU}" stroke-width="2.5" filter="url(#glow)"/>')
b.append(f'<path d="{path([P(a, R + 22) for a in [W * tf * i / 40 for i in range(41)]])}" fill="none" stroke="{OR}" stroke-width="2" marker-end="url(#ao)"/>')
for kk in range(N + 1):
    tt = tf * kk / N; a = W * tt; op = 0.18 + 0.82 * kk / N
    base, top = P(a, R), P(a, R - 175)
    nx, ny = math.cos(a), -math.sin(a)
    b.append(f'<line x1="{f1(base[0])}" y1="{f1(base[1])}" x2="{f1(top[0])}" y2="{f1(top[1])}" stroke="#9aa6b8" stroke-width="{9 if kk == N else 7}" opacity="{op:.2f}"/>')
    bx, by = cx + v0 * tt * s, cy + r0 * s
    b.append(f'<line x1="{f1(top[0])}" y1="{f1(top[1])}" x2="{f1(bx)}" y2="{f1(by)}" stroke="#fff" stroke-opacity="{0.10 * op:.2f}" stroke-dasharray="2 3"/>')
    b.append(f'<circle cx="{f1(bx)}" cy="{f1(by)}" r="{5 if kk == N else 4}" fill="url(#ballg)" opacity="{op:.2f}" filter="url(#glow)"/>')
b.append(f'<line x1="{f1(cx)}" y1="{f1(cy + r0 * s)}" x2="{f1(cx + v0 * tf * s)}" y2="{f1(cy + r0 * s)}" stroke="{TE}" stroke-width="1.6" stroke-dasharray="6 5"/>')
ib, fb = P(ang_b, R), P(W * tf, R)
b.append(f'<path d="{path([P(ang_b + (W * tf - ang_b) * i / 10, R + 9) for i in range(11)])}" stroke="{INK}" stroke-width="1.4" fill="none" marker-start="url(#tick)" marker-end="url(#tick)"/>')
b.append('</g>')
b.append(callout(cx + v0 * tf * s * 0.35, cy + r0 * s, 70, 182, 'ball keeps 81.6 m/s, flies straight', TE, 12))
b.append(callout(*P(W * tf * 0.55, R + 22), 230, 414, 'floor below moves 99.05 m/s', OR, 12))
b.append(callout(fb[0] + 6, fb[1] - 4, 330, 228, 'tower base got ahead', INK, 12))
# panel kanan: kerangka berputar, lintasan sebenarnya
b.append(f'<rect x="492" y="116" width="436" height="330" rx="14" fill="url(#card)" stroke="#fff" stroke-opacity="0.08"/>')
b.append(t(510, 142, 'SEEN ON THE STATION · ROTATING', 11, MU, 'start', 600, 'letter-spacing="2"'))
fl, txx, ks = 404, 830, 1.30
def Q(x, y): return txx + x * ks, fl - y * ks
curve = []
for i in range(81):
    tt = tf * i / 80; xb, yb = v0 * tt, r0
    rb = math.hypot(xb, yb); ab = math.atan2(xb, yb)
    curve.append(((ab - W * tt) * R, R - rb))
b.append(f'<rect x="494" y="{fl}" width="432" height="40" fill="url(#earth)"/>')
rr_ = random.Random(3)
for i in range(30):
    x = 500 + i * 14.5; hgt = 4 + rr_.random() * 14
    if abs(x - txx) < 20: continue
    b.append(f'<rect x="{f1(x)}" y="{f1(fl - hgt)}" width="10" height="{f1(hgt)}" fill="#59657a" opacity="0.55"/>')
b.append(f'<line x1="494" y1="{fl}" x2="926" y2="{fl}" stroke="{CU}" stroke-width="2.5" filter="url(#glow)"/>')
b.append(tower(txx + 2, fl, Q(0, 221)[1], 26))
b.append(f'<line x1="{txx - 22}" y1="{f1(Q(0, 175)[1])}" x2="{txx + 26}" y2="{f1(Q(0, 175)[1])}" stroke="{CU2}" stroke-width="2.5"/>')
b.append(person(txx - 14, Q(0, 175)[1], -math.pi / 2, 0.8, '#ffffff'))
b.append(f'<line x1="{f1(Q(-4, h0)[0])}" y1="{f1(Q(0, h0)[1])}" x2="{f1(Q(-4, 0)[0])}" y2="{fl}" stroke="#ffffff" stroke-opacity="0.35" stroke-dasharray="3 5"/>')
b.append(f'<path d="{path([Q(x - 4, y) for x, y in curve])}" fill="none" stroke="{TE}" stroke-width="2.4" filter="url(#glow)"/>')
for kk in range(N + 1):
    x, y = curve[int(round(kk / N * 80))]; X, Y_ = Q(x - 4, y); op = 0.25 + 0.75 * kk / N
    b.append(f'<circle cx="{f1(X)}" cy="{f1(Y_)}" r="{5 if kk == N else 4}" fill="url(#ballg)" opacity="{op:.2f}"/>')
lx = Q(-miss - 4, 0)[0]
b.append(f'<line x1="{f1(lx)}" y1="{fl + 22}" x2="{f1(Q(-4, 0)[0])}" y2="{fl + 22}" stroke="{INK}" marker-start="url(#tick)" marker-end="url(#tick)"/>')
b.append(f'<text x="615" y="{fl - 150}" font-size="34" font-weight="700" fill="{TE}" text-anchor="middle">{miss:.1f}<tspan font-size="14" fill="{INK}" dx="4">m</tspan></text>')
b.append(t(615, fl - 130, 'lands behind the tower', 12, INK, 'middle'))
b.append(t(615, fl - 114, f'{h0} m drop · {tf:.2f} s', 11.5, MU, 'middle'))
b.append(f'<line x1="520" y1="168" x2="590" y2="168" stroke="{OR}" stroke-width="2" marker-end="url(#ao)"/>')
b.append(t(598, 172, 'spin', 12, OR, 'start', 600))
b.append(foot(H_ - 30, 'One fall, two views. Outside, the ball goes straight and the floor overtakes it. Ghosts are 1.16 s apart.'))
files['cc-03-coriolis-drop.svg'] = doc(3, 'Why a dropped ball misses the tower', 'Coriolis: anything that falls toward the floor lags behind the spin', '\n'.join(b), ex)

# ================================================================== 04 air mancur dan hujan
vj = 10.0; tl = 2 * vj / g
jet = [(W * (vj * tt * tt - g * tt ** 3 / 3), vj * tt - g * tt * tt / 2) for tt in [tl * i / 80 for i in range(81)]]
land = jet[-1][0]
vt = 7.0; vl = 2 * W * vt * vt / g; deg = math.degrees(math.atan(vl / vt))
ex = f'''<linearGradient id="jet" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#bfeef4"/><stop offset="1" stop-color="#ffffff"/></linearGradient>
<linearGradient id="pool" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a8fb4" stop-opacity="0.9"/><stop offset="1" stop-color="#103347"/></linearGradient>
<radialGradient id="lamp" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ffe2a0" stop-opacity="0.55"/><stop offset="1" stop-color="#ffe2a0" stop-opacity="0"/></radialGradient>
<linearGradient id="sky2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a3442" stop-opacity="0.9"/><stop offset="1" stop-color="#0b0f16" stop-opacity="0"/></linearGradient>'''
b = []
b.append(f'<rect x="32" y="116" width="436" height="300" rx="14" fill="url(#card)" stroke="#fff" stroke-opacity="0.08"/>')
b.append(t(50, 142, 'FOUNTAIN · GOING UP', 11, MU, 'start', 600, 'letter-spacing="2"'))
kz = 38.0; nx, ny = 190, 372
def J(x, y): return nx + x * kz, ny - y * kz
b.append(f'<ellipse cx="{nx + 30}" cy="{ny + 8}" rx="150" ry="22" fill="url(#pool)" stroke="#9aa6b8" stroke-width="3"/>')
b.append(f'<line x1="{nx}" y1="{ny}" x2="{nx}" y2="{f1(J(0, 5.6)[1])}" stroke="#fff" stroke-opacity="0.35" stroke-dasharray="3 5"/>')
b.append(t(nx - 8, J(0, 4.6)[1], 'straight up?', 11.5, MU, 'end'))
b.append(f'<path d="{path([J(x, y) for x, y in jet])}" fill="none" stroke="url(#jet)" stroke-width="5" stroke-linecap="round" filter="url(#glow)"/>')
rd = random.Random(9)
for i in range(26):
    q = jet[int(rd.random() * 80)]; X, Y_ = J(q[0], q[1])
    b.append(f'<circle cx="{f1(X + rd.uniform(-7, 7))}" cy="{f1(Y_ + rd.uniform(-7, 7))}" r="{rd.uniform(0.8, 2):.1f}" fill="#d9f6fb" opacity="0.8"/>')
lx_, ly_ = J(land, 0)
for i in range(3):
    b.append(f'<ellipse cx="{f1(lx_)}" cy="{f1(ly_ + 2)}" rx="{8 + i * 9}" ry="{2.5 + i * 2.6}" fill="none" stroke="#d9f6fb" stroke-opacity="{0.7 - i * 0.2:.1f}"/>')
b.append(f'<line x1="{nx}" y1="{ny + 44}" x2="{f1(lx_)}" y2="{ny + 44}" stroke="{INK}" marker-start="url(#tick)" marker-end="url(#tick)"/>')
b.append(f'<rect x="{f1(lx_ + 12)}" y="{ny - 104}" width="190" height="78" rx="10" fill="#0a0e16" fill-opacity="0.7"/>')
b.append(f'<text x="{f1(lx_ + 22)}" y="{ny - 70}" font-size="32" font-weight="700" fill="{TE}">{land:.2f}<tspan font-size="14" fill="{INK}" dx="4">m</tspan></text>')
b.append(t(lx_ + 22, ny - 50, 'lands ahead, with the spin', 12, INK))
b.append(t(lx_ + 22, ny - 34, '10 m/s jet · peak 5.1 m · 2.04 s', 11.5, MU))
b.append(f'<line x1="300" y1="170" x2="370" y2="170" stroke="{OR}" stroke-width="2" marker-end="url(#ao)"/><text x="378" y="174" font-size="12" fill="{OR}" font-weight="600">spin</text>')
# hujan
b.append(f'<rect x="492" y="116" width="436" height="300" rx="14" fill="url(#card)" stroke="#fff" stroke-opacity="0.08"/>')
b.append(t(510, 142, 'RAIN · COMING DOWN', 11, MU, 'start', 600, 'letter-spacing="2"'))
b.append(f'<rect x="494" y="150" width="432" height="90" fill="url(#sky2)"/>')
for x, y, s_ in ((560, 168, 1.3), (700, 160, 1.6), (850, 172, 1.2), (630, 186, 1.0)):
    b.append(cloud(x, y, s_, 0.55, '#7a8596'))
lpx, gy = 790, 388
b.append(f'<circle cx="{lpx - 20}" cy="230" r="90" fill="url(#lamp)"/>')
rr2 = random.Random(4); sl = vl / vt
for i in range(70):
    x = 505 + rr2.random() * 410; y = 195 + rr2.random() * 175; Ls = 14 + rr2.random() * 16
    near = math.hypot(x - (lpx - 20), y - 230) < 80
    b.append(f'<line x1="{f1(x)}" y1="{f1(y)}" x2="{f1(x - Ls * sl)}" y2="{f1(y + Ls)}" stroke="{"#ffe9b8" if near else TE}" stroke-opacity="{0.9 if near else 0.55}" stroke-width="1.3" stroke-linecap="round"/>')
b.append(f'<rect x="494" y="{gy}" width="432" height="26" fill="#0f1720"/><line x1="494" y1="{gy}" x2="926" y2="{gy}" stroke="{CU}" stroke-width="2" filter="url(#glow)"/>')
for x in (560, 680, 860):
    b.append(f'<ellipse cx="{x}" cy="{gy + 10}" rx="34" ry="4" fill="#5d7f9b" opacity="0.45"/>')
b.append(f'<rect x="{lpx - 2}" y="226" width="4" height="{gy - 226}" fill="#2a3240"/><path d="M{lpx} 228 Q{lpx} 220 {lpx - 18} 222" stroke="#2a3240" stroke-width="4" fill="none"/><ellipse cx="{lpx - 20}" cy="226" rx="7" ry="3" fill="#ffe9b8" filter="url(#glow2)"/>')
ax_, ay_ = 560, 262; Lr = 110
b.append(f'<line x1="{ax_}" y1="{ay_}" x2="{ax_}" y2="{ay_ + Lr}" stroke="#fff" stroke-opacity="0.6" stroke-dasharray="3 5"/>')
b.append(f'<line x1="{ax_}" y1="{ay_}" x2="{f1(ax_ - Lr * sl)}" y2="{ay_ + Lr}" stroke="{TE}" stroke-width="3" marker-end="url(#at)" filter="url(#glow)"/>')
b.append(f'<path d="M{ax_} {ay_ + 60} A60 60 0 0 1 {f1(ax_ - 60 * math.sin(math.radians(deg)))} {f1(ay_ + 60 * math.cos(math.radians(deg)))}" fill="none" stroke="{INK}" stroke-width="1.4"/>')
b.append(f'<rect x="{ax_ + 4}" y="{ay_ + 36}" width="206" height="78" rx="10" fill="#0a0e16" fill-opacity="0.75"/>')
b.append(f'<text x="{ax_ + 12}" y="{ay_ + 70}" font-size="32" font-weight="700" fill="{TE}">{deg:.1f}<tspan font-size="14" fill="{INK}" dx="2">°</tspan></text>')
b.append(t(ax_ + 12, ay_ + 90, 'tilt with no wind', 12, INK))
b.append(t(ax_ + 12, ay_ + 106, 'falls 7 m/s, drifts 0.99 m/s back', 11.5, MU))
b.append(f'<line x1="760" y1="170" x2="830" y2="170" stroke="{OR}" stroke-width="2" marker-end="url(#ao)"/><text x="838" y="174" font-size="12" fill="{OR}" font-weight="600">spin</text>')
# aturan praktis
b.append(f'<rect x="32" y="432" width="896" height="74" rx="14" fill="url(#card)" stroke="#fff" stroke-opacity="0.08"/>')
b.append(t(52, 462, 'RULE OF THUMB', 11, CU, 'start', 600, 'letter-spacing="2"'))
b.append(t(52, 488, 'Up, toward the axis', 15, INK, 'start', 600)); b.append(t(212, 488, 'gets ahead (with the spin)', 15, TE))
b.append(t(500, 488, 'Down, toward the floor', 15, INK, 'start', 600)); b.append(t(680, 488, 'falls behind (against it)', 15, OR))
b.append(f'<line x1="480" y1="448" x2="480" y2="494" stroke="#fff" stroke-opacity="0.1"/>')
files['cc-04-fountain-rain.svg'] = doc(4, 'Fountain and rain: Coriolis both ways', 'The same effect, opposite direction of travel', '\n'.join(b), ex)

# ================================================================== 05 berat saat bergerak
ex = f'''<linearGradient id="up" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CU}" stop-opacity="0.45"/><stop offset="1" stop-color="{CU}" stop-opacity="0.02"/></linearGradient>
<linearGradient id="dn" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{TE}" stop-opacity="0.45"/><stop offset="1" stop-color="{TE}" stop-opacity="0.02"/></linearGradient>
<linearGradient id="road" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2a313d"/><stop offset="1" stop-color="#151a22"/></linearGradient>'''
b = []
X0, Y0, CW, CH = 96, 132, 520, 300
f = mapper(X0, Y0, CW, CH, 150, 2.2)
b.append(axes(X0, Y0, CW, CH, [0, 30, 60, 90, 120, 150], [0, 0.5, 1.0, 1.5, 2.0], 150, 2.2, 'speed along the ring road (km/h)', 'felt weight (g)', str, lambda v: f'{v:g}'))
gp = lambda v: (W * R + v / 3.6) ** 2 / R / g
gm = lambda v: (W * R - v / 3.6) ** 2 / R / g
pro = [f(v, gp(v)) for v in range(0, 151, 3)]
ret = [f(v, gm(v)) for v in range(0, 151, 3)]
one = [f(v, 1) for v in range(0, 151, 3)]
b.append(f'<polygon points="{pts(pro + one[::-1])}" fill="url(#up)"/>')
b.append(f'<polygon points="{pts(one + ret[::-1])}" fill="url(#dn)"/>')
b.append(f'<line x1="{X0}" y1="{f1(f(0, 1)[1])}" x2="{X0 + CW}" y2="{f1(f(0, 1)[1])}" stroke="#fff" stroke-opacity="0.45" stroke-dasharray="4 5"/>')
b.append(t(X0 + CW - 4, f(0, 1)[1] - 8, 'standing still: 1 g', 11.5, MU, 'end'))
b.append(f'<path d="{path(pro)}" fill="none" stroke="{CU}" stroke-width="3" filter="url(#glow)"/>')
b.append(f'<path d="{path(ret)}" fill="none" stroke="{TE}" stroke-width="3" filter="url(#glow)"/>')
for v in (50, 100):
    for fn, c in ((gp, CU), (gm, TE)):
        x, y = f(v, fn(v)); b.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="3.5" fill="{c}"/>')
        b.append(t(x, y + (-10 if c == CU else 18), f'{fn(v):.2f}', 11, c, 'middle'))
for fn, c in ((gp, CU), (gm, TE)):
    x, y = f(150, fn(150))
    b.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="11" fill="{c}" opacity="0.18"/><circle cx="{f1(x)}" cy="{f1(y)}" r="5" fill="{c}" filter="url(#glow)"/>')
b.append(t(f(60, 1.68)[0], f(60, 1.68)[1], 'with the spin: heavier', 13, CU, 'start', 600, 'transform="rotate(-12 %s %s)"' % (f1(f(60, 1.68)[0]), f1(f(60, 1.68)[1]))))
b.append(t(f(40, 0.55)[0], f(40, 0.55)[1], 'against the spin: lighter', 13, TE, 'start', 600, 'transform="rotate(9 %s %s)"' % (f1(f(40, 0.55)[0]), f1(f(40, 0.55)[1]))))
# sisipan jalan cincin
icx, icy, ir = 778, 232, 70
b.append(f'<circle cx="{icx}" cy="{icy}" r="{ir + 12}" fill="none" stroke="url(#road)" stroke-width="22"/>')
b.append(f'<circle cx="{icx}" cy="{icy}" r="{ir + 12}" fill="none" stroke="#fff" stroke-opacity="0.3" stroke-dasharray="6 8"/>')
b.append(f'<circle cx="{icx}" cy="{icy}" r="{ir - 6}" fill="none" stroke="{CU}" stroke-opacity="0.25"/>')
b.append(f'<circle cx="{icx}" cy="{icy}" r="5" fill="#fff6d6" filter="url(#glow2)"/>')
b.append(f'<path d="{path(arc_pts(icx, icy, ir + 32, math.radians(-150), math.radians(-40)))}" fill="none" stroke="{CU}" stroke-width="3" marker-end="url(#ac)" filter="url(#glow)"/>')
b.append(f'<path d="{path(arc_pts(icx, icy, ir + 32, math.radians(140), math.radians(30)))}" fill="none" stroke="{TE}" stroke-width="3" marker-end="url(#at)" filter="url(#glow)"/>')
b.append(f'<path d="{path(arc_pts(icx, icy, ir - 20, math.radians(200), math.radians(260)))}" fill="none" stroke="{OR}" stroke-width="2" marker-end="url(#ao)"/>')
b.append(t(icx, icy + 4 - 22, 'station spin', 10.5, OR, 'middle'))
b.append(t(icx, 128, 'RING ROAD, TOP DOWN', 11, MU, 'middle', 600, 'letter-spacing="2"'))
b.append(card(660, 348, 128, '2.02', 'g', 'with the spin', CU))
b.append(card(800, 348, 128, '0.34', 'g', 'against the spin', TE))
b.append(pill(660, 446, "g' = (ωR + v)² / R", 12.5, CU2))
b.append(foot(H_ - 30, 'Motorbike in sport mode at 150 km/h. At 356.6 km/h against the spin you would match the floor speed and weigh nothing.'))
files['cc-05-moving-weight.svg'] = doc(5, 'Your weight depends on where you are going', 'Moving with the spin adds to your circling speed; moving against it takes it away', '\n'.join(b), ex)

# ================================================================== 06 lift ke sumbu
d = R - 6; acc = 1.0; vm = 20.0; ta = vm / acc; tc = (d - vm * ta) / vm; T = 2 * ta + tc
def hv(tt):
    if tt < ta: return acc * tt * tt / 2, acc * tt
    if tt < ta + tc: return vm * ta / 2 + vm * (tt - ta), vm
    u = T - tt; return d - acc * u * u / 2, acc * u
ex = f'''<linearGradient id="wall" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1a212c"/><stop offset="0.5" stop-color="#2a3442"/><stop offset="1" stop-color="#171d27"/></linearGradient>
<linearGradient id="shaft" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{CU}"/><stop offset="1" stop-color="{TE}"/></linearGradient>
<linearGradient id="spd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{TE}" stop-opacity="0.45"/><stop offset="1" stop-color="{TE}" stop-opacity="0.03"/></linearGradient>'''
b = []
fy, hy = 470, 140; kk_ = (fy - hy) / d
Yh = lambda h: fy - h * kk_
sx = 150
b.append(f'<rect x="{sx - 70}" y="{hy}" width="140" height="{fy - hy}" fill="url(#wall)" rx="6"/>')
for i in range(1, 10):
    b.append(f'<line x1="{sx - 70}" y1="{f1(Yh(i * 100))}" x2="{sx + 70}" y2="{f1(Yh(i * 100))}" stroke="#fff" stroke-opacity="0.05"/>')
b.append(f'<line x1="{sx}" y1="{fy}" x2="{sx}" y2="{hy}" stroke="url(#shaft)" stroke-width="3" filter="url(#glow)"/>')
b.append(f'<rect x="20" y="{fy}" width="{sx + 130}" height="18" fill="url(#ground)"/><line x1="20" y1="{fy}" x2="{sx + 150}" y2="{fy}" stroke="{CU}" stroke-width="2" filter="url(#glow)"/>')
rr3 = random.Random(2)
for i in range(9):
    x = 30 + i * 13; hh = 6 + rr3.random() * 26
    b.append(f'<rect x="{x}" y="{f1(fy - hh)}" width="10" height="{f1(hh)}" fill="#59657a" opacity="0.6"/>')
b.append(f'<ellipse cx="{sx}" cy="{hy - 4}" rx="86" ry="16" fill="none" stroke="{TE}" stroke-width="3" filter="url(#glow)"/>')
b.append(f'<ellipse cx="{sx}" cy="{hy - 4}" rx="60" ry="9" fill="#fff6d6" opacity="0.15" filter="url(#blur)"/>')
b.append(person(sx + 54, hy + 20, math.radians(-130), 0.9, TE))
b.append(t(sx + 78, hy + 26, 'hub: 0 g', 12, TE, 'start', 600))
for tt in (0, 10, 20, 35, 50, 60, T):
    h, v = hv(tt); y = Yh(h); op = 0.3 + 0.7 * tt / T
    b.append(f'<rect x="{sx - 9}" y="{f1(y - 13)}" width="18" height="13" rx="3" fill="{INK}" opacity="{op:.2f}"/>')
for tt in (20, 50):
    h, v = hv(tt); y = Yh(h)
    b.append(callout(sx + 10, y - 6, sx + 30, y - 6, f'{tt:.0f} s · {h:.0f} m · {(R - h) / R:.2f} g', INK, 11.5))
hc, _ = hv(35); yc = Yh(hc)
b.append(f'<line x1="{sx - 12}" y1="{f1(yc - 6)}" x2="{sx - 62}" y2="{f1(yc - 6)}" stroke="{OR}" stroke-width="2.5" marker-end="url(#ao)" filter="url(#glow)"/>')
b.append(t(sx - 66, yc - 16, '0.40 g', 12, OR, 'end', 700))
# grafik kecepatan + gravitasi
X0, Y0, CW, CH = 400, 140, 480, 300
fs = mapper(X0, Y0, CW, CH, 70, 22); fg = mapper(X0, Y0, CW, CH, 70, 1.1)
for x0_, x1_, lab, c in ((0, ta, 'speed up', '#ffffff'), (ta, ta + tc, 'cruise 20 m/s', TE), (ta + tc, T, 'brake', '#ffffff')):
    b.append(f'<rect x="{f1(fs(x0_, 0)[0])}" y="{Y0}" width="{f1(fs(x1_, 0)[0] - fs(x0_, 0)[0])}" height="{CH}" fill="{c}" opacity="0.03"/>')
    b.append(t((fs(x0_, 0)[0] + fs(x1_, 0)[0]) / 2, Y0 + 18, lab, 11.5, MU, 'middle', 600))
b.append(axes(X0, Y0, CW, CH, [0, 10, 20, 30, 40, 50, 60, 70], [0, 5, 10, 15, 20], 70, 22, 'time in the lift (s)', 'lift speed (m/s)', str, str))
for gv in (0, 0.5, 1.0):
    b.append(t(X0 + CW + 10, fg(0, gv)[1] + 4, f'{gv:g} g', 11.5, CU))
sp = [fs(T * i / 140, hv(T * i / 140)[1]) for i in range(141)]
b.append(f'<polygon points="{pts(sp + [fs(T, 0), fs(0, 0)])}" fill="url(#spd)"/>')
b.append(f'<path d="{path(sp)}" fill="none" stroke="{TE}" stroke-width="2.5"/>')
gl = [fg(T * i / 140, (R - hv(T * i / 140)[0]) / R) for i in range(141)]
b.append(f'<path d="{path(gl)}" fill="none" stroke="{CU}" stroke-width="3" filter="url(#glow)"/>')
xe, ye = fg(T, 0.006)
b.append(f'<circle cx="{f1(xe)}" cy="{f1(ye)}" r="10" fill="{CU}" opacity="0.2"/><circle cx="{f1(xe)}" cy="{f1(ye)}" r="4.5" fill="{CU}"/>')
b.append(t(fg(1, 0.84)[0], fg(1, 0.84)[1], 'felt gravity', 12.5, CU, 'start', 600))
b.append(t(fs(28, 17.5)[0], fs(28, 17.5)[1], 'speed', 12.5, TE, 'start', 600))
b.append(f'<text x="{X0 + CW}" y="{Y0 - 14}" font-size="28" font-weight="700" fill="{CU}" text-anchor="end">{T:.1f}<tspan font-size="13" fill="{INK}" dx="3">s</tspan><tspan font-size="13" fill="{MU}" dx="10">for</tspan><tspan font-size="28" fill="{CU}" dx="8">994</tspan><tspan font-size="13" fill="{INK}" dx="3">m</tspan></text>')
b.append(foot(H_ - 30, 'Orange: real physics not yet in the game. At 20 m/s the cabin wall pushes you sideways with 2ωv = 0.40 g. Shift = 5x speed.'))
files['cc-06-lift.svg'] = doc(6, 'Riding the lift to zero g', 'From the floor of end cap A up to the hub on the axis', '\n'.join(b), ex)

# ================================================================== 07 orbit dan gerhana
P_orb = 2 * math.pi * math.sqrt((2.6e8) ** 3 / 3.7931e16) / 3600
ex = f'''<radialGradient id="sun" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fff8e0"/><stop offset="0.25" stop-color="#ffd27a" stop-opacity="0.9"/><stop offset="1" stop-color="#f3a55a" stop-opacity="0"/></radialGradient>
<linearGradient id="bands" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d9c08e"/><stop offset="0.18" stop-color="#c8a873"/><stop offset="0.3" stop-color="#e6d3a8"/><stop offset="0.45" stop-color="#b8925e"/><stop offset="0.55" stop-color="#e2c895"/><stop offset="0.7" stop-color="#c49f69"/><stop offset="0.85" stop-color="#dcc497"/><stop offset="1" stop-color="#b08a58"/></linearGradient>
<linearGradient id="night" x1="0" y1="0" x2="1" y2="0"><stop offset="0.35" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.85"/></linearGradient>
<linearGradient id="umbra" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000" stop-opacity="0.85"/><stop offset="1" stop-color="#000" stop-opacity="0.1"/></linearGradient>
<linearGradient id="ringg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f1e2bf"/><stop offset="0.5" stop-color="#cdb487"/><stop offset="1" stop-color="#5a4d38"/></linearGradient>
<linearGradient id="tl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{OR}" stop-opacity="0.25"/><stop offset="1" stop-color="{CU}" stop-opacity="0.35"/></linearGradient>
<clipPath id="planet"><circle cx="440" cy="290" r="{60.268 * 0.66:.1f}"/></clipPath>'''
b = []
cx, cy, k = 440, 290, 0.66
rs, ro = 60.268 * k, 260 * k
b.append(f'<circle cx="-40" cy="{cy}" r="190" fill="url(#sun)"/>')
for i in range(6):
    y = cy - 125 + i * 50
    b.append(f'<line x1="70" y1="{y}" x2="170" y2="{y}" stroke="{OR}" stroke-opacity="0.6" stroke-width="1.6" marker-end="url(#ao)"/>')
b.append(t(70, cy - 145, 'SUNLIGHT', 11, OR, 'start', 600, 'letter-spacing="2"'))
b.append(f'<rect x="{cx}" y="{f1(cy - rs)}" width="{W_ - cx}" height="{f1(2 * rs)}" fill="url(#umbra)"/>')
b.append(f'<circle cx="{cx}" cy="{cy}" r="{f1(ro)}" fill="none" stroke="#fff" stroke-opacity="0.18" stroke-width="6" filter="url(#blur)"/>')
b.append(f'<circle cx="{cx}" cy="{cy}" r="{f1(ro)}" fill="none" stroke="#fff" stroke-opacity="0.45" stroke-dasharray="3 6"/>')
ring = lambda half: f'<path d="M{f1(cx - rs * 2.25)} {cy} A{f1(rs * 2.25)} {f1(rs * 0.42)} 0 0 {half} {f1(cx + rs * 2.25)} {cy}" fill="none" stroke="url(#ringg)" stroke-width="7" transform="rotate(-14 {cx} {cy})" opacity="0.9"/>'
b.append(ring(1))
b.append(f'<g clip-path="url(#planet)"><rect x="{f1(cx - rs)}" y="{f1(cy - rs)}" width="{f1(2 * rs)}" height="{f1(2 * rs)}" fill="url(#bands)" transform="rotate(-14 {cx} {cy})"/><rect x="{f1(cx - rs)}" y="{f1(cy - rs)}" width="{f1(2 * rs)}" height="{f1(2 * rs)}" fill="url(#night)"/></g>')
b.append(ring(0))
half = math.asin(60.268 / 260)
b.append(f'<path d="{path(arc_pts(cx, cy, ro, -half, half, 30))}" fill="none" stroke="{OR}" stroke-width="6" stroke-linecap="round" filter="url(#glow)"/>')
b.append(callout(cx + ro + 4, cy + 8, cx + ro + 30, cy + 112, 'eclipse arc', OR, 12))
b.append(f'<path d="{path(arc_pts(cx, cy, ro + 18, math.radians(-150), math.radians(-105)))}" fill="none" stroke="{INK}" stroke-opacity="0.7" stroke-width="1.6" marker-end="url(#a)"/>')
sa = math.radians(-130); st = (cx + ro * math.cos(sa), cy + ro * math.sin(sa))
b.append(f'<g transform="translate({f1(st[0])} {f1(st[1])}) rotate(-40)" filter="url(#glow)"><rect x="-13" y="-4" width="26" height="8" rx="2" fill="{CU}"/><ellipse cx="13" cy="0" rx="2" ry="4" fill="#fff3c4"/></g>')
b.append(callout(st[0] + 6, st[1] - 6, st[0] + 40, st[1] - 26, 'Copper Corn Station · 260,000 km out', CU, 12))
b.append(t(cx, cy + rs + 30, 'Saturn', 12, INK, 'middle', 600))
b.append(card(712, 130, 216, '37.57', 'h', 'one orbit', INK))
b.append(card(712, 208, 216, '2.78', 'h', 'in Saturn\'s shadow per orbit', OR))
b.append(t(712, 306, 'During the eclipse the sunline', 12.5, INK)); b.append(t(712, 324, 'fades and Saturn\'s limb glows.', 12.5, INK))
b.append(t(712, 348, 'Press I to jump there.', 12.5, CU2, 'start', 600))
# garis waktu satu orbit
tx0, tx1, tyy = 32, 928, 488; ecl0 = tx0 + (tx1 - tx0) * 0.6; ecl1 = ecl0 + (tx1 - tx0) * 2.78 / P_orb
b.append(f'<rect x="{tx0}" y="{tyy - 8}" width="{tx1 - tx0}" height="16" rx="8" fill="url(#tl)"/>')
b.append(f'<rect x="{f1(ecl0)}" y="{tyy - 8}" width="{f1(ecl1 - ecl0)}" height="16" fill="#05070b" stroke="{OR}" stroke-width="1.5"/>')
b.append(t(tx0, tyy - 16, 'ONE ORBIT · 37.57 h', 11, MU, 'start', 600, 'letter-spacing="2"'))
b.append(t((ecl0 + ecl1) / 2, tyy - 16, 'eclipse 2.78 h', 11.5, OR, 'middle', 600))
b.append(t(tx1, tyy - 16, 'sunlight 34.79 h', 11.5, CU, 'end'))
files['cc-07-orbit-eclipse.svg'] = doc(7, 'Orbit and Saturn eclipse', 'Top view of the orbit plane, to scale. The Sun lies in this plane, 25° from the station axis', '\n'.join(b), ex)

# ================================================================== 08 di balik layar: bayangan silinder dibuka
ex = f'''<pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="7" stroke="#ff6b5a" stroke-opacity="0.55" stroke-width="2"/></pattern>
<linearGradient id="rays" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd98a" stop-opacity="0.5"/><stop offset="1" stop-color="#ffd98a" stop-opacity="0"/></linearGradient>
<clipPath id="boxL"><rect x="70" y="300" width="340" height="110"/></clipPath>'''
b = []
b.append(f'<rect x="32" y="116" width="400" height="340" rx="14" fill="url(#card)" stroke="#fff" stroke-opacity="0.08"/>')
b.append(t(50, 142, 'THE PROBLEM', 11, '#ff8a7a', 'start', 600, 'letter-spacing="2"'))
ccx, ccy, cr = 240, 40, 340
A0, A1 = math.radians(62), math.radians(118)
fl_ = arc_pts(ccx, ccy, cr, A0, A1, 80)
b.append(f'<polygon points="{pts(fl_ + arc_pts(ccx, ccy, cr + 60, A1, A0, 80))}" fill="url(#ground)"/>')
for i in range(8):
    x = 90 + i * 44
    b.append(f'<line x1="{x}" y1="160" x2="{x}" y2="300" stroke="url(#rays)" stroke-width="2"/>')
b.append(f'<g clip-path="url(#boxL)"><polygon points="{pts(arc_pts(ccx, ccy, cr, A0 - 0.2, A1 + 0.2, 80) + [(470, 420), (20, 420)])}" fill="url(#hatch)"/></g>')
rb = random.Random(6)
for i in range(9):
    A = A0 + (A1 - A0) * (i + 0.5) / 9; hgt = 22 + rb.random() * 34
    ux, uy = math.cos(A), math.sin(A); px, py = -uy, ux
    base = (ccx + ux * cr, ccy + uy * cr); top = (ccx + ux * (cr - hgt), ccy + uy * (cr - hgt)); w_ = 7
    b.append(f'<polygon points="{pts([(base[0] + px * w_, base[1] + py * w_), (base[0] - px * w_, base[1] - py * w_), (top[0] - px * w_, top[1] - py * w_), (top[0] + px * w_, top[1] + py * w_)])}" fill="url(#bldg)"/>')
    sh = (ccx + math.cos(A + 0.04) * cr, ccy + math.sin(A + 0.04) * cr)
    b.append(f'<line x1="{f1(base[0])}" y1="{f1(base[1])}" x2="{f1(sh[0])}" y2="{f1(sh[1])}" stroke="#000" stroke-opacity="0.6" stroke-width="3"/>')
b.append(f'<path d="{path(fl_)}" fill="none" stroke="{CU}" stroke-width="2.5" filter="url(#glow)"/>')
b.append(f'<rect x="70" y="300" width="340" height="110" fill="none" stroke="{TE}" stroke-width="2" stroke-dasharray="7 5"/>')
b.append(callout(380, 392, 300, 436, 'texels wasted inside the rock', '#ff8a7a', 11.5))
b.append(callout(95, 300, 112, 254, 'walls leave the box', '#ff8a7a', 11.5))
b.append(pill(400, 286, 'flat shadow box', 11.5, TE, 'end'))
# panah tengah
b.append(f'<line x1="446" y1="300" x2="524" y2="300" stroke="{INK}" stroke-width="2.5" marker-end="url(#a)" filter="url(#glow)"/>')
b.append(f'<text x="485" y="286" font-size="12" fill="{CU2}" text-anchor="middle" font-weight="700" font-family="ui-monospace, Menlo, Consolas, monospace">shUnroll()</text>')
b.append(f'<rect x="538" y="116" width="390" height="340" rx="14" fill="url(#card)" stroke="#fff" stroke-opacity="0.08"/>')
b.append(t(556, 142, 'THE TRICK', 11, '#7fe0a0', 'start', 600, 'letter-spacing="2"'))
fx0, fx1, fyy = 558, 908, 380
b.append(f'<rect x="{fx0}" y="{fyy}" width="{fx1 - fx0}" height="50" fill="url(#ground)"/>')
for i in range(8):
    x = 576 + i * 44
    b.append(f'<line x1="{x}" y1="160" x2="{x}" y2="{fyy - 40}" stroke="url(#rays)" stroke-width="2"/>')
rb = random.Random(6)
for i in range(9):
    x = fx0 + 22 + i * 38; hgt = 22 + rb.random() * 34
    b.append(f'<rect x="{x - 7}" y="{f1(fyy - hgt)}" width="14" height="{f1(hgt)}" fill="url(#bldg)"/>')
    b.append(f'<line x1="{x + 7}" y1="{fyy}" x2="{x + 20}" y2="{fyy}" stroke="#000" stroke-opacity="0.6" stroke-width="3"/>')
b.append(f'<line x1="{fx0}" y1="{fyy}" x2="{fx1}" y2="{fyy}" stroke="{CU}" stroke-width="2.5" filter="url(#glow)"/>')
b.append(f'<rect x="{fx0 + 4}" y="{fyy - 64}" width="{fx1 - fx0 - 8}" height="74" fill="{TE}" fill-opacity="0.06" stroke="{TE}" stroke-width="2" stroke-dasharray="7 5" filter="url(#glow)"/>')
b.append(pill(fx1 - 4, fyy - 84, 'box hugs the floor everywhere', 11.5, '#7fe0a0', 'end'))
b.append(pill((fx0 + fx1) / 2, 214, '(θ, r)  →  (s = θR, h = R - r)', 13, CU2, 'middle'))
b.append(t((fx0 + fx1) / 2, 246, 'bend the world flat before rendering depth', 12, MU, 'middle'))
b.append(foot(H_ - 30, 'The depth pass and every receiving shader use the same unrolling, so shadows land in the right place on the curved wall.'))
files['cc-08-unrolled-shadow.svg'] = doc(8, 'Behind the scenes: unrolling the cylinder', 'Shadow maps are rendered in unrolled coordinates (stage 18b-3)', '\n'.join(b), ex)

# ================================================================== 09 di balik layar: dua scene
ex = f'''<radialGradient id="sun" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fff8e0"/><stop offset="0.3" stop-color="#ffd27a" stop-opacity="0.8"/><stop offset="1" stop-color="#f3a55a" stop-opacity="0"/></radialGradient>
<linearGradient id="bands" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d9c08e"/><stop offset="0.3" stop-color="#e6d3a8"/><stop offset="0.5" stop-color="#b8925e"/><stop offset="0.7" stop-color="#e2c895"/><stop offset="1" stop-color="#b08a58"/></linearGradient>
<linearGradient id="planeA" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1b2232" stop-opacity="0.95"/><stop offset="1" stop-color="#0b0f18" stop-opacity="0.95"/></linearGradient>
<linearGradient id="planeB" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1d2a22" stop-opacity="0.96"/><stop offset="1" stop-color="#0e1410" stop-opacity="0.96"/></linearGradient>
<linearGradient id="hull" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a4558"/><stop offset="0.6" stop-color="#2c3a2a"/><stop offset="1" stop-color="#4a6236"/></linearGradient>
<clipPath id="pa"><polygon points="90,130 470,130 430,330 50,330"/></clipPath>'''
b = []
A = [(90, 130), (470, 130), (430, 330), (50, 330)]
b.append(f'<polygon points="{pts(A)}" fill="url(#planeA)" stroke="{OR}" stroke-width="1.6" filter="url(#shadow)"/>')
b.append(f'<g clip-path="url(#pa)">{stars(21, 70, (50, 130, 420, 200), 0.9)}<circle cx="120" cy="300" r="70" fill="url(#sun)"/>'
         f'<circle cx="320" cy="225" r="34" fill="url(#bands)"/><ellipse cx="320" cy="225" rx="70" ry="12" fill="none" stroke="#e6d3a8" stroke-width="4" opacity="0.8" transform="rotate(-14 320 225)"/></g>')
b.append(t(100, 156, '1 · farScene', 15, OR, 'start', 700))
b.append(t(100, 176, '1 unit = 1,000 km', 12.5, INK))
B = [(330, 250), (720, 250), (680, 440), (290, 440)]
b.append(f'<polygon points="{pts(B)}" fill="url(#planeB)" stroke="{CU}" stroke-width="1.6" filter="url(#shadow)"/>')
cx0, cx1, cyy, ry_ = 380, 640, 360, 34
b.append(f'<path d="M{cx0} {cyy - ry_} L{cx1} {cyy - ry_} A12 {ry_} 0 0 1 {cx1} {cyy + ry_} L{cx0} {cyy + ry_} A12 {ry_} 0 0 1 {cx0} {cyy - ry_} Z" fill="url(#hull)" stroke="{CU}" stroke-width="1.4"/>')
b.append(f'<rect x="{cx0}" y="{cyy - 1.2}" width="{cx1 - cx0}" height="2.4" fill="#fff6d6" filter="url(#glow)"/>')
b.append(f'<ellipse cx="{cx1}" cy="{cyy}" rx="12" ry="{ry_}" fill="#ffe7a8" opacity="0.7" filter="url(#glow)"/>')
b.append(t(340, 276, '2 · main scene', 15, CU, 'start', 700))
b.append(t(340, 296, '1 unit = 1 m', 12.5, INK))
b.append(f'<path d="M470 190 C 560 190, 600 210, 640 246" fill="none" stroke="{INK}" stroke-width="1.6" stroke-dasharray="5 4" marker-end="url(#a)"/>')
b.append(t(560, 182, 'drawn first, depth cleared, then', 11.5, MU, 'middle'))
# rentang kedalaman (skala log)
lx0, lx1, ly0 = 96, 900, 476
def L(m): return lx0 + (math.log10(m) - math.log10(0.1)) / (math.log10(3e10) - math.log10(0.1)) * (lx1 - lx0)
b.append(t(lx0 - 64, ly0 - 30, 'DEPTH RANGE · LOG SCALE', 11, MU, 'start', 600, 'letter-spacing="2"'))
for m, lab in ((1, '1 m'), (1e3, '1 km'), (1e6, '1,000 km'), (1e9, '1 million km')):
    b.append(f'<line x1="{f1(L(m))}" y1="{ly0 - 14}" x2="{f1(L(m))}" y2="{ly0 + 40}" stroke="#fff" stroke-opacity="0.08"/>')
    b.append(t(L(m), ly0 + 54, lab, 11, MU, 'middle'))
b.append(f'<rect x="{f1(L(0.25))}" y="{ly0 - 8}" width="{f1(L(12000) - L(0.25))}" height="12" rx="6" fill="{CU}" filter="url(#glow)"/>')
b.append(t(L(12000) + 8, ly0 + 3, 'main camera 0.25 m to 12 km', 11.5, CU, 'start', 600))
b.append(f'<rect x="{f1(L(1e6))}" y="{ly0 + 12}" width="{f1(L(2e10) - L(1e6))}" height="12" rx="6" fill="{OR}" filter="url(#glow)"/>')
b.append(t(L(1e6) - 8, ly0 + 23, 'farCam 1,000 km to 20 million km', 11.5, OR, 'end', 600))
b.append(card(752, 128, 176, '48,000', ':1', 'main camera far / near', CU))
b.append(card(752, 206, 176, '1.3 bn', ':1', 'one camera out to Saturn', '#ff8a7a'))
b.append(t(752, 300, 'One depth buffer cannot', 12.5, INK)); b.append(t(752, 318, 'cover a pebble and Saturn:', 12.5, INK))
b.append(t(752, 336, 'surfaces would flicker', 12.5, INK)); b.append(t(752, 354, '(z-fighting).', 12.5, INK))
files['cc-09-two-scenes.svg'] = doc(9, 'Behind the scenes: two scenes, two scales', 'How a pebble at your feet and Saturn 260,000 km away share one frame', '\n'.join(b), ex, h=H_)

for n, s_ in files.items():
    open(os.path.join(OUT, n), 'w').write(s_)
print(f'drop t {tf:.3f} s, miss {miss:.2f} m, v0 {v0:.2f} m/s; fountain {land:.3f} m; rain {deg:.2f} deg; lift {T:.1f} s; orbit {P_orb:.2f} h')
print(sorted(files))
