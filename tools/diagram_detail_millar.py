# Bangkitkan diagram SVG untuk konsep halaman detail Millar's World (docs/millar/detail/konsep-halaman-detail.md).
# Pakai: python tools/diagram_detail_millar.py  (menulis docs/millar/detail/gambar/mi-*.svg + salinan experiences/millar/detail/)
# Label English saja (satu gambar untuk kedua bahasa). Angka dari CONFIG experiences/millar/index.html (g 12,75, R 8.282 km,
# dilatasi 61.362, gelombang 1.200 m / 125 m/s, waveG, arus balik, terbang KS-07); penampang gelombang memakai waveG() yang sama
# dengan game, dilatasi orbit Kerr dihitung dengan presisi 60 digit. Angka kunci di-assert. Tanpa library luar.
import math, os, random, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'millar', 'detail', 'gambar')
W_, H_ = 960, 540
GA, GA2, TE, VI, RE, INK, MU = '#8fd3dc', '#d4f3f7', '#f3a55a', '#b79cff', '#ff6b5a', '#e8ecf2', '#9aa2ae'   # GA = aksen Millar (--mi)
FONT = 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif'

# ------------------------------------------------------------------ dasar (gaya sama dengan diagram Copper)
def f1(v): return f'{v:.1f}'

def esc(s): return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def t(x, y, s, size=13, fill=INK, anchor='start', weight=400, extra=''):
    s = esc(s)
    return f'<text x="{f1(x)}" y="{f1(y)}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" {extra}>{s}</text>'

def pts(P): return ' '.join(f'{f1(x)},{f1(y)}' for x, y in P)

def path(P): return 'M' + ' L'.join(f'{f1(x)} {f1(y)}' for x, y in P)

def tw(s, size): return len(s) * size * 0.56

def stars(seed, n=150, box=(0, 0, W_, H_), op=1.0):
    r = random.Random(seed); o = []
    for _ in range(n):
        x = box[0] + r.random() * box[2]; y = box[1] + r.random() * box[3]
        rr = 0.35 + r.random() ** 3 * 1.3
        o.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="{rr:.2f}" fill="#fff" opacity="{op * (0.15 + 0.6 * r.random()):.2f}"/>')
    return ''.join(o)

def defs(extra=''):
    mk = lambda i, c: f'<marker id="{i}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1L9 5L0 9z" fill="{c}"/></marker>'
    return f'''<defs>
<radialGradient id="bg" cx="0.5" cy="0.4" r="0.85"><stop offset="0" stop-color="#0f1c22"/><stop offset="0.6" stop-color="#081115"/><stop offset="1" stop-color="#030607"/></radialGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="glow2" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>
<linearGradient id="card" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity="0.08"/><stop offset="1" stop-color="#ffffff" stop-opacity="0.02"/></linearGradient>
<radialGradient id="hole" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#000"/><stop offset="0.82" stop-color="#000"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
<radialGradient id="ringglow" cx="0.5" cy="0.5" r="0.5"><stop offset="0.55" stop-color="{GA}" stop-opacity="0"/><stop offset="0.8" stop-color="{GA}" stop-opacity="0.35"/><stop offset="1" stop-color="{GA}" stop-opacity="0"/></radialGradient>
{mk('a', INK)}{mk('ag', GA)}{mk('at', TE)}{mk('av', VI)}{mk('ar', RE)}
<marker id="tick" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M5 0V10" stroke="{INK}" stroke-width="1.6"/></marker>
{extra}
</defs>'''

def doc(no, title, sub, body, extra_defs='', h=H_):
    s = stars(no * 11, 160, (0, 0, W_, h), 0.55)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W_} {h}" width="{W_}" height="{h}" font-family="{FONT}">
{defs(extra_defs)}
<rect width="{W_}" height="{h}" rx="18" fill="url(#bg)"/>
<g>{s}</g>
<rect x="0.5" y="0.5" width="{W_ - 1}" height="{h - 1}" rx="18" fill="none" stroke="#ffffff" stroke-opacity="0.08"/>
<rect x="32" y="30" width="22" height="3" rx="1.5" fill="{GA}"/>
{t(62, 35, f"MILLAR'S WORLD · {no:02d}", 11, GA, 'start', 600, 'letter-spacing="2.6"')}
{t(32, 68, title, 25, INK, 'start', 650)}
{t(32, 92, sub, 13.5, MU)}
{body}
</svg>
'''

def pill(x, y, s, size=12.5, col=INK, anchor='start', bg='rgba(6,12,15,0.85)', bd='rgba(255,255,255,0.16)'):
    w = tw(s, size) + 20; h = size + 12
    x0 = x if anchor == 'start' else (x - w if anchor == 'end' else x - w / 2)
    return (f'<rect x="{f1(x0)}" y="{f1(y - h / 2)}" width="{f1(w)}" height="{f1(h)}" rx="{f1(h / 2)}" fill="{bg}" stroke="{bd}"/>'
            + t(x0 + w / 2, y + size * 0.36, s, size, col, 'middle', 500))

def callout(px, py, lx, ly, s, col=INK, size=12, anchor='start'):
    return (f'<path d="M{f1(px)} {f1(py)} L{f1(lx)} {f1(ly)}" stroke="{col}" stroke-opacity="0.55" stroke-width="1.2" fill="none"/>'
            f'<circle cx="{f1(px)}" cy="{f1(py)}" r="3" fill="{col}"/>' + pill(lx, ly, s, size, col, anchor))

def card(x, y, w, num, unit, lab, col=GA, h=66):
    return (f'<rect x="{f1(x)}" y="{y}" width="{f1(w)}" height="{h}" rx="12" fill="url(#card)" stroke="#ffffff" stroke-opacity="0.10"/>'
            f'<text x="{f1(x + 16)}" y="{y + 34}" font-size="25" font-weight="700" fill="{col}">{num}<tspan font-size="13" font-weight="500" fill="{INK}" dx="4">{unit}</tspan></text>'
            + t(x + 16, y + 54, lab, 11.5, MU))

def panel(x, y, w, h, label, cid=None):
    o = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="url(#card)" stroke="#fff" stroke-opacity="0.08"/>'
    if cid: o += f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14"/></clipPath>'
    return o + t(x + 18, y + 26, label, 11, MU, 'start', 600, 'letter-spacing="2"')

def axes(x0, y0, w, h, xt, yt, X, Y, xlab, ylab, xfmt=str, yfmt=str):
    o = []
    for v in xt:
        o.append(f'<line x1="{f1(X(v))}" y1="{y0}" x2="{f1(X(v))}" y2="{y0 + h}" stroke="#fff" stroke-opacity="0.06"/>')
        o.append(t(X(v), y0 + h + 18, xfmt(v), 11, MU, 'middle'))
    for v in yt:
        o.append(f'<line x1="{x0}" y1="{f1(Y(v))}" x2="{x0 + w}" y2="{f1(Y(v))}" stroke="#fff" stroke-opacity="0.06"/>')
        o.append(t(x0 - 8, Y(v) + 4, yfmt(v), 11, MU, 'end'))
    o.append(f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="#fff" stroke-opacity="0.25"/>')
    o.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + h}" stroke="#fff" stroke-opacity="0.25"/>')
    o.append(t(x0 + w / 2, y0 + h + 38, xlab, 11.5, MU, 'middle'))
    o.append(f'<text transform="translate({x0 - 44} {y0 + h / 2}) rotate(-90)" font-size="11.5" fill="{MU}" text-anchor="middle">{ylab}</text>')
    return ''.join(o)

def hole(cx, cy, rh, glow=True):
    o = ''
    if glow: o += f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(rh * 1.9)}" fill="url(#ringglow)"/>'
    return o + f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(rh)}" fill="#000" stroke="#000" stroke-width="1"/>'

def kelvin(T):
    """Warna benda hitam (pendekatan Tanner Helland), 0..1."""
    x = max(10.0, T / 100.0)
    if x <= 66:
        r = 255; g = 99.4708 * math.log(x) - 161.1196
        b = 0 if x <= 19 else 138.5177 * math.log(x - 10) - 305.0448
    else:
        r = 329.6987 * (x - 60) ** -0.1332; g = 288.1222 * (x - 60) ** -0.0755; b = 255
    return [min(1, max(0, c / 255)) for c in (r, g, b)]

def hexc(c): return '#%02x%02x%02x' % tuple(int(255 * min(1, max(0, v))) for v in c)


files = {}

# ------------------------------------------------------------------ fisika (sama dengan CONFIG experiences/millar/index.html)
G = 12.75; G_E = 9.80665; R_P = 8282e3; DIL = 61362; JUMP_V = 3.13; EYE = 1.7; DEPTH = 0.66
WV = dict(H=1200, v=125, wf=80, wr=30, wb=1100, bk=0.8, wt=6000, dd=0.2, ddL=6000)
CUR = dict(max=1.6, at=2500, w=3500, push=0.35)
YEAR = 365.25 * 86400
def out_s(s): return s * DIL                                           # detik di luar
def waveG(u):                                                           # = waveG() di game (u < 0 = di depan muka)
    r = math.sqrt(u * u + WV['wr'] ** 2) - WV['wr']
    return math.exp(-r / WV['wf']) if u < 0 else WV['bk'] * math.exp(-((u / WV['wb']) ** 2)) + (1 - WV['bk']) * math.exp(-r / WV['wt'])
def drawdown(u): return -WV['dd'] * math.exp(-(((u + WV['ddL']) / WV['ddL']) ** 2))
def current(u):
    if u >= 0: return 0.0
    k = (u + CUR['at']) / CUR['w']; sm = min(1, max(0, -u / 150)); return CUR['max'] * math.exp(-k * k) * sm * sm * (3 - 2 * sm)
def horizon(h): return math.sqrt(2 * R_P * h)
def climb_t(h, v, a=22.0): return v / a + (h - v * v / (2 * a)) / v
D10 = None
def kerr_isco_ut(e):                                                    # dilatasi orbit lingkaran di ISCO Kerr, 1 - a = e (presisi tinggi)
    from decimal import Decimal as Dd, getcontext
    getcontext().prec = 60
    a = 1 - Dd(e); t = Dd(1) / Dd(3); cb = lambda x: x ** t if x > 0 else Dd(0)
    Z1 = 1 + cb(1 - a * a) * (cb(1 + a) + cb(1 - a)); Z2 = (3 * a * a + Z1 * Z1).sqrt()
    r = 3 + Z2 - ((3 - Z1) * (3 + Z1 + 2 * Z2)).sqrt()
    return float(r), float((r ** Dd('1.5') + a) / (r ** Dd('0.75') * (r ** Dd('1.5') - 3 * r.sqrt() + 2 * a).sqrt()))

N = {}
N['out1s_h'] = out_s(1) / 3600
N['jumpE'] = JUMP_V ** 2 / (2 * G_E); N['jumpM'] = JUMP_V ** 2 / (2 * G); N['jumpK'] = N['jumpM'] / N['jumpE']
N['airM'] = 2 * JUMP_V / G; N['airE'] = 2 * JUMP_V / G_E
N['hor'] = horizon(EYE); N['crest'] = horizon(WV['H']) + N['hor']; N['warn'] = N['crest'] / WV['v']; N['warnY'] = out_s(N['warn']) / YEAR
N['c_shallow'] = math.sqrt(G * DEPTH); N['c_sol'] = math.sqrt(G * (DEPTH + WV['H'])); N['d125'] = WV['v'] ** 2 / G
GM = G * R_P ** 2; r_o = R_P + 350e3
N['v_orb'] = math.sqrt(GM / r_o); N['P_orb'] = 2 * math.pi * r_o / N['v_orb']; N['P_orbY'] = out_s(N['P_orb']) / YEAR; N['v_esc'] = math.sqrt(2 * G * R_P)
N['isco0'] = 1 / math.sqrt(1 - 1.5 / 3)
lo, hi = 1e-16, 1e-12                                                   # cari 1 - a yang memberi 61.362x (bisection di log)
for _ in range(60):
    m = math.sqrt(lo * hi)
    if kerr_isco_ut(m)[1] > DIL: lo = m
    else: hi = m
N['spin_e'] = math.sqrt(lo * hi); N['spin_r'] = kerr_isco_ut(N['spin_e'])[0]
N['climb40'] = climb_t(1300, 40); N['climb65'] = climb_t(1300, 65)
N['interval'] = (150e3 + 60e3) / WV['v']
assert abs(N['out1s_h'] - 17.045) < 0.001
assert abs(N['jumpK'] - 0.769) < 0.001
assert abs(N['hor'] - 5306) < 1 and abs(N['crest'] / 1e3 - 146.3) < 0.1
assert abs(N['warn'] / 60 - 19.5) < 0.05 and abs(N['warnY'] - 2.28) < 0.01
assert abs(N['c_sol'] - 123.7) < 0.05 and abs(N['c_shallow'] - 2.90) < 0.01
assert abs(N['v_orb'] - 10065) < 2 and abs(N['P_orb'] / 60 - 89.8) < 0.05 and abs(N['P_orbY'] - 10.48) < 0.01
assert abs(N['isco0'] - 1.4142) < 1e-4 and abs(kerr_isco_ut(1.0)[1] - 1.4142) < 1e-4
assert 1e-14 < N['spin_e'] < 2e-14
assert 21 < N['climb65'] < 23 and 33 < N['climb40'] < 35


# ================================================================== 01 planet sekilas
ex = f'''<radialGradient id="earth" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#5b8fd6"/><stop offset="0.6" stop-color="#2c4f86"/><stop offset="1" stop-color="#0d1d33"/></radialGradient>
<radialGradient id="mill" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#bfe7ee"/><stop offset="0.55" stop-color="#5f9fae"/><stop offset="1" stop-color="#14323a"/></radialGradient>
<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7fc4d2" stop-opacity="0.85"/><stop offset="1" stop-color="#1d4b56" stop-opacity="0.95"/></linearGradient>'''
b = []
b.append(panel(32, 112, 430, 320, 'SIZE · TO SCALE'))
sE, sM = 75 / 6371e3, 75 / 6371e3
b.append(f'<circle cx="130" cy="290" r="{f1(6371e3 * sE)}" fill="url(#earth)"/>')
b.append(f'<circle cx="335" cy="290" r="{f1(R_P * sM)}" fill="url(#mill)" filter="url(#glow)"/>')
b.append(t(130, 412, 'Earth · 6,371 km', 12, INK, 'middle', 600) + t(335, 412, "Millar · 8,282 km", 12, GA, 'middle', 600))
b.append(pill(240, 150, 'same density, 1.3x the radius = 1.3 g', 11.5, GA2, 'middle'))
# penampang: orang di air setinggi lutut
b.append(panel(482, 112, 446, 320, 'KNEE-DEEP · TO SCALE'))
x0, yb = 520, 400; s = 120                              # 1 m = 120 px, dasar laut di yb
ys = yb - DEPTH * s
b.append(f'<rect x="{x0 - 20}" y="{yb}" width="410" height="22" fill="#3a3326"/>')
P = [(x0 - 20 + i * 4, ys + 5 * math.sin(i * 0.31) + 3 * math.sin(i * 0.77 + 1)) for i in range(103)]
b.append(f'<path d="{path(P)} L{f1(x0 + 390)} {yb} L{f1(x0 - 20)} {yb} Z" fill="url(#sea)"/>')
b.append(f'<path d="{path(P)}" fill="none" stroke="#dff6fa" stroke-width="1.5" opacity="0.8"/>')
px = 650; hh = 1.75 * s                                  # astronaut 1,75 m
b.append(f'<g stroke="{INK}" stroke-width="7" stroke-linecap="round" fill="none"><path d="M{px - 12} {yb} L{px - 6} {f1(yb - 0.85 * s)} L{px + 6} {f1(yb - 0.85 * s)} L{px + 12} {yb}"/><path d="M{px} {f1(yb - 0.85 * s)} L{px} {f1(yb - 1.45 * s)}"/><path d="M{px - 22} {f1(yb - 1.05 * s)} L{px} {f1(yb - 1.4 * s)} L{px + 22} {f1(yb - 1.05 * s)}"/></g>')
b.append(f'<circle cx="{px}" cy="{f1(yb - 1.6 * s)}" r="15" fill="#1b2a30" stroke="{INK}" stroke-width="3"/><rect x="{px - 2}" y="{f1(yb - 1.66 * s)}" width="14" height="8" rx="3" fill="{GA}"/>')
b.append(f'<line x1="{x0 + 330}" y1="{yb}" x2="{x0 + 330}" y2="{f1(ys)}" stroke="{GA}" marker-start="url(#tick)" marker-end="url(#tick)"/>')
b.append(pill(x0 + 322, ys + DEPTH * s / 2, '0.66 m water (0.48-0.84)', 11, GA, 'end'))
b.append(pill(x0 + 210, 150, 'wind chop: Hs 0.35 m, ~4.5 m long', 11, GA2, 'middle'))
b.append(f'<line x1="{px + 40}" y1="{yb}" x2="{px + 40}" y2="{f1(yb - EYE * s)}" stroke="{INK}" stroke-opacity="0.6" marker-start="url(#tick)" marker-end="url(#tick)"/>')
b.append(t(px + 48, yb - EYE * s / 2 - 30, 'eye 1.7 m', 11, MU))
cw = (W_ - 64 - 3 * 12) / 4
for i, (n_, u_, l_, c_) in enumerate([('1.3', 'g', '12.75 m/s² surface gravity', GA), ('91', 'kg', 'a 70 kg person on a scale', INK),
                                      (f'{N["v_esc"] / 1e3:.1f}', 'km/s', 'escape speed (Earth 11.2)', GA2), ('5.3', 'km', 'horizon from eye height', INK)]):
    b.append(card(32 + i * (cw + 12), 452, cw, n_, u_, l_, c_, 62))
files['mi-01-planet.svg'] = doc(1, "Millar's World at a glance", 'A shallow ocean on a heavy planet, orbiting close to Gargantua', '\n'.join(b), ex)


# ================================================================== 02 satu jam = tujuh tahun
rows = [('1 second on the planet', 1), ('one jump in the air (0.49 s)', N['airM']), ('5 minutes: the radar mission', 300), ('getting swept: +400 s', 400),
        ('walking 1 km (11 min)', 1000 / 1.5), ('warning time: crest to you', N['warn']), ('one giant-wave cycle (28 min)', N['interval']),
        ('one orbit at 350 km (90 min)', N['P_orb']), ('1 hour', 3600)]
def human(s):
    if s < 86400: return f'{s / 3600:.1f} hours'
    if s < YEAR: return f'{s / 86400:.0f} days'
    return f'{s / YEAR:.2f} years'
b = []
cx, cy, R0 = 170, 300, 105
b.append(f'<circle cx="{cx}" cy="{cy}" r="{R0}" fill="#0b1418" stroke="{GA}" stroke-width="3" filter="url(#glow)"/>')
for k in range(12):
    a = k * math.pi / 6
    b.append(f'<line x1="{f1(cx + 0.86 * R0 * math.sin(a))}" y1="{f1(cy - 0.86 * R0 * math.cos(a))}" x2="{f1(cx + 0.97 * R0 * math.sin(a))}" y2="{f1(cy - 0.97 * R0 * math.cos(a))}" stroke="{INK}" stroke-width="2"/>')
b.append(f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy - 80}" stroke="{GA}" stroke-width="3"/><line x1="{cx}" y1="{cy}" x2="{cx + 45}" y2="{cy}" stroke="{INK}" stroke-width="4"/>')
b.append(t(cx, cy + R0 + 30, 'your clock: 1 hour', 13, GA, 'middle', 650))
b.append(t(cx, 150, 'x 61,362', 22, GA2, 'middle', 700))
b.append(t(cx, 170, 'outside, time runs faster', 11.5, MU, 'middle'))
# batang log
x0, x1 = 520, 850; lo_, hi_ = math.log10(3600), math.log10(10 * YEAR)
X = lambda s: x0 + (math.log10(s) - lo_) / (hi_ - lo_) * (x1 - x0)
b.append(t(330, 132, 'TIME THAT PASSES OUTSIDE · LOG SCALE', 11, MU, 'start', 600, 'letter-spacing="2"'))
for s_, lab in ((3600, '1 h'), (86400, '1 day'), (30 * 86400, '1 month'), (YEAR, '1 year'), (10 * YEAR, '10 years')):
    b.append(f'<line x1="{f1(X(s_))}" y1="150" x2="{f1(X(s_))}" y2="436" stroke="#fff" stroke-opacity="0.07"/>' + t(X(s_), 452, lab, 10.5, MU, 'middle'))
for i, (lab, s_) in enumerate(rows):
    y = 160 + i * 31; o = out_s(s_)
    b.append(t(330, y + 14, lab, 11, INK))
    w = max(2, X(min(o, 10 * YEAR)) - x0)
    col = GA if o < YEAR else GA2
    b.append(f'<rect x="{x0}" y="{y + 3}" width="{f1(w)}" height="14" rx="4" fill="{col}" opacity="0.85"/>')
    b.append(t(x0 + w + 6, y + 14, human(o), 11, col, 'start', 600))
b.append(pill(170, 470, '1 h = 7 x 365.25 x 24 h outside', 11.5, MU, 'middle'))
files['mi-02-time.svg'] = doc(2, 'One hour here, seven years outside', 'The same moments, measured on your clock and on a clock far from Gargantua', '\n'.join(b))
N['rows'] = [(l, human(out_s(s))) for l, s in rows]


# ================================================================== 03 kenapa harus berputar
b = []
x0, y0, w, h = 110, 140, 520, 290
xs = list(range(0, 17))
X = lambda e: x0 + (-math.log10(e)) / 16 * w
Y = lambda v: y0 + h - math.log10(v) / 6 * h
b.append(axes(x0, y0, w, h, [1, 1e-4, 1e-8, 1e-12, 1e-16], [1, 10, 100, 1e3, 1e4, 1e5, 1e6], X, Y,
              'how far from the maximum spin: 1 - a  (a = J c / G M²)', 'time dilation of the innermost stable orbit',
              lambda v: '1' if v == 1 else f'1e{int(math.log10(v))}', lambda v: f'{int(v):,}' if v < 1e4 else f'1e{int(math.log10(v))}'))
P = [(X(10 ** -q), Y(kerr_isco_ut(10 ** -q)[1])) for q in [i * 0.1 for i in range(0, 161)]]
b.append(f'<path d="{path(P)}" fill="none" stroke="{GA}" stroke-width="2.6" filter="url(#glow)"/>')
b.append(f'<line x1="{x0}" y1="{f1(Y(DIL))}" x2="{x0 + w}" y2="{f1(Y(DIL))}" stroke="{RE}" stroke-dasharray="6 4" stroke-width="1.6"/>')
b.append(pill(x0 + 8, Y(DIL) - 14, "Millar: 61,362x", 11, RE))
b.append(f'<circle cx="{f1(X(N["spin_e"]))}" cy="{f1(Y(DIL))}" r="5" fill="{RE}" filter="url(#glow)"/>')
b.append(callout(X(N['spin_e']), Y(DIL), X(N['spin_e']) - 30, Y(DIL) + 50, f'1 - a = {N["spin_e"]:.1e}'.replace('e-', 'e-'), RE, 11, 'end'))
b.append(callout(X(1), Y(N['isco0']), X(1) + 30, Y(N['isco0']) - 40, 'no spin (Schwarzschild): 1.41x', GA2, 11))
b.append(card(660, 140, 268, '1.41', 'x', 'best stable orbit without spin', GA2))
b.append(card(660, 218, 268, f'{N["spin_e"]:.1e}', '', 'spin gap needed for 61,362x', RE))
b.append(card(660, 296, 268, f'{N["spin_r"]:.5f}', 'GM/c²', 'orbit radius, just above the horizon', GA))
for i, line in enumerate(['A non-spinning hole cannot slow time', 'this much on a stable orbit. Only a', 'hole spinning within about 1 part in', '100 trillion of the maximum can.']):
    b.append(t(660, 394 + i * 19, line, 12.5, INK))
files['mi-03-spin.svg'] = doc(3, 'Why Gargantua must spin', 'Kerr circular orbits: the slowest clock on the innermost stable orbit, against the spin', '\n'.join(b))


# ================================================================== 04 gravitasi dan lompatan
b = []
x0, yb, sx, sy = 90, 400, 160, 420
b.append(panel(32, 112, 600, 320, 'SAME LEG PUSH (3.13 m/s), SIDE BY SIDE · HEIGHT x1'))
for k, (gg, col, lab, off) in enumerate(((G_E, INK, 'Earth', 0), (G, GA, 'Millar 1.3 g', 290))):
    T_ = 2 * JUMP_V / gg; vx = 0.9
    P = [(x0 + off + vx * T_ * i / 40 * sx, yb - (JUMP_V * T_ * i / 40 - 0.5 * gg * (T_ * i / 40) ** 2) * sy) for i in range(41)]
    b.append(f'<path d="{path(P)}" fill="none" stroke="{col}" stroke-width="2.4" stroke-dasharray="5 4"/>')
    for i in range(0, 41, 8):
        b.append(f'<circle cx="{f1(P[i][0])}" cy="{f1(P[i][1])}" r="6" fill="{col}" opacity="{0.3 + 0.7 * i / 40:.2f}"/>')
    hmax = JUMP_V ** 2 / (2 * gg)
    b.append(f'<line x1="{f1(x0 + off - 14)}" y1="{yb}" x2="{f1(x0 + off - 14)}" y2="{f1(yb - hmax * sy)}" stroke="{col}" marker-start="url(#tick)" marker-end="url(#tick)"/>')
    b.append(pill(x0 + off + 60, yb - hmax * sy - 22, f'{lab}: {hmax:.2f} m, {T_:.2f} s in the air', 11, col, 'middle'))
b.append(f'<line x1="50" y1="{yb}" x2="612" y2="{yb}" stroke="{GA}" stroke-opacity="0.6"/>')
b.append(card(652, 112, 276, '77', '%', 'of an Earth jump (0.384 vs 0.50 m)', GA))
b.append(card(652, 190, 276, '91', 'kg', 'a 70 kg person on the scale', INK))
b.append(card(652, 268, 276, '0.52', 's', 'a dropped helmet falls 1.7 m (Earth 0.59)', GA2))
b.append(card(652, 346, 276, f'{out_s(N["airM"]) / 3600:.1f}', 'h', 'pass outside during one jump', RE, 66))
files['mi-04-gravity.svg'] = doc(4, 'Gravity at 1.3 g', 'Every jump is lower and shorter; every step carries 30% more weight', '\n'.join(b))
N['airM_out_h'] = out_s(N['airM']) / 3600


# ================================================================== 05 cakrawala
b = []
b.append(panel(32, 112, 600, 320, 'LINE OF SIGHT OVER THE CURVE · HEIGHTS EXAGGERATED', 'p5'))
b.append('<g clip-path="url(#p5)">')
cx, cy, Rr = 332, 1580, 1300                                   # lengkung skematik
b.append(f'<circle cx="{cx}" cy="{cy}" r="{Rr}" fill="#14323a" stroke="{GA}" stroke-width="2"/>')
ang_e, ang_w = -0.17, 0.17
ex_, ey_ = cx + Rr * math.sin(ang_e), cy - Rr * math.cos(ang_e)
wx_, wy_ = cx + Rr * math.sin(ang_w), cy - Rr * math.cos(ang_w)
eh = 40; wh = 110
E = (ex_ + eh * math.sin(ang_e), ey_ - eh * math.cos(ang_e)); Wt = (wx_ + wh * math.sin(ang_w), wy_ - wh * math.cos(ang_w))
US_ = [-400 + i * 20 for i in range(171)]
AA = lambda uu: ang_w + uu / 3000 * 0.05
WP = [(cx + (Rr + wh * waveG(uu)) * math.sin(AA(uu)), cy - (Rr + wh * waveG(uu)) * math.cos(AA(uu))) for uu in US_]
base = [(cx + Rr * math.sin(AA(uu)), cy - Rr * math.cos(AA(uu))) for uu in reversed(US_)]
b.append(f'<path d="{path(WP + base)} Z" fill="#cfeff4" opacity="0.92"/>')
Wt = max(WP, key=lambda q: -q[1])
b.append(f'<line x1="{f1(E[0])}" y1="{f1(E[1])}" x2="{f1(Wt[0] - 16)}" y2="{f1(Wt[1] + 2)}" stroke="{GA2}" stroke-width="1.6" stroke-dasharray="6 4"/>')
b.append(f'<circle cx="{f1(E[0])}" cy="{f1(E[1])}" r="5" fill="{INK}"/>')
b.append('</g>')
b.append(pill(E[0] - 6, E[1] - 24, 'you, eye 1.7 m', 11, INK, 'middle'))
b.append(pill(Wt[0] - 20, Wt[1] - 26, 'crest 1,200 m', 11, GA2, 'middle'))
b.append(pill(332, 168, f'first sight of the crest: {N["crest"] / 1e3:.0f} km away', 11.5, GA2, 'middle'))
b.append(pill(332, 410, 'the sea surface itself ends at 5.3 km', 11, MU, 'middle'))
# grafik jarak terlihat vs tinggi
x0, y0, w, h = 700, 140, 220, 240
X = lambda hh: x0 + (math.log10(hh) - 0) / 4 * w
Y = lambda d: y0 + h - d / 300 * h
b.append(axes(x0, y0, w, h, [1, 10, 100, 1000, 10000], [0, 100, 200, 300], X, Y, 'height of the object (m, log)', 'visible from (km)',
              lambda v: f'{int(v):,}', lambda v: f'{int(v)}'))
P = [(X(10 ** (q / 50)), Y((horizon(10 ** (q / 50)) + N['hor']) / 1e3)) for q in range(0, 185)]
b.append(f'<path d="{path(P)}" fill="none" stroke="{GA}" stroke-width="2.4" filter="url(#glow)"/>')
b.append(f'<circle cx="{f1(X(1200))}" cy="{f1(Y(N["crest"] / 1e3))}" r="5" fill="{GA2}"/>')
cw = (W_ - 64 - 3 * 12) / 4
for i, (n_, u_, l_, c_) in enumerate([(f'{N["crest"] / 1e3:.0f}', 'km', 'crest rises over the horizon', GA2), (f'{N["warn"] / 60:.1f}', 'min', 'until it reaches you (125 m/s)', GA),
                                      (f'{N["warnY"]:.2f}', 'years', 'pass outside meanwhile', RE), ('5.3', 'km', 'horizon from eye height', INK)]):
    b.append(card(32 + i * (cw + 12), 452, cw, n_, u_, l_, c_, 62))
files['mi-05-horizon.svg'] = doc(5, 'Mountains on the horizon', 'What looks like a mountain range is a wave, still hidden behind the curve of the planet', '\n'.join(b))


# ================================================================== 06 penampang gelombang
b = []
b.append(panel(32, 112, 896, 230, 'CROSS-SECTION FROM THE GAME (waveG) · TO SCALE, 1:1', 'p6'))
x0, x1, yb = 52, 908, 318
U0, U1 = -4000, 7500
X = lambda u: x0 + (u - U0) / (U1 - U0) * (x1 - x0)
sc = (x1 - x0) / (U1 - U0)
Yh = lambda z: yb - z * sc
P = [(X(u), Yh(WV['H'] * waveG(u))) for u in [U0 + (U1 - U0) * i / 900 for i in range(901)]]
b.append(f'<path d="{path(P)} L{x1} {yb} L{x0} {yb} Z" fill="#9fd7e0" opacity="0.85"/>')
b.append(f'<path d="{path(P)}" fill="none" stroke="#eafcff" stroke-width="1.6"/>')
b.append(f'<line x1="{x0}" y1="{yb}" x2="{x1}" y2="{yb}" stroke="{GA}" stroke-opacity="0.6"/>')
tx = X(1500); th = 828 * sc                                                  # menara 828 m untuk skala
b.append(f'<rect x="{f1(tx - 3)}" y="{f1(yb - th)}" width="6" height="{f1(th)}" fill="#6c7585"/>')
b.append(pill(tx + 10, yb - th - 4, '828 m tower for scale', 10.5, MU))
b.append(f'<line x1="{f1(X(-300))}" y1="{yb}" x2="{f1(X(-300))}" y2="{f1(Yh(1200))}" stroke="{INK}" marker-start="url(#tick)" marker-end="url(#tick)"/>')
b.append(pill(X(-320), Yh(600), '1,200 m', 11, INK, 'end'))
b.append(f'<line x1="{f1(X(-1200))}" y1="{yb - 30}" x2="{f1(X(-2400))}" y2="{yb - 30}" stroke="{GA}" stroke-width="2.4" marker-end="url(#ag)"/>')
b.append(t(X(-1800), yb - 40, '125 m/s', 12, GA, 'middle', 650))
b.append(callout(X(30), Yh(1100), X(900), 160, 'near-vertical concave face (80 m scale)', GA2, 11))
b.append(callout(X(2400), Yh(WV['H'] * waveG(2400)), X(3800), 200, 'thick body, then a 6 km tail', INK, 11))
# arus balik dan air surut
x0b, y0b, wb, hb = 110, 380, 360, 110
Xb = lambda u: x0b + (u + 9000) / 9000 * wb
Yb = lambda v: y0b + hb - v / 2 * hb
b.append(axes(x0b, y0b, wb, hb, [-9000, -6000, -3000, 0], [0, 1, 2], Xb, Yb, 'distance in front of the face (m)', 'current m/s', lambda v: f'{int(v / 1000)} km', lambda v: f'{v}'))
P = [(Xb(u), Yb(current(u))) for u in [-9000 + i * 10 for i in range(901)]]
b.append(f'<path d="{path(P)}" fill="none" stroke="{GA}" stroke-width="2.4" filter="url(#glow)"/>')
b.append(callout(Xb(-2500), Yb(1.6), Xb(-8800), Yb(2.15), 'backwash 1.6 m/s, drags you at 35%', GA, 10.5))
b.append(card(520, 380, 190, '0.2', 'm', 'drawdown, 6 km ahead', GA2, 62))
b.append(card(722, 380, 206, '984-1,200', 'm', 'height along the front', INK, 62))
b.append(card(520, 452, 408, '4.3', 's', 'swept: foam to white-out; +400 s = 0.78 years out', RE, 62))
files['mi-06-wave.svg'] = doc(6, 'The 1.2 km wave', 'A wall of water moving at 125 m/s, preceded by a drawdown and a backwash', '\n'.join(b))


# ================================================================== 07 libration dan laju
b = []
b.append(panel(32, 112, 470, 330, 'TIDALLY LOCKED, BUT ROCKING (LIBRATION)'))
cx, cy, Rr = 240, 290, 92
for k, ang in enumerate((-12, 0, 12)):
    a = math.radians(ang); op = 0.25 if ang else 1
    pts_ = []
    for i in range(121):
        th = i / 120 * math.tau; rr = Rr * (1 + 0.16 * math.cos(2 * (th - a)))
        pts_.append((cx + rr * math.cos(th), cy - rr * math.sin(th)))
    b.append(f'<path d="{path(pts_)} Z" fill="{"#5f9fae" if not ang else "none"}" stroke="{GA}" stroke-opacity="{op}" stroke-width="1.6"/>')
b.append(f'<circle cx="{cx}" cy="{cy}" r="{Rr - 6}" fill="#14323a"/>')
b.append(f'<circle cx="465" cy="{cy}" r="16" fill="#000" stroke="{TE}" stroke-width="3" filter="url(#glow)"/>')
b.append(t(465, cy + 36, 'Gargantua', 11, TE, 'middle'))
b.append(f'<path d="M{cx + 70} {cy - 82} A 110 110 0 0 1 {cx + 70} {cy + 82}" fill="none" stroke="{GA2}" stroke-width="2" marker-start="url(#ag)" marker-end="url(#ag)"/>')
b.append(pill(cx, 150, 'the tidal bulge swings with the rocking', 11, GA2, 'middle'))
b.append(pill(cx, 418, 'the shallow sea sloshes into a giant wave (Thorne)', 11, INK, 'middle'))
# laju
x0, y0, w, h = 540, 150, 290, 210
bars = [('shallow-water speed √(g d), d = 0.66 m', N['c_shallow'], MU), ('solitary-wave guess √(g (d + a))', N['c_sol'], GA2), ('the game wave (design value)', 125.0, GA)]
for i, (lab, v_, col) in enumerate(bars):
    y = y0 + i * 70
    b.append(t(x0, y, lab, 11.5, INK))
    b.append(f'<rect x="{x0}" y="{y + 10}" width="{f1(v_ / 130 * w)}" height="18" rx="5" fill="{col}"/>')
    b.append(t(x0 + v_ / 130 * w + 8, y + 24, f'{v_:.1f} m/s', 11.5, col, 'start', 650))
b.append(t(x0, 380, f'125 m/s in ordinary shallow water would need {N["d125"]:,.0f} m of depth.', 11, MU))
b.append(t(x0, 398, 'The solitary-wave formula is only valid for small waves,', 11, MU))
b.append(t(x0, 416, 'so its closeness here is a coincidence, not a proof.', 11, MU))
cw = (W_ - 64 - 2 * 12) / 3
for i, (n_, u_, l_, c_) in enumerate([('40', 's', 'planet wobble period in the game', GA), ('0.35-1.75', '°', 'wobble grows as the wave nears', GA2), ('28', 'min', 'between giant waves (3.3 years outside)', INK)]):
    b.append(card(32 + i * (cw + 12), 458, cw, n_, u_, l_, c_, 60))
files['mi-07-libration.svg'] = doc(7, 'Why the waves come', 'A planet that always faces Gargantua still rocks a little, and its ocean sloshes', '\n'.join(b))


# ================================================================== 08 lolos ke orbit
b = []
x0, y0, w, h = 92, 140, 380, 270
X = lambda tt: x0 + tt / 40 * w
Y = lambda z: y0 + h - z / 1500 * h
b.append(axes(x0, y0, w, h, [0, 10, 20, 30, 40], [0, 500, 1000, 1500], X, Y, 'seconds after lift-off', 'altitude (m)', lambda v: f'{v}', lambda v: f'{v:,}'))
for vmax, col, lab in ((40, GA2, 'climb 40 m/s'), (65, GA, 'Shift: 65 m/s')):
    P = []
    for i in range(401):
        tt = i * 0.1; a = 22.0
        z = 0.5 * a * tt * tt if tt < vmax / a else vmax * vmax / (2 * a) + vmax * (tt - vmax / a)
        P.append((X(tt), Y(min(z, 1500))))
    b.append(f'<path d="{path(P)}" fill="none" stroke="{col}" stroke-width="2.4" filter="url(#glow)"/>')
    b.append(pill(X(39.5), Y(330 if vmax == 40 else 170), f'{lab}: 1,300 m in {climb_t(1300, vmax):.1f} s', 10.5, col, 'end'))
b.append(f'<line x1="{x0}" y1="{f1(Y(1200))}" x2="{x0 + w}" y2="{f1(Y(1200))}" stroke="{RE}" stroke-dasharray="6 4"/>')
b.append(t(x0 + 6, Y(1200) - 6, 'wave crest 1,200 m', 11, RE))
# orbit berskala
cx, cy = 720, 300; sc = 120 / 8282
b.append(f'<circle cx="{cx}" cy="{cy}" r="{f1(8282 * sc)}" fill="url(#bgp)" stroke="{GA}" stroke-width="1.5"/>')
b.append(f'<circle cx="{cx}" cy="{cy}" r="{f1((8282 + 350) * sc)}" fill="none" stroke="{GA2}" stroke-dasharray="4 4" stroke-width="1.6"/>')
a = -0.8; sx_, sy_ = cx + (8282 + 350) * sc * math.cos(a), cy + (8282 + 350) * sc * math.sin(a)
b.append(f'<circle cx="{f1(sx_)}" cy="{f1(sy_)}" r="5" fill="{INK}" filter="url(#glow)"/>')
b.append(f'<line x1="{f1(sx_)}" y1="{f1(sy_)}" x2="{f1(sx_ + 50 * math.sin(-a))}" y2="{f1(sy_ + 50 * math.cos(a))}" stroke="{INK}" stroke-width="1.8" marker-end="url(#a)"/>')
b.append(pill(cx, 152, 'orbit 350 km · to scale', 11, GA2, 'middle'))
cw = (W_ - 64 - 3 * 12) / 4
for i, (n_, u_, l_, c_) in enumerate([(f'{N["v_orb"] / 1e3:.2f}', 'km/s', 'circular speed at 350 km', GA), (f'{N["P_orb"] / 60:.1f}', 'min', 'one orbit on your clock', GA2),
                                      (f'{N["P_orbY"]:.1f}', 'years', 'pass outside per orbit', RE), ('300', 'm', 'past the face counts as escaped', INK)]):
    b.append(card(32 + i * (cw + 12), 452, cw, n_, u_, l_, c_, 62))
ex8 = '<radialGradient id="bgp" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#bfe7ee"/><stop offset="0.55" stop-color="#5f9fae"/><stop offset="1" stop-color="#14323a"/></radialGradient>'
files['mi-08-escape-orbit.svg'] = doc(8, 'Escape to orbit', 'KS-07 climbs over the wave, then circles the planet at ten kilometres per second', '\n'.join(b), ex8)


# ------------------------------------------------------------------ tulis
PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'experiences', 'millar', 'detail')
for d_ in (OUT, PAGE):
    os.makedirs(d_, exist_ok=True)
    for n_, s_ in files.items():
        open(os.path.join(d_, n_), 'w').write(s_)
print(f"1 s = {N['out1s_h']:.3f} h; jump {N['jumpE']:.3f} / {N['jumpM']:.3f} m ({N['jumpK'] * 100:.1f}%), air {N['airM']:.3f} s = {N['airM_out_h']:.1f} h outside")
print(f"horizon {N['hor']:.0f} m; crest seen {N['crest'] / 1e3:.1f} km; warning {N['warn'] / 60:.2f} min = {N['warnY']:.3f} years")
print(f"speeds: shallow {N['c_shallow']:.2f}, solitary {N['c_sol']:.2f} m/s; depth for 125 m/s {N['d125']:.0f} m")
print(f"orbit {N['v_orb']:.0f} m/s, {N['P_orb'] / 60:.2f} min = {N['P_orbY']:.2f} years; escape {N['v_esc']:.0f} m/s; climb {N['climb40']:.1f} / {N['climb65']:.1f} s")
print(f"spin: no spin {N['isco0']:.4f}x; 61,362x at 1 - a = {N['spin_e']:.3e}, ISCO {N['spin_r']:.6f} M; wave cycle {N['interval']:.0f} s")
print('rows:', N['rows'])
print(sorted(files))
