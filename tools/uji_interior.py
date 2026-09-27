"""Uji 14c (Copper Corn Station): ruangan maya di balik jendela (interior mapping). Shader bangunan terkompilasi,
uInterior per preset (Ultra/Tinggi/Sedang nyala, Rendah/Hemat mati), render gedung saja (target float 1280 x 800) di depan
gedung kota dekat: ruangan terlihat berbeda dari kaca lama, hasil deterministik, tanpa nilai tidak valid (NaN, negatif) siang dan malam.
Pakai: python tools/uji_interior.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(async () => {
  const S = window.__station, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const THREE = await import('https://cdn.jsdelivr.net/npm/three@0.186.1/build/three.module.js');
  const on = [0, 1, 2, 3, 4].map((i) => { S.applyPreset(i); return S.BUILD_U.uInterior.value; });
  S.applyPreset(0);
  out[`uInterior per preset Ultra..Hemat: ${on.join(' ')}`] = on.join('') === '11100';
  const W = 1280, H = 800, rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.FloatType });
  const shoot = () => {                                     // gedung saja, tanpa post; mesh dipinjam lalu dikembalikan
    const sc = new THREE.Scene(), ms = Object.values(S.cityMeshes), par = ms.map((m) => m.parent);
    ms.forEach((m) => sc.add(m)); sc.fog = S.scene.fog; sc.rotation.copy(S.scene.rotation); sc.background = new THREE.Color(0, 0, 0);
    const cam = S.camera.clone(); cam.aspect = W / H; cam.updateProjectionMatrix();
    S.renderer.setRenderTarget(rt); S.renderer.clear(); S.renderer.render(sc, cam); S.renderer.setRenderTarget(null);
    ms.forEach((m, i) => par[i].add(m));
    const px = new Float32Array(W * H * 4); S.renderer.readRenderTargetPixels(rt, 0, 0, W, H, px); return px;
  };
  const types = Object.keys(S.BUILD).sort((x, y) => S.BUILD[y].length - S.BUILD[x].length);
  const g = S.BUILD[types[0]].find((q) => q[4] > 15 && q[1] > 300);
  for (const [nm, hr] of [['siang', 11], ['malam', 21]]) {
    S.clock.hour = hr; S.teleport('cooper');
    const za = g[1] - g[3] / 2 - 14;
    Object.assign(S.player, { theta: g[0] / S.R, za, h: S.groundH(g[0], za), heading: Math.PI, pitch: 0.3 });
    await wait(3000);
    S.BUILD_U.uInterior.value = 1; const a = shoot(), a2 = shoot();
    S.BUILD_U.uInterior.value = 0; const b = shoot(); S.BUILD_U.uInterior.value = 1;
    let bad = 0, chg = 0, same = 0, bld = 0;
    for (let i = 0; i < a.length; i += 4) {
      for (let c = 0; c < 3; c++) if (!Number.isFinite(a[i + c]) || a[i + c] < 0) bad++;
      if (a[i] + a[i + 1] + a[i + 2] > 0) bld++;
      if (Math.abs(a[i] - b[i]) + Math.abs(a[i + 1] - b[i + 1]) + Math.abs(a[i + 2] - b[i + 2]) > 0.02) chg++;
      if (a[i] !== a2[i] || a[i + 1] !== a2[i + 1] || a[i + 2] !== a2[i + 2]) same++;
    }
    const n = W * H;
    out[`${nm}: gedung ${(bld / n * 100).toFixed(1)}% layar, berubah oleh ruangan ${(chg / n * 100).toFixed(2)}% layar`] = bld / n > 0.05 && chg / n > 0.005;
    out[`${nm}: tanpa nilai tidak valid (${bad}), deterministik (${same} piksel beda)`] = bad === 0 && same === 0;
  }
  rt.dispose();
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
