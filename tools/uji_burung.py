"""Uji tahap 12b-4 (Cooper Station): kawanan burung siang, merpati terbang saat didekati lalu hinggap lagi,
burung pulang saat senja dan tidak ada di malam hari.
Pakai: python tools/uji_burung.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, json, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(() => {
  const st = window.__station, B = st.BIRDS, P = st.player, out = {};
  st.clock.hour = 10;
  for (let k = 0; k < 50; k++) { st.stepBirds(0.1); } st.updateBirds();
  out.siang = { kawanan: B.flocks.filter((f) => !f.dead).length, burungTerbang: B.flocks.reduce((a, f) => a + (f.members ? f.members.filter((b) => !b.gone).length : 0), 0), instanceGPU: B.n, kelompokMerpati: B.groups.length };
  const f0 = B.flocks[0].members[0]; out.contohTinggi = +f0.p[2].toFixed(1);
  // merpati: pemain mendekat
  const G = B.groups[0]; st.teleport('cooper'); P.theta = G.s / st.R; P.za = G.za + 20; P.state = 'ground'; st.updateCamera();
  for (let k = 0; k < 10; k++) st.stepBirds(0.1);
  out.merpatiSebelum = G.birds.filter((b) => b.fly).length;
  P.za = G.za + 1; for (let k = 0; k < 3; k++) st.stepBirds(0.1);
  out.merpatiTerbangSaatDidekati = G.birds.filter((b) => b.fly).length + ' dari ' + G.birds.length;
  P.za = G.za + 60; for (let k = 0; k < 150; k++) { st.clock.sim += 0.1; st.stepBirds(0.1); }
  out.merpatiHinggapLagi = G.birds.filter((b) => !b.fly).length + ' dari ' + G.birds.length;
  st.clock.hour = 17.9; for (let k = 0; k < 900; k++) st.stepBirds(0.1);
  out.senjaBurungTersisa = B.flocks.reduce((a, f) => a + (f.members ? f.members.filter((b) => !b.gone).length : 0), 0);
  st.clock.hour = 23; for (let k = 0; k < 10; k++) st.stepBirds(0.1); st.updateBirds(); out.malamInstance = B.n;
  let t0 = performance.now(); st.clock.hour = 10; for (let k = 0; k < 200; k++) st.stepBirds(0.05); out.msStepBurung = +((performance.now() - t0) / 200).toFixed(3);
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
        ok = h['siang']['burungTerbang'] > 0 and h['merpatiTerbangSaatDidekati'].startswith(h['merpatiTerbangSaatDidekati'].split(' dari ')[1]) and h['malamInstance'] == 0
        print('HASIL:', 'LOLOS' if ok else 'GAGAL')
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())
