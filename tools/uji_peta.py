"""Uji 13d + peta A (Copper Corn Station): peta besar M. Kanvas dan latar tergambar, 22 penanda lokasi di dalam bingkai,
zoom dan pusatkan ke pemain, klik penanda memindah pemain dan menutup peta, legenda ikut bahasa; peta A: 8 tempat fisika
(lokasi tujuan tidak di dalam collider atau air, hub = melayang), tab samping (satu panel tampil, tab diingat), hologram 3D
tergambar dan sorotan memutar silinder sampai tempat itu menghadap pengamat.
Pakai: python tools/uji_peta.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, os, pathlib
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
  out[`penanda di dalam bingkai: ${inside} dari ${S.MAP_MARKS.length}`] = inside === S.MAP_MARKS.length && inside >= 22;
  S.mapZoomAt(3); S.mapCenterMe();
  const pxP = S.MAPV.W / 2 + (S.player.za - S.MAPV.cx) * S.MAPV.k;
  out[`zoom ${S.MAPV.zoom}, pemain terlihat di peta (x ${Math.round(pxP)} dari ${S.MAPV.W})`] = S.MAPV.zoom > 1 && pxP > 0 && pxP < S.MAPV.W;
  S.mapGo(S.MAP_MARKS[5]);
  out['klik penanda 6: pindah ke lapangan baseball, peta tertutup'] = document.getElementById('map').hidden && Math.abs(S.player.za - S.SPOTS.baseball.za) < 1;
  // peta A: tempat fisika
  const fis = S.MAP_MARKS.filter((m) => m.fis);
  out[`tempat fisika: ${fis.map((m) => m.key).join(' ')}`] = fis.length === 8 && new Set(S.MAP_MARKS.map((m) => m.key)).size === S.MAP_MARKS.length;
  for (const k of ['aqueduct', 'pump', 'lake', 'ring', 'capB']) {
    const T = S.SPOTS[k]; if (!T) { out[`lokasi ${k} ada`] = false; continue; }
    const col = S.colAt(T.s, T.za, 0.4), w = S.waterAt(T.s, T.za);
    out[`lokasi ${k}: s ${Math.round(T.s)} za ${Math.round(T.za)}, tanpa collider, tidak di air (kedalaman ${w ? w.depth.toFixed(2) : 0})`] = !col && !(w && w.depth > 0.05);
  }
  S.MAP_MARKS.find((m) => m.key === 'H').go();
  out[`H: hub nol-g, state ${S.player.state}`] = S.player.state === 'float';
  S.MAP_MARKS.find((m) => m.key === 'D').go();
  out[`D: dek pandang, h ${Math.round(S.player.h)}`] = S.player.deck && S.player.h > 170;
  S.MAP_MARKS.find((m) => m.key === 'W').go();
  out['W: danau terbesar'] = S.player.state === 'ground' && Math.abs(S.player.za - S.SPOTS.lake.za) < 1;
  // tab dan hologram (mapGo menutup peta lewat toggleMap, jadi buka hanya bila tertutup)
  if (document.getElementById('map').hidden) S.toggleMap(); await wait(300);
  S.mapTab('fisika');
  const shown = [...document.querySelectorAll('#mapLegend [data-mpane]')].filter((d) => !d.hidden).map((d) => d.dataset.mpane);
  out[`tab: panel tampil ${shown.join(',')}, ${document.querySelectorAll('#mapLegend [data-mpane=fisika] button').length} tombol fisika`] = shown.length === 1 && shown[0] === 'fisika' && document.querySelectorAll('#mapLegend [data-mpane=fisika] button').length === 8;
  out['tab diingat'] = localStorage.getItem('cooperStation.mapTab') === 'fisika';
  const hc = document.getElementById('mapHolo'), hd = hc.getContext('2d').getImageData(0, 0, hc.width, hc.height).data;
  let lit = 0; for (let i = 0; i < hd.length; i += 4) if (hd[i] + hd[i + 1] + hd[i + 2] > 120) lit++;
  out[`hologram ${hc.width}x${hc.height}, piksel garis ${lit}`] = hc.width > 100 && lit > 500;
  const m = S.MAP_MARKS.find((x) => x.key === 'U'), p = m.at();
  S.MAPV.hl = { s: p.s, za: p.za, h: 0, name: m.name, i: -1 }; for (let i = 0; i < 40; i++) S.drawHolo(0.1);   // langkah frame langsung (sandbox lambat)
  const o = S.holoP(p.s, p.za, 0, [0, 0, 0]), o2 = S.holoP(p.s + Math.PI * S.R, p.za, 0, [0, 0, 0]);   // titik di seberang keliling
  out[`sorot U: hologram berputar sampai tempat di sisi dekat (beda kedalaman dengan seberang ${(o[2] - o2[2]).toFixed(2)} dari maks 1,96)`] = o[2] - o2[2] > 1.8;
  S.MAPV.hl = null; S.mapTab('tempat'); S.toggleMap();
  S.setLang('en'); S.toggleMap(); await wait(300);
  const lh = [...document.querySelectorAll('#mapLegend .lh')].map((x) => x.textContent).join(' | ');
  out[`legenda English: ${lh}`] = /Places/.test(lh); S.toggleMap(); S.setLang('id');
  return out;
})()
"""

async def main():
    page_url = pathlib.Path(__file__).resolve().parent.parent.joinpath('experiences/cooper-station/index.html').as_uri()
    async with async_playwright() as p:
        kw = {'executable_path': os.environ['CHROMIUM']} if os.environ.get('CHROMIUM') else {}
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'], **kw)
        pg = await b.new_page(viewport={'width': 1200, 'height': 800})
        errs = []
        pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
        await pg.goto(page_url)
        await pg.wait_for_function('window.__stationReady === true', timeout=240000)
        for k, v in (await pg.evaluate(UJI)).items(): print(('OK   ' if v else 'GAGAL'), k)
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())
