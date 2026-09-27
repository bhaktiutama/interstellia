"""Uji tahap 12b-3 (Copper Corn Station): pejalan kaki menyeberang hanya saat lampu "jalan" (tidak ada orang di jalan
saat lampu mobil yang melintas hijau), biaya CPU simulasi, preset Hemat mengecilkan radius dan kepadatan.
Pakai: python tools/uji_pejalan_kaki.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, json, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(() => {
  const st = window.__station, P = st.PEDS, out = {};
  let konflik = 0, menunggu = 0, menyeberang = 0, sampel = 0, msStep = 0, msUpd = 0; const contoh = [];
  const dt = 0.1, n = 6000;
  st.teleport('cooper'); st.player.theta = 250 / st.R; st.player.za = 600; st.updateCamera();
  for (let k = 0; k < n; k++) {
    st.clock.sim += dt;
    let t0 = performance.now(); st.stepPeds(dt); msStep += performance.now() - t0;
    t0 = performance.now(); st.updatePeds(); msUpd += performance.now() - t0;
    if (k % 10) continue;
    for (const p of P.walk) {
      if (p.kind !== 'z' && p.kind !== 's') continue;
      for (const c of p.cross) if (Math.abs(p.u - c.c) < 12) {
        sampel++; menyeberang++;
        if (st.sigState(c.k, c.m, 1 - c.axis, st.clock.sim) === 0) { konflik++; if (contoh.length < 4) contoh.push({ jenis: p.kind, u: +(p.u - c.c).toFixed(1), q: +st.sigQ(c.k, c.m, c.axis, st.clock.sim).toFixed(1) }); }
      }
      if (p.pose === 1) menunggu++;
    }
  }
  const tot = { total: P.list.length };
  Object.assign(out, tot, { detikSim: n * dt, sampelMenyeberang: menyeberang, diJalanSaatMobilHijau: konflik, contoh, sampelMenunggu: menunggu,
    msStepPedsRata: +(msStep / n).toFixed(3), msUpdatePedsRata: +(msUpd / n).toFixed(3), instanceGPU: P.n });
  const H = st.PRESETS.findIndex((p) => p.name === 'Hemat'); st.applyPreset(H); st.updatePeds(); out.hemat = { radius: P.radius, dens: P.dens, instanceGPU: P.n }; st.applyPreset(0);
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
        await pg.goto(page_url)
        await pg.wait_for_function('window.__stationReady === true', timeout=240000)
        h = await pg.evaluate(UJI)
        print(json.dumps(h, indent=1, ensure_ascii=False))
        ok = h['diJalanSaatMobilHijau'] == 0 and h['sampelMenyeberang'] > 0 and h['hemat']['radius'] == 80
        print('HASIL:', 'LOLOS' if ok else 'GAGAL')
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())
