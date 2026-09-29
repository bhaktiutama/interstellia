"""Uji 21a-1 (Copper Corn Station): orang, pohon, dan merpati tidak berada di dalam kolam air mancur Coriolis.
Pengunjung air mancur datang, berdiri atau duduk di bibir kolam, lalu pergi (30 menit simulasi); kelompok mengobrol di plaza
bubar dan berkumpul lagi di tempat lain; jalur lurus pengunjung tidak menembus pohon; angka Coriolis tetap.
Pakai: python tools/uji_air_mancur.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(() => {
  const st = window.__station, F = st.FOUNT, V = st.VIS, out = {}, g = 9.81, om = st.OMEGA;
  const d = (s, za) => st.fountDist(s, za);
  out[`geser Coriolis tetap: 10 m/s ${F.shift10.toFixed(3)} m, 6 m/s ${F.shift6.toFixed(3)} m`] =
    Math.abs(F.shift10 - 4 / 3 * om * 1000 / (g * g)) < 1e-3 && Math.abs(F.shift6 - 4 / 3 * om * 216 / (g * g)) < 1e-3;
  const inBasin = (p) => d(p.s, p.za) < V.minR - 1e-3 && !(p.kind === 'visit' && p.pose === 2 && Math.abs(d(p.s, p.za) - V.sitR) < 1e-3);
  const awal = st.PEDS.list.filter(inBasin);
  out[`saat muat: orang di dalam kolam ${awal.length}`] = awal.length === 0;
  const pohon = st.treeList.filter(([s, za]) => d(s, za) < F.clear - 1e-3).length;
  out[`pohon dalam ${F.clear} m dari pusat kolam: ${pohon}`] = pohon === 0;
  const G0 = st.BIRDS.groups.map((G) => d(G.s, G.za)).sort((a, b) => a - b)[0];
  out[`titik merpati terdekat ${G0.toFixed(1)} m dari pusat kolam`] = G0 >= F.clear;

  // 30 menit simulasi pengunjung plaza (semua dianggap dekat pemain: dilangkahkan tiap langkah)
  const vis = st.PEDS.walk.filter((p) => p.kind === 'visit'); for (const p of vis) p.isNear = true;
  const fount = V.fount, groups = V.groups, seen = new Set(), stayT = new Map(), sitters = new Set();
  let maxStay = 0, masuk = 0, nan = 0, tabrak = 0, dt = 0.2, t = st.clock.sim;
  const bubar = new Map(), kumpul = new Map(), prev = new Map(groups.map((G) => [G, G.st]));
  const COL = st.COL;
  for (let k = 0; k < 9000; k++) {
    t += dt; st.stepPeds(dt, t);
    for (const p of vis) {
      if (!isFinite(p.s) || !isFinite(p.za) || !isFinite(p.hd)) nan++;
      if (inBasin(p)) masuk++;
      if ((p.st === 'in' || p.st === 'out' || p.st === 'stay') && d(p.s, p.za) > 7.5 && st.colAt(p.s, p.za, 0)) tabrak++;
    }
    for (const p of fount) {
      if (p.st === 'stay') { seen.add(p); if (p.pose === 2) sitters.add(p); stayT.set(p, (stayT.get(p) || 0) + dt); maxStay = Math.max(maxStay, stayT.get(p)); }
      else stayT.set(p, 0);
    }
    for (const G of groups) {
      const a = prev.get(G);
      if (a !== 'apart' && G.st === 'apart') bubar.set(G, (bubar.get(G) || 0) + 1);
      if (a === 'gather' && G.st === 'talk') kumpul.set(G, (kumpul.get(G) || 0) + 1);
      prev.set(G, G.st);
    }
  }
  const kunj = fount.reduce((a, p) => a + (seen.has(p) ? 1 : 0), 0);
  out[`pengunjung air mancur ${fount.length}, pernah di tepi kolam ${kunj}, duduk ${sitters.size}`] = fount.length === 8 && kunj >= 6 && sitters.size >= 1;
  out[`lama di tepi kolam paling lama ${maxStay.toFixed(0)} s (batas 120 s)`] = maxStay > 15 && maxStay <= 120;
  out[`30 menit: posisi di dalam kolam ${masuk}, nilai tidak valid ${nan}`] = masuk === 0 && nan === 0;
  out[`30 menit: titik jalur lurus di dalam pohon/benda ${tabrak}`] = tabrak === 0;
  const nb = groups.filter((G) => bubar.get(G)).length, nk = groups.filter((G) => kumpul.get(G)).length;
  out[`kelompok mengobrol ${groups.length}: bubar ${nb}, berkumpul lagi ${nk}`] = groups.length > 10 && nb === groups.length && nk >= groups.length * 0.9;
  const dekat = groups.map((G) => d(G.c[0], G.c[1])).sort((a, b) => a - b)[0];
  out[`pusat kelompok terdekat ${dekat.toFixed(1)} m dari pusat kolam`] = dekat >= 8.5 - 1e-3;

  // merpati: jalan-jalan, lalu dikejutkan pemain, lalu hinggap lagi: tidak ada yang di dalam kolam
  st.clock.hour = 10; const P = st.player, GF = st.BIRDS.groups.reduce((a, G) => (d(G.s, G.za) < d(a.s, a.za) ? G : a));
  P.state = 'ground'; P.theta = F.s / st.R; P.za = F.za + 22;
  let burungMasuk = 0;
  const cek = () => { for (const b of GF.birds) if (b.h <= 0.01 && d(b.s, b.za) < 5.2 - 1e-3) burungMasuk++; };
  for (let k = 0; k < 600; k++) { st.clock.sim += 0.1; st.stepBirds(0.1); cek(); }
  P.theta = GF.birds[0].s / st.R; P.za = GF.birds[0].za + 1; for (let k = 0; k < 3; k++) { st.clock.sim += 0.1; st.stepBirds(0.1); }
  const terbang = GF.birds.filter((b) => b.fly).length;
  P.za = F.za + 60; for (let k = 0; k < 300; k++) { st.clock.sim += 0.1; st.stepBirds(0.1); cek(); }
  out[`merpati plaza air mancur: terbang ${terbang}/${GF.birds.length}, hinggap lagi ${GF.birds.filter((b) => !b.fly).length}, di dalam kolam ${burungMasuk}`] =
    terbang === GF.birds.length && burungMasuk === 0;
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
