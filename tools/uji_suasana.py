"""Uji tahap 12b-5 (Cooper Station): kafe, lampu untaian, bendera, sepeda, orang duduk di kafe, suara kota berjalan
tanpa error, dan tidak ada normal nol di geometri (normal nol = NaN di sebagian GPU, tampil sebagai titik putih menyala).
Pakai: python tools/uji_suasana.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(async () => {
  const st = window.__station, V = st.VIBE, out = {};
  out[`kafe: ${V.counts.cafeTable} meja, ${V.counts.cafeChair} kursi`] = V.counts.cafeTable > 20;
  out[`lampu untaian: ${V.counts.bulb} bohlam`] = V.counts.bulb > 300;
  out[`bendera dan umbul-umbul: ${V.nFlags}`] = V.nFlags >= 6;
  out[`sepeda di halte: ${V.counts.bike}`] = V.counts.bike > 0;
  const duduk = st.PEDS.list.filter((p) => p.pose === 2 && V.cafeSeats.some(([s, z]) => Math.abs(s - p.s) < 0.01 && Math.abs(z - p.za) < 0.01)).length;
  out[`orang duduk di kafe: ${duduk}`] = duduk > 0;
  let nol = 0; const seen = new Set();
  st.TREES.templates[0].leaf.parent.parent.traverse((o) => { const g = o.geometry; if (!g || seen.has(g) || !g.attributes.normal) return; seen.add(g);
    const n = g.attributes.normal.array; for (let i = 0; i < n.length; i += 3) if (n[i] * n[i] + n[i + 1] * n[i + 1] + n[i + 2] * n[i + 2] < 1e-12) nol++; });
  out[`titik dengan normal nol: ${nol}`] = nol === 0;
  window.dispatchEvent(new KeyboardEvent('keydown', { code: 'KeyI' })); window.dispatchEvent(new KeyboardEvent('keyup', { code: 'KeyI' }));
  const K = st.FURN.kinds.cafeTable; st.teleport('cooper'); st.player.theta = (K.ps[0] + 3) / st.R; st.player.za = K.pz[0];
  await new Promise((r) => setTimeout(r, 3000));
  out['suara kota berjalan (audio aktif)'] = !!(st.AUDIO.crowd && st.AUDIO.car);
  return out;
})()
"""

async def main():
    page_url = pathlib.Path(__file__).resolve().parent.parent.joinpath('experiences/cooper-station/index.html').as_uri()
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
        pg = await b.new_page(viewport={'width': 320, 'height': 200})
        errs = []
        pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
        await pg.goto(page_url)
        await pg.wait_for_function('window.__stationReady === true', timeout=240000)
        for k, v in (await pg.evaluate(UJI)).items(): print(('OK   ' if v else 'GAGAL'), k)
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())
