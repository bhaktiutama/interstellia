"""Uji tahap 12b-2 + 25b (Copper Corn Station): 17 jenis pohon (8 lama + 6 jenis 25b + 3 jenis 25d; 8 dengan ?pohon=lama),
tinggi jenis baru, persentase pohon berwarna per suasana daun, daun jatuh mati di preset Hemat dan bisa dinyalakan manual.
Pakai: python tools/uji_pohon.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(() => {
  const st = window.__station, T = st.TREES, out = {}, jenis = new Set(T.list.map((t) => T.templates[t.tpl].kind));
  out['17 jenis pohon terpakai (' + [...jenis].join(', ') + ')'] = jenis.size === 17;
  // 25b: jumlah dan tinggi (persentil 10 / 50 / 90, m) per jenis; elm sebagai pembanding
  const pc = (a, q) => a[Math.min(a.length - 1, Math.floor(q * a.length))];
  for (const k of ['elm', 'aspen', 'beech', 'basswood', 'chestnut', 'ash', 'walnut', 'hickory', 'blacklocust', 'honeylocust']) {
    const hs = T.list.filter((t) => !t.forest && T.templates[t.tpl].kind === k).map((t) => T.templates[t.tpl].height * t.sc).sort((a, b) => a - b);
    out[`INFO ${k}: ${hs.length} pohon, tinggi ${[0.1, 0.5, 0.9].map((q) => hs.length ? pc(hs, q).toFixed(1) : '-').join(' / ')} m`] = true;
    if (k !== 'elm') out[`${k}: ada di kota/taman/luar, median tinggi 5-20 m`] = hs.length > 50 && pc(hs, 0.5) > 5 && pc(hs, 0.5) < 20;
  }
  const pct = (m) => 100 * T.list.filter((t) => st.leafColorFor(t, m)).length / T.list.length;
  const [h, c, g] = [0, 1, 2].map(pct);
  out[`Hijau: hanya pohon bunga (${h.toFixed(1)}%)`] = h < 6;
  out[`Campur: 15-25% berwarna (${c.toFixed(1)}%)`] = c >= 15 && c <= 25;
  out[`Gugur: lebih dari separuh (${g.toFixed(1)}%)`] = g > 50;
  const H = st.PRESETS.findIndex((p) => p.name === 'Hemat'), fu = st.LEAF.fallUser;
  st.LEAF.fallUser = null; st.applyPreset(H); out['Hemat: daun jatuh mati'] = st.FALL.n === 0;
  st.LEAF.fallUser = true; st.applyPreset(H); out['Hemat + nyala manual: daun jatuh ada'] = st.FALL.n > 0;
  st.LEAF.fallUser = fu; st.applyPreset(0); out['Ultra: 3000 daun jatuh'] = st.FALL.n === 3000 || fu === false;
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
        for k, v in (await pg.evaluate(UJI)).items(): print('     ' + k[5:] if k.startswith('INFO ') else ('OK   ' if v else 'GAGAL') + ' ' + k)
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())
