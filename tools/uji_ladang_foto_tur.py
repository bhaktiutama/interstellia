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
  // C3: tur sinematik v2.1 (22 titik; tur hanya mengatur jam, awan, posisi kamera, motor dan lemparan lewat keadaan biasa)
  const p0 = { th: st.player.theta, za: st.player.za };
  const w0 = { hour: st.clock.hour, rate: st.clock.hourRate, orbit: st.clock.orbit, mode: st.WEATHER.mode, moto: st.MOTO.on };
  st.startTour();
  const hour0 = st.clock.hour, N = st.TOUR.keys.length, CIRC = 2 * Math.PI * st.R;
  const wrap = (x) => x - CIRC * Math.round(x / CIRC);
  let bad = false, maxH = 0, steps = 0, fadeMax = 0;
  const idx = new Set(), K = {}, nSub = Math.round(0.05 / st.STEP);
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
    }
    if (key.moto && st.MOTO.on) {
      if (r.s0 === undefined) { r.s0 = st.MOTO.s; r.d0 = (st.districtAt(st.MOTO.s, st.MOTO.za) || {}).name; r.zaMin = 1e9; r.zaMax = -1e9; r.ds = 0; r.sPrev = st.MOTO.s; }
      r.ds += wrap(r.sPrev - st.MOTO.s); r.sPrev = st.MOTO.s;          // jarak keliling ke arah s berkurang (melawan putaran)
      r.zaMin = Math.min(r.zaMin, st.MOTO.za); r.zaMax = Math.max(r.zaMax, st.MOTO.za);
      r.d1 = (st.districtAt(st.MOTO.s, st.MOTO.za) || {}).name; r.g1 = st.MOTO.gFelt;
      r.v1 = st.MOTO.v; r.vMin = Math.min(r.vMin ?? 1e9, st.MOTO.v); r.ground = r.ground || P.state === 'ground';
    }
    fadeMax = Math.max(fadeMax, +document.getElementById('tourFade').style.opacity || 0);
    if (!isFinite(P.theta + P.za + P.h + P.heading + P.pitch + st.clock.hour + st.camera.position.length())) bad = true;
    if (!st.ext.active) maxH = Math.max(maxH, P.h);
  }
  const T = steps * 0.05, get = (n) => K[n] || {}, eye = st.TOUR.keys.filter((q) => q.h === 0).length;
  const ball = st.TOUR.keys.find((q) => q.ball), L = ball && ball.landing;
  out[`tur: ${idx.size} dari ${N} titik, ${T.toFixed(0)} s (target 200-260 s), tanpa NaN`] = !bad && idx.size === N && N === 22 && T > 200 && T < 260;
  out[`tur: ${eye} titik setinggi mata (>= 9)`] = eye >= 9;
  out[`tur: tinggi maksimum ${maxH.toFixed(0)} m (tidak melewati sumbu)`] = maxH < st.R - 30;
  out[`tur: jam mulai ${hour0.toFixed(2)}, akhir ${(get('Meninggalkan stasiun').hour || 0).toFixed(2)}`] = hour0 === 12 && Math.abs(get('Meninggalkan stasiun').hour - 7) < 0.05;
  out['tur: pembuka dan penutup di kamera luar'] = !!get('Menuju Copper Corn Station').ext && !!get('Meninggalkan stasiun').ext;
  const H = get('Hujan miring');
  out[`tur: hujan di sungai (RAIN.k ${H.rain.toFixed(2)}, awan di atas kamera ${H.cloud.toFixed(2)} > 0,12), siang tanpa hujan (${get('Ukuran stasiun').rain.toFixed(2)})`] = H.rain > 0.5 && H.cloud > 0.12 && get('Ukuran stasiun').rain < 0.05;
  const G = get('Genangan di jalan kota');
  out[`tur: genangan (basah min ${G.wetMin.toFixed(2)}, hujan akhir ${G.rainEnd.toFixed(2)}, awan di jalan ${G.cloud.toFixed(2)})`] = G.wetMin > 0.5 && G.rainEnd < 0.1 && G.cloud > 0.12;
  const B = get('Burung di bawah awan');
  out[`tur: burung formasi V dekat kamera (${B.bird.toFixed(0)} m < 60)`] = B.bird < 60;
  const M = get('Naik motor ke New York');
  out[`tur: motor jalan lingkar za ${M.zaMin.toFixed(1)}-${M.zaMax.toFixed(1)} (rute bus merah 500), ${M.ds.toFixed(0)} m keliling ${M.d0} -> ${M.d1}, ${(M.vMin * 3.6).toFixed(0)}-${(M.v1 * 3.6).toFixed(0)} km/h, terasa ${M.g1.toFixed(2)} g`] =
    M.ground && M.ds > 800 && M.zaMin > 490 && M.zaMax < 500 && M.d0 === 'Galileo' && M.d1 === 'New York' && M.vMin > 20 && M.g1 < 0.5;
  out[L ? `tur: bola searah putaran ${Math.abs(L[0].arc).toFixed(1)} m / ${L[0].time.toFixed(2)} s, melawan ${Math.abs(L[1].arc).toFixed(1)} m / ${L[1].time.toFixed(2)} s` : 'tur: bola dilempar'] = !!L && L[0].arc > 0 && L[1].arc < 0 && L[1].time > L[0].time;
  out[`tur: gerhana dari dalam (ECL.k min ${get('Gerhana Saturnus').ecl.toFixed(2)})`] = get('Gerhana Saturnus').ecl < 0.2 && !get('Gerhana Saturnus').ext;
  out[`tur: layar gelap saat pindah kamera (maks ${fadeMax.toFixed(2)})`] = fadeMax > 0.9;
  out['tur selesai: kembali ke posisi awal, berjalan'] = !st.TOUR.on && st.player.state === 'ground' && Math.abs(st.player.za - p0.za) < 0.01 && Math.abs(st.player.theta - p0.th) < 1e-6 && !st.ext.active;
  out['tur selesai: jam, laju jam, orbit, cuaca, motor dikembalikan'] = st.clock.hour === w0.hour && st.clock.hourRate === w0.rate && st.clock.orbit === w0.orbit && st.WEATHER.mode === w0.mode && st.MOTO.on === w0.moto && document.getElementById('tourFade').style.opacity === '0';
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
