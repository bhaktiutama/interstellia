"""Uji 15d (Copper Corn Station): permukiman padat bertingkat. Jumlah rumah per bentuk, tanah kosong di sel permukiman
(titik sampel yang jauh dari rumah), rumah tidak bertumpuk, tidak di trotoar atau jalan, gang ada, masjid (15e) menggantikan setengah gereja, biaya segitiga dicatat.
Pakai: python tools/uji_permukiman.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(async () => {
  const S = window.__station, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const CIRC = 2 * Math.PI * S.R, wrapS = (x) => { x = ((x % CIRC) + CIRC) % CIRC; return x > CIRC / 2 ? x - CIRC : x; };
  const city = S.houseList.filter(([s, za, w, d, h, t]) => za > 230 && za < 2560 && !(t === 'hip' && h > 20));   // menara gereja memang menempel badan gereja
  const res = city.filter(([, , w, d, h, t]) => t !== 'flat' || (w < 7 && d < 9));
  out[`rumah di kota ${city.length} (permukiman ${res.length}), gang ${S.GANGS.length}, pohon halaman ${S.YARD_TREES.length}`] = res.length > 9000 && S.GANGS.length > 300;
  // grid rumah untuk cari tetangga
  const G = new Map(), key = (s, z) => `${Math.floor(((s % CIRC) + CIRC) % CIRC / 40)}|${Math.floor(z / 40)}`;
  city.forEach((b, i) => { const k = key(b[0], b[1]); (G.get(k) || G.set(k, []).get(k)).push(i); });
  const near = (s, z) => { const a = []; for (let i = -1; i <= 1; i++) for (let j = -1; j <= 1; j++) { const k = `${(Math.floor(((s % CIRC) + CIRC) % CIRC / 40) + i + 158) % 158}|${Math.floor(z / 40) + j}`; for (const q of G.get(k) || []) a.push(q); } return a; };
  let over = 0; const ov = [];
  const isRes = new Set(res);
  city.forEach((A, i) => { if (!isRes.has(A)) return; const [s, za, w, d] = A; for (const j of near(s, za)) if (j > i) { const b = city[j]; if (!isRes.has(b)) continue; const ox = (w + b[2]) / 2 - Math.abs(wrapS(s - b[0])), oz = (d + b[3]) / 2 - Math.abs(za - b[1]); if (ox > 0.3 && oz > 0.3) { over++; if (ov.length < 3) ov.push([+s.toFixed(0), +za.toFixed(0)]); } } });
  out[`rumah permukiman bertumpuk: ${over}` + (ov.length ? ` ${JSON.stringify(ov)}` : '')] = over === 0;
  let onSw = 0; const sw = [];
  for (const [s, za, w, d] of res) for (const [x, z] of [[-1, -1], [1, -1], [-1, 1], [1, 1], [0, 0]]) if (S.SIDEWALK.d(s + x * w / 2, za + z * d / 2) >= 0.2) { onSw++; if (sw.length < 3) sw.push([+s.toFixed(0), +za.toFixed(0)]); break; }
  out[`rumah di trotoar: ${onSw}` + (sw.length ? ` ${JSON.stringify(sw)}` : '')] = onSw === 0;
  // tanah kosong: titik sampel tiap 10 m di sel permukiman/tepi yang bukan jalan, trotoar, air, atau lapangan; jarak ke rumah terdekat
  let pts = 0, far = 0;
  for (const c of S.cityCells) {
    if (c.cls !== 'permukiman' && c.cls !== 'tepi') continue;
    for (let s = c.s0 + 20; s < c.s0 + S.ART - 20; s += 10) for (let za = c.z0 + 20; za < c.z0 + 230; za += 10) {
      if (S.inWater(s, za, 3) || S.inRiver(s, za, 3) || S.SIDEWALK.d(s, za) >= 0) continue;
      pts++;
      let best = 1e9; for (const j of near(s, za)) { const b = city[j]; best = Math.min(best, Math.max(0, Math.abs(wrapS(s - b[0])) - b[2] / 2, Math.abs(za - b[1]) - b[3] / 2)); }
      if (best > 25) far++;
    }
  }
  out[`sel permukiman: titik lebih dari 25 m dari rumah ${(far / pts * 100).toFixed(1)}% dari ${pts}`] = far / pts < 0.2;
  // 15e: masjid menggantikan setengah gereja, tiga gaya, normal geometri sah (tanpa NaN atau nol)
  const M = S.MOSQUE, churches = S.BUILD.gablez.filter((b) => b[6] === '#e9e4da').length, kinds = new Set(M.list.map((q) => q[2]));
  out[`masjid ${M.list.length} (gaya ${[...kinds].map((k) => M.names[k]).join(', ')}), gereja ${churches}`] = M.list.length >= 3 && kinds.size === 3 && Math.abs(M.list.length - churches) <= 2;
  const N = M.mesh.geometry.attributes.normal.array; let badN = 0;
  for (let i = 0; i < N.length; i += 3) { const l = Math.hypot(N[i], N[i + 1], N[i + 2]); if (!Number.isFinite(l) || l < 0.5) badN++; }
  out[`kubah dan menara: ${N.length / 9} segitiga, normal tidak sah ${badN}`] = badN === 0;
  const cost = () => { const i = S.renderer.info.render; return `${Math.round(i.triangles / 1000)} rb segitiga`; };
  S.clock.hour = 11; S.applyPreset(0); S.teleport('cooper'); await wait(3000); const u = cost();
  S.applyPreset(4); await wait(3000); const h = cost(); S.applyPreset(0);
  out[`biaya titik awal kota: Ultra ${u}, Hemat ${h}`] = true;
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
