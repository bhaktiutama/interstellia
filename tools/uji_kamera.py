"""Uji Rencana K (kamera rangefinder, shared/camera.js).
Bagian 1 (selalu, butuh node): rumus CAMKIT tanpa browser: EV, CoC, hiperfokal, bidang pandang, bukaan berbilah,
label rana, rentang tajam, chunk tEXt PNG.
Bagian 2 (--browser, butuh playwright + Chromium): per experience masuk mode kamera, foto akumulasi (live view, mode A),
foto rana 1/4 s (dunia maju), video 2 s, keluar = uniform kamera mati, tanpa error halaman.
Pakai: python tools/uji_kamera.py [--browser] [cooper|millar|gargantua ...]
CHROMIUM=<jalur chrome> opsional (mis. /opt/pw-browsers/chromium-1194/chrome-linux/chrome)."""
import asyncio, json, os, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

NODE = r"""
global.window = {}; global.localStorage = { getItem: () => null, setItem() {} };
global.TextEncoder = require('util').TextEncoder; global.TextDecoder = require('util').TextDecoder;
require(process.argv[1]); const K = window.CAMKIT, out = {};
const near = (a, b, e) => Math.abs(a - b) <= e;
out['EV f/16 1/125 ISO 100 = 14,97'] = near(K.ev100(16, 1 / 125, 100), 14.966, 0.01);
out['EV f/1,4 1/30 ISO 3200 = 0,88'] = near(K.ev100(1.4, 1 / 30, 3200), 0.88, 0.01);
out['CoC 50 mm f/1,4 fokus 2 m objek jauh = 0,916 mm'] = near(K.cocMM(50, 1.4, 2, 1e12), 0.916, 0.001);
out['CoC 90 mm f/2,4 fokus 5 m = 0,687 mm'] = near(K.cocMM(90, 2.4, 5, 1e12), 0.687, 0.001);
out['hiperfokal 50 mm f/8 = 10,47 m'] = near(K.hyperfocal(50, 8), 10.47, 0.01);
out['hiperfokal 28 mm f/8 = 3,29 m'] = near(K.hyperfocal(28, 8), 3.29, 0.01);
out['bidang vertikal 50 mm 3:2 = 26,99 derajat'] = near(K.fovV(50, 1.5), 26.99, 0.01);
out['bidang horizontal 28 mm = 65,47 derajat'] = near(K.fovH(28), 65.47, 0.01);
out['jari-jari bukaan 50 mm f/1,4 = 17,86 mm'] = near(K.apertureR(50, 1.4) * 1000, 17.86, 0.01);
out['geser patch objek 2 m fokus tak hingga = 0,025 rad'] = near(K.rfShift(0.05, 2, Infinity), 0.025, 1e-9);
out['rana x2 = EV turun 1'] = near(K.ev100(4, 1 / 60, 100) - K.ev100(4, 1 / 30, 100), 1, 1e-9);
let mx = 0, mn = 9; for (let i = 0; i < 256; i++) { const p = K.bladeSample(i, 1.4, 1.4); const r = Math.hypot(p[0], p[1]); mx = Math.max(mx, r); }
for (let i = 0; i < 256; i++) { const p = K.bladeSample(i, 16, 1.4); const r = Math.hypot(p[0], p[1]); mn = Math.min(mn, r); }
out['sampel bukaan di dalam lingkaran satuan'] = mx <= 1 + 1e-9;
out['label rana 1/250, 1/320, 2s, B'] = K.shutterLabel(1 / 250) === '1/250' && K.shutterLabel(1 / 300) === '1/320' && K.shutterLabel(2.2) === '2s' && K.shutterLabel(Infinity) === 'B';
const dr = K.dofRange(50, 8, 3); out['rentang tajam 50 mm f/8 fokus 3 m = 2,34-4,19 m'] = near(dr[0], 2.34, 0.01) && near(dr[1], 4.19, 0.01);
out['CRC32 "IEND" = AE426082'] = K.crc32(new Uint8Array([73, 69, 78, 68])) === 0xAE426082;
console.log(JSON.stringify(out));
"""


def part_node():
    r = subprocess.run(['node', '-e', NODE, str(ROOT / 'shared/camera.js')], capture_output=True, text=True)
    if r.returncode:
        print(r.stderr); return False
    res = json.loads(r.stdout)
    for k, v in res.items(): print(('LULUS ' if v else 'GAGAL ') + k)
    return all(res.values())


EXP = {
    'cooper': ('experiences/cooper-station/index.html', 'window.__stationReady === true',
               "() => { document.getElementById('go').click(); window.__station.togglePhoto(true, 'kamera'); }"),
    'millar': ('experiences/millar/index.html', 'window.__millarReady === true',
               "() => { window.__millar.start(); setTimeout(() => window.__millar.togglePhoto(true, 'kamera'), 1500); }"),
    'gargantua': ('experiences/gargantua/index.html', 'true', "() => window.__gargantua.togglePhoto(true, 'kamera')"),
}


async def part_browser(names):
    from playwright.async_api import async_playwright
    ok = True
    async with async_playwright() as p:
        kw = {'args': ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required']}
        if os.environ.get('CHROMIUM'): kw['executable_path'] = os.environ['CHROMIUM']
        b = await p.chromium.launch(**kw)
        for n in names:
            rel, ready, enter = EXP[n]
            pg = await b.new_page(viewport={'width': 640, 'height': 360}, accept_downloads=True)
            errs = []
            pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
            pg.on('console', lambda m: errs.append(m.text[:300]) if m.type == 'error' else None)
            await pg.goto((ROOT / rel).as_uri())
            await pg.wait_for_function(ready, timeout=300000)
            await pg.wait_for_timeout(3000)
            await pg.evaluate(enter)
            await pg.wait_for_timeout(5000)
            res = {}
            res['masuk mode kamera'] = await pg.evaluate('CAMKIT.on')
            await pg.evaluate("() => { window.__shots = []; CAMKIT.onSaved = (b, n) => window.__shots.push([n, b.size]); Object.assign(CAMKIT.st, { mode: 'A', video: false, live: true }); CAMKIT.shutterPress(); }")
            await pg.wait_for_function('window.__shots.length > 0', timeout=600000)
            s = await pg.evaluate('window.__shots[0]')
            res[f'foto live view tersimpan ({s[1]} byte, {s[0]})'] = s[1] > 2000
            await pg.evaluate("() => { Object.assign(CAMKIT.st, { mode: 'M', sh: 10, live: false }); CAMKIT.shutterPress(); }")
            await pg.wait_for_function('window.__shots.length > 1', timeout=900000)
            s = await pg.evaluate('window.__shots[1]')
            res[f'foto rana 1/4 s tersimpan ({s[1]} byte)'] = s[1] > 2000
            await pg.evaluate("() => { window.__vid = null; CAMKIT.onRecorded = (b) => { window.__vid = b.size; }; Object.assign(CAMKIT.st, { video: true, mode: 'A' }); CAMKIT.recStart(); }")
            await pg.wait_for_timeout(2500)
            await pg.evaluate('CAMKIT.recStop()')
            await pg.wait_for_function('window.__vid !== null', timeout=30000)
            res[f'video tersimpan ({await pg.evaluate("window.__vid")} byte)'] = (await pg.evaluate('window.__vid')) > 0
            await pg.evaluate("() => { CAMKIT.st.video = false; }")
            await pg.keyboard.press('KeyF')
            await pg.wait_for_timeout(1500)
            res['keluar: kamera mati, uniform eksposur kamera mati'] = await pg.evaluate('!CAMKIT.on && CAMKIT.U.E[0] === 0')
            res['tanpa error halaman: ' + ('; '.join(errs[:3]) or 'tidak ada')] = not errs
            print('==', n)
            for k, v in res.items(): print(('LULUS ' if v else 'GAGAL ') + k)
            ok = ok and all(res.values())
            await pg.close()
        await b.close()
    return ok


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    good = part_node()
    if '--browser' in sys.argv:
        good = asyncio.run(part_browser(args or list(EXP))) and good
    print('SEMUA LULUS' if good else 'ADA YANG GAGAL')
    sys.exit(0 if good else 1)
