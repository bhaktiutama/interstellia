"""Uji 14a (Copper Corn Station): hutan lebat. Jumlah dan tinggi pohon hutan, tidak ada rumah di blok hutan,
jalan setapak bebas pohon, tidak ada pohon di koridor rel, tombol 0 mendarat di jalan setapak, pakis tergambar di dekat
pemain (Ultra) dan mati di Hemat, biaya gambar di tengah hutan per preset dicatat.
Pakai: python tools/uji_hutan.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(async () => {
  const S = window.__station, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms)), F = S.FOREST;
  const CIRC = 2 * Math.PI * S.R, wrap = (d) => ((d + CIRC / 2) % CIRC + CIRC) % CIRC - CIRC / 2;
  const ft = S.TREES.list.filter((t) => t.forest), hs = ft.map((t) => S.TREES.templates[t.tpl].height * t.sc);
  out[`pohon hutan: ${ft.length}, tinggi ${Math.min(...hs).toFixed(0)}-${Math.max(...hs).toFixed(0)} m`] = ft.length > 3000 && Math.min(...hs) >= 21 && Math.max(...hs) <= 36;
  out[`rumah di blok hutan: ${S.houseList.filter(([s, za]) => S.inForest(s, za, 5)).length}`] = S.houseList.filter(([s, za]) => S.inForest(s, za, 5)).length === 0;
  const trail = S.TREES.list.filter((t) => S.inForest(t.s, t.za) && Math.abs(t.s - S.forestTrail(t.za)) < F.trailW / 2 + 0.5).length;
  out[`pohon di jalan setapak: ${trail}`] = trail === 0;
  out[`pohon di koridor rel: ${S.TREES.list.filter((t) => Math.abs(wrap(t.s)) < 7).length}`] = S.TREES.list.filter((t) => Math.abs(wrap(t.s)) < 7).length === 0;
  S.clock.hour = 11; S.applyPreset(0); S.teleport('forest'); await wait(3000);
  const d = Math.abs(S.player.theta * S.R - S.forestTrail(S.player.za));
  out[`tombol 0: di jalan setapak (${d.toFixed(1)} m dari tengah jalan)`] = d < F.trailW / 2;
  out[`Ultra: pakis tergambar ${F.mesh.geometry.instanceCount}`] = F.mesh.geometry.instanceCount > 200;
  const cost = (i) => { let full = 0; S.TREES.templates.forEach((T) => { full += T.bark.count; }); const inf = S.renderer.info.render; return `preset ${i}: ${full} pohon mesh penuh, ${Math.round(inf.triangles / 1000)} rb segitiga`; };
  const c0 = cost(0);
  S.applyPreset(4); await wait(3000);
  out[`Hemat: pakis mati (${F.mesh.geometry.instanceCount}) | ${c0} | ${cost(4)}`] = F.mesh.geometry.instanceCount === 0;
  S.applyPreset(0);
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
