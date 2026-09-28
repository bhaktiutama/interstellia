"""Uji 19a-19b (Copper Corn Station): gerak kepala saat jalan dan lari, motor (fisika, POV, lampu depan).
- 19a: kamera naik-turun per langkah (jalan sekitar 3,6 cm puncak ke puncak, lari sekitar 7 cm), jumlah langkah = jarak / 0,72 m,
  FOV melebar saat lari lalu kembali tepat 70 derajat, level Mati = tanpa gerak, hentakan saat mendarat setelah lompat.
- 19b: naik motor (C), kecepatan puncak normal sekitar 60 km/h, belok kanan = miring ke kanan dan heading berkurang, jarak
  pengereman sesuai cengkeraman ban, berat terasa searah / melawan putaran = (omega r +- v)^2 / r, menabrak gedung berhenti,
  tidak masuk air, turun hanya saat pelan, E di dekat motor parkir = naik lagi, lift = motor ditinggal, teleport = motor ikut,
  lampu depan menyala malam (posisi di depan motor, arah ke depan) dan mati siang, kamera tanpa nilai tidak valid.
Pakai: python tools/uji_gerak.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(async () => {
  const S = window.__station, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const P = S.player, B = S.BOB, M = S.MOTO, R = S.R, cam = S.camera, K = S.keys, OM = S.OMEGA, U = S.LIGHT.uniforms;
  const frame = (n = 1) => { for (let i = 0; i < n; i++) { S.physicsStep(1 / 120); S.physicsStep(1 / 120); B.last = performance.now() - 1000 / 60; S.updateCamera(); } };
  const eyeOff = () => (R - Math.hypot(cam.position.x, cam.position.y)) - (P.h + S.CONFIG.eye);
  const finite = () => [cam.position.x, cam.position.y, cam.position.z, cam.quaternion.x, cam.quaternion.y, cam.quaternion.z, cam.quaternion.w].every(Number.isFinite);
  const walk = (n, run) => { let lo = 1, hi = -1; K.add('KeyW'); if (run) K.add('ShiftLeft');
    for (let i = 0; i < n; i++) { frame(); if (i > n / 3) { const o = eyeOff(); lo = Math.min(lo, o); hi = Math.max(hi, o); } }
    K.delete('KeyW'); K.delete('ShiftLeft'); return hi - lo; };
  const keep = B.level;
  // --- 19a: gerak kepala ---------------------------------------------------------------------------------------------
  S.respawn(); P.state = 'ground'; P.heading = 0; P.pitch = 0; B.level = 1; frame(30);
  const st0 = B.steps, d0 = P.distance, ppW = walk(180, false), nSt = B.steps - st0, dW = P.distance - d0;
  out[`jalan 3 s: naik-turun ${(ppW * 100).toFixed(1)} cm puncak ke puncak, ${nSt} langkah untuk ${dW.toFixed(2)} m (0,72 m per langkah)`] =
    ppW > 0.02 && ppW < 0.06 && Math.abs(nSt - dW / 0.72) <= 1.01;
  const ppR = walk(180, true), fovR = cam.fov;
  out[`lari 3 s: naik-turun ${(ppR * 100).toFixed(1)} cm, FOV ${fovR.toFixed(1)} derajat`] = ppR > 0.05 && ppR < 0.11 && ppR > 1.5 * ppW && fovR > 72.5 && fovR < 74.5;
  frame(150);
  out[`berhenti: FOV kembali ${cam.fov.toFixed(2)}, sisa gerak ${(Math.abs(eyeOff()) * 1000).toFixed(1)} mm (napas)`] = cam.fov === S.CONFIG.fov && Math.abs(eyeOff()) < 0.006;
  B.level = 0; frame(20);
  const pp0 = walk(150, true);
  out[`level Mati: gerak ${(pp0 * 1000).toFixed(3)} mm, FOV ${cam.fov.toFixed(2)}`] = pp0 < 1e-4 && cam.fov === S.CONFIG.fov;
  B.level = 1; frame(60);
  S.jump(); let air = 0, dip = 0; for (let i = 0; i < 120; i++) { frame(); if (P.state === 'air') air++; else dip = Math.min(dip, eyeOff()); }
  out[`lompat ${(air / 60).toFixed(2)} s lalu mendarat: kepala turun ${(dip * 100).toFixed(1)} cm lalu kembali (${(eyeOff() * 1000).toFixed(1)} mm)`] = air > 20 && dip < -0.02 && dip > -0.12 && Math.abs(eyeOff()) < 0.006;
  // --- 19b: motor ----------------------------------------------------------------------------------------------------
  S.teleport('cooper'); S.respawn(); P.heading = 0; P.pitch = 0; frame(5);
  S.toggleMoto();
  out[`naik motor: on ${M.on}, mode ${P.mode}, posisi motor = pemain`] = M.on && P.mode === 'naik motor' && Math.abs(M.za - P.za) < 1e-6;
  const z0 = M.za; K.add('KeyW'); frame(600); K.delete('KeyW');
  out[`gas 10 s di boulevard: ${(M.v * 3.6).toFixed(1)} km/h (puncak normal sekitar 60), gigi ${M.gear}, jarak ${(M.za - z0).toFixed(0)} m`] = M.v * 3.6 > 55 && M.v * 3.6 < 63 && M.gear >= 4;
  out[`kamera di motor: FOV ${cam.fov.toFixed(1)}, mata ${(eyeOff() + S.CONFIG.eye).toFixed(2)} m di atas tanah, nilai valid ${finite()}`] = cam.fov > 71.5 && Math.abs(eyeOff() + S.CONFIG.eye - 1.36) < 0.1 && finite();
  // belok kanan
  const hd0 = M.hd; K.add('KeyD'); frame(40); const leanR = M.lean, dHd = M.hd - hd0; K.delete('KeyD');
  out[`belok kanan 0,67 s pada ${(M.v * 3.6).toFixed(0)} km/h: miring ${(leanR * 180 / Math.PI).toFixed(1)} derajat ke kanan, heading ${(dHd * 180 / Math.PI).toFixed(1)} derajat`] = leanR > 0.08 && dHd < -0.05;
  K.add('KeyA'); frame(40); K.delete('KeyA'); frame(60);
  // rem
  const v0 = M.v, zb = M.za, sb = M.s; K.add('KeyS'); let tb = 0; while (M.v > 0.05 && tb < 900) { frame(); tb++; } K.delete('KeyS');
  const db = Math.hypot(M.za - zb, ((M.s - sb + 3 * Math.PI * R) % (2 * Math.PI * R)) - Math.PI * R), dbA = v0 * v0 / (2 * 0.9 * 0.85 * 9.81 * M.gFelt);
  out[`rem dari ${(v0 * 3.6).toFixed(0)} km/h: berhenti ${(tb / 60).toFixed(1)} s, ${db.toFixed(1)} m (rem saja ${dbA.toFixed(1)} m + hambatan)`] = M.v <= 0.05 && db > 0.75 * dbA && db < 1.1 * dbA;
  // berat terasa
  const gF = (v) => (OM * (R - M.h) + v) ** 2 / (R - M.h) / 9.81;
  M.hd = Math.PI / 2; M.v = 15; S.physicsStep(1 / 120); const gSp = M.gFelt;
  M.hd = -Math.PI / 2; M.v = 15; S.physicsStep(1 / 120); const gAn = M.gFelt;
  M.hd = 0; M.v = 15; S.physicsStep(1 / 120); const gAx = M.gFelt;
  out[`berat terasa 54 km/h: searah putaran ${gSp.toFixed(3)} g (analitik ${gF(15).toFixed(3)}), melawan ${gAn.toFixed(3)} g (${gF(-15).toFixed(3)}), sejajar sumbu ${gAx.toFixed(3)} g`] =
    Math.abs(gSp - gF(15)) < 0.005 && Math.abs(gAn - gF(-15)) < 0.005 && Math.abs(gAx - gF(0)) < 0.005 && gSp > 1.25 && gAn < 0.78;
  M.v = 0; frame(5);
  // tabrakan: gedung kota (collider besar), mulai 30 m di depannya (titik bebas), gas penuh mode sport ke arah +za
  S.respawn(); S.toggleMoto();
  let bld = null;
  const C = 2 * Math.PI * R, wr = (x) => ((x % C) + C * 1.5) % C - C / 2;
  for (const c of S.COL.items) {                                   // jalur 30 m di depan muka gedung bebas collider lain
    if (c[2] < 5 || c[3] < 5 || c[1] < 400 || c[1] > 2400) continue;
    const z0 = c[1] - c[3] - 30, z1 = c[1] - c[3];
    if (S.COL.items.some((o) => o !== c && Math.abs(wr(o[0] - c[0])) < o[2] + 0.6 && o[1] + o[3] > z0 - 1 && o[1] - o[3] < z1)) continue;
    if (S.inWater(c[0], z0)) continue;
    bld = c; break;
  }
  if (bld) {
    Object.assign(M, { s: bld[0], za: bld[1] - bld[3] - 30, hd: 0, v: 0 }); M.h = M.hPrev = S.groundH(M.s, M.za); P.theta = M.s / R; P.za = M.za;
    const face = bld[1] - bld[3]; K.add('KeyW'); K.add('ShiftLeft');
    let maxV = 0, maxZ = -1e9; for (let i = 0; i < 360; i++) { frame(); maxV = Math.max(maxV, M.v); maxZ = Math.max(maxZ, M.za); }
    K.delete('KeyW'); K.delete('ShiftLeft');
    out[`melaju ke gedung (muka di za ${face.toFixed(1)}): paling jauh ${(maxZ - face).toFixed(2)} m dari muka gedung, maks ${(maxV * 3.6).toFixed(0)} km/h, kini ${(M.v * 3.6).toFixed(1)} km/h`] = maxZ < face && maxV > 8 && M.v < 2;
  } else out['gedung untuk uji tabrakan tidak ditemukan'] = false;
  // air
  let wp = null;
  for (let za = 2600; za < 3300 && !wp; za += 2) for (let s = 0; s < 2 * Math.PI * R && !wp; s += 7) if (S.inWater(s, za) && !S.inWater(s, za - 30, 1)) wp = [s, za];
  if (wp) {
    Object.assign(M, { s: wp[0], za: wp[1] - 30, hd: 0, v: 0 }); P.theta = M.s / R; P.za = M.za; M.h = M.hPrev = S.groundH(M.s, M.za);
    K.add('KeyW'); let wet = false; for (let i = 0; i < 300; i++) { frame(); if (S.inWater(M.s, M.za)) wet = true; } K.delete('KeyW');
    out[`melaju ke air (s ${wp[0].toFixed(0)}, za ${wp[1]}): motor tidak pernah di air, berhenti ${(M.za - wp[1]).toFixed(1)} m dari titik air`] = !wet && M.v < 3;
  } else out['titik air untuk uji tidak ditemukan'] = false;
  // turun hanya saat pelan; parkir; E naik lagi
  M.v = 10; S.motoDismount(); const stillOn = M.on;
  M.v = 0; frame(2); S.motoDismount();
  const dP = Math.hypot(((P.theta * R - M.s + 3 * Math.PI * R) % (2 * Math.PI * R)) - Math.PI * R, P.za - M.za);
  out[`turun di 36 km/h ditolak (${stillOn}); diam: turun, parkir ${M.parked}, pemain ${dP.toFixed(2)} m dari motor`] = stillOn && !M.on && M.parked && dP > 0.5 && dP < 1.6;
  const a = S.availableAction(); if (a && a.key === 'moto') S.doAction();
  out[`aksi di dekat motor parkir: ${a ? a.key : 'tidak ada'}, naik lagi ${M.on}`] = !!a && a.key === 'moto' && M.on;
  // teleport membawa motor, lift meninggalkan motor
  S.teleport('hill'); frame(2);
  out[`teleport ke bukit di atas motor: motor ikut (${Math.hypot(M.za - P.za, M.s - P.theta * R).toFixed(3)} m)`] = M.on && Math.hypot(M.za - P.za, M.s - P.theta * R) < 0.01;
  S.enterLift(); frame(2);
  out[`lift: motor ditinggal (on ${M.on}, parkir ${M.parked}), state ${P.state}`] = !M.on && M.parked && P.state === 'lift';
  // lampu depan
  S.respawn(); S.toggleMoto(); M.hd = 0; frame(3);
  const hk = S.clock.hour; S.clock.hour = 23; S.updateLighting(); frame(1); S.updateLighting(); frame(1);
  const hd = U.uL_HeadDir.value, hp = U.uL_Head.value, fwdZ = hd.z, lampAhead = hp.z + 4000 - M.za;
  out[`malam: lampu depan ${hp.w.toFixed(2)}, ${lampAhead.toFixed(2)} m di depan pusat motor, arah sorot z ${fwdZ.toFixed(3)}, kolam (s ${U.uL_HeadG.value.x.toFixed(0)}, za ${U.uL_HeadG.value.y.toFixed(0)})`] =
    hp.w > 0.9 && lampAhead > 0.5 && lampAhead < 0.9 && fwdZ > 0.99 && Math.abs(U.uL_HeadG.value.y - M.za) < 1e-3;
  S.clock.hour = 12; S.updateLighting(); frame(1); S.updateLighting(); frame(1);
  out[`siang: lampu depan ${U.uL_Head.value.w.toFixed(2)}`] = U.uL_Head.value.w === 0;
  S.clock.hour = 23; S.updateLighting(); S.motoDismount(); frame(2);
  out[`malam, motor diparkir: lampu depan ${U.uL_Head.value.w.toFixed(2)}, model terlihat ${S.MOTO.mesh.visible}`] = U.uL_Head.value.w === 0 && S.MOTO.mesh.visible;
  S.clock.hour = hk; S.updateLighting();
  // tampilan: render beberapa frame sungguhan di atas motor (malam) tanpa error
  S.toggleMoto(); S.clock.hour = 22; await wait(1500);
  out[`render di atas motor: kamera valid ${finite()}, dasbor digambar`] = finite();
  S.motoDismount(); B.level = keep; S.clock.hour = hk; S.respawn();
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
