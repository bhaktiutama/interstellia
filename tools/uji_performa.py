"""Uji fungsi untuk perubahan performa cabang perf/optimasi-threejs (docs/app/analisa-performa-threejs-webgpu.md).

Pakai: python tools/uji_performa.py   (THREE_LOCAL=<folder three.module.js + three.core.js>, CHROMIUM=<jalur chrome> opsional)
Halaman dibuka lewat file:// (cara pemilik menjalankannya), jadi pemuatan data besar secara dinamis ikut teruji.

Yang diperiksa:
  - Copper: tanpa error, data orang dan rumput termuat (model GLB aktif, rumput fluffy aktif), `?rumput=lama` dan `?orang=lama` masih jalan (jalur cadangan), Jupiter 4k termuat lewat decode() tanpa error
  - Millar: tanpa error, konteks WebGL tanpa stensil (stencil: false), lagu tema bisa didekode (fetch data:) dan elemen audio punya sumber blob
  - petunjuk muat: Copper dan Millar punya preconnect + modulepreload three.js, tanpa <script src> besar yang memblokir
"""
import asyncio, os, pathlib, sys
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOCAL, EXE = os.environ.get('THREE_LOCAL'), os.environ.get('CHROMIUM')
bad = []

def cek(ok, msg):
    print(('  ok   ' if ok else '  GAGAL ') + msg)
    if not ok: bad.append(msg)

async def page(b, rel, query, ready, timeout=900000):
    pg = await b.new_page(viewport={'width': 640, 'height': 360})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.on('console', lambda m: errs.append('console: ' + m.text[:160]) if m.type == 'error' and 'Failed to load resource' not in m.text else None)
    if LOCAL:
        async def serve(route):
            await route.fulfill(path=str(pathlib.Path(LOCAL) / route.request.url.rsplit('/', 1)[-1]), content_type='text/javascript', headers={'Access-Control-Allow-Origin': '*'})
        await pg.route('https://cdn.jsdelivr.net/**', serve)
    await pg.goto(ROOT.joinpath(rel).as_uri() + query)
    await pg.wait_for_function(ready, timeout=timeout)
    return pg, errs

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'],
                                    **({'executable_path': EXE} if EXE else {}))
        # --- petunjuk muat (statis) ---
        for rel in ('experiences/cooper-station/index.html', 'experiences/millar/index.html'):
            t = ROOT.joinpath(rel).read_text()
            cek('rel="preconnect" href="https://cdn.jsdelivr.net"' in t and 'rel="modulepreload"' in t and t.count('modulepreload') == 2, f'{rel}: preconnect + modulepreload (module + core)')
        t = ROOT.joinpath('experiences/cooper-station/index.html').read_text()
        cek('<script src="assets/orang.data.js">' not in t and '<script src="assets/rumput.data.js">' not in t, 'Copper: data besar tidak lagi <script src> yang memblokir')

        # --- Copper ---
        print('Copper')
        pg, errs = await page(b, 'experiences/cooper-station/index.html', '?lang=id', 'window.__stationReady === true')
        r = await pg.evaluate("""() => { const S = window.__station;
          return { orang: !!window.ORANG_DATA, rumput: !!window.RUMPUT_DATA, fluff: !!(S.FLUFF && (S.FLUFF.lawn || S.FLUFF.wheat)), dp: !!window.__dataP } }""")
        cek(not errs, f'tanpa error ({errs[:2]})')
        cek(r['orang'] and r['rumput'] and r['dp'], f'data orang + rumput termuat async: {r}')
        cek(r['fluff'], 'rumput fluffy aktif (bukan jalur lama)')
        await pg.close()

        pg, errs = await page(b, 'experiences/cooper-station/index.html', '?lang=id&rumput=lama&orang=lama', 'window.__stationReady === true')
        cek(not errs, f'?rumput=lama&orang=lama tanpa error ({errs[:2]})')
        await pg.close()

        # data besar gagal dimuat (offline / 404): jalur cadangan lama (rumput lama, model kotak) harus tetap jalan
        pg = await b.new_page(viewport={'width': 640, 'height': 360})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        if LOCAL:
            async def serve(route):
                await route.fulfill(path=str(pathlib.Path(LOCAL) / route.request.url.rsplit('/', 1)[-1]), content_type='text/javascript', headers={'Access-Control-Allow-Origin': '*'})
            await pg.route('https://cdn.jsdelivr.net/**', serve)
        await pg.route('**/assets/orang.data.js', lambda r: r.abort())
        await pg.route('**/assets/rumput.data.js', lambda r: r.abort())
        await pg.goto(ROOT.joinpath('experiences/cooper-station/index.html').as_uri() + '?lang=id')
        await pg.wait_for_function('window.__stationReady === true', timeout=900000)
        r = await pg.evaluate("({ orang: !!window.ORANG_DATA, rumput: !!window.RUMPUT_DATA })")
        cek(not errs and not r['orang'] and not r['rumput'], f'data besar gagal dimuat: halaman tetap siap tanpa error ({errs[:2]}, {r})')
        await pg.close()

        pg, errs = await page(b, 'experiences/cooper-station/index.html', '?lang=id&planet=jupiter&jres=4k', 'window.__stationReady === true')
        cek(not errs, f'Jupiter 4k (decode) tanpa error ({errs[:2]})')
        cek(await pg.evaluate('window.JUPITER_MAP === undefined'), 'peta Jupiter dikonsumsi (JUPITER_MAP dilepas)')
        await pg.close()

        # --- Millar ---
        print('Millar')
        pg, errs = await page(b, 'experiences/millar/index.html', '?lang=id', 'window.__millarReady === true')
        attr = await pg.evaluate("(() => { const c = document.querySelector('canvas'); const gl = c.getContext('webgl2'); return gl ? gl.getContextAttributes() : null; })()")
        cek(not errs, f'tanpa error ({errs[:2]})')
        cek(attr is not None and attr.get('stencil') is False, f'konteks WebGL tanpa stensil: {attr}')
        await pg.click('#go', timeout=300000)
        await pg.wait_for_timeout(1500)
        r = await pg.evaluate("""async () => { const el = SONGKIT.element('../../shared/musik/'); for (let i = 0; i < 100 && !el.src; i++) await new Promise((r) => setTimeout(r, 100));
          return { src: (el.src || '').slice(0, 5), cur: SONGKIT.current }; }""")
        cek(r['src'] == 'blob:' and r['cur'] in ('tema1', 'tema2'), f'lagu tema didekode (fetch data:) menjadi blob URL: {r}')
        dur = await pg.evaluate("""async () => { const el = SONGKIT.element('../../shared/musik/'); for (let i = 0; i < 100 && !(el.duration > 0); i++) await new Promise((r) => setTimeout(r, 100)); return el.duration; }""")
        cek(dur and dur > 30, f'mp3 hasil dekode valid (durasi {dur} s)')
        await pg.close()
        await b.close()
    print('\nSEMUA LULUS' if not bad else f'\n{len(bad)} GAGAL: {bad}')
    sys.exit(1 if bad else 0)

asyncio.run(main())
