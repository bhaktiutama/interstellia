"""Uji Millar's World R1 + R1b + R2 + R3 + R4 + R5 + M3a-M3d: halaman termuat tanpa error, kamus English lengkap, 5 preset bisa berganti (dan ?preset=hemat),
tidak ada daratan (dasar laut selalu di bawah air terendah), fisika (1,3 g, lompat 77%), gelombang 125 m/s, jam dilatasi,
tersapu = kembali dengan penalti waktu, audio (lapisan ikut jarak gelombang, efek, bisu), misi radar (lokasi, gelombang tepat waktu, galat radar, rute terpendek bisa ditempuh, gagal bila tersapu), terbang KS-07 v5 (lepas landas, lolos di atas gelombang, tertelan, mendarat di tempat baru), shuttle KS-07 v5 (v1 di modul bersama tetap = Copper, tapak di dasar laut, kaki dan badan menahan pemain, tangga), lensa Gargantua (radius bayangan, busur terbelokkan), tidak ada nilai tidak valid (NaN/Inf) di render HDR tiap preset.
Pakai: python tools/uji_millar.py   (butuh: pip install playwright && playwright install chromium)
Tanpa akses CDN langsung: THREE_LOCAL=<folder berisi three.module.js dan three.core.js> python tools/uji_millar.py
Chromium sendiri: CHROMIUM=<jalur executable>"""
import asyncio, os, pathlib
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
UJI = r"""
(async () => {
  const M = window.__millar, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms));
  M.CINE.enabled = false;                                   // sinematik M4 diuji tersendiri di 5k
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
  M.setMode('jelajah'); M.start(); await wait(200);          // uji fisika lama memakai mode Jelajah; mode Misi diuji di 5j
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
  M.U.uWX.value += 150 - M.frontX(0); const cBefore = M.CLK.planet; let under = 0, rot = 0, tSw = 0;
  for (let i = 0; i < 300 && M.CLK.swept <= 0; i++) { M.simStep(0.05, 0.05); under = Math.max(under, M.SWEEP.under); rot = Math.max(rot, Math.abs(M.SWEEP.rx) + Math.abs(M.SWEEP.rz)); if (M.SWEEP.on) tSw = M.SWEEP.t; }
  out[`tersapu R4: di bawah air ${under.toFixed(2)}, kamera terguling ${rot.toFixed(1)} rad, urutan ${tSw.toFixed(2)} s`] = under > 0.99 && rot > 3 && tSw > 4;
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

  // 5f. R4: gelombang raksasa rapat, arus air surut, gelombang dekat tanpa nilai tidak valid
  {
    const face = M.US.filter((u) => u >= -800 && u <= 300), gaps = face.slice(1).map((u, i) => u - face[i]);
    const zs = M.ZS.map(Math.abs).sort((a, b) => a - b), dz = zs[1] - zs[0];
    out[`muka gelombang: ${M.US.length} sampel profil, ${face.length} di muka (jarak ${Math.min(...gaps).toFixed(1)}-${Math.max(...gaps).toFixed(1)} m), baris ${dz.toFixed(1)} m dekat pemain`] = face.length >= 50 && Math.max(...gaps) <= 26 && dz <= 6.5;
    const P = M.P; P.x = 0; P.z = 0; P.vx = 0; P.vz = 0; P.view = 0;
    M.U.uWX.value += 30000 - M.frontX(0); const cFar = M.currentAt(0, 0);
    M.U.uWX.value += M.CONFIG.current.at - M.frontX(0); const cNear = M.currentAt(0, 0);
    const x0 = P.x; for (let i = 0; i < 120; i++) M.stepPlayer(1 / 60); const drift = P.x - x0;
    out[`arus: ${cFar.toFixed(2)} m/s (gelombang 30 km), ${cNear.toFixed(2)} m/s (2,5 km); pemain terseret ${drift.toFixed(2)} m dalam 2 s ke arah gelombang`] = cFar < 0.01 && Math.abs(cNear - M.CONFIG.current.max) < 0.05 && drift > 0.8 && drift < 1.5;
    P.x = 0; P.pitch = 0.3; P.yaw = -Math.PI / 2;
    const from = M.THREE.DataUtils.fromHalfFloat;
    for (const d of [1500, 350]) {
      M.U.uWX.value += d - M.frontX(0); await wait(1500);
      const T = M.POST.hdr, w = T.width, h = T.height, b = new Uint16Array(w * h * 4); M.renderer.readRenderTargetPixels(T, 0, 0, w, h, b);
      let bad = 0, hot = 0; for (let k = 0; k < b.length; k += 4) for (let c = 0; c < 3; c++) { const x = from(b[k + c]); if (!Number.isFinite(x)) bad++; else if (x > 50) hot++; }
      out[`gelombang ${d} m di depan: tidak valid ${bad}, titik > 50: ${hot}`] = bad === 0 && hot === 0;
    }
    M.U.uWX.value += 40000 - M.frontX(0); P.pitch = 0.02;
  }

  // 5g. R5: audio (AudioContext berjalan setelah start, tingkat lapisan ikut jarak gelombang, efek, bisu)
  {
    const A = M.AUDIO, ctx = A.ctx;
    out[`audio: AudioContext ${ctx ? ctx.state : 'tidak ada'}, ${ctx ? ctx.sampleRate : 0} Hz`] = !!ctx && ctx.state === 'running';
    const km = [150, 60, 20, 8, 2, 0.5], mx = km.map((k) => M.audioMix(k * 1000, 1, 0, 0, 0.5, 0));
    const inc = (f) => mx.every((m, i) => i === 0 || f(m) > f(mx[i - 1]));
    out[`gemuruh ${km.map((k, i) => k + ' km ' + mx[i].rumble.toFixed(3)).join(', ')}; naik dan makin terbuka saat mendekat`] = inc((m) => m.rumble) && inc((m) => m.rumbleLP) && mx[0].rumble < 0.02;
    out[`deru air pecah: 8 km ${mx[3].roar.toFixed(2)}, 2 km ${mx[4].roar.toFixed(2)}, 500 m ${mx[5].roar.toFixed(2)}`] = mx[3].roar === 0 && mx[4].roar > 0 && mx[5].roar > mx[4].roar;
    const uw = M.audioMix(2000, 1, 0, 0, 0.5, 1), dry = M.audioMix(2000, 1, 0, 0, 0, 0), wd = M.audioMix(40000, 1, 0, 1.5, 0.5, 0);
    const cur = M.audioMix(2500, 1, M.CONFIG.current.max, 0, 0.5, 0), vals = [...mx, uw, dry, wd, cur, M.audioMix(0, 1.5, 0, 0, 0, 0), M.audioMix(-3000, 1.5, 0, 0, 0, 0)];
    const valid = vals.every((m) => Object.values(m).every(Number.isFinite));
    out[`bawah air: lowpass ${uw.lp} Hz (di atas ${dry.lp} Hz); kecipak jalan ${wd.wade.toFixed(2)}, diam ${dry.wade}; arus ${cur.current.toFixed(2)}; semua nilai valid ${valid}`] = uw.lp <= 400 && dry.lp >= 20000 && wd.wade > 0.1 && wd.wade <= 0.18 && mx[0].wind <= 0.14 && dry.wade === 0 && cur.current > 0.3 && valid;
    const P = M.P; P.view = 0; P.depth = 0.5; const n0 = A.sfx; M.footstep(1, true); M.sfxImpact(); const n1 = A.sfx;
    out[`efek suara: langkah dua kaki + hantaman = ${n1 - n0} bunyi`] = n1 - n0 === 3;
    M.U.uWX.value += 1500 - M.frontX(0); await wait(1200);
    let rms = 0;
    if (ctx) { const d = new Float32Array(A.an.fftSize); A.an.getFloatTimeDomainData(d); rms = Math.sqrt(d.reduce((s, x) => s + x * x, 0) / d.length); }
    M.setSound(false); await wait(500); const g = ctx ? A.master.gain.value : 0; M.setSound(true);
    out[`keluaran (gelombang 1,5 km): RMS ${rms.toFixed(4)}; M bisu -> gain master ${g.toFixed(4)}`] = rms > 0.001 && Number.isFinite(rms) && g < 0.01;
    M.U.uWX.value += 40000 - M.frontX(0);
  }

  // 5i. M3a + M3d: shuttle KS-07 v5 mendarat di air (modul bersama shared/kestrel.js)
  {
    const S = M.SHIP, K = window.KESTREL, KS = K.build(M.THREE);
    const fp = (g) => { let h = 0, n = 0; for (const a of [...Object.values(g.attributes), g.index].filter(Boolean)) for (let j = 0; j < a.array.length; j++) { h = (h * 31 + Math.round(a.array[j] * 1e5)) % 2147483647; n++; } return `n${n} h${h}`; };
    const sid = [fp(KS.hullG), fp(KS.partsG), fp(KS.glowG)].join(', ');
    // v1 disimpan di modul bersama tanpa perubahan (sidik jari tahap 11d; Copper memakai v5 sejak M3e)
    out[`KS-07 v1 di modul bersama tidak berubah (${sid})`] = sid === 'n24318 h620106941, n14256 h2123920359, n1458 h-1932132836';
    const g = M.KS.geo, pa = g.attributes.position.array, na = g.attributes.normal.array, ca = g.attributes.color.array;
    let bad = 0, lum = 0, glass = 0; for (let i = 0; i < pa.length; i++) if (!Number.isFinite(pa[i]) || !Number.isFinite(na[i])) bad++;
    for (let i = 0; i < ca.length; i += 3) { lum += 0.3 * ca[i] + 0.59 * ca[i + 1] + 0.11 * ca[i + 2]; if (ca[i + 2] - ca[i] > 0.035 && ca[i + 1] < 0.1) glass++; }
    lum /= ca.length / 3;
    const gc = M.KS.glass.attributes.color.array; let gOk = 0; for (let i = 0; i < gc.length; i += 3) if (gc[i + 2] - gc[i] > 0.035 && gc[i + 1] < 0.1) gOk++;
    out[`KS-07 v5: ${g.attributes.position.count} titik, 3 kaki, tidak valid ${bad}, warna gelap rata-rata ${lum.toFixed(3)}, kaca terpisah ${gOk} titik (sisa di badan ${glass})`] = bad === 0 && S.pads.length === 3 && lum < 0.25 && glass === 0 && gOk > 0 && gOk === gc.length / 3;
    // urutan segitiga = arah normal, kaca menghadap keluar (dulu loft terbalik: tersamar DoubleSide, gosong perut salah sisi)
    { const V3 = M.THREE.Vector3, eye = new V3(...M.CK.eye); let agree = 0, dis = 0, gout = 0, gin = 0, lin = 0, lout = 0;
      const faces = (geo, fn) => { const pp = geo.attributes.position, nn = geo.attributes.normal; for (let i = 0; i < pp.count; i += 3) { const a = new V3().fromBufferAttribute(pp, i), b = new V3().fromBufferAttribute(pp, i + 1), c = new V3().fromBufferAttribute(pp, i + 2); fn(a, b, c, new V3().fromBufferAttribute(nn, i), i); } };
      faces(g, (a, b, c, n) => { const f = b.clone().sub(a).cross(c.clone().sub(a)); if (f.lengthSq() > 1e-12) { if (f.dot(n) > 0) agree++; else dis++; } });
      faces(M.KS.glass, (a, b, c, n) => { if (n.dot(eye.clone().sub(a)) < 0) gout++; else gin++; });
      faces(M.CK.geo, (a, b, c, n, i) => { if (i < 156) { if (n.dot(eye.clone().sub(a)) > 0) lin++; else lout++; } });
      out[`urutan segitiga badan sesuai normal ${agree}/${agree + dis}, kaca menghadap keluar ${gout}/${gout + gin}, pelapis kokpit menghadap ke dalam ${lin}/${lin + lout}`] = dis === 0 && gin === 0 && gout > 0 && lout === 0 && lin > 0; }
    // kokpit v5: geometri valid, mata di dalam badan, di atas kursi, bisa melihat melewati hidung
    { const cg = M.CK.geo.attributes, [w, h, cy] = window.KESTREL.v5At(M.CK.eye[2]); let cb = 0;
      for (const a of [cg.position.array, cg.normal.array, M.CK.stick.attributes.position.array, M.CK.throttle.attributes.position.array]) for (const x of a) if (!Number.isFinite(x)) cb++;
      const top = cy + h / 2, nose = window.KESTREL.v5At(-5.4), look = Math.atan2(M.CK.eye[1] - (nose[2] + nose[1] / 2), M.CK.eye[2] + 5.4) * 180 / Math.PI;
      out[`kokpit v5: ${cg.position.count} titik, tidak valid ${cb}, 3 layar MFD, mata ${(top - M.CK.eye[1]).toFixed(2)} m di bawah atap, pandangan lewat hidung ${look.toFixed(1)} derajat ke bawah`] = cb === 0 && M.CK.screens.length === 3 && top - M.CK.eye[1] > 0.2 && look > 3; }
    const gap = S.pads.map((p) => S.y - S.padDrop - M.seabed(p.x, p.z));
    out[`tapak di dasar laut: celah ${gap.map((x) => x.toFixed(2)).join(' / ')} m; perut ${S.belly.toFixed(2)} m di atas muka air rata-rata`] = gap.every((x) => x >= -0.001 && x < 0.4) && S.belly > 0.3;
    const P = M.P, p0 = S.pads[1]; P.view = 0; P.x = p0.x - 3; P.z = p0.z; P.vx = P.vz = 0; P.yaw = -Math.PI / 2;   // menghadap +x ke kaki
    M.U.uWX.value += 40000 - M.frontX(0);
    const walk = (n) => { let dmin = 1e9; M.keys.KeyW = true; for (let i = 0; i < n; i++) { M.stepPlayer(1 / 60); dmin = Math.min(dmin, Math.hypot(P.x - p0.x, P.z - p0.z)); } M.keys.KeyW = false; return dmin; };
    const dmin = walk(240);
    out[`kaki pendarat menahan pemain: jarak terdekat ${dmin.toFixed(2)} m (batas ${(p0.r + 0.3).toFixed(2)} m)`] = dmin >= p0.r + 0.29;
    // badan dan sayap (lebih rendah dari kepala): berjalan dari belakang lurus ke tengah tidak boleh masuk ke bawahnya
    const [bx, bz] = M.shipToWorld(0, 10), [fx, fz] = M.shipToWorld(0, 0);
    P.x = bx; P.z = bz; P.vx = P.vz = 0; P.yaw = Math.atan2(-(fx - bx), -(fz - bz));
    let inside = 0; M.keys.KeyW = true; for (let i = 0; i < 400; i++) { M.stepPlayer(1 / 60); const [mx, mz] = M.worldToShip(P.x, P.z); for (const L of M.KS.low) if (mx > L.x0 && mx < L.x1 && mz > L.z0 && mz < L.z1) inside++; } M.keys.KeyW = false;
    out[`badan dan sayap menahan pemain: ${inside} langkah di bawahnya`] = inside === 0;
    out[`pintu di sisi yang menghadap titik awal: ${Math.hypot(S.door.x, S.door.z).toFixed(1)} m (pusat ${Math.hypot(S.x, S.z).toFixed(1)} m)`] = Math.hypot(S.door.x, S.door.z) < Math.hypot(S.x, S.z);
    const pos = M.seaFar.geometry.attributes.position, ix = M.seaFar.geometry.index.array, v = (k) => new M.THREE.Vector3().fromBufferAttribute(pos, ix[k]);
    const nrm = new M.THREE.Vector3().crossVectors(v(1).sub(v(0)), v(2).sub(v(0)));
    out[`laut jauh menghadap ke atas (normal y ${nrm.y.toFixed(3)}; dulu terbalik dan dibuang culling)`] = nrm.y > 0;
    // render dengan shuttle di layar: tanpa nilai tidak valid atau titik menyala
    P.x = 0; P.z = 0; P.pitch = 0.06; P.yaw = Math.atan2(-(S.x), -(S.z)); await wait(1500);
    const T = M.POST.hdr, w = T.width, h = T.height, bb = new Uint16Array(w * h * 4); M.renderer.readRenderTargetPixels(T, 0, 0, w, h, bb);
    const from = M.THREE.DataUtils.fromHalfFloat; let nb = 0, hot = 0;
    for (let k = 0; k < bb.length; k += 4) for (let c = 0; c < 3; c++) { const x = from(bb[k + c]); if (!Number.isFinite(x)) nb++; else if (x > 50) hot++; }
    out[`shuttle di layar: tidak valid ${nb}, titik > 50: ${hot}`] = nb === 0 && hot === 0;
    // pandangan kokpit (V) saat terbang: interior tampil, layar MFD tergambar, tanpa nilai tidak valid
    { const keep = { x: P.x, y: P.y, z: P.z }, FL = M.FLY;
      P.x = S.door.x; P.z = S.door.z; M.missionAction();
      Object.assign(FL, { landed: false, spool: 1, view: 1 }); FL.y += 30; await wait(1500);
      const vis = M.COCKPIT.group.visible, sc = M.COCKPIT.screens.tengah, px = sc.g.getImageData(0, 0, sc.cv.width, sc.cv.height).data; let lit = 0;
      for (let k = 0; k < px.length; k += 4) if (px[k] + px[k + 1] + px[k + 2] > 150) lit++;
      const T3 = M.POST.hdr, b3 = new Uint16Array(T3.width * T3.height * 4); M.renderer.readRenderTargetPixels(T3, 0, 0, T3.width, T3.height, b3);
      let nb3 = 0, hot3 = 0; for (let k = 0; k < b3.length; k += 4) for (let c = 0; c < 3; c++) { const x = M.THREE.DataUtils.fromHalfFloat(b3[k + c]); if (!Number.isFinite(x)) nb3++; else if (x > 50) hot3++; }
      M.flyReset(); const off = !M.COCKPIT.group.visible;
      out[`pandangan kokpit: interior tampil ${vis}, layar tengah ${lit} piksel terang, tidak valid ${nb3}, titik > 50: ${hot3}; mendarat/atur ulang = interior disembunyikan ${off}`] = vis && lit > 50 && nb3 === 0 && hot3 === 0 && off;
      Object.assign(P, keep); }
    P.yaw = -Math.PI / 2 + 18 * Math.PI / 180;
  }

  // 5h. tombol standar (patokan Copper Corn Station, docs/app/tombol.md)
  {
    const key = (code) => dispatchEvent(new KeyboardEvent('keydown', { code, bubbles: true }));
    const up = (code) => dispatchEvent(new KeyboardEvent('keyup', { code, bubbles: true }));
    const r = {}, p0 = M.PRESET.idx, s0 = M.AUDIO.on, b0 = M.BOB.level;
    key('KeyQ'); up('KeyQ'); r.Q = M.PRESET.idx === (p0 + 1) % M.PRESETS.length;
    key('KeyP'); up('KeyP'); r.P = M.POST.mode === 1; key('KeyP'); up('KeyP'); key('KeyP'); up('KeyP'); r.P3 = M.POST.mode === 0;
    key('KeyU'); up('KeyU'); r.U = M.AUDIO.on === !s0; key('KeyU'); up('KeyU');
    key('Backquote'); up('Backquote'); r.panel = !document.getElementById('lab').hidden && document.querySelectorAll('#labBtns button').length === M.LAB.length;
    document.querySelectorAll('#labBtns button')[4].click(); r.bobPanel = M.BOB.level !== b0;
    key('Backquote'); up('Backquote'); r.panelTutup = document.getElementById('lab').hidden;
    key('KeyB'); up('KeyB'); r.B = M.BOB.level !== b0;                                                  // B tidak lagi dipakai
    key('KeyM'); up('KeyM'); r.M = M.MIS.radar && !document.getElementById('radar').hidden && M.AUDIO.on === s0; key('KeyM'); up('KeyM'); r.M2 = !M.MIS.radar;   // M = radar
    key('Slash'); up('Slash'); r.help = !document.getElementById('help').hidden && document.querySelectorAll('#helpRows tr').length >= 12;
    key('Escape'); up('Escape'); r.helpTutup = document.getElementById('help').hidden;
    key('KeyF'); up('KeyF'); r.F = M.PHOTO.on && document.body.classList.contains('photo');
    key('Escape'); up('Escape'); r.Fkeluar = !M.PHOTO.on;
    M.PRESET.idx !== p0 && M.applyPreset(p0); while (M.BOB.level !== b0) M.cycleBob();
    const gagal = Object.keys(r).filter((k) => !r[k]);
    out[`tombol: Q grafik, P efek layar (3 mode), U suara, \` panel (gerak kepala), ? bantuan, F foto, M radar; B kosong; gagal: ${gagal.join(', ') || 'tidak ada'}`] = gagal.length === 0;
  }

  // 5j. M3c: misi radar (lokasi, gelombang tepat waktu, radar, rute bisa ditempuh sebelum gelombang, gagal bila tersapu)
  {
    const C = M.CONFIG.mission, SH = M.SHIP, P = M.P, dd = (a, b) => Math.hypot(a.x - b.x, a.z - b.z);
    P.x = 0; P.z = 0;
    let okN = 0, tmin = 1e9, tmax = 0;
    for (let sd = 1; sd <= 200; sd++) {
      const g = M.missionSites(sd * 7919); if (!g) continue;
      const pts = g.pts, rs = pts.map((p) => dd(p, SH)), seps = [dd(pts[0], pts[1]), dd(pts[0], pts[2]), dd(pts[1], pts[2])];
      if (rs.every((r) => r >= C.rMin - 0.01 && r <= C.rMax + 0.01) && seps.every((x) => x >= C.sep) && g.tour >= C.tourMin && g.tour <= C.tourMax) okN++;
      tmin = Math.min(tmin, g.tour); tmax = Math.max(tmax, g.tour);
    }
    out[`lokasi misi: ${okN}/200 benih memenuhi syarat (jarak ${C.rMin}-${C.rMax} m, antarlokasi >= ${C.sep} m), rute ${tmin.toFixed(0)}-${tmax.toFixed(0)} m`] = okN === 200;
    M.setMode('misi'); M.setLevel(1); M.startMission();
    const eta = (M.frontX(P.z) - P.x) / M.CONFIG.wave.v;
    out[`mode Misi Normal: gelombang tiba dalam ${eta.toFixed(1)} s (batas ${M.MIS.limit} s), 3 pecahan di layar`] = Math.abs(eta - 300) < 0.5 && M.MIS.sites.length === 3 && M.MIS.group;
    // radar: galat mengecil saat dekat
    const S0 = M.MIS.sites[0], err = (dist) => { P.x = S0.x - dist; P.z = S0.z; let e = 0; for (let k = 0; k < 400; k++) { M.radarFix(S0); e += Math.hypot(S0.blip.x - S0.x, S0.blip.z - S0.z); } return e / 400; };
    const eFar = err(200), eNear = err(15);
    out[`radar: galat rata-rata ${eFar.toFixed(1)} m di 200 m, ${eNear.toFixed(1)} m di 15 m`] = eNear < eFar / 3 && eNear < 5;
    M.stopMission(); M.startMission();
    // rute: lari (Shift + W) ke tiap barang menurut urutan terpendek, tahan E 2 s, lalu ke pintu KS-07 dan E
    const MI = M.MIS, targets = [...MI.order.map((i) => ({ x: MI.sites[i].ix, z: MI.sites[i].iz, i })), { x: SH.door.x, z: SH.door.z, door: true }];
    const dt = 1 / 30; let T = 0, stuck = 0, side = 0, last = { x: P.x, z: P.z }, lastT = 0, holds = 0;
    M.keys.ShiftLeft = true;
    for (const tg of targets) {
      const R = tg.door ? C.doorR - 0.8 : C.pickR - 0.8;
      // titik jalan: ke tangga lewat sisi luarnya; memutari wahana (lingkaran 8 m) bila garis lurus menembusnya
      const way = [];
      if (tg.door) way.push({ x: SH.door.x - Math.cos(SH.yaw) * 4, z: SH.door.z + Math.sin(SH.yaw) * 4 });
      const aim = way.length ? way[0] : tg, ex = aim.x - P.x, ez = aim.z - P.z, L2 = ex * ex + ez * ez;
      const u = Math.max(0, Math.min(1, ((SH.x - P.x) * ex + (SH.z - P.z) * ez) / Math.max(L2, 1e-6))), cx = P.x + ex * u - SH.x, cz = P.z + ez * u - SH.z, cd = Math.hypot(cx, cz);
      if (cd < 8 && Math.hypot(aim.x - SH.x, aim.z - SH.z) > 3) { const k = 10 / Math.max(cd, 0.5), sx = cd > 0.5 ? cx : -ez, sz = cd > 0.5 ? cz : ex; way.unshift({ x: SH.x + sx * (cd > 0.5 ? k : 10 / Math.sqrt(L2)), z: SH.z + sz * (cd > 0.5 ? k : 10 / Math.sqrt(L2)) }); }
      for (const wp of way) while (Math.hypot(wp.x - P.x, wp.z - P.z) > 1.5 && T < 420) {
        P.yaw = Math.atan2(-(wp.x - P.x), -(wp.z - P.z)); M.keys.KeyW = true; M.stepPlayer(dt); M.updateMission(dt, dt); T += dt;
      }
      while (Math.hypot(tg.x - P.x, tg.z - P.z) > R && T < 420) {
        P.yaw = Math.atan2(-(tg.x - P.x), -(tg.z - P.z)) + (side > 0 ? 1.2 : 0);
        M.keys.KeyW = true; M.stepPlayer(dt); M.updateMission(dt, dt); T += dt; side -= dt;
        if (T - lastT > 1) { if (Math.hypot(P.x - last.x, P.z - last.z) < 0.4) { side = 1.5; stuck++; } last = { x: P.x, z: P.z }; lastT = T; }
      }
      M.keys.KeyW = false;
      for (let k = 0; k < 20; k++) { M.stepPlayer(dt); M.updateMission(dt, dt); T += dt; }      // berhenti (inersia air)
      if (tg.door) M.missionAction();
      else { M.keys.KeyE = true; for (let k = 0; k < 66 && !MI.sites[tg.i].got; k++) { M.stepPlayer(dt); M.updateMission(dt, dt); T += dt; } M.keys.KeyE = false; if (MI.sites[tg.i].got) holds++; }
    }
    M.keys.ShiftLeft = false;
    const FL = M.FLY;
    out[`rute terpendek ${MI.tour.toFixed(0)} m: lari + ambil ${holds}/3 + naik = ${T.toFixed(0)} s, cadangan lepas landas 45 s, batas ${MI.limit} s (tersendat ${stuck}x)`] = FL.on && !MI.result && holds === 3 && T + 45 <= MI.limit;
    // M3d: lepas landas (R + Shift) dengan gelombang 45 s lagi, lolos di atas puncak
    M.U.uWX.value += FL.x + M.CONFIG.wave.v * 45 - M.frontX(FL.z);
    M.keys.KeyR = true; M.keys.ShiftLeft = true; let tUp = -1, tt = 0;
    for (let k = 0; k < 90 * 30 && !MI.result; k++) { M.simStep(dt, dt); M.updateFly(dt); M.updateMission(dt, dt); tt += dt; if (tUp < 0 && FL.y - FL.water > 1300) tUp = tt; }
    M.keys.KeyR = false; M.keys.ShiftLeft = false;
    await wait(1200);
    const T2 = M.POST.hdr, w2 = T2.width, h2 = T2.height, b2 = new Uint16Array(w2 * h2 * 4); M.renderer.readRenderTargetPixels(T2, 0, 0, w2, h2, b2);
    const fromH = M.THREE.DataUtils.fromHalfFloat; let nb2 = 0, hot2 = 0;
    for (let k = 0; k < b2.length; k += 4) for (let c = 0; c < 3; c++) { const x = fromH(b2[k + c]); if (!Number.isFinite(x)) nb2++; else if (x > 50) hot2++; }
    out[`lepas landas: 1.300 m dalam ${tUp.toFixed(1)} s, gelombang lewat di bawah: ${MI.result ? MI.result.why : '-'} (ketinggian ${MI.result ? MI.result.alt.toFixed(0) : '-'} m); render terbang tidak valid ${nb2}, titik > 50: ${hot2}`] = !!MI.result && MI.result.ok && MI.result.why === 'lolos' && tUp > 0 && tUp < 40 && nb2 === 0 && hot2 === 0;
    document.getElementById('result').hidden = true; M.STATE.started = true;
    // tertelan: naik ke wahana saat gelombang tinggal 3 s, tidak lepas landas
    M.startMission(); for (const S of MI.sites) S.got = true;
    P.x = M.SHIP.door.x; P.z = M.SHIP.door.z; M.missionAction();
    M.U.uWX.value += FL.x + M.CONFIG.wave.v * 3 - M.frontX(FL.z);
    for (let k = 0; k < 20 * 30 && !MI.result; k++) { M.simStep(dt, dt); M.updateFly(dt); }
    out[`wahana masih di air saat gelombang tiba = ${MI.result ? MI.result.why : 'tidak ada hasil'}`] = !!MI.result && !MI.result.ok && MI.result.why === 'tertelan';
    document.getElementById('result').hidden = true; M.STATE.started = true;
    // gagal: gelombang 300 m di depan, tersapu -> layar hasil gagal
    M.startMission(); P.x = 0; P.z = 0; P.y = M.seabed(0, 0) + M.CONFIG.eye;
    M.U.uWX.value += P.x + 300 - M.frontX(P.z);
    for (let k = 0; k < 400 && !MI.result; k++) M.simStep(dt, dt);
    out[`tersapu di mode Misi = misi gagal (layar hasil tampil: ${!document.getElementById('result').hidden})`] = !!MI.result && !MI.result.ok && !document.getElementById('result').hidden;
    document.getElementById('result').hidden = true; M.stopMission(); M.setMode('jelajah'); M.STATE.started = true;
    M.U.uWX.value += 40000 - M.frontX(0); P.x = 0; P.z = 0;
    // mode Jelajah: naik, terbang maju 2 s, berhenti, turun, E mendarat di tempat baru, turun di samping tangga
    const x0 = M.SHIP.x, z0 = M.SHIP.z;
    P.x = M.SHIP.door.x; P.z = M.SHIP.door.z; M.missionAction();
    const run = (n, ks) => { for (const k of ks) M.keys[k] = true; for (let i = 0; i < n; i++) M.updateFly(dt); for (const k of ks) M.keys[k] = false; };
    run(75, []); run(60, ['KeyR']); run(60, ['KeyW']); run(150, []);
    let guard = 0; while (FL.y - FL.water > M.SHIP.padDrop + 2 && guard++ < 900) run(1, ['KeyF']);
    run(90, []); M.missionAction();
    const moved = Math.hypot(M.SHIP.x - x0, M.SHIP.z - z0), pd = Math.hypot(P.x - M.SHIP.door.x, P.z - M.SHIP.door.z);
    out[`mode Jelajah: terbang dan mendarat ${moved.toFixed(0)} m dari tempat semula, pemain turun ${pd.toFixed(1)} m dari tangga`] = !FL.on && moved > 10 && pd < 2 && M.SHIP.legs.visible;
    M.flyReset(); P.x = 0; P.z = 0; P.y = M.seabed(0, 0) + M.CONFIG.eye; P.view = 0;
  }

  // 5k. M4: pandangan orbit dan sinematik kedatangan / keberangkatan
  {
    const hdrCheck = () => { const T = M.POST.hdr, b = new Uint16Array(T.width * T.height * 4); M.renderer.readRenderTargetPixels(T, 0, 0, T.width, T.height, b);
      let nb = 0, mx = 0, lum = 0; for (let k = 0; k < b.length; k += 4) for (let c = 0; c < 3; c++) { const x = M.THREE.DataUtils.fromHalfFloat(b[k + c]); if (!Number.isFinite(x)) nb++; else { mx = Math.max(mx, x); lum += x; } }
      return { nb, mx, lum: lum / (b.length * 0.75) }; };
    const C = M.CINE, P = M.P, dt = 1 / 30;
    M.CINE.enabled = true; M.CINE.played = false; M.STATE.started = false; M.setMode('misi');
    M.startWithCine();
    const shots = [];
    for (const tt of [3, 10, 17]) { C.t = tt; await wait(900); const h = hdrCheck(); shots.push(`${tt} s ${C.orbit ? 'orbit' : 'dunia'} tidak valid ${h.nb} terang ${h.lum.toFixed(3)}`); if (!(C.orbit && h.nb === 0 && h.lum > 0.001)) shots.push('GAGAL'); }
    out[`sinematik orbit: ${shots.join(', ')}`] = C.on && C.kind === 'arrive' && !shots.includes('GAGAL') && !M.STATE.started;
    // jalan penuh 21-35 s dengan langkah tetap: kapal tidak pernah di bawah titik mendarat, kamera di atas air, berakhir di titik semula
    C.t = 20.9; let minGap = 1e9, camLow = 0, steps = 0, ckSeen = 0; const yl = (() => { M.placeShip(...M.SHIP.home); return M.SHIP.y; })();
    while (C.on && steps++ < 600) { M.cineStep(dt); if (C.world) { minGap = Math.min(minGap, M.SHIP.mesh.position.y - yl); if (M.camera.position.y < M.drawdown(M.camera.position.x - M.frontX(M.camera.position.z)) + 0.5) camLow++; if (M.COCKPIT.group.visible) ckSeen++; } }
    const home = M.SHIP.home, dHome = Math.hypot(M.SHIP.x - home[0], M.SHIP.z - home[1]);
    const dDoor = Math.hypot(P.x - M.SHIP.door.x, P.z - M.SHIP.door.z);
    out[`kedatangan (dari kokpit): mendarat ${dHome.toFixed(2)} m dari titik semula, celah terendah ${minGap.toFixed(2)} m, kamera di bawah air ${camLow}x, kokpit tampil ${ckSeen}x, misi mulai ${M.MIS.on}, pemain ${dDoor.toFixed(1)} m dari tangga`] =
      !C.on && dHome < 0.01 && minGap > -0.01 && camLow === 0 && ckSeen > 100 && M.MIS.on && M.STATE.started && dDoor < 2 && M.SHIP.legs.visible && !M.COCKPIT.group.visible;
    // lewati: Spasi langsung ke permainan
    M.stopMission(); M.STATE.started = false; C.played = false; M.startWithCine(); C.t = 12;
    window.dispatchEvent(new KeyboardEvent('keydown', { code: 'Space', key: ' ' }));
    out[`lewati (Spasi): sinematik ${C.on ? 'masih jalan' : 'berhenti'}, permainan mulai ${M.STATE.started}`] = !C.on && M.STATE.started && M.MIS.on;
    // keberangkatan: misi berhasil -> naik ke orbit, hasil baru tampil sesudah 14 s, Ulangi = misi baru tanpa sinematik kedatangan
    for (const S of M.MIS.sites) S.got = true; P.x = M.SHIP.door.x; P.z = M.SHIP.door.z; M.missionAction();
    Object.assign(M.FLY, { landed: false, spool: 1 }); M.FLY.y += 300;
    M.finishMission(true, 'lolos');
    const res = () => !document.getElementById('result').hidden;
    const early = res(); let t0 = 0; for (let k = 0; k < 150; k++) { M.cineStep(0.1); if (res() && !t0) t0 = C.t; }
    await wait(700); const hd = hdrCheck();
    document.getElementById('resAgain').click(); await wait(300);
    out[`keberangkatan: hasil tampil di awal ${early}, tampil pada ${t0.toFixed(1)} s (orbit, tidak valid ${hd.nb}); Ulangi -> sinematik ${C.on}, misi ${M.MIS.on}, terbang ${M.FLY.on}`] =
      !early && t0 >= 14 && t0 < 14.5 && hd.nb === 0 && !C.on && M.MIS.on && !M.FLY.on && M.STATE.started;
    // pandangan orbit dari panel: ditolak saat misi berjalan, jalan di Jelajah, tombol apa saja kembali
    M.startCine('orbit'); const refused = !C.on;
    M.stopMission(); M.setMode('jelajah'); M.STATE.started = true; M.startCine('orbit'); const onO = C.on && C.kind === 'orbit';
    await wait(600); const ho = hdrCheck();
    window.dispatchEvent(new KeyboardEvent('keydown', { code: 'KeyW', key: 'w' })); window.dispatchEvent(new KeyboardEvent('keyup', { code: 'KeyW', key: 'w' }));
    out[`pandangan orbit (panel): ditolak saat misi ${refused}, tampil di Jelajah ${onO} (tidak valid ${ho.nb}), tombol = kembali ${!C.on && M.STATE.started}`] = refused && onO && ho.nb === 0 && !C.on && M.STATE.started;
    M.CINE.enabled = false; M.flyReset(); P.x = 0; P.z = 0; P.y = M.seabed(0, 0) + M.CONFIG.eye; P.view = 0; M.keys.KeyW = false;
  }

  // 5l. Perbaikan: percikan kaki, arah miring wahana, bayangan dari cahaya Gargantua, gosong bergradasi
  {
    const P = M.P, V3 = M.THREE.Vector3, S = M.SPL;
    // percikan: satu langkah lari di air 0,5 m, butir naik setinggi lutut dan terlempar ke depan
    for (let k = 0; k < 200; k++) M.stepSplash(0.05);
    P.view = 0; P.x = 0; P.z = 0; P.depth = 0.5; P.yaw = 0; P.vx = 0; P.vz = -3; const y0 = M.seabed(0, 0) + 0.5;
    M.footstep(1.2, true); let n0 = 0; for (let i = 0; i < S.max; i++) if (S.life[i] > 0) n0++;
    let hMax = 0, fMax = 0; for (let k = 0; k < 40; k++) { M.stepSplash(1 / 60); for (let i = 0; i < S.max; i++) if (S.life[i] > 0) { hMax = Math.max(hMax, S.pos[i * 3 + 1] - y0); fMax = Math.max(fMax, -S.pos[i * 3 + 2]); } }
    P.vz = 0;
    out[`percikan kaki: ${n0} butir per langkah (dua kaki), tinggi ${hMax.toFixed(2)} m, terlempar ${fMax.toFixed(2)} m ke depan`] = n0 > 40 && hMax > 0.3 && fMax > 0.6;
    // arah miring: A = belok kiri dan sayap kiri turun (dulu miring ke kanan)
    M.setMode('jelajah'); M.STATE.started = true; M.stopMission();
    P.x = M.SHIP.door.x; P.z = M.SHIP.door.z; M.missionAction(); const FL = M.FLY;
    Object.assign(FL, { landed: false, spool: 1 }); FL.y += 20;
    const y0w = FL.yaw; M.keys.KeyW = true; for (let k = 0; k < 90; k++) M.updateFly(1 / 30);
    M.keys.KeyA = true; for (let k = 0; k < 45; k++) M.updateFly(1 / 30); M.keys.KeyA = false; M.keys.KeyW = false;
    M.SHIP.mesh.updateMatrixWorld(true);
    const L = M.SHIP.mesh.localToWorld(new V3(-5, 0, 1.3)), R = M.SHIP.mesh.localToWorld(new V3(5, 0, 1.3));
    out[`belok kiri (A): arah +${((FL.yaw - y0w) * 180 / Math.PI).toFixed(0)} derajat, miring ${(FL.roll * 180 / Math.PI).toFixed(1)} derajat, ujung sayap kiri ${(L.y - R.y).toFixed(2)} m dari kanan`] = FL.yaw > y0w + 0.3 && FL.roll > 0.05 && L.y < R.y - 0.3;
    M.flyReset();
    // bayangan: kamera menatap bayangan KS-07 di dasar laut; terang turun dibanding bayangan dimatikan
    M.BODY.level = 0;   // bayangan KS-07 diuji tanpa bayangan tubuh pemain (diuji di 5m)
    M.MOOD.brk = 1; const sy = M.seabed(M.SHIP.x, M.SHIP.z), h = M.SHIP.y + 0.3 - sy, G = M.THREE.Vector3;
    const gd = new V3(Math.cos(22 * Math.PI / 180) * Math.cos(28 * Math.PI / 180), Math.sin(22 * Math.PI / 180), -Math.cos(22 * Math.PI / 180) * Math.sin(28 * Math.PI / 180));
    const sx = M.SHIP.x - gd.x * h / gd.y, sz = M.SHIP.z - gd.z * h / gd.y;
    const gh = Math.hypot(gd.x, gd.z); P.x = sx - gd.x / gh * 4; P.z = sz - gd.z / gh * 4; P.y = M.seabed(P.x, P.z) + M.CONFIG.eye;   // 4 m dari bayangan, sudut curam (sudut landai: pantulan langit menutupi dasar)
    P.yaw = Math.atan2(-(sx - P.x), -(sz - P.z)); P.pitch = -Math.atan2(1.7, Math.hypot(sx - P.x, sz - P.z));
    const lumC = () => { const T = M.POST.hdr, w = T.width, hh = T.height, n = 24, b = new Uint16Array(n * n * 4); M.renderer.readRenderTargetPixels(T, (w - n) >> 1, (hh - n) >> 1, n, n, b);
      let l = 0; for (let k = 0; k < b.length; k += 4) l += 0.3 * M.THREE.DataUtils.fromHalfFloat(b[k]) + 0.59 * M.THREE.DataUtils.fromHalfFloat(b[k + 1]) + 0.11 * M.THREE.DataUtils.fromHalfFloat(b[k + 2]); return l / (n * n); };
    // kedua render di frame yang sama (dulu dua frame berbeda: buih dan ombak yang bergerak membuat hasil acak);
    // tunggu sampai kamera benar-benar di posisi pemain (frame SwiftShader bisa lebih dari 1 s)
    for (let w = 0; w < 60 && Math.hypot(M.camera.position.x - P.x, M.camera.position.z - P.z) > 0.3; w++) await wait(250); await wait(600); const rd = () => { M.updateShadow(); M.renderer.setRenderTarget(M.POST.hdr); M.renderer.clear(); M.renderer.render(M.scene, M.camera); return lumC(); };
    const l1 = rd(), k1 = M.U.uShK.value; M.makeShadow(0); const l0 = rd();
    M.makeShadow(M.SHD_SIZE[M.PRESET.idx]); await wait(300);
    out[`bayangan Gargantua: terang di bayangan KS-07 ${l1.toFixed(4)} vs tanpa bayangan ${l0.toFixed(4)} (${(100 * (1 - l1 / l0)).toFixed(0)}% lebih gelap, kuat ${k1.toFixed(2)}), peta ${M.SHD.size} px`] = M.SHD.size > 0 && k1 > 0 && l1 < l0 * 0.93;
    // gosong bergradasi di perut: hidung memutih pudar > tengah abu-abu > belakang jelaga
    const g = M.KS.geo, pa = g.attributes.position.array, na = g.attributes.normal.array, ca = g.attributes.color.array, acc = { nose: [0, 0], mid: [0, 0], rear: [0, 0] };
    for (let i = 0; i < pa.length; i += 3) { if (na[i + 1] > -0.95 || Math.abs(pa[i]) > 0.7) continue; const z = pa[i + 2], key = z < -4.8 ? 'nose' : z > -2.4 && z < -0.4 ? 'mid' : z > 0.6 && z < 2.4 ? 'rear' : null; if (!key) continue; acc[key][0] += (ca[i] + ca[i + 1] + ca[i + 2]) / 3; acc[key][1]++; }
    const lm = (k) => acc[k][0] / Math.max(1, acc[k][1]);
    out[`gosong perut bergradasi: hidung (putih pudar) ${lm('nose').toFixed(3)}, tengah (abu-abu) ${lm('mid').toFixed(3)}, hilir (jelaga) ${lm('rear').toFixed(3)}`] = lm('nose') > 0.3 && lm('nose') > lm('mid') && lm('mid') > lm('rear') && lm('rear') < 0.1;
    M.BODY.level = 2; P.x = 0; P.z = 0; P.y = M.seabed(0, 0) + M.CONFIG.eye; P.pitch = 0; P.yaw = -Math.PI / 2 + 0.3;
  }

  // 5m. M6a: tubuh astronaut orang pertama (low poly): anggaran, terlihat saat menunduk, tidak di horizon, lapisan kepala, mode tersembunyi
  {
    const P = M.P, B = M.BODY, snap = () => { const T = M.POST.hdr, w = T.width, h = T.height, b = new Uint16Array(w * h * 4); M.renderer.readRenderTargetPixels(T, 0, 0, w, h, b); return b; };
    const diff = (a, b) => { let n = 0; for (let k = 0; k < a.length; k += 4) if (Math.abs(a[k] - b[k]) + Math.abs(a[k + 1] - b[k + 1]) + Math.abs(a[k + 2] - b[k + 2]) > 40) n++; return 100 * n / (a.length / 4); };
    M.setMode('jelajah'); M.STATE.started = true; M.stopMission(); M.flyReset(); M.SWEEP.on = false;
    P.view = 0; P.x = 0; P.z = 0; P.y = M.seabed(0, 0) + M.CONFIG.eye; P.ground = true; P.yaw = -Math.PI / 2 + 0.3; M.MOOD.brk = 1;
    let bad = 0; for (const o of B.parts) for (const n of ['position', 'normal', 'color']) for (const v of o.geometry.attributes[n].array) if (!Number.isFinite(v)) bad++;
    out[`tubuh: ${B.tris} segitiga (detail ${B.detail}, <= ${[450, 1200, 3000][B.detail]}), ${B.parts.length} bagian, nilai tidak valid ${bad}`] = B.tris > 0 && B.tris <= [450, 1200, 3000][B.detail] && bad === 0;
    // dua gambar dalam satu tugas sinkron (waktu, ombak, kamera sama), hanya tingkat tubuh berbeda
    const shot = (lv) => { B.level = lv; M.camera.position.set(P.x, P.y, P.z); M.camera.rotation.set(P.pitch, P.yaw, 0); M.camera.updateMatrixWorld(true); M.U.uCam.value.copy(M.camera.position); M.updateShadow(); M.renderer.setRenderTarget(M.POST.hdr); M.renderer.clear(); M.renderer.render(M.scene, M.camera); M.renderer.setRenderTarget(null); return snap(); };
    const lumD = (a, b) => { let n = 0, l = 0; for (let k = 0; k < a.length; k += 4) if (Math.abs(a[k] - b[k]) + Math.abs(a[k + 1] - b[k + 1]) + Math.abs(a[k + 2] - b[k + 2]) > 40) { n++; l += 0.3 * M.THREE.DataUtils.fromHalfFloat(a[k]) + 0.59 * M.THREE.DataUtils.fromHalfFloat(a[k + 1]) + 0.11 * M.THREE.DataUtils.fromHalfFloat(a[k + 2]); } return n ? l / n : 0; };
    const inFrame = (o, dg = 0.95) => { const v = o.userData.c.clone(); o.localToWorld(v); v.project(M.camera); return Math.abs(v.x) < dg && Math.abs(v.y) < dg && v.z < 1; };
    const loc = (o) => { const v = o.userData.c.clone(); o.localToWorld(v); return B.group.worldToLocal(v); };
    P.pitch = -60 * Math.PI / 180; B.level = 2; M.updateBody(10); const dn1 = shot(2), limbsIn = B.feet.every((o) => inFrame(o)) && B.hands.every((o) => inFrame(o)), dn0 = shot(0);
    const lumB = lumD(dn1, dn0);
    P.pitch = 4 * Math.PI / 180; const hz1 = shot(2), hz0 = shot(0); B.level = 2;
    const dD = diff(dn1, dn0), dH = diff(hz1, hz0);
    out[`tubuh terlihat saat menunduk 60 derajat: ${dD.toFixed(2)}% piksel beda dari Mati (5-40%), terang rata-rata ${lumB.toFixed(3)} (> 0,12), di horizon ${dH.toFixed(2)}% (= 0)`] = dD > 5 && dD < 40 && lumB > 0.12 && dH === 0;
    out[`tubuh menunduk: kedua sepatu dan kedua tangan di dalam bingkai ${limbsIn}`] = limbsIn;
    // lari: kaki depan dan belakang berjauhan, tangan keluar ke sisi dan tetap di bingkai; udara: lengan terentang
    P.pitch = -50 * Math.PI / 180; M.BOB.run = 1; M.BOB.amp = 0.055; M.BOB.phase = 0; M.updateBody(10); shot(2);
    const fz = B.feet.map((o) => loc(o).z), hx = B.hands.map((o) => Math.abs(loc(o).x)), runVis = B.hands.some((o) => inFrame(o, 1.2));
    out[`lari: kaki beda z ${Math.abs(fz[0] - fz[1]).toFixed(2)} m (> 0,7), tangan keluar ${Math.min(...hx).toFixed(2)} m (> 0,30), salah satu di bingkai ${runVis}`] = Math.abs(fz[0] - fz[1]) > 0.7 && Math.min(...hx) > 0.30 && runVis;
    P.ground = false; M.BOB.run = 0; M.BOB.amp = 0; M.updateBody(10); shot(2); const ax = B.hands.map((o) => Math.abs(loc(o).x)); P.ground = true;
    out[`udara: lengan terentang, tangan ${Math.min(...ax).toFixed(2)} m dari sumbu (> 0,45)`] = Math.min(...ax) > 0.45;
    // pose halus: dari diam ke lari dalam 60 frame, tiap sendi berubah < 0,35 rad per frame
    M.BOB.run = 0; M.BOB.amp = 0; M.updateBody(10); let mxd = 0, prev = null;
    for (let f = 0; f < 90; f++) { M.BOB.run = 1; M.BOB.amp = 0.055; M.BOB.phase += 0.17; M.updateBody(1 / 60);
      const cur = [...B.legs, ...B.knees, ...B.ankles, ...B.arms, ...B.elbows].map((j) => j.rotation.x); if (prev) cur.forEach((v, i) => { mxd = Math.max(mxd, Math.abs(v - prev[i])); }); prev = cur; }
    out[`pose halus: perubahan sendi terbesar ${mxd.toFixed(3)} rad per frame (< 0,35), nilai tidak valid ${prev.some((v) => !Number.isFinite(v)) ? 'ada' : 'tidak'}`] = mxd < 0.35 && prev.every((v) => Number.isFinite(v));
    M.BOB.run = 0; M.BOB.amp = 0; M.BOB.phase = 0; M.updateBody(10);
    // FOV: naik saat lari, kembali tepat saat diam
    M.keys.KeyW = true; M.keys.ShiftLeft = true; await wait(3500); const fovRun = M.camera.fov; M.keys.KeyW = false; M.keys.ShiftLeft = false; for (let f = 0; f < 90; f++) M.stepPlayer(1 / 30); await wait(2500); const fov0 = M.camera.fov;
    out[`FOV lari ${fovRun.toFixed(2)} (> 70,5, <= ${70 + M.CONFIG.walk.fovRun}), diam ${fov0.toFixed(3)} (= 70)`] = fovRun > 70.5 && fovRun <= 70 + M.CONFIG.walk.fovRun + 0.01 && Math.abs(fov0 - 70) < 0.001;
    P.x = 0; P.z = 0; P.y = M.seabed(0, 0) + M.CONFIG.eye; P.pitch = -60 * Math.PI / 180; M.updateBody(10);
    // lapisan: kepala hanya bayangan (3) di orang pertama, ikut tampil (0) di drone; badan di 0 dan 3; Bayangan = semua hanya 3
    B.level = 2; P.view = 0; M.updateBody(); const h0 = B.head.layers.isEnabled(0), h3 = B.head.layers.isEnabled(3), b0 = B.parts[0].layers.isEnabled(0);
    P.view = 1; M.updateBody(); const h1 = B.head.layers.isEnabled(0); P.view = 0;
    B.level = 1; M.updateBody(); const s0 = B.parts[0].layers.isEnabled(0), s3 = B.parts[0].layers.isEnabled(3);
    out[`tubuh lapisan: kepala orang pertama 0=${h0} 3=${h3}, drone 0=${h1}, badan 0=${b0}, mode Bayangan 0=${s0} 3=${s3}`] = !h0 && h3 && h1 && b0 && !s0 && s3;
    // tersembunyi saat terbang, sinematik, tersapu, dan Mati
    B.level = 2; M.updateBody(); const vis = B.group.visible;
    M.FLY.on = true; M.updateBody(); const vf = B.group.visible; M.FLY.on = false;
    M.CINE.on = true; M.updateBody(); const vc = B.group.visible; M.CINE.on = false;
    M.SWEEP.on = true; M.updateBody(); const vs = B.group.visible; M.SWEEP.on = false;
    B.level = 0; M.updateBody(); const vm = B.group.visible; B.level = 2; M.updateBody();
    out[`tubuh tampil ${vis}, tersembunyi saat terbang ${!vf}, sinematik ${!vc}, tersapu ${!vs}, Mati ${!vm}`] = vis && !vf && !vc && !vs && !vm;
    // kaki di dasar laut dan ikut lompat; garis basah mengikuti muka air
    P.x = 5; P.z = 5; P.y = M.seabed(5, 5) + M.CONFIG.eye; M.updateBody(); const fy0 = B.group.position.y - M.seabed(5, 5);
    P.y += 1.2; M.updateBody(); const fy1 = B.group.position.y - M.seabed(5, 5); P.y -= 1.2; M.updateBody();
    out[`tubuh: telapak di dasar laut ${fy0.toFixed(3)} m, ikut lompat ${fy1.toFixed(3)} m, uWater ${M.bodyMat.uniforms.uWater.value.toFixed(2)} = muka air ${M.waterHere(M.STATE.visT).toFixed(2)}`] = Math.abs(fy0) < 0.01 && Math.abs(fy1 - 1.2) < 0.01 && Math.abs(M.bodyMat.uniforms.uWater.value - M.waterHere(M.STATE.visT)) < 0.01;
    // panel: baris Tubuh di akhir, gerak kepala tetap indeks 4, siklus tersimpan
    const n = M.LAB.length, lv = B.level; M.cycleBody(); const lv1 = B.level, sv = localStorage.getItem('millar.body'); B.level = lv; M.cycleBody(); M.cycleBody(); M.cycleBody();
    out[`panel Tubuh: baris ke-${n} dari ${n}, siklus ${lv} -> ${lv1}, tersimpan ${sv}, gerak kepala tetap indeks 4`] = M.LAB[n - 1][1]().includes('Tubuh') && M.LAB[4][1]().includes('Gerak kepala') && lv1 === (lv + 1) % 3 && sv === String(lv1) && B.level === lv;
    P.x = 0; P.z = 0; P.y = M.seabed(0, 0) + M.CONFIG.eye; P.pitch = 0; P.yaw = -Math.PI / 2 + 0.3;
  }

  // 5m. M5d: plasma masuk atmosfer mengikuti bentuk wahana (bukan bola); perut yang menghadap aliran paling terang
  {
    const C = M.CINE, hdr = (n) => { const T = M.POST.hdr, w = T.width, h = T.height, b = new Uint16Array(n * n * 4); M.renderer.readRenderTargetPixels(T, (w - n) >> 1, (h - n) >> 1, n, n, b);
      let l = 0, nb = 0; for (let k = 0; k < b.length; k += 4) { const r = M.THREE.DataUtils.fromHalfFloat(b[k]), g = M.THREE.DataUtils.fromHalfFloat(b[k + 1]), bl = M.THREE.DataUtils.fromHalfFloat(b[k + 2]); if (!Number.isFinite(r + g + bl)) nb++; else l += 0.3 * r + 0.59 * g + 0.11 * bl; } return { l: l / (n * n), nb }; };
    let spheres = 0; M.ORB.plasma.traverse((o) => { if (o.geometry && o.geometry.type === 'SphereGeometry') spheres++; });
    M.CINE.enabled = true; M.CINE.played = false; M.STATE.started = false; M.setMode('jelajah'); M.startWithCine(); C.t = 17; await wait(900);
    const shot = (el) => { M.cineStep(0); M.orbShipCam(0.03, Math.PI * 0.55, el, 0); M.renderOrbit(performance.now()); return hdr(20); };
    const below = shot(-0.9), above = shot(0.9), full = (() => { const T = M.POST.hdr, b = new Uint16Array(T.width * T.height * 4); M.renderer.readRenderTargetPixels(T, 0, 0, T.width, T.height, b); let nb = 0; for (const x of b) if (!Number.isFinite(M.THREE.DataUtils.fromHalfFloat(x))) nb++; return nb; })();
    M.cineStop(); M.CINE.enabled = false; M.STATE.started = true;
    out[`plasma masuk atmosfer: bola di grup plasma ${spheres}, terang dilihat dari bawah (perut) ${below.l.toFixed(3)} vs dari atas ${above.l.toFixed(3)}, tidak valid ${below.nb + above.nb + full}`] =
      spheres === 0 && below.l > above.l * 1.3 && below.nb + above.nb + full === 0 && M.ORB_U.uFlowL.value.y < -0.3;
  }

  // 5n. M5a-2: laut dari ketinggian tidak berulang tiap petak FFT (korelasi pada geser 37 m turun), tanpa nilai tidak valid
  {
    const P = M.P; M.applyPreset(1); await wait(1500); M.flyReset(); P.view = 1; P.x = 300; P.z = -200; P.yaw = 0; P.pitch = -Math.PI / 2 + 0.002; M.MOOD.brk = 0;
    const corr = async (k) => {
      M.U.uMacroK.value = k; M.CONFIG.views[1].h = 120; P.y = 120;                       // 120 m: seluruh layar di luar laut dekat
      for (let w = 0; w < 80 && Math.abs(M.camera.position.y - 120) > 2; w++) await wait(250); await wait(1200);
      const T = M.POST.hdr, w = T.width, h = T.height, b = new Uint16Array(w * h * 4); M.renderer.readRenderTargetPixels(T, 0, 0, w, h, b);
      const L0i = new Float32Array(w * h); let nb = 0; for (let i = 0; i < w * h; i++) { const r = M.THREE.DataUtils.fromHalfFloat(b[i * 4]), g = M.THREE.DataUtils.fromHalfFloat(b[i * 4 + 1]); if (!Number.isFinite(r + g)) { nb++; continue; } L0i[i] = 0.4 * r + 0.6 * g; }
      // high-pass: kurangi rata-rata lokal 13 x 13 px (gradasi pantulan langit tidak ikut dihitung sebagai pola)
      const I = new Float64Array((w + 1) * (h + 1)); for (let y = 0; y < h; y++) { let rs = 0; for (let x = 0; x < w; x++) { rs += L0i[y * w + x]; I[(y + 1) * (w + 1) + x + 1] = I[y * (w + 1) + x + 1] + rs; } }
      const L = new Float32Array(w * h), R = 6; for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const x0 = Math.max(0, x - R), x1 = Math.min(w, x + R + 1), y0 = Math.max(0, y - R), y1 = Math.min(h, y + R + 1);
        const sm = I[y1 * (w + 1) + x1] - I[y0 * (w + 1) + x1] - I[y1 * (w + 1) + x0] + I[y0 * (w + 1) + x0]; L[y * w + x] = L0i[y * w + x] - sm / ((x1 - x0) * (y1 - y0)); }
      const hgt = M.camera.position.y - M.drawdown(M.camera.position.x - M.frontX(M.camera.position.z)), mpp = 2 * hgt * Math.tan(M.camera.fov * Math.PI / 360) / h;
      const L0 = M.OCEAN.casc[0] ? M.OCEAN.casc[0].L : 37, dx = Math.round(L0 / mpp);
      let sa = 0, sb = 0, saa = 0, sbb = 0, sab = 0, n = 0;
      for (let y = Math.round(h * 0.2); y < h * 0.8; y++) for (let x = Math.round(w * 0.1); x + dx < w * 0.9; x++) { const a = L[y * w + x], c = L[y * w + x + dx]; sa += a; sb += c; saa += a * a; sbb += c * c; sab += a * c; n++; }
      const cv = sab / n - (sa / n) * (sb / n), va = saa / n - (sa / n) ** 2, vb = sbb / n - (sb / n) ** 2;
      return { r: cv / Math.sqrt(Math.max(va * vb, 1e-20)), nb, dx, hgt };
    };
    const off = await corr(0), on = await corr(1);
    M.CONFIG.views[1].h = 60; P.view = 0; P.x = 0; P.z = 0; P.y = M.seabed(0, 0) + M.CONFIG.eye; P.pitch = 0;
    out[`laut dari ${off.hgt.toFixed(0)} m: korelasi pada geser satu petak FFT (${on.dx} px) ${off.r.toFixed(3)} -> ${on.r.toFixed(3)} dengan variasi makro, tidak valid ${off.nb + on.nb}`] =
      on.r < off.r * 0.7 && on.nb === 0 && off.nb === 0 && M.U.uMacroK.value === 1;
  }

  // 5o. M5c: percikan lari menyatu dengan laut: semburan tidak terlempar jauh ke depan kaki, tonjolan haluan di depan tulang
  //     kering dan cekung di belakang, buih jejak, mahkota air tampil lalu hilang, render tanpa nilai tidak valid
  {
    const P = M.P, S = M.SPL, R = M.RIP, from = M.THREE.DataUtils.fromHalfFloat;
    for (let k = 0; k < 200; k++) M.stepSplash(0.05);
    M.makeRipple(M.PRESETS[M.PRESET.idx]);   // grid riak kosong: sisa riak uji lari sebelumnya bisa jenuh di batas +-0,2 m (pernah gagal -200 mm)
    P.view = 0; P.x = 0; P.z = 0; P.depth = 0.5; P.yaw = 0; P.vx = 0; P.vz = -3; P.ground = true; M.updateBody(10);
    const fw = Math.max(...[-1, 1].map((sd) => -M.bodyFootAt(sd).z));   // M6b: percikan keluar dari sepatu yang terlihat
    M.footstep(1.2, true); let fRel = 0, t = 0, nb = 0;
    for (let k = 0; k < 50; k++) { M.stepSplash(1 / 60); t += 1 / 60; for (let i = 0; i < S.max; i++) if (S.life[i] > 0) fRel = Math.max(fRel, -(S.pos[i * 3 + 2] + fw + 3 * t)); }
    const up = M.CROWN.slots.filter((q) => q.t < 1).length; let tc = 0;
    for (let k = 0; k < 120 && M.CROWN.slots.some((q) => q.t < 1); k++) { M.stepCrown(1 / 60); tc += 1 / 60; }
    // tonjolan dan cekung: kaki tetap di tempat, kaki terus mendorong air selama 0,25 s
    for (let i = 0; i < 90; i++) M.updateRipple(1 / 60);
    const ph = M.BOB.phase; for (let k = 0; k < 15; k++) { M.BOB.phase = ph; M.headBob(1 / 60, 3, true, 0.5); M.updateRipple(1 / 60); }
    const N = R.N, b = new Uint16Array(N * N * 4); M.renderer.readRenderTargetPixels(R.rt[R.i], 0, 0, N, N, b);
    const at = (x, z, c) => { const i = Math.round((x - R.ox) / R.dx + N / 2 - 0.5), j = Math.round((z - R.oz) / R.dx + N / 2 - 0.5); return from(b[(j * N + i) * 4 + c]); };
    const Lg = M.bodyLegAt(1, 0.5), lx = Lg.x, hF = at(lx, Lg.z - 0.14, 0), hB = at(lx, Lg.z + 0.12, 0), fB = at(lx, Lg.z + 0.12, 2);   // M6b: kaki yang terlihat memotong muka air
    // render dengan mahkota tampil
    P.vz = 0; P.pitch = -1.0; M.footstep(1.2, true); for (let k = 0; k < 10; k++) M.stepCrown(1 / 60);
    M.renderer.setRenderTarget(M.POST.hdr); M.renderer.clear(); M.renderer.render(M.scene, M.camera);
    { const T = M.POST.hdr, bb = new Uint16Array(T.width * T.height * 4); M.renderer.readRenderTargetPixels(T, 0, 0, T.width, T.height, bb); for (const x of bb) if (!Number.isFinite(from(x))) nb++; }
    P.pitch = 0;
    out[`percikan menyatu (M5c): semburan paling jauh ${fRel.toFixed(2)} m di depan kaki (lari 3 m/s), tonjolan depan ${(hF * 1000).toFixed(1)} mm / cekung belakang ${(hB * 1000).toFixed(1)} mm, buih jejak ${fB.toFixed(2)}, mahkota ${up} tampil lalu hilang ${tc.toFixed(2)} s, tidak valid ${nb}`] =
      fRel < 1.2 && hF > 0 && hB < hF && fB > 0.05 && up === 2 && tc < 0.8 && nb === 0;
  }

  // 5p. M5e: penampang gelombang raksasa = tembok tebal: profil JS = GLSL (50 titik di GPU), muka atas hampir tegak,
  //     lebar badan pada setengah tinggi 0,8-2,5 km, punggung turun ke sekitar 20% dalam 1,5-2,5 km
  {
    const T3 = M.THREE, n = 50, u0 = -1500, u1 = 3500, uAt = (i) => u0 + (u1 - u0) * i / (n - 1);
    const rt = new T3.WebGLRenderTarget(n, 1, { type: T3.FloatType, depthBuffer: false });
    const mat = new T3.ShaderMaterial({ defines: { NW: 1, NM: 1 }, vertexShader: 'void main() { gl_Position = vec4(position.xy, 0.0, 1.0); }',
      fragmentShader: M.COMMON + `void main() { float u = ${u0.toFixed(1)} + ${(u1 - u0).toFixed(1)} * (gl_FragCoord.x - 0.5) / ${(n - 1).toFixed(1)}; gl_FragColor = vec4(waveG(u), 0.0, 0.0, 1.0); }` });
    const sc = new T3.Scene(), q = new T3.Mesh(new T3.PlaneGeometry(2, 2), mat); q.frustumCulled = false; sc.add(q);
    M.renderer.setRenderTarget(rt); M.renderer.render(sc, new T3.OrthographicCamera(-1, 1, 1, -1, 0, 1));
    const px = new Float32Array(n * 4); M.renderer.readRenderTargetPixels(rt, 0, 0, n, 1, px); M.renderer.setRenderTarget(null); rt.dispose(); mat.dispose();
    let dMax = 0; for (let i = 0; i < n; i++) dMax = Math.max(dMax, Math.abs(px[i * 4] - M.waveG(uAt(i))) * M.CONFIG.wave.H);
    // muka atas: kemiringan rata-rata antara 1/3 dan 0,9 tinggi, di bagian gelombang terendah (0,82 H)
    const G = M.waveG; let ua = 0, ub = 0; for (let u = -2000; u < 0; u += 0.1) { if (!ua && G(u) >= 1 / 3) ua = u; if (!ub && G(u) >= 0.9) ub = u; }
    const slope = Math.atan(M.CONFIG.wave.H * 0.82 * (0.9 - 1 / 3) / (ub - ua)) * 180 / Math.PI;
    let wa = null, wb = 0; for (let u = -2000; u < 8000; u += 1) if (G(u) >= 0.5) { if (wa === null) wa = u; wb = u; }
    let u20 = 0; for (let u = 0; u < 8000; u += 5) if (G(u) <= 0.22) { u20 = u; break; }
    out[`gelombang tembok (M5e): profil JS = GLSL selisih ${dMax.toFixed(3)} m (${n} titik), muka atas ${slope.toFixed(1)} derajat, lebar setengah tinggi ${((wb - wa) / 1000).toFixed(2)} km, punggung 22% di ${(u20 / 1000).toFixed(2)} km`] =
      dMax < 0.5 && slope > 75 && wb - wa > 800 && wb - wa < 2500 && u20 > 1500 && u20 < 2500;
  }

  // 5n. M6b: percikan dan riak keluar dari sepatu yang terlihat, fase langkah sinkron, yaw badan tertinggal
  {
    const P = M.P, B = M.BODY, Q = B.pose, PI = Math.PI;
    M.setMode('jelajah'); M.STATE.started = true; M.stopMission(); M.flyReset(); M.SWEEP.on = false; M.CINE.on = false;
    P.view = 0; P.x = 3; P.z = 3; P.y = M.seabed(3, 3) + M.CONFIG.eye; P.ground = true; P.yaw = 0.7; B.level = 2;
    // telapak: bodyFootAt() = pusat mesh sepatu (bidang air), 6 fase x menunduk / tegak x 2 kaki
    let maxd = 0;
    for (const dnv of [0, 1]) for (const ph of [0.3, 1.1, 2.0, 2.9, 3.8, 5.0]) {
      P.pitch = dnv ? -60 * PI / 180 : 0; M.BOB.amp = 0.034; M.BOB.run = 0; M.BOB.phase = ph; M.updateBody(10); B.group.updateMatrixWorld(true);
      for (const sd of [-1, 1]) { const F = M.bodyFootAt(sd), o = B.feet[sd < 0 ? 0 : 1], v = o.userData.c.clone(); o.localToWorld(v); maxd = Math.max(maxd, Math.hypot(v.x - F.x, v.z - F.z)); }
    }
    out[`percikan dari sepatu: bodyFootAt dekat pusat sepatu, selisih terbesar ${maxd.toFixed(3)} m (< 0,08)`] = maxd < 0.08;
    // fase: kaki yang menapak saat headBob melewati kelipatan pi = kaki terdepan, 6 persilangan berturut-turut, juga di air dangkal dan setelah mendarat
    P.pitch = 0; M.BOB.phase = 0.01; M.BOB.side = 0; M.BOB.amp = 0.034; Q.mv = 1; let ok = 0, tot = 0, goal = 0;
    const walkSteps = (depth, n) => { P.depth = depth; goal += n; for (let f = 0; f < 400 && tot < goal; f++) {
      const sp = M.BOB.side, n0 = M.BOB.steps; Q.mv = 1; M.headBob(1 / 60, 1.4, false, depth);
      if (M.BOB.steps !== n0) { const L = M.bodyLegs(); tot++; if ((L.sw[1] > L.sw[0] ? 1 : -1) === (sp ? 1 : -1)) ok++; } } };
    walkSteps(0.5, 4);
    const s0 = M.BOB.side, n0 = M.BOB.steps; P.depth = 0.5; M.footstep(1.2, true);
    out[`mendarat: BOB.side ${s0} -> ${M.BOB.side} (tetap), langkah ${n0} -> ${M.BOB.steps}`] = M.BOB.side === s0 && M.BOB.steps === n0 + 1;
    walkSteps(0.5, 4); walkSteps(0.02, 4);
    out[`fase langkah: kaki yang menapak = kaki terdepan ${ok}/${tot} persilangan (air dalam, setelah mendarat, air dangkal)`] = tot === 12 && ok === tot;
    // jangkauan telapak saat menapak: jalan dan lari
    const reach = (run) => { P.pitch = 0; M.BOB.run = run; M.BOB.amp = run ? 0.055 : 0.034; M.BOB.phase = PI; Q.mv = 1; M.updateBody(10);
      const F = M.bodyFootAt(-1), by = B.yaw; return -(F.x - P.x) * Math.sin(by) - (F.z - P.z) * Math.cos(by); };
    const rw = reach(0), rr = reach(1);
    out[`jangkauan telapak: jalan ${rw.toFixed(3)} m (pinggul 0,04 + 0,25 + ujung 0,07), lari ${rr.toFixed(3)} m (0,04 + 0,40 + 0,07)`] = Math.abs(rw - 0.36) < 0.04 && Math.abs(rr - 0.51) < 0.04;
    M.BOB.run = 0; M.BOB.amp = 0; M.BOB.phase = 0; Q.mv = 0; M.updateBody(10);
    // titik kaki memotong muka air: di antara telapak dan pinggul, 0,5/0,9 dari telapak
    const F = M.bodyFootAt(1), G = M.bodyLegAt(1, 0.45), H = M.bodyLegAt(1, 0), Hh = M.bodyLegAt(1, 5);
    const tt = Math.hypot(G.x - F.x, G.z - F.z) / Math.max(1e-6, Math.hypot(Hh.x - F.x, Hh.z - F.z));
    out[`titik kaki di air: pada ${(100 * tt).toFixed(1)}% dari telapak ke pinggul (kedalaman 0,45 dari 0,9 = 50%), kedalaman 0 = telapak ${Math.hypot(H.x - F.x, H.z - F.z) < 1e-6}`] = Math.abs(tt - 0.5) < 0.03 && Math.hypot(H.x - F.x, H.z - F.z) < 1e-6;
    // yaw tertinggal: belok mendadak 1,5 rad, tertinggal 0,3-0,44 rad, lalu menyusul
    P.yaw = 0.7; M.updateBody(10); P.yaw += 1.5; M.updateBody(1 / 60); const lag0 = Math.abs(P.yaw - B.yaw), rot = B.group.rotation.y === B.yaw;
    for (let f = 0; f < 90; f++) M.updateBody(1 / 60); const lag1 = Math.abs(P.yaw - B.yaw);
    out[`yaw badan tertinggal ${lag0.toFixed(2)} rad (0,3-0,44), menyusul ${lag1.toFixed(3)} rad dalam 1,5 s (< 0,05), rotasi kelompok = BODY.yaw ${rot}`] = lag0 > 0.3 && lag0 <= 0.44 + 1e-6 && lag1 < 0.05 && rot;
    // pose dihitung walau tubuh Mati: posisi telapak tidak melompat saat panel diubah
    B.level = 0; P.pitch = -60 * PI / 180; M.updateBody(10); const Fm = M.bodyFootAt(1); B.level = 2; M.updateBody(10); const Fv = M.bodyFootAt(1);
    out[`pose tetap dihitung saat tubuh Mati: selisih telapak ${Math.hypot(Fm.x - Fv.x, Fm.z - Fv.z).toFixed(4)} m`] = Math.hypot(Fm.x - Fv.x, Fm.z - Fv.z) < 1e-6;
    P.depth = 0; P.x = 0; P.z = 0; P.y = M.seabed(0, 0) + M.CONFIG.eye; P.pitch = 0; P.yaw = -PI / 2 + 0.3; P.ground = true; M.updateBody(10);
  }

  // 5r. M6d-2: sudut pandang tubuh: bahu dan tutup badan di luar pandangan saat menunduk, badan atas kaku terhadap kepala, telapak menapak (IK)
  {
    const P = M.P, B = M.BODY, PI = Math.PI, V3 = M.THREE.Vector3, cam = M.camera, lv0 = M.BOB.level;
    M.setMode('jelajah'); M.STATE.started = true; M.stopMission(); M.flyReset(); M.SWEEP.on = false; M.CINE.on = false;
    P.view = 0; P.x = 3; P.z = 3; P.y = M.seabed(3, 3) + M.CONFIG.eye; P.ground = true; P.yaw = 0.7; P.depth = 0.5; B.level = 2;
    Object.assign(M.BOB, { shX: 0, shY: 0, y: 0, vy: 0, run: 0, amp: 0 });
    const pts = () => [...B.arms.map((o) => o.getWorldPosition(new V3())), ...[[0.21, 0.47, 0.12], [-0.21, 0.47, 0.12], [0, 0.47, 0.24]].map((q) => B.torso.localToWorld(new V3(...q)))];
    // speed 0 = diam; n frame, 60 pertama untuk menetap
    const walk = (speed, run, pitch, lv, n = 150) => {
      M.BOB.level = lv; P.pitch = pitch; const r = { rel: [[1e9, -1e9], [1e9, -1e9], [1e9, -1e9]], solMin: 1e9, lowMax: -1e9, seen: 0, ndcY: -9, dyStep: [], dyMin: 0, bad: 0 };
      for (let f = 0; f < n; f++) {
        const n0 = M.BOB.steps; M.headBob(1 / 60, speed, run, 0.5); M.fpCamera(); cam.updateMatrixWorld(true); M.updateBody(1 / 60); B.group.updateMatrixWorld(true);
        if (f < 60) continue;
        const t = B.torso.getWorldPosition(new V3()).sub(cam.position), c = Math.cos(P.yaw), s = Math.sin(P.yaw), loc = [t.x * c - t.z * s, t.y, t.x * s + t.z * c];
        loc.forEach((v, k) => { r.rel[k][0] = Math.min(r.rel[k][0], v); r.rel[k][1] = Math.max(r.rel[k][1], v); });
        const so = B.ankles.map((o) => o.getWorldPosition(new V3()).y - 0.05 - B.group.position.y);
        r.solMin = Math.min(r.solMin, ...so); r.lowMax = Math.max(r.lowMax, Math.min(...so));
        for (const q of pts()) { q.project(cam); if (q.z > -1 && q.z < 1 && Math.abs(q.x) <= 1) { r.ndcY = Math.max(r.ndcY, q.y); if (q.y >= -1) r.seen++; } }
        if (M.BOB.steps !== n0) r.dyStep.push(M.BOB.dy); r.dyMin = Math.min(r.dyMin, M.BOB.dy);
        for (const j of [...B.legs, ...B.knees, ...B.ankles, B.torso]) for (const v of [j.rotation.x, j.position.y]) if (!Number.isFinite(v)) r.bad++;
      }
      return r;
    };
    let seen = 0, ndcY = -9, bad = 0;
    for (const pitch of [-0.9, -1.2, -1.45]) for (const [sp, rn] of [[0, false], [1.4, false], [3.0, true]]) { const r = walk(sp, rn, pitch, 2, 100); seen += r.seen; ndcY = Math.max(ndcY, r.ndcY); bad += r.bad; }
    out[`bahu tersembunyi saat menunduk (pitch -0,9/-1,2/-1,45 x diam/jalan/lari): titik terlihat ${seen}, ndc.y tertinggi ${ndcY.toFixed(2)} (< -1)`] = seen === 0;
    const span = (r) => Math.max(...r.rel.map(([a, b]) => b - a)) * 1000;
    const rows = [], sol = [];
    for (const lv of [2, 1, 0]) for (const [sp, rn] of [[1.4, false], [3.0, true]]) { const r = walk(sp, rn, -1.0, lv); rows.push(span(r)); sol.push([r.solMin, r.lowMax]); bad += r.bad;
      if (lv === 2 && !rn) { const rw = r; out[`gerak kepala terdalam saat kaki menapak: BOB.dy saat langkah ${rw.dyStep.length ? (Math.max(...rw.dyStep) * 1000).toFixed(1) : '-'} mm, minimum ${(rw.dyMin * 1000).toFixed(1)} mm`] = rw.dyStep.length >= 2 && Math.max(...rw.dyStep) <= 0.9 * rw.dyMin; } }
    out[`badan atas kaku terhadap kepala (jalan/lari x Normal/Halus/Mati): pergeseran terbesar ${Math.max(...rows).toFixed(2)} mm (< 3)`] = Math.max(...rows) < 3;
    const sMin = Math.min(...sol.map((x) => x[0])), lMax = Math.max(...sol.map((x) => x[1]));
    out[`telapak menapak (IK): telapak terendah tiap frame ${(lMax * 1000).toFixed(1)} mm dari dasar (< 15), tidak ada di bawah ${(sMin * 1000).toFixed(1)} mm (> -15), nilai tidak valid ${bad}`] = lMax < 0.015 && sMin > -0.015 && bad === 0;
    // pitch 0, diam: kamera tepat di posisi pemain (leher 0)
    Object.assign(M.BOB, { level: lv0, run: 0, amp: 0, phase: 0, y: 0, vy: 0, dy: 0, dx: 0, roll: 0, shX: 0, shY: 0 }); P.pitch = 0; M.fpCamera();
    const d0 = Math.hypot(cam.position.x - P.x, cam.position.y - P.y, cam.position.z - P.z);
    out[`pitch 0 diam: kamera = posisi pemain, selisih ${d0.toExponential(1)} m`] = d0 < 1e-9;
    P.depth = 0; P.x = 0; P.z = 0; P.y = M.seabed(0, 0) + M.CONFIG.eye; P.yaw = -PI / 2 + 0.3; P.ground = true; M.updateBody(10);
  }

  // 5s. M6e: tingkat detail tubuh (segitiga per tingkat, nilai valid), kotor di bawah, biaya updateBody, pilot di kokpit (tangan di tongkat dan tuas),
  //     tangan menjangkau barang misi saat tahan E
  {
    const P = M.P, B = M.BODY, V3 = M.THREE.Vector3, cam = M.camera, d0 = B.detail, lim = [450, 1200, 3000], tr = [];
    let bad = 0;
    for (const d of [0, 1, 2]) { M.setBodyDetail(d); tr.push(B.tris); for (const o of B.parts) for (const n of ['position', 'normal', 'color']) for (const v of o.geometry.attributes[n].array) if (!Number.isFinite(v)) bad++; }
    out[`tubuh per tingkat detail: ${tr.join(' / ')} segitiga (<= 450 / 1.200 / 3.000), ${B.parts.length} bagian, nilai tidak valid ${bad}, preset -> detail ${M.BODY_DETAIL.join(',')}`] =
      tr.every((n, i) => n > 0 && n <= lim[i]) && tr[0] < tr[1] && tr[1] < tr[2] && bad === 0 && B.parts.length === 7 && M.BODY_DETAIL.join() === '2,2,2,1,0';
    M.setBodyDetail(d0);
    // kotor: rata-rata terang warna titik sepatu dibanding badan
    // pakaian (pose ikat): titik di bawah 0,35 m (betis) dibanding di atas 1,1 m (dada, lengan atas)
    const sg = B.suit.geometry, sc = sg.attributes.color.array, sp = sg.userData.skin.p0; let lo = 0, nlo = 0, hi = 0, nhi = 0;
    for (let k = 0; k < sc.length; k += 3) { const l = 0.3 * sc[k] + 0.59 * sc[k + 1] + 0.11 * sc[k + 2]; if (sp[k + 1] < 0.35) { lo += l; nlo++; } else if (sp[k + 1] > 1.1) { hi += l; nhi++; } }
    const kf = lo / Math.max(1, nlo), kl = hi / Math.max(1, nhi);
    out[`kotor: betis ${kf.toFixed(3)} lebih gelap dari dada ${kl.toFixed(3)} (rasio ${(kf / kl).toFixed(2)} < 0,8)`] = nlo > 0 && kf / kl < 0.8;
    // biaya: updateBody rata-rata 600 panggilan saat berjalan
    M.setMode('jelajah'); M.STATE.started = true; M.stopMission(); M.flyReset(); M.SWEEP.on = false; M.CINE.on = false;
    P.view = 0; P.x = 3; P.z = 3; P.y = M.seabed(3, 3) + M.CONFIG.eye; P.ground = true; P.pitch = -1.0; B.level = 2; M.BOB.amp = 0.034; M.BOB.run = 0;
    let t0 = performance.now(); for (let f = 0; f < 600; f++) { M.BOB.phase += 0.1; M.updateBody(1 / 60); } const ms = (performance.now() - t0) / 600;
    out[`biaya updateBody: ${ms.toFixed(4)} ms rata-rata (600 frame, < 0,1)`] = ms < 0.1;
    // pilot di kokpit
    M.boardShip(); M.FLY.view = 1; M.flyCamera(); cam.updateMatrixWorld(true); M.updateBody(1 / 60); B.group.updateMatrixWorld(true);
    const hw = (o) => { const v = o.userData.c.clone(); return o.localToWorld(v); };
    const gS = M.COCKPIT.stick.localToWorld(new V3(0, 0.21, 0.01)), gT = M.COCKPIT.throttle.localToWorld(new V3(0.02, 0.15, 0));
    const glove = (i) => B.elbows[i].localToWorld(new V3(0, -0.33, -0.02)), eS = glove(1).distanceTo(gS), eT = glove(0).distanceTo(gT), eye = B.group.localToWorld(new V3(0, M.CONFIG.eye, 0)).distanceTo(cam.position);
    M.FLY.lookP = -0.7; M.flyCamera(); cam.updateMatrixWorld(true); M.updateBody(1 / 60); B.group.updateMatrixWorld(true);
    // kokpit lebar: tangan di konsol samping, terlihat saat menoleh ke sisinya (lutut terlihat saat menunduk lurus)
    const inFr = (v) => { v.project(cam); return Math.abs(v.x) < 1 && Math.abs(v.y) < 1 && v.z < 1; }, kneeIn = B.knees.every((o) => inFr(o.getWorldPosition(new V3())));
    const handIn = (i) => [-1.1, -0.7, 0.7, 1.1].some((ly) => { M.FLY.lookY = ly; M.flyCamera(); cam.updateMatrixWorld(true); return inFr(hw(B.hands[i])); });
    const inF = kneeIn && handIn(0) && handIn(1); M.FLY.lookY = 0; M.flyCamera(); cam.updateMatrixWorld(true);
    const seatVis = B.group.visible && B.seat;
    // render kokpit HDR: tanpa nilai tidak valid atau titik menyala
    const r = M.renderer, T = M.POST.hdr, w = T.width, h = T.height, buf = new Uint16Array(w * h * 4), from = M.THREE.DataUtils.fromHalfFloat; let nb = 0, nh = 0;
    M.U.uCam.value.copy(cam.position);
    M.updateShadow(); r.setRenderTarget(T); r.clear(); r.render(M.scene, cam); r.setRenderTarget(null); r.readRenderTargetPixels(T, 0, 0, w, h, buf);
    for (let k = 0; k < buf.length; k += 4) for (let c = 0; c < 3; c++) { const x = from(buf[k + c]); if (!Number.isFinite(x)) nb++; else if (x > 50) nh++; }
    M.FLY.view = 0; M.flyCamera(); M.updateBody(1 / 60); const rearHidden = !B.group.visible;
    out[`pilot di kokpit: tangan kanan ${(eS * 100).toFixed(1)} cm dari tongkat, kiri ${(eT * 100).toFixed(1)} cm dari tuas (< 4), mata ${(eye * 100).toFixed(2)} cm dari kamera, lutut dan tangan (menoleh) di bingkai ${inF}, render tidak valid ${nb} / menyala ${nh}, tampilan belakang tersembunyi ${rearHidden}`] =
      seatVis && eS < 0.04 && eT < 0.04 && eye < 0.01 && inF && nb === 0 && nh === 0 && rearHidden;
    M.flyReset(); M.updateBody(10);
    // tahan E: tangan kanan menuju barang
    const wx0 = M.U.uWX.value, ck0 = M.U.uChopK.value;   // startMission memindah gelombang dan keadaan laut: dikembalikan setelahnya
    M.setMode('misi'); M.setLevel(1); M.startMission(); const S = M.MIS.sites[0]; P.x = S.ix + 0.6; P.z = S.iz; P.y = M.seabed(P.x, P.z) + M.CONFIG.eye; P.yaw = Math.PI / 2; P.pitch = -0.6; M.updateBody(10);
    const it = S.item.getWorldPosition(new V3()), d1 = hw(B.hands[1]).distanceTo(it);
    M.MIS.near = 0; M.MIS.hold = 0.5; for (let f = 0; f < 30; f++) M.updateBody(1 / 60); const d2 = hw(B.hands[1]).distanceTo(it), dl = hw(B.hands[0]).distanceTo(it);
    M.MIS.hold = 0; for (let f = 0; f < 60; f++) M.updateBody(1 / 60); const d3 = hw(B.hands[1]).distanceTo(it);
    out[`ambil barang: tangan kanan ${d1.toFixed(2)} -> ${d2.toFixed(2)} m dari barang saat tahan E (lebih dekat 30%), kembali ${d3.toFixed(2)} m saat dilepas`] = d2 < 0.7 * d1 && Math.abs(d3 - d1) < 0.03;
    M.stopMission(); M.setMode('jelajah'); M.U.uWX.value = wx0; M.U.uChopK.value = ck0;
    P.depth = 0; P.x = 0; P.z = 0; P.y = M.seabed(0, 0) + M.CONFIG.eye; P.pitch = 0; P.yaw = -Math.PI / 2 + 0.3; P.ground = true; M.updateBody(10);
  }

  // 5t. M6f: pakaian satu mesh berkulit: kulit = tulang, tidak robek atau mengempis saat lari / duduk / menjangkau, tanpa nilai tidak valid
  {
    const P = M.P, B = M.BODY, V3 = M.THREE.Vector3, d0 = B.detail;
    M.setMode('jelajah'); M.STATE.started = true; M.stopMission(); M.flyReset(); M.SWEEP.on = false; M.CINE.on = false;
    P.view = 0; P.x = 3; P.z = 3; P.y = M.seabed(3, 3) + M.CONFIG.eye; P.ground = true; P.pitch = -1.0; B.level = 2;
    const rows = []; let bad = 0, okW = true, openBad = 0, outBad = 0;
    for (const d of [0, 1, 2]) {
      M.setBodyDetail(d); const g = B.suit.geometry, S = g.userData.skin, ix = g.index.array, P0 = S.p0;
      for (let v = 0; v < S.count; v++) if (!(S.w[v] >= 0 && S.w[v] <= 1)) okW = false;
      const edges = (arr) => { let mx = 0; for (let t = 0; t < ix.length; t += 3) for (const [a, b] of [[ix[t], ix[t + 1]], [ix[t + 1], ix[t + 2]], [ix[t + 2], ix[t]]]) mx = Math.max(mx, Math.hypot(arr[3 * a] - arr[3 * b], arr[3 * a + 1] - arr[3 * b + 1], arr[3 * a + 2] - arr[3 * b + 2])); return mx; };
      const e0 = edges(P0);
      // tepi terbuka (sisi milik satu segitiga) hanya di ujung bawah kaki (di dalam sepatu) dan lengan (di dalam manset); pangkal paha di dalam panggul
      const ec = new Map(); for (let t = 0; t < ix.length; t += 3) for (const [a, b] of [[ix[t], ix[t + 1]], [ix[t + 1], ix[t + 2]], [ix[t + 2], ix[t]]]) { const key = a < b ? a + ',' + b : b + ',' + a; ec.set(key, (ec.get(key) || 0) + 1); }
      for (const [key, n] of ec) if (n === 1) for (const v of key.split(',').map(Number)) { const y = P0[3 * v + 1]; if (!(Math.abs(y - 0.04) < 0.01 || Math.abs(y - 0.83) < 0.01)) openBad++; }
      for (let v = 0; v < S.count; v++) if (S.bi[2 * v] === 0 && (S.bi[2 * v + 1] === 2 || S.bi[2 * v + 1] === 4) && S.w[v] > 0.99 && P0[3 * v + 1] < 1.05) {
        const y = P0[3 * v + 1], hw = y > 0.98 ? 0.215 : 0.225, x = Math.abs(P0[3 * v]), z = P0[3 * v + 2];
        if ((x / hw) ** 2 + (z / 0.125) ** 2 > 1) outBad++; }
      // lingkar lutut kiri: titik bobot campur paha/betis terdekat lutut
      const knee = (arr) => { let s = 0, n = 0; const c = new V3(); const pts = []; for (let v = 0; v < S.count; v++) if (S.bi[2 * v] === 3 && Math.abs(P0[3 * v + 1] - 0.47) < 0.03) pts.push(v);
        for (const v of pts) c.add(new V3(arr[3 * v], arr[3 * v + 1], arr[3 * v + 2])); c.multiplyScalar(1 / Math.max(1, pts.length));
        for (const v of pts) { s += Math.hypot(arr[3 * v] - c.x, arr[3 * v + 1] - c.y, arr[3 * v + 2] - c.z); n++; } return n ? s / n : 0; };
      const k0 = knee(P0); let eMax = 0, kMin = 9, errMax = 0;
      const poses = [
        () => { M.BOB.run = 1; M.BOB.amp = 0.055; M.BOB.phase = 0; M.updateBody(10); },
        () => { M.BOB.run = 1; M.BOB.amp = 0.055; M.BOB.phase = Math.PI / 2; M.updateBody(10); },
        () => { M.BOB.run = 0; M.BOB.amp = 0; P.ground = false; M.updateBody(10); P.ground = true; },
        () => { M.boardShip(); M.FLY.view = 1; M.flyCamera(); M.updateBody(1 / 60); },
      ];
      for (const f of poses) {
        f(); const a = g.attributes.position.array, nn = g.attributes.normal.array;
        for (const x of a) if (!Number.isFinite(x)) bad++; for (const x of nn) if (!Number.isFinite(x)) bad++;
        eMax = Math.max(eMax, edges(a) / e0); kMin = Math.min(kMin, knee(a) / k0);
        // titik dengan bobot penuh betis = pivot lutut x posisi ikat lokal
        for (let v = 0; v < S.count; v += 7) if (S.bi[2 * v] === 3 && S.w[v] === 1) {
          const q = B.knees[0].worldToLocal(B.group.localToWorld(new V3(a[3 * v], a[3 * v + 1], a[3 * v + 2])));
          const loc = new V3(P0[3 * v], P0[3 * v + 1], P0[3 * v + 2]).applyMatrix4(B.bindInv[3]); errMax = Math.max(errMax, q.distanceTo(loc));
        }
        M.flyReset(); M.FLY.view = 0;
      }
      rows.push(`d${d}: tepi terpanjang ${eMax.toFixed(2)}x, lutut ${kMin.toFixed(2)}x, kulit=tulang ${(errMax * 1000).toFixed(2)} mm`);
      okW = okW && eMax < 2.5 && kMin > 0.6 && errMax < 1e-3;
    }
    // batang kaku: panggul = badan atas x geser (0, -0,03, 0) saat lari dan menunduk (pinggang tidak tertekuk / tergeser)
    let trk = 0; for (const [run, pt] of [[1, -1.2], [1, 0], [0, -1.2]]) { P.pitch = pt; M.BOB.run = run; M.BOB.amp = run ? 0.055 : 0.034; M.BOB.phase = 0.7; M.updateBody(10); B.group.updateMatrixWorld(true);
      const q = B.torso.localToWorld(new V3(0, -0.03, 0)).distanceTo(B.pelvis.getWorldPosition(new V3())), qa = B.torso.getWorldQuaternion(new M.THREE.Quaternion()).angleTo(B.pelvis.getWorldQuaternion(new M.THREE.Quaternion()));
      trk = Math.max(trk, q + qa * 0.5); }
    out[`batang tubuh kaku (M6f-c): panggul vs badan atas saat lari / menunduk ${(trk * 1000).toFixed(2)} mm (< 2)`] = trk < 0.002;
    M.setBodyDetail(d0); M.BOB.run = 0; M.BOB.amp = 0; M.BOB.phase = 0; P.pitch = 0; M.updateBody(10);
    out[`pakaian satu mesh berkulit (M6f): ${rows.join('; ')} (tepi < 2,5x, lutut > 0,6x, < 1 mm), nilai tidak valid ${bad}`] = okW && bad === 0;
    out[`pakaian tanpa lubang: titik tepi terbuka di luar sepatu / manset ${openBad}, pangkal paha keluar dari panggul ${outBad} titik`] = openBad === 0 && outBad === 0;
  }

  // 5p. M6c: tubuh tidak membayangi dirinya, bayangan KS-07 tetap jatuh di tubuh, garis basah yang ingat, busa garis air di kaki
  {
    const P = M.P, B = M.BODY, Cb = M.CONFIG.body, PI = Math.PI, from = M.THREE.DataUtils.fromHalfFloat, V3 = M.THREE.Vector3;
    M.setMode('jelajah'); M.STATE.started = true; M.stopMission(); M.flyReset(); M.SWEEP.on = false; M.CINE.on = false;
    P.view = 0; P.ground = true; P.depth = 0; B.level = 2; B.cast = true; M.MOOD.brk = 1; M.BOB.run = 0; M.BOB.amp = 0; M.BOB.phase = 0; P.vx = 0; P.vz = 0;
    const snap = () => { const T = M.POST.hdr, w = T.width, h = T.height, b = new Uint16Array(w * h * 4); M.renderer.readRenderTargetPixels(T, 0, 0, w, h, b); return b; };
    // render sinkron (waktu, ombak sama); updateBody(10) setelah peta bayangan: peredaman busa dan yaw langsung di sasaran
    const shot = () => { M.camera.position.set(P.x, P.y, P.z); M.camera.rotation.set(P.pitch, P.yaw, 0, 'YXZ'); M.camera.updateMatrixWorld(true); M.U.uCam.value.copy(M.camera.position);
      M.updateShadow(); M.updateBody(10); M.renderer.setRenderTarget(M.POST.hdr); M.renderer.clear(); M.renderer.render(M.scene, M.camera); M.renderer.setRenderTarget(null); return snap(); };
    const lum = (b, k) => 0.3 * from(b[k]) + 0.59 * from(b[k + 1]) + 0.11 * from(b[k + 2]);
    const maskOf = (a, b) => { const m = []; for (let k = 0; k < a.length; k += 4) if (Math.abs(a[k] - b[k]) + Math.abs(a[k + 1] - b[k + 1]) + Math.abs(a[k + 2] - b[k + 2]) > 40) m.push(k); return m; };
    const mlum = (b, m) => { let l = 0; for (const k of m) l += lum(b, k); return m.length ? l / m.length : 0; };
    const place = (x, z) => { P.x = x; P.z = z; P.y = M.seabed(x, z) + M.CONFIG.eye; };
    // invers matriks bayangan
    place(0, 0); P.yaw = -PI / 2 + 0.3; P.pitch = -60 * PI / 180; M.updateBody(10); M.updateShadow();
    const I = new M.THREE.Matrix4().multiplyMatrices(M.bodyMat.uniforms.uShMI.value, M.U.uShM.value).elements;
    let ie = 0; for (let k = 0; k < 16; k++) ie = Math.max(ie, Math.abs(I[k] - (k % 5 === 0 ? 1 : 0)));
    out[`bayangan tubuh: uShMI x uShM = identitas, galat ${ie.toExponential(1)} (< 1e-4)`] = ie < 1e-4;
    // tanpa bayangan diri: masker tubuh = Tampil vs Bayangan (bayangan tubuh di dasar laut ada di keduanya); dalam masker, tubuh menghalangi vs tidak
    const gd = new V3(Math.cos(22 * PI / 180) * Math.cos(28 * PI / 180), Math.sin(22 * PI / 180), -Math.cos(22 * PI / 180) * Math.sin(28 * PI / 180)), gh = Math.hypot(gd.x, gd.z);
    P.yaw = Math.atan2(-gd.x, -gd.z);   // menghadap cahaya: sisi depan tubuh tersinari
    B.level = 2; const a2 = shot(); B.level = 1; const a1 = shot(); B.level = 2; B.cast = false; const a2n = shot(); B.cast = true;
    const m0 = maskOf(a2, a1), l2 = mlum(a2, m0), l2n = mlum(a2n, m0), area = 100 * m0.length / (a2.length / 4);
    out[`tanpa bayangan diri: masker tubuh ${area.toFixed(1)}% (5-40%), terang dengan tubuh di peta bayangan ${l2.toFixed(4)} vs tanpa ${l2n.toFixed(4)} (beda ${(100 * Math.abs(l2 / l2n - 1)).toFixed(2)}%, < 1%)`] = area > 5 && area < 40 && Math.abs(l2 / l2n - 1) < 0.01;
    // bayangan KS-07 tetap jatuh di tubuh: pemain di titik yang dada / pinggulnya terhalang wahana, KS-07 di peta bayangan vs tidak
    let best = { d: 0, h: 0, l1: 0, l0: 0 };
    for (const hb of [0.6, 1.0, 1.4]) {
      const sy = M.seabed(M.SHIP.x, M.SHIP.z), h = M.SHIP.y + 0.3 - (sy + hb); place(M.SHIP.x - gd.x * h / gd.y, M.SHIP.z - gd.z * h / gd.y);
      B.level = 2; const s2 = shot(); B.level = 1; const s1 = shot(); B.level = 2; const mm = maskOf(s2, s1);
      M.SHIP.mesh.traverse((o) => o.layers.disable(3)); const s2o = shot(); M.SHIP.mesh.traverse((o) => o.layers.enable(3));
      const l1 = mlum(s2, mm), l0 = mlum(s2o, mm), d = l0 > 0 ? 1 - l1 / l0 : 0; if (d > best.d) best = { d, h: hb, l1, l0 };
    }
    out[`bayangan KS-07 di tubuh: terang ${best.l1.toFixed(4)} vs tanpa wahana ${best.l0.toFixed(4)} (${(100 * best.d).toFixed(1)}% lebih gelap, > 20%, titik setinggi ${best.h} m)`] = best.d > 0.2;
    // basah yang ingat: diam = kedalaman, lari naik, lompat turun pelan, kering kembali ke muka air, tersapu = seluruhnya
    let spot = null; for (let x = 0; x <= 60 && !spot; x += 3) for (let z = -30; z <= 30 && !spot; z += 3) { place(x, z); const d = M.waterHere(M.STATE.visT) - M.seabed(x, z); if (d > 0.2 && d < 0.8 && Math.hypot(x - M.SHIP.x, z - M.SHIP.z) > 12) spot = [x, z]; }
    place(...(spot || [0, 0])); P.pitch = -60 * PI / 180; B.wetH = 0; M.updateBody(10); const dep = M.waterHere(M.STATE.visT) - M.seabed(P.x, P.z), w0 = B.wetH;
    M.BOB.run = 1; M.BOB.amp = 0.055; M.updateBody(10); const wr = B.wetH, wr2 = wr; M.BOB.run = 0; M.BOB.amp = 0;
    P.y += 1.2; P.ground = false; for (let f = 0; f < 60; f++) M.updateBody(1 / 60); const wj = B.wetH; P.y -= 1.2; P.ground = true;
    for (let f = 0; f < 600; f++) M.updateBody(0.1); const wd = B.wetH, uw = M.bodyMat.uniforms.uWetH.value;
    M.SWEEP.on = true; M.updateBody(1 / 60); const ws = B.wetH; M.SWEEP.on = false; M.updateBody(10);
    out[`basah: kedalaman ${dep.toFixed(2)} m, diam ${w0.toFixed(2)}, lari ${wr.toFixed(2)} (>= +0,25), lompat 1 s ${wj.toFixed(3)} (turun ${(wr2 - wj).toFixed(3)} <= 0,02), 60 s ${wd.toFixed(2)} (= kedalaman), tersapu ${ws.toFixed(1)}, uWetH ${uw.toFixed(2)}`] =
      Math.abs(w0 - dep) < 0.02 && wr >= dep + 0.25 && wr2 - wj > 0 && wr2 - wj <= 0.02 && Math.abs(wd - dep) < 0.02 && ws === 2 && Math.abs(uw - wd) < 1e-6;
    // busa garis air: titik = bodyLegAt, kekuatan 0 saat Mati / di udara / terbang, terlihat dan setempat di render
    const su = M.seaNear.material.uniforms; M.updateBody(10); const L0 = M.bodyLegAt(-1, dep), L1 = M.bodyLegAt(1, dep), lg = su.uLegs.value;
    const le = Math.max(Math.hypot(lg.x - L0.x, lg.y - L0.z), Math.hypot(lg.z - L1.x, lg.w - L1.z)), k1 = su.uLegK.value;
    B.level = 0; M.updateBody(10); const kM = su.uLegK.value; B.level = 2; P.ground = false; M.updateBody(10); const kA = su.uLegK.value; P.ground = true;
    M.FLY.on = true; M.updateBody(10); const kF = su.uLegK.value; M.FLY.on = false; M.updateBody(10);
    out[`busa garis air: titik = bodyLegAt (selisih ${le.toFixed(4)} m), kekuatan ${k1.toFixed(2)} di air, Mati ${kM}, udara ${kA}, terbang ${kF}`] = le < 0.01 && (dep > 0.85 || k1 > 0.5) && kM === 0 && kA === 0 && kF === 0;
    P.vx = -Math.sin(P.yaw) * 4; P.vz = -Math.cos(P.yaw) * 4; Cb.foam = 1; const f1 = shot(); Cb.foam = 0; const f0 = shot(); Cb.foam = 1; P.vx = 0; P.vz = 0;
    const fa = 100 * maskOf(f1, f0).length / (f1.length / 4);
    out[`busa garis air terlihat dan setempat: ${fa.toFixed(2)}% piksel beda (0,05-10%; M6e: kaki kotor lebih gelap, busa di atasnya lebih kontras)`] = fa > 0.05 && fa < 10;
    place(0, 0); P.pitch = 0; P.yaw = -PI / 2 + 0.3; M.updateBody(10);
  }

  // 5q. M6d: visor helm: tengah layar tidak tersentuh, bingkai di sudut, mati saat terbang / sinematik / foto / drone, embun napas, tetes air, kilau, napas, panel
  {
    const P = M.P, V = M.VISOR, u = M.M_COMP.uniforms, PI = Math.PI;
    M.setMode('jelajah'); M.STATE.started = true; M.stopMission(); M.flyReset(); M.SWEEP.on = false; M.CINE.on = false; M.PHOTO.on = false;
    P.view = 0; P.x = 0; P.z = 0; P.y = M.seabed(0, 0) + M.CONFIG.eye; P.ground = true; P.yaw = -PI / 2 + 0.3; P.pitch = -0.3; M.MOOD.brk = 1;
    M.BOB.run = 0; M.BOB.amp = 0; V.ex = 0; V.wet = 0; V.fog = 0; M.BODY.level = 2;
    const L = M.POST.ldr, w = L.width, h = L.height;
    const rnd = () => { M.camera.position.set(P.x, P.y, P.z); M.camera.rotation.set(P.pitch, P.yaw, 0, 'YXZ'); M.camera.updateMatrixWorld(true); M.U.uCam.value.copy(M.camera.position);
      M.updateShadow(); M.renderer.setRenderTarget(M.POST.hdr); M.renderer.clear(); M.renderer.render(M.scene, M.camera); M.updateVisor(0); M.postRender(0);
      const b = new Uint8Array(w * h * 4); M.renderer.readRenderTargetPixels(L, 0, 0, w, h, b); M.renderer.setRenderTarget(null); return b; };
    const frac = (a, b, x0, x1, y0, y1) => { let n = 0, m = 0; for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) { const k = (y * w + x) * 4; m++; if (Math.abs(a[k] - b[k]) + Math.abs(a[k + 1] - b[k + 1]) + Math.abs(a[k + 2] - b[k + 2]) > 6) n++; } return 100 * n / Math.max(1, m); };
    V.level = 2; const a2 = rnd(); V.level = 0; const a0 = rnd(); V.level = 2;
    const cen = frac(a2, a0, w >> 2, (3 * w) >> 2, h >> 2, (3 * h) >> 2), cw = Math.round(w * 0.08), ch = Math.round(h * 0.08);
    const cor = (frac(a2, a0, 0, cw, 0, ch) + frac(a2, a0, w - cw, w, 0, ch) + frac(a2, a0, 0, cw, h - ch, h) + frac(a2, a0, w - cw, w, h - ch, h)) / 4;
    out[`visor Penuh: tengah layar ${cen.toFixed(2)}% piksel beda dari Mati (< 0,5%), sudut ${cor.toFixed(1)}% (> 20%)`] = cen < 0.5 && cor > 20;
    const offs = []; const off = (fn, undo) => { fn(); M.updateVisor(0); offs.push(u.uVis.value); undo(); };
    off(() => { M.FLY.on = true; }, () => { M.FLY.on = false; }); off(() => { M.CINE.on = true; }, () => { M.CINE.on = false; });
    off(() => { M.PHOTO.on = true; }, () => { M.PHOTO.on = false; }); off(() => { P.view = 1; }, () => { P.view = 0; });
    M.updateVisor(0); const onV = u.uVis.value;
    out[`visor aktif berjalan kaki (uVis ${onV}), mati saat terbang / sinematik / foto / drone: ${offs.join(' / ')}`] = onV === 1 && offs.every((x) => x === 0);
    // embun napas: lari 20 s, lalu diam 30 s
    let fmx = 0; M.BOB.run = 1; M.BOB.amp = 0.055; for (let f = 0; f < 600; f++) { M.updateVisor(1 / 30); fmx = Math.max(fmx, V.fog); }
    M.BOB.run = 0; M.BOB.amp = 0; for (let f = 0; f < 900; f++) M.updateVisor(1 / 30); const f0 = V.fog;
    out[`embun napas: lari maksimum ${fmx.toFixed(3)} (0,04-0,12), diam 30 s ${f0.toFixed(4)} (< 0,005)`] = fmx > 0.04 && fmx <= 0.12 + 1e-9 && f0 < 0.005;
    // tetes air: mendarat di air, kering, tersapu, terlihat
    V.wet = 0; P.depth = 0.5; M.footstep(1.2, true); const wl = V.wet; for (let f = 0; f < 270; f++) M.updateVisor(1 / 30); const wd = V.wet;
    M.SWEEP.on = true; M.updateVisor(1 / 30); const ws = V.wet; M.SWEEP.on = false; for (let f = 0; f < 270; f++) M.updateVisor(1 / 30); const ws9 = V.wet; P.depth = 0;
    V.wet = 1; V.seed = 5; V.ex = 0; const b1 = rnd(); V.wet = 0; const b0 = rnd(); const wa = frac(b1, b0, 0, w, 0, h);
    out[`tetes air: mendarat ${wl.toFixed(2)} (>= 0,25), 9 s ${wd.toFixed(2)}, tersapu ${ws.toFixed(2)} lalu 9 s ${ws9.toFixed(2)}, render basah ${wa.toFixed(1)}% piksel beda (> 1%)`] = wl >= 0.25 && wd === 0 && ws === 1 && ws9 === 0 && wa > 1;
    // kilau Gargantua di tepi atas
    const G = M.GDIR; P.yaw = Math.atan2(-G.x, -G.z); P.pitch = Math.asin(G.y);
    M.camera.rotation.set(P.pitch, P.yaw, 0, 'YXZ'); M.camera.updateMatrixWorld(true); M.updateVisor(0); const g1 = V.glint;
    P.yaw += PI; M.camera.rotation.set(P.pitch, P.yaw, 0, 'YXZ'); M.camera.updateMatrixWorld(true); M.updateVisor(0); const g0 = V.glint;
    out[`kilau visor: menghadap Gargantua ${g1.toFixed(2)} (> 0,2), membelakangi ${g0.toFixed(2)} (= 0)`] = g1 > 0.2 && g0 === 0;
    const A = M.AUDIO; out[`napas dan dengung suit: AudioContext ${!!A.ctx}, simpul napas ${!!A.brG}, suit ${!!A.suitG}`] = !A.ctx || (!!A.brG && !!A.suitG);
    // panel: Visor sebelum Tubuh, Tubuh terakhir, gerak kepala indeks 4, siklus tersimpan
    const n = M.LAB.length, lv = V.level; M.cycleVisor(); const lv1 = V.level, sv = localStorage.getItem('millar.visor'); M.cycleVisor(); M.cycleVisor();
    out[`panel Visor: baris ke-${n - 1} (sebelum Tubuh ke-${n}), siklus ${lv} -> ${lv1}, tersimpan ${sv}`] = M.LAB[n - 2][1]().includes('Visor') && M.LAB[n - 1][1]().includes('Tubuh') && M.LAB[4][1]().includes('Gerak kepala') && lv1 === (lv + 1) % 3 && sv === String(lv1) && V.level === lv;
    V.level = 1; V.wet = 0; V.ex = 0; localStorage.removeItem('millar.visor'); P.x = 0; P.z = 0; P.y = M.seabed(0, 0) + M.CONFIG.eye; P.pitch = 0; P.yaw = -PI / 2 + 0.3; M.updateVisor(0);
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
    // M6c: tubuh terlihat (menunduk) di 3 suasana: tanpa nilai tidak valid atau titik menyala
    { const P = M.P, sv = P.pitch; let bb = 0, bh = 0; P.pitch = -60 * Math.PI / 180; M.BODY.level = 2; P.view = 0;
      for (const mi of [0, 1, 2]) { M.MOOD.idx = mi; M.updateMood(60, M.STATE.visT);
        M.camera.position.set(P.x, P.y, P.z); M.camera.rotation.set(P.pitch, P.yaw, 0, 'YXZ'); M.camera.updateMatrixWorld(true); M.U.uCam.value.copy(M.camera.position);
        M.updateShadow(); r.setRenderTarget(T); r.clear(); r.render(M.scene, M.camera); r.setRenderTarget(null); r.readRenderTargetPixels(T, 0, 0, w, h, buf);
        for (let k = 0; k < buf.length; k += 4) for (let c = 0; c < 3; c++) { const x = from(buf[k + c]); if (!Number.isFinite(x)) bb++; else if (x > 50) bh++; } }
      M.MOOD.idx = 0; M.updateMood(60, M.STATE.visT); M.MOOD.brk = 1; P.pitch = sv;
      out[`preset ${M.PRESETS[i].name}: tubuh menunduk di 3 suasana (detail ${M.BODY.detail}, ${M.BODY.tris} segitiga), tidak valid ${bb}, titik > 50: ${bh}`] = bb === 0 && bh === 0 && M.BODY.detail === M.BODY_DETAIL[i]; }
  }
  M.applyPreset(4);
  return out;
})()
"""

async def main():
    local = os.environ.get('THREE_LOCAL')
    async with async_playwright() as p:
        exe = os.environ.get('CHROMIUM')                              # opsional: jalur Chromium sendiri
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'], **({'executable_path': exe} if exe else {}))
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
