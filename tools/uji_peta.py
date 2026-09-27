"""Uji 13d (Copper Corn Station): peta besar M. Kanvas dan latar tergambar, 10 penanda lokasi di dalam bingkai,
zoom dan pusatkan ke pemain, klik penanda memindah pemain dan menutup peta, legenda ikut bahasa.
Pakai: python tools/uji_peta.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(async () => {
  const S = window.__station, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms));
  document.getElementById('start').hidden = true;
  S.toggleMap(); await wait(2500);
  const cv = document.getElementById('mapCanvas');
  out[`kanvas peta ${cv.width}x${cv.height}`] = cv.width > 400 && cv.height > 250;
  const px = cv.getContext('2d').getImageData(cv.width * 0.3 | 0, cv.height / 2 | 0, 1, 1).data;
  out['latar dan rel tergambar'] = px[3] === 255 && px[0] + px[1] + px[2] > 60;
  const inside = S.MAP_MARKS.filter((m) => m.px >= 0 && m.px <= cv.width && m.py >= 0 && m.py <= cv.height).length;
  out[`penanda di dalam bingkai: ${inside} dari ${S.MAP_MARKS.length}`] = inside === S.MAP_MARKS.length && inside >= 10;
  S.mapZoomAt(3); S.mapCenterMe();
  const pxP = S.MAPV.W / 2 + (S.player.za - S.MAPV.cx) * S.MAPV.k;
  out[`zoom ${S.MAPV.zoom}, pemain terlihat di peta (x ${Math.round(pxP)} dari ${S.MAPV.W})`] = S.MAPV.zoom > 1 && pxP > 0 && pxP < S.MAPV.W;
  S.mapGo(S.MAP_MARKS[5]);
  out['klik penanda 6: pindah ke lapangan baseball, peta tertutup'] = document.getElementById('map').hidden && Math.abs(S.player.za - S.SPOTS.baseball.za) < 1;
  S.setLang('en'); S.toggleMap(); await wait(300);
  const lh = [...document.querySelectorAll('#mapLegend .lh')].map((x) => x.textContent).join(' | ');
  out[`legenda English: ${lh}`] = /Places/.test(lh); S.toggleMap(); S.setLang('id');
  return out;
})()
"""

async def main():
    page_url = pathlib.Path(__file__).resolve().parent.parent.joinpath('experiences/cooper-station/index.html').as_uri()
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        pg = await b.new_page(viewport={'width': 1200, 'height': 800})
        errs = []
        pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
        await pg.goto(page_url)
        await pg.wait_for_function('window.__stationReady === true', timeout=240000)
        for k, v in (await pg.evaluate(UJI)).items(): print(('OK   ' if v else 'GAGAL'), k)
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())
