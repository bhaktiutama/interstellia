"""Uji tahap 16 (Copper Corn Station): distrik. Tiap sel kota tepat satu distrik (14 distrik kota, nama unik), zona luar kota
bernama (taman, pertanian), halte trem bernama distrik, notifikasi distrik muncul saat pemain pindah distrik.
Pakai: python tools/uji_distrik.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(async () => {
  const S = window.__station, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const CIRC_H = Math.PI * S.R, D = S.DISTRICTS, city = D.filter((d) => d.kind === 'mega' || d.kind === 'astro');
  const cnt = new Map(); let none = 0;
  for (const c of S.cityCells) { const d = S.districtAt(c.s0 + S.ART / 2, c.z0 + 125); if (!d) none++; else cnt.set(d.name, (cnt.get(d.name) || 0) + 1); }
  out[`sel kota ${S.cityCells.length}: tanpa distrik ${none}, distrik kota terisi ${cnt.size}/${city.length}`] = none === 0 && cnt.size === 14 && city.length === 14;
  out[`nama distrik unik (${D.length})`] = new Set(D.map((d) => d.name)).size === D.length;
  const mega = city.filter((d) => d.kind === 'mega').map((d) => d.name).sort().join(', ');
  out[`megacity: ${mega}`] = mega === 'Delhi, Kairo, New York, Shanghai, Tokyo';
  const luar = [[1000, 2900], [4000, 2900], [0, 3500], [0, 4500], [0, 5500], [0, 6200]].map(([s, za]) => (S.districtAt(s, za) || {}).name);
  out[`luar kota: ${luar.join(', ')}`] = luar.join() === 'Taman Nil,Taman Mekong,Punjab,Pampas,Iowa,Ukraina';
  const stops = S.TRAM.stops.map((s) => s.name).join(', ');
  out[`halte: ${stops}`] = /New York, Pasar New York, Kairo, Taman Nil, Pampas/.test(stops);
  // 16c: pusat New York dan balai distrik
  const site = (t) => S.SITES.filter((x) => x.type === t);
  const cbd = S.BUILD.flat.filter((b) => Math.hypot(((b[0] + CIRC_H) % (2 * CIRC_H)) - CIRC_H, b[1] - 480) < 400 && b[5] === 8).map((b) => b[4]);
  out[`menara ikon ${S.LANDMARK.h.toFixed(0)} m, menara CBD ${cbd.length} (tertinggi ${Math.max(...cbd).toFixed(0)} m), alun-alun ${site('alun').length}`] = S.LANDMARK.h > 200 && Math.max(...cbd) > 120 && site('alun').length === 1;
  const balai = site('balai');
  out[`balai distrik ${balai.length}, tiap distrik kota satu`] = balai.length === 14 && new Set(balai.map((x) => x.district.name)).size === 14 && balai.every((x) => S.districtAt(x.q.bs, x.q.bz) === x.district);
  S.setLang('id'); S.teleport('cooper'); await wait(1500); S.teleport('baseball');
  const here = S.districtAt(S.player.theta * S.R, S.player.za);
  let toast = ''; for (let q = 0; q < 40 && toast !== `Distrik ${here && here.name}`; q++) { await wait(250); toast = document.getElementById('toast').textContent; }   // HUD diperbarui berkala
  out[`notifikasi saat pindah: "${toast}"`] = !!here && toast === `Distrik ${here.name}`;
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
        pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' else None)
        await pg.goto(page_url)
        await pg.wait_for_function('window.__stationReady === true', timeout=240000)
        for k, v in (await pg.evaluate(UJI)).items(): print(('OK   ' if v else 'GAGAL'), k)
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())
