"""Uji 15c (Copper Corn Station): pejalan kaki di trotoar dan jalan setapak, bukan di rumput. Titik rute trotoar kota
(kecuali saat menyeberang jalan atau lewat dek cincin) harus di pita trotoar SIDEWALK (12-17 m dari sumbu arteri),
tidak di dalam collider gedung atau pohon; pejalan kaki taman besar berjalan di PARK_PATHS; mesh jalan setapak punya normal.
Pakai: python tools/uji_trotoar.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(() => {
  const S = window.__station, out = {}, ART = S.ART, SW = S.SIDEWALK, COL = S.COL;
  const CIRC = 2 * Math.PI * S.R, wrapS = (x) => { x = ((x % CIRC) + CIRC) % CIRC; return x > CIRC / 2 ? x - CIRC : x; };
  const inCol = (s, za) => {
    const cs = ((Math.floor((((s % CIRC) + CIRC) % CIRC) / COL.cell) % 1000) + 1000) % 1000, arr = COL.grid.get(cs * 1000 + Math.floor(za / COL.cell));
    return !!arr && arr.some((i) => { const [a, b, hs, hz] = COL.items[i]; return Math.abs(wrapS(s - a)) < hs + 0.25 && Math.abs(za - b) < hz + 0.25; });
  };
  let n = 0, onSw = 0, inside = 0; const bad = [];
  for (const p of S.PEDS.walk) {
    if (p.kind !== 'z' && p.kind !== 's') continue;
    for (let i = 0; i <= 10; i++) {
      const u = p.a + (p.b - p.a) * i / 10, s = p.kind === 'z' ? p.fix : u, za = p.kind === 'z' ? u : p.fix;
      if (p.cross.some((c) => Math.abs(u - c.c) < 12.5)) continue;                 // sedang menyeberang
      if (p.kind === 'z' && [1000, 2000].some((z) => Math.abs(za - z) < 9)) continue;   // dek cincin
      n++; if (SW.d(s, za) >= 0) onSw++; else if (bad.length < 5) bad.push([+s.toFixed(1), +za.toFixed(1)]);
      if (inCol(s, za)) inside++;
    }
  }
  out[`titik rute trotoar di trotoar: ${onSw}/${n}` + (bad.length ? ` contoh luar ${JSON.stringify(bad)}` : '')] = n > 1000 && onSw === n;
  out[`titik rute trotoar di dalam gedung/pohon: ${inside}`] = inside === 0;
  const runs = S.PARK_PATHS.runs, dSeg = (s, za) => Math.min(...runs.map(([a0, a1, b0, b1]) => {
    const vs = a1 - a0, vz = b1 - b0, L2 = vs * vs + vz * vz, t = Math.max(0, Math.min(1, ((s - a0) * vs + (za - b0) * vz) / L2));
    return Math.hypot(s - a0 - vs * t, za - b0 - vz * t); }));
  const park = S.PEDS.walk.filter((p) => p.kind === 'seg' && p.zone === 1);
  let offPath = 0; for (const p of park.slice(0, 400)) for (const t of [0, 0.5, 1]) if (dSeg(p.p0[0] + (p.p1[0] - p.p0[0]) * t, p.p0[1] + (p.p1[1] - p.p0[1]) * t) > 1.3) offPath++;
  out[`pejalan kaki taman besar ${park.length}, di luar jalan setapak ${offPath}`] = park.length > 500 && offPath === 0;
  const km = runs.reduce((a, [a0, a1, b0, b1]) => a + Math.hypot(a1 - a0, b1 - b0), 0) / 1000;
  const N = S.PARK_PATHS.mesh.geometry.attributes.normal;
  out[`jalan setapak ${runs.length} ruas, ${km.toFixed(1)} km, ${N.count / 3} segitiga, normal ada`] = runs.length > 30 && !!N && N.count > 0;
  return out;
})()
"""

async def main():
    page_url = pathlib.Path(__file__).resolve().parent.parent.joinpath('experiences/cooper-station/index.html').as_uri()
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        pg = await b.new_page(viewport={'width': 320, 'height': 200})
        errs = []
        pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
        pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' else None)
        await pg.goto(page_url)
        await pg.wait_for_function('window.__stationReady === true', timeout=240000)
        for k, v in (await pg.evaluate(UJI)).items(): print(('OK   ' if v else 'GAGAL'), k)
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())
