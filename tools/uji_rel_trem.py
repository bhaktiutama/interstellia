"""Uji 13a (Copper Corn Station): koridor rel trem bersih. Semua instance di scene diubah ke koordinat stasiun;
tidak boleh ada benda setinggi lebih dari 0,3 m dalam 2,4 m dari as rel (selain rel, alas kerikil, garis peron),
tidak ada pohon dalam 7 m, tidak ada collider di atas rel.
Pakai: python tools/uji_rel_trem.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(() => {
  const S = window.__station, R = S.R, CIRC = 2 * Math.PI * R, HALF = 4000, out = {};
  const wrap = (d) => ((d + CIRC / 2) % CIRC + CIRC) % CIRC - CIRC / 2;
  const m = new S.camera.matrix.constructor(), v = new S.camera.position.constructor(), bad = [];
  S.scene.updateMatrixWorld(true);
  S.scene.traverse((o) => {
    if (!o.isInstancedMesh) return;
    for (let i = 0; i < o.count; i++) {
      o.getMatrixAt(i, m); v.setFromMatrixPosition(m).applyMatrix4(o.matrixWorld);
      const s = Math.atan2(v.y, v.x) * R, za = v.z + HALF, h = R - Math.hypot(v.x, v.y);
      if (Math.abs(wrap(s)) < 2.4 && za > 30 && za < 7970 && h > 0.3 && h < 15) bad.push(`${wrap(s).toFixed(1)},${Math.round(za)},${h.toFixed(1)}`);
    }
  });
  out[`benda di koridor rel: ${bad.length}${bad.length ? ' (' + bad.slice(0, 5).join(' ; ') + ')' : ''}`] = bad.length === 0;
  const tr = S.TREES.list.filter((t) => Math.abs(wrap(t.s)) < 7);
  out[`pohon dalam 7 m dari rel: ${tr.length}`] = tr.length === 0;
  const col = S.COL.items.filter(([s, za, hs]) => Math.abs(wrap(s)) - hs < 1.9 && za > 30 && za < 7970);
  out[`collider di atas rel: ${col.length}`] = col.length === 0;
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
