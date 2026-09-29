"""Uji 21c (Copper Corn Station): menara kaca malam dari jauh tidak lagi terang rata. Menara kaca (gaya 1) tertinggi
dirender sendirian ke target float dari 800 m: siang untuk topeng muka gedung, malam 23.00 untuk pola lampu.
Ukuran: sebaran terang sepanjang baris (blok kantor menyala / gelap) dan antarbaris (lantai), rata-rata terang,
tanpa nilai tidak valid; faktor jam kantor / hunian; siang tidak dipengaruhi faktor jam.
Pakai: python tools/uji_gedung_malam.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(async () => {
  const S = window.__station, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const THREE = await import('https://cdn.jsdelivr.net/npm/three@0.186.1/build/three.module.js');
  const L = S.BUILD.flat; let idx = -1; L.forEach((q, i) => { if (q[7] === 1 && (idx < 0 || q[4] > L[idx][4])) idx = i; }); const g = L[idx];
  out[`menara kaca tertinggi ${g[4].toFixed(0)} m (lebar ${g[2].toFixed(0)} x ${g[3].toFixed(0)} m)`] = g[7] === 1 && g[4] > 100;
  const src = S.cityMeshes.flat, geo1 = src.geometry.clone(), m1 = new THREE.Matrix4();
  geo1.setAttribute('aStyle', new THREE.InstancedBufferAttribute(new Float32Array([g[7], g[8]]), 2));
  const one = new THREE.InstancedMesh(geo1, src.material, 1); src.getMatrixAt(idx, m1); one.setMatrixAt(0, m1);
  if (src.instanceColor) { const c = new THREE.Color(); src.getColorAt(idx, c); one.setColorAt(0, c); }
  one.frustumCulled = false;
  geo1.computeBoundingBox(); const ctr = geo1.boundingBox.getCenter(new THREE.Vector3()).applyMatrix4(m1);
  const out3 = new THREE.Vector3(0, 0, -1).transformDirection(m1), up = new THREE.Vector3(0, 1, 0).transformDirection(m1);
  const W = 400, H = 400, rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.FloatType });
  const cam = new THREE.PerspectiveCamera(20, 1, 1, 5000); cam.up.copy(up); cam.position.copy(ctr).addScaledVector(out3, 800); cam.lookAt(ctr); cam.updateMatrixWorld();
  const sc = new THREE.Scene(); sc.add(one); sc.background = new THREE.Color(0, 0, 0);
  const shoot = () => {
    S.renderer.setRenderTarget(rt); S.renderer.clear(); S.renderer.render(sc, cam); S.renderer.setRenderTarget(null);
    const px = new Float32Array(W * H * 4); S.renderer.readRenderTargetPixels(rt, 0, 0, W, H, px); return px;
  };
  const lum = (p, i) => 0.2126 * p[i] + 0.7152 * p[i + 1] + 0.0722 * p[i + 2];
  S.teleport('nyc'); S.clock.hour = 11; await wait(2500);
  const day = shoot(), mask = new Uint8Array(W * H);
  for (let i = 0; i < W * H; i++) mask[i] = day[i * 4] + day[i * 4 + 1] + day[i * 4 + 2] > 1e-4 ? 1 : 0;
  S.BUILD_U.uLitT.value.set(0.1, 0.1); const day2 = shoot(); S.BUILD_U.uLitT.value.set(1, 1); const day3 = shoot();
  let dd = 0; for (let i = 0; i < day2.length; i++) if (day2[i] !== day3[i]) dd++;
  out[`siang: faktor jam tidak mengubah gambar (${dd} nilai beda)`] = dd === 0;
  const lt = {}; for (const h of [20, 3]) { S.clock.hour = h; S.updateLighting(); lt[h] = S.BUILD_U.uLitT.value.toArray().map((v) => +v.toFixed(2)); }
  out[`faktor jam kantor/hunian: 20.00 ${lt[20].join('/')}, 03.00 ${lt[3].join('/')}`] = lt[20][0] > 0.9 && lt[20][1] > 0.9 && lt[3][0] < 0.35 && lt[3][1] < 0.35;
  S.clock.hour = 23; S.updateLighting(); await wait(2500);
  const nt = shoot(); let bad = 0, n = 0, sum = 0;
  const rowCV = [], rowMean = [];
  for (let y = 0; y < H; y++) {
    let c = 0, s1 = 0, s2 = 0;
    for (let x = 0; x < W; x++) {
      const i = y * W + x; if (!mask[i]) continue;
      for (let k = 0; k < 3; k++) if (!Number.isFinite(nt[i * 4 + k]) || nt[i * 4 + k] < 0) bad++;
      const v = lum(nt, i * 4); c++; s1 += v; s2 += v * v;
    }
    if (c < 20) continue;
    const m = s1 / c; n += c; sum += s1; rowMean.push(m);
    if (m > 1e-4) rowCV.push(Math.sqrt(Math.max(0, s2 / c - m * m)) / m);
  }
  const avg = (a) => a.reduce((x, y) => x + y, 0) / Math.max(1, a.length);
  const mAll = sum / Math.max(1, n), cvRow = avg(rowCV);
  const mm = avg(rowMean), cvCol = Math.sqrt(avg(rowMean.map((v) => (v - mm) * (v - mm)))) / Math.max(1e-6, mm);
  out[`malam 23.00 dari 800 m: ${n} piksel muka gedung, tanpa nilai tidak valid (${bad})`] = n > 3000 && bad === 0;
  out[`sebaran terang sepanjang baris ${cvRow.toFixed(2)} (blok menyala/gelap; lama 0,05; batas > 0,25)`] = cvRow > 0.25;
  out[`sebaran terang antarbaris ${cvCol.toFixed(2)} (lantai), terang rata-rata ${mAll.toFixed(3)}`] = cvCol > 0.3 && mAll > 0.01;
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
