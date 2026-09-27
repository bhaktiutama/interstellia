"""Uji tahap 12a (Copper Corn Station): pintu terminal bisa dilewati, gerbang B1 membawa ke kokpit, sandar otomatis selesai.
Pakai: python tools/uji_spaceport.py   (butuh: pip install playwright && playwright install chromium)
Fisika dijalankan langsung lewat window.__station.physicsStep, jadi hasil tidak bergantung FPS (SwiftShader lambat)."""
import asyncio, json, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(() => {
  const st = window.__station, P = st.player, R = st.R, T = st.TERM, PORT = st.PORT, out = {};
  const walk = (pts) => {                                    // jalan lurus per 0,1 m dengan kolisi pemain (radius 0,35 m)
    P.state = 'ground'; P.theta = pts[0][0] / R; P.za = pts[0][1];
    for (let k = 1; k < pts.length; k++) {
      const [s1, z1] = pts[k];
      for (let i = 0; i < 3000; i++) {
        const s = P.theta * R, z = P.za, dx = s1 - s, dz = z1 - z, L = Math.hypot(dx, dz);
        if (L < 0.05) break;
        const d = Math.min(0.1, L); P.theta = (s + dx / L * d) / R; P.za = z + dz / L * d; st.collide(0.35);
      }
      if (Math.hypot(P.theta * R - s1, P.za - z1) > 0.2) return false;
    }
    return true;
  };
  const S = T.s, Z = T.za;
  for (const x of [-5.5, 0, 5.5]) out['pintu selatan x=' + x] = walk([[S + x, Z + 45], [S + x, Z + 20]]);
  for (const z of [-4.5, 0, 4.5]) out['pintu barat z=' + z] = walk([[S - 75, Z + z], [S - 45, Z + z]]);
  out['selatan ke gerbang B1'] = walk([[S, Z + 45], [S, Z + 20], [S + 2, Z + 10], [S + 2, Z - 10], [S, Z - 29.5]]);
  out['kaca utara tertutup'] = !walk([[S, Z - 29.5], [S, Z - 40]]);
  walk([[S, Z - 20], [S, Z - 29.5]]);
  const a = st.availableAction(); out['aksi gerbang ada'] = !!a && a.key === 'gate';
  st.doAction();
  const seq = [P.state];
  for (let i = 0; i < 200 / st.STEP && P.state !== 'ship'; i++) { st.physicsStep(st.STEP); if (seq[seq.length - 1] !== P.state) seq.push(P.state); }
  out['urutan ' + seq.join(' > ')] = seq.join('>') === 'lift>pod>ship';
  st.portAction(); for (let i = 0; i < 6 / st.STEP; i++) st.physicsStep(st.STEP);
  out['lepas sandar'] = PORT.mode === 'fly';
  PORT.v.set(0, 0, -25); for (let i = 0; i < 8 / st.STEP; i++) st.physicsStep(st.STEP); PORT.v.set(0, 0, 0);
  st.portAction(); for (let i = 0; i < 60 / st.STEP && PORT.mode !== 'docked'; i++) st.physicsStep(st.STEP);
  out['sandar otomatis'] = PORT.mode === 'docked';
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
        hasil = await pg.evaluate(UJI)
        for k, v in hasil.items(): print(('OK   ' if v else 'GAGAL'), k)
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())
