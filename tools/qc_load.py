"""Cek cepat: buka index.html di Chromium headless, tunggu siap, cetak error.
Pakai: python tools/qc_load.py [experiences/cooper-station/index.html]   (default: Copper Corn Station; butuh: pip install playwright && playwright install chromium)
Bila tidak ada GPU, pakai SwiftShader (lambat tapi cukup untuk cek error)."""
import asyncio, pathlib, sys
from playwright.async_api import async_playwright

async def main():
    rel = sys.argv[1] if len(sys.argv) > 1 else 'experiences/cooper-station/index.html'
    page_url = pathlib.Path(__file__).resolve().parent.parent.joinpath(rel).as_uri()
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        pg = await b.new_page(viewport={'width': 320, 'height': 200})
        errs = []
        pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
        pg.on('console', lambda m: errs.append(m.type + ': ' + m.text[:300]) if m.type in ('error', 'warning') else None)
        await pg.goto(page_url)
        if 'cooper-station' in rel:                                   # Copper Corn Station punya penanda siap
            await pg.wait_for_function('window.__stationReady === true', timeout=120000)
        elif 'millar' in rel:                                         # Millar's World: siap setelah frame pertama
            await pg.wait_for_function('window.__millarReady === true', timeout=60000)
        await pg.wait_for_timeout(5000)
        print('halaman:', rel)
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())
