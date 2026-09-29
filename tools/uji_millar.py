"""Uji Millar's World R1 + R1b + R2 + R3: halaman termuat tanpa error, kamus English lengkap, 5 preset bisa berganti (dan ?preset=hemat),
tidak ada daratan (dasar laut selalu di bawah air terendah), fisika (1,3 g, lompat 77%), gelombang 125 m/s, jam dilatasi,
tersapu = kembali dengan penalti waktu, lensa Gargantua (radius bayangan, busur terbelokkan), tidak ada nilai tidak valid (NaN/Inf) di render HDR tiap preset.
Pakai: python tools/uji_millar.py   (butuh: pip install playwright && playwright install chromium)
Tanpa akses CDN langsung: THREE_LOCAL=<folder berisi three.module.js dan three.core.js> python tools/uji_millar.py
Chromium sendiri: CHROMIUM=<jalur executable>"""
import asyncio, os, pathlib
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
UJI = r"""
(async () => {
  const M = window.__millar, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms));
  // 1. kamus English: semua t('...') di kode dan semua data-t
  const EN = M.I18N.en, src = document.querySelector('script[type=module]').textContent;
  const re = /\bt\((['`])((?:\\.|(?!\1).)*)\1/g; let m; const hilang = [];
  while ((m = re.exec(src))) if (!(m[2] in EN)) hilang.push(m[2]);
  document.querySelectorAll('[data-t]').forEach((el) => { if (!(el.dataset.t in EN)) hilang.push(el.dataset.t); });
  for (const p of M.PRESETS) if (!(p.name in EN)) hilang.push(p.name);
  for (const x of M.MOODS) if (!(x.key in EN)) hilang.push(x.key);
  for (const v of M.CONFIG.views) if (!(v.key in EN)) hilang.push(v.key);
  out[`teks tanpa entri English: ${hilang.length}${hilang.length ? ' (' + hilang.slice(0, 5).join(' | ') + ')' : ''}`] = hilang.length === 0;

  // 2. tidak ada daratan: dasar laut tertinggi < air terendah (surut penuh dikurangi lembah ombak terdalam)
  let bedMax = -9;
  for (let i = 0; i < 40000; i++) { const x = (Math.random() - 0.5) * 20000, z = (Math.random() - 0.5) * 20000; bedMax = Math.max(bedMax, M.seabed(x, z)); }
  const trough = M.CHOP.base.slice(0, 16).reduce((s, b) => s + (b.a || 0), 0);
  const low = -M.CONFIG.wave.dd - M.CONFIG.chop.Hs * M.CONFIG.seaState.near / 2;
  out[`dasar laut tertinggi ${bedMax.toFixed(3)} m < air terendah ${low.toFixed(3)} m (surut + setengah Hs laut terbesar)`] = bedMax < low;
  out[`jumlah amplitudo ombak ${trough.toFixed(3)} m (batas atas lembah, info)`] = true;

  // 3. mulai, fisika lompat dengan langkah tetap
  M.start(); await wait(200);
  const P = M.P; P.view = 0; P.x = 0; P.z = 0; P.y = M.seabed(0, 0) + M.CONFIG.eye; P.ground = true;
  const y0 = P.y; P.vy = M.CONFIG.jumpV; P.ground = false; let top = y0;
  for (let i = 0; i < 240; i++) { M.stepPlayer(1 / 120); top = Math.max(top, P.y); }
  const jh = top - y0, jEarth = M.CONFIG.jumpV ** 2 / (2 * 9.80665);
  out[`lompat ${jh.toFixed(3)} m = ${(100 * jh / jEarth).toFixed(1)}% dari Bumi (harapan 77%)`] = Math.abs(jh / jEarth - 0.769) < 0.02;
  out[`gravitasi ${M.CONFIG.g} m/s2 = ${(M.CONFIG.g / 9.80665).toFixed(3)} g`] = Math.abs(M.CONFIG.g / 9.80665 - 1.3) < 0.002;

  // 4. gelombang dan jam: 10 s simulasi
  M.U.uWX.value += 80000 - M.frontX(0); const f0 = M.frontX(0), c0 = M.CLK.planet;
  for (let i = 0; i < 100; i++) M.simStep(0.1, 0.1);
  const v = (f0 - M.frontX(0)) / 10, dp = M.CLK.planet - c0;
  out[`kecepatan gelombang ${v.toFixed(2)} m/s (125)`] = Math.abs(v - 125) < 0.01;
  out[`1 s planet = ${(dp / 10 * M.CONFIG.dil / 3600).toFixed(2)} jam di luar (17,04)`] = Math.abs(dp / 10 * M.CONFIG.dil / 3600 - 17.045) < 0.01;

  // 5. tersapu: gelombang 150 m di depan
  M.U.uWX.value += 150 - M.frontX(0); const cBefore = M.CLK.planet;
  for (let i = 0; i < 300 && M.CLK.swept <= 0; i++) M.simStep(0.05, 0.05);
  const lost = (M.CLK.planet - cBefore) * M.CONFIG.dil / (365.25 * 86400);
  out[`tersapu: kembali ke awal (x ${P.x}), waktu di luar bertambah ${lost.toFixed(2)} tahun`] = M.CLK.swept > 0 && P.x === 0 && lost > 0.77;
  M.CLK.white = 0; M.U.uWX.value += 12000 - M.frontX(0);

  // 5b. lensa Gargantua (R1b): render GCUBE ke kamera sempit ke arah Gargantua, ukur radius bayangan ke atas
  //     (harapan CONFIG.garg.rad), ada busur piringan terbelokkan di atas bayangan, pusat gelap
  {
    const from = M.THREE.DataUtils.fromHalfFloat;
    const TH = M.THREE, N = 256, fov = 40, rt = new TH.WebGLRenderTarget(N, N, { type: TH.HalfFloatType });
    const cam = new TH.PerspectiveCamera(fov, 1, 0.1, 100); cam.position.set(0, 0, 0); cam.up.set(0, 1, 0);
    cam.lookAt(M.GU_.uGDir.value); cam.updateMatrixWorld(); cam.updateProjectionMatrix();
    M.renderer.setRenderTarget(rt); M.renderer.render(M.gScene, cam); M.renderer.setRenderTarget(null);
    const buf = new Uint16Array(N * N * 4); M.renderer.readRenderTargetPixels(rt, 0, 0, N, N, buf);
    const px = (x, y) => { const k = (y * N + x) * 4; return [from(buf[k]), from(buf[k + 1]), from(buf[k + 2]), from(buf[k + 3])]; };
    const hole = (p) => p[3] < 0.01 && p[0] + p[1] + p[2] < 0.05;
    const c = N / 2; let k = 0; while (k < c - 1 && hole(px(c, c + k))) k++;
    const ang = Math.atan(k / c * Math.tan(fov / 2 * Math.PI / 180)) * 180 / Math.PI;
    let arc = 0; for (let j = k; j < Math.min(c - 1, 2 * k); j++) { const p = px(c, c + j); arc = Math.max(arc, p[0] + p[1] + p[2]); }
    let bad = 0; for (let i = 0; i < buf.length; i++) if (!Number.isFinite(from(buf[i]))) bad++;
    out[`lensa: radius bayangan ${ang.toFixed(2)} derajat (harapan ${M.CONFIG.garg.rad}), D = ${M.LENS.D.toFixed(2)} rs`] = Math.abs(ang - M.CONFIG.garg.rad) < 0.8;
    out[`lensa: pusat gelap, busur piringan di atas bayangan (terang ${arc.toFixed(2)}), tidak valid ${bad}`] = hole(px(c, c)) && arc > 0.3 && bad === 0;
    rt.dispose();
  }

  // 5c. ombak FFT (R2): tinggi dari GPU = DFT di CPU (dari spektrum yang sama), tinggi signifikan, cakupan buih
  {
    const from = M.THREE.DataUtils.fromHalfFloat, O = M.OCEAN;
    const readC = (c) => { const N = O.N, b = new Uint16Array(N * N * 4); M.renderer.readRenderTargetPixels(c.out, 0, 0, N, N, b); return b; };
    for (const pi of [3, 0]) {
      M.applyPreset(pi); await wait(1500);
      const name = M.PRESETS[pi].name;
      out[`FFT aktif di ${name}: ${O.on}, ${O.casc.length} kaskade N ${O.N}`] = O.on && O.casc.length === M.PRESETS[pi].fftL.length;
      if (!O.on) continue;
      let v = 0, foam = 0, n = 0; const bufs = O.casc.map(readC);
      bufs.forEach((b) => { let s = 0, s2 = 0; for (let k = 0; k < b.length; k += 4) { const h = from(b[k + 1]); s += h; s2 += h * h; } const m = s / (b.length / 4); v += s2 / (b.length / 4) - m * m; });
      for (let k = 0; k < bufs[0].length; k += 4) { if (from(bufs[0][k + 3]) < M.CONFIG.fft.foamJ - 0.15) foam++; n++; }
      const hs = 4 * Math.sqrt(v) / O.amp;                    // dibagi pengali keadaan laut saat itu
      out[`FFT ${name}: tinggi signifikan ${hs.toFixed(3)} m pada keadaan laut 1 (CONFIG ${M.CONFIG.chop.Hs})`] = Math.abs(hs / M.CONFIG.chop.Hs - 1) < 0.08;
      out[`FFT ${name}: buih baru ${(100 * foam / n).toFixed(1)}% permukaan kaskade 1 (info)`] = true;
      if (pi === 3) {                                           // bandingkan dengan DFT langsung di 6 titik (N 64)
        const c = O.casc[0], N = O.N, L = c.L, t = O.t, b = bufs[0], g = M.CONFIG.g, dd = M.CONFIG.chop.depth; let err = 0;
        for (let q = 0; q < 6; q++) {
          const mx = (q * 37 + 5) % N, mz = (q * 23 + 11) % N, x = mx * L / N, z = mz * L / N; let re = 0;
          for (let m = 0; m < N; m++) for (let nn = 0; nn < N; nn++) {
            const o = (m * N + nn) * 4, kx = (nn < N / 2 ? nn : nn - N) * 2 * Math.PI / L, kz = (m < N / 2 ? m : m - N) * 2 * Math.PI / L, kl = Math.hypot(kx, kz);
            const w = Math.sqrt(g * kl * Math.tanh(Math.min(kl * dd, 20))), ph = w * t, cs = Math.cos(ph), sn = Math.sin(ph);
            const hr = c.raw[o] * cs - c.raw[o + 1] * sn + c.raw[o + 2] * cs + c.raw[o + 3] * sn;
            const hi = c.raw[o] * sn + c.raw[o + 1] * cs - c.raw[o + 2] * sn + c.raw[o + 3] * cs;
            const a = kx * x + kz * z; re += hr * Math.cos(a) - hi * Math.sin(a);
          }
          err = Math.max(err, Math.abs(re * O.amp - from(b[(mz * N + mx) * 4 + 1])));
        }
        out[`FFT GPU = DFT CPU di 6 titik: selisih maks ${(err * 1000).toFixed(2)} mm`] = err < 0.003;
      }
    }
    M.applyPreset(4); await wait(800);
    out[`Hemat tetap Gerstner (FFT ${M.OCEAN.on})`] = !M.OCEAN.on && M.seaNear.material.defines.FFT === 0;
  }

  // 5d. keadaan laut: ombak angin kecil saat gelombang raksasa jauh, besar saat dekat (FFT ikut)
  {
    const ks = [150000, 60000, 20000, 4000].map((d) => M.seaStateTarget(d));
    out[`keadaan laut: ${ks.map((k) => k.toFixed(2)).join(' / ')} untuk 150 / 60 / 20 / 4 km (naik saat mendekat)`] = ks[0] < ks[1] && ks[1] < ks[2] && ks[2] < ks[3] && Math.abs(ks[0] - M.CONFIG.seaState.far) < 0.01 && Math.abs(ks[3] - M.CONFIG.seaState.near) < 0.01;
    const from = M.THREE.DataUtils.fromHalfFloat, O = M.OCEAN, tau = M.CONFIG.seaState.tau;
    M.applyPreset(1); M.CONFIG.seaState.tau = 1e-4;
    const hsNow = async (d) => {
      M.U.uWX.value += d - M.frontX(M.P.z) + M.P.x; await wait(1500);
      let v = 0; for (const c of O.casc) { const N = O.N, b = new Uint16Array(N * N * 4); M.renderer.readRenderTargetPixels(c.out, 0, 0, N, N, b); let s1 = 0, s2 = 0; for (let k = 0; k < b.length; k += 4) { const h = from(b[k + 1]); s1 += h; s2 += h * h; } const n = b.length / 4; v += s2 / n - (s1 / n) ** 2; }
      return 4 * Math.sqrt(v);
    };
    const hFar = await hsNow(150000), hNear = await hsNow(3000);
    out[`FFT ikut keadaan laut: Hs ${hFar.toFixed(3)} m (jauh) -> ${hNear.toFixed(3)} m (dekat), harapan ${(0.35 * M.CONFIG.seaState.far).toFixed(3)} -> ${(0.35 * M.CONFIG.seaState.near).toFixed(3)}`] =
      Math.abs(hFar / (0.35 * M.CONFIG.seaState.far) - 1) < 0.08 && Math.abs(hNear / (0.35 * M.CONFIG.seaState.near) - 1) < 0.08;
    M.CONFIG.seaState.tau = tau; M.U.uWX.value += 40000 - M.frontX(M.P.z) + M.P.x;
  }

  // 5e. R3: riak menyebar dari kaki, cipratan jatuh lagi, langkah sesuai panjang langkah, air menahan gerak, kedalaman dari FFT
  {
    const from = M.THREE.DataUtils.fromHalfFloat, R = M.RIP, P = M.P;
    P.view = 0; P.x = 0; P.z = 0; P.vx = 0; P.vz = 0; P.y = M.seabed(0, 0) + M.CONFIG.eye; P.ground = true;
    M.updateRipple(1 / 60);
    for (let i = 0; i < 90; i++) M.updateRipple(1 / 60);          // tenangkan dulu
    const sx = R.ox + 2.0, sz = R.oz;
    M.ripSource(sx, sz, 0.22, -0.03, 0.8);
    for (let i = 0; i < 60; i++) M.updateRipple(1 / 60);          // 1 s
    const N = R.N, b = new Uint16Array(N * N * 4); M.renderer.readRenderTargetPixels(R.rt[R.i], 0, 0, N, N, b);
    const ci = Math.round((sx - R.ox) / R.dx + N / 2 - 0.5), cj = Math.round((sz - R.oz) / R.dx + N / 2 - 0.5);
    let best = 0, rBest = 0, bad = 0;
    for (let k = 0; k < b.length; k++) if (!Number.isFinite(from(b[k]))) bad++;
    for (let d = 2; d < N / 2 - 4; d++) { const i = ci + d; if (i >= N) break; const h = Math.abs(from(b[(cj * N + i) * 4])); if (h > best) { best = h; rBest = d * R.dx; } }
    const foam = from(b[(cj * N + ci) * 4 + 2]);
    out[`riak: cincin di ${rBest.toFixed(2)} m setelah 1 s (kecepatan ${R.c} m/s), buih jejak ${foam.toFixed(2)}, tidak valid ${bad}`] = rBest > 0.7 && rBest < 1.8 && foam > 0.1 && bad === 0;
    P.depth = 0.5; M.footstep(1, true);
    const a0 = M.SPL.alive || M.SPL.life.filter((l) => l > 0).length;
    for (let i = 0; i < 60; i++) M.stepSplash(1 / 30);
    out[`cipratan: ${a0} butir saat melangkah, sisa ${M.SPL.alive} setelah 2 s`] = a0 > 10 && M.SPL.alive === 0;
    // berjalan 4 s ke depan dengan langkah tetap
    const s0 = M.BOB.steps; M.keys.KeyW = true; let v01 = 0, vEnd = 0, dist = 0;
    for (let i = 0; i < 240; i++) { const x0 = P.x, z0 = P.z; M.stepPlayer(1 / 60); dist += Math.hypot(P.x - x0, P.z - z0); if (i === 5) v01 = Math.hypot(P.vx, P.vz); }
    vEnd = Math.hypot(P.vx, P.vz); M.keys.KeyW = false;
    const steps = M.BOB.steps - s0, exp = dist / M.CONFIG.walk.stride;
    out[`langkah: ${steps} langkah untuk ${dist.toFixed(2)} m (harapan ${exp.toFixed(1)})`] = Math.abs(steps - exp) <= 1.5;
    out[`air menahan: kecepatan ${v01.toFixed(2)} m/s setelah 0,1 s, ${vEnd.toFixed(2)} m/s setelah 4 s`] = v01 < 0.5 * vEnd && vEnd > 0.5;
    const lv = M.BOB.level; M.BOB.level = 0; M.headBob(1 / 60, 1.2, false, 0.5, 0); const off = Math.abs(M.BOB.dy) + Math.abs(M.BOB.dx); M.BOB.level = lv;
    out[`gerak kepala Mati: simpangan ${off.toFixed(4)} m`] = off === 0;
    await wait(2500);
    out[`kedalaman dari FFT (baca balik GPU): ok ${M.OCEAN.probe.ok}, h ${M.OCEAN.probe.h.toFixed(3)} m`] = !M.OCEAN.on || (M.OCEAN.probe.ok && Math.abs(M.OCEAN.probe.h) < 1);
  }

  // 6. tiap preset: berganti tanpa error, render HDR tanpa NaN/Inf dan tanpa titik menyala (> 50) di cakrawala dan di Gargantua
  //    (dulu: dengan MSAA, kedalaman air diekstrapolasi negatif di segitiga kecil cakrawala -> nilai meledak)
  const r = M.renderer, from = M.THREE.DataUtils.fromHalfFloat;
  M.P.pitch = 0.32; M.P.yaw = -Math.PI / 2 + 0.45; M.MOOD.brk = 1; M.STATE.visT = 137;   // cerah, Gargantua dan cakrawala di layar
  for (let i = 0; i < M.PRESETS.length; i++) {
    M.applyPreset(i); for (let w = 0; w < 40 && M.GCUBE.pending.length; w++) await wait(300); M.SKYCUBE.full = true; await wait(900);
    const T = M.POST.hdr, w = T.width, h = T.height;
    let bad = 0, hot = 0, mx = 0;
    const buf = new Uint16Array(w * h * 4); r.readRenderTargetPixels(T, 0, 0, w, h, buf);
    for (let k = 0; k < buf.length; k += 4) for (let c = 0; c < 3; c++) { const x = from(buf[k + c]); if (!Number.isFinite(x)) bad++; else { if (x > 50) hot++; mx = Math.max(mx, x); } }
    out[`preset ${M.PRESETS[i].name}: ${w}x${h}${T.samples ? ' MSAA ' + T.samples : ''}, tidak valid ${bad}, titik > 50: ${hot}, maks ${mx.toFixed(2)}`] = bad === 0 && hot === 0;
  }
  M.applyPreset(4);
  return out;
})()
"""

async def main():
    local = os.environ.get('THREE_LOCAL')
    async with async_playwright() as p:
        exe = os.environ.get('CHROMIUM')                              # opsional: jalur Chromium sendiri
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'], **({'executable_path': exe} if exe else {}))
        errs = []
        async def page(q):
            pg = await b.new_page(viewport={'width': 480, 'height': 270})
            pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
            pg.on('console', lambda m: errs.append(m.type + ': ' + m.text[:300]) if m.type in ('error', 'warning') else None)
            if local:
                async def serve(route):
                    await route.fulfill(path=str(pathlib.Path(local) / route.request.url.rsplit('/', 1)[-1]), content_type='text/javascript',
                                        headers={'Access-Control-Allow-Origin': '*'})
                await pg.route('https://cdn.jsdelivr.net/**', serve)
            await pg.goto(ROOT.joinpath('experiences/millar/index.html').as_uri() + q)
            await pg.wait_for_function('window.__millarReady === true', timeout=120000)
            await pg.wait_for_timeout(1500)
            return pg
        pg = await page('?lang=id')
        hasil = await pg.evaluate(UJI)
        pg2 = await page('?preset=hemat')
        hem = await pg2.evaluate('[window.__millar.PRESET.idx, window.__millar.PRESET.auto]')
        hasil[f'?preset=hemat -> preset {hem[0]}, otomatis {hem[1]}'] = hem == [4, False]
        ok = True
        for k, v in hasil.items():
            print(('OK   ' if v else 'GAGAL') + ' ' + k); ok &= bool(v)
        print('error:', errs[:10] or 'tidak ada')
        print('HASIL:', 'LULUS' if ok and not errs else 'GAGAL')
        await b.close()

asyncio.run(main())
