"""Uji 17a (Copper Corn Station): orbit dan gerhana Saturnus. Matahari 25 derajat dari sumbu dan tepat di bidang orbit,
lompat ke gerhana (tombol I) tiba 2 menit sebelum mulai, lama gerhana sekitar 2,8 jam per orbit, penumbra singkat,
sinar lewat end cap dan silau Matahari padam saat gerhana, cahaya tepi atmosfer Saturnus terlihat, tanpa nilai tidak valid.
Pakai: python tools/uji_gerhana.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(async () => {
  const S = window.__station, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const THREE = await import('https://cdn.jsdelivr.net/npm/three@0.186.1/build/three.module.js');
  const DEG = Math.PI / 180, TAU = 2 * Math.PI, sd = S.SUN_DIR, E = S.ECL;
  const ax = Math.acos(sd.z) / DEG;
  const n = new THREE.Vector3(0, 0, 1).applyAxisAngle(new THREE.Vector3(1, 0, 0), S.ORBIT.axisTiltDeg * DEG);
  out[`Matahari ${ax.toFixed(2)} derajat dari sumbu (target 25), jarak dari bidang orbit ${(Math.asin(Math.abs(sd.dot(n))) / DEG).toFixed(3)} derajat`] = Math.abs(ax - 25) < 0.01 && Math.abs(sd.dot(n)) < 1e-6;
  const setPhase = (phi) => { S.clock.orbit = (phi - S.ORBIT.phi0) / TAU * S.T_ORB; S.updateFar(); };
  // lompat ke gerhana
  S.clock.orbit = 1000; S.updateFar(); S.jumpToEclipse();
  out[`lompat (I): gerhana dimulai dalam ${S.eclipseIn().toFixed(0)} s waktu orbit (target 120), Matahari masih terang (k ${E.k.toFixed(2)})`] = Math.abs(S.eclipseIn() - 120) < 2 && E.k === 1;
  // lama gerhana dan penumbra: pindai satu orbit
  let dark = 0, pen = 0;
  for (let tt = 0; tt < S.T_ORB; tt += 5) { S.clock.orbit = tt; S.updateEclipse(); S.updateFar(); if (E.k < 0.5) dark += 5; }
  const t0 = (E.phiC - E.half * 1.05 - S.ORBIT.phi0) / TAU * S.T_ORB;
  for (let tt = t0; tt < t0 + 1200; tt += 0.5) { S.clock.orbit = tt; S.updateFar(); if (E.k > 0.01 && E.k < 0.99) pen += 0.5; }
  out[`lama gerhana ${(dark / 3600).toFixed(2)} jam per orbit ${(S.T_ORB / 3600).toFixed(2)} jam (target 2,5-2,9)`] = dark / 3600 > 2.4 && dark / 3600 < 2.9;
  out[`penumbra saat masuk ${pen.toFixed(1)} s (target 10-60)`] = pen >= 10 && pen <= 60;
  // di tengah gerhana
  setPhase(E.phiC); S.updateLighting();
  const L = S.LIGHT.uniforms;
  out[`tengah gerhana: k ${E.k.toFixed(3)}, sinar end cap ${L.uL_SunI.value.toFixed(3)}, silau ${S.saturn.userData.glareMat.uniforms.uK.value.toFixed(3)}`] = E.k === 0 && L.uL_SunI.value === 0 && S.saturn.userData.glareMat.uniforms.uK.value === 0;
  const hudOk = await (async () => { for (let i = 0; i < 40; i++) { await wait(500); if (/gerhana|eclipse/.test(document.getElementById('hOrb').textContent)) return true; } return false; })();
  out[`HUD fase orbit: ${document.getElementById('hOrb').textContent}`] = hudOk;
  // render langit jauh ke arah Saturnus: cahaya tepi atmosfer ada, tanpa nilai tidak valid
  const W = 320, H = 320, rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.FloatType });
  const cam = new THREE.PerspectiveCamera(40, 1, 1, 20000); cam.lookAt(S.saturn.position); cam.updateMatrixWorld(true);
  const shoot = () => {
    const U = S.saturn.userData.U; U.uCamL.value.copy(S.saturn.position).negate().applyQuaternion(S.saturn.quaternion.clone().invert());
    S.renderer.setRenderTarget(rt); S.renderer.setClearColor(0x000000, 1); S.renderer.clear(); S.renderer.render(S.farScene, cam); S.renderer.setRenderTarget(null);
    const px = new Float32Array(W * H * 4); S.renderer.readRenderTargetPixels(rt, 0, 0, W, H, px);
    let sum = 0, bad = 0; for (let i = 0; i < px.length; i += 4) { for (let c = 0; c < 3; c++) if (!Number.isFinite(px[i + c]) || px[i + c] < 0) bad++; sum += px[i] + px[i + 1] + px[i + 2]; }
    return { mean: sum / (W * H * 3), bad };
  };
  const limb = S.saturn.children.find((c) => c.renderOrder === 1);
  const on = shoot(); limb.visible = false; const off = shoot(); limb.visible = true;
  out[`cahaya tepi atmosfer saat gerhana: dengan ${on.mean.toFixed(5)} > tanpa ${off.mean.toFixed(5)}`] = on.mean > off.mean * 1.05;
  // sisi seberang orbit: terang kembali
  setPhase(E.phiC + Math.PI); S.updateLighting();
  const day = shoot();
  out[`sisi seberang orbit: k ${E.k.toFixed(2)}, sinar end cap ${L.uL_SunI.value.toFixed(3)}`] = E.k === 1 && Math.abs(L.uL_SunI.value - 0.12) < 1e-6;
  // silau Matahari: menyala di luar gerhana, padam saat gerhana (kamera menghadap Matahari)
  cam.lookAt(sd.clone().multiplyScalar(9000)); cam.updateMatrixWorld(true);
  S.saturn.visible = false;                                         // hanya bintang, titik Matahari, dan silau
  const glare = S.farScene.children.find((c) => c.material === S.saturn.userData.glareMat);
  const sunDay = shoot(); setPhase(E.phiC); const sunEcl = shoot();
  glare.visible = false; const base = shoot(); glare.visible = true; S.saturn.visible = true;
  out[`silau Matahari (di atas latar ${base.mean.toFixed(5)}): terang +${(sunDay.mean - base.mean).toFixed(5)}, saat gerhana +${(sunEcl.mean - base.mean).toFixed(5)}`] = sunDay.mean - base.mean > 1e-3 && Math.abs(sunEcl.mean - base.mean) < 1e-5;
  const nbad = on.bad + off.bad + day.bad + sunDay.bad + sunEcl.bad + base.bad;
  out[`render langit jauh: tanpa nilai tidak valid (${nbad})`] = nbad === 0;
  rt.dispose(); S.clock.orbit = 0; S.updateFar();
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
