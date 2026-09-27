"""Cek cepat: buka index.html di Chromium headless, tunggu siap, cetak error.
Pakai: python tools/qc_load.py   (butuh: pip install playwright && playwright install chromium)
Bila tidak ada GPU, pakai SwiftShader (lambat tapi cukup untuk cek error)."""
import asyncio, pathlib
from playwright.async_api import async_playwright

async def main():
    page_url = pathlib.Path(__file__).resolve().parent.parent.joinpath('index.html').as_uri()
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        pg = await b.new_page(viewport={'width': 320, 'height': 200})
        errs = []
        pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
        pg.on('console', lambda m: errs.append(m.type + ': ' + m.text[:300]) if m.type in ('error', 'warning') else None)
        await pg.goto(page_url)
        await pg.wait_for_function('window.__stationReady === true', timeout=120000)
        await pg.wait_for_timeout(3000)
        print('siap:', await pg.evaluate('window.__stationReady'))
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())
