"""Ukur draw call Copper Corn Station per pass dan per sumber kode (analisa: docs/cooper-station/analisa-draw-call-cooper-station.md).

Pakai:
  python tools/ukur_draw_call.py                                  # Ultra, lokasi Rumah Cooper (1) dan Puncak bukit (2)
  python tools/ukur_draw_call.py --preset hemat 1 tp:nyc 0        # preset Hemat; lokasi: tombol 0-9 atau tp:<kunci SPOTS>
  python tools/ukur_draw_call.py --json hasil.json                # simpan rekaman mentah (satu baris per panggilan renderBufferDirect)
Lingkungan: THREE_LOCAL=<folder three.core.js + three.module.js> untuk sandbox tanpa CDN, CHROMIUM=<jalur chrome> opsional.

Cara kerja: renderBufferDirect dibungkus, tiap panggilan dicatat (pass dari render target, jumlah instance, draw GL nyata, jumlah panggilan
GL). Lokasi pembuatan objek (baris index.html) didapat dari three.core.js yang ditambal di jalan (Object3D menyimpan tumpukan panggilan).
Draw call "nyata" = selisih renderer.info.render.calls (sama dengan angka HUD); "kosong" = mesh terkirim tetapi 0 instance (three.js tetap
memasang program dan uniform, tanpa draw GL). Pass bake oktahedral (target 1024, sementara tiap frame saat Ultra baru dimuat) dipisah.
Di sandbox (SwiftShader) jumlahnya dapat dipercaya, waktu (ms) tidak mewakili GPU asli."""
import argparse, asyncio, collections, json, os, pathlib, re, statistics
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / 'experiences/cooper-station/index.html'
SRC = PAGE.read_text().split('\n')
CDN = 'https://cdn.jsdelivr.net/npm/three@0.186.1/build/'
PATCH_FROM = 'class Object3D extends EventDispatcher {'

HOOK = r"""
() => {
  const S = window.__station, r = S.renderer, D = window.__dc = { on: false, rec: [], fr: 0, gl: 0 };
  const ri = r.info.reset.bind(r.info); r.info.reset = function () { D.fr++; return ri(); };
  const P = WebGL2RenderingContext.prototype;                         // hitung semua panggilan GL
  for (const k of Object.getOwnPropertyNames(P)) { const d = Object.getOwnPropertyDescriptor(P, k), f = d && d.value;
    if (typeof f !== 'function' || k === 'constructor' || k === 'getError') continue; P[k] = function () { D.gl++; return f.apply(this, arguments); }; }
  const reg = new Map(), seen = new Set();                            // nama jalur objek dari ekspor window.__station (mis. TREES.templates[3].bark)
  const walk = (v, path, depth) => {
    if (!v || typeof v !== 'object' || seen.has(v) || depth > 3) return; seen.add(v);
    if (v.isObject3D) { if (!reg.has(v)) reg.set(v, path); return; }
    if (v.isMaterial || v.isBufferGeometry || v.isTexture || v.isWebGLRenderTarget) return;
    if (Array.isArray(v)) { v.slice(0, 60).forEach((x, i) => walk(x, path + '[' + i + ']', depth + 1)); return; }
    for (const k of Object.keys(v).slice(0, 80)) { try { walk(v[k], path + '.' + k, depth + 1); } catch (e) {} }
  };
  for (const k of Object.keys(S)) { try { walk(S[k], k, 0); } catch (e) {} }
  const orig = r.renderBufferDirect.bind(r);
  r.renderBufferDirect = function (camera, scene, geometry, material, object, group) {
    if (!D.on) return orig(camera, scene, geometry, material, object, group);
    const rt = r.getRenderTarget(), c0 = r.info.render.calls, g0 = D.gl, t0 = performance.now();
    const res = orig(camera, scene, geometry, material, object, group);
    const site = (object.__site || '').split('|')[0].replace(/.*index\.html\?[^:]*:/, '').split(':')[0];
    D.rec.push([D.fr, rt ? 'rt' + rt.width + (rt.depthTexture ? 'd' : '') : 'canvas', scene === S.farScene ? 'far' : 'main', camera.uuid.slice(0, 5),
      reg.get(object) || '', +site || 0, object.isInstancedMesh ? object.count : 1, r.info.render.calls - c0, D.gl - g0, +(performance.now() - t0).toFixed(3),
      geometry.type, material.type, object.frustumCulled ? 1 : 0]);
    return res;
  };
}
"""

def category(path, geo):
    p = path.split('[')[0].split('.')[0]
    if path.endswith('.bark') or path.endswith('.leaf'): return 'pohon dekat (kulit + daun)'
    if path.endswith('.imp') or path.endswith('.oct'): return 'impostor pohon'
    return {'FURN': 'perabot kota (FURN)', 'PEDS': 'pejalan kaki', 'TRAFFIC': 'mobil', 'SHP': 'gedung + atap (SHP.stat)', 'tramMesh': 'trem', 'TRAM_PARTS': 'trem'}.get(p, '')

async def run(args):
    local = os.environ.get('THREE_LOCAL')
    async def serve(route):
        name = route.request.url.rsplit('/', 1)[-1]
        if local: body = (pathlib.Path(local) / name).read_text()
        else: body = await (await route.fetch()).text()
        if name == 'three.core.js':
            i = body.index(PATCH_FROM); j = body.index('super();', body.index('constructor() {', i)) + len('super();')
            body = body[:j] + "\n\t\ttry { this.__site = (new Error().stack || '').split('\\n').filter(l => l.includes('index.html')).slice(0, 3).join('|'); } catch (e) {}" + body[j:]
        await route.fulfill(body=body, content_type='text/javascript', headers={'Access-Control-Allow-Origin': '*'})
    out = {}
    async with async_playwright() as p:
        kw = {'executable_path': os.environ['CHROMIUM']} if os.environ.get('CHROMIUM') else {}
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'], **kw)
        pg = await b.new_page(viewport={'width': 640, 'height': 360})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.route(CDN + '**', serve)
        await pg.goto(PAGE.as_uri() + f'?lang=id&preset={args.preset}' + (('&' + args.q) if args.q else ''))
        await pg.wait_for_function('window.__stationReady === true', timeout=900000)
        await pg.click('#go', timeout=300000)
        await pg.wait_for_timeout(4000)
        await pg.evaluate(HOOK)
        for k in args.spots:
            if k.startswith('tp:'): await pg.evaluate('(n) => window.__station.teleport(n)', k[3:])
            else: await pg.keyboard.press('Digit' + k)
            await pg.wait_for_timeout(5000)
            await pg.evaluate('() => { __dc.rec.length = 0; __dc.on = true; }')
            await pg.evaluate('() => new Promise(res => { let n = 0; const f = () => { if (++n >= 8) { __dc.on = false; res(); } else requestAnimationFrame(f); }; requestAnimationFrame(f); })')
            out[k] = await pg.evaluate('() => __dc.rec')
        await b.close()
    return out, errs

def show(name, rec, top):
    frames = sorted(set(r[0] for r in rec)); f = frames[len(frames) // 2]
    rs = [r for r in rec if r[0] == f]
    bake = [r for r in rs if r[1] == 'rt1024']; rs = [r for r in rs if r[1] != 'rt1024']
    real = sum(r[7] for r in rs)
    print(f'\n=== {name}: terkirim {len(rs)}, draw GL nyata {real}, kosong {sum(1 for r in rs if r[7] == 0)}, panggilan GL {sum(r[8] for r in rs)}'
          + (f'  (+ bake oktahedral {len(bake)} draw, sementara)' if bake else ''))
    cams = collections.OrderedDict()
    for r in rs: cams.setdefault((r[1], r[2], r[3]), []).append(r)
    for (rt, sc, cam), v in cams.items():
        if len(v) >= 5: print(f'  pass {rt:8s} {sc:4s}: terkirim {len(v):3d}, nyata {sum(x[7] for x in v):3d}')
    cat = collections.defaultdict(lambda: [0, 0, 0])               # utama, bayangan, kosong
    for r in rs:
        c = category(r[4], r[10]) or 'lainnya'
        if r[7] == 0: cat[c][2] += 1
        elif r[1].startswith('rt2048'): cat[c][1] += r[7]
        else: cat[c][0] += r[7]
    print('  kategori (nyata utama + bayangan, kosong):')
    for c, e in sorted(cat.items(), key=lambda x: -(x[1][0] + x[1][1])): print(f'    {c:30s} {e[0]:4d} + {e[1]:4d}   kosong {e[2]}')
    g = collections.defaultdict(lambda: [0, 0, ''])
    for r in rs:
        e = g[r[5]]; e[0] += r[7]; e[1] += 1 if r[7] == 0 else 0; e[2] = r[4]
    print(f'  {top} sumber teratas (baris index.html):')
    for ln, e in sorted(g.items(), key=lambda x: -x[1][0])[:top]:
        print(f'    L{ln:<6d} nyata {e[0]:3d} kosong {e[1]:3d} {e[2][:24]:24s}| {SRC[ln - 1].strip()[:90] if ln else "?"}')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('spots', nargs='*', default=['1', '2'])
    ap.add_argument('--preset', default='ultra'); ap.add_argument('--top', type=int, default=14); ap.add_argument('--json'); ap.add_argument('--q', default='', help='parameter URL tambahan, mis. tekstur=lama')
    a = ap.parse_args()
    res, errs = asyncio.run(run(a))
    for k, rec in res.items(): show(f'{a.preset} / {k}', rec, a.top)
    if a.json: pathlib.Path(a.json).write_text(json.dumps(res))
    print('\ngalat halaman:', errs[:3] or 'tidak ada')
