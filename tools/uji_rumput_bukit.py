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
  // kehalusan angin rumput: 60 s langkah 1/60 s; geseran hembusan per langkah <= kecepatan angin x dt, arah berubah pelan
  const V = S.VU || null;
  let maxStep = 0, maxTurn = 0, prev = S.MEADOW_WIND().off.clone(), pa = Math.atan2(S.MEADOW_WIND().w.y, S.MEADOW_WIND().w.x);
  for (let k = 0; k < 3600; k++) {
    S.updateWind(1 / 60);
    const o = S.MEADOW_WIND().off, w = S.MEADOW_WIND().w, a = Math.atan2(w.y, w.x);
    maxStep = Math.max(maxStep, o.distanceTo(prev) / (1 / 60)); prev = o.clone();
    let da = Math.abs(a - pa); if (da > Math.PI) da = 2 * Math.PI - da; maxTurn = Math.max(maxTurn, da * 60); pa = a;
  }
  out[`hembusan bergeser maks ${maxStep.toFixed(2)} m/s, arah angin rumput berubah maks ${(maxTurn * 180 / Math.PI).toFixed(2)} derajat/s`] = maxStep < 8 && maxTurn * 180 / Math.PI < 2;
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
