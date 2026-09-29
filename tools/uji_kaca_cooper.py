"""Uji 21b (Copper Corn Station): kaca jendela rumah Cooper. Kaca = satu bidang per jendela (normal menghadap keluar).
Panel kaca dirender sendirian ke target float di atas latar hitam lalu putih: dari selisihnya didapat alpha (seberapa pekat)
dan cahaya yang ditambahkan kaca (pantulan). Dari dalam rumah: alpha kecil (luar terlihat jelas), paling tinggi 0,35 walau
dilihat miring, pantulan redup (ruangan). Dari luar: pantulan daratan seberang tetap ada dan lebih terang daripada dari dalam.
Tanpa nilai tidak valid siang dan malam.
Pakai: python tools/uji_kaca_cooper.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(async () => {
  const S = window.__station, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const THREE = await import('https://cdn.jsdelivr.net/npm/three@0.186.1/build/three.module.js');
  const glass = []; S.COOPER_HOUSE.traverse((o) => { if (o.isMesh && o.material.userData.spec && o.material.userData.spec.glass === 2) glass.push(o); });
  const G = glass[0], pos = G.geometry.attributes.position, nrm = G.geometry.attributes.normal;
  out[`kaca jendela: ${glass.length} mesh, ${pos.count / 6} bidang (6 verteks per bidang)`] = glass.length === 1 && pos.count === 22 * 6;
  S.COOPER_HOUSE.updateMatrixWorld(true);
  const M = S.COOPER_HOUSE.matrixWorld, c = new THREE.Vector3();
  for (let i = 0; i < 6; i++) c.add(new THREE.Vector3().fromBufferAttribute(pos, i));
  c.multiplyScalar(1 / 6).applyMatrix4(M);                                    // pusat panel pertama (depan lantai 1)
  const n = new THREE.Vector3().fromBufferAttribute(nrm, 0).transformDirection(M);   // normal keluar
  const up = new THREE.Vector3(0, 1, 0).transformDirection(M), side = new THREE.Vector3().crossVectors(up, n).normalize();
  const W = 160, H = 160, rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.FloatType });
  const one = new THREE.Mesh(G.geometry, G.material); one.matrixAutoUpdate = false; one.matrix.copy(M); one.frustumCulled = false;
  const sc = new THREE.Scene(); sc.add(one);
  const cam = new THREE.PerspectiveCamera(20, 1, 0.05, 100); cam.up.copy(up);
  const shoot = (bg) => {
    sc.background = new THREE.Color(bg, bg, bg);
    S.renderer.setRenderTarget(rt); S.renderer.clear(); S.renderer.render(sc, cam); S.renderer.setRenderTarget(null);
    const px = new Float32Array(W * H * 4); S.renderer.readRenderTargetPixels(rt, 0, 0, W, H, px); return px;
  };
  const pct = (a, q) => { if (!a.length) return NaN; const b = [...a].sort((x, y) => x - y); return b[Math.floor((b.length - 1) * q)]; }, med = (a) => pct(a, 0.5);
  const view = (from) => {                                                    // alpha dan cahaya tambahan per piksel kaca (tanpa kisi putih)
    cam.position.copy(from); cam.lookAt(c); cam.updateMatrixWorld(); cam.updateProjectionMatrix();
    const B = shoot(0), Wt = shoot(1), al = [], add = []; let bad = 0, kisi = 0;
    for (let i = 0; i < B.length; i += 4) {
      for (let k = 0; k < 3; k++) if (!Number.isFinite(B[i + k]) || !Number.isFinite(Wt[i + k])) bad++;
      const a = 1 - ((Wt[i] - B[i]) + (Wt[i + 1] - B[i + 1]) + (Wt[i + 2] - B[i + 2])) / 3;
      if (a < 1e-4 && B[i] + B[i + 1] + B[i + 2] < 1e-5) continue;            // bukan piksel kaca
      if (a > 0.9) { kisi++; continue; }                                      // kisi putih pejal
      al.push(a); add.push((B[i] + B[i + 1] + B[i + 2]) / 3);
    }
    return { n: al.length, kisi, bad, aMed: med(al), a80: pct(al, 0.8), addMed: med(add) };   // p80: tepi kisi (tercampur filter tekstur) tidak ikut
  };
  // ukur kaca saja: isi tekstur diganti sementara tanpa kisi putih (objek tekstur sama, shader tidak dikompilasi ulang)
  const tx = G.material.map, cv = tx.image, g2 = cv.getContext('2d'), keep = g2.getImageData(0, 0, cv.width, cv.height);
  g2.clearRect(0, 0, cv.width, cv.height); g2.fillStyle = 'rgba(150,176,172,0.04)'; g2.fillRect(0, 0, cv.width, cv.height); tx.needsUpdate = true;
  const R = {};
  for (const [nm, hr] of [['siang', 11], ['malam', 22]]) {
    S.clock.hour = hr; S.teleport('cooper'); await wait(2500);
    R[nm] = {
      dalam: view(c.clone().addScaledVector(n, -3)),                                            // dari dalam, tegak lurus
      miring: view(c.clone().addScaledVector(n, -0.4).addScaledVector(side, 4.5)),             // dari dalam, sekitar 85 derajat
      luar: view(c.clone().addScaledVector(n, 3)),                                              // dari luar, tegak lurus
      luarMiring: view(c.clone().addScaledVector(n, 0.4).addScaledVector(side, 4.5)),          // dari luar, sekitar 85 derajat
    };
  }
  g2.putImageData(keep, 0, 0); tx.needsUpdate = true;
  const f = (x) => x.toFixed(3);
  for (const nm of ['siang', 'malam']) {
    const r = R[nm], bad = r.dalam.bad + r.miring.bad + r.luar.bad + r.luarMiring.bad;
    out[`${nm}: tanpa nilai tidak valid (${bad}), piksel kaca dalam/miring/luar/luar miring ${r.dalam.n}/${r.miring.n}/${r.luar.n}/${r.luarMiring.n}`] =
      bad === 0 && r.dalam.n > 500 && r.miring.n > 300 && r.luar.n > 500 && r.luarMiring.n > 300;
    out[`${nm} dari dalam: alpha tegak lurus ${f(r.dalam.aMed)}, miring 85 derajat ${f(r.miring.a80)} (batas 0,35)`] = r.dalam.aMed < 0.1 && r.miring.a80 <= 0.3501;
    out[`${nm} dari luar: alpha tegak lurus ${f(r.luar.aMed)}, miring 85 derajat ${f(r.luarMiring.a80)} (pantulan daratan tetap)`] = r.luar.aMed < 0.1 && r.luarMiring.a80 > 0.5;
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
