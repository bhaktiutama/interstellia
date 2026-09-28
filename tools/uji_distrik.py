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
  // 16d: pasar di tempat strategis (Pasar New York dekat halte 1125, pasar tani dekat halte Taman Nil), lapak dan pedagang
  const M = S.MARKET, ny = M.list.find((m) => m.name === 'Pasar New York'), tani = M.list.find((m) => m.farm);
  const dStop = (m, za) => Math.hypot(((m.s + CIRC_H) % (2 * CIRC_H)) - CIRC_H, m.za - za);
  out[`pasar ${M.list.length} (besar ${M.list.filter((m) => m.big).length}), lapak ${M.stalls.length}; Pasar New York ${ny ? dStop(ny, 1125).toFixed(0) : '-'} m dari halte, pasar tani ${tani ? dStop(tani, 2950).toFixed(0) : '-'} m`] =
    M.list.length >= 14 && M.list.filter((m) => m.big).length === 5 && M.stalls.length > 200 && ny && dStop(ny, 1125) < 150 && tani && dStop(tani, 2950) < 80;
  // revisi 16: atap lengkung di atas gedung pasar (6,5 m), lapak ikut tinggi tanah, tanah terinjak di pasar permukiman
  const roofs = M.list.filter((m) => m.big).map((m) => m.roofY);
  out[`atap pasar besar: lengkung ${roofs.map((y) => y[0].toFixed(1) + '-' + y[1].toFixed(1)).join(', ')} m`] = roofs.length === 5 && roofs.every((y) => y[0] >= 6.4 && y[1] > 12);
  // dasar meja lapak pasar tani (tanah tidak datar) = tinggi tanah: titik terendah mesh lapak di sekitar tiap lapak
  const gp = S.MOSQUE.meshG.geometry.attributes.position.array, farm = M.list.find((m) => m.farm);
  const nil = M.stalls.filter(([s, za]) => Math.abs(za - farm.za) < 40 && Math.abs(((s - farm.s + 3 * CIRC_H) % (2 * CIRC_H)) - CIRC_H) < 40);
  let worst = 0, slope = 0;
  for (const [s, za] of nil) {
    let lo = 1e9;
    for (let i = 0; i < gp.length; i += 3) {
      const x = gp[i], y = gp[i + 1], vz = gp[i + 2] + 4000, vs = Math.atan2(y, x) * S.R, h = S.R - Math.hypot(x, y);
      if (Math.abs(vz - za) < 0.8 && Math.abs(((vs - s + 3 * CIRC_H) % (2 * CIRC_H)) - CIRC_H) < 1.4) lo = Math.min(lo, h);
    }
    const g = S.groundH(s, za); worst = Math.max(worst, Math.abs(lo - g)); slope = Math.max(slope, g);
  }
  out[`lapak pasar tani ikut tanah: ${nil.length} lapak, tanah sampai ${slope.toFixed(2)} m, selisih dasar maks ${worst.toFixed(3)} m`] = nil.length > 10 && worst < 0.05;
  const worn = M.list.filter((m) => m.worn), lc = S.landCanvas.getContext('2d');
  const isGreen = (m) => { const LW = S.landCanvas.width, LH = S.landCanvas.height, x = Math.floor((((m.spot.s % (2 * CIRC_H)) + 2 * CIRC_H) % (2 * CIRC_H)) / (2 * CIRC_H) * LW), y = Math.floor((1 - m.spot.za / 8000) * LH), p = lc.getImageData(x, y, 1, 1).data; return p[1] > p[0] * 1.02 && (Math.max(...p.slice(0, 3)) - Math.min(...p.slice(0, 3))) / Math.max(...p.slice(0, 3)) > 0.15; };
  out[`pasar di permukiman bertanah terinjak: ${worn.length}, masih hijau ${worn.filter(isGreen).length}`] = worn.length > 0 && worn.filter(isGreen).length === 0;
  // 16e: taman distrik, sekolah, rumah sakit
  out[`taman distrik ${site('taman').length}, sekolah ${site('sekolah').length}, rumah sakit ${site('rs').length}`] = site('taman').length === 14 && site('sekolah').length === 9 && site('rs').length === 2;
  // 16f: peta: penanda baru, ikon fasilitas, legenda distrik
  S.setLang('id'); S.toggleMap(); await wait(400);
  const leg = document.getElementById('mapLegend') || document.querySelector('.mapLegend, #map .legend');
  const legText = leg ? leg.textContent : '';
  const nFac = S.MAPV.fac ? S.MAPV.fac.length : 0;
  S.mapZoomAt(2); await wait(300);
  const nFac2 = S.MAPV.fac ? S.MAPV.fac.length : 0; S.toggleMap();
  out[`peta: penanda ${S.MAP_MARKS.length}, ikon fasilitas ${nFac2}, legenda memuat distrik dan fasilitas`] = S.MAP_MARKS.length === 14 && nFac2 > 60 && /Kepler/.test(legText) && /Pasar/.test(legText);
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
