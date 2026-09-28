"""Uji 17c + 17e + 17f + awan terpantul (Copper Corn Station).
- 17c adaptasi mata: nilai luminans teradaptasi terbentuk, tanpa nilai tidak valid; malam lebih gelap dari siang sehingga
  pengali eksposur malam lebih besar (dibatasi), siang di luar sekitar 1.
- 17e lampu malam: nightLight() menyala dekat tiang lampu kota saat malam, nol di siang hari dan di ladang, hilang di atas 18 m.
- 17f bayangan sunline: peta bayangan dirender di pusat kota siang hari; sebagian titik tanah terbayangi, bayangan memanjang
  searah sumbu (lebih panjang ke arah za daripada ke arah keliling), tanpa nilai tidak valid; malam peta dimatikan.
- Awan: pantulan ke atas berubah ke warna awan bila peta awan penuh, kembali ke daratan bila kosong.
Pakai: python tools/uji_cahaya_lanjut.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(async () => {
  const S = window.__station, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const THREE = await import('https://cdn.jsdelivr.net/npm/three@0.186.1/build/three.module.js');
  const U = S.LIGHT.uniforms;
  // alat: evaluasi fungsi GLSL di banyak titik (satu piksel = satu titik)
  const evalGLSL = (W, H, body, extra = {}) => {
    const mat = new THREE.ShaderMaterial({ uniforms: Object.assign(extra, U),
      vertexShader: 'void main() { gl_Position = vec4(position.xy, 0.0, 1.0); }',
      fragmentShader: S.LIGHT_GLSL + `\nvoid main() { vec2 f = (gl_FragCoord.xy - 0.5) / vec2(${W - 1}.0, ${H - 1}.0);\n${body}\n}` });
    const sc = new THREE.Scene(), q = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), mat); q.frustumCulled = false; sc.add(q);
    const rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.FloatType });
    S.renderer.setRenderTarget(rt); S.renderer.render(sc, new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1)); S.renderer.setRenderTarget(null);
    const px = new Float32Array(W * H * 4); S.renderer.readRenderTargetPixels(rt, 0, 0, W, H, px); rt.dispose(); mat.dispose();
    return px;
  };
  const badOf = (px) => { let b = 0; for (let i = 0; i < px.length; i++) if (!Number.isFinite(px[i])) b++; return b; };
  let bad = 0;

  // ---------- 17e: lampu malam ----------
  const lampBody = (zaA, zaB, h) => `
    float za = mix(${zaA}.0, ${zaB}.0, f.y), s = f.x * 6283.185307 - 3141.59265, th = s / uL_R, r = uL_R - ${h}.0;
    vec3 p = vec3(r * cos(th), r * sin(th), za - uL_HalfL), n = vec3(-cos(th), -sin(th), 0.0);
    gl_FragColor = vec4(nightLight(p, n), 1.0);`;
  const maxOf = (px) => { let m = 0; for (let i = 0; i < px.length; i += 4) m = Math.max(m, px[i]); return m; };
  S.clock.hour = 23; S.updateLighting(); S.updateLighting();
  const cityN = evalGLSL(512, 256, lampBody(150, 2600, 1)); bad += badOf(cityN);
  const farmN = evalGLSL(128, 64, lampBody(4300, 4700, 1));   // ladang di antara dua cincin struktur (lampu cincin di za 4.009 dan 5.009) bad += badOf(farmN);
  const highN = evalGLSL(512, 256, lampBody(150, 2600, 30)); bad += badOf(highN);
  S.clock.hour = 13; S.updateLighting(); S.updateLighting();
  const dayN = evalGLSL(512, 256, lampBody(150, 2600, 1)); bad += badOf(dayN);
  out[`17e malam: cahaya lampu di kota maks ${maxOf(cityN).toFixed(2)}, ladang ${maxOf(farmN).toFixed(3)}, di ketinggian 30 m ${maxOf(highN).toFixed(3)}; siang ${maxOf(dayN).toFixed(3)}`] =
    maxOf(cityN) > 0.5 && maxOf(farmN) < 1e-3 && maxOf(highN) < 1e-3 && maxOf(dayN) < 1e-3;

  // ---------- 17f: bayangan sunline ----------
  S.teleport('nyc'); await wait(2500);
  S.clock.hour = 12; S.updateLighting(); S.sunShadowPass();
  out[`17f siang: peta bayangan sunline aktif (${U.uL_SunShOn.value})`] = U.uL_SunShOn.value === 1;
  const ps = S.player, s0 = ps.theta * S.R, z0 = ps.za, E = S.SUNSH.ext * 0.9;
  const shBody = `
    float s = ${s0.toFixed(3)} + (f.x * 2.0 - 1.0) * ${E.toFixed(1)}, za = ${z0.toFixed(3)} + (f.y * 2.0 - 1.0) * ${E.toFixed(1)}, th = s / uL_R, r = uL_R - 0.05;
    vec3 p = vec3(r * cos(th), r * sin(th), za - uL_HalfL), n = vec3(-cos(th), -sin(th), 0.0);
    float roof; gl_FragColor = vec4(sunlineShadow(p, n, roof), sunShCover(p), roof, 1.0);`;
  const W = 256, sh = evalGLSL(W, W, shBody); bad += badOf(sh);
  let shaded = 0, partial = 0, runS = 0, runZ = 0, nS = 0, nZ = 0;
  const v = (x, y) => sh[(y * W + x) * 4];
  for (let y = 0; y < W; y++) for (let x = 0; x < W; x++) { const a = v(x, y); if (a < 0.5) shaded++; if (a > 0.05 && a < 0.95) partial++; }
  // kehalusan: rata-rata perubahan antar piksel searah keliling (x) vs searah sumbu (y); penumbra memanjang searah sumbu
  for (let y = 1; y < W; y++) for (let x = 1; x < W; x++) { runS += Math.abs(v(x, y) - v(x - 1, y)); runZ += Math.abs(v(x, y) - v(x, y - 1)); nS++; nZ++; }
  const fr = shaded / (W * W);
  out[`17f pusat kota: ${(100 * fr).toFixed(1)}% tanah terbayangi sunline, ${(100 * partial / (W * W)).toFixed(1)}% penumbra`] = fr > 0.03 && fr < 0.9 && partial > 0;
  out[`17f bayangan tajam ke arah keliling, lembut searah sumbu: perubahan per piksel keliling ${(runS / nS).toFixed(4)} > sumbu ${(runZ / nZ).toFixed(4)}`] = runS / nS > runZ / nZ;
  S.clock.hour = 23; S.updateLighting(); S.sunShadowPass();
  out[`17f malam: peta bayangan sunline mati (${U.uL_SunShOn.value})`] = U.uL_SunShOn.value === 0;
  S.clock.hour = 12; S.updateLighting(); S.sunShadowPass();

  // ---------- awan terpantul ----------
  const upBody = `
    vec3 P = vec3(0.0, -998.0, 3300.0), d = normalize(vec3(0.25 * (f.x - 0.5), 1.0, 0.25 * (f.y - 0.5)));
    gl_FragColor = vec4(farEnv(P, d, 0.1, 0.0), 1.0);`;
  const ctx = S.CLOUD.mapCtx, tex = S.CLOUD.mapTex, cw = ctx.canvas.width, ch = ctx.canvas.height;
  const avg = (px) => { let r = 0, g = 0, b = 0, n = 0; for (let i = 0; i < px.length; i += 4) { r += px[i]; g += px[i + 1]; b += px[i + 2]; n++; } return [r / n, g / n, b / n]; };
  ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
  ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, cw, ch); tex.needsUpdate = true;
  const full = avg(evalGLSL(32, 32, upBody));
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, cw, ch); tex.needsUpdate = true;
  const none = avg(evalGLSL(32, 32, upBody));
  const cc = U.uL_CloudCol.value;
  out[`awan terpantul: peta awan penuh (${full.map((x) => x.toFixed(3)).join(', ')}) mendekati warna awan (${cc.x.toFixed(2)}, ${cc.y.toFixed(2)}, ${cc.z.toFixed(2)}); tanpa awan = daratan (${none.map((x) => x.toFixed(3)).join(', ')})`] =
    full[2] > none[2] * 1.5 && none[1] > none[2];
  S.CLOUD.drawShadow();                                               // kembalikan peta awan sebenarnya

  // ---------- 17c: adaptasi mata ----------
  const readL = () => { const px = new Uint16Array(4); S.renderer.readRenderTargetPixels(S.POST_R.lum[S.ADAPT.cur], 0, 0, 1, 1, px); return [...px].map((h) => THREE.DataUtils.fromHalfFloat(h)); };   // target half-float
  const mult = (L) => Math.min(S.ADAPT.max, Math.max(S.ADAPT.min, Math.pow(S.ADAPT.key / Math.max(L, 1e-4), S.ADAPT.pow)));
  // [0] = teradaptasi, [1] = sesaat. Sandbox lambat (beberapa fps), jadi pengali diuji dari nilai sesaat.
  const hr0 = S.clock.hourRate; S.clock.hourRate = 0;
  S.teleport('cooper'); S.clock.hour = 13; await wait(5000);
  const Ld = readL();
  S.player.theta = S.COOPER.s / S.R; S.player.za = S.COOPER.za; S.player.h = 0; await wait(5000);   // di dalam rumah Cooper
  const Lh = readL();
  S.teleport('spaceport'); await wait(5000);
  const Lt = readL();
  S.teleport('cooper'); S.clock.hour = 23; await wait(6000);
  const Ln = readL();
  out[`17c luminans sesaat: siang di luar ${Ld[1].toFixed(4)} (x${mult(Ld[1]).toFixed(2)}), dalam rumah Cooper ${Lh[1].toFixed(4)} (x${mult(Lh[1]).toFixed(2)}), terminal ${Lt[1].toFixed(4)} (x${mult(Lt[1]).toFixed(2)}), malam ${Ln[1].toFixed(4)} (x${mult(Ln[1]).toFixed(2)})`] =
    [Ld, Lh, Lt, Ln].every((v) => Number.isFinite(v[0]) && v[0] > 0) && Math.abs(mult(Ld[1]) - 1) < 0.2 && mult(Lh[1]) > 1.6 && mult(Lt[1]) > 1.6 && mult(Ln[1]) > 1.8;
  out[`17c nilai teradaptasi bergerak ke arah malam: ${Ld[0].toFixed(4)} -> ${Ln[0].toFixed(4)}`] = Ln[0] < Ld[0];
  S.clock.hour = 12; S.clock.hourRate = hr0;

  // ---------- 18a: kompleks utilitas padat ----------
  const UT = S.UTIL, inBand = S.houseList.filter(([s, za, w, d, h, t]) => za > UT.za0 && za < UT.za1 && w > 5 && d > 5);
  let ov = 0; const mo = (x) => { const C = 2 * Math.PI * S.R; return ((x % C) + C * 1.5) % C - C / 2; };
  for (let i = 0; i < inBand.length; i++) for (let j = i + 1; j < inBand.length; j++) {
    const A = inBand[i], B = inBand[j];
    if (Math.abs(mo(A[0] - B[0])) < (A[2] + B[2]) / 2 - 0.5 && Math.abs(A[1] - B[1]) < (A[3] + B[3]) / 2 - 0.5) ov++;
  }
  const inSky = inBand.filter(([s]) => Math.abs(mo(s - S.SKY_S)) < 45).length;
  out[`18a utilitas: ${S.UTIL_PLAN.modules} modul, ${S.UTIL_PLAN.silos} tangki, ${S.UTIL_PLAN.pipes} rak pipa; ${inBand.length} bangunan dasar; tumpang tindih ${ov}; di Skyway ${inSky}`] =
    S.UTIL_PLAN.modules > 1000 && ov === 0 && inSky === 0;

  out[`semua evaluasi shader: tanpa nilai tidak valid (${bad})`] = bad === 0;
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
