# Bangkitkan sketsa diagram SVG untuk konsep halaman detail Copper Corn Station.
# Pakai: python tools/diagram_detail_copper.py  (menulis docs/cooper-station/detail/gambar/cc-*.svg)
# Label English saja; angka dari R 1.000 m, g 9,81 m/s^2 (sama dengan CONFIG).
import math, os, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'cooper-station', 'detail', 'gambar')
g = 9.81; R = 1000.0; W = math.sqrt(g / R)
CU, TE, OR, INK, MU, LN, BG = '#d9bd62', '#8fd3dc', '#f3a55a', '#e8ecf2', '#9aa2ae', 'rgba(255,255,255,0.14)', '#0b0e14'
FONT = 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif'

def doc(w, h, title, sub, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="{FONT}">
<defs>
<marker id="a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{INK}"/></marker>
<marker id="ac" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{CU}"/></marker>
<marker id="at" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{TE}"/></marker>
<marker id="ao" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{OR}"/></marker>
</defs>
<rect width="{w}" height="{h}" rx="14" fill="{BG}"/>
<text x="24" y="36" font-size="18" font-weight="600" fill="{INK}">{title}</text>
<text x="24" y="58" font-size="13" fill="{MU}">{sub}</text>
{body}
</svg>
'''

def t(x, y, s, size=13, fill=INK, anchor='start', weight='400'):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{s}</text>'

def path(pts):
    return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts)

def person(x, y, ang, s=1.0, col=INK):
    # orang kecil berdiri di (x, y), kepala ke arah ang (radian, arah layar)
    ux, uy = math.cos(ang), math.sin(ang)
    hx, hy = x + ux * 14 * s, y + uy * 14 * s
    return (f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{hx:.1f}" y2="{hy:.1f}" stroke="{col}" stroke-width="2"/>'
            f'<circle cx="{x + ux * 18 * s:.1f}" cy="{y + uy * 18 * s:.1f}" r="{4 * s:.1f}" fill="{col}"/>')

def chart(x0, y0, w, h, xmax, ymax, xt, yt, xlab, ylab, xfmt=str, yfmt=str):
    o = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="none" stroke="{LN}"/>']
    for v in xt:
        X = x0 + v / xmax * w
        o.append(f'<line x1="{X:.1f}" y1="{y0}" x2="{X:.1f}" y2="{y0 + h}" stroke="{LN}"/>')
        o.append(t(X, y0 + h + 18, xfmt(v), 12, MU, 'middle'))
    for v in yt:
        Y = y0 + h - v / ymax * h
        o.append(f'<line x1="{x0}" y1="{Y:.1f}" x2="{x0 + w}" y2="{Y:.1f}" stroke="{LN}"/>')
        o.append(t(x0 - 8, Y + 4, yfmt(v), 12, MU, 'end'))
    o.append(t(x0 + w / 2, y0 + h + 38, xlab, 12, MU, 'middle'))
    o.append(f'<text transform="translate({x0 - 44} {y0 + h / 2}) rotate(-90)" font-size="12" fill="{MU}" text-anchor="middle">{ylab}</text>')
    return '\n'.join(o)

def mapper(x0, y0, w, h, xmax, ymax):
    return lambda x, y: (x0 + x / xmax * w, y0 + h - y / ymax * h)

files = {}

# 1 ---- stasiun sekilas ----
b = []
cx, cy, r = 190, 250, 140
b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{CU}" stroke-width="6"/>')
b.append(f'<circle cx="{cx}" cy="{cy}" r="5" fill="#fff8d8"/>')
b.append(t(cx + 10, cy - 8, 'sunline (axis)', 12, MU))
b.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + r * math.cos(math.radians(-35)):.1f}" y2="{cy + r * math.sin(math.radians(-35)):.1f}" stroke="{INK}" stroke-dasharray="4 4"/>')
b.append(t(cx + 20, cy - 70, 'R = 1,000 m', 13, INK, 'end'))
# arah putar: busur dengan panah (berlawanan jarum jam di layar)
a0, a1, rr = math.radians(200), math.radians(250), r + 22
b.append(f'<path d="M{cx + rr * math.cos(a0):.1f} {cy + rr * math.sin(a0):.1f} A{rr} {rr} 0 0 1 {cx + rr * math.cos(a1):.1f} {cy + rr * math.sin(a1):.1f}" fill="none" stroke="{INK}" stroke-width="2" marker-end="url(#a)"/>')
b.append(t(cx + 60, 100, 'spin: 1 turn every 63.4 s (0.946 rpm)', 12, MU))
# kecepatan tanah di bawah
b.append(f'<line x1="{cx}" y1="{cy + r}" x2="{cx - 78}" y2="{cy + r}" stroke="{TE}" stroke-width="2.5" marker-end="url(#at)"/>')
b.append(t(cx - 8, cy + r + 22, 'floor speed 99.05 m/s', 12, TE, 'middle'))
for ang in (90, 210, 330):
    A = math.radians(ang); px, py = cx + (r - 3) * math.cos(A), cy + (r - 3) * math.sin(A)
    b.append(person(px, py, A + math.pi, 1.0))
b.append(t(cx, 432, 'Cross-section: heads point to the axis', 12, MU, 'middle'))
# tampak samping: 8.000 m = 380 px, skala 0,0475 px/m
sx0, sy0, sc = 390, 205, 380 / 8000
L, D = 8000 * sc, 2000 * sc
b.append(f'<rect x="{sx0}" y="{sy0}" width="{L:.1f}" height="{D:.1f}" fill="none" stroke="{CU}" stroke-width="3"/>')
b.append(f'<line x1="{sx0}" y1="{sy0 + D / 2:.1f}" x2="{sx0 + L:.1f}" y2="{sy0 + D / 2:.1f}" stroke="#fff8d8" stroke-width="2" stroke-dasharray="6 4"/>')
b.append(f'<line x1="{sx0}" y1="{sy0 - 14}" x2="{sx0 + L:.1f}" y2="{sy0 - 14}" stroke="{INK}" marker-start="url(#a)" marker-end="url(#a)"/>')
b.append(t(sx0 + L / 2, sy0 - 22, 'L = 8,000 m', 13, INK, 'middle'))
b.append(t(sx0, sy0 + D + 22, 'End cap A', 12, INK)); b.append(t(sx0, sy0 + D + 38, 'lift, hub, despun dock', 12, MU))
b.append(t(sx0 + L, sy0 + D + 22, 'End cap B', 12, INK, 'end')); b.append(t(sx0 + L, sy0 + D + 38, 'sunlight enters at 25 deg', 12, MU, 'end'))
reach = 2 * R / math.tan(math.radians(25))   # 4.289 m
ex, ey = sx0 + L - reach * sc, sy0 + D
b.append(f'<line x1="{sx0 + L + 24:.1f}" y1="{sy0 - 24 * math.tan(math.radians(25)):.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{OR}" stroke-width="2" marker-end="url(#ao)"/>')
b.append(f'<line x1="{ex:.1f}" y1="{ey + 50:.1f}" x2="{sx0 + L:.1f}" y2="{ey + 50:.1f}" stroke="{OR}" marker-start="url(#ao)" marker-end="url(#ao)"/>')
b.append(t((ex + sx0 + L) / 2, ey + 68, 'sunlit reach about 4.3 km', 12, OR, 'middle'))
b.append(t(sx0 + L / 2, 400, 'Side view (to scale)', 12, MU, 'middle'))
b.append(t(sx0, 432, 'Orbit: 260,000 km from Saturn, one orbit every 37.57 h', 12, MU))
files['cc-01-station.svg'] = doc(800, 450, 'Copper Corn Station at a glance', 'An O\'Neill cylinder: the city lives on the inside wall', '\n'.join(b))

# 2 ---- gravitasi dari putaran ----
b = []
cx, cy, r = 180, 255, 130
b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{CU}" stroke-width="5"/>')
b.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="#fff8d8"/>')
for k in range(8):
    A = k * math.pi / 4
    b.append(f'<line x1="{cx + 30 * math.cos(A):.1f}" y1="{cy + 30 * math.sin(A):.1f}" x2="{cx + (r - 14) * math.cos(A):.1f}" y2="{cy + (r - 14) * math.sin(A):.1f}" stroke="{INK}" stroke-width="2" marker-end="url(#a)" opacity="0.85"/>')
for k in (0, 2, 4, 6):
    A = k * math.pi / 4 + math.pi / 8
    b.append(person(cx + (r - 3) * math.cos(A), cy + (r - 3) * math.sin(A), A + math.pi, 0.9, TE))
b.append(t(cx, 420, '"Down" = away from the axis, in every direction', 12, MU, 'middle'))
b.append(t(cx, 438, 'g = ω² r : the spin pushes you onto the wall', 12, MU, 'middle'))
X0, Y0, CW, CH = 420, 100, 340, 260
f = mapper(X0, Y0, CW, CH, 1000, 1.0)
b.append(chart(X0, Y0, CW, CH, 1000, 1.0, [0, 250, 500, 750, 1000], [0, 0.25, 0.5, 0.75, 1.0], 'height above the floor (m)', 'felt gravity (g)', lambda v: f'{v:,}', lambda v: f'{v:g}'))
b.append(f'<path d="{path([f(0, 1), f(1000, 0)])}" stroke="{CU}" stroke-width="3" fill="none"/>')
for h, lab, dx, dy in ((175, 'deck 175 m: 0.825 g', 10, -8), (500, 'halfway: 0.5 g', 10, -8), (1000, 'axis hub: 0 g', -10, -22)):
    x, y = f(h, (R - h) / R)
    b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{CU}"/>')
    if h == 1000: b.append(t(f(560, 0.05)[0], f(560, 0.05)[1], lab, 12, INK)); continue
    b.append(t(x + dx, y + dy, lab, 12, INK, 'end' if dx < 0 else 'start'))
b.append(t(X0, Y0 - 14, 'g(h) = ω² (R - h): weaker the higher you go', 12, INK))
files['cc-02-spin-gravity.svg'] = doc(800, 460, 'Gravity from spin', 'R 1,000 m, ω 0.09905 rad/s, 1 g on the floor', '\n'.join(b))

# 3 ---- Coriolis: bola dari dek ----
b = []
h0 = 176.5                      # dek 175 m + tangan 1,5 m (PHYS.handH)
r0 = R - h0; v0 = W * r0
tf = math.sqrt(R * R - r0 * r0) / v0
ang_b = math.atan2(math.sqrt(R * R - r0 * r0), r0)
miss = (W * tf - ang_b) * R
cx, cy, rr = 200, 255, 150; k = rr / R
# kerangka inersia: titik lepas tepat di bawah pusat (arah layar +y), putaran berlawanan jarum jam di layar (sudut layar berkurang)
def scr(a, rad):    # a = sudut dari arah bawah, positif = arah putaran (ke kanan di layar)
    return cx + rad * k * math.sin(a), cy + rad * k * math.cos(a)
b.append(f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="none" stroke="{CU}" stroke-width="4"/>')
P = scr(0, r0); I = scr(ang_b, R); F = scr(W * tf, R)
b.append(f'<line x1="{P[0]:.1f}" y1="{P[1]:.1f}" x2="{I[0]:.1f}" y2="{I[1]:.1f}" stroke="{TE}" stroke-width="2.5" stroke-dasharray="5 4"/>')
b.append(f'<circle cx="{P[0]:.1f}" cy="{P[1]:.1f}" r="4" fill="{TE}"/>')
b.append(f'<circle cx="{I[0]:.1f}" cy="{I[1]:.1f}" r="5" fill="{TE}"/>')
b.append(f'<circle cx="{F[0]:.1f}" cy="{F[1]:.1f}" r="5" fill="{OR}"/>')
arc = [scr(0, R + 18 / k)]
arcp = ' '.join(f'{scr(a, R + 18 / k)[0]:.1f},{scr(a, R + 18 / k)[1]:.1f}' for a in [i / 30 * W * tf for i in range(31)])
b.append(f'<polyline points="{arcp}" fill="none" stroke="{OR}" stroke-width="2" marker-end="url(#ao)"/>')
b.append(t(P[0] - 6, P[1] - 10, 'release', 12, TE, 'end'))
b.append(t(I[0] - 4, I[1] + 22, 'ball lands', 12, TE, 'end'))
b.append(t(F[0] + 12, F[1] - 2, 'tower base', 12, OR))
b.append(t(cx, cy - 22, 'Outside view (inertial):', 12, INK, 'middle'))
b.append(t(cx, cy - 6, 'ball flies straight at 81.6 m/s,', 12, MU, 'middle'))
b.append(t(cx, cy + 10, 'floor under it moves 99.05 m/s', 12, MU, 'middle'))
# kerangka berputar: lintasan relatif menara (x = busur di lantai, y = tinggi)
X0, Y0, CW, CH = 470, 92, 300, 290
pts = []
for i in range(81):
    tt = tf * i / 80
    xb, yb = v0 * tt, r0                     # inersia: lurus menyinggung
    rb = math.hypot(xb, yb); ab = math.atan2(xb, yb)
    rel = (ab - W * tt) * R                  # busur relatif terhadap titik di bawah menara
    pts.append((rel, R - rb))
f = mapper(X0, Y0, CW, CH, 1, 1)
def g2(x, y): return X0 + CW - 40 + x / 110 * (CW - 60), Y0 + CH - y / 200 * CH
b.append(f'<line x1="{X0}" y1="{Y0 + CH}" x2="{X0 + CW}" y2="{Y0 + CH}" stroke="{CU}" stroke-width="4"/>')
tx, ty = g2(0, 0); tx2, ty2 = g2(0, 175)
b.append(f'<rect x="{tx - 6:.1f}" y="{ty2:.1f}" width="12" height="{ty - ty2:.1f}" fill="#3a404b"/>')
b.append(f'<path d="{path([g2(x, y) for x, y in pts])}" fill="none" stroke="{TE}" stroke-width="2.5"/>')
lx, ly = g2(-miss, 0)
b.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="5" fill="{TE}"/>')
b.append(f'<line x1="{lx:.1f}" y1="{ly + 18:.1f}" x2="{tx:.1f}" y2="{ly + 18:.1f}" stroke="{INK}" marker-start="url(#a)" marker-end="url(#a)"/>')
b.append(t((lx + tx) / 2, ly + 36, f'{miss:.1f} m against the spin', 12, INK, 'middle'))
b.append(t(X0, Y0 - 10, 'On the station (rotating view): 176.5 m drop, 6.96 s', 12, INK))
b.append(f'<line x1="{X0 + 10}" y1="{Y0 + 24}" x2="{X0 + 90}" y2="{Y0 + 24}" stroke="{OR}" stroke-width="2" marker-end="url(#ao)"/>')
b.append(t(X0 + 96, Y0 + 28, 'spin direction', 12, OR))
b.append(t(24, 440, 'Same physics, two views: outside, the ball goes straight and the floor overtakes it.', 12, MU))
files['cc-03-coriolis-drop.svg'] = doc(800, 460, 'Why a dropped ball misses the tower', 'Coriolis: falling things lag behind the spin', '\n'.join(b))

# 4 ---- air mancur dan hujan ----
b = []
X0, Y0, CW, CH = 70, 110, 320, 260
vj = 10.0; tl = 2 * vj / g
def fz(x, y): return X0 + 80 + x / 3.0 * (CW - 100), Y0 + CH - y / 6.0 * CH
pts = []
for i in range(61):
    tt = tl * i / 60
    pts.append((W * (vj * tt * tt - g * tt ** 3 / 3), vj * tt - g * tt * tt / 2))
land = pts[-1][0]
b.append(f'<line x1="{X0}" y1="{Y0 + CH}" x2="{X0 + CW}" y2="{Y0 + CH}" stroke="{CU}" stroke-width="4"/>')
b.append(f'<line x1="{fz(0, 0)[0]:.1f}" y1="{fz(0, 0)[1]:.1f}" x2="{fz(0, 5.6)[0]:.1f}" y2="{fz(0, 5.6)[1]:.1f}" stroke="{INK}" stroke-dasharray="3 4" opacity="0.6"/>')
b.append(f'<path d="{path([fz(x, y) for x, y in pts])}" fill="none" stroke="{TE}" stroke-width="3"/>')
b.append(f'<line x1="{fz(0, 0)[0]:.1f}" y1="{Y0 + CH + 18}" x2="{fz(land, 0)[0]:.1f}" y2="{Y0 + CH + 18}" stroke="{INK}" marker-start="url(#a)" marker-end="url(#a)"/>')
b.append(t(fz(land / 2, 0)[0], Y0 + CH + 36, f'lands {land:.2f} m ahead (with the spin)', 12, INK, 'middle'))
b.append(t(fz(0, 0)[0] - 8, fz(0, 5.1)[1] + 4, '5.1 m', 12, MU, 'end'))
b.append(t(X0, Y0 - 14, 'Fountain: jet straight up at 10 m/s', 13, INK))
b.append(t(X0, Y0 + 4, 'rising water keeps its speed, gets ahead', 12, MU))
# hujan
X1 = 470; vt = 7.0; vl = 2 * W * vt * vt / g; deg = math.degrees(math.atan(vl / vt))
b.append(f'<line x1="{X1}" y1="{Y0 + CH}" x2="{X1 + 280}" y2="{Y0 + CH}" stroke="{CU}" stroke-width="4"/>')
for i in range(9):
    x = X1 + 40 + i * 28; y = Y0 + 30 + (i % 3) * 40
    dx = -60 * vl / vt
    b.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x + dx:.1f}" y2="{y + 60:.1f}" stroke="{TE}" stroke-width="2" stroke-linecap="round"/>')
ax, ay = X1 + 140, Y0 + 150
b.append(f'<line x1="{ax}" y1="{ay}" x2="{ax}" y2="{ay + 90}" stroke="{INK}" stroke-dasharray="3 4" opacity="0.6"/>')
b.append(f'<line x1="{ax}" y1="{ay}" x2="{ax - 90 * vl / vt:.1f}" y2="{ay + 90}" stroke="{TE}" stroke-width="2.5" marker-end="url(#at)"/>')
b.append(t(ax + 8, ay + 60, f'{deg:.1f} deg', 13, INK))
b.append(f'<line x1="{X1 + 180}" y1="{Y0 + CH - 20}" x2="{X1 + 260}" y2="{Y0 + CH - 20}" stroke="{OR}" stroke-width="2" marker-end="url(#ao)"/>')
b.append(t(X1 + 180, Y0 + CH - 28, 'spin', 12, OR))
b.append(t(X1, Y0 - 14, 'Rain: no wind, still tilted', 13, INK))
b.append(t(X1, Y0 + 4, 'falling 7 m/s, drifts 0.99 m/s against spin', 12, MU))
b.append(t(24, 440, 'Rule of thumb: moving up (toward the axis) = ahead; moving down = behind.', 12, MU))
files['cc-04-fountain-rain.svg'] = doc(800, 460, 'Fountain and rain: Coriolis both ways', 'Same force, opposite direction of travel', '\n'.join(b))

# 5 ---- berat saat bergerak ----
b = []
X0, Y0, CW, CH = 90, 95, 620, 270
f = mapper(X0, Y0, CW, CH, 150, 2.2)
b.append(chart(X0, Y0, CW, CH, 150, 2.2, [0, 30, 60, 90, 120, 150], [0, 0.5, 1.0, 1.5, 2.0], 'speed along the ring road (km/h)', 'felt weight (g)', str, lambda v: f'{v:g}'))
pro = [f(v, (W * R + v / 3.6) ** 2 / R / g) for v in range(0, 151, 5)]
ret = [f(v, (W * R - v / 3.6) ** 2 / R / g) for v in range(0, 151, 5)]
b.append(f'<path d="{path(pro)}" fill="none" stroke="{CU}" stroke-width="3"/>')
b.append(f'<path d="{path(ret)}" fill="none" stroke="{TE}" stroke-width="3"/>')
for v, col, lab in ((150, CU, '2.02 g'), (150, TE, '0.34 g')):
    gg = (W * R + (v / 3.6 if col == CU else -v / 3.6)) ** 2 / R / g
    x, y = f(v, gg)
    b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{col}"/>')
    b.append(t(x - 10, y - 10, lab, 13, col, 'end'))
b.append(t(f(50, 1.62)[0], f(50, 1.62)[1], 'with the spin: heavier', 13, CU))
b.append(t(f(20, 0.45)[0], f(20, 0.45)[1], 'against the spin: lighter', 13, TE))
b.append(t(X0 + 6, Y0 - 12, "g' = (ωR + v)² / R : zero g against the spin at 356.6 km/h (= floor speed)", 12, INK))
files['cc-05-moving-weight.svg'] = doc(800, 440, 'Your weight depends on where you are going', 'Motorbike in sport mode: up to 150 km/h', '\n'.join(b))

# 6 ---- lift ke sumbu ----
b = []
d = R - 6; a = 1.0; vm = 20.0; ta = vm / a; tc = (d - vm * ta) / vm; T = 2 * ta + tc
def hv(tt):
    if tt < ta: return a * tt * tt / 2, a * tt
    if tt < ta + tc: return vm * ta / 2 + vm * (tt - ta), vm
    u = T - tt; return d - a * u * u / 2, a * u
X0, Y0, CW, CH = 90, 95, 620, 120
f = mapper(X0, Y0, CW, CH, 70, 20)
b.append(chart(X0, Y0, CW, CH, 70, 20, [0, 10, 20, 30, 40, 50, 60, 70], [0, 10, 20], '', 'speed (m/s)', str, str))
b.append(f'<path d="{path([f(T * i / 140, hv(T * i / 140)[1]) for i in range(141)])}" fill="none" stroke="{TE}" stroke-width="3"/>')
for x0, x1, lab in ((0, ta, 'speed up 1 m/s²'), (ta, ta + tc, 'cruise 20 m/s'), (ta + tc, T, 'slow down')):
    b.append(t(f((x0 + x1) / 2, 0)[0], Y0 + 16, lab, 12, MU, 'middle'))
Y1 = 270
f2 = mapper(X0, Y1, CW, CH, 70, 1.0)
b.append(chart(X0, Y1, CW, CH, 70, 1.0, [0, 10, 20, 30, 40, 50, 60, 70], [0, 0.5, 1.0], 'time in the lift (s)', 'felt gravity (g)', str, lambda v: f'{v:g}'))
b.append(f'<path d="{path([f2(T * i / 140, (R - hv(T * i / 140)[0]) / R) for i in range(141)])}" fill="none" stroke="{CU}" stroke-width="3"/>')
xe, ye = f2(T, 0.006)
b.append(f'<circle cx="{xe:.1f}" cy="{ye:.1f}" r="5" fill="{CU}"/>')
b.append(t(xe - 8, ye - 10, f'hub: float ({T:.1f} s)', 12, CU, 'end'))
b.append(t(X0 + 6, 470, 'Real physics not yet in the game: at 20 m/s the cabin wall pushes you sideways with 2ωv = 0.40 g.', 12, MU))
files['cc-06-lift.svg'] = doc(800, 490, 'Lift to the zero-g axis', '994 m from the floor of end cap A to the hub, at normal speed (Shift = 5x)', '\n'.join(b))

# 7 ---- orbit dan gerhana ----
b = []
cx, cy, k = 400, 260, 160 / 260
rs, ro = 60.268 * k, 260 * k
b.append(f'<rect x="{cx:.1f}" y="{cy - rs:.1f}" width="{360:.1f}" height="{2 * rs:.1f}" fill="#000" opacity="0.65"/>')
b.append(f'<circle cx="{cx}" cy="{cy}" r="{ro:.1f}" fill="none" stroke="{INK}" stroke-dasharray="4 5" opacity="0.6"/>')
b.append(f'<circle cx="{cx}" cy="{cy}" r="{rs:.1f}" fill="#c9a46a"/>')
b.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rs * 2.1:.1f}" ry="{rs * 0.35:.1f}" fill="none" stroke="#e6d3a8" stroke-width="2" opacity="0.7"/>')
half = math.asin(60.268 / 260)
a0, a1 = -half, half
p0 = (cx + ro * math.cos(a0), cy + ro * math.sin(a0)); p1 = (cx + ro * math.cos(a1), cy + ro * math.sin(a1))
b.append(f'<path d="M{p0[0]:.1f} {p0[1]:.1f} A{ro:.1f} {ro:.1f} 0 0 1 {p1[0]:.1f} {p1[1]:.1f}" fill="none" stroke="{OR}" stroke-width="5"/>')
b.append(t(p1[0] + 12, cy + 4, 'eclipse arc', 12, OR))
for i in range(5):
    y = cy - 120 + i * 60
    b.append(f'<line x1="40" y1="{y}" x2="130" y2="{y}" stroke="{OR}" stroke-width="2" marker-end="url(#ao)"/>')
b.append(t(40, cy - 140, 'sunlight', 12, OR))
b.append(t(cx, cy + rs + 28, 'Saturn', 12, INK, 'middle'))
sa = math.radians(-120); st = (cx + ro * math.cos(sa), cy + ro * math.sin(sa))
b.append(f'<circle cx="{st[0]:.1f}" cy="{st[1]:.1f}" r="5" fill="{CU}"/>')
b.append(t(st[0] - 10, st[1] - 10, 'station, orbit 260,000 km', 12, CU, 'end'))
b.append(t(560, 112, 'orbit: 37.57 h', 13, INK))
b.append(t(560, 130, 'in shadow: 2.78 h per orbit', 13, OR))
b.append(t(560, 148, 'sunline fades, the limb glows', 12, MU))
b.append(t(24, 440, 'Top view of the orbit plane, to scale. Sun lies in the orbit plane, 25 deg from the station axis.', 12, MU))
files['cc-07-orbit-eclipse.svg'] = doc(800, 460, 'Orbit and Saturn eclipse', 'Press I in the game to jump to the next eclipse', '\n'.join(b))

# 8 ---- trik: peta bayangan silinder dibuka ----
b = []
cx, cy, r = 190, 170, 120
b.append(f'<path d="M{cx - r} {cy} A{r} {r} 0 0 0 {cx + r} {cy}" fill="none" stroke="{CU}" stroke-width="5"/>')
for ang in (200, 235, 270, 305, 340):
    A = math.radians(ang)
    px, py = cx + r * math.cos(A), cy - r * math.sin(A)
    ux, uy = -math.cos(A), math.sin(A)
    b.append(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{px + ux * 30:.1f}" y2="{py + uy * 30:.1f}" stroke="#7f8896" stroke-width="10"/>')
b.append(f'<rect x="{cx - 125}" y="{cy + 50}" width="250" height="85" fill="none" stroke="{TE}" stroke-width="2" stroke-dasharray="6 4"/>')
b.append(t(cx, cy + 165, 'flat shadow box vs curved floor:', 12, MU, 'middle'))
b.append(t(cx, cy + 181, 'wasted texels, walls cut off', 12, MU, 'middle'))
b.append(f'<line x1="350" y1="250" x2="430" y2="250" stroke="{INK}" stroke-width="2" marker-end="url(#a)"/>')
b.append(t(390, 240, 'shUnroll()', 13, INK, 'middle'))
X1, Y1 = 460, 290
b.append(f'<line x1="{X1}" y1="{Y1}" x2="{X1 + 300}" y2="{Y1}" stroke="{CU}" stroke-width="5"/>')
for i in range(5):
    x = X1 + 30 + i * 60
    b.append(f'<line x1="{x}" y1="{Y1}" x2="{x}" y2="{Y1 - 30}" stroke="#7f8896" stroke-width="10"/>')
b.append(f'<rect x="{X1}" y="{Y1 - 60}" width="300" height="70" fill="none" stroke="{TE}" stroke-width="2" stroke-dasharray="6 4"/>')
b.append(t(X1 + 150, Y1 + 30, 's = θR across, h = R - r up', 12, MU, 'middle'))
b.append(t(X1 + 150, Y1 + 46, 'the box hugs the floor everywhere', 12, MU, 'middle'))
b.append(t(24, 410, 'Depth and receivers both use (θ, r) -> (s, h), so shadows line up on the curved wall.', 12, MU))
files['cc-08-unrolled-shadow.svg'] = doc(800, 430, 'Behind the scenes: unrolling the cylinder for shadows', 'Shadow maps rendered in unrolled coordinates (stage 18b-3)', '\n'.join(b))

# 9 ---- trik: dua scene ----
b = []
b.append(f'<rect x="60" y="100" width="300" height="160" rx="10" fill="none" stroke="{OR}" stroke-width="2"/>')
b.append(t(80, 128, '1. farScene', 15, OR, 'start', '600'))
b.append(t(80, 150, '1 unit = 1,000 km', 13, INK))
for i, s in enumerate(['Saturn 60,268 km radius', 'orbit 260,000 km', 'stars, the Sun', 'drawn first, then depth cleared']):
    b.append(t(80, 182 + i * 22, s, 12, MU))
b.append(f'<rect x="440" y="100" width="300" height="160" rx="10" fill="none" stroke="{CU}" stroke-width="2"/>')
b.append(t(460, 128, '2. main scene', 15, CU, 'start', '600'))
b.append(t(460, 150, '1 unit = 1 m', 13, INK))
for i, s in enumerate(['station 8,000 m x 2,000 m', 'city, trees, people, cars', 'drawn on top with its own', 'near and far planes']):
    b.append(t(460, 182 + i * 22, s, 12, MU))
b.append(f'<line x1="360" y1="180" x2="440" y2="180" stroke="{INK}" stroke-width="2" marker-end="url(#a)"/>')
b.append(t(24, 300, 'Why: one scene in metres would put Saturn at 2.6e8 units, where a 32-bit float', 12, MU))
b.append(t(24, 318, 'can only step in 16 m, and one depth buffer cannot cover 0.1 m to 3e8 m.', 12, MU))
files['cc-09-two-scenes.svg'] = doc(800, 345, 'Behind the scenes: two scenes, two scales', 'Precision trick for a planet and a pebble in one frame', '\n'.join(b))

for n, s in files.items():
    open(os.path.join(OUT, n), 'w').write(s)
print(f'drop t {tf:.3f} s, miss {miss:.2f} m, v0 {v0:.2f} m/s; fountain {land:.3f} m; rain {deg:.2f} deg; lift {T:.1f} s')
print(sorted(files))
