"""Uji tahap 12d (Copper Corn Station): siklus tanam gandum dan mesin ladang, mode foto (FOV, blur, simpan PNG,
semua dikembalikan saat keluar), tur sinematik v2.1 (22 titik, jam 12:00 sampai 07:00, hujan di bawah awan, genangan, burung formasi V, motor ke kota,
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
  // C3: tur sinematik v2.3 (22 titik; tur hanya mengatur jam, awan, posisi kamera, motor dan lemparan lewat keadaan biasa)
  const p0 = { th: st.player.theta, za: st.player.za };
  const w0 = { hour: st.clock.hour, rate: st.clock.hourRate, orbit: st.clock.orbit, mode: st.WEATHER.mode, moto: st.MOTO.on, adapt: st.ADAPT.on, bloom: st.POST.bloom };
  st.startTour();
  const hour0 = st.clock.hour, N = st.TOUR.keys.length, CIRC = 2 * Math.PI * st.R;
  const wrap = (x) => x - CIRC * Math.round(x / CIRC);
  let bad = false, maxH = 0, steps = 0, fadeMax = 0; const ext0 = {};
  const idx = new Set(), K = {}, nSub = Math.round(0.05 / st.STEP), ball0 = st.TOUR.keys.find((q) => q.ball);
  for (let k = 0; k < 8000 && st.TOUR.on; k++, steps++) {
    const key = st.TOUR.keys[st.TOUR.i];
    for (let q = 0; q < nSub; q++) st.physicsStep(st.STEP);           // urutan seperti worldStep
    st.stepTour(0.05); if (!st.TOUR.on) break;
    st.updateCamera(); st.stepBirds(0.05); st.updateRain(0.05); st.updateFar(); st.updateClouds(0.05);
    idx.add(st.TOUR.i);
    const P = st.player, ps = P.theta * st.R, hold = st.TOUR.t > (key.dur || 0);
    const r = K[key.title] || (K[key.title] = { rain: 0, wetMin: 1, ecl: 1, ext: false, cloud: 0, bird: 1e9, z0: st.MOTO.za, ground: false });
    r.hour = st.clock.hour; r.rain = Math.max(r.rain, st.RAIN.k); r.ecl = Math.min(r.ecl, st.ECL.k); r.ext = r.ext || st.ext.active; r.rainEnd = st.RAIN.k;
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
      if (key.ball && ball0 && ball0.bb && ball0.bb.t > 0 && !ball0.bb.done) {   // kamera menghadap bola, jarak ke bola
        const b = ball0.bb.pos, eye = { x: 0, y: 0, z: 0 }, th = P.theta, rr = st.R - P.h - st.CONFIG.eye;
        const ex = rr * Math.cos(th), ey = rr * Math.sin(th), ez = P.za - st.R * 4;
        const dx = b.x - ex, dy = b.y - ey, dzz = b.z - (P.za - 4000), up = [-Math.cos(th), -Math.sin(th)], tg = [-Math.sin(th), Math.cos(th)];
        const dt = dx * tg[0] + dy * tg[1], du = dx * up[0] + dy * up[1], dist = Math.hypot(dx, dy, dzz);
        const hd = Math.atan2(dt, dzz), pt = Math.atan2(du, Math.hypot(dt, dzz));
        const err = Math.hypot(wrap((P.heading - hd) * st.R) / st.R * Math.cos(pt), P.pitch - pt) * 180 / Math.PI;
        r.ballAim = Math.max(r.ballAim || 0, err); if (r.ballD0 === undefined) r.ballD0 = dist; r.ballD1 = dist;
        r.under = (r.under || 0) + (P.h < st.groundH(ps, P.za) - 0.01 ? 1 : 0);
      }
    }
    if (key.moto && st.MOTO.on) {
      if (r.s0 === undefined) { r.s0 = st.MOTO.s; r.d0 = (st.districtAt(st.MOTO.s, st.MOTO.za) || {}).name; r.zaMin = 1e9; r.zaMax = -1e9; r.ds = 0; r.sPrev = st.MOTO.s; }
      r.ds += wrap(r.sPrev - st.MOTO.s); r.sPrev = st.MOTO.s;          // jarak keliling ke arah s berkurang (melawan putaran)
      r.zaMin = Math.min(r.zaMin, st.MOTO.za); r.zaMax = Math.max(r.zaMax, st.MOTO.za);
      r.d1 = (st.districtAt(st.MOTO.s, st.MOTO.za) || {}).name; r.g1 = st.MOTO.gFelt;
      r.v1 = st.MOTO.v; r.vMin = Math.min(r.vMin ?? 1e9, st.MOTO.v); r.ground = r.ground || P.state === 'ground';
    }
    if (st.ext.active && !ext0.seen) Object.assign(ext0, { seen: true, adapt: st.ADAPT.on, bloom: st.POST.bloom });
    fadeMax = Math.max(fadeMax, +document.getElementById('tourFade').style.opacity || 0);
    if (!isFinite(P.theta + P.za + P.h + P.heading + P.pitch + st.clock.hour + st.camera.position.length())) bad = true;
    if (!st.ext.active) maxH = Math.max(maxH, P.h);
  }
  const T = steps * 0.05, get = (n) => K[n] || {}, eye = st.TOUR.keys.filter((q) => q.h === 0).length;
  const ball = st.TOUR.keys.find((q) => q.ball), L = ball && ball.landing, deg = 180 / Math.PI;
  out[`tur: ${idx.size} dari ${N} titik, ${T.toFixed(0)} s (target 260-320 s), tanpa NaN`] = !bad && idx.size === N && N === 22 && T > 260 && T < 320;
  out[`tur: ${eye} titik setinggi mata (>= 9)`] = eye >= 9;
  out[`tur: tinggi maksimum ${maxH.toFixed(0)} m (tidak melewati sumbu)`] = maxH < st.R - 30;
  out[`tur: jam mulai ${hour0.toFixed(2)}, akhir ${(get('Meninggalkan stasiun').hour || 0).toFixed(2)}`] = hour0 === 12 && Math.abs(get('Meninggalkan stasiun').hour - 7) < 0.05;
  out['tur: pembuka dan penutup di kamera luar'] = !!get('Menuju Copper Corn Station').ext && !!get('Meninggalkan stasiun').ext;
  const H = get('Hujan miring');
  out[`tur: hujan di sungai (RAIN.k ${H.rain.toFixed(2)}, awan di atas kamera ${H.cloud.toFixed(2)} > 0,12), siang tanpa hujan (${get('Ukuran stasiun').rain.toFixed(2)})`] = H.rain > 0.5 && H.cloud > 0.12 && get('Ukuran stasiun').rain < 0.05;
  const G = get('Genangan di jalan kota');
  out[`tur: genangan (basah min ${G.wetMin.toFixed(2)}, hujan akhir ${G.rainEnd.toFixed(2)}, awan di jalan ${G.cloud.toFixed(2)})`] = G.wetMin > 0.5 && G.rainEnd < 0.1 && G.cloud > 0.12;
  const B = get('Burung di bawah awan'), Bl = st.TOUR.keys.find((q) => q.track).land || {};
  out[`tur: kawanan burung: awal ${(B.flock0 ?? 1e9).toFixed(0)} m, akhir ${(B.flock ?? 1e9).toFixed(0)} m, kamera di tanah (mata ${B.last.eyeH.toFixed(2)} m + 1,7), menengadah ${(B.ptBird * deg).toFixed(0)} derajat, meleset ${B.aimErr.toFixed(1)} derajat`] =
    (B.flock0 ?? 1e9) < 40 && Math.abs(B.last.eyeH) < 0.1 && B.ptBird > 20 / deg && B.aimErr < 15 && !st.colAt(Bl.s, Bl.za, 1) && !st.inWater(Bl.s, Bl.za, 1);
  const Sk = get('Skyway: jendela ke angkasa'), skM = ((Sk.last.za % 50) + 50) % 50;
  out[`tur: Skyway za ${Sk.last.za.toFixed(1)}, ${Math.min(skM, 50 - skM).toFixed(1)} m dari balok jendela (>= 10)`] = Math.min(skM, 50 - skM) >= 10;
  const Dk = get('Dek pandang malam'), dkK = (st.R - st.DECK.h) / st.R, dkFloor = st.groundH(Dk.last.s, Dk.last.za) + st.DECK.h, dkRail = st.DECK.half - Math.abs(wrap(Dk.last.s - st.DECK.s)) * dkK;
  out[`tur: dek mata ${(Dk.last.h - dkFloor).toFixed(2)} m + 1,7 di atas lantai, ${dkRail.toFixed(2)} m dari pagar`] = Math.abs(Dk.last.h - dkFloor) < 0.1 && dkRail > 0 && dkRail < 1;
  const Hu = get('Hutan lebat'), huD = Math.hypot(wrap(Hu.last.s - Hu.first.s), Hu.last.za - Hu.first.za);
  out[`tur: hutan berjalan ${huD.toFixed(0)} m setinggi mata (${Hu.last.eyeH.toFixed(2)}), dari dalam hutan ke luar`] = huD >= 25 && Math.abs(Hu.last.eyeH) < 0.1 && st.inForest(Hu.first.s, Hu.first.za) && !st.inForest(Hu.last.s, Hu.last.za);
  const M = get('Naik motor ke New York');
  out[`tur: motor jalan lingkar za ${M.zaMin.toFixed(1)}-${M.zaMax.toFixed(1)} (rute bus merah 500), ${M.ds.toFixed(0)} m keliling ${M.d0} -> ${M.d1}, ${(M.vMin * 3.6).toFixed(0)}-${(M.v1 * 3.6).toFixed(0)} km/h, terasa ${M.g1.toFixed(2)} g`] =
    M.ground && M.ds > 800 && M.zaMin > 490 && M.zaMax < 500 && M.d0 === 'Galileo' && M.d1 === 'New York' && M.vMin > 20 && M.g1 < 0.5;
  const Bo = get('Lempar bola melawan putaran');
  out[L ? `tur: bola 80 m/s 10 derajat melawan putaran: jatuh ${Math.abs(L.arc).toFixed(0)} m keliling setelah ${L.time.toFixed(1)} s; kamera menghadap bola (meleset maks ${(Bo.ballAim || 99).toFixed(1)} derajat), jarak ${(Bo.ballD0 || 0).toFixed(0)} -> ${(Bo.ballD1 || 0).toFixed(0)} m, di bawah tanah ${Bo.under || 0} kali` : 'tur: bola dilempar'] =
    !!L && Math.abs(L.arc) > 2500 && Math.abs(L.arc) < 3200 && L.time > 40 && L.time < 50 && ball.ball.v === 80 && ball.ball.e === 10 && Bo.ballAim < 10 && Bo.ballD0 < 20 && Bo.ballD1 > Bo.ballD0 && Bo.ballD1 < 90 && !Bo.under;
  const Ec = get('Gerhana Saturnus');
  out[`tur: gerhana dari tepi ladang jagung setinggi mata (${Ec.last.eyeH.toFixed(2)})`] = Math.abs(Ec.last.eyeH) < 0.1 && st.fieldList.some((f) => f.corn && Math.abs(Ec.last.za - (f.z0 - 3)) < 0.5);
  const Gw = get('Genangan di jalan kota'), gwD = Math.hypot(wrap(Gw.last.s - Gw.first.s), Gw.last.za - Gw.first.za);
  out[`tur: genangan sambil berjalan ${gwD.toFixed(0)} m setinggi mata`] = gwD >= 20 && Math.abs(Gw.last.eyeH) < 0.1;
  out[`tur: kamera luar tanpa adaptasi mata (${ext0.adapt}) dan bloom ${ext0.bloom}`] = ext0.adapt === false && Math.abs(ext0.bloom - 0.25) < 1e-9;
  out[`tur: gerhana dari dalam (ECL.k min ${get('Gerhana Saturnus').ecl.toFixed(2)})`] = get('Gerhana Saturnus').ecl < 0.2 && !get('Gerhana Saturnus').ext;
  out[`tur: layar gelap saat pindah kamera (maks ${fadeMax.toFixed(2)})`] = fadeMax > 0.9;
  out['tur selesai: kembali ke posisi awal, berjalan'] = !st.TOUR.on && st.player.state === 'ground' && Math.abs(st.player.za - p0.za) < 0.01 && Math.abs(st.player.theta - p0.th) < 1e-6 && !st.ext.active;
  out['tur selesai: jam, laju jam, orbit, cuaca, motor dikembalikan'] = st.clock.hour === w0.hour && st.clock.hourRate === w0.rate && st.clock.orbit === w0.orbit && st.WEATHER.mode === w0.mode && st.MOTO.on === w0.moto && st.ADAPT.on === w0.adapt && st.POST.bloom === w0.bloom && document.getElementById('tourFade').style.opacity === '0';
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
