"""Uji 15a (Copper Corn Station): trem menyala saat malam. Lampu strip plafon di atas ambang bloom, interior diterangi lampu
kabin (uCabin), kolam cahaya trem di tanah (uTram), siang tidak berubah. Render trem saja (target float) dari samping:
malam dengan lampu kabin lebih terang daripada tanpa, tanpa nilai tidak valid.
Pakai: python tools/uji_trem_malam.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(async () => {
  const S = window.__station, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const THREE = await import('https://cdn.jsdelivr.net/npm/three@0.186.1/build/three.module.js');
  const W = 480, H = 300, rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.FloatType });
  const shoot = () => {                                     // trem saja dari samping, 7 m dari sumbu rel
    const sc = new THREE.Scene(), tm = S.tramMesh, par = tm.parent; sc.add(tm); sc.rotation.copy(S.scene.rotation);
    sc.background = new THREE.Color(0, 0, 0); tm.updateMatrixWorld(true);
    const cam = new THREE.PerspectiveCamera(60, W / H, 0.1, 200), M = tm.matrixWorld;
    cam.position.set(7, 1.8, 0).applyMatrix4(M); cam.up.set(0, 1, 0).transformDirection(M);
    cam.lookAt(new THREE.Vector3(0, 1.6, 0).applyMatrix4(M)); cam.updateMatrixWorld(true);
    S.renderer.setRenderTarget(rt); S.renderer.clear(); S.renderer.render(sc, cam); S.renderer.setRenderTarget(null); par.add(tm);
    const px = new Float32Array(W * H * 4); S.renderer.readRenderTargetPixels(rt, 0, 0, W, H, px);
    let sum = 0, bad = 0; for (let i = 0; i < px.length; i += 4) { for (let c = 0; c < 3; c++) if (!Number.isFinite(px[i + c]) || px[i + c] < 0) bad++; sum += px[i] + px[i + 1] + px[i + 2]; }
    return { mean: sum / (W * H * 3), bad };
  };
  S.clock.hour = 12; S.updateLighting(); S.updateTramVisual();
  out[`siang: lampu kabin mati (uCabin ${S.CABIN_LIGHT.uCabin.value.r.toFixed(2)}), kolam cahaya mati (${S.groundMat.uniforms.uTram.value.w.toFixed(2)})`] = S.CABIN_LIGHT.uCabin.value.r === 0 && S.groundMat.uniforms.uTram.value.w === 0;
  S.clock.hour = 22; S.updateLighting(); await wait(1500); S.updateTramVisual();
  const lamp = S.TRAM_PARTS.cabinLamp.color, u = S.groundMat.uniforms.uTram.value;
  out[`malam: strip plafon ${lamp.r.toFixed(2)} (ambang bloom ${S.POST.bloomThr}), uCabin ${S.CABIN_LIGHT.uCabin.value.r.toFixed(2)}`] = lamp.r > S.POST.bloomThr && S.CABIN_LIGHT.uCabin.value.r > 0.5;
  out[`malam: kolam cahaya tanah mengikuti trem (za ${u.y.toFixed(0)} = ${S.tram.za.toFixed(0)}, malam ${u.w.toFixed(2)})`] = Math.abs(u.y - S.tram.za) < 0.01 && u.w > 0.9;
  const on = shoot(); const keep = S.CABIN_LIGHT.uCabin.value.clone(); S.CABIN_LIGHT.uCabin.value.setRGB(0, 0, 0);
  const off = shoot(); S.CABIN_LIGHT.uCabin.value.copy(keep);
  out[`render trem malam: dengan lampu kabin ${on.mean.toFixed(4)} > tanpa ${off.mean.toFixed(4)}`] = on.mean > off.mean * 1.3;
  out[`render trem: tanpa nilai tidak valid (${on.bad + off.bad})`] = on.bad + off.bad === 0;
  // revisi 16: lampu halte (strip di bawah atap + kolam cahaya di peron): menyala malam, padam siang
  const sl = S.STOP_LIGHT, nightStrip = sl.strip.material.color.r, nightPool = sl.pool.material.color.r;
  S.clock.hour = 12; S.updateLighting(); await wait(1500);
  const dayStrip = sl.strip.material.color.r, dayPool = sl.pool.material.color.r;
  out[`lampu halte: strip malam ${nightStrip.toFixed(2)} / siang ${dayStrip.toFixed(2)}, kolam peron malam ${nightPool.toFixed(2)} / siang ${dayPool.toFixed(2)}`] = nightStrip > S.POST.bloomThr && dayStrip < 1 && nightPool > 0.3 && dayPool < 0.01;
  rt.dispose(); S.clock.hour = 12;
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
