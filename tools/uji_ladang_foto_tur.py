"""Uji tahap 12d (Copper Corn Station): siklus tanam gandum dan mesin ladang, mode foto (FOV, blur, simpan PNG,
semua dikembalikan saat keluar), tur sinematik v2.9 (20 titik, jam 12:00 sampai 07:00, hujan di bawah awan, genangan, burung formasi V, motor ke kota,
lempar bola melawan putaran, gerhana dari dalam, pembuka dan penutup kamera luar, tanpa NaN, semua dikembalikan).
Pakai: python tools/uji_ladang_foto_tur.py   (butuh: pip install playwright && playwright install chromium; CHROMIUM opsional)"""
import asyncio, os, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(async () => {
  const st = window.__station, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms));
  // B4: siklus tanam dan mesin
  const wheat = st.fieldList.filter((f) => f.crop === 'wheat' && !f.meadow), n = [0, 0, 0, 0];
  for (const f of wheat) { const ph = st.farmStage(f); n[ph < 0.45 ? 0 : ph < 0.72 ? 1 : ph < 0.82 ? 2 : 3]++; }
  out[`gandum per tahap: tumbuh ${n[0]}, menguning ${n[1]}, masak ${n[2]}, tunggul ${n[3]}`] = n.every((x) => x > 0);
  st.clock.hour = 11; st.teleport('wheat'); await wait(4000);
  out[`mesin ladang dekat pemain: ${st.FARM.machines.length}`] = st.FARM.machines.length > 0;
  // C2: mode foto
  const rate0 = st.clock.hourRate;
  st.togglePhoto(true);
  const set = (id, v, ev) => { const el = document.getElementById(id); if (el.type === 'checkbox') el.checked = v; else el.value = v; el.dispatchEvent(new Event(ev || 'input')); };
  set('phFov', 40); set('phBlur', 0.6); set('phPause', true, 'change');
  await wait(300);
  out[`mode foto: FOV ${st.camera.fov}, blur ${st.compMat.uniforms.uDof.value}, waktu berhenti`] = st.camera.fov === 40 && st.compMat.uniforms.uDof.value === 0.6 && st.clock.hourRate === 0;
  out['mode foto: HUD tersembunyi'] = getComputedStyle(document.getElementById('hud')).display === 'none';
  const url = await new Promise((r) => { window.__captureCb = r; });
  out[`tangkapan PNG ${url.length} karakter`] = url.startsWith('data:image/png') && url.length > 5000;
  st.togglePhoto(false);
  out['keluar mode foto: FOV, blur, waktu kembali'] = st.camera.fov === st.CONFIG.fov && st.compMat.uniforms.uDof.value === 0 && st.clock.hourRate === rate0;
  // C3: tur sinematik v2.5 (22 titik; tur hanya mengatur jam, awan, posisi kamera, motor dan lemparan lewat keadaan biasa)
  const p0 = { th: st.player.theta, za: st.player.za };
  const w0 = { hour: st.clock.hour, rate: st.clock.hourRate, orbit: st.clock.orbit, mode: st.WEATHER.mode, moto: st.MOTO.on, adapt: st.ADAPT.on, bloom: st.POST.bloom, rays: st.RAYS.on };
  st.startTour();
  const hour0 = st.clock.hour, N = st.TOUR.keys.length, CIRC = 2 * Math.PI * st.R;
  const wrap = (x) => x - CIRC * Math.round(x / CIRC);
  let bad = false, maxH = 0, steps = 0, fadeMax = 0; const ext0 = {};
  const deg0 = 180 / Math.PI, glance = { y: 0, p: 0, n: 0 }, idx = new Set(), K = {}, nSub = Math.round(0.05 / st.STEP), ball0 = st.TOUR.keys.find((q) => q.ball);
  for (let k = 0; k < 8000 && st.TOUR.on; k++, steps++) {
    const key = st.TOUR.keys[st.TOUR.i];
    for (let q = 0; q < nSub; q++) st.physicsStep(st.STEP);           // urutan seperti worldStep
    st.stepTour(0.05); if (!st.TOUR.on) break;
    st.updateCamera();
    st.updateReal();                                                   // posisi mata untuk burung (seperti worldStep)
    st.stepBirds(0.05); st.updateRain(0.05); st.updateFar(); st.updateClouds(0.05);
    idx.add(st.TOUR.i);
    const P = st.player, ps = P.theta * st.R, hold = st.TOUR.t > (key.dur || 0);
    const r = K[key.title] || (K[key.title] = { rain: 0, wetMin: 1, ecl: 1, ext: false, cloud: 0, bird: 1e9, z0: st.MOTO.za, ground: false });
    { const q = { s: ((ps % CIRC) + CIRC) % CIRC, za: P.za, h: P.h }; if (!st.ext.active && !(key.moto && !st.MOTO.on)) { if (!r.anyFirst) r.anyFirst = q; r.anyLast = q; } }
    r.hour = st.clock.hour; r.rain = Math.max(r.rain, st.RAIN.k); r.ecl = Math.min(r.ecl, st.ECL.k); r.ext = r.ext || st.ext.active; r.rainEnd = st.RAIN.k;
    if (key.ext === 'in') { r.camZ = st.camera.position.z; r.lookEnd = [st.ADAPT.on, st.POST.bloom, st.RAYS.on]; }
    if (!r.lookStart) r.lookStart = [st.ADAPT.on, st.POST.bloom, st.RAYS.on];              // pembuka: posisi kamera luar terakhir (sudah menembus kaca end cap A?)
    r.rays = r.rays || st.RAYS.on; if (key.fly) r.hMax = Math.max(r.hMax || 0, P.h - st.groundH(ps, P.za));
    if (hold && key.B && !key.track && !key.ball && !key.eclipse && !key.path && !key.moto && !key.fly) {   // melihat sekitar: simpangan dari arah titik
      const dy = Math.abs(wrap((P.heading - key.B.hd) * st.R) / st.R) * deg0, dp = Math.abs(P.pitch - key.B.pt) * deg0;
      glance.y = Math.max(glance.y, dy); glance.p = Math.max(glance.p, dp); glance.n++;
      const m = Math.hypot(dy, dp); if (r.glPrev !== undefined && m < r.glPrev - 1e-4) glance.rev = (glance.rev || 0) + 1; r.glPrev = m;   // v2.8: satu arah, tidak kembali
    }
    if (hold && key.path) {                                            // v2.8: jalan kaki: laju, gerak kepala (tinggi mata naik-turun), langkah
      const e = P.h - st.groundH(ps, P.za); r.bobMin = Math.min(r.bobMin ?? 9, e); r.bobMax = Math.max(r.bobMax ?? -9, e);
      if (r.wPrev) r.wMax = Math.max(r.wMax || 0, Math.hypot(wrap(ps - r.wPrev.s), P.za - r.wPrev.za) / 0.05);
      r.wPrev = { s: ps, za: P.za }; r.walkT = (r.walkT || 0) + 0.05; r.steps = key.bob ? key.bob.n : 0;
      if (key.title === 'Air mancur Coriolis') { const dF = Math.hypot(wrap(ps - st.FOUNT.s), P.za - st.FOUNT.za); r.fMin = Math.min(r.fMin ?? 99, dF); r.fMax = Math.max(r.fMax || 0, dF); r.fCol = (r.fCol || 0) + (st.colAt(((ps % CIRC) + CIRC) % CIRC, P.za, 0.3) ? 1 : 0); }
    }
    if (hold) {
      r.wetMin = Math.min(r.wetMin, st.RAIN.wet);
      const look = key.hd === 180 ? -25 : 25;
      r.cloud = Math.max(r.cloud, st.cloudCoverAt(((ps % CIRC) + CIRC) % CIRC, P.za + (key.title === 'Genangan di jalan kota' ? look : 0)));
      for (const V of st.BIRDS.vees) if (!V.dead) r.bird = Math.min(r.bird, Math.hypot(wrap(V.s - ps), V.za - P.za, V.h - P.h));
      const pos = { s: ((ps % CIRC) + CIRC) % CIRC, za: P.za, h: P.h, eyeH: P.h - st.groundH(ps, P.za), hd: P.heading, pt: P.pitch };
      if (!r.first) r.first = pos;
      r.last = pos; r.hs0 = r.hs0 ?? (r.bird < 1e9 ? r.bird : undefined);
      if (key.ball) r.ballMove = Math.max(r.ballMove || 0, Math.hypot(wrap(pos.s - r.first.s), pos.za - r.first.za));
      if (key.track) {                                                 // kawanan terdekat: jarak dan sudut antara arah kamera dan pusat kawanan
        let best = null, bd = 1e9;
        for (const F of st.BIRDS.flocks) {
          if (F.dead || !F.members) continue; const live = F.members.filter((q) => !q.gone); if (!live.length) continue;
          const s0 = live[0].p[0]; let a = 0, z = 0, h = 0; for (const q of live) { a += s0 + wrap(q.p[0] - s0); z += q.p[1]; h += q.p[2]; }
          const c = { s: a / live.length, za: z / live.length, h: h / live.length }, d = Math.hypot(wrap(c.s - ps), c.za - P.za); if (d < bd) { bd = d; best = c; }
        }
        if (best) { const ds = wrap(best.s - ps), dz = best.za - P.za, bh = st.groundH(best.s, best.za) + best.h, hd = Math.atan2(ds, dz), pt = Math.atan2(bh - P.h - st.CONFIG.eye, Math.hypot(ds, dz));
          r.flock = Math.hypot(ds, dz, bh - P.h - st.CONFIG.eye); if (r.flock0 === undefined) r.flock0 = r.flock;
          r.aimErr = Math.hypot(wrap((P.heading - hd) * st.R) / st.R * Math.cos(pt), P.pitch - pt) * 180 / Math.PI; r.ptBird = pt; }
      }
      if (key.eclipse && st.TOUR.t > key.dur + 1.5) {                 // Matahari (arah SUN_DIR diputar -omega t, seperti updateLighting): tinggi di atas cakrawala dan meleset dari arah kamera
        const a = st.OMEGA * st.clock.sim, sy0 = Math.sin(25 / deg0), sx = sy0 * Math.sin(a), sy = sy0 * Math.cos(a), sz = Math.cos(25 / deg0), th = P.theta;
        const up = -(sx * Math.cos(th) + sy * Math.sin(th)), tg = -sx * Math.sin(th) + sy * Math.cos(th);
        const hd = Math.atan2(tg, sz), el = Math.atan2(up, Math.hypot(tg, sz));
        r.sunEl = Math.min(r.sunEl ?? 99, el * deg0);
        r.sunAim = Math.max(r.sunAim || 0, Math.hypot(wrap((P.heading - hd) * st.R) / st.R * Math.cos(el), P.pitch - el) * deg0);
      }
      if (key.ball && ball0 && ball0.bb && ball0.bb.t > 0) {            // v2.8: bola di dalam bingkai, laju kamera, geser ke samping; akhir: seluruh lintasan di bingkai
        const b = ball0.bb, cam = st.camera, v = cam.position.clone(), ndc = (x, y, z) => { v.set(x, y, z).project(cam); return Math.max(Math.abs(v.x), Math.abs(v.y)) + (v.z > 1 ? 9 : 0); };
        cam.updateMatrixWorld();
        if (!b.done) r.ballOut = Math.max(r.ballOut || 0, ndc(b.pos.x, b.pos.y, b.pos.z));
        const cp = cam.position.clone(); if (r.cPrev) (r.cSp || (r.cSp = [])).push(cp.distanceTo(r.cPrev) / 0.05); r.cPrev = cp;
        const side = Math.abs(P.za - (b.p0.z + 4000)); if (r.side !== undefined && side < r.side - 0.01) r.sideRev = (r.sideRev || 0) + 1; r.side = side;
        let all = 0; for (let i = 0; i <= 40; i++) { const t = b.tEnd * i / 40, c = Math.cos(st.OMEGA * t), sn = Math.sin(st.OMEGA * t), x = b.p0.x + b.vin.x * t, y = b.p0.y + b.vin.y * t;
          all = Math.max(all, ndc(x * c + y * sn, -x * sn + y * c, b.p0.z + b.vin.z * t)); }
        r.pathIn = all; r.under = (r.under || 0) + (P.h < st.groundH(ps, P.za) - 0.01 ? 1 : 0);
      }
    }
    if (key.moto && st.MOTO.on) {
      if (r.s0 === undefined) { r.s0 = st.MOTO.s; r.d0 = (st.districtAt(st.MOTO.s, st.MOTO.za) || {}).name; r.zaMin = 1e9; r.zaMax = -1e9; r.ds = 0; r.sPrev = st.MOTO.s; }
      r.ds += wrap(r.sPrev - st.MOTO.s); r.sPrev = st.MOTO.s;          // jarak keliling ke arah s berkurang (melawan putaran)
      r.zaMin = Math.min(r.zaMin, st.MOTO.za); r.zaMax = Math.max(r.zaMax, st.MOTO.za);
      r.d1 = (st.districtAt(st.MOTO.s, st.MOTO.za) || {}).name; r.g1 = st.MOTO.gFelt;
      r.v1 = st.MOTO.v; r.vMax = Math.max(r.vMax || 0, st.MOTO.v); r.gMin = Math.min(r.gMin ?? 9, st.MOTO.gFelt); r.ground = r.ground || P.state === 'ground';
    }
    if (st.ext.active && !ext0.seen) Object.assign(ext0, { seen: true, adapt: st.ADAPT.on, bloom: st.POST.bloom });
    fadeMax = Math.max(fadeMax, +document.getElementById('tourFade').style.opacity || 0);
    if (!isFinite(P.theta + P.za + P.h + P.heading + P.pitch + st.clock.hour + st.camera.position.length())) bad = true;
    if (!st.ext.active) maxH = Math.max(maxH, P.h);
  }
  const T = steps * 0.05, get = (n) => K[n] || {}, eye = st.TOUR.keys.filter((q) => q.h === 0).length;
  const ball = st.TOUR.keys.find((q) => q.ball), L = ball && ball.landing, deg = 180 / Math.PI;
  out[`tur: ${idx.size} dari ${N} titik, ${T.toFixed(0)} s (target 260-360 s), tanpa NaN`] = !bad && idx.size === N && N === 20 && T > 260 && T < 360;
  out[`tur: ${eye} titik setinggi mata (>= 9)`] = eye >= 9;
  out[`tur: tinggi maksimum ${maxH.toFixed(0)} m (tidak melewati sumbu)`] = maxH < st.R - 30;
  out[`tur: jam mulai ${hour0.toFixed(2)}, akhir ${(get('Meninggalkan stasiun').hour || 0).toFixed(2)}`] = hour0 === 12 && Math.abs(get('Meninggalkan stasiun').hour - 7) < 0.05;
  out['tur: pembuka dan penutup di kamera luar'] = !!get('Menuju Copper Corn Station').ext && !!get('Meninggalkan stasiun').ext;
  const H = get('Hujan miring');
  out[`tur: hujan di jalan lingkar rute merah (RAIN.k ${H.rain.toFixed(2)}, awan di atas kamera ${H.cloud.toFixed(2)}, awan terbaik di ruas s 700-3.200 ${(st.TOUR.rainCov || 0).toFixed(2)}), siang tanpa hujan (${get('Ukuran stasiun').rain.toFixed(2)})`] = H.rain > 0.5 && (H.cloud > 0.12 || st.TOUR.rainCov < 0.12) && get('Ukuran stasiun').rain < 0.05;
  const G = get('Genangan di jalan kota');
  out[`tur: genangan (basah min ${G.wetMin.toFixed(2)}, hujan akhir ${G.rainEnd.toFixed(2)}, awan di jalan ${G.cloud.toFixed(2)})`] = G.wetMin > 0.6 && G.rainEnd < 0.1;   // v2.5: lokasi = tempat turun dari motor (awan tidak dipilih), jadi jalan dibuat lebih basah
  const B = get('Burung di bawah awan'), Bl = st.TOUR.keys.find((q) => q.track).land || {};
  out[`tur: kawanan burung: awal ${(B.flock0 ?? 1e9).toFixed(0)} m, akhir ${(B.flock ?? 1e9).toFixed(0)} m, kamera di tanah (mata ${B.last.eyeH.toFixed(2)} m + 1,7), menengadah ${(B.ptBird * deg).toFixed(0)} derajat, meleset ${B.aimErr.toFixed(1)} derajat`] =
    (B.flock0 ?? 1e9) < 40 && Math.abs(B.last.eyeH) < 0.1 && B.ptBird > 15 / deg && B.aimErr < 15 && !st.colAt(Bl.s, Bl.za, 1) && !st.inWater(Bl.s, Bl.za, 1);
  const Sk = get('Skyway: jendela ke angkasa'), skM = ((Sk.last.za % 50) + 50) % 50;
  out[`tur: Skyway za ${Sk.last.za.toFixed(1)}, ${Math.min(skM, 50 - skM).toFixed(1)} m dari balok jendela (>= 10)`] = Math.min(skM, 50 - skM) >= 10;
  const Lc = get('Lampu kota malam'), Lm = Lc.last;
  out[`tur: lampu kota malam: naik ${(Lc.hMax || 0).toFixed(0)} m, menghadap kota (arah ${(Lm.hd * deg0).toFixed(0)} derajat), berakhir za ${Lm.za.toFixed(0)} dekat rumah Cooper`] =
    Lc.hMax > 300 && Math.abs(Math.abs(wrap(Lm.hd * st.R) / st.R) - Math.PI) < 0.2 && Lm.za > 6000;
  const Hu = get('Hutan lebat'), huD = Math.hypot(wrap(Hu.last.s - Hu.first.s), Hu.last.za - Hu.first.za);
  out[`tur: hutan berjalan ${huD.toFixed(0)} m setinggi mata (${Hu.last.eyeH.toFixed(2)}), dari dalam hutan ke luar`] = huD >= 25 && Math.abs(Hu.last.eyeH) < 0.1 && st.inForest(Hu.first.s, Hu.first.za) && !st.inForest(Hu.last.s, Hu.last.za);
  const M = get('Naik motor ke New York');
  out[`tur: motor jalan lingkar za ${M.zaMin.toFixed(1)}-${M.zaMax.toFixed(1)} (rute bus merah 500), ${M.ds.toFixed(0)} m keliling ${M.d0} -> ${M.d1}, maks ${(M.vMax * 3.6).toFixed(0)} km/h, terasa min ${M.gMin.toFixed(2)} g, akhir ${(M.v1 * 3.6).toFixed(1)} km/h`] =
    M.ground && M.ds > 400 && M.ds < 800 && M.zaMin > 490 && M.zaMax < 500 && M.d1 === 'New York' && M.vMax * 3.6 > 140 && M.gMin < 0.5 && M.v1 < 1;
  const Hj = get('Hujan miring'), Gw0 = get('Genangan di jalan kota');
  const rmJ = Math.hypot(wrap(Hj.anyLast.s - M.s0), Hj.anyLast.za - M.zaMin), mwJ = Math.hypot(wrap(Gw0.anyFirst.s - M.anyLast.s), Gw0.anyFirst.za - M.anyLast.za);
  out[`tur: hujan di kota tempat naik motor (${Hj.d || (st.districtAt(Hj.anyLast.s, Hj.anyLast.za) || {}).name}, motor mulai di titik yang sama, lompat ${rmJ.toFixed(1)} m), motor berhenti ${(M.v1 * 3.6).toFixed(1)} km/h lalu jalan kaki dari situ (lompat ${mwJ.toFixed(1)} m)`] =
    rmJ < 3 && mwJ < 3;
  const Gw1 = Gw0.last; out[`tur: jalan kaki sejajar sumbu (arah akhir ${(Gw1.hd * deg0).toFixed(0)} derajat)`] = Math.abs(Gw1.hd * deg0) < 15;
  const ord = st.TOUR.keys.slice(0, 5).map((q) => q.title).join(' > ');
  out[`tur: urutan pembuka ${ord}`] = ord === 'Menuju Copper Corn Station > Ukuran stasiun > Dekat sumbu: gravitasi mengecil > Gravitasi dari putaran > Menara ikon New York';
  out[`tur: pembuka masuk menembus kaca end cap A (kamera z ${(get('Menuju Copper Corn Station').camZ + 4000).toFixed(0)} m dari kaca)`] = get('Menuju Copper Corn Station').camZ > -4000 && get('Menuju Copper Corn Station').camZ < -3900;
  out[`tur: melihat sekitar saat diam pelan ke satu arah: menoleh maks ${glance.y.toFixed(1)} derajat, naik-turun maks ${glance.p.toFixed(1)} derajat (<= 10), kembali ${glance.rev || 0} kali`] = glance.n > 0 && glance.y > 0.5 && glance.y <= 10 && glance.p <= 10 && !glance.rev;
  for (const n of ['Air mancur Coriolis', 'Hutan lebat', 'Genangan di jalan kota']) {
    const W = get(n);
    out[`tur: ${n}: lari ${W.walkT.toFixed(1)} s, laju maks ${W.wMax.toFixed(2)} m/s (pemain lari 5), mata naik-turun ${((W.bobMax - W.bobMin) * 100).toFixed(1)} cm, ${W.steps} langkah`] =
      W.wMax > 4.5 && W.wMax < 5.6 && W.bobMax - W.bobMin > 0.04 && W.bobMax - W.bobMin < 0.15 && W.steps > 12;
  }
  const Fw = get('Air mancur Coriolis');
  const Li = get('Menuju Copper Corn Station').lookEnd, Lu = get('Ukuran stasiun').lookStart;
  out[`tur: akhir pembuka = awal Ukuran stasiun (adaptasi, bloom, sunrays ${JSON.stringify(Li)} / ${JSON.stringify(Lu)})`] = JSON.stringify(Li) === JSON.stringify(Lu);
  out[`tur: bunyi kaca pecah saat bola mendarat (${!!ball0.shatter})`] = !!ball0.shatter;
  out[`tur: berlari mengitari air mancur ${Fw.fMin.toFixed(1)}-${Fw.fMax.toFixed(1)} m dari pusat, menabrak ${Fw.fCol} kali`] = Fw.fMin > 11 && Fw.fMax < 13 && !Fw.fCol;
  out[`tur: sunrays mati di cuaca cerah (Ukuran ${get('Ukuran stasiun').rays}), nyala saat berawan (Hutan ${get('Hutan lebat').rays})`] = get('Ukuran stasiun').rays === false && get('Hutan lebat').rays === w0.rays;
  const Bo = get('Lempar bola melawan putaran');
  const sp = Bo.cSp || [0], q4 = Math.floor(sp.length / 4), avg = (a) => a.reduce((x, y) => x + y, 0) / Math.max(1, a.length), v1 = avg(sp.slice(1, q4)), v4 = avg(sp.slice(3 * q4));
  out[L ? `tur: bola 80 m/s 10 derajat melawan putaran: jatuh ${Math.abs(L.arc).toFixed(0)} m keliling setelah ${L.time.toFixed(1)} s; bola di bingkai (maks ${(Bo.ballOut || 9).toFixed(2)}), kamera ${v1.toFixed(0)} -> ${v4.toFixed(0)} m/s, ke samping ${(Bo.side || 0).toFixed(0)} m (mundur ${Bo.sideRev || 0}), akhir lintasan penuh di bingkai (${(Bo.pathIn || 9).toFixed(2)})` : 'tur: bola dilempar'] =
    !!L && L.time > 40 && Math.abs(L.arc) > 2500 && ball.ball.v === 80 && ball.ball.e === 10 && Bo.ballOut < 1 && v4 < 0.5 * v1 && Bo.side > 100 && !Bo.sideRev && Bo.pathIn < 1 && !Bo.under;
  const Sk0 = get('Skyway: jendela ke angkasa').anyFirst, Bo1 = Bo.anyLast, skJ = Math.hypot(wrap(Sk0.s - Bo1.s), Sk0.za - Bo1.za, Sk0.h - Bo1.h);
  out[`tur: terbang ke Skyway mulai dari kamera pengejar bola (lompat ${skJ.toFixed(1)} m < 5)`] = skJ < 5;
  let sg = 0, rev = []; const fl = [];
  for (let i = 1; i < N; i++) {                                         // terbang panjang (tanpa layar gelap) tidak berbalik arah za
    const A = st.TOUR.keys[i - 1], Q = st.TOUR.keys[i], ra = get(A.title), rq = get(Q.title);
    if (A.ext !== undefined || Q.ext !== undefined || Q.cut || Q.from || !ra.anyLast || !rq.anyLast) { sg = 0; continue; }
    const d = rq.anyLast.za - ra.anyLast.za; fl.push(d.toFixed(0)); if (Math.abs(d) < 1000 || Q.title === 'Pagi berkabut') continue;   // v2.7: gerhana -> pagi berkabut (danau di belakang, 1,5-2,3 km mundur) langsung tanpa kamera luar
    if (sg && Math.sign(d) !== sg) rev.push(`${A.title} -> ${Q.title}`); sg = Math.sign(d);
  }
  out[`tur: terbang tidak bolak-balik (dza ${fl.join(', ')}; berbalik ${rev.join('; ') || 'tidak ada'}; gerhana -> pagi berkabut dikecualikan)`] = rev.length === 0;
  const Ec = get('Gerhana Saturnus');
  out[`tur: gerhana dari tepi ladang jagung setinggi mata (${Ec.last.eyeH.toFixed(2)})`] = Math.abs(Ec.last.eyeH) < 0.1 && st.fieldList.some((f) => f.corn && Math.abs(Ec.last.za - (f.z0 - 3)) < 0.5);
  out[`tur: gerhana dekat rumah Cooper (${Math.abs(wrap(Ec.last.s - st.COOPER.s)).toFixed(0)} m keliling)`] = Math.abs(wrap(Ec.last.s - st.COOPER.s)) <= 1200;
  out[`tur: gerhana: Matahari min ${(Ec.sunEl ?? -99).toFixed(1)} derajat di atas cakrawala (> 10), meleset dari arah kamera maks ${(Ec.sunAim ?? 99).toFixed(1)} derajat (< 15)`] = Ec.sunEl > 10 && Ec.sunAim < 15;
  const Gw = get('Genangan di jalan kota'), gwD = Math.hypot(wrap(Gw.last.s - Gw.first.s), Gw.last.za - Gw.first.za);
  out[`tur: genangan sambil berjalan ${gwD.toFixed(0)} m setinggi mata`] = gwD >= 20 && Math.abs(Gw.last.eyeH) < 0.1;
  out[`tur: kamera luar tanpa adaptasi mata (${ext0.adapt}) dan bloom ${ext0.bloom}`] = ext0.adapt === false && Math.abs(ext0.bloom - 0.25) < 1e-9;
  out[`tur: gerhana dari dalam (ECL.k min ${get('Gerhana Saturnus').ecl.toFixed(2)})`] = get('Gerhana Saturnus').ecl < 0.2 && !get('Gerhana Saturnus').ext;
  out[`tur: layar gelap saat pindah kamera (maks ${fadeMax.toFixed(2)})`] = fadeMax > 0.9;
  out['tur selesai: kembali ke posisi awal, berjalan'] = !st.TOUR.on && st.player.state === 'ground' && Math.abs(st.player.za - p0.za) < 0.01 && Math.abs(st.player.theta - p0.th) < 1e-6 && !st.ext.active;
  out['tur selesai: jam, laju jam, orbit, cuaca, motor dikembalikan'] = st.clock.hour === w0.hour && st.clock.hourRate === w0.rate && st.clock.orbit === w0.orbit && st.WEATHER.mode === w0.mode && st.MOTO.on === w0.moto && st.ADAPT.on === w0.adapt && st.POST.bloom === w0.bloom && st.RAYS.on === w0.rays && document.getElementById('tourFade').style.opacity === '0';
  return out;
})()
"""

async def main():
    page_url = pathlib.Path(__file__).resolve().parent.parent.joinpath('experiences/cooper-station/index.html').as_uri()
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'], **({'executable_path': os.environ['CHROMIUM']} if os.environ.get('CHROMIUM') else {}))
        pg = await b.new_page(viewport={'width': 320, 'height': 200})
        errs = []
        pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
        await pg.goto(page_url)
        await pg.wait_for_function('window.__stationReady === true', timeout=240000)
        for k, v in (await pg.evaluate(UJI)).items(): print(('OK   ' if v else 'GAGAL'), k)
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())
