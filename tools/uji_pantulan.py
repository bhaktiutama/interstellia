"""Uji 17b + 17d (Copper Corn Station): pantulan daratan seberang dan kilap material.
farEnv() dirender untuk banyak arah pantul dari tanah (siang dan malam, tiga tingkat kekasaran): tanpa nilai tidak valid,
arah ke atas memantulkan daratan (hijau lebih kuat dari biru), arah sepanjang sumbu ke end cap jauh berkabut (biru),
arah tepat ke sumbu memantulkan sunline. Ambient siang ikut warna daratan. Material bertanda specMat() terkompilasi,
trem dengan kilap berbeda dari tanpa kilap, tanpa nilai tidak valid.
Pakai: python tools/uji_pantulan.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(async () => {
  const S = window.__station, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const THREE = await import('https://cdn.jsdelivr.net/npm/three@0.186.1/build/three.module.js');
  const U = S.LIGHT.uniforms, W = 72, H = 36;
  // piksel = arah: x = azimut di bidang singgung tanah (0 = +z, ke end cap B), y = elevasi 0..90 derajat (atas = ke sumbu)
  const mat = new THREE.ShaderMaterial({
    uniforms: Object.assign({ uRough: { value: 0 }, uP: { value: new THREE.Vector3(0, -998, 3300) } }, U),
    vertexShader: 'void main() { gl_Position = vec4(position.xy, 0.0, 1.0); }',
    fragmentShader: S.LIGHT_GLSL + `
      uniform float uRough; uniform vec3 uP;
      void main() {
        vec2 f = gl_FragCoord.xy / vec2(${W}.0, ${H}.0);
        float az = f.x * 6.2831853, el = f.y * 1.5707963;
        vec3 up = vec3(0.0, 1.0, 0.0), tz = vec3(0.0, 0.0, 1.0), tx = vec3(1.0, 0.0, 0.0);
        vec3 d = normalize(up * sin(el) + (tz * cos(az) + tx * sin(az)) * cos(el));
        gl_FragColor = vec4(farEnv(uP, d, uRough, 1.0), 1.0);
      }`,
  });
  const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), mat), sc = new THREE.Scene(); sc.add(quad); quad.frustumCulled = false;
  const cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1), rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.FloatType });
  const shoot = () => { S.renderer.setRenderTarget(rt); S.renderer.render(sc, cam); S.renderer.setRenderTarget(null);
    const px = new Float32Array(W * H * 4); S.renderer.readRenderTargetPixels(rt, 0, 0, W, H, px); return px; };
  const at = (px, x, y) => { const i = (y * W + x) * 4; return [px[i], px[i + 1], px[i + 2]]; };
  let bad = 0;
  for (const hr of [13, 23]) {
    S.clock.hour = hr; S.updateLighting();
    for (const r of [0, 0.5, 1]) {
      mat.uniforms.uRough.value = r; const px = shoot();
      for (let i = 0; i < px.length; i += 4) for (let c = 0; c < 3; c++) if (!Number.isFinite(px[i + c]) || px[i + c] < 0) bad++;
      if (hr === 13 && r === 0.5) {
        let g = 0, b = 0, n = 0;                                    // arah miring ke atas (elevasi 40-75 derajat), azimut ke samping
        for (let y = Math.round(H * 40 / 90); y < Math.round(H * 75 / 90); y++) for (const x of [Math.round(W / 4), Math.round(W * 3 / 4)]) { const c = at(px, x, y); g += c[1]; b += c[2]; n++; }
        out[`siang, pantulan miring ke atas = daratan seberang: hijau ${(g / n).toFixed(3)} > biru ${(b / n).toFixed(3)}`] = g > b;
        const cap = at(px, Math.round(W / 2), 0);                    // mendatar ke -z: 7,3 km udara ke end cap A
        out[`siang, mendatar ke end cap A jauh = kabut: biru ${cap[2].toFixed(3)} > hijau ${cap[1].toFixed(3)}`] = cap[2] > cap[1];
      }
      if (hr === 13 && r === 0) {
        const top = at(px, 0, H - 1), side = at(px, Math.round(W / 4), Math.round(H * 0.6));
        out[`siang, tepat ke sumbu = sunline: ${top[1].toFixed(2)} > miring ${side[1].toFixed(2)}`] = top[1] > side[1] * 1.5;
      }
    }
  }
  out[`farEnv siang dan malam, kekasaran 0 / 0,5 / 1: tanpa nilai tidak valid (${bad})`] = bad === 0;
  // ambient siang mengikuti warna daratan
  S.clock.hour = 13; S.updateLighting();
  const a = U.uL_AmbCol.value, L = S.FAR.land;
  out[`rata-rata daratan (${L.map((x) => x.toFixed(3)).join(', ')}); ambient siang (${a.x.toFixed(3)}, ${a.y.toFixed(3)}, ${a.z.toFixed(3)}): biru < hijau`] = a.z < a.y;
  // material berkilap: terkompilasi dan berpengaruh
  const specs = []; S.scene.traverse((o) => { if (o.material && o.material.userData && o.material.userData.specU) specs.push(o.material); });
  const uniq = [...new Set(specs)];
  out[`material berkilap terkompilasi: ${uniq.length}`] = uniq.length >= 8;
  const tm = S.tramMesh, tmats = []; tm.traverse((o) => { if (o.material && o.material.userData && o.material.userData.specU) tmats.push(o.material); });
  const W2 = 320, H2 = 200, rt2 = new THREE.WebGLRenderTarget(W2, H2, { type: THREE.FloatType });
  const shootTram = () => {
    const sc2 = new THREE.Scene(), par = tm.parent; sc2.add(tm); sc2.rotation.copy(S.scene.rotation); tm.updateMatrixWorld(true);
    const c2 = new THREE.PerspectiveCamera(60, W2 / H2, 0.1, 200), M = tm.matrixWorld;
    c2.position.set(7, 1.8, 3).applyMatrix4(M); c2.up.set(0, 1, 0).transformDirection(M); c2.lookAt(new THREE.Vector3(0, 1.6, 0).applyMatrix4(M)); c2.updateMatrixWorld(true);
    S.renderer.setRenderTarget(rt2); S.renderer.setClearColor(0x000000, 1); S.renderer.clear(); S.renderer.render(sc2, c2); S.renderer.setRenderTarget(null); par.add(tm);
    const px = new Float32Array(W2 * H2 * 4); S.renderer.readRenderTargetPixels(rt2, 0, 0, W2, H2, px);
    let sum = 0, nb = 0; for (let i = 0; i < px.length; i += 4) { for (let c = 0; c < 3; c++) if (!Number.isFinite(px[i + c]) || px[i + c] < 0) nb++; sum += px[i] + px[i + 1] + px[i + 2]; }
    return { mean: sum / (W2 * H2 * 3), bad: nb, px };
  };
  const on = shootTram(), keep = tmats.map((m) => m.userData.specU.value.clone());
  tmats.forEach((m) => m.userData.specU.value.set(1, 0, 0));        // kekasaran 1, F0 0, bukan logam: kilap praktis nol
  const off = shootTram(); tmats.forEach((m, i) => m.userData.specU.value.copy(keep[i]));
  let dmax = 0, nd = 0; for (let i = 0; i < on.px.length; i += 4) { const d = Math.abs(on.px[i + 1] - off.px[i + 1]); dmax = Math.max(dmax, d); if (d > 0.01) nd++; }
  const tu = new Set(tmats).size;
  out[`trem: ${tu} material berkilap, selisih piksel terbesar ${dmax.toFixed(3)}, ${nd} piksel berubah > 0,01 (rata-rata ${on.mean.toFixed(4)} / ${off.mean.toFixed(4)})`] = tu >= 3 && dmax > 0.02 && nd > 50;
  out[`render trem: tanpa nilai tidak valid (${on.bad + off.bad})`] = on.bad + off.bad === 0;
  rt.dispose(); rt2.dispose(); S.clock.hour = 12;
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
