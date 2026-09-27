"""Uji tahap 12c (Copper Corn Station): angka fisika hujan dan air mancur Coriolis, hujan muncul saat mendung,
tanah basah, angin menguat, tidak ada hujan di dalam terminal.
Pakai: python tools/uji_hujan.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, math, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(() => {
  const st = window.__station, out = {}, g = 9.81, om = st.OMEGA;
  out[`hujan menyamping ${st.RAIN.vlat.toFixed(3)} m/s = 2 omega vt^2/g`] = Math.abs(st.RAIN.vlat - 2 * om * 49 / g) < 1e-3;
  out[`air mancur 10 m/s bergeser ${st.FOUNT.shift10.toFixed(3)} m = (4/3) omega v^3/g^2`] = Math.abs(st.FOUNT.shift10 - 4 / 3 * om * 1000 / (g * g)) < 1e-3;
  while (st.WEATHER.mode !== 'mendung') st.cycleWeather();
  for (let k = 0; k < 150; k++) { st.WEATHER.cover = 0.95; st.updateClouds(1); st.updateRain(1); }
  out[`mendung: hujan ${st.RAIN.mesh.geometry.instanceCount} tetes`] = st.RAIN.mesh.geometry.instanceCount > 0;
  out[`tanah basah ${st.RAIN.wet.toFixed(2)}`] = st.RAIN.wet > 0.8;
  out[`angin menguat ${st.WIND.base.toFixed(2)} m/s`] = st.WIND.base > 3;
  const P = st.player; P.state = 'ground'; P.theta = st.TERM.s / st.R; P.za = st.TERM.za; st.updateRain(0.1);
  out['tidak ada hujan di dalam terminal'] = st.rainSheltered() && st.RAIN.mesh.geometry.instanceCount === 0;
  while (st.WEATHER.mode !== 'cerah') st.cycleWeather();
  for (let k = 0; k < 400; k++) { st.WEATHER.cover = 0.14; st.updateClouds(1); st.updateRain(1); }
  out[`cerah: hujan berhenti, tanah mengering (${st.RAIN.wet.toFixed(2)})`] = st.RAIN.k < 0.02 && st.RAIN.wet < 0.5;
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
