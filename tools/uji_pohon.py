"""Uji tahap 12b-2 (Cooper Station): 8 jenis pohon, persentase pohon berwarna per suasana daun,
daun jatuh mati di preset Hemat dan bisa dinyalakan manual.
Pakai: python tools/uji_pohon.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(() => {
  const st = window.__station, T = st.TREES, out = {}, jenis = new Set(T.list.map((t) => T.templates[t.tpl].kind));
  out['8 jenis pohon terpakai (' + [...jenis].join(', ') + ')'] = jenis.size === 8;
  const pct = (m) => 100 * T.list.filter((t) => st.leafColorFor(t, m)).length / T.list.length;
  const [h, c, g] = [0, 1, 2].map(pct);
  out[`Hijau: hanya pohon bunga (${h.toFixed(1)}%)`] = h < 6;
  out[`Campur: 15-25% berwarna (${c.toFixed(1)}%)`] = c >= 15 && c <= 25;
  out[`Gugur: lebih dari separuh (${g.toFixed(1)}%)`] = g > 50;
  const H = st.PRESETS.findIndex((p) => p.name === 'Hemat'), fu = st.LEAF.fallUser;
  st.LEAF.fallUser = null; st.applyPreset(H); out['Hemat: daun jatuh mati'] = st.FALL.n === 0;
  st.LEAF.fallUser = true; st.applyPreset(H); out['Hemat + nyala manual: daun jatuh ada'] = st.FALL.n > 0;
  st.LEAF.fallUser = fu; st.applyPreset(0); out['Ultra: 2000 daun jatuh'] = st.FALL.n === 2000 || fu === false;
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
        pg.on('console', lambda m: errs.append(m.type + ': ' + m.text[:200]) if m.type == 'error' else None)
        await pg.goto(page_url)
        await pg.wait_for_function('window.__stationReady === true', timeout=240000)
        await pg.wait_for_timeout(3000)
        for k, v in (await pg.evaluate(UJI)).items(): print(('OK   ' if v else 'GAGAL'), k)
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())
