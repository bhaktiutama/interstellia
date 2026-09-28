"""Uji 15b (Copper Corn Station): mobil di boulevard samping rel trem. Lajur ada di kota dan pertanian, di luar koridor trem
dan peron, simulasi 30 menit tanpa mobil menabrak trem, tanpa konflik di simpang boulevard (mobil boulevard dan mobil
arteri melingkar di kotak simpang yang sama), mobil boulevard berhenti di lampu merah, lampu jalan boulevard terpasang.
Pakai: python tools/uji_boulevard.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(() => {
  const S = window.__station, TR = S.TRAFFIC, tram = S.tram, TRAM = S.TRAM, out = {};
  const CIRC = 2 * Math.PI * S.R, wrapS = (x) => { x = ((x % CIRC) + CIRC) % CIRC; return x > CIRC / 2 ? x - CIRC : x; };
  const pos = (c) => { const ln = c.ln, along = ln.seg0 + (ln.dir > 0 ? c.u : ln.L - c.u); return ln.type === 0 ? [ln.line + ln.lat * ln.dir, along] : [along, ln.line - ln.lat * ln.dir]; };
  const blvd = TR.lanes.filter((ln) => ln.type === 0 && Math.abs(wrapS(ln.line - TRAM.s)) < 1);
  const bc = blvd.flatMap((ln) => ln.cars);
  const inCity = bc.filter((c) => pos(c)[1] < 3200).length, inFarm = bc.length - inCity;
  out[`lajur boulevard ${blvd.length}, mobil ${bc.length} (kota ${inCity}, pertanian ${inFarm})`] = blvd.length === 4 && inCity > 40 && inFarm > 10;
  out[`lajur di luar koridor trem dan peron (jarak terdekat ${Math.min(...blvd.map((l) => l.lat))} m)`] = blvd.every((l) => l.lat > 9);
  let hit = 0, conflict = 0, redStops = 0; const dt = 0.1, n = 18000;
  const cars = TR.carList.filter((c) => c.on);
  for (let k = 0; k < n; k++) {
    S.clock.sim += dt; S.stepTram(dt); S.stepTraffic(dt);
    if (k % 5) continue;
    const box = new Map();
    for (const c of cars) {
      const [s, za] = pos(c), sw = wrapS(s - TRAM.s);
      if (Math.abs(sw) < 3.5 && Math.abs(za - tram.za) < 10) hit++;
      const m = Math.round(za / 250);
      if (Math.abs(sw) < 20 && m >= 1 && m <= 10 && Math.abs(za - m * 250) < 12) { const o = box.get(m) || [0, 0]; o[c.ln.type]++; box.set(m, o); }
      if (c.ln.type === 0 && Math.abs(wrapS(c.ln.line - TRAM.s)) < 1 && c.v < 0.3 && za < 2600) {
        const d = Math.abs(za - m * 250); if (d > 12 && d < 40) redStops++;
      }
    }
    for (const o of box.values()) if (o[0] && o[1]) conflict++;
  }
  out[`30 menit: mobil menabrak trem ${hit}`] = hit === 0;
  out[`30 menit: konflik di simpang boulevard ${conflict}`] = conflict === 0;
  out[`mobil boulevard berhenti di garis henti (${redStops} sampel)`] = redStops > 50;
  out['lampu jalan boulevard ada di kota'] = S.TRAFFIC.lamps > 0;
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
