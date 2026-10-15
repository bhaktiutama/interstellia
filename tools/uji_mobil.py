"""Uji tahap 26 (Copper Corn Station): mobil detail dekat.
- Geometri CARGEO tiap jenis: tanpa NaN / Infinity, normal satuan tidak nol, di dalam kotak lama CAR_TYPES (lebar 0,93 x wx,
  spion 0,98 x wx, panjang +-h, tinggi ct; lampu atap taksi dan atap bus putih boleh lebih tinggi seperti CAR_EXTRA lama),
  jumlah segitiga <= 2.000 (bus <= 2.600).
- Ultra di pusat kota (teleport nyc): mobil parkir dekat dan lalu lintas dekat tampil, jumlah per jenis, tanpa error.
- Ganti preset Ultra -> Sedang -> Hemat: radius dekat 150 / 80 / 0, Hemat = tidak ada mobil detail.
- ?mobil=lama: CARGEO, TRAFFIC.near, dan material dekat tidak dibuat (mobil sebelum tahap 26).
Pakai: python tools/uji_mobil.py   (THREE_LOCAL = folder three.module.js untuk sandbox tanpa CDN, CHROMIUM opsional)"""
import asyncio, json, os, pathlib, sys
from playwright.async_api import async_playwright

GEO = r"""
(() => {
  const S = window.__station, out = [];
  S.CARGEO.forEach((g, t) => {
    const p = g.attributes.position.array, n = g.attributes.normal.array;
    let bad = 0, nz = 0, mx = 0, mz = 0, my = 0, out_w = 0;
    for (let i = 0; i < p.length; i += 3) {
      if (![p[i], p[i + 1], p[i + 2], n[i], n[i + 1], n[i + 2]].every(Number.isFinite)) bad++;
      const l = Math.hypot(n[i], n[i + 1], n[i + 2]); if (Math.abs(l - 1) > 1e-3) nz++;
      mx = Math.max(mx, Math.abs(p[i])); my = Math.max(my, p[i + 1]); mz = Math.max(mz, Math.abs(p[i + 2]));
    }
    const tris = (g.index ? g.index.count : p.length / 3) / 3;
    out.push({ t, tris, verts: p.length / 3, bad, normalBukanSatuan: nz, setengahLebar: +mx.toFixed(3), setengahPanjang: +mz.toFixed(3), tinggi: +my.toFixed(3) });
  });
  return out;
})()
"""

async def run(b, q, local, fn):
    pg = await b.new_page(viewport={'width': 320, 'height': 200}); errs = []
    pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
    pg.on('console', lambda m: errs.append(m.type + ': ' + m.text[:300]) if m.type == 'error' else None)
    if local:
        async def serve(route):
            await route.fulfill(path=str(pathlib.Path(local) / route.request.url.rsplit('/', 1)[-1]), content_type='text/javascript', headers={'Access-Control-Allow-Origin': '*'})
        await pg.route('https://cdn.jsdelivr.net/**', serve)
    url = pathlib.Path(__file__).resolve().parent.parent.joinpath('experiences/cooper-station/index.html').as_uri() + q
    await pg.goto(url, wait_until='commit')
    await pg.wait_for_function('window.__stationReady === true', timeout=900000)
    await pg.evaluate("document.getElementById('go').click()")
    await pg.wait_for_timeout(1500)
    r = await fn(pg)
    await pg.close()
    return r, errs

async def main():
    local, exe = os.environ.get('THREE_LOCAL'), os.environ.get('CHROMIUM')
    gagal = []
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'], **({'executable_path': exe} if exe else {}))

        async def baru(pg):
            geo = await pg.evaluate(GEO)
            await pg.evaluate("window.__station.teleport('nyc')"); await pg.wait_for_timeout(3000)
            st = []
            for i in (0, 2, 4):
                await pg.evaluate(f"window.__station.applyPreset({i})"); await pg.wait_for_timeout(2500)
                st.append(await pg.evaluate("""() => { const S = window.__station; return { preset: S.PRESET ? S.PRESET.idx : null,
                  near: S.MOBIL.near, parkir: S.CAR_NEAR.total, parkirPerJenis: S.CAR_NEAR.count.slice(), lalin: S.TRAFFIC.near ? S.TRAFFIC.near.total : null,
                  lalinPerJenis: S.TRAFFIC.near ? S.TRAFFIC.near.count.slice() : null }; }"""))
            return {'geo': geo, 'preset': st}
        r, errs = await run(b, '?preset=ultra', local, baru)
        print('geometri:'); [print(' ', json.dumps(g)) for g in r['geo']]
        print('preset (Ultra, Sedang, Hemat) di pusat kota:'); [print(' ', json.dumps(s)) for s in r['preset']]
        print('error:', errs[:5] or 'tidak ada')
        TYPES = [  # h, ct, wx (sama dengan CAR_TYPES)
            (2.2, 1.45, 1), (2.0, 1.48, 0.98), (2.3, 1.8, 1.05), (2.5, 2.08, 1.08), (2.65, 1.78, 1.06), (2.2, 1.45, 1), (6.0, 2.42, 1.4)]
        for g in r['geo']:
            h, ct, wx = TYPES[g['t']]
            if g['bad'] or g['normalBukanSatuan']: gagal.append(f"jenis {g['t']}: nilai tidak valid / normal")
            if g['setengahLebar'] > 0.98 * wx + 1e-3: gagal.append(f"jenis {g['t']}: lebar {g['setengahLebar']}")
            if g['setengahPanjang'] > h + 1e-3: gagal.append(f"jenis {g['t']}: panjang {g['setengahPanjang']}")
            if g['tinggi'] > (1.61 if g['t'] == 5 else 3.11 if g['t'] == 6 else ct + 1e-3): gagal.append(f"jenis {g['t']}: tinggi {g['tinggi']}")
            if g['tris'] > (2600 if g['t'] == 6 else 2000): gagal.append(f"jenis {g['t']}: {g['tris']} segitiga")
        u, s, hm = r['preset']
        if u['near'] != 150 or s['near'] != 80 or hm['near'] != 0: gagal.append(f"radius dekat {u['near']} / {s['near']} / {hm['near']}")
        if not u['parkir']: gagal.append('Ultra: tidak ada mobil parkir dekat')
        if hm['parkir'] or hm['lalin']: gagal.append('Hemat: masih ada mobil detail')
        if errs: gagal.append('error halaman (baru)')

        async def lama(pg):
            return await pg.evaluate("() => { const S = window.__station; return { lama: S.MOBIL.lama, cargeo: S.CARGEO, lalin: S.TRAFFIC.near || null, mat: S.CAR_NEAR ? S.CAR_NEAR.mat : null }; }")
        r2, errs2 = await run(b, '?preset=ultra&mobil=lama', local, lama)
        print('?mobil=lama:', json.dumps(r2), 'error:', errs2[:5] or 'tidak ada')
        if not r2['lama'] or r2['cargeo'] is not None or r2['lalin'] is not None or r2['mat'] is not None: gagal.append('?mobil=lama: objek tahap 26 masih dibuat')
        if errs2: gagal.append('error halaman (lama)')
        await b.close()
    print('\nHASIL:', 'LOLOS' if not gagal else 'GAGAL\n  ' + '\n  '.join(gagal))
    sys.exit(1 if gagal else 0)

asyncio.run(main())
