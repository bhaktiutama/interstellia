"""Uji 13b-13c (Copper Corn Station): mobil jalan melingkar melintasi jendela Skyway lewat jembatan (lajur satu keliling
penuh, tidak hilang), tidak ada pohon di jalan yang melintasi promenade, akuaduk sungai ada di titik sungai memotong
jendela, tombol 5 (Skyway) menempatkan pemain di atas lantai kaca dengan pandangan ke bawah.
Pakai: python tools/uji_skyway.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(() => {
  const S = window.__station, out = {}, CIRC = 2 * Math.PI * S.R, SKY = Math.PI * S.R;
  const wrap = (d) => ((d + CIRC / 2) % CIRC + CIRC) % CIRC - CIRC / 2;
  const ring = S.TRAFFIC.lanes.filter((l) => l.type === 1);
  out[`lajur melingkar satu keliling penuh (${Math.round(ring[0].L)} m)`] = ring.every((l) => Math.abs(l.L - CIRC) < 1);
  let crossed = 0; const seen = new Map();
  for (let k = 0; k < 600; k++) {
    S.stepTraffic(0.1, 100 + k * 0.1);
    for (const l of ring) for (const c of l.cars) {
      const d = wrap((l.dir > 0 ? l.seg0 + c.u : l.seg0 + l.L - c.u) - SKY), p = seen.get(c);
      if (p !== undefined && Math.sign(p) !== Math.sign(d) && Math.abs(d) < 30) crossed++; seen.set(c, d);
    }
  }
  out[`mobil melintasi Skyway dalam 60 s: ${crossed}`] = crossed > 10;
  const tr = S.TREES.list.filter((t) => Math.abs(wrap(t.s - SKY)) < 48 && S.SKY_ROADS.some((z) => Math.abs(t.za - z) < 15)).length;
  out[`pohon di jalan Skyway: ${tr}`] = tr === 0;
  out[`akuaduk di za ${S.SKYX.riverZ.toFixed(0)} (sungai memotong jendela)`] = !!S.SKYX.flow && Math.abs(S.SKYX.riverZ - 2381.7) < 1;
  S.teleport('skyway');
  const ds = wrap(S.player.theta * S.R - SKY), pt = S.player.pitch * 180 / Math.PI;
  out[`tombol 5: di atas kaca (${ds.toFixed(1)} m dari tengah), pandangan ${pt.toFixed(0)} derajat`] = Math.abs(ds) < 13 && pt < -45;
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
        for k, v in (await pg.evaluate(UJI)).items(): print(('OK   ' if v else 'GAGAL'), k)
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())
