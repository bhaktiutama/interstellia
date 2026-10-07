"""Uji 21e (Copper Corn Station): kabut pagi. Kerapatan scene.fog naik sebelum fajar, penuh 6,0-7,2, menipis sampai 9,5, puncak
sekitar 5x kerapatan dasar (V4 Ultra / Tinggi: 2x + lapisan kabut tanah); warna lebih pucat hangat saat kabut; pantulan daratan seberang (uL_FarAvg) ikut berkabut; mendung
menghapus kabut pagi; kamera luar tanpa kabut tidak berubah; render pagi tanpa nilai tidak valid.
Pakai: python tools/uji_kabut_pagi.py   (butuh: pip install playwright && playwright install chromium)
Tanpa akses CDN langsung: THREE_LOCAL=<folder berisi three.module.js dan three.core.js> python tools/uji_kabut_pagi.py
Chromium sendiri: CHROMIUM=<jalur executable>"""
import asyncio, os, pathlib
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = 'experiences/cooper-station/index.html'

UJI = r"""
(async () => {
  const S = window.__station, out = {}, info = [], wait = (ms) => new Promise((r) => setTimeout(r, ms));
  S.teleport('nyc'); await wait(2000);
  const at = (h, ov) => {   // keadaan kabut pada jam h (cuaca dibekukan)
    S.WEATHER.cover = ov ? 1 : 0; S.WEATHER.ov = ov ? 1 : 0; S.clock.hour = h; S.updateLighting();
    const c = S.scene.fog.color, U = S.LIGHT.uniforms;
    return { d: S.scene.fog.density, c: [c.r, c.g, c.b], far: U.uL_FarAvg.value.toArray(), fogD: U.uL_FogD.value };
  };
  const base = S.CONFIG.fogDensity, hrs = [4.0, 5.0, 6.0, 6.6, 7.2, 8.0, 9.0, 9.6, 12.0], v = {};
  for (const h of hrs) { v[h] = at(h, false); info.push(`jam ${h}: kerapatan ${(v[h].d / base).toFixed(2)} x dasar, warna ${v[h].c.map((x) => x.toFixed(3)).join(' ')}`); }
  out['jam 4,0 dan 12,0 sama dengan dasar (kabut pagi tidak aktif)'] = Math.abs(v[4].d - base) < 1e-9 && Math.abs(v[12].d - base) < 1e-9;
  out[`naik 5,0 -> 6,0 (${(v[5].d / base).toFixed(2)} -> ${(v[6].d / base).toFixed(2)})`] = v[6].d > v[5].d && v[5].d > base;
  // V4: di Ultra / Tinggi (ATMO.gate) kabut pagi menjadi lapisan menempel tanah di compMat; kabut rata material hanya +1x (puncak 2x)
  const pk = S.ATMO && S.ATMO.gate ? 2 : 5;
  out[`puncak 6,0-7,2 sekitar ${pk}x (${(v[6.6].d / base).toFixed(2)})` + (pk === 2 ? ', V4 lapisan kabut tanah aktif' : '')] = Math.abs(v[6.6].d / base - pk) < 0.05 && Math.abs(v[7.2].d / base - pk) < 0.05;
  if (pk === 2) out[`V4: kabut tanah jam 6,6 penuh (ATMO.mist ${S.ATMO.mist.toFixed(2)})`] = S.ATMO.mist > 0.95;
  out[`menipis 8,0 -> 9,0 -> 9,6 (${(v[8].d / base).toFixed(2)} ${(v[9].d / base).toFixed(2)} ${(v[9.6].d / base).toFixed(2)})`] = v[8].d > v[9].d && v[9].d > base && Math.abs(v[9.6].d - base) < 1e-9;
  out['farEnv memakai kerapatan yang sama (uL_FogD)'] = Math.abs(v[6.6].fogD - v[6.6].d) < 1e-12;
  const lum = (a) => 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2], sat = (a) => Math.max(...a) - Math.min(...a);
  // pantulan daratan seberang: pada jam 6,6 lebih dekat ke warna kabut daripada tanpa kabut pagi (dibanding jam 6,6 mendung tidak relevan)
  const s0 = at(6.6, false); S.CONFIG.fogDensity = 0; const s1 = at(6.6, false); S.CONFIG.fogDensity = base;   // tanpa kabut sama sekali
  const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
  out[`pantulan daratan ikut berkabut jam 6,6 (jarak ke warna kabut ${dist(s0.far, s0.c).toFixed(3)} < tanpa kabut ${dist(s1.far, s0.c).toFixed(3)})`] = dist(s0.far, s0.c) < dist(s1.far, s0.c);
  at(12, false);
  out['di luar pagi uL_FarAvg sama dengan rumus lama (kabut 10,8%)'] = (() => { const U = S.LIGHT.uniforms, FL = U.uL_FarLight.value, L = S.FAR.land, F = U.uL_FogCol.value;
    const e = [L[0] * FL.x * 0.892 + F.x * 0.108, L[1] * FL.y * 0.892 + F.y * 0.108, L[2] * FL.z * 0.892 + F.z * 0.108];
    return dist(e, U.uL_FarAvg.value.toArray()) < 1e-6; })();
  const m = at(6.6, true);
  out[`mendung: kabut pagi tidak menumpuk (${(m.d / base).toFixed(2)} x = 1 + 0,25 + 0,9)`] = Math.abs(m.d / base - 2.15) < 1e-6;
  info.push(`saturasi warna kabut jam 6,6 ${sat(v[6.6].c).toFixed(3)} vs jam 9,6 ${sat(v[9.6].c).toFixed(3)}; luminans ${lum(v[6.6].c).toFixed(3)} vs ${lum(v[9.6].c).toFixed(3)}`);
  // render pagi tanpa nilai tidak valid
  at(6.6, false); await wait(1500);
  const THREE = await import('https://cdn.jsdelivr.net/npm/three@0.186.1/build/three.module.js');
  const rt = new THREE.WebGLRenderTarget(160, 100, { type: THREE.FloatType }), px = new Float32Array(160 * 100 * 4);
  let bad = 0, n = 0;
  for (let k = 0; k < 3; k++) {
    S.clock.hour = 6.6; S.updateLighting();
    S.renderer.setRenderTarget(rt); S.renderer.render(S.scene, S.camera); S.renderer.setRenderTarget(null);
    S.renderer.readRenderTargetPixels(rt, 0, 0, 160, 100, px);
    for (let i = 0; i < px.length; i++) { n++; if (!Number.isFinite(px[i]) || px[i] < 0) bad++; }
    await wait(500);
  }
  rt.dispose();
  out[`render pagi (jam 6,6) tanpa nilai tidak valid (${bad} dari ${n})`] = bad === 0;
  out.__info = info;
  return out;
})()
"""

async def main():
    local = os.environ.get('THREE_LOCAL')
    async with async_playwright() as p:
        exe = os.environ.get('CHROMIUM')
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'], **({'executable_path': exe} if exe else {}))
        pg = await b.new_page(viewport={'width': 320, 'height': 200})
        errs = []
        pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
        pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' else None)
        if local:
            async def serve(route):
                await route.fulfill(path=str(pathlib.Path(local) / route.request.url.rsplit('/', 1)[-1]), content_type='text/javascript',
                                    headers={'Access-Control-Allow-Origin': '*'})
            await pg.route('https://cdn.jsdelivr.net/**', serve)
        await pg.goto(ROOT.joinpath(HTML).as_uri(), wait_until='commit', timeout=240000)
        await pg.wait_for_function('window.__stationReady === true', timeout=240000)
        res = await pg.evaluate(UJI)
        info = res.pop('__info', [])
        for k, v in res.items(): print(('OK   ' if v else 'GAGAL'), k)
        for r in info: print('   ', r)
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())
