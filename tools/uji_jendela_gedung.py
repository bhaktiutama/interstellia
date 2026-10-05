"""Uji 21d (Copper Corn Station): jendela gedung kantor tinggi (gaya 0 dan 1) bervariasi per gedung, satu ruangan selebar
beberapa bay, dan ruangan tidak terlihat dari jauh. Satu instance gedung dirender sendirian (seperti uji_gedung_malam.py).
Ukuran:
  1. variasi: periode mullion (bay) dan tinggi lantai dari 10 menara kaca berbeda (autokorelasi profil kolom dan baris, kamera ortografik)
  2. ruangan: periode struktur di selisih gambar (interior hidup - mati) di 14 m dibanding periode mullion
  3. jauh: di 150 m gambar interior hidup = mati (0 nilai beda) untuk gaya 0 dan 1; di 14 m berbeda jelas
  4. gaya lain (2, 3, 7, 8, 9, 11) sama dengan versi sebelum 21d (UJI_BASE, bawaan origin/main; selisih dalam kebisingan awan dan waktu) bila git tersedia
  5. tanpa nilai tidak valid siang dan malam di 15 / 60 / 150 / 800 m
Pakai: python tools/uji_jendela_gedung.py   (butuh: pip install playwright && playwright install chromium)
Tanpa akses CDN langsung: THREE_LOCAL=<folder berisi three.module.js dan three.core.js> python tools/uji_jendela_gedung.py
Chromium sendiri: CHROMIUM=<jalur executable>"""
import asyncio, os, pathlib, subprocess
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = 'experiences/cooper-station/index.html'

# fungsi bersama: render satu instance gedung ke target float. type = kunci BUILD / cityMeshes, idx = indeks instance
LIB = r"""
window.__lib = async () => {
  const S = window.__station, THREE = await import('https://cdn.jsdelivr.net/npm/three@0.186.1/build/three.module.js');
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const rig = (type, idx, size) => {
    const L = S.BUILD[type][idx], src = S.cityMeshes[type], geo1 = src.geometry.clone(), m1 = new THREE.Matrix4();
    geo1.setAttribute('aStyle', new THREE.InstancedBufferAttribute(new Float32Array([L[7], L[8]]), 2));
    const one = new THREE.InstancedMesh(geo1, src.material, 1); src.getMatrixAt(idx, m1); one.setMatrixAt(0, m1);
    if (src.instanceColor) { const c = new THREE.Color(); src.getColorAt(idx, c); one.setColorAt(0, c); }
    one.frustumCulled = false; geo1.computeBoundingBox();
    const ctr = geo1.boundingBox.getCenter(new THREE.Vector3()).applyMatrix4(m1);
    const out = new THREE.Vector3(0, 0, -1).transformDirection(m1), up = new THREE.Vector3(0, 1, 0).transformDirection(m1), rt3 = new THREE.Vector3().crossVectors(up, out);
    const sc = new THREE.Scene(); sc.add(one); sc.background = new THREE.Color(0, 0, 0);
    const rt = new THREE.WebGLRenderTarget(size, size, { type: THREE.FloatType });
    return { L, one, ctr, out, up, rt3, sc, rt, size, geo1 };
  };
  const shoot = (r, cam) => {
    cam.updateMatrixWorld(); S.renderer.setRenderTarget(r.rt); S.renderer.clear(); S.renderer.render(r.sc, cam); S.renderer.setRenderTarget(null);
    const px = new Float32Array(r.size * r.size * 4); S.renderer.readRenderTargetPixels(r.rt, 0, 0, r.size, r.size, px); return px;
  };
  const persp = (r, dist, fov = 20, yOff = 0) => {      // kamera di depan muka, mata setinggi ctr + yOff
    const cam = new THREE.PerspectiveCamera(fov, 1, 0.5, 6000); cam.up.copy(r.up);
    const tgt = r.ctr.clone().addScaledVector(r.up, yOff); cam.position.copy(tgt).addScaledVector(r.out, dist); cam.lookAt(tgt); return cam;
  };
  const ortho = (r, dist, span, yOff) => {              // ortografik: span m x span m, piksel = span / size m
    const cam = new THREE.OrthographicCamera(-span / 2, span / 2, span / 2, -span / 2, 0.5, 6000); cam.up.copy(r.up);
    const tgt = r.ctr.clone().addScaledVector(r.up, yOff); cam.position.copy(tgt).addScaledVector(r.out, dist); cam.lookAt(tgt); return cam;
  };
  const lum = (p, i) => 0.2126 * p[i] + 0.7152 * p[i + 1] + 0.0722 * p[i + 2];
  const dispose = (r) => { r.rt.dispose(); r.geo1.dispose(); };
  return { S, THREE, wait, rig, shoot, persp, ortho, lum, dispose };
};
"""

UJI = r"""
(async () => {
  const { S, wait, rig, shoot, persp, ortho, lum, dispose } = await window.__lib(), out = {}, info = {};
  S.teleport('nyc'); S.clock.hour = 11; S.updateLighting(); await wait(2500);
  const tall = []; S.BUILD.flat.forEach((q, i) => { if (q[7] === 1 && q[4] > 40 && q[2] >= 18) tall.push(i); });
  const step = Math.max(1, Math.floor(tall.length / 10)), pick = []; for (let i = 0; i < tall.length && pick.length < 10; i += step) pick.push(tall[i]);
  out[`menara kaca > 40 m ditemukan: ${tall.length} (diuji ${pick.length})`] = pick.length >= 4;
  // periode dominan dari profil 1D (autokorelasi), lag dalam piksel -> meter
  const period = (prof, mpp, lo, hi) => {
    const n = prof.length, mean = prof.reduce((a, b) => a + b, 0) / n, p = prof.map((v) => v - mean);
    const ac = (k) => { let s = 0; for (let i = 0; i + k < n; i++) s += p[i] * p[i + k]; return s / (n - k); };
    const r0 = ac(0); if (r0 < 1e-12) return { per: 0, str: 0 };
    let best = 0, bk = 0; for (let k = Math.ceil(lo / mpp); k <= Math.min(n / 2, Math.floor(hi / mpp)); k++) { const a = ac(k) / r0; if (a > best + 1e-9) { best = a; bk = k; } }
    return { per: bk * mpp, str: best };
  };
  const SZ = 384, SPAN = 16, mpp = SPAN / SZ, rows = [];
  for (const idx of pick) {
    const r = rig('flat', idx, SZ), H = r.L[4];
    const cam = ortho(r, 60, SPAN, -0.25 * H);   // sekitar seperempat tinggi, jauh dari lobi dan mahkota
    S.BUILD_U.uInterior.value = 0; const p0 = shoot(r, cam);
    const col = new Array(SZ).fill(0), row = new Array(SZ).fill(0);
    for (let y = 0; y < SZ; y++) for (let x = 0; x < SZ; x++) { const v = lum(p0, (y * SZ + x) * 4); col[x] += v / SZ; row[y] += v / SZ; }
    const h = period(col, mpp, 0.9, 8), v = period(row, mpp, 2.4, 6);
    // ruangan: selisih interior hidup - mati dari 14 m (perspektif sempit)
    const camN = persp(r, 14, 38, 0), a0 = shoot(r, camN); S.BUILD_U.uInterior.value = 1; const a1 = shoot(r, camN);
    let diff = 0; const dprof = new Array(SZ).fill(0);
    for (let y = 0; y < SZ; y++) for (let x = 0; x < SZ; x++) { const i = (y * SZ + x) * 4, d = Math.abs(lum(a1, i) - lum(a0, i)); diff += d; dprof[x] += d / SZ; }
    const mpp14 = 2 * 14 * Math.tan(19 * Math.PI / 180) / SZ, rm = period(dprof, mpp14, 1.0, 12);
    rows.push({ idx, H, W: r.L[2], bay: h.per, bayStr: h.str, fh: v.per, room: rm.per, roomStr: rm.str, diff: diff / (SZ * SZ) });
    dispose(r);
  }
  S.BUILD_U.uInterior.value = 1;
  info.rows = rows.map((q) => `H${q.H.toFixed(0)} W${q.W.toFixed(0)} bay ${q.bay.toFixed(2)} (${q.bayStr.toFixed(2)}) lantai ${q.fh.toFixed(2)} ruang ${q.room.toFixed(2)} (${q.roomStr.toFixed(2)})`);
  const uniq = (a, q) => new Set(a.map((x) => Math.round(x / q))).size;
  const bays = rows.filter((q) => q.bayStr > 0.15).map((q) => q.bay), fhs = rows.filter((q) => q.fh > 0).map((q) => q.fh);
  out[`variasi jarak mullion: ${uniq(bays, 0.3)} nilai berbeda dari ${bays.length} menara (butuh >= 3)`] = uniq(bays, 0.3) >= 3;
  out[`variasi tinggi lantai: ${uniq(fhs, 0.25)} nilai berbeda (butuh >= 3)`] = uniq(fhs, 0.25) >= 3;
  const rooms = rows.filter((q) => q.roomStr > 0.2 && q.bayStr > 0.15 && q.bay > 0), wide = rooms.filter((q) => q.room >= 1.5 * q.bay).length;
  info.room0 = `INFO autokorelasi selisih gambar: ${wide} dari ${rooms.length} menara berpola (metode berisik, tidak jadi syarat)`;
  // lebar ruangan dari bentangan jendela menyala (malam 20.00, interior mati, kamera ortografik): bentangan menyala tidak putus
  // oleh mullion / sirip (celah <= 1,7 m digabung); ruangan gelap di antara memutus. Persentil ke-10 panjang bentangan yang tidak
  // menyentuh tepi gambar ~ lebar satu ruangan. Lantai terbuka (selebar muka) menyentuh tepi dan dilewati.
  S.clock.hour = 20; S.updateLighting(); await wait(1500); S.BUILD_U.uInterior.value = 0;
  const widths = [];
  for (const idx of pick) {
    const r = rig('flat', idx, SZ), H = r.L[4], p1 = shoot(r, ortho(r, 60, SPAN, -0.25 * H)), vals = [];
    for (let i = 0; i < SZ * SZ; i++) vals.push(lum(p1, i * 4)); vals.sort((a, b) => a - b); const thr = Math.max(0.02, vals[Math.floor(vals.length * 0.99)] * 0.25), runs = [];
    for (let y = 0; y < SZ; y++) {
      let x = 0, start = -1, lastOn = -1;
      for (x = 0; x <= SZ; x++) {
        const on = x < SZ && lum(p1, (y * SZ + x) * 4) > thr;
        if (on) { if (start < 0) start = x; lastOn = x; }
        else if (start >= 0 && (x >= SZ || x - lastOn > 1.7 / mpp)) { if (start > 1 && lastOn < SZ - 2) runs.push((lastOn - start + 1) * mpp); start = -1; }
      }
    }
    runs.sort((a, b) => a - b); const useful = runs.filter((v) => v > 1.0);
    widths.push(useful.length >= 8 ? useful[Math.floor(useful.length * 0.1)] : -1); dispose(r);
  }
  S.BUILD_U.uInterior.value = 1;
  const okW = widths.filter((v) => v > 0);
  info.room = `INFO lebar ruangan terkecil per menara (m): ${widths.map((v) => v > 0 ? v.toFixed(1) : '-').join(' ')}`;
  out[`lebar ruangan (persentil 10 bentangan menyala) >= 4,5 m pada ${okW.filter((v) => v >= 4.5).length} dari ${okW.length} menara terukur (lama: 1,5 m per bay; butuh > separuh)`] = okW.length >= 3 && okW.filter((v) => v >= 4.5).length * 2 > okW.length;
  S.clock.hour = 11; S.updateLighting(); await wait(1000);
  out[`interior terlihat dari 14 m (selisih rata-rata ${rows.reduce((a, q) => a + q.diff, 0) / rows.length > 0.01 ? 'cukup' : 'kecil'})`] = rows.reduce((a, q) => a + q.diff, 0) / rows.length > 0.01;

  // 3. jauh tanpa ruangan: gaya 0 dan 1
  const s0 = []; S.BUILD.flat.forEach((q, i) => { if (q[7] === 0 && q[4] > 14) s0.push(i); });
  const cases = [['flat', pick[0]], ['flat', pick[Math.floor(pick.length / 2)]], ['flat', s0[0]], ['flat', s0[Math.floor(s0.length / 2)]]];
  let farDiff = 0, nearDiff = 0, farN = 0;
  for (const [t, idx] of cases) {
    const r = rig(t, idx, 256);
    S.BUILD_U.uInterior.value = 0; const f0 = shoot(r, persp(r, 150, 12)), n0 = shoot(r, persp(r, 14, 38, 0));
    S.BUILD_U.uInterior.value = 1; const f1 = shoot(r, persp(r, 150, 12)), n1 = shoot(r, persp(r, 14, 38, 0));
    for (let i = 0; i < f0.length; i++) { if (f0[i] !== f1[i]) farDiff++; if (n0[i] !== n1[i]) nearDiff++; } farN += f0.length;
    dispose(r);
  }
  out[`150 m: gambar interior hidup = mati untuk gaya 0 dan 1 (${farDiff} dari ${farN} nilai beda)`] = farDiff === 0;
  out[`14 m: interior mengubah gambar (${nearDiff} nilai beda)`] = nearDiff > 1000;

  // 5. nilai tidak valid
  let bad = 0, nPx = 0;
  const tests = [pick[0], pick[pick.length - 1], s0[0]];
  for (const hour of [11, 23]) {
    S.clock.hour = hour; S.updateLighting(); await wait(1500);
    for (const idx of tests) {
      const r = rig('flat', idx, 192);
      for (const d of [15, 60, 150, 800]) {
        const p = shoot(r, persp(r, d, d < 100 ? 40 : 12, 0));
        for (let i = 0; i < p.length; i++) { nPx++; if (!Number.isFinite(p[i]) || p[i] < 0) bad++; }
      }
      dispose(r);
    }
  }
  out[`siang dan malam di 15 / 60 / 150 / 800 m: tanpa nilai tidak valid (${bad} dari ${nPx})`] = bad === 0;
  out.__info = info.rows.concat(info.room0, info.room);
  return out;
})()
"""

# gaya lain: ringkasan gambar per (tipe, gaya) untuk dibandingkan antara versi sekarang dan HEAD
OTHER = r"""
(async () => {
  const { S, wait, rig, shoot, persp, dispose } = await window.__lib(), res = {};
  S.teleport('nyc'); S.clock.hour = 11; S.updateLighting(); await wait(2500);
  const want = [2, 3, 7, 9, 11, 8];
  for (const hour of [11, 23]) {
    S.clock.hour = hour; S.updateLighting(); await wait(1200);
    for (const st of want) for (const type of ['flat', 'gable', 'hip', 'gablez']) {
      const list = S.BUILD[type]; if (!list) continue; const idx = list.findIndex((q) => q[7] === st && q[4] > 4); if (idx < 0) continue;
      const r = rig(type, idx, 96), key = `${hour}:${type}:${st}`;
      res[key] = Array.from(shoot(r, persp(r, 12 + r.L[4], 45, 0)).map((v) => Math.fround(v))); dispose(r);
    }
  }
  return res;
})()
"""

BASE = os.environ.get('UJI_BASE', 'origin/main')                       # versi sebelum 21d (commit 391ded6)

def git_head_html():
    try:
        return subprocess.run(['git', 'show', f'{BASE}:{HTML}'], cwd=ROOT, capture_output=True, check=True).stdout
    except Exception:
        return None

async def main():
    local = os.environ.get('THREE_LOCAL')
    async with async_playwright() as p:
        exe = os.environ.get('CHROMIUM')
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'], **({'executable_path': exe} if exe else {}))
        errs = []
        async def page(rel):
            pg = await b.new_page(viewport={'width': 320, 'height': 200})
            pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
            pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' else None)
            if local:
                async def serve(route):
                    await route.fulfill(path=str(pathlib.Path(local) / route.request.url.rsplit('/', 1)[-1]), content_type='text/javascript',
                                        headers={'Access-Control-Allow-Origin': '*'})
                await pg.route('https://cdn.jsdelivr.net/**', serve)
            await pg.goto(ROOT.joinpath(rel).as_uri(), wait_until='commit', timeout=240000)
            await pg.wait_for_function('window.__stationReady === true', timeout=240000)
            await pg.evaluate(LIB)
            return pg
        pg = await page(HTML)
        res = {} if os.environ.get('HANYA_GAYA_LAIN') else await pg.evaluate(UJI)
        info = res.pop('__info', [])
        for k, v in res.items(): print(('OK   ' if v else 'GAGAL'), k)
        print('menara:'); [print('   ', r) for r in info]
        # 4. gaya lain identik dengan HEAD
        old = git_head_html()
        if old is None:
            print('LEWAT git tidak tersedia: perbandingan gaya lain dengan HEAD dilewati')
        else:
            tmp = ROOT.joinpath('experiences/cooper-station/_sebelum_21d.html')
            try:
                tmp.write_bytes(old)
                pg2 = await page('experiences/cooper-station/_sebelum_21d.html')
                new, before = await pg.evaluate(OTHER), await pg2.evaluate(OTHER)
            finally:
                tmp.unlink(missing_ok=True)
            new2 = await pg.evaluate(OTHER)                                   # kontrol: versi baru dirender lagi (awan dan waktu bergerak)
            keys = sorted(set(new) & set(before))
            mad = lambda a, b: sum(abs(x - y) for x, y in zip(a, b)) / max(1, len(a))
            rows = [(k, mad(new[k], before[k]), mad(new[k], new2[k])) for k in keys]
            bad = [(k, round(d, 5), round(c, 5)) for k, d, c in rows if d > 3 * c + 1e-4]
            print(('OK   ' if keys and not bad else 'GAGAL'), f'gaya 2, 3, 7, 8, 9, 11 sama dengan {BASE} dalam kebisingan render (selisih rata-rata <= 3x kontrol): {len(keys) - len(bad)} dari {len(keys)} gambar', bad[:6])
            print('   selisih terbesar vs sebelum / kontrol:', max(((round(d, 5), round(c, 5)) for _, d, c in rows), default=None))
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())
