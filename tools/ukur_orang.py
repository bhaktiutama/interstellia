"""Ukur orang (rencana tahap 28a, docs/cooper-station/rencana-tahap-28-cooper-station.md): sidik jari geometri model orang,
jumlah orang tergambar per band jarak (0-12, 12-30, 30-90, > 90 m) di 6 lokasi x 3 preset, segitiga yang digambar, biaya CPU updatePeds,
dan apakah orang ikut pass bayangan. Hasil dicetak sebagai JSON; --simpan <berkas> menulis sidik jari ke JSON acuan (tools/uji_orang_lama.json).

Pakai: python tools/ukur_orang.py [--simpan tools/uji_orang_lama.json] [--url "?orang=lama"]
Lingkungan: THREE_LOCAL=<folder three.module.js + three.core.js> untuk sandbox tanpa CDN, CHROMIUM=<jalur chrome> opsional.
Catatan: di sandbox (SwiftShader) jumlah dan segitiga dapat dipercaya, waktu GPU tidak mewakili GPU asli."""
import asyncio, json, os, pathlib, sys
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent

UKUR = r"""
(async () => {
  const st = window.__station, P = st.PEDS, out = {};
  const fnv = (arr) => { let h = 0x811c9dc5; const u = new Uint8Array(arr.buffer, arr.byteOffset, arr.byteLength); for (let i = 0; i < u.length; i++) { h ^= u[i]; h = Math.imul(h, 0x01000193) >>> 0; } return h.toString(16); };
  const g = P.mesh.geometry, A = g.attributes;
  out.geometri = { tri: g.index.count / 3, titik: A.position.count, hashPos: fnv(A.position.array), hashNrm: fnv(A.normal.array), hashPart: fnv(A.aPart.array), hashIdx: fnv(g.index.array) };
  out.lama = P.lama; out.layerMask = P.mesh.layers.mask; out.total = P.list.length;
  const CIRC = 2 * Math.PI * st.R, wrap = (d) => ((d % CIRC) + 1.5 * CIRC) % CIRC - CIRC / 2;
  const bands = [12, 30, 90, 1e9], lok = ['cooper', 'nyc', 'market', 'fountain', 'baseball', 'spaceport'];
  const frames = (n) => new Promise((r) => { let k = 0; const f = () => (++k >= n ? r() : requestAnimationFrame(f)); requestAnimationFrame(f); });
  out.lokasi = {};
  for (const pi of [0, 2, 4]) {
    st.applyPreset(pi); const nm = st.PRESETS[pi].name; out.lokasi[nm] = {};
    for (const k of lok) {
      st.teleport(k); st.updateCamera(); for (let i = 0; i < 40; i++) { st.clock.sim += 0.1; st.stepPeds(0.1); }
      let ms = 0; const N = 20; for (let i = 0; i < N; i++) { const t0 = performance.now(); st.updatePeds(); ms += performance.now() - t0; }
      await frames(3); const a = g.attributes.aP.array, n = P.n, eS = st.player.theta * st.R, eZ = st.player.za, cnt = [0, 0, 0, 0];
      for (let i = 0; i < n; i++) { const d = Math.hypot(wrap(a[i * 4] - eS), a[i * 4 + 1] - eZ); cnt[bands.findIndex((b) => d < b)]++; }
      out.lokasi[nm][k] = { n, band: cnt, msUpdate: +(ms / N).toFixed(3), triSemua: st.renderer.info.render.triangles, tiriOrang: n * out.geometri.tri };
    }
  }
  st.applyPreset(0);
  return out;
})()
"""

async def main():
    args = sys.argv[1:]
    simpan = args[args.index('--simpan') + 1] if '--simpan' in args else None
    extra = args[args.index('--url') + 1] if '--url' in args else ''
    local = os.environ.get('THREE_LOCAL'); chromium = os.environ.get('CHROMIUM')
    async with async_playwright() as p:
        kw = {'args': ['--use-angle=swiftshader', '--enable-unsafe-swiftshader']}
        if chromium: kw['executable_path'] = chromium
        b = await p.chromium.launch(**kw)
        pg = await b.new_page(viewport={'width': 320, 'height': 200})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        if local:
            async def serve(route):
                await route.fulfill(path=str(pathlib.Path(local) / route.request.url.rsplit('/', 1)[-1]), content_type='text/javascript', headers={'Access-Control-Allow-Origin': '*'})
            await pg.route('https://cdn.jsdelivr.net/**', serve)
        await pg.goto(ROOT.joinpath('experiences/cooper-station/index.html').as_uri() + extra)
        await pg.wait_for_function('window.__stationReady === true', timeout=900000)
        h = await pg.evaluate(UKUR)
        print(json.dumps(h, indent=1, ensure_ascii=False)); print('error:', errs[:5] or 'tidak ada')
        if simpan: pathlib.Path(simpan).write_text(json.dumps(h['geometri'], indent=1) + '\n', encoding='utf-8')
        await b.close()

asyncio.run(main())
