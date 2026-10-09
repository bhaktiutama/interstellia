# Bangkitkan diagram SVG untuk konsep halaman detail Gargantua (docs/gargantua/detail/konsep-halaman-detail.md).
# Pakai: python tools/diagram_detail_gargantua.py  (menulis docs/gargantua/detail/gambar/gg-*.svg)
# Label English saja (satu gambar untuk kedua bahasa). Satuan seperti di experience: rs = 1, M = 0,5, c = 1;
# massa 1e8 Matahari hanya untuk angka km dan detik. Lintasan sinar dan orbit diintegrasikan dari persamaan
# yang sama dengan kode (sinar a = -1,5 h^2 p / r^5, geodesik r'' = -M/r^2 + L^2/r^3 - 3 M L^2/r^4), bukan digambar tangan.
# Angka kunci di-assert agar dokumen, diagram, dan game satu sumber. Tanpa library luar.
import math, os, random, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'gargantua', 'detail', 'gambar')
M = 0.5
RS_KM = 2.954e8; TS = 985.27                       # rs dalam km dan rs/c dalam detik untuk 1e8 Matahari (= MIS_T di kode)
B_C = 1.5 * math.sqrt(3)                           # parameter dampak kritis foton
W_, H_ = 960, 540
GA, GA2, TE, VI, RE, INK, MU = '#f3a55a', '#ffd08a', '#8fd3dc', '#b79cff', '#ff6b5a', '#e8ecf2', '#9aa2ae'
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
<radialGradient id="bg" cx="0.5" cy="0.4" r="0.85"><stop offset="0" stop-color="#17121a"/><stop offset="0.6" stop-color="#0a090e"/><stop offset="1" stop-color="#040406"/></radialGradient>
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
{t(62, 35, f'GARGANTUA · {no:02d}', 11, GA, 'start', 600, 'letter-spacing="2.6"')}
{t(32, 68, title, 25, INK, 'start', 650)}
{t(32, 92, sub, 13.5, MU)}
{body}
</svg>
'''

def pill(x, y, s, size=12.5, col=INK, anchor='start', bg='rgba(10,10,14,0.85)', bd='rgba(255,255,255,0.16)'):
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


# ------------------------------------------------------------------ fisika (sama dengan kode experience)
def ray(px, py, vx, vy, stop, h0=0.02, nmax=40000):
    """Foton di bidang: a = -1,5 h^2 p / r^5 (rs = 1), h = |p x v|. Kembali (titik, tertangkap, arah akhir)."""
    hh = (px * vy - py * vx) ** 2
    def acc(x, y):
        r = math.hypot(x, y); k = -1.5 * hh / r ** 5
        return k * x, k * y
    P = [(px, py)]
    for _ in range(nmax):
        r = math.hypot(px, py)
        if r < 1.0: return P, True, (vx, vy)
        if stop(px, py, vx, vy): return P, False, (vx, vy)
        h = h0 * min(1.0, (r - 0.6) / 2.0)
        ax, ay = acc(px, py)                                    # RK4
        k1 = (vx, vy, ax, ay)
        a2 = acc(px + vx * h / 2, py + vy * h / 2); k2 = (vx + ax * h / 2, vy + ay * h / 2, *a2)
        a3 = acc(px + k2[0] * h / 2, py + k2[1] * h / 2); k3 = (vx + a2[0] * h / 2, vy + a2[1] * h / 2, *a3)
        a4 = acc(px + k3[0] * h, py + k3[1] * h); k4 = (vx + a3[0] * h, vy + a3[1] * h, *a4)
        px += h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); py += h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        vx += h / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2]); vy += h / 6 * (k1[3] + 2 * k2[3] + 2 * k3[3] + k4[3])
        P.append((px, py))
    return P, False, (vx, vy)

def orbit(r0, L, E=1.0, tmax=4000.0, rcap=1.0, rout=40.0):
    """Geodesik benda bermassa di bidang, waktu wajar: r'' = -M/r^2 + L^2/r^3 - 3ML^2/r^4, phi' = L/r^2 (= misAcc())."""
    vr2 = E * E - (1 - 1 / r0) * (1 + L * L / r0 ** 2)
    r, vr, ph, tau = r0, -math.sqrt(max(0.0, vr2)), 0.0, 0.0
    f = lambda r, vr: (vr, -M / r ** 2 + L * L / r ** 3 - 3 * M * L * L / r ** 4, L / r ** 2)
    P = [(r, ph)]
    while tau < tmax:
        if r < rcap: return P, 'captured', tau
        if r > rout and vr > 0: return P, 'escaped', tau
        h = 0.004 * r ** 1.5
        k1 = f(r, vr); k2 = f(r + k1[0] * h / 2, vr + k1[1] * h / 2)
        k3 = f(r + k2[0] * h / 2, vr + k2[1] * h / 2); k4 = f(r + k3[0] * h, vr + k3[1] * h)
        r += h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); vr += h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        ph += h / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2]); tau += h
        P.append((r, ph))
    return P, 'bound', tau

def Gout(r): return r + 2 * math.sqrt(r) + 2 * math.log(abs(math.sqrt(r) - 1))      # sinar keluar, waktu PG (= relStep)
def tau_fall(r0, r): return 2 / 3 * (r0 ** 1.5 - r ** 1.5)                           # jatuh E = 1, waktu wajar = waktu PG
def v_gas(r): return math.sqrt(M / (r - 2 * M))                                        # orbit lingkaran, pengamat diam
def crit_d(r0): return math.degrees(math.asin(2 * math.sqrt(r0 - 1) / r0))            # L = r0 sin d / akar(r0 - 1) = 2
def tidal_g(r): return 2 * 299792458.0 ** 2 / (r ** 3 * (RS_KM * 1e3) ** 2) / 9.81     # tubuh 2 m (= kode)
def T_disk(r, rin=3.0, k=0.85): return r ** -0.75 * max(0.0, 1 - k * math.sqrt(rin / r)) ** 0.25

N = dict()
N['shadow_deg'] = math.degrees(math.asin(B_C / 22 * math.sqrt(1 - 1 / 22)))
N['fall_h'] = tau_fall(22, 1); N['fall_hours'] = N['fall_h'] * TS / 3600
N['inside_s'] = tau_fall(1, 0) * TS
N['crit22'] = crit_d(22); N['crit10'] = crit_d(10); N['crit6'] = crit_d(6)
N['v_isco'] = v_gas(3); N['rel_isco'] = 2 * N['v_isco'] / (1 + N['v_isco'] ** 2)
N['beam_edge'] = ((1 + N['v_isco']) / (1 - N['v_isco'])) ** 4
N['relay_clock'] = math.sqrt(1 - 1.5 / 22)
N['tide_h'] = tidal_g(1); N['tide_1g_r'] = (2 * 299792458.0 ** 2 / ((RS_KM * 1e3) ** 2 * 9.81)) ** (1 / 3)
N['tide_1g_s'] = tau_fall(N['tide_1g_r'], 0) * TS
N['dust_J'] = (1 / math.sqrt(1 - N['rel_isco'] ** 2) - 1) * 1e-9 * 299792458.0 ** 2
g_fast = 1.3 / math.sqrt(1 - 1 / 22); N['beta_fast'] = math.sqrt(1 - 1 / g_fast ** 2)
N['drdtau_fast'] = math.sqrt(1.3 ** 2 - (1 - 1 / 22))
N['ab90_fast'] = math.degrees(math.acos(N['beta_fast']))
N['zoom_deg'] = math.degrees(math.log(10) / math.sqrt(0.5))
assert abs(N['shadow_deg'] - 6.63) < 0.01, N['shadow_deg']
assert abs(N['fall_h'] - 68.13) < 0.01 and abs(N['fall_hours'] - 18.65) < 0.01
assert abs(N['inside_s'] - 656.8) < 0.1
assert abs(N['crit22'] - 24.62) < 0.005 and abs(N['crit10'] - 36.87) < 0.005 and abs(N['crit6'] - 48.19) < 0.005
assert abs(N['rel_isco'] - 0.8) < 1e-9 and abs(N['beam_edge'] - 81) < 1e-6
assert abs(N['relay_clock'] - 0.9653) < 1e-4
assert abs(N['tide_h'] - 2.1e-7) < 0.05e-7 and abs(N['tide_1g_r'] - 0.00594) < 0.00001 and abs(N['tide_1g_s'] - 0.30) < 0.01
assert abs(N['dust_J'] - 6.0e7) < 0.05e7
assert abs(N['drdtau_fast'] - 0.86) < 0.005
assert abs(N['zoom_deg'] - 186.6) < 0.05


# ================================================================== 01 anatomi
ex = f'''<radialGradient id="diskg" cx="0.5" cy="0.5" r="0.5"><stop offset="0.24" stop-color="#fff1cf"/><stop offset="0.4" stop-color="{GA2}"/><stop offset="0.7" stop-color="{GA}" stop-opacity="0.75"/><stop offset="1" stop-color="#a0401c" stop-opacity="0.15"/></radialGradient>'''
b = []
b.append(panel(32, 112, 420, 320, 'TOP VIEW · TO SCALE', 'p1'))
cx, cy, s = 242, 280, 6.4
b.append('<g clip-path="url(#p1)">')
b.append(f'<circle cx="{cx}" cy="{cy}" r="{f1(22 * s)}" fill="none" stroke="{TE}" stroke-opacity="0.55" stroke-dasharray="3 5"/>')
rr = random.Random(5)
outer = [(cx + 12 * s * math.cos(a), cy + 12 * s * math.sin(a)) for a in [i * math.pi / 60 for i in range(121)]]
inner = [(cx + 3 * s * math.cos(-a), cy + 3 * s * math.sin(-a)) for a in [i * math.pi / 60 for i in range(121)]]
b.append(f'<path d="{path(outer)} Z {path(inner)} Z" fill="url(#diskg)" fill-rule="evenodd" filter="url(#glow)"/>')
for i in range(26):                                                                   # jejak gas (spiral Kepler)
    r0_ = 3.3 + rr.random() * 8.4; a0 = rr.random() * math.tau; span = 0.5 + rr.random() * 0.6
    P = [(cx + (r0_ - 0.15 * j / 10) * s * math.cos(a0 + span * j / 10), cy + (r0_ - 0.15 * j / 10) * s * math.sin(a0 + span * j / 10)) for j in range(11)]
    b.append(f'<path d="{path(P)}" fill="none" stroke="#fff6dc" stroke-opacity="{0.15 + 0.3 * rr.random():.2f}" stroke-width="1.1"/>')
b.append(hole(cx, cy, s, False))
b.append(f'<circle cx="{cx}" cy="{cy}" r="{f1(1.5 * s)}" fill="none" stroke="{TE}" stroke-width="1.2"/>')
b.append(f'<circle cx="{cx}" cy="{cy}" r="{f1(3 * s)}" fill="none" stroke="{INK}" stroke-width="1.4"/>')
ra = math.radians(-40)
rx_, ry_ = cx + 22 * s * math.cos(ra), cy + 22 * s * math.sin(ra)
b.append(f'<g filter="url(#glow)"><rect x="{f1(rx_ - 6)}" y="{f1(ry_ - 3)}" width="12" height="6" rx="1.5" fill="{TE}"/><line x1="{f1(rx_ - 13)}" y1="{f1(ry_)}" x2="{f1(rx_ + 13)}" y2="{f1(ry_)}" stroke="{TE}" stroke-width="1.6"/></g>')
b.append(f'<path d="M{f1(cx + 22 * s * math.cos(ra + 0.2))} {f1(cy + 22 * s * math.sin(ra + 0.2))} A{f1(22 * s)} {f1(22 * s)} 0 0 1 {f1(cx + 22 * s * math.cos(ra + 0.55))} {f1(cy + 22 * s * math.sin(ra + 0.55))}" fill="none" stroke="{TE}" stroke-width="1.8" marker-end="url(#at)"/>')
b.append('</g>')
b.append(callout(rx_ - 4, ry_ - 4, 424, 150, 'relay, 22 rs', TE, 11.5, 'end'))
b.append(callout(cx + 8 * s, cy + 6 * s, 424, 412, 'disk 3 to 12 rs', GA, 11.5, 'end'))
b.append(callout(cx - 3 * s * 0.71, cy + 3 * s * 0.71, 50, 412, 'ISCO 3 rs', INK, 11.5))
b.append(callout(cx - 1.5 * s * 0.71, cy - 1.5 * s * 0.71, 50, 150, 'photon sphere 1.5 rs', TE, 11.5))
# tangga jari-jari (skala log)
x0, x1 = 500, 900
LX = lambda r: x0 + math.log10(r / 0.8) / math.log10(30 / 0.8) * (x1 - x0)
b.append(t(500, 132, 'THE RADII THAT MATTER · LOG SCALE', 11, MU, 'start', 600, 'letter-spacing="2"'))
b.append(f'<line x1="{x0}" y1="164" x2="{x1}" y2="164" stroke="#fff" stroke-opacity="0.25"/>')
for r in (1, 2, 5, 10, 20):
    b.append(f'<line x1="{f1(LX(r))}" y1="159" x2="{f1(LX(r))}" y2="169" stroke="#fff" stroke-opacity="0.35"/>' + t(LX(r), 155, f'{r} rs', 10.5, MU, 'middle'))
rows = [(1.0, 'Event horizon', 'no way back, even for light', '#ffffff'),
        (1.5, 'Photon sphere', 'light can circle the hole (unstable)', TE),
        (2.0, 'Marginally bound orbit', 'zoom-whirl happens here', VI),
        (3.0, 'ISCO, inner edge of the disk', 'last stable circular orbit', INK),
        (12.0, 'Outer edge of the disk', 'the disk spans 3 to 12 rs', GA),
        (22.0, 'Relay orbit, mission start', 'its clock runs 0.9653x', TE)]
for i, (r, name, note, col) in enumerate(rows):
    y = 192 + i * 40
    b.append(f'<circle cx="{f1(LX(r))}" cy="164" r="4" fill="{col}" filter="url(#glow)"/>')
    au = r * RS_KM / 1.496e8
    b.append(f'<circle cx="{x0 + 4}" cy="{y}" r="4" fill="{col}"/>')
    b.append(t(x0 + 16, y + 4, name, 13, col, 'start', 600) + t(x0 + 16, y + 20, note, 11, MU))
    b.append(t(x1 + 28, y + 4, f'{r:g} rs', 13, col, 'end', 600) + t(x1 + 28, y + 20, f'{au:.1f} AU', 11, MU, 'end'))
cw = (W_ - 64 - 3 * 12) / 4
for i, (n, u, l, c) in enumerate([('1e8', 'Suns', 'assumed mass (game)', GA), ('1.97', 'AU', '1 rs = 295 million km', INK),
                                  ('16.4', 'min', 'rs/c: light crosses 1 rs', TE), (f'{N["shadow_deg"]:.2f}', '°', 'shadow radius seen from 22 rs', GA2)]):
    b.append(card(32 + i * (cw + 12), 448, cw, n, u, l, c, 62))
files['gg-01-anatomy.svg'] = doc(1, 'Anatomy of a black hole', 'Every number in the experience is measured in rs, the Schwarzschild radius', '\n'.join(b), ex)


# ================================================================== 02 cahaya dibelokkan
b = []
b.append(panel(32, 112, 620, 400, 'LIGHT RAYS FROM THE LEFT · TO SCALE', 'p2'))
cx, cy, s = 372, 330, 26.0
X0 = (40 - cx) / s
stop = lambda x, y, vx, vy: (x > (660 - cx) / s) or (abs(y) > 7.4 and vy * y > 0) or (x < X0 - 0.5)
b.append('<g clip-path="url(#p2)">')
b.append(f'<rect x="{cx}" y="{f1(cy - B_C * s)}" width="300" height="{f1(2 * B_C * s)}" fill="#000" opacity="0.5"/>')
defl = {}
for sgn in (1, -1):
    for bb in (0.5, 1.2, 1.9, 2.45, B_C + 0.0004, 2.8, 3.3, 4.0, 4.9, 5.9, 7.0):
        near = abs(bb - B_C) < 0.03
        if near and sgn < 0: continue
        P, cap, (vx, vy) = ray(X0, sgn * bb, 1.0, 0.0, stop)
        if not cap: defl[bb] = math.degrees(math.atan2(-sgn * vy, vx))
        col = RE if cap else (TE if near else GA2)
        op = 1.0 if near else (0.6 if cap else 0.75)
        b.append(f'<path d="{path([(cx + x * s, cy - y * s) for x, y in P[::3] + [P[-1]]])}" fill="none" stroke="{col}" stroke-opacity="{op}" stroke-width="{2.2 if near else 1.3}"{" filter=\"url(#glow)\"" if near else ""}/>')
b.append(f'<circle cx="{cx}" cy="{cy}" r="{f1(1.5 * s)}" fill="none" stroke="{TE}" stroke-opacity="0.7" stroke-dasharray="4 4"/>')
b.append(hole(cx, cy, s))
b.append('</g>')
b.append(f'<line x1="636" y1="{f1(cy - B_C * s)}" x2="636" y2="{f1(cy + B_C * s)}" stroke="{INK}" marker-start="url(#tick)" marker-end="url(#tick)"/>')
b.append(pill(628, cy, 'shadow, 5.2 rs wide', 11.5, INK, 'end'))
b.append(callout(cx - 0.7 * s, cy + 0.7 * s, 60, 488, 'b < 2.598 rs: captured', RE, 11.5))
b.append(callout(cx - 0.3 * s, cy - 1.47 * s, 60, 150, 'b just above 2.598 rs: loops the photon sphere', TE, 11.5))
b.append(callout(cx + 5.0 * s, cy + 6.35 * s, 636, 488, f'b = 5.9 rs: bent {defl[5.9]:.0f}°', GA2, 11.5, 'end'))
b.append(card(672, 112, 256, '2.598', 'rs', 'critical impact parameter, 3√3/2 rs', TE))
b.append(card(672, 190, 256, f'{N["shadow_deg"]:.2f}', '°', 'shadow radius seen from the relay', GA))
b.append(card(672, 268, 256, f'{defl[7.0]:.0f}', '°', f'bend at b = 7 rs (weak-field guess {math.degrees(2 / 7):.0f}°)', GA2))
for i, line in enumerate(['The hole looks black because every ray', 'aimed inside 2.598 rs falls in. Rays',
                          'just outside wrap around the photon', 'sphere and come back out: the thin', 'bright ring around the shadow.']):
    b.append(t(672, 370 + i * 19, line, 12.5, INK))
b.append(pill(672, 488, "u'' = -u + 1.5 u²  (u = rs / r)", 12, MU))
files['gg-02-light-bending.svg'] = doc(2, 'Bent light', 'Rays are traced through curved space; the shadow is 2.6 times wider than the horizon', '\n'.join(b))
N['defl'] = defl


# ================================================================== 03 citra piringan (atas dan bawah)
EL = 8.0                                            # pengamat 8 derajat di atas bidang piringan
D0 = 30.0
ox, oy = D0 * math.cos(math.radians(EL)), D0 * math.sin(math.radians(EL))
dx, dy = -ox / D0, -oy / D0
def shoot(bb, record=False):
    """Jejak mundur dari pengamat dengan offset b (tegak lurus garis pandang) sampai menembus bidang piringan 3-12 rs."""
    px, py = ox - dy * bb, oy + dx * bb
    # integrasi manual dengan deteksi bidang y = 0
    pts_ = [(px, py)]; vx, vy = dx, dy; prev = (px, py)
    hh = (px * vy - py * vx) ** 2
    for _ in range(60000):
        r = math.hypot(px, py)
        if r < 1: return pts_, ('hole', None)
        if r > D0 + 2 and (px * vx + py * vy) > 0: return pts_, ('sky', None)
        h = 0.01 * min(1.0, (r - 0.6) / 2)
        k = -1.5 * hh / r ** 5
        vx += k * px * h; vy += k * py * h; nx, ny = px + vx * h, py + vy * h
        if (py > 0) != (ny > 0):
            xc = px + (nx - px) * (py / (py - ny))
            if 3 <= abs(xc) <= 12:
                pts_.append((xc, 0.0))
                face = 'top' if py > 0 else 'bottom'
                return pts_, ('far ' + face if xc < 0 else 'near ' + face, xc)
        px, py = nx, ny; pts_.append((px, py))
    return pts_, ('none', None)
cats = {}
for i in range(-1600, 1601):
    bb = i * 0.01
    _, (c, xc) = shoot(bb)
    if c not in ('hole', 'sky', 'none'): cats.setdefault(c, []).append(bb)
b = []
b.append(panel(32, 112, 470, 400, 'SIDE VIEW · RAYS TRACED BACK FROM YOU', 'p3'))
cx, cy, s = 300, 312, 16.0
b.append('<g clip-path="url(#p3)">')
b.append(f'<rect x="{f1(cx - 12 * s)}" y="{cy - 2}" width="{f1(9 * s)}" height="4" rx="2" fill="{GA}" filter="url(#glow)"/>')
b.append(f'<rect x="{f1(cx + 3 * s)}" y="{cy - 2}" width="{f1(9 * s)}" height="4" rx="2" fill="{GA}" filter="url(#glow)"/>')
pick = {'far top': (TE, 'top'), 'far bottom': (VI, 'bottom'), 'near top': (GA2, 'near')}
chosen = {}
for c, (col, _) in pick.items():
    L_ = sorted(cats.get(c, []), key=abs)
    if not L_: continue
    bb = L_[len(L_) // 3]
    chosen[c] = bb
    P, _ = shoot(bb)
    b.append(f'<path d="{path([(cx + x * s, cy - y * s) for x, y in P[::4] + [P[-1]]])}" fill="none" stroke="{col}" stroke-width="2" filter="url(#glow)"/>')
    hx, hy = P[-1]
    b.append(f'<circle cx="{f1(cx + hx * s)}" cy="{f1(cy - hy * s)}" r="4.5" fill="{col}"/>')
b.append(hole(cx, cy, s))
b.append('</g>')
b.append(pill(486, 166, f'to you: 30 rs away, {EL:.0f}° above the disk →', 11.5, INK, 'end'))
b.append(pill(cx - 7.5 * s, 352, 'far side of the disk', 11.5, GA, 'middle'))
b.append(pill(cx + 7.5 * s, 352, 'near side', 11.5, GA, 'middle'))
# citra (skematik dari rentang b hasil jejak)
b.append(panel(522, 112, 406, 400, 'WHAT YOU SEE · SCHEMATIC'))
icx, icy, isc = 725, 318, 13.5
rng = {c: (min(abs(v) for v in L_), max(abs(v) for v in L_)) for c, L_ in cats.items()}
def ann(r0, r1, a0, a1, col, op):
    A = [i / 60 for i in range(61)]
    o_ = [(icx + r1 * isc * math.cos(a0 + (a1 - a0) * u), icy - r1 * isc * math.sin(a0 + (a1 - a0) * u)) for u in A]
    i_ = [(icx + r0 * isc * math.cos(a1 - (a1 - a0) * u), icy - r0 * isc * math.sin(a1 - (a1 - a0) * u)) for u in A]
    return f'<polygon points="{pts(o_ + i_)}" fill="{col}" opacity="{op}" filter="url(#glow)"/>'
ft, fb = rng['far top'], rng['far bottom']
b.append(ann(ft[0], min(ft[1], 13), 0.0, math.pi, GA, 0.85))
b.append(ann(fb[0], min(fb[1], 13), math.pi, 2 * math.pi, '#c9733a', 0.75))
b.append(f'<circle cx="{icx}" cy="{icy}" r="{f1(B_C * isc + 1.5)}" fill="none" stroke="{GA2}" stroke-width="1.6" filter="url(#glow)"/>')
b.append(f'<circle cx="{icx}" cy="{icy}" r="{f1(B_C * isc)}" fill="#000"/>')
sE = math.sin(math.radians(EL))
b.append(f'<path d="M{f1(icx - 12 * isc)} {icy} A{f1(12 * isc)} {f1(12 * isc * sE)} 0 0 0 {f1(icx + 12 * isc)} {icy} L{f1(icx + 3 * isc)} {icy} A{f1(3 * isc)} {f1(3 * isc * sE)} 0 0 1 {f1(icx - 3 * isc)} {icy} Z" fill="{GA2}" filter="url(#glow)"/>')
b.append(callout(icx + 1, icy - ft[0] * isc - 6, 912, 156, 'far side, top face, bent over', TE, 11.5, 'end'))
b.append(callout(icx, icy + fb[0] * isc + 8, 540, 488, 'far side, underside, bent under', VI, 11.5))
b.append(callout(icx + 9 * isc, icy + 4, 912, 440, 'near side, direct', GA2, 11.5, 'end'))
b.append(callout(icx - 2.2 * isc, icy - 0.8 * isc, 540, 200, 'shadow', INK, 11.5))
files['gg-03-disk-image.svg'] = doc(3, 'Why you see the top and the bottom of the disk', 'Light from behind the hole bends over and under it, so the far side shows as arcs', '\n'.join(b))
N['img_top'] = ft; N['img_bot'] = fb


# ================================================================== 04 warna dan terang piringan
TN = max(T_disk(3 + i * 0.001) for i in range(9000))
INC = 70.0
def disk_svg(cx, cy, s, physics):
    o = []; si, ci = math.sin(math.radians(INC)), math.cos(math.radians(INC))
    rs_ = [3 * (4 ** (j / 18)) for j in range(19)]
    cells = []
    for j in range(18):
        for k in range(72):
            r0_, r1_ = rs_[j], rs_[j + 1]; a0, a1 = k * math.tau / 72, (k + 1) * math.tau / 72
            rm, am = (r0_ + r1_) / 2, (a0 + a1) / 2
            v = v_gas(rm); bl = -v * math.cos(am) * si
            D = 1 / (math.sqrt(1 - v * v) * (1 - bl)); g = math.sqrt(1 - 1 / rm) / math.sqrt(1 - 1 / 22)
            sh = g * D if physics else 1.0
            Tn = T_disk(rm) / TN
            col = kelvin(7500 * Tn * sh)
            I = (Tn * sh) ** 4 * (1.0 if physics else 1.0)
            lum = (1 - math.exp(-1.2 * I)) ** 0.6
            col = [c * lum for c in col]
            P = [(cx + rr_ * s * math.cos(aa), cy - rr_ * s * math.sin(aa) * ci) for rr_, aa in ((r0_, a0), (r1_, a0), (r1_, a1), (r0_, a1))]
            cells.append((math.sin(am), P, col))
    far = [c for c in cells if c[0] >= 0]; near = [c for c in cells if c[0] < 0]
    for _, P, col in far: o.append(f'<polygon points="{pts(P)}" fill="{hexc(col)}" stroke="{hexc(col)}" stroke-width="0.6"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{f1(s * 1.0)}" fill="#000"/>')
    for _, P, col in near: o.append(f'<polygon points="{pts(P)}" fill="{hexc(col)}" stroke="{hexc(col)}" stroke-width="0.6"/>')
    return ''.join(o)
b = []
b.append(panel(32, 112, 450, 400, f'SEEN {90 - INC:.0f}° ABOVE THE DISK · NO LENSING'))
b.append(t(52, 162, 'FILM MODE (game default)', 11.5, MU, 'start', 600))
b.append(f'<g filter="url(#glow)">{disk_svg(257, 232, 15.5, False)}</g>')
b.append(t(52, 334, 'PHYSICS: DOPPLER + BEAMING + REDSHIFT', 11.5, MU, 'start', 600))
b.append(f'<g filter="url(#glow)">{disk_svg(257, 410, 15.5, True)}</g>')
b.append(pill(52, 492, 'coming toward you: hotter, brighter', 11, TE))
b.append(pill(462, 492, 'moving away: redder, dimmer', 11, RE, 'end'))
# grafik rasio terang vs r
x0, y0, w, h = 560, 128, 360, 180
X = lambda r: x0 + (r - 3) / 9 * w
Y = lambda q: y0 + h - math.log10(q) / 2 * h
b.append(axes(x0, y0, w, h, (3, 6, 9, 12), (1, 10, 100), X, Y, 'radius in the disk (rs)', 'bright / dim side', lambda v: f'{v}', lambda v: f'{v}x'))
for inc, col, lab in ((90, GA, 'edge-on'), (INC, GA2, f'{90 - INC:.0f}° above')):
    sI = math.sin(math.radians(inc))
    P = [(X(r), Y(((1 + v_gas(r) * sI) / (1 - v_gas(r) * sI)) ** 4)) for r in [3 + i * 0.1 for i in range(91)]]
    b.append(f'<path d="{path(P)}" fill="none" stroke="{col}" stroke-width="2.4" filter="url(#glow)"/>')
    b.append(pill(P[-1][0] - 4, P[-1][1] + (-16 if inc == 90 else 16), lab, 10.5, col, 'end'))
N['beam_70'] = ((1 + v_gas(3) * math.sin(math.radians(INC))) / (1 - v_gas(3) * math.sin(math.radians(INC)))) ** 4
b.append(callout(X(3), Y(81), X(4.6), Y(81) - 2, '81x at the ISCO', GA, 11.5))
# suhu
x0, y0, w, h = 560, 368, 360, 90
Yt = lambda q: y0 + h - q * h
b.append(axes(x0, y0, w, h, (3, 6, 9, 12), (0, 0.5, 1), X, Yt, 'radius (rs)', 'temperature', lambda v: f'{v}', lambda v: f'{v:g}'))
P = [(X(r), Yt(T_disk(r) / TN)) for r in [3 + i * 0.05 for i in range(181)]]
b.append(f'<path d="{path(P)}" fill="none" stroke="{GA2}" stroke-width="2.2"/>')
rmax = max([3 + i * 0.001 for i in range(9000)], key=T_disk)
b.append(callout(X(rmax), Yt(1), X(rmax) + 40, Yt(1) + 8, f'hottest at {rmax:.1f} rs', GA2, 10.5))
N['T_peak_r'] = rmax
files['gg-04-disk-doppler.svg'] = doc(4, 'Colour and brightness of the disk', f'Gas at the inner edge orbits at {N["v_isco"]:.1f} c: one side is blue-white and bright, the other red and dim', '\n'.join(b))


# ================================================================== 05 jatuh ke horizon
b = []
x0, y0, w, h = 92, 128, 470, 270
TMAX = 100.0
X = lambda T: x0 + T / TMAX * w
Y = lambda r: y0 + h - r / 22 * h
b.append(axes(x0, y0, w, h, (0, 20, 40, 60, 80, 100), (0, 1, 5, 10, 15, 20), X, Y,
              'time in rs/c  (100 rs/c = 27.4 hours for 1e8 Suns)', 'distance from centre (rs)', lambda v: f'{v}', lambda v: f'{v}'))
b.append(f'<rect x="{x0}" y="{f1(Y(1))}" width="{w}" height="{f1(Y(0) - Y(1))}" fill="#000" opacity="0.7"/>')
b.append(f'<line x1="{x0}" y1="{f1(Y(1))}" x2="{x0 + w}" y2="{f1(Y(1))}" stroke="{RE}" stroke-width="1.4" stroke-dasharray="5 4"/>')
b.append(t(x0 + w - 6, Y(1) - 6, 'event horizon', 11, RE, 'end'))
own = [(X(tau_fall(22, r)), Y(r)) for r in [22 - 22 * i / 400 for i in range(401)]]
b.append(f'<path d="{path(own)}" fill="none" stroke="{GA}" stroke-width="2.6" filter="url(#glow)"/>')
seen = []
for i in range(600):
    r = 22 - (22 - 1.0000001) * (1 - (1 - i / 599) ** 3)
    if r <= 1.0: break
    Ta = tau_fall(22, r) + Gout(22) - Gout(r)
    if Ta > TMAX: break
    seen.append((X(Ta * N['relay_clock']), Y(r)))
b.append(f'<path d="{path(seen)}" fill="none" stroke="{TE}" stroke-width="2.2" stroke-dasharray="7 5"/>')
th = tau_fall(22, 1)
b.append(f'<circle cx="{f1(X(th))}" cy="{f1(Y(1))}" r="4" fill="{GA}"/>')
b.append(callout(X(tau_fall(22, 15)), Y(15), 200, 160, 'your own clock: proper time', GA))
b.append(callout(X(th), Y(1), 330, 380, f'horizon after {th:.2f} rs/c = {N["fall_hours"]:.2f} h', GA))
b.append(callout(X(88), Y(1.04), 452, 330, 'what the relay sees: never crosses', TE, 11.5))
# pasang surut (log)
x0, y0, w, h = 650, 128, 270, 270
lr0, lr1 = math.log10(22), math.log10(0.003)
Xr = lambda r: x0 + (math.log10(r) - lr0) / (lr1 - lr0) * w
Yg = lambda gg: y0 + h - (math.log10(gg) + 10) / 14 * h
b.append(axes(x0, y0, w, h, (20, 1, 0.1, 0.01), (1e-8, 1e-4, 1, 1e3), Xr, Yg, 'distance from centre (rs, log)', 'stretch on a 2 m body (g)',
              lambda v: f'{v:g}', lambda v: '1' if v == 1 else ('1000' if v == 1e3 else f'1e{int(math.log10(v))}')))
P = [(Xr(r), Yg(tidal_g(r))) for r in [10 ** (lr0 + (lr1 - lr0) * i / 200) for i in range(201)]]
b.append(f'<path d="{path(P)}" fill="none" stroke="{VI}" stroke-width="2.4" filter="url(#glow)"/>')
b.append(f'<line x1="{f1(Xr(1))}" y1="{y0}" x2="{f1(Xr(1))}" y2="{y0 + h}" stroke="{RE}" stroke-dasharray="5 4"/>')
b.append(f'<line x1="{x0}" y1="{f1(Yg(1))}" x2="{x0 + w}" y2="{f1(Yg(1))}" stroke="{INK}" stroke-opacity="0.5" stroke-dasharray="3 4"/>')
b.append(callout(Xr(1), Yg(tidal_g(1)), Xr(1) + 12, Yg(tidal_g(1)) + 40, f'horizon: {N["tide_h"]:.1e} g'.replace('e-0', 'e-'), RE, 11))
b.append(callout(Xr(N['tide_1g_r']), Yg(1), Xr(N['tide_1g_r']) - 10, Yg(1) - 40, f'1 g at {N["tide_1g_r"]:.4f} rs', VI, 11, 'end'))
cw = (W_ - 64 - 3 * 12) / 4
for i, (n, u, l, c) in enumerate([(f'{N["fall_hours"]:.2f}', 'h', 'relay to horizon, your clock', GA), (f'{N["inside_s"]:.0f}', 's', 'horizon to the centre', RE),
                                  ('2e-7', 'g', 'stretch felt at the horizon', INK), (f'{N["tide_1g_s"]:.1f}', 's', 'of real stretching, at the end', VI)]):
    b.append(card(32 + i * (cw + 12), 466, cw, n, u, l, c, 58))
files['gg-05-fall.svg'] = doc(5, 'Falling in', 'Straight in from the relay at 22 rs, starting with the local free-fall speed (E = 1)', '\n'.join(b), h=H_)


# ================================================================== 06 diagram ruang-waktu, jam membeku
b = []
x0, y0, w, h = 92, 120, 560, 350
TM = 110.0
X = lambda r: x0 + r / 23 * w
Y = lambda T: y0 + h - T / TM * h
b.append(f'<clipPath id="p6"><rect x="{x0}" y="{y0}" width="{w}" height="{h}"/></clipPath>')
b.append(axes(x0, y0, w, h, (0, 1, 5, 10, 15, 20), (0, 20, 40, 60, 80, 100), X, Y, 'distance from centre (rs)', 'time (rs/c, rain-frame clock)', lambda v: f'{v}', lambda v: f'{v}'))
b.append(f'<g clip-path="url(#p6)">')
b.append(f'<rect x="{x0}" y="{y0}" width="{f1(X(1) - x0)}" height="{h}" fill="#000" opacity="0.6"/>')
b.append(f'<line x1="{f1(X(1))}" y1="{y0}" x2="{f1(X(1))}" y2="{y0 + h}" stroke="{RE}" stroke-width="1.6" stroke-dasharray="5 4"/>')
b.append(f'<line x1="{f1(X(22))}" y1="{y0}" x2="{f1(X(22))}" y2="{y0 + h}" stroke="{TE}" stroke-width="3" filter="url(#glow)"/>')
craft = [(X(r), Y(tau_fall(22, r))) for r in [22 - 22 * i / 300 for i in range(301)]]
b.append(f'<path d="{path(craft)}" fill="none" stroke="{GA}" stroke-width="2.6" filter="url(#glow)"/>')
arrivals = []
for te in (0, 10, 20, 30, 40, 50, 60, 65, 67, 67.8, 68.0, 68.4):
    re_ = (22 ** 1.5 - 1.5 * te) ** (2 / 3)
    if re_ > 1:
        P = []
        for i in range(400):
            r = re_ + (22 - re_) * (i / 399) ** 1.6
            P.append((X(r), Y(te + Gout(r) - Gout(re_))))
        Ta = te + Gout(22) - Gout(re_); arrivals.append((te, Ta))
        b.append(f'<path d="{path(P)}" fill="none" stroke="{GA2}" stroke-opacity="0.75" stroke-width="1.3"/>')
    else:
        # di dalam horizon sinar "keluar" pun bergerak ke dalam: dr/dT = 1 - 1/akar(r) < 0
        r, T = re_, te; P = [(X(r), Y(T))]
        while r > 0.05:
            dT = 0.002; r += (1 - 1 / math.sqrt(r)) * dT; T += dT; P.append((X(r), Y(T)))
        b.append(f'<path d="{path(P)}" fill="none" stroke="{RE}" stroke-width="1.6"/>')
    b.append(f'<circle cx="{f1(X(re_))}" cy="{f1(Y(te))}" r="3" fill="{GA2}"/>')
for r in (16, 8, 3, 1.0, 0.5):                                                          # kerucut cahaya
    T = tau_fall(22, r); L_ = 2.2
    so, si = 1 - 1 / math.sqrt(r), -1 - 1 / math.sqrt(r)
    for sl, col in ((so, GA2), (si, MU)):
        n_ = math.hypot(sl * w / 23, h / TM)
        ex_, ey_ = sl * w / 23 / n_, (h / TM) / n_
        b.append(f'<line x1="{f1(X(r))}" y1="{f1(Y(T))}" x2="{f1(X(r) + ex_ * 26)}" y2="{f1(Y(T) - ey_ * 26)}" stroke="#fff" stroke-width="1.6"/>')
    b.append(f'<path d="M{f1(X(r))} {f1(Y(T))} L{f1(X(r) + so * w / 23 / math.hypot(so * w / 23, h / TM) * 26)} {f1(Y(T) - (h / TM) / math.hypot(so * w / 23, h / TM) * 26)} L{f1(X(r) + si * w / 23 / math.hypot(si * w / 23, h / TM) * 26)} {f1(Y(T) - (h / TM) / math.hypot(si * w / 23, h / TM) * 26)} Z" fill="#fff" opacity="0.12"/>')
b.append('</g>')
for te, Ta in arrivals:
    if Ta < TM: b.append(f'<line x1="{f1(X(22) - 6)}" y1="{f1(Y(Ta))}" x2="{f1(X(22) + 6)}" y2="{f1(Y(Ta))}" stroke="{TE}" stroke-width="2"/>')
b.append(pill(X(22), y0 - 12, 'relay', 11.5, TE, 'middle'))
b.append(callout(X(9), Y(tau_fall(22, 9)), 260, 300, 'your fall', GA))
b.append(callout(X(0.5) + 4, Y(tau_fall(22, 0.5)) + 6, 150, 448, 'inside: even outgoing light moves in', RE, 11))
b.append(callout(X(16) + 16, Y(tau_fall(22, 16)) - 12, 470, 410, 'light cones tip inward', INK, 11))
re68 = (22 ** 1.5 - 1.5 * 68.0) ** (2 / 3)
b.append(callout(X(3.0), Y(68.0 + Gout(3.0) - Gout(re68)), 250, 150, 'pulses sent near the horizon climb out slowly', GA2, 11))
gaps = [b_[1] - a_[1] for a_, b_ in zip(arrivals, arrivals[1:])]
b.append(card(676, 120, 252, f'{N["relay_clock"]:.4f}', 'x', 'relay clock vs far away', TE))
b.append(card(676, 198, 252, f'{2 * TS / 60:.1f}', 'min', 'redshift grows e-fold (2 rs/c)', GA))
b.append(card(676, 276, 252, '∞', '', 'wait for the pulse sent at the horizon', RE))
for i, line in enumerate(['Pulses leave the craft every 10 rs/c', 'of its own time, then closer together.', 'They reach the relay further and',
                          'further apart. The last one sent', 'from inside never arrives.']):
    b.append(t(676, 378 + i * 19, line, 12.5, INK))
files['gg-06-spacetime.svg'] = doc(6, 'The frozen clock', 'Time goes up, distance goes right; light cones tilt toward the hole and close at the horizon', '\n'.join(b))
N['arrivals'] = arrivals


# ================================================================== 07 orbit, sudut kritis, zoom-whirl
b = []
x0, y0, w, h = 92, 132, 330, 260
X = lambda r: x0 + (r - 1) / 15 * w
Y = lambda V: y0 + h - (V - 0.85) / 0.30 * h
b.append(axes(x0, y0, w, h, (1, 2, 3, 6, 10, 16), (0.9, 1.0, 1.1), X, Y, 'r (rs)', 'effective potential, E²', lambda v: f'{v}', lambda v: f'{v:g}'))
b.append(f'<clipPath id="p7"><rect x="{x0}" y="{y0}" width="{w}" height="{h}"/></clipPath><g clip-path="url(#p7)">')
for L, col, lab in ((1.6, MU, 'L = 1.6'), (math.sqrt(3), INK, 'L = √3, ISCO'), (2.0, VI, 'L = 2, critical'), (2.3, GA2, 'L = 2.3')):
    P = [(X(r), Y((1 - 1 / r) * (1 + L * L / r ** 2))) for r in [1 + i * 0.02 for i in range(751)]]
    b.append(f'<path d="{path(P)}" fill="none" stroke="{col}" stroke-width="2"/>')
b.append(f'<line x1="{x0}" y1="{f1(Y(1))}" x2="{x0 + w}" y2="{f1(Y(1))}" stroke="{GA}" stroke-dasharray="6 4" stroke-width="1.6"/>')
b.append('</g>')
for i, (col, lab) in enumerate(((GA2, 'L = 2.3: bounces back'), (VI, 'L = 2: peak = 1 at 2 rs'), (INK, 'L = √3: ISCO at 3 rs'), (MU, 'L = 1.6: no barrier'))):
    yy = y0 + 18 + i * 17
    b.append(f'<line x1="{x0 + w - 150}" y1="{yy}" x2="{x0 + w - 132}" y2="{yy}" stroke="{col}" stroke-width="2.4"/>' + t(x0 + w - 126, yy + 4, lab, 10.5, col))
b.append(pill(x0 + w - 4, Y(1) + 14, 'E = 1: free-fall energy', 10.5, GA, 'end'))
# lintasan dari 22 rs
cx, cy, s = 580, 360, 15.0
b.append(panel(462, 112, 466, 400, 'AIMED FROM 22 RS AT FREE-FALL SPEED', 'p7b'))
b.append('<g clip-path="url(#p7b)">')
b.append(f'<circle cx="{cx}" cy="{cy}" r="{f1(2 * s)}" fill="none" stroke="{VI}" stroke-opacity="0.6" stroke-dasharray="3 4"/>')
res = {}
for d, col in ((12, RE), (23.0, '#ff9a7a'), (24.6199, VI), (26.0, GA2), (40.0, TE)):
    L = 22 * math.sin(math.radians(d)) / math.sqrt(21)
    P, out, tau = orbit(22, L, 1.0, 6000, 1.0, 60)
    res[d] = (L, out, P[-1][1])
    Q = [(cx + r * s * math.cos(ph), cy - r * s * math.sin(ph)) for r, ph in P[::6] + [P[-1]]]
    b.append(f'<path d="{path(Q)}" fill="none" stroke="{col}" stroke-width="{2.4 if d == 24.6199 else 1.7}"{" filter=\"url(#glow)\"" if d == 24.6199 else ""}/>')
b.append(hole(cx, cy, s))
b.append(f'<g filter="url(#glow)"><circle cx="{f1(cx + 22 * s)}" cy="{cy}" r="5" fill="{GA}"/></g>')
b.append('</g>')
b.append(pill(cx + 22 * s - 6, cy - 22, 'start', 11, GA, 'end'))
lw = res[24.6199]
for i, (col, lab) in enumerate(((RE, '12°: straight in'), ('#ff9a7a', '23°: swings round, falls in'),
                                 (VI, f'24.62°: circles {math.degrees(lw[2]) / 360:.1f} times, falls in'), (GA2, '26°: slingshot, escapes'), (TE, '40°: gently bent'))):
    yy = 410 + i * 19
    b.append(f'<line x1="{720}" y1="{yy}" x2="{738}" y2="{yy}" stroke="{col}" stroke-width="2.4"/>' + t(744, yy + 4, lab, 11, col))
cw = (390 - 2 * 10) / 3
for i, (n, u, l, c) in enumerate([(f'{N["crit22"]:.2f}', '°', 'critical at 22 rs', VI), (f'{N["crit10"]:.2f}', '°', 'at 10 rs', INK), (f'{N["crit6"]:.2f}', '°', 'at 6 rs', INK)]):
    b.append(card(32 + i * (cw + 10), 446, cw, n, u, l, c, 58))
b.append(t(480, 156, f'+{N["zoom_deg"]:.1f}° of extra whirl for every 10x closer to the critical angle', 11, MU))
files['gg-07-orbits.svg'] = doc(7, 'Orbits and the critical angle', 'Aim a little off centre and you whirl around 2 rs; aim more and you fly past', '\n'.join(b))
N['whirl_turns'] = math.degrees(lw[2]) / 360; N['orbit_res'] = res


# ================================================================== 08 susur piringan dan aberasi
b = []
x0, y0, w, h = 92, 132, 360, 240
X = lambda r: x0 + (r - 3) / 9 * w
Y = lambda v: y0 + h - v * h
b.append(axes(x0, y0, w, h, (3, 4, 6, 9, 12), (0, 0.2, 0.4, 0.6, 0.8, 1.0), X, Y, 'radius (rs)', 'speed (c)', lambda v: f'{v}', lambda v: f'{v:g}'))
rs8 = [3 + i * 0.05 for i in range(181)]
for f_, col, lab in ((lambda r: 2 * v_gas(r) / (1 + v_gas(r) ** 2), RE, 'gas vs you, skimming against the flow'),
                     (v_gas, GA2, 'gas vs a hovering observer'),
                     (lambda r: 0.0, TE, 'gas vs you, skimming with the flow')):
    P = [(X(r), Y(f_(r))) for r in rs8]
    b.append(f'<path d="{path(P)}" fill="none" stroke="{col}" stroke-width="2.4" filter="url(#glow)"/>')
b.append(pill(X(5.4), Y(0.64) - 6, 'against the flow: 2v / (1 + v²)', 10.5, RE))
b.append(pill(X(7.6), Y(0.34) + 4, 'gas vs hovering', 10.5, GA2))
b.append(pill(X(7.6), Y(0.0) - 14, 'with the flow: almost 0', 10.5, TE))
b.append(card(32, 446, 200, '0.80', 'c', 'head-on gas at the ISCO', RE, 58))
b.append(card(242, 446, 230, f'{N["dust_J"] / 1e7:.1f}e7', 'J', '1 µg dust grain at 0.8 c (14 kg TNT)', GA, 58))
# aberasi
cx, cy, R0 = 714, 356, 140
bf = N['beta_fast']
b.append(panel(500, 112, 428, 400, f'SKY AHEAD WHEN FALLING AT {bf:.2f} c (FAST ARRIVAL)'))
b.append(f'<path d="M{cx - R0} {cy} A{R0} {R0} 0 0 1 {cx + R0} {cy}" fill="none" stroke="#fff" stroke-opacity="0.2"/>')
b.append(f'<line x1="{cx - R0 - 10}" y1="{cy}" x2="{cx + R0 + 10}" y2="{cy}" stroke="#fff" stroke-opacity="0.2"/>')
b.append(f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy - R0 - 24}" stroke="{GA}" stroke-width="2" marker-end="url(#ag)"/>')
b.append(t(cx + 8, cy - R0 - 16, 'direction of travel', 11.5, GA, 'start'))
for th in (15, 30, 45, 60, 75, 90):
    for sgn in (1, -1):
        a = math.radians(th); ap = math.acos((math.cos(a) + bf) / (1 + bf * math.cos(a)))
        X1, Y1 = cx + sgn * R0 * math.sin(a), cy - R0 * math.cos(a)
        X2, Y2 = cx + sgn * R0 * 0.78 * math.sin(ap), cy - R0 * 0.78 * math.cos(ap)
        b.append(f'<circle cx="{f1(X1)}" cy="{f1(Y1)}" r="3.4" fill="#fff" opacity="0.45"/>')
        b.append(f'<path d="M{f1(X1)} {f1(Y1)} L{f1(X2)} {f1(Y2)}" stroke="{TE}" stroke-opacity="0.5" stroke-width="1.2" marker-end="url(#at)"/>')
        b.append(f'<circle cx="{f1(X2)}" cy="{f1(Y2)}" r="3.6" fill="{TE}" filter="url(#glow)"/>')
a90 = N['ab90_fast']
b.append(f'<path d="M{cx} {cy} L{f1(cx + R0 * 0.78 * math.sin(math.radians(a90)))} {f1(cy - R0 * 0.78 * math.cos(math.radians(a90)))}" stroke="{TE}" stroke-dasharray="4 4"/>')
b.append(pill(cx, cy + 34, f'stars at 90° appear at {a90:.1f}° from ahead', 11.5, TE, 'middle'))
b.append(pill(cx, cy + 64, 'white: at rest · blue: as you see them', 11, MU, 'middle'))
b.append(t(520, 484, f'"0.86 c" in the game text is dr/dτ; the speed past a hovering', 11, MU))
b.append(t(520, 500, f'observer is {bf:.2f} c (E = 1.3 at 22 rs).', 11, MU))
files['gg-08-skim-aberration.svg'] = doc(8, 'Skimming the disk, squeezing the sky', 'Relative speed decides everything: head-on gas hits at 0.8 c, and the sky crowds forward', '\n'.join(b))


# ------------------------------------------------------------------ tulis
os.makedirs(OUT, exist_ok=True)
for n, s_ in files.items():
    open(os.path.join(OUT, n), 'w').write(s_)
print(f"shadow {N['shadow_deg']:.3f} deg; fall {N['fall_h']:.3f} rs/c = {N['fall_hours']:.3f} h; inside {N['inside_s']:.1f} s")
print(f"crit {N['crit22']:.3f} / {N['crit10']:.3f} / {N['crit6']:.3f} deg; zoom {N['zoom_deg']:.2f} deg; whirl 24.6199 deg = {N['whirl_turns']:.2f} turns")
print(f"ISCO gas {N['v_isco']:.3f} c, head-on {N['rel_isco']:.3f} c, beaming edge-on {N['beam_edge']:.1f}x, {90 - INC:.0f} deg above {N['beam_70']:.1f}x; T peak {N['T_peak_r']:.2f} rs")
print(f"tide horizon {N['tide_h']:.2e} g; 1 g at {N['tide_1g_r']:.5f} rs, {N['tide_1g_s']:.2f} s before; dust {N['dust_J']:.2e} J")
print(f"fast: beta {N['beta_fast']:.3f}, dr/dtau {N['drdtau_fast']:.3f}, 90 deg -> {N['ab90_fast']:.1f} deg; relay clock {N['relay_clock']:.4f}")
print('image b ranges: top', [round(v, 2) for v in N['img_top']], 'bottom', [round(v, 2) for v in N['img_bot']])
print('pulses (emit, arrive rs/c):', [(a, round(b_, 1)) for a, b_ in N['arrivals']])
print('orbits:', {d: (round(v[0], 4), v[1]) for d, v in N['orbit_res'].items()})
print(sorted(files))
