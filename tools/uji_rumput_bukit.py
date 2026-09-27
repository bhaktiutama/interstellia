"""Uji 14b (Copper Corn Station): rumput tinggi di bukit. Lapisan rumput tinggi aktif di puncak bukit dan mati di kota,
radius per preset (Hemat: hanya lapisan dekat), rumput pendek lama disembunyikan di bukit, biaya gambar dicatat.
Pakai: python tools/uji_rumput_bukit.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(async () => {
  const S = window.__station, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms)), M = S.MEADOW;
  const cost = () => { const i = S.renderer.info.render; return `${Math.round(i.triangles / 1000)} rb segitiga`; };
  S.clock.hour = 11; S.applyPreset(0);
  S.teleport('cooper'); S.player.theta = 14 / 1000; S.player.za = 625; await wait(3000);
  out[`kota: rumput tinggi mati (${cost()})`] = !M.active && M.near.geometry.instanceCount === 0;
  S.teleport('hill'); await wait(3000);
  out[`puncak bukit Ultra: ${M.near.geometry.instanceCount} + ${M.mid.geometry.instanceCount} rumpun (${cost()})`] = M.active && M.near.geometry.instanceCount > 5000 && M.mid.geometry.instanceCount > 5000;
  out['rumput pendek disembunyikan di bukit (uMeadowOn)'] = S.GRASS.near.material.uniforms.uMeadowOn.value === 1;
  S.applyPreset(4); await wait(3000);
  out[`Hemat: lapisan dekat saja (${M.near.geometry.instanceCount} + ${M.mid.geometry.instanceCount}, ${cost()})`] = M.near.geometry.instanceCount > 0 && M.mid.geometry.instanceCount === 0;
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
