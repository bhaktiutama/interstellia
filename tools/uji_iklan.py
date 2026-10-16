"""Uji tahap 27 (Copper Corn Station): plang, reklame, dan sudut LCD.
- Atlas BRANDKIT: 48 merek, tiap sel punya warna rata-rata (tidak hitam semua), tabel bahasa IKLAN.langs lengkap.
- 27b: semua mesh gedung punya atribut aLang (baris bahasa plang per gedung), gedung di Tokyo memakai baris 'ja'.
- 27c / 27d: jumlah papan per jenis (reklame atap, logo menara, papan menonjol, halte, lapak, kafe, billboard tiang, minimarket) > 0;
  billboard tiang, minimarket, dan papan A tidak di badan jalan atau air; billboard tiang hanya di distrik dan tidak di distrik tani.
- 27e: layar LCD di alun-alun New York dibuat, render malam di alun-alun tanpa nilai tidak valid (piksel kanvas terbaca, bukan NaN).
- 27f: preset Hemat = radius papan 0,45x dan layar LCD diam.
- ?iklan=0: tidak ada atribut aLang, tidak ada kind FURN 'ik*', layar LCD tidak dibuat (kota sebelum tahap 27).
- ?neon=0: papan lain tetap, layar LCD tidak dibuat.
Pakai: python tools/uji_iklan.py   (THREE_LOCAL = folder three.module.js untuk sandbox tanpa CDN, CHROMIUM opsional)"""
import asyncio, json, os, pathlib, sys
from playwright.async_api import async_playwright

INFO = r"""
(() => {
  const S = window.__station, K = window.BRANDKIT, I = S.IKLAN;
  const avg = I.avg ? Array.from(I.avg) : [];
  let hitam = 0; for (let i = 0; i < avg.length; i += 3) if (avg[i] + avg[i + 1] + avg[i + 2] < 0.003) hitam++;
  const aLang = Object.values(S.cityMeshes).filter((m) => m.geometry.attributes.aStyle).map((m) => !!m.geometry.attributes.aLang);
  let tokyo = null;
  const fl = S.cityMeshes.flat;
  if (fl && fl.geometry.attributes.aLang) {
    const la = fl.geometry.attributes.aLang.array;
    S.BUILD.flat.forEach((e, i) => { const D = S.districtAt(e[0], e[1]); if (D && D.name === 'Tokyo' && tokyo === null) tokyo = la[i]; });
  }
  const ik = Object.keys(S.FURN.kinds).filter((k) => k.startsWith('ik'));
  const bad = [];
  for (const k of ['ikTiang', 'ikKios', 'ikKafe']) {
    const F = S.FURN.kinds[k]; if (!F) continue;
    for (let i = 0; i < F.n; i++) {
      const s = F.ps[i], za = F.pz[i];
      if (S.onRoad(s, za) || S.inWater(s, za, 0)) bad.push([k, +s.toFixed(1), +za.toFixed(1)]);
      if (k === 'ikTiang') { const D = S.districtAt(s, za); if (!D || D.kind === 'tani') bad.push([k, 'distrik', D && D.name]); }
    }
  }
  return { on: I.on, merek: K ? K.BRANDS.length : 0, sel: avg.length / 3, hitam, langs: I.langs, ja: I.row ? I.row.ja : null, tokyo,
    aLang, count: I.count, ik, bad: bad.slice(0, 10), nBad: bad.length, lcd: I.lcd ? { on: I.lcd.on, diag: I.lcd.diag, len: I.lcd.len } : null };
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
            info = await pg.evaluate(INFO)
            # malam di alun-alun New York: render beberapa frame lalu baca piksel kanvas (NaN tampak sebagai piksel rusak / error)
            await pg.evaluate("""() => { const S = window.__station; S.teleport('nyc'); S.clock.hour = 22; S.updateLighting(0); }""")
            await pg.wait_for_timeout(4000)
            px = await pg.evaluate("""() => { const c = document.querySelector('canvas'); const g = document.createElement('canvas'); g.width = 32; g.height = 20;
              const x = g.getContext('2d'); x.drawImage(c, 0, 0, 32, 20); const d = x.getImageData(0, 0, 32, 20).data; let s = 0; for (const v of d) s += v; return s; }""")
            hemat = await pg.evaluate("""() => { const S = window.__station; S.applyPreset(4); const F = S.FURN.kinds.ikRoofS || S.FURN.kinds.ikLogo;
              const r = F ? F.range / F.base : null, st = S.IKLAN.lcd ? S.IKLAN.lcd.static : null; S.applyPreset(0); return { k: r, lcdDiam: st }; }""")
            return {'info': info, 'px': px, 'hemat': hemat}
        r, errs = await run(b, '?preset=ultra', local, baru)
        i = r['info']
        print('baru:', json.dumps(i, ensure_ascii=False))
        print('piksel malam:', r['px'], 'Hemat:', json.dumps(r['hemat']))
        print('error:', errs[:5] or 'tidak ada')
        if not i['on']: gagal.append('IKLAN mati di jalur baru')
        if i['merek'] != 48 or i['sel'] != 192 or i['hitam']: gagal.append(f"atlas: {i['merek']} merek, {i['sel']} sel, {i['hitam']} sel hitam")
        if len(i['langs']) != 14: gagal.append(f"bahasa plang {len(i['langs'])} (harus 14)")
        if not all(i['aLang']): gagal.append('ada mesh gedung tanpa aLang')
        if i['tokyo'] is not None and i['tokyo'] != i['ja']: gagal.append(f"gedung Tokyo memakai baris {i['tokyo']}, bukan ja {i['ja']}")
        for k in ['ikRoofS', 'ikLogo', 'ikBlade', 'ikHalte', 'ikPasar', 'ikKafeS', 'ikTiangS', 'ikKiosS']:
            if not (i['count'] or {}).get(k): gagal.append(f'tidak ada papan {k}')
        if i['nBad']: gagal.append(f"{i['nBad']} papan di jalan / air / luar distrik: {i['bad']}")
        if not i['lcd'] or not i['lcd']['on']: gagal.append('layar LCD New York tidak dibuat')
        if not r['px']: gagal.append('render malam alun-alun kosong')
        if r['hemat']['k'] is None or abs(r['hemat']['k'] - 0.45) > 1e-6 or r['hemat']['lcdDiam'] is False: gagal.append(f"preset Hemat: {r['hemat']}")
        if errs: gagal.append('error halaman (baru)')

        async def lama(pg):
            return await pg.evaluate("""() => { const S = window.__station; return { on: S.IKLAN.on,
              aLang: Object.values(S.cityMeshes).some((m) => !!m.geometry.attributes.aLang), ik: Object.keys(S.FURN.kinds).filter((k) => k.startsWith('ik')),
              lcd: !!(S.IKLAN.lcd && S.IKLAN.lcd.on), def: 'IKLAN' in (S.cityMeshes.flat.material.defines || {}) }; }""")
        r2, errs2 = await run(b, '?preset=ultra&iklan=0', local, lama)
        print('?iklan=0:', json.dumps(r2), 'error:', errs2[:5] or 'tidak ada')
        if r2['on'] or r2['aLang'] or r2['ik'] or r2['lcd'] or r2['def']: gagal.append('?iklan=0: objek tahap 27 masih dibuat')
        if errs2: gagal.append('error halaman (?iklan=0)')

        async def tanpaNeon(pg):
            return await pg.evaluate("() => { const S = window.__station; return { lcd: !!(S.IKLAN.lcd && S.IKLAN.lcd.on), ik: Object.keys(S.FURN.kinds).filter((k) => k.startsWith('ik')).length }; }")
        r3, errs3 = await run(b, '?preset=ultra&neon=0', local, tanpaNeon)
        print('?neon=0:', json.dumps(r3), 'error:', errs3[:5] or 'tidak ada')
        if r3['lcd'] or not r3['ik']: gagal.append('?neon=0: LCD masih dibuat atau papan lain hilang')
        if errs3: gagal.append('error halaman (?neon=0)')
        await b.close()
    print('\nHASIL:', 'LOLOS' if not gagal else 'GAGAL\n  ' + '\n  '.join(gagal))
    sys.exit(1 if gagal else 0)

asyncio.run(main())
