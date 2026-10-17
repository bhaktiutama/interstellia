"""Uji orang model GLB di Copper (rencana tahap 28G2, docs/cooper-station/rencana-tahap-28-glb-cooper-station.md):
model baru terpasang, ember (karakter, tingkat detail) berisi orang sesuai jumlah, tingkat detail menurut jarak, segitiga per tingkat di anggaran,
hanya ember berisi yang digambar, payung dan duduk tidak merusak, jumlah draw call orang, tanpa error; ?orang=lama = model kotak lama persis
(sidik jari tools/uji_orang_lama.json). Pakai: python tools/uji_orang.py   (butuh: pip install playwright; THREE_LOCAL / CHROMIUM opsional)"""
import asyncio, json, os, pathlib, sys
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
BARU = r"""
(async () => {
  const st = window.__station, P = st.PEDS, out = {};
  const frames = (n) => new Promise((r) => { let k = 0; const f = () => (++k >= n ? r() : requestAnimationFrame(f)); requestAnimationFrame(f); });
  out.newModel = P.newModel; out.lama = P.lama; out.mesh = !!P.mesh; out.ember = P.buckets ? P.buckets.length : 0; out.karakter = P.chars ? P.chars.length : 0;
  const hasil = {};
  for (const k of ['market', 'nyc', 'spaceport', 'baseball']) {
    st.teleport(k); st.updateCamera(); for (let i = 0; i < 40; i++) { st.clock.sim += 0.1; st.stepPeds(0.1); } st.updatePeds(); await frames(3);
    const B = P.buckets, sum = B.reduce((s, b) => s + b.n, 0), vis = B.filter((b) => b.mesh.visible).length;
    let salah = 0, tri = 0, instOk = 0;
    for (const b of B) { if (b.g.instanceCount !== b.n) salah++; if (b.n > b.cap) salah++; tri += b.n * P.chars[b.ch].lods[b.lod].nt;
      for (let i = 0; i < b.n * 4; i++) if (!Number.isFinite(b.P[i]) || !Number.isFinite(b.I[i]) || !Number.isFinite(b.J[i])) salah++; if (b.n > 0 && !b.mesh.visible) salah++; }
    const per = [0, 1, 2].map((l) => B.filter((b) => b.lod === l).reduce((s, b) => s + b.n, 0));
    hasil[k] = { n: P.n, jumlahEmber: sum, tingkat: per, ember_terlihat: vis, salah, tiriOrang: tri, draw: renderer_calls(st) };
  }
  function renderer_calls(st) { return st.renderer.info.render.calls; }
  out.lokasi = hasil;
  // radius tingkat detail: orang L0 hanya dalam batas dekat preset
  st.applyPreset(0); out.lodR_ultra = P.lodR.slice(); st.applyPreset(4); out.lodR_hemat = P.lodR.slice(); st.applyPreset(0);
  out.tris = P.chars.map((c) => c.lods.map((l) => l.nt));
  // payung dan duduk: paksa payung terbuka lalu hitung orang berpayung
  P.uk = 1; st.updatePeds(); out.payung = P.umbMesh.geometry.instanceCount;
  out.duduk = P.list.filter((p) => p.pose === 2).length;
  return out;
})()
"""
LAMA = r"""
(async () => { const st = window.__station, P = st.PEDS, g = P.mesh && P.mesh.geometry, A = g && g.attributes;
  const fnv = (arr) => { let h = 0x811c9dc5; const u = new Uint8Array(arr.buffer, arr.byteOffset, arr.byteLength); for (let i = 0; i < u.length; i++) { h ^= u[i]; h = Math.imul(h, 0x01000193) >>> 0; } return h.toString(16); };
  return { lama: P.lama, newModel: P.newModel, buckets: !!P.buckets, geo: g ? { tri: g.index.count / 3, titik: A.position.count, hashPos: fnv(A.position.array), hashNrm: fnv(A.normal.array), hashPart: fnv(A.aPart.array), hashIdx: fnv(g.index.array) } : null }; })()
"""

async def buka(b, url, local):
    pg = await b.new_page(viewport={'width': 320, 'height': 200}); errs = []
    pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)[:200]))
    pg.on('console', lambda m: errs.append(m.type + ': ' + m.text[:200]) if m.type in ('error', 'warning') else None)
    if local:
        async def serve(route):
            await route.fulfill(path=str(pathlib.Path(local) / route.request.url.rsplit('/', 1)[-1]), content_type='text/javascript', headers={'Access-Control-Allow-Origin': '*'})
        await pg.route('https://cdn.jsdelivr.net/**', serve)
    await pg.goto(url); await pg.wait_for_function('window.__stationReady === true', timeout=900000)
    return pg, errs

async def main():
    local = os.environ.get('THREE_LOCAL'); chromium = os.environ.get('CHROMIUM'); base = ROOT.joinpath('experiences/cooper-station/index.html').as_uri()
    gagal = []
    def cek(nama, ok, info=''):
        print(('LOLOS ' if ok else 'GAGAL ') + nama + (' | ' + str(info) if info else '')); 
        if not ok: gagal.append(nama)
    async with async_playwright() as p:
        kw = {'args': ['--use-angle=swiftshader', '--enable-unsafe-swiftshader']}
        if chromium: kw['executable_path'] = chromium
        b = await p.chromium.launch(**kw)
        pg, errs = await buka(b, base, local); r = await pg.evaluate(BARU)
        cek('model GLB terpasang (13 karakter x 3 tingkat = 39 ember, tanpa mesh kotak lama)', r['newModel'] and not r['lama'] and not r['mesh'] and r['ember'] == 39 and r['karakter'] == 13, f"ember {r['ember']}, karakter {r['karakter']}")
        for k, v in r['lokasi'].items():
            cek(f'{k}: {v["n"]} orang = jumlah ember, instanceCount cocok, nilai valid, ember berisi terlihat', v['n'] == v['jumlahEmber'] and v['salah'] == 0, f"tingkat {v['tingkat']}, ember terlihat {v['ember_terlihat']}, tiri orang {v['tiriOrang']}, draw call adegan {v['draw']}")
        cek('radius tingkat detail per preset (Ultra 30 / 90 m, Hemat tanpa L0)', r['lodR_ultra'] == [30, 90] and r['lodR_hemat'] == [0, 35], f"{r['lodR_ultra']} {r['lodR_hemat']}")
        cek('segitiga per karakter per tingkat <= 3.000 / 750 / 180', all(t[0] <= 3000 and t[1] <= 750 and t[2] <= 180 for t in r['tris']), r['tris'][0])
        cek('payung terbuka bila hujan dipaksa, orang duduk ada', r['payung'] > 0 and r['duduk'] > 0, f"payung {r['payung']}, duduk {r['duduk']}")
        cek('tanpa error atau peringatan di konsol', not errs, errs[:3])
        await pg.close()
        pg, errs = await buka(b, base + '?orang=lama', local); r = await pg.evaluate(LAMA)
        lama = json.loads(ROOT.joinpath('tools/uji_orang_lama.json').read_text())
        cek('?orang=lama: model kotak lama persis (sidik jari geometri sama dengan sebelum tahap 28)', r['lama'] and not r['newModel'] and not r['buckets'] and r['geo'] == lama, r['geo'])
        cek('?orang=lama tanpa error', not errs, errs[:3])
        await b.close()
    print('\nHASIL:', 'LOLOS' if not gagal else 'GAGAL ' + str(gagal)); sys.exit(1 if gagal else 0)

asyncio.run(main())
