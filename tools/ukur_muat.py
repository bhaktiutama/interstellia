"""Ukur muat dan tersendat per experience (rencana P0, docs/app/rencana-performa.md) lewat PROFKIT (?prof=1).

Pakai:
  python tools/ukur_muat.py                      # ketiga experience, cetak ringkasan
  python tools/ukur_muat.py millar --cek         # satu experience, gagal (exit 1) bila ada program baru di frame pertama atau saat tombol
  python tools/ukur_muat.py --json hasil.json    # simpan data mentah PROFKIT
Lingkungan: THREE_LOCAL=<folder three.module.js + three.core.js> untuk sandbox tanpa CDN, CHROMIUM=<jalur chrome> opsional.

Catatan: di sandbox (SwiftShader) jumlah program dan urutannya dapat dipercaya, lamanya tidak mewakili GPU asli.
Untuk GPU asli buka halaman dengan ?prof=1 di browser, lalu tombol "Salin hasil".
"""
import asyncio, json, os, pathlib, sys
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXP = {
    # pre: dijalankan setelah muat. Di GPU dengan kompilasi paralel varian lain dikompilasi otomatis di latar belakang;
    # sandbox tidak punya ekstensi itu, jadi dipaksa agar hasilnya mewakili GPU asli.
    'cooper-station': {'keys': ['KeyP', 'KeyP', 'Digit8', 'Digit1', 'KeyC', 'KeyC', 'Digit7', 'KeyN', 'KeyP', 'KeyQ'], 'go': True,
                       'pre': 'PROFKIT.parallel || window.__station.warmLater(true)'},
    'millar': {'keys': ['Space', 'KeyN', 'KeyP', 'KeyQ', 'KeyQ', 'KeyF', 'Escape', 'KeyM'], 'go': True},
    'gargantua': {'keys': ['KeyQ', 'KeyP', 'KeyF', 'Escape', 'KeyV'], 'go': False},
}

async def run(b, name, cfg, local):
    pg = await b.new_page(viewport={'width': 640, 'height': 360})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    if local:
        async def serve(route):
            await route.fulfill(path=str(pathlib.Path(local) / route.request.url.rsplit('/', 1)[-1]), content_type='text/javascript',
                                headers={'Access-Control-Allow-Origin': '*'})
        await pg.route('https://cdn.jsdelivr.net/**', serve)
    await pg.goto(ROOT.joinpath(f'experiences/{name}/index.html').as_uri() + '?prof=1&lang=id')
    await pg.wait_for_function('window.PROFKIT && PROFKIT.cur === "main"', timeout=900000)   # siap + frame pertama selesai
    await pg.wait_for_timeout(1500)
    if cfg.get('pre'): await pg.evaluate(cfg['pre'])
    if cfg['go']:
        await pg.click('#go', timeout=300000)
        await pg.wait_for_timeout(6000)
    for k in cfg['keys']:
        await pg.keyboard.press(k)
        await pg.wait_for_timeout(3500)
    await pg.wait_for_timeout(500)
    d = await pg.evaluate('PROFKIT.data()')
    d['errs'] = errs
    await pg.close()
    return d

def show(name, d):
    ph, w = d['programsByPhase'], d['waitMsByPhase']
    print(f"\n== {name}  (GPU: {d['gpu'][:50]}, kompilasi paralel: {'ya' if d['parallel'] else 'tidak'})")
    print(f"siap {d['readyAt'] / 1000:.2f} s, frame pertama {d['firstFrameMs']} ms, long task maks {d['longMax']} ms")
    print(f"program: muat {ph.get('muat', 0)}, frame pertama {ph.get('frame1', 0)}, bermain {ph.get('main', 0)}; total {d['programs']}")
    print(f"tunggu program (ms): muat {w.get('muat', 0)}, frame pertama {w.get('frame1', 0)}, bermain {w.get('main', 0)}")
    marks = d['marks']
    for i, (t, lab) in enumerate(marks):
        nxt = marks[i + 1][0] if i + 1 < len(marks) else d['readyAt']
        if nxt - t >= 200: print(f"  tahap {lab}: {nxt - t} ms")
    for k in d['keys']:
        print(f"  tombol {k['key']}: {k['programs']} program, frame maks {round(k['maxFrame'])} ms, long task maks {k['maxLong']} ms")
    if d['errs']: print('  error:', d['errs'][:3])

async def main():
    args = [a for a in sys.argv[1:]]
    cek = '--cek' in args
    out = None
    if '--json' in args: out = args[args.index('--json') + 1]
    names = [a for a in args if a in EXP] or list(EXP)
    local = os.environ.get('THREE_LOCAL')
    exe = os.environ.get('CHROMIUM')
    res, bad = {}, []
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'],
                                    **({'executable_path': exe} if exe else {}))
        for n in names:
            d = res[n] = await run(b, n, EXP[n], local)
            show(n, d)
            if d['programsByPhase'].get('frame1', 0): bad.append(f"{n}: {d['programsByPhase']['frame1']} program di frame pertama")
            bad += [f"{n}: tombol {k['key']} {k['programs']} program" for k in d['keys'] if k['programs']]
            if d['errs']: bad.append(f"{n}: error halaman")
        await b.close()
    if out: json.dump(res, open(out, 'w'), indent=1)
    if cek:
        print('\nCEK:', 'lulus' if not bad else 'GAGAL\n  ' + '\n  '.join(bad))
        sys.exit(1 if bad else 0)

asyncio.run(main())
