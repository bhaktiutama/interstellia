"""Uji Millar's World R1: halaman termuat tanpa error, kamus English lengkap, 5 preset bisa berganti (dan ?preset=hemat),
tidak ada daratan (dasar laut selalu di bawah air terendah), fisika (1,3 g, lompat 77%), gelombang 125 m/s, jam dilatasi,
tersapu = kembali dengan penalti waktu, tidak ada nilai tidak valid (NaN/Inf) di render HDR tiap preset.
Pakai: python tools/uji_millar.py   (butuh: pip install playwright && playwright install chromium)
Tanpa akses CDN langsung: THREE_LOCAL=<folder berisi three.module.js dan three.core.js> python tools/uji_millar.py
Chromium sendiri: CHROMIUM=<jalur executable>"""
import asyncio, os, pathlib
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
UJI = r"""
(async () => {
  const M = window.__millar, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms));
  // 1. kamus English: semua t('...') di kode dan semua data-t
  const EN = M.I18N.en, src = document.querySelector('script[type=module]').textContent;
  const re = /\bt\((['`])((?:\\.|(?!\1).)*)\1/g; let m; const hilang = [];
  while ((m = re.exec(src))) if (!(m[2] in EN)) hilang.push(m[2]);
  document.querySelectorAll('[data-t]').forEach((el) => { if (!(el.dataset.t in EN)) hilang.push(el.dataset.t); });
  for (const p of M.PRESETS) if (!(p.name in EN)) hilang.push(p.name);
  for (const x of M.MOODS) if (!(x.key in EN)) hilang.push(x.key);
  for (const v of M.CONFIG.views) if (!(v.key in EN)) hilang.push(v.key);
  out[`teks tanpa entri English: ${hilang.length}${hilang.length ? ' (' + hilang.slice(0, 5).join(' | ') + ')' : ''}`] = hilang.length === 0;

  // 2. tidak ada daratan: dasar laut tertinggi < air terendah (surut penuh dikurangi lembah ombak terdalam)
  let bedMax = -9;
  for (let i = 0; i < 40000; i++) { const x = (Math.random() - 0.5) * 20000, z = (Math.random() - 0.5) * 20000; bedMax = Math.max(bedMax, M.seabed(x, z)); }
  const trough = M.CHOP.base.slice(0, 16).reduce((s, b) => s + (b.a || 0), 0);
  const low = -M.CONFIG.wave.dd - M.CONFIG.chop.Hs / 2;
  out[`dasar laut tertinggi ${bedMax.toFixed(3)} m < air terendah ${low.toFixed(3)} m (surut + setengah Hs)`] = bedMax < low;
  out[`jumlah amplitudo ombak ${trough.toFixed(3)} m (batas atas lembah, info)`] = true;

  // 3. mulai, fisika lompat dengan langkah tetap
  M.start(); await wait(200);
  const P = M.P; P.view = 0; P.x = 0; P.z = 0; P.y = M.seabed(0, 0) + M.CONFIG.eye; P.ground = true;
  const y0 = P.y; P.vy = M.CONFIG.jumpV; P.ground = false; let top = y0;
  for (let i = 0; i < 240; i++) { M.stepPlayer(1 / 120); top = Math.max(top, P.y); }
  const jh = top - y0, jEarth = M.CONFIG.jumpV ** 2 / (2 * 9.80665);
  out[`lompat ${jh.toFixed(3)} m = ${(100 * jh / jEarth).toFixed(1)}% dari Bumi (harapan 77%)`] = Math.abs(jh / jEarth - 0.769) < 0.02;
  out[`gravitasi ${M.CONFIG.g} m/s2 = ${(M.CONFIG.g / 9.80665).toFixed(3)} g`] = Math.abs(M.CONFIG.g / 9.80665 - 1.3) < 0.002;

  // 4. gelombang dan jam: 10 s simulasi
  M.U.uWX.value += 80000 - M.frontX(0); const f0 = M.frontX(0), c0 = M.CLK.planet;
  for (let i = 0; i < 100; i++) M.simStep(0.1, 0.1);
  const v = (f0 - M.frontX(0)) / 10, dp = M.CLK.planet - c0;
  out[`kecepatan gelombang ${v.toFixed(2)} m/s (125)`] = Math.abs(v - 125) < 0.01;
  out[`1 s planet = ${(dp / 10 * M.CONFIG.dil / 3600).toFixed(2)} jam di luar (17,04)`] = Math.abs(dp / 10 * M.CONFIG.dil / 3600 - 17.045) < 0.01;

  // 5. tersapu: gelombang 150 m di depan
  M.U.uWX.value += 150 - M.frontX(0); const cBefore = M.CLK.planet;
  for (let i = 0; i < 300 && M.CLK.swept <= 0; i++) M.simStep(0.05, 0.05);
  const lost = (M.CLK.planet - cBefore) * M.CONFIG.dil / (365.25 * 86400);
  out[`tersapu: kembali ke awal (x ${P.x}), waktu di luar bertambah ${lost.toFixed(2)} tahun`] = M.CLK.swept > 0 && P.x === 0 && lost > 0.77;
  M.CLK.white = 0; M.U.uWX.value += 12000 - M.frontX(0);

  // 6. tiap preset: berganti tanpa error, render HDR tanpa NaN/Inf dan tanpa titik menyala (> 50) di cakrawala
  //    (dulu: dengan MSAA, kedalaman air diekstrapolasi negatif di segitiga kecil cakrawala -> nilai meledak)
  const r = M.renderer, from = M.THREE.DataUtils.fromHalfFloat;
  M.P.pitch = 0.02; M.P.yaw = -Math.PI / 2 + 0.25;
  for (let i = 0; i < M.PRESETS.length; i++) {
    M.applyPreset(i); await wait(900);
    const T = M.POST.hdr, w = T.width, h = T.height;
    let bad = 0, hot = 0, mx = 0;
    const buf = new Uint16Array(w * h * 4); r.readRenderTargetPixels(T, 0, 0, w, h, buf);
    for (let k = 0; k < buf.length; k += 4) for (let c = 0; c < 3; c++) { const x = from(buf[k + c]); if (!Number.isFinite(x)) bad++; else { if (x > 50) hot++; mx = Math.max(mx, x); } }
    out[`preset ${M.PRESETS[i].name}: ${w}x${h}${T.samples ? ' MSAA ' + T.samples : ''}, tidak valid ${bad}, titik > 50: ${hot}, maks ${mx.toFixed(2)}`] = bad === 0 && hot === 0;
  }
  M.applyPreset(4);
  return out;
})()
"""

async def main():
    local = os.environ.get('THREE_LOCAL')
    async with async_playwright() as p:
        exe = os.environ.get('CHROMIUM')                              # opsional: jalur Chromium sendiri
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'], **({'executable_path': exe} if exe else {}))
        errs = []
        async def page(q):
            pg = await b.new_page(viewport={'width': 480, 'height': 270})
            pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
            pg.on('console', lambda m: errs.append(m.type + ': ' + m.text[:300]) if m.type in ('error', 'warning') else None)
            if local:
                async def serve(route):
                    await route.fulfill(path=str(pathlib.Path(local) / route.request.url.rsplit('/', 1)[-1]), content_type='text/javascript',
                                        headers={'Access-Control-Allow-Origin': '*'})
                await pg.route('https://cdn.jsdelivr.net/**', serve)
            await pg.goto(ROOT.joinpath('experiences/millar/index.html').as_uri() + q)
            await pg.wait_for_function('window.__millarReady === true', timeout=120000)
            await pg.wait_for_timeout(1500)
            return pg
        pg = await page('?lang=id')
        hasil = await pg.evaluate(UJI)
        pg2 = await page('?preset=hemat')
        hem = await pg2.evaluate('[window.__millar.PRESET.idx, window.__millar.PRESET.auto]')
        hasil[f'?preset=hemat -> preset {hem[0]}, otomatis {hem[1]}'] = hem == [4, False]
        ok = True
        for k, v in hasil.items():
            print(('OK   ' if v else 'GAGAL') + ' ' + k); ok &= bool(v)
        print('error:', errs[:10] or 'tidak ada')
        print('HASIL:', 'LULUS' if ok and not errs else 'GAGAL')
        await b.close()

asyncio.run(main())
