"""Uji tahap 12b-1 (Cooper Station): peron trem tidak di jalan, lalu lintas 30 menit tanpa tabrakan mobil-trem,
tanpa mobil tumpang tindih, tanpa mobil dari dua arah di dalam simpang yang sama.
Pakai: python tools/uji_lalu_lintas.py   (butuh: pip install playwright && playwright install chromium)
Simulasi dijalankan langsung (stepTram + stepTraffic tiap 0,1 s), jadi hasil tidak bergantung FPS."""
import asyncio, json, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(() => {
  const st = window.__station, TR = st.TRAFFIC, X = st.XING, tram = st.tram, TRAM = st.TRAM, R = st.R, out = {};
  const CIRC = 2 * Math.PI * R, wrapS = (x) => { x = ((x % CIRC) + CIRC) % CIRC; return x > CIRC / 2 ? x - CIRC : x; };
  // 1) peron vs jalan
  const roads = []; for (let m = 1; m <= 10; m++) if (!st.RINGS_Z.some((z) => Math.abs(z - m * 250) < 1)) roads.push([m * 250, 12, 'arteri']);
  for (const z of st.RINGS_Z) roads.push([z, 8, 'cincin']);
  out.peronDiJalan = TRAM.stops.filter((s) => roads.some(([z, h]) => Math.abs(s.za - z) < 13 + h)).map((s) => s.name);
  out.jarakPeronKeJalan = TRAM.stops.map((s) => `${s.name} ${Math.min(...roads.map(([z, h]) => Math.abs(s.za - z) - 13 - h)).toFixed(0)} m`);
  // 2) simulasi 30 menit
  const pos = (c) => { const ln = c.ln, along = ln.seg0 + (ln.dir > 0 ? c.u : ln.L - c.u); return ln.type === 0 ? [ln.line + ln.lat * ln.dir, along] : [along, ln.line - ln.lat * ln.dir]; };
  let hitTram = 0, overlap = 0, boxConflict = 0, stopsAtRed = 0, maxQueue = 0, tramCloses = 0, prevClosed = X.closed.slice(); const hitList = [];
  const dt = 0.1, n = 18000; let ms = 0;
  const cars = TR.carList.filter((c) => c.on);
  for (let k = 0; k < n; k++) {
    st.clock.sim += dt; st.stepTram(dt);
    const t0 = performance.now(); st.stepTraffic(dt); ms += performance.now() - t0;
    X.closed.forEach((c, j) => { if (c && !prevClosed[j]) tramCloses++; }); prevClosed = X.closed.slice();
    if (k % 5) continue;
    const occ = new Map();
    for (const c of cars) {
      const [s, za] = pos(c), sw = wrapS(s);
      // trem: lebar 2,65 m di s = 0, panjang 18 m
      if (Math.abs(sw) < 1.33 + 2.2 && Math.abs(za - tram.za) < 9 + 0.9) { hitTram++; if (hitList.length < 5) hitList.push({ t: st.clock.sim.toFixed(1), sw: sw.toFixed(1), za: za.toFixed(1), tram: tram.za.toFixed(1), v: c.v.toFixed(1) }); }
      // kotak simpang: siapa di dalam
      const kk = Math.round(s / st.ART), mm = Math.round(za / 250);
      if (kk > 0 && kk < 26 && Math.abs(wrapS(s - kk * st.ART)) < 12 && Math.abs(za - mm * 250) < 12) { const key = kk * 100 + mm; const o = occ.get(key) || [0, 0]; o[c.ln.type]++; occ.set(key, o); }
      if (c.v < 0.3) stopsAtRed++;
    }
    for (const o of occ.values()) if (o[0] && o[1]) boxConflict++;
    for (const ln of TR.lanes) { let q = 0; const C = ln.cars.filter((c) => c.on); for (let j = 0; j < C.length; j++) { const a = C[j], b = C[(j + 1) % C.length]; if (C.length > 1 && ((b.u - a.u + ln.L) % ln.L) < 4.4) overlap++; if (a.v < 0.3) q++; } maxQueue = Math.max(maxQueue, q); }
  }
  Object.assign(out, { detikSim: n * dt, mobilAktif: cars.length, tabrakanTrem: hitTram, contoh: hitList, mobilTumpangTindih: overlap, konflikDalamSimpang: boxConflict, perlintasanTertutupKali: tramCloses, mobilBerhentiDiLajurMaks: maxQueue, sampelMobilBerhenti: stopsAtRed, msPerLangkahRata: +(ms / n).toFixed(3) });
  const vs = cars.map((c) => c.v); out.kecepatanRata = +(vs.reduce((a, b) => a + b, 0) / vs.length).toFixed(2);
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
        ok = not h['peronDiJalan'] and h['tabrakanTrem'] == 0 and h['mobilTumpangTindih'] == 0 and h['konflikDalamSimpang'] == 0
        print('HASIL:', 'LOLOS' if ok else 'GAGAL')
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())
