"""Uji Copper Corn Station tahap 30 (Jupiter sebagai pilihan planet, orbit 150.000 km) dan tahap 31 (bulan Saturnus dan Jupiter).
Per planet (?planet=saturn|jupiter): periode orbit = Kepler (37,57 jam / 9,008 jam), setengah sudut gerhana = asin(R/r), diameter sudut planet dari stasiun
(26,8 / 56,9 derajat), lama gerhana per orbit (2,80 / 1,42 jam) dan penumbra, kunci teks (planet disebut sesuai pilihan, angka bantuan 37,6 / 9,0 jam),
pemilih planet di layar mulai, pilihan tersimpan (cooperStation.planet), render langit jauh tanpa nilai tidak valid dan planet tergambar.
Bulan: jumlah (7 / 4), jarak ke pusat planet = a, periode (posisi kembali setelah 1 periode NASA), periode Kepler dalam 0,5% dari NASA, rotasi sinkron
(sumbu +x objek ke luar dari planet), jarak terdekat hasil pemindai di antara |a - r| dan a + r, sudut tampak = rumus, lompat ke konjungsi tiba di jarak itu,
bulan masuk bayangan planet meredup (uK = 0 di umbra), bulan terang di sisi Matahari tergambar, tanpa nilai tidak valid, ?bulan=0 tanpa bulan.
Saturnus identik: dengan ?bulan=0 render langit jauh dari 3 arah sama dengan komit sebelum tahap 30 (0 nilai berbeda).
Pakai: python tools/uji_planet.py   (butuh playwright; THREE_LOCAL=<folder three/build>, CHROMIUM=<executable> opsional)"""
import asyncio, os, pathlib, subprocess
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE_COMMIT = os.environ.get('BASE_COMMIT', '24b174e')            # komit sebelum tahap 30 (rencana Jupiter dan bulan, Copper belum diubah)

UJI = r"""
(async (key) => {
  const S = window.__station, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const THREE = S.THREE || (await import('https://cdn.jsdelivr.net/npm/three@0.186.1/build/three.module.js'));
  const DEG = Math.PI / 180, TAU = 2 * Math.PI, PL = S.PLANET, E = S.ECL, SAT = S.SATURN, T = S.T_ORB;
  const want = { saturn: { T: 37.57, half: 13.40, diam: 26.8, ecl: 2.80, n: 7 }, jupiter: { T: 9.008, half: 28.46, diam: 56.9, ecl: 1.42, n: 4 } }[key];
  out[`${key}: planet = ${PL.key}`] = PL.key === key;
  out[`${key}: periode ${(T / 3600).toFixed(3)} jam = Kepler 2 pi sqrt(r^3 / GM) (target ${want.T})`] = Math.abs(T / 3600 - want.T) < 0.02 && Math.abs(T - 2 * Math.PI * Math.sqrt(Math.pow(PL.orbitR * 1e6, 3) / PL.GM)) < 1;
  out[`${key}: setengah sudut gerhana ${(E.half / DEG).toFixed(2)} derajat (target ${want.half}), diameter sudut planet ${(2 * Math.asin(SAT.rEq / S.saturn.position.length()) / DEG).toFixed(1)} derajat (target ${want.diam})`] =
    Math.abs(E.half / DEG - want.half) < 0.05 && Math.abs(2 * Math.asin(SAT.rEq / Math.hypot(...S.saturn.position.toArray().map((x, i) => (S.updateFar(), x)))) / DEG - want.diam) < 0.1;
  // lama gerhana satu orbit
  let dark = 0; const step = Math.max(5, T / 4000);
  for (let tt = 0; tt < T; tt += step) { S.clock.orbit = tt; S.updateFar(); if (E.k < 0.5) dark += step; }
  out[`${key}: lama gerhana ${(dark / 3600).toFixed(3)} jam per orbit (target ${want.ecl} +- 3%)`] = Math.abs(dark / 3600 - want.ecl) / want.ecl < 0.03;
  // teks
  const tx = S.t('Orbit Saturnus: {x}x', { x: 1 }), hp = S.t('Lompat ke 2 menit sebelum gerhana Saturnus (sekali tiap orbit 37,6 jam, lamanya sekitar 2,8 jam). Lihat lewat kaca end cap B atau kamera luar (V)');
  out[`${key}: teks "${tx}" / bantuan "${hp.slice(0, 60)}..."`] = key === 'saturn' ? tx.includes('Saturnus') && hp.includes('37,6 jam') : tx.includes('Jupiter') && !tx.includes('Saturn') && hp.includes('Jupiter') && hp.includes('9,0 jam') && hp.includes('1,4 jam');
  out[`${key}: pemilih planet: ${[...document.querySelectorAll('#planetPick button')].map((b) => b.textContent + (b.classList.contains('on') ? '*' : '')).join(' ')}`] =
    document.querySelectorAll('#planetPick button').length === 2 && document.querySelector('#planetPick button.on').dataset.planet === key;
  // render langit jauh
  const W = 256, H = 256, rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.FloatType }), cam = new THREE.PerspectiveCamera(key === 'jupiter' ? 75 : 40, 1, 1, 20000);
  const shoot = (lookAt) => {
    S.clock.orbit = 0; S.updateFar(); cam.position.set(0, 0, 0); cam.lookAt(lookAt); cam.updateMatrixWorld(true);
    const U = S.saturn.userData.U; U.uCamL.value.copy(S.saturn.position).negate().applyQuaternion(S.saturn.quaternion.clone().invert());
    S.renderer.setRenderTarget(rt); S.renderer.setClearColor(0x000000, 1); S.renderer.clear(); S.renderer.render(S.farScene, cam); S.renderer.setRenderTarget(null);
    const px = new Float32Array(W * H * 4); S.renderer.readRenderTargetPixels(rt, 0, 0, W, H, px);
    let sum = 0, bad = 0, ctr = 0; for (let i = 0; i < px.length; i += 4) { for (let c = 0; c < 3; c++) if (!Number.isFinite(px[i + c]) || px[i + c] < 0) bad++; sum += px[i] + px[i + 1] + px[i + 2]; }
    for (let y = 120; y < 136; y++) for (let x = 120; x < 136; x++) { const i = (y * W + x) * 4; ctr += px[i] + px[i + 1] + px[i + 2]; }
    return { mean: sum / (W * H * 3), bad, ctr: ctr / (256 * 3), px };
  };
  const dirs = [S.saturn.position.clone(), new THREE.Vector3(1, 0.3, -0.5).add(S.saturn.position), new THREE.Vector3(-1, 0.4, 0.8).add(S.saturn.position)];
  const shots = dirs.map((d) => shoot(d)); const nbad = shots.reduce((s, x) => s + x.bad, 0);
  out[`${key}: render langit jauh: tanpa nilai tidak valid (${nbad}), planet di tengah terang ${shots[0].ctr.toFixed(4)} > 0,02`] = nbad === 0 && shots[0].ctr > 0.02;
  // bulan
  const M = S.MOONS;
  out[`${key}: bulan ${M.list.length} (target ${want.n}): ${M.list.map((m) => m.name).join(', ')}`] = M.on && M.list.length === want.n;
  let okPos = true, okKep = true, okSync = true, infoA = [];
  for (const m of M.list) {
    const Pm = TAU / m.w, p0 = new THREE.Vector3(), p1 = new THREE.Vector3(); S.clock.orbit = 12345; S.updateFar();
    const tK = 2 * Math.PI * Math.sqrt(Math.pow(m.a * 1e6, 3) / PL.GM) / 86400;
    okKep = okKep && Math.abs(tK - m.P) / m.P < 0.005;
    const l0 = new THREE.Vector3(), l1 = new THREE.Vector3();
    const loc = (tt, o) => { const Mm = m.M0 + m.w * tt, i = m.inc * DEG; return o.set(m.a * Math.cos(Mm), m.a * Math.sin(Mm) * Math.sin(i), m.a * Math.sin(Mm) * Math.cos(i)); };
    loc(100, l0); loc(100 + Pm, l1);
    okPos = okPos && l0.distanceTo(l1) < 1e-6 * m.a && Math.abs(l0.length() - m.a) < 1e-9 * m.a;
    // sinkron: sumbu +x objek searah posisi (proyeksi ke bidang khatulistiwa)
    S.clock.orbit = 777; S.updateFar();
    const ax = new THREE.Vector3(1, 0, 0).applyAxisAngle(new THREE.Vector3(0, 1, 0), m.mesh.rotation.y), rad = m.mesh.position.clone().normalize();
    okSync = okSync && ax.dot(rad) > 0.95;
  }
  out[`${key}: posisi kembali setelah 1 periode NASA dan jarak = a (${okPos}), periode Kepler dalam 0,5% (${okKep}), rotasi sinkron (${okSync})`] = okPos && okKep && okSync;
  // jarak terdekat dan sudut, lompat ke konjungsi
  let okJ = true, rows = [];
  for (const m of M.list) {
    S.clock.orbit = 0; S.updateFar(); S.jumpToMoon(m.i); S.updateFar();
    const d = m.dist, lo = Math.abs(m.a - PL.orbitR), hi = m.a + PL.orbitR, ang = 2 * Math.atan(m.R / 1000 / d) / DEG, angLo = 2 * Math.atan(m.R / 1000 / lo) / DEG;
    rows.push(`${m.name} ${(d * 1000).toFixed(0)} km ${ang.toFixed(2)} derajat`);
    okJ = okJ && d >= lo - 1e-6 && d <= hi && Math.abs(m.ang - ang) < 0.01 && ang <= angLo + 1e-6 && Math.abs(S.moonDistAt(m, S.clock.orbit) - d) < 1e-6;
  }
  out[`${key}: lompat ke konjungsi (antara |a - r| dan a + r, sudut = rumus): ${rows.join('; ')}`] = okJ;
  // bulan masuk bayangan planet: cari bulan dan waktu dengan uK = 0
  let umbra = null;
  for (const m of M.list) { for (let tt = 0; tt < 40 * 86400 && !umbra; tt += 90) { S.clock.orbit = tt; S.updateFar(); if (m.mat.uniforms.uK.value === 0) umbra = { m, tt }; } if (umbra) break; }
  out[`${key}: gerhana bulan: ${umbra ? umbra.m.name + ' di umbra pada ' + (umbra.tt / 86400).toFixed(2) + ' hari (uK 0)' : 'tidak ditemukan dalam 40 hari'}`] = !!umbra;
  // bulan tergambar: arahkan kamera ke bulan terang (Enceladus / Io) saat konjungsi, FOV kecil
  const m0 = M.list[key === 'jupiter' ? 0 : 1]; S.clock.orbit = 0; S.updateFar(); S.jumpToMoon(m0.i); S.updateFar();
  let lit = false, cur = null;
  for (let k = 0; k < 400 && !lit; k++) {                                   // geser waktu hingga bulan di sisi terang (fase > 0,3)
    S.clock.orbit += 600; S.updateFar();
    const w = new THREE.Vector3(); m0.mesh.getWorldPosition(w); const toC = w.clone().negate().normalize(), ph = 0.5 * (1 + S.SUN_DIR.dot(toC));
    if (ph > 0.6 && m0.mat.uniforms.uK.value === 1) lit = true;
  }
  const wp = new THREE.Vector3(); m0.mesh.getWorldPosition(wp); const cm = new THREE.PerspectiveCamera(Math.max(0.5, 3 * m0.ang), 1, 1, 20000); cm.lookAt(wp); cm.updateMatrixWorld(true);
  S.renderer.setRenderTarget(rt); S.renderer.setClearColor(0x000000, 1); S.renderer.clear(); S.renderer.render(S.farScene, cm); S.renderer.setRenderTarget(null);
  const px = new Float32Array(W * H * 4); S.renderer.readRenderTargetPixels(rt, 0, 0, W, H, px);
  let c0 = 0, cb = 0; for (let y = 120; y < 136; y++) for (let x = 120; x < 136; x++) { const i = (y * W + x) * 4; c0 += px[i] + px[i + 1] + px[i + 2]; if (!Number.isFinite(px[i])) cb++; }
  out[`${key}: ${m0.name} di sisi terang tergambar (terang tengah ${(c0 / 768).toFixed(3)} > 0,01, tidak valid ${cb})`] = lit && c0 / 768 > 0.01 && cb === 0;
  // titik saat bulan jauh
  const pa = M.pts.geometry.attributes.aB.array; out[`${key}: kecerahan titik bulan terhingga dan <= 1`] = [...pa].every((x) => Number.isFinite(x) && x >= 0 && x <= 1);
  rt.dispose(); S.clock.orbit = 0; S.updateFar();
  return out;
})
"""

async def main():
    local = os.environ.get('THREE_LOCAL')
    errs = []
    base_file = ROOT / 'experiences/cooper-station/_baseline30.html'
    async with async_playwright() as p:
        exe = os.environ.get('CHROMIUM')
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'], **({'executable_path': exe} if exe else {}))

        async def page(path, q):
            pg = await b.new_page(viewport={'width': 320, 'height': 200})
            pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
            pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' else None)
            if local:
                async def serve(route):
                    await route.fulfill(path=str(pathlib.Path(local) / route.request.url.rsplit('/', 1)[-1]), content_type='text/javascript', headers={'Access-Control-Allow-Origin': '*'})
                await pg.route('https://cdn.jsdelivr.net/**', serve)
            await pg.goto(ROOT.joinpath(path).as_uri() + q, wait_until='domcontentloaded', timeout=240000)
            await pg.wait_for_function('window.__stationReady === true', timeout=300000)
            return pg
        hasil = {}
        for key in ['saturn', 'jupiter']:
            pg = await page('experiences/cooper-station/index.html', f'?lang=id&planet={key}')
            hasil.update(await pg.evaluate(UJI, key))
            if key == 'jupiter':
                hasil['jupiter: bantuan English: planet dan angka'] = await pg.evaluate("""(() => { const S = window.__station; S.setLang('en'); const a = S.t('Lompat ke 2 menit sebelum gerhana Saturnus (sekali tiap orbit 37,6 jam, lamanya sekitar 2,8 jam). Lihat lewat kaca end cap B atau kamera luar (V)'); S.setLang('id'); return a.includes('Jupiter') && a.includes('9.0-hour') && a.includes('1.4 hours') && !a.includes('Saturn'); })()""")
            await pg.close()
        # pilihan tersimpan: tanpa ?planet= mengikuti localStorage cooperStation.planet
        pg = await page('experiences/cooper-station/index.html', '?lang=id&planet=jupiter')
        await pg.evaluate("localStorage.setItem('cooperStation.planet', 'jupiter')"); await pg.close()
        pg = await b.new_page(viewport={'width': 320, 'height': 200})
        if local:
            async def serve2(route):
                await route.fulfill(path=str(pathlib.Path(local) / route.request.url.rsplit('/', 1)[-1]), content_type='text/javascript', headers={'Access-Control-Allow-Origin': '*'})
            await pg.route('https://cdn.jsdelivr.net/**', serve2)
        await pg.goto(ROOT.joinpath('experiences/cooper-station/index.html').as_uri() + '?lang=id', wait_until='domcontentloaded', timeout=240000)
        await pg.evaluate("localStorage.setItem('cooperStation.planet', 'jupiter')"); await pg.reload(wait_until='domcontentloaded')
        await pg.wait_for_function('window.__stationReady === true', timeout=300000)
        hasil['cooperStation.planet = jupiter dipakai tanpa ?planet='] = await pg.evaluate("window.__station.PLANET.key === 'jupiter'")
        await pg.evaluate("localStorage.removeItem('cooperStation.planet')"); await pg.close()
        # Saturnus identik dengan komit sebelum tahap 30 (?bulan=0)
        try:
            src = subprocess.check_output(['git', 'show', f'{BASE_COMMIT}:experiences/cooper-station/index.html'], cwd=ROOT)
            base_file.write_bytes(src)
            JS = r"""(async () => { const S = window.__station; const THREE = S.THREE || (await import('https://cdn.jsdelivr.net/npm/three@0.186.1/build/three.module.js'));
              const W = 256, H = 256, rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.FloatType }), cam = new THREE.PerspectiveCamera(40, 1, 1, 20000), res = [];
              for (const o of [0, 5000, 20000]) for (const d of [[0, 0, 0], [1, 0.3, -0.5], [-1, 0.4, 0.8]]) {
                S.clock.orbit = o; S.updateFar(); cam.position.set(0, 0, 0); cam.lookAt(new THREE.Vector3(...d).add(S.saturn.position)); cam.updateMatrixWorld(true);
                const U = S.saturn.userData.U; U.uCamL.value.copy(S.saturn.position).negate().applyQuaternion(S.saturn.quaternion.clone().invert());
                S.renderer.setRenderTarget(rt); S.renderer.setClearColor(0x000000, 1); S.renderer.clear(); S.renderer.render(S.farScene, cam); S.renderer.setRenderTarget(null);
                const px = new Float32Array(W * H * 4); S.renderer.readRenderTargetPixels(rt, 0, 0, W, H, px); res.push(Array.from(px));
              }
              return res; })()"""
            pn = await page('experiences/cooper-station/index.html', '?lang=id&bulan=0'); new = await pn.evaluate(JS); await pn.close()
            po = await page('experiences/cooper-station/_baseline30.html', '?lang=id'); old = await po.evaluate(JS); await po.close()
            diff = sum(1 for a, c in zip(new, old) for x, y in zip(a, c) if abs(x - y) > 1e-6)
            hasil[f'Saturnus identik dengan komit {BASE_COMMIT}: {diff} nilai berbeda di 9 render langit jauh'] = diff == 0
        finally:
            if base_file.exists(): base_file.unlink()
        await b.close()
    ok = True
    for k, v in hasil.items():
        print(('OK   ' if v else 'GAGAL') + ' ' + k); ok &= bool(v)
    print('error:', errs[:10] or 'tidak ada')
    print('HASIL:', 'LULUS' if ok and not errs else 'GAGAL')

asyncio.run(main())
