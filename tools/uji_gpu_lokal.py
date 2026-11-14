#!/usr/bin/env python3
"""Uji GPU lokal otomatis (Fase A2, daftar `docs/app/daftar-uji-gpu.md`).

Membuka ketiga experience di Chrome SUNGGUHAN dengan GPU komputer ini (bukan SwiftShader), menjalankan titik uji,
mengukur FPS (rata-rata, persentil waktu frame), waktu GPU per pass (Copper, Millar), menangkap layar, mencari titik
putih terisolasi (petunjuk NaN), dan mengumpulkan data `?prof=1` (program shader per tombol, waktu muat).

Pasang sekali:
    pip install playwright pillow
    python -m playwright install chromium        (atau pakai Chrome terpasang: --chrome)
Jalankan dari folder repo:
    python tools/uji_gpu_lokal.py                  (prioritas 1, preset bawaan menurut mesin)
    python tools/uji_gpu_lokal.py --lengkap        (juga prioritas 2: tur, motor, kamera, gelombang Millar, ...)
    python tools/uji_gpu_lokal.py --preset ultra,tinggi --exp copper
Hasil: folder `hasil-uji-gpu/<tanggal>-<komputer>/` berisi `laporan.md`, `hasil.json`, tangkapan layar `*.jpg`, `prof-*.json`.
Kirim `laporan.md` (dan foto baris bermasalah) ke Claude, atau commit folder itu ke cabang sendiri.

Catatan: jendela Chrome terbuka dan dikendalikan skrip; jangan dipakai selama uji (sekitar 15-40 menit per preset).
Butuh internet (three.js dari cdn.jsdelivr.net). Halaman disajikan lewat server lokal http://127.0.0.1:<port>.
"""
import argparse, asyncio, datetime, functools, http.server, json, os, pathlib, platform, socket, sys, threading, time

try:
    from playwright.async_api import async_playwright
except ImportError:
    sys.exit('Playwright belum terpasang: pip install playwright  lalu  python -m playwright install chromium')
try:
    from PIL import Image, ImageChops, ImageFilter
except ImportError:
    Image = None

ROOT = pathlib.Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- server lokal
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')                # selalu berkas terbaru dari disk
        super().end_headers()

def serve():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, port

# ---------------------------------------------------------------- pengukuran di halaman
FPS_JS = """async (sec) => {
  const t = [], t0 = performance.now();
  await new Promise((res) => { const f = (now) => { t.push(now); if (now - t0 < sec * 1000) requestAnimationFrame(f); else res(); }; requestAnimationFrame(f); });
  const d = []; for (let i = 1; i < t.length; i++) d.push(t[i] - t[i - 1]);
  const s = d.slice().sort((a, b) => a - b), q = (p) => s.length ? s[Math.min(s.length - 1, Math.floor(p * s.length))] : 0;
  const tot = t[t.length - 1] - t[0];
  return { fps: tot > 0 ? (t.length - 1) * 1000 / tot : 0, p50: q(0.5), p95: q(0.95), p99: q(0.99), max: s.length ? s[s.length - 1] : 0, n: d.length, over50: d.filter((x) => x > 50).length };
}"""
GL_JS = """() => { const c = document.createElement('canvas'), gl = c.getContext('webgl2'); if (!gl) return 'tanpa WebGL2';
  const e = gl.getExtension('WEBGL_debug_renderer_info'); return e ? gl.getParameter(e.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER); }"""
# waktu GPU per pass (EXT_disjoint_timer_query_webgl2), bila experience punya GPUT
GPU_JS = {
    'copper': "(() => { const G = window.__station && window.__station.GPUT; return G && G.ext && G.n ? { bayangan: G.ms.sh, scene: G.ms.sc, post: G.ms.po } : null; })()",
    'millar': "(() => { const G = window.__millar && window.__millar.GPUT; return G && G.ext && G.n ? { langit: G.ms.sk, laut: G.ms.oc, scene: G.ms.sc, post: G.ms.po } : null; })()",
    'gargantua': 'null',
}

# indeks tombol di kartu mulai (#presetPick) per experience
PRESET_IDX = {
    'copper':    {'ultra': 0, 'tinggi': 1, 'sedang': 2, 'rendah': 3, 'hemat': 4},
    'millar':    {'ultra': 0, 'tinggi': 1, 'sedang': 2, 'rendah': 3, 'hemat': 4},
    'gargantua': {'rendah': 0, 'sedang': 1, 'tinggi': 2, 'ultra': 3, 'hemat': 0},   # Gargantua tanpa Hemat: pakai Rendah
}
PAGE = {'copper': 'experiences/cooper-station/index.html', 'millar': 'experiences/millar/index.html', 'gargantua': 'experiences/gargantua/index.html'}

def sleep(s): return asyncio.sleep(s)

async def hold(pg, key, sec):
    await pg.keyboard.down(key); await sleep(sec); await pg.keyboard.up(key)

# ---------------------------------------------------------------- titik uji
# Tiap titik: (id, prioritas, nama, fungsi persiapan async (pg, S), tombol ditahan saat ukur atau None)
# S = nama objek uji global di halaman. Persiapan memakai fungsi uji yang diekspor experience (window.__station dst.).
def ev(js): return lambda pg: pg.evaluate(js)

async def c_day(pg, spot):
    await pg.evaluate(f"(() => {{ const S = window.__station; S.teleport('{spot}'); S.clock.hour = 13; S.WEATHER.mode = 'cerah'; S.WEATHER.state = 'cerah'; }})()")
async def c_rain(pg):
    await pg.evaluate("(() => { const S = window.__station; S.teleport('fountain'); S.clock.hour = 13; S.WEATHER.mode = 'mendung'; S.WEATHER.state = 'mendung'; })()")
    await sleep(15)                                                  # awan menebal, hujan, genangan
async def c_night(pg):
    await pg.evaluate("(() => { const S = window.__station; S.teleport('nyc'); S.clock.hour = 21; S.WEATHER.mode = 'cerah'; S.WEATHER.state = 'cerah'; })()")
async def c_ext(pg):
    await pg.evaluate("(() => { const S = window.__station; S.clock.hour = 13; if (!S.ext.active) S.toggleExterior(); })()")
async def c_eclipse(pg):
    await pg.evaluate("(() => { const S = window.__station; if (!S.ext.active) S.toggleExterior(); S.jumpToEclipse(); })()"); await sleep(5)
async def c_ship(pg):
    await pg.evaluate("(() => { const S = window.__station; if (S.ext.active) S.toggleExterior(); S.teleport('cooper'); S.portBoard(); })()")
    await sleep(4); await pg.keyboard.press('KeyE'); await sleep(8); await pg.keyboard.press('KeyE'); await sleep(4)   # melayang ke palka, duduk
async def c_fly(pg):
    await pg.keyboard.press('KeyE'); await sleep(10)                 # lepas sandar, kendali manual
    await hold(pg, 'KeyW', 2)                                        # tuas gas naik sekitar 1/1 (bertahan)
async def c_moto(pg):
    await pg.evaluate("(() => { const S = window.__station; if (S.ext.flight || S.ext.active) S.toggleExterior(); S.teleport('nyc'); S.clock.hour = 21; })()")
    await sleep(2); await pg.keyboard.press('KeyC'); await sleep(3)
async def c_cam(pg):
    await pg.evaluate("(() => { const S = window.__station; S.teleport('cooper'); S.clock.hour = 13; })()"); await sleep(2); await pg.keyboard.press('KeyF'); await sleep(3)
async def c_tour(pg):
    await pg.keyboard.press('Escape'); await pg.evaluate("window.__station.startTour()")
async def c_moon(pg, i):
    await pg.evaluate(f"window.__station.moonLook({i})"); await sleep(6)

COPPER = [
    ('C3', 1, 'Rumah Cooper siang (tekstur dekat, kota)', lambda pg: c_day(pg, 'cooper'), None),
    ('C3j', 1, 'Rumah Cooper siang, berjalan (lari)', lambda pg: c_day(pg, 'cooper'), 'KeyW'),
    ('C4', 1, 'New York siang (orang GLB, mobil dekat)', lambda pg: c_day(pg, 'nyc'), None),
    ('C5', 1, 'Puncak bukit (rumput fluffy, pohon)', lambda pg: c_day(pg, 'hill'), None),
    ('C6', 1, 'Hutan lebat (pohon, impostor)', lambda pg: c_day(pg, 'forest'), None),
    ('C7', 1, 'Air mancur, mendung + hujan (genangan, SSR)', c_rain, None),
    ('C8', 1, 'New York malam (lampu, gedung malam)', c_night, None),
    ('C9', 1, 'Kamera luar (lambung, Skyway)', c_ext, None),
    ('C9g', 1, 'Kamera luar, gerhana', c_eclipse, None),
    ('C11', 1, 'Kokpit shuttle sandar', c_ship, None),
    ('C11t', 1, 'Shuttle terbang (W gas, D guling)', c_fly, 'KeyD'),
    ('C14', 2, 'Motor malam New York (W)', c_moto, 'KeyW'),
    ('C12', 2, 'Kamera rangefinder (jendela bidik)', c_cam, None),
    ('C13', 2, 'Tur sinematik Y (90 s pertama)', c_tour, None),
]
COPPER_JUP = [
    ('C10', 1, 'Jupiter: rumah Cooper siang', lambda pg: c_day(pg, 'cooper'), None),
    ('C10a', 1, 'Jupiter: lihat Io (kamera luar)', lambda pg: c_moon(pg, 0), None),
    ('C10b', 1, 'Jupiter: lihat Europa (kamera luar)', lambda pg: c_moon(pg, 1), None),
]

async def m_board(pg):
    await pg.evaluate("window.__millar.boardShip()"); await sleep(4)
async def m_wave(pg):
    await pg.keyboard.press('KeyG'); await sleep(130)                # gelombang dipanggil ke 20 km, 125 m/s: sekitar 3,7 km setelah 130 s
async def m_cam(pg):
    await pg.keyboard.press('KeyF'); await sleep(3)

MILLAR = [
    ('M2', 1, 'Berdiri di air', None, None),
    ('M2j', 1, 'Berjalan di air (lari bawaan)', None, 'KeyW'),
    ('M4', 1, 'Naik KS-07, naik ke atas (R)', m_board, 'KeyR'),
    ('M3', 2, 'Gelombang mendekat (G, tunggu 130 s)', m_wave, None),
    ('M6', 2, 'Kamera rangefinder (jendela bidik)', m_cam, None),
]

async def g_mood(pg):
    await pg.evaluate("window.__gargantua.setMood(true)"); await sleep(4)
async def g_mission(pg, sc, view):
    await pg.evaluate(f"""(() => {{ const G = window.__gargantua; G.setMood(false); G.startMission('{sc}');
      for (let i = 0; i < 4 && G.SHIP.view !== '{view}'; i++) G.cycleShipView(); }})()"""); await sleep(6)

GARGANTUA = [
    ('G1', 1, 'Tampilan awal (piringan, bintang)', None, None),
    ('G2', 1, 'Suasana Kelam (debu, planet Millar)', g_mood, None),
    ('G3', 1, 'Misi susur piringan, kokpit', lambda pg: g_mission(pg, 'skim', 'cockpit'), None),
    ('G3c', 1, 'Misi susur piringan, kamera luar', lambda pg: g_mission(pg, 'skim', 'chase'), None),
    ('G5', 2, 'Misi jatuh lurus, pandangan relai', lambda pg: g_mission(pg, 'drip', 'relay'), None),
    ('G4', 2, 'Skenario tesseract (membidik)', lambda pg: g_mission(pg, 'tesseract', 'chase'), None),
]

# ---------------------------------------------------------------- titik putih terisolasi (petunjuk NaN)
def bright_dots(path):
    """Jumlah piksel sangat terang (> 245) yang dikelilingi gelap (rata-rata 5 x 5 < 110). Heuristik, bukan bukti NaN:
    bintang dan lampu kecil juga terhitung; yang penting perbandingan antar titik dan antar mesin, serta dua tangkapan berturut-turut."""
    if Image is None: return None
    L = Image.open(path).convert('L')
    br = L.point(lambda v: 255 if v > 245 else 0)
    dk = L.filter(ImageFilter.BoxBlur(2)).point(lambda v: 255 if v < 110 else 0)
    return ImageChops.multiply(br, dk).histogram()[255]

# ---------------------------------------------------------------- jalannya satu experience
async def run_exp(ctx, base, exp, preset, args, out, extra='', points=None, tag=''):
    pg = await ctx.new_page()
    if os.environ.get('THREE_LOCAL'):                                # tanpa CDN (sandbox): three.js dari folder lokal
        local = pathlib.Path(os.environ['THREE_LOCAL'])
        async def serve_three(route):
            await route.fulfill(path=str(local / route.request.url.rsplit('/', 1)[-1]), content_type='text/javascript', headers={'Access-Control-Allow-Origin': '*'})
        await pg.route('https://cdn.jsdelivr.net/**', serve_three)
    log = []; res = {'exp': exp + tag, 'preset': preset, 'titik': [], 'galat': log}
    pg.on('pageerror', lambda e: log.append('pageerror: ' + str(e)[:300]))
    pg.on('console', lambda m: log.append(f'{m.type}: {m.text[:300]}') if m.type == 'error' else None)
    url = f"{base}/{PAGE[exp]}?prof=1&lang=id{extra}"
    t0 = time.time()
    await pg.goto(url, wait_until='domcontentloaded', timeout=120000)
    res['renderer'] = await pg.evaluate(GL_JS)
    await pg.wait_for_function("document.getElementById('ready') && !document.getElementById('ready').hidden", timeout=600000)
    res['muat_s'] = round(time.time() - t0, 1)
    idx = PRESET_IDX[exp][preset]
    await pg.evaluate(f"""(() => {{ const b = document.querySelectorAll('#presetPick button')[{idx}]; if (b) b.click();
      const a = document.getElementById('presetAuto'); if (a && a.checked) {{ a.checked = false; a.dispatchEvent(new Event('change')); }}
      const c = document.getElementById('cineOn'); if (c && c.checked !== {str(bool(args.cine)).lower()}) {{ c.checked = {str(bool(args.cine)).lower()}; c.dispatchEvent(new Event('change')); }}
      const m = document.querySelector('#modePick button:not([data-mode="misi"])'); if (m) m.click();
      const G = window.__gargantua; if (G) {{ G.CONFIG.adaptive = false; G.CONFIG.renderScale = G.CONFIG.presets[G.CONFIG.quality].scale; }}   // resolusi adaptif mati: skala tetap preset
      document.getElementById('go').click(); }})()""")
    if exp == 'copper':
        await pg.wait_for_function('window.__stationReady === true', timeout=600000)
        await pg.evaluate('window.__station.setHudMode(false)')     # HUD lengkap = GPUT aktif
    elif exp == 'gargantua':
        res['skala'] = await pg.evaluate('window.__gargantua.CONFIG.renderScale')
    elif exp == 'millar':
        await pg.wait_for_function('window.__millarReady === true', timeout=600000)
        if args.cine: await sleep(40)                                 # sinematik kedatangan diukur di titik M1
    await sleep(3)
    pts = points if points is not None else {'copper': COPPER, 'millar': MILLAR, 'gargantua': GARGANTUA}[exp]
    if exp == 'millar' and args.cine and points is None:
        pts = [('M1', 1, 'Sinematik kedatangan (sedang berjalan)', None, None)]
    for pid, pri, name, setup, key in pts:
        if pri > args.prioritas: continue
        r = {'id': pid, 'nama': name}
        try:
            if setup: await setup(pg)
            await sleep(args.settle)
            if key: await pg.keyboard.down(key)
            sec = 90 if pid == 'C13' else args.detik
            r.update(await pg.evaluate(FPS_JS, sec))
            if key: await pg.keyboard.up(key)
            r['gpu_ms'] = await pg.evaluate(GPU_JS[exp])
            shot = out / f"{exp}{tag}-{preset}-{pid}.jpg"; shot2 = out / f"{exp}{tag}-{preset}-{pid}-b.jpg"
            try:                                                     # foto gagal (mis. GPU sangat lambat) tidak membuang angka FPS
                await pg.screenshot(path=str(shot), type='jpeg', quality=80, timeout=120000)
                await sleep(0.15)
                await pg.screenshot(path=str(shot2), type='jpeg', quality=80, timeout=120000)
                a, b = bright_dots(shot), bright_dots(shot2)
                r['titik_putih'] = None if a is None else [a, b]
                shot2.unlink(missing_ok=True)
                r['foto'] = shot.name
            except Exception as e:
                r['foto'] = '-'; r['catatan'] = 'foto gagal: ' + str(e)[:120]
            print(f"  {pid:5s} {name[:44]:44s} {r['fps']:6.1f} fps  p95 {r['p95']:5.1f} ms  >50ms {r['over50']}")
        except Exception as e:                                       # satu titik gagal tidak menghentikan uji
            r['galat'] = str(e)[:300]; print(f"  {pid:5s} GAGAL: {r['galat']}")
            for k in ('KeyW', 'KeyD', 'KeyR'):
                try: await pg.keyboard.up(k)
                except Exception: pass
        res['titik'].append(r)
    if args.tombol:                                                  # P4: ganti preset dan efek layar tanpa tersendat
        for k in ['KeyQ'] * 5 + ['KeyP'] * 3:
            await pg.keyboard.press(k); await sleep(1.5)
    prof = await pg.evaluate('window.PROFKIT ? window.PROFKIT.data() : null')
    (out / f"prof-{exp}{tag}-{preset}.json").write_text(json.dumps(prof, indent=1), encoding='utf-8')
    res['prof'] = f"prof-{exp}{tag}-{preset}.json"
    await pg.close()
    return res

# ---------------------------------------------------------------- laporan
def report(out, meta, runs):
    L = [f"# Hasil uji GPU lokal", '', f"Tanggal: {meta['tanggal']} · Komputer: {meta['komputer']} · OS: {meta['os']}",
         f"GPU (WebGL): {meta['renderer']} · Viewport: {meta['viewport']} · Vsync: {meta['vsync']}", '']
    if 'swiftshader' in meta['renderer'].lower() or 'llvmpipe' in meta['renderer'].lower():
        L += ['**PERINGATAN: render perangkat lunak (bukan GPU). Angka FPS tidak bermakna. Coba --chrome atau perbarui driver.**', '']
    L += ['Kolom: FPS rata-rata; p50 / p95 / maks = waktu frame (ms); >50 ms = frame tersendat; GPU = ms per pass;',
          'titik putih = piksel terang terisolasi di dua tangkapan berturut-turut (petunjuk NaN bila naik tajam, bukan bukti).', '']
    for r in runs:
        L += [f"## {r['exp']} · preset {r['preset']}", '', f"Muat sampai tombol Mulai: {r.get('muat_s', '-')} s · data muat: `{r.get('prof', '-')}`" + (f" · skala render {r['skala']}" if 'skala' in r else ''), '',
              '| Titik | Nama | FPS | p50 | p95 | maks | >50 ms | GPU ms | Titik putih | Foto |', '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
        for t in r['titik']:
            if 'galat' in t and 'fps' not in t:
                L.append(f"| {t['id']} | {t['nama']} | GAGAL: {t['galat'][:80]} | | | | | | | |"); continue
            g = ' / '.join(f"{k} {v:.1f}" for k, v in (t.get('gpu_ms') or {}).items()) or '-'
            tp = '-' if not t.get('titik_putih') else f"{t['titik_putih'][0]} / {t['titik_putih'][1]}"
            L.append(f"| {t['id']} | {t['nama']} | {t['fps']:.1f} | {t['p50']:.1f} | {t['p95']:.1f} | {t['max']:.0f} | {t['over50']} | {g} | {tp} | {t.get('foto', '-')}{(' (' + (t.get('catatan') or t.get('galat') or '') + ')') if (t.get('catatan') or t.get('galat')) else ''} |")
        if r['galat']:
            L += ['', 'Galat konsol:', ''] + [f"- `{x}`" for x in r['galat'][:15]]
        L.append('')
    (out / 'laporan.md').write_text('\n'.join(L), encoding='utf-8')

# ---------------------------------------------------------------- utama
async def main():
    ap = argparse.ArgumentParser(description='Uji GPU lokal otomatis Interstellia (Fase A2)')
    ap.add_argument('--exp', default='copper,millar,gargantua', help='daftar experience: copper,millar,gargantua')
    ap.add_argument('--preset', default='', help='mis. ultra,tinggi (bawaan: Mac = hemat,sedang; lainnya = ultra,tinggi)')
    ap.add_argument('--lengkap', action='store_true', help='juga titik prioritas 2 (tur, motor, kamera, gelombang, relai, tesseract)')
    ap.add_argument('--tanpa-jupiter', dest='nojup', action='store_true', help='lewati putaran Copper dengan Jupiter 8k dan bulan')
    ap.add_argument('--detik', type=float, default=10, help='lama ukur per titik (s)')
    ap.add_argument('--settle', type=float, default=6, help='jeda sebelum ukur (s)')
    ap.add_argument('--vsync', action='store_true', help='biarkan batas FPS layar (bawaan: dilepas agar terlihat kemampuan GPU)')
    ap.add_argument('--asli', action='store_true', help='ukuran jendela dan DPR layar asli (bawaan: 1920 x 1080, DPR 1, agar bisa dibanding antar mesin)')
    ap.add_argument('--chrome', action='store_true', help='pakai Google Chrome terpasang (channel chrome) alih-alih Chromium Playwright')
    ap.add_argument('--headless', action='store_true', help='tanpa jendela (hanya untuk cek alur skrip; GPU biasanya tidak dipakai)')
    ap.add_argument('--tanpa-tombol', dest='tombol', action='store_false', help='lewati uji ganti preset Q / P')
    args = ap.parse_args()
    args.prioritas = 2 if args.lengkap else 1
    args.cine = False
    mac = platform.system() == 'Darwin'
    presets = [p.strip().lower() for p in (args.preset or ('hemat,sedang' if mac else 'ultra,tinggi')).split(',') if p.strip()]
    exps = [e.strip() for e in args.exp.split(',') if e.strip() in PAGE]
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M')
    out = ROOT / 'hasil-uji-gpu' / f"{stamp}-{socket.gethostname().split('.')[0]}"
    out.mkdir(parents=True, exist_ok=True)
    srv, port = serve(); base = f"http://127.0.0.1:{port}"
    flags = ['--ignore-gpu-blocklist', '--enable-gpu-rasterization']
    if not args.vsync: flags += ['--disable-gpu-vsync', '--disable-frame-rate-limit']
    runs, renderer = [], '?'
    async with async_playwright() as p:
        kw = {'channel': 'chrome'} if args.chrome else {'executable_path': os.environ['CHROMIUM']} if os.environ.get('CHROMIUM') else {}
        b = await p.chromium.launch(headless=args.headless, args=flags, **kw)
        for preset in presets:
            for exp in exps:
                if preset not in PRESET_IDX[exp]: continue
                ctx = await b.new_context(**({'no_viewport': True} if args.asli else {'viewport': {'width': 1920, 'height': 1080}, 'device_scale_factor': 1}))
                await ctx.add_init_script("try { localStorage.setItem('cooperStation.tourSeen', '1'); } catch (e) {}")   # tawaran tur Copper tidak menutupi foto
                print(f"\n== {exp} · {preset}")
                try:
                    r = await run_exp(ctx, base, exp, preset, args, out)
                    runs.append(r); renderer = r.get('renderer', renderer)
                    if exp == 'copper' and not args.nojup:
                        print(f"== copper (Jupiter 8k) · {preset}")
                        runs.append(await run_exp(ctx, base, exp, preset, args, out, '&planet=jupiter&jres=8k', COPPER_JUP, '-jupiter'))
                    if exp == 'millar' and args.lengkap:
                        print(f"== millar (sinematik) · {preset}")
                        args.cine = True
                        try: runs.append(await run_exp(ctx, base, exp, preset, args, out, '', None, '-sinematik'))
                        finally: args.cine = False
                except Exception as e:
                    print('  GAGAL MUAT:', e); runs.append({'exp': exp, 'preset': preset, 'titik': [], 'galat': ['gagal muat: ' + str(e)[:300]]})
                await ctx.close()
                meta = {'tanggal': stamp, 'komputer': socket.gethostname(), 'os': f"{platform.system()} {platform.release()} {platform.machine()}",
                        'renderer': renderer, 'viewport': 'asli' if args.asli else '1920 x 1080 DPR 1', 'vsync': 'ya' if args.vsync else 'dilepas'}
                (out / 'hasil.json').write_text(json.dumps({'meta': meta, 'runs': runs}, indent=1), encoding='utf-8')
                report(out, meta, runs)                              # laporan ditulis ulang tiap experience: hasil parsial tetap ada bila uji dihentikan
        await b.close()
    srv.shutdown()
    print(f"\nSelesai. Laporan: {out / 'laporan.md'}")

if __name__ == '__main__':
    asyncio.run(main())
