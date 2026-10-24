"""Uji pilihan wahana di Millar's World dan Gargantua (rencana docs/app/rencana-pilihan-wahana.md): tiga wahana (ks07, pr11, gx01) x dua experience.
Millar per wahana (?ship=): wahana terpilih tergambar dan ukurannya sesuai, nama di teks, tapak dan tangga (kolisi, titik naik), kokpit (mata, tangan di
tongkat dan tuas untuk ks07 / pr11, render tanpa nilai tidak valid), terbang (lepas landas, mendarat), lolos dari gelombang di mode Misi dengan margin,
sinematik kedatangan (mendarat tepat di titik semula, kamera di atas air), pandangan orbit dengan plasma tanpa nilai tidak valid, pilihan tersimpan
(lazarus.ship) dan pemilih di layar mulai.
Gargantua per wahana: blob termuat dan nama wahana di teks, V menyalakan wahana (kamera luar), kokpit dan relai di misi, piksel wahana berbeda dari tanpa
wahana, render tanpa error, pemilih di panel.
Pakai: python tools/uji_wahana.py   (butuh playwright; THREE_LOCAL=<folder berisi three.module.js dan three.core.js>, CHROMIUM=<executable> opsional)"""
import asyncio, os, pathlib
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHIPS = os.environ.get('SHIPS', 'ks07,pr11,gx01').split(',')

MILLAR = r"""
(async (id) => {
  const M = window.__millar, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms)), P = M.P, V3 = M.THREE.Vector3;
  const FL = M.FLY, MI = M.MIS, KS = M.KS, dt = 1 / 30;
  M.CINE.enabled = false;
  const hdr = (n) => { const T = M.POST.hdr, w = n ? n : T.width, h = n ? n : T.height, b = new Uint16Array(w * h * 4);
    M.renderer.readRenderTargetPixels(T, n ? (T.width - n) >> 1 : 0, n ? (T.height - n) >> 1 : 0, w, h, b);
    let nb = 0, hot = 0, lum = 0; for (let k = 0; k < b.length; k += 4) for (let c = 0; c < 3; c++) { const x = M.THREE.DataUtils.fromHalfFloat(b[k + c]); if (!Number.isFinite(x)) nb++; else { if (x > 50) hot++; lum += x; } }
    return { nb, hot, lum: lum / (b.length * 0.75) }; };
  // 1. deskriptor dan adegan
  out[`${id}: KS.id ${KS.id}, ${KS.size.L} x ${KS.size.W} m, mesh wahana ${M.SHIP.mesh.children.length} anak, layar kokpit ${Object.keys(M.COCKPIT.screens).join('/')}`] =
    KS.id === id && M.SHIP.mesh.children.length >= 6 && ['kiri', 'tengah', 'kanan'].every((n) => !!M.COCKPIT.screens[n]) && M.CK === KS.cockpit;
  const nm = M.t('E: naik ke KS-07'), want = { ks07: 'KS-07', pr11: 'PR-11', gx01: 'GX-01' }[id];
  out[`${id}: teks memakai nama wahana: "${nm}"`] = nm.includes(want) && (id === 'ks07' || !nm.includes('KS-07'));
  out[`${id}: pemilih di layar mulai: ${document.querySelectorAll('#shipPick button').length} tombol, aktif ${[...document.querySelectorAll('#shipPick button.on')].map((b) => b.dataset.ship)}`] =
    document.querySelectorAll('#shipPick button').length === 3 && document.querySelector('#shipPick button.on').dataset.ship === id;
  // 2. tapak, kolisi, titik naik
  M.setMode('jelajah'); M.start(); await wait(300);
  const pad = M.SHIP.pads[0]; P.x = pad.x + 0.1; P.z = pad.z; M.shipPush(); const dp = Math.hypot(P.x - pad.x, P.z - pad.z);
  const door = M.SHIP.door; P.x = door.x; P.z = door.z; M.shipPush(); const dd = Math.hypot(P.x - door.x, P.z - door.z);
  out[`${id}: tapak mendorong pemain keluar (${dp.toFixed(2)} >= r + 0,3 = ${(pad.r + 0.3).toFixed(2)} m), titik naik tidak terdorong (${dd.toFixed(2)} m), wahana di dasar laut y ${M.SHIP.y.toFixed(2)}`] =
    dp >= pad.r + 0.29 && dd < 0.05 && Number.isFinite(M.SHIP.y);
  // 3. kokpit
  M.BODY.showSeat = true; M.boardShip(); FL.view = 1; M.flyCamera(); M.camera.updateMatrixWorld(true); M.updateBody(1 / 60); const B = M.BODY; B.group.updateMatrixWorld(true);
  const eyeW = new V3(...KS.eye).applyMatrix4(M.SHIP.mesh.matrix), eyeD = eyeW.distanceTo(M.camera.position);
  const gS = M.COCKPIT.stick.localToWorld(new V3(0, 0.21, 0.01)), gT = M.COCKPIT.throttle.localToWorld(new V3(0.02, 0.15, 0));
  const glove = (i) => B.elbows[i].localToWorld(new V3(0, -0.33, -0.02)), eS = glove(1).distanceTo(gS), eT = glove(0).distanceTo(gT);
  M.U.uCam.value.copy(M.camera.position); M.updateShadow(); M.renderer.setRenderTarget(M.POST.hdr); M.renderer.clear(); M.renderer.render(M.scene, M.camera); M.renderer.setRenderTarget(null);
  const h1 = hdr();
  out[`${id}: kokpit: kamera ${(eyeD * 100).toFixed(2)} cm dari mata wahana, tangan ${(eS * 100).toFixed(1)} / ${(eT * 100).toFixed(1)} cm dari tongkat / tuas (ks07, pr11 < 4), render tidak valid ${h1.nb}, titik > 50: ${h1.hot}, terang ${h1.lum.toFixed(3)}`] =
    eyeD < 0.01 && h1.nb === 0 && h1.hot === 0 && h1.lum > 0.001 && (id === 'gx01' || (eS < 0.04 && eT < 0.04));
  M.flyReset(); FL.view = 0; M.updateBody(10);
  // 4. lolos dari gelombang di mode Misi (lepas landas R + Shift, gelombang 45 s lagi)
  M.setMode('misi'); M.setLevel(1); M.startMission(); for (const S of MI.sites) S.got = true;
  P.x = M.SHIP.door.x; P.z = M.SHIP.door.z; M.missionAction();
  M.U.uWX.value += FL.x + M.CONFIG.wave.v * 45 - M.frontX(FL.z);
  M.keys.KeyR = true; M.keys.ShiftLeft = true; let tUp = -1, tt = 0, bad = 0;
  for (let k = 0; k < 90 * 30 && !MI.result; k++) { M.simStep(dt, dt); M.updateFly(dt); M.updateMission(dt, dt); tt += dt; if (!Number.isFinite(FL.y)) bad++; if (tUp < 0 && FL.y - FL.water > 1300) tUp = tt; }
  M.keys.KeyR = false; M.keys.ShiftLeft = false;
  out[`${id}: lepas landas: 1.300 m dalam ${tUp.toFixed(1)} s, hasil ${MI.result ? MI.result.why : '-'} (ketinggian ${MI.result ? MI.result.alt.toFixed(0) : '-'} m), nilai tidak valid ${bad}`] = !!MI.result && MI.result.ok && MI.result.why === 'lolos' && bad === 0;
  document.getElementById('result').hidden = true; M.STATE.started = true;
  // tertelan bila tidak lepas landas
  M.startMission(); for (const S of MI.sites) S.got = true; P.x = M.SHIP.door.x; P.z = M.SHIP.door.z; M.missionAction();
  M.U.uWX.value += FL.x + M.CONFIG.wave.v * 3 - M.frontX(FL.z);
  for (let k = 0; k < 20 * 30 && !MI.result; k++) { M.simStep(dt, dt); M.updateFly(dt); }
  out[`${id}: tidak lepas landas = ${MI.result ? MI.result.why : '-'}`] = !!MI.result && !MI.result.ok && MI.result.why === 'tertelan';
  document.getElementById('result').hidden = true; M.stopMission(); M.setMode('jelajah'); M.STATE.started = true; M.flyReset();
  // 5. Jelajah: naik, mendarat, turun di samping tangga
  M.U.uWX.value += 40000 - M.frontX(0); P.x = 0; P.z = 0;
  M.BODY.showSeat = false; const x0 = M.SHIP.x, z0 = M.SHIP.z; M.boardShip(); M.keys.KeyR = true; for (let k = 0; k < 240; k++) M.updateFly(dt); M.keys.KeyR = false; M.keys.KeyW = true; for (let k = 0; k < 120; k++) M.updateFly(dt); M.keys.KeyW = false;   // 240 langkah: wahana berat menyalakan mesin lebih lama (spool)
  for (let k = 0; k < 90; k++) M.updateFly(dt);
  const yAir = FL.y - FL.water; M.keys.KeyF = true; for (let k = 0; k < 900 && FL.y - FL.water > M.CONFIG.fly.landH + M.SHIP.padDrop; k++) M.updateFly(dt); M.keys.KeyF = false;
  for (let k = 0; k < 60; k++) M.updateFly(dt);
  M.flyLand();
  const moved = Math.hypot(M.SHIP.x - x0, M.SHIP.z - z0), dDoor = Math.hypot(P.x - M.SHIP.door.x, P.z - M.SHIP.door.z);
  out[`${id}: terbang ${yAir.toFixed(0)} m di atas air, mendarat ${moved.toFixed(0)} m dari tempat semula, pemain ${dDoor.toFixed(1)} m dari tangga, mendarat ${!FL.on}`] = yAir > 5 && moved > 3 && dDoor < 2.5 && !FL.on && M.SHIP.legs.visible;
  // 6. sinematik kedatangan sampai titik semula, plasma di orbit
  const C = M.CINE; M.CINE.enabled = true; C.played = false; M.STATE.started = false; M.setMode('misi'); M.startWithCine();
  C.t = 20.9; let minGap = 1e9, camLow = 0, steps = 0; const yl = (() => { M.placeShip(...M.SHIP.home); return M.SHIP.y; })();
  while (C.on && steps++ < 600) { M.cineStep(dt); if (C.world) { minGap = Math.min(minGap, M.SHIP.mesh.position.y - yl); if (M.camera.position.y < M.drawdown(M.camera.position.x - M.frontX(M.camera.position.z)) + 0.5) camLow++; } }
  const home = M.SHIP.home, dHome = Math.hypot(M.SHIP.x - home[0], M.SHIP.z - home[1]);
  out[`${id}: kedatangan: mendarat ${dHome.toFixed(2)} m dari titik semula, celah terendah ${minGap.toFixed(2)} m, kamera di bawah air ${camLow}x, misi ${M.MIS.on}`] = !C.on && dHome < 0.01 && minGap > -0.01 && camLow === 0 && M.MIS.on;
  M.stopMission(); M.setMode('jelajah'); M.STATE.started = false; C.played = false; M.startWithCine(); C.t = 17; await wait(900);
  M.cineStep(0); M.orbShipCam(0.03, Math.PI * 0.55, -0.9, 0); M.renderOrbit(performance.now()); const ho = hdr(20);
  M.orbShipCam(0.03, Math.PI * 0.55, 0.9, 0); M.renderOrbit(performance.now()); const hu = hdr(20);
  M.renderOrbit(performance.now()); const hf = hdr();
  out[`${id}: orbit dengan plasma: dari bawah ${ho.lum.toFixed(3)} vs atas ${hu.lum.toFixed(3)}, tidak valid ${ho.nb + hu.nb + hf.nb}`] = ho.nb + hu.nb + hf.nb === 0 && ho.lum > hu.lum * 1.3;
  M.cineStop(); M.CINE.enabled = false; M.STATE.started = true;
  return out;
})
"""

GARG = r"""
(async (id) => {
  const G = window.__gargantua, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms)), S = G.SHIP;
  const want = { ks07: 'KS-07', pr11: 'PR-11', gx01: 'GX-01' }[id];
  out[`${id}: blob ${S.data ? S.data.name : '-'}, SHIP.ready ${S.ready}, ${S.data ? (S.data.n / 3 | 0) : 0} segitiga, layar ${S.data ? S.data.screens.length : 0}, kamera luar ${S.chase.join(',')}`] = !!S.data && S.data.name === want && S.ready && S.data.screens.length >= 3;
  const lab = document.body.innerText;
  out[`${id}: panel memuat pemilih wahana (Vessel) dan tombol V bernama ${want}`] = /Vessel|Wahana/.test(lab) && lab.includes(want + ' vessel') || lab.includes('Wahana ' + want);
  // tangkapan layar tanpa wahana, kamera luar, kokpit: dari python (kanvas WebGL tanpa preserveDrawingBuffer)
  // misi: kamera luar, kokpit, relai, layar akhir bernama wahana
  G.state.paused = false; G.startMission('polar'); await wait(300);
  const seq = [];
  for (let k = 0; k < 4; k++) { G.cycleShipView(); await wait(350); seq.push(S.view); }
  G.stopMission(); await wait(200);
  out[`${id}: V di misi berganti ${seq.join(' > ')}`] = seq.join(',') === 'cockpit,relay,chase,cockpit' || seq.join(',') === 'relay,chase,cockpit,relay';
  const d = G.misData ? true : false;
  out[`${id}: pemilih mengganti wahana lewat FLEET.set (kunci lazarus.ship)`] = !!window.FLEET && window.FLEET.current('gx01') === id && window.FLEET.KEY === 'lazarus.ship';
  return out;
})
"""

async def main():
    local = os.environ.get('THREE_LOCAL')
    errs = []
    async with async_playwright() as p:
        exe = os.environ.get('CHROMIUM')
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'], **({'executable_path': exe} if exe else {}))

        async def page(path, q, ready, vp=(480, 270)):
            pg = await b.new_page(viewport={'width': vp[0], 'height': vp[1]})
            pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
            pg.on('console', lambda m: errs.append(m.type + ': ' + m.text[:300]) if m.type in ('error', 'warning') and 'GPU stall' not in m.text and 'Automatic fallback' not in m.text else None)
            if local:
                async def serve(route):
                    await route.fulfill(path=str(pathlib.Path(local) / route.request.url.rsplit('/', 1)[-1]), content_type='text/javascript', headers={'Access-Control-Allow-Origin': '*'})
                await pg.route('https://cdn.jsdelivr.net/**', serve)
            await pg.goto(ROOT.joinpath(path).as_uri() + q, wait_until='domcontentloaded', timeout=180000)
            await pg.wait_for_function(ready, timeout=180000)
            await pg.wait_for_timeout(1500)
            return pg
        hasil = {}
        for sid in SHIPS:
            pg = await page('experiences/millar/index.html', f'?lang=id&ship={sid}', 'window.__millarReady === true')
            hasil.update(await pg.evaluate(MILLAR, sid))
            await pg.close()
        for sid in SHIPS:
            pg = await page('experiences/gargantua/index.html', f'?lang=en&ship={sid}', 'window.__gargantua !== undefined && window.__gargantua.SHIP !== undefined', (640, 360))
            hasil.update(await pg.evaluate(GARG, sid))
            shots = []
            await pg.evaluate("window.__gargantua.state.paused = true")
            for js in ["window.__gargantua.setShip(false)", "window.__gargantua.setShip(true, 'chase')", "window.__gargantua.setShip(true, 'cockpit')"]:
                await pg.evaluate(js); await pg.wait_for_timeout(900); shots.append(await pg.screenshot())
            hasil[f'{sid}: wahana tergambar (tangkapan layar tanpa wahana, kamera luar, kokpit berbeda satu sama lain)'] = len({bytes(x) for x in shots}) == 3
            await pg.evaluate("window.__gargantua.setShip(false)")
            await pg.close()
        # pilihan tersimpan: tanpa ?ship= wahana mengikuti localStorage lazarus.ship
        pg = await page('experiences/millar/index.html', '?lang=id&ship=pr11', 'window.__millarReady === true')
        await pg.evaluate("localStorage.setItem('lazarus.ship', 'pr11')"); await pg.close()
        pg = await b.new_page(viewport={'width': 480, 'height': 270})
        await pg.goto(ROOT.joinpath('experiences/millar/index.html').as_uri() + '?lang=id', wait_until='domcontentloaded', timeout=180000)
        await pg.evaluate("localStorage.setItem('lazarus.ship', 'pr11')")
        pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
        if local:
            async def serve2(route):
                await route.fulfill(path=str(pathlib.Path(local) / route.request.url.rsplit('/', 1)[-1]), content_type='text/javascript', headers={'Access-Control-Allow-Origin': '*'})
            await pg.route('https://cdn.jsdelivr.net/**', serve2)
        await pg.reload(); await pg.wait_for_function('window.__millarReady === true', timeout=180000)
        hasil['lazarus.ship = pr11 dipakai tanpa ?ship='] = await pg.evaluate("window.__millar.KS.id === 'pr11'")
        await b.close()
    ok = True
    for k, v in hasil.items():
        print(('OK   ' if v else 'GAGAL') + ' ' + k); ok &= bool(v)
    print('error:', errs[:10] or 'tidak ada')
    print('HASIL:', 'LULUS' if ok and not errs else 'GAGAL')

asyncio.run(main())
