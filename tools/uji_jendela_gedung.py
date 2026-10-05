"""Uji 21d + 21e (Copper Corn Station): jendela gedung kaca (gaya 0, 1) dan deretan menengah / podium (gaya 2, 11) bervariasi per
gedung, satu ruangan selebar beberapa bay, ruangan tidak terlihat dari jauh, pantulan kaca dengan penghalang gedung seberang (21e).
Satu instance gedung dirender sendirian (seperti uji_gedung_malam.py). Waktu, putaran sunline, dan awan dibekukan (freeze).
Catatan: perbandingan dengan versi lain dari git dibuang; dua halaman tetap berbeda walau waktu dibekukan (peta bayangan dirender ulang
tiap frame, selisih kontrol satu halaman 0,0115).
Ukuran:
  1. variasi: periode mullion (bay) dan tinggi lantai per gaya 1, 2, 11 (autokorelasi profil kolom dan baris, kamera ortografik)
  2. jauh: di 150 m gambar interior hidup = mati (0 nilai beda) untuk gaya 0, 1, 2, 11; di 14 m berbeda jelas
  3. tanpa nilai tidak valid siang dan malam di 15 / 60 / 150 / 800 m
  4. pantulan ngarai kota (21e): dengan dan tanpa baris penghalang (shader dipinjam sementara, satu blok sinkron): etalase lantai
     dasar berubah jelas (gedung seberang terpantul), kaca lantai 90 m menara > 120 m hampir tidak berubah (masih daratan seberang)
  INFO: lebar bentangan jendela menyala malam (metode berisik, bukan syarat)
Pakai: python tools/uji_jendela_gedung.py   (butuh: pip install playwright && playwright install chromium)
Tanpa akses CDN langsung: THREE_LOCAL=<folder berisi three.module.js dan three.core.js> python tools/uji_jendela_gedung.py
Chromium sendiri: CHROMIUM=<jalur executable>"""
import asyncio, os, pathlib
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
  const freeze = (h) => {                                // jam tetap, sunline tidak berputar, tanpa awan: gambar bisa diulang
    S.WEATHER.cover = 0; S.WEATHER.ov = 0; for (const g of S.CLOUD.groups) g.w = 0; S.CLOUD.drawShadow();
    S.clock.sim = 500; S.clock.hour = h; S.updateLighting(); if (S.BUILD_U.uTime) S.BUILD_U.uTime.value = 0;
  };
  const lum = (p, i) => 0.2126 * p[i] + 0.7152 * p[i + 1] + 0.0722 * p[i + 2];
  const dispose = (r) => { r.rt.dispose(); r.geo1.dispose(); };
  return { S, THREE, wait, freeze, rig, shoot, persp, ortho, lum, dispose };
};
"""

UJI = r"""
(async () => {
  const { S, wait, freeze, rig, shoot, persp, ortho, lum, dispose } = await window.__lib(), out = {}, info = [];
  S.teleport('nyc'); await wait(2500); freeze(11);
  const period = (prof, mpp, lo, hi) => {
    const n = prof.length, mean = prof.reduce((a, b) => a + b, 0) / n, p = prof.map((v) => v - mean);
    const ac = (k) => { let s = 0; for (let i = 0; i + k < n; i++) s += p[i] * p[i + k]; return s / (n - k); };
    const r0 = ac(0); if (r0 < 1e-12) return { per: 0, str: 0 };
    let best = 0, bk = 0; for (let k = Math.ceil(lo / mpp); k <= Math.min(n / 2, Math.floor(hi / mpp)); k++) { const a = ac(k) / r0; if (a > best + 1e-9) { best = a; bk = k; } }
    return { per: bk * mpp, str: best };
  };
  const pickOf = (st, minH, minW, n) => {
    const all = []; S.BUILD.flat.forEach((q, i) => { if (q[7] === st && q[4] > minH && q[2] >= minW) all.push(i); });
    const step = Math.max(1, Math.floor(all.length / n)), pk = []; for (let i = 0; i < all.length && pk.length < n; i += step) pk.push(all[i]);
    return pk;
  };
  const picks = { 1: pickOf(1, 40, 18, 8), 2: pickOf(2, 17, 16, 6), 11: pickOf(11, 6, 12, 6), 0: pickOf(0, 14, 12, 2) };
  // 1. variasi per gaya
  const SZ = 320, SPAN = 16, mpp = SPAN / SZ;
  info.push(`gedung terpilih: gaya 1 ${picks[1].length}, gaya 2 ${picks[2].length}, gaya 11 ${picks[11].length}, gaya 0 ${picks[0].length}`);
  for (const st of [1, 2, 11]) {
    const rows = [];
    for (const idx of picks[st]) {
      const r = rig('flat', idx, SZ), H = r.L[4];
      const span = st === 1 ? SPAN : st === 11 ? Math.min(SPAN, 0.9 * r.L[2]) : Math.min(SPAN, 0.8 * H, 0.9 * r.L[2]), mpp = span / SZ;   // gedung rendah: gambar tetap di dalam muka (podium 7-10 m: satu lantai di atas etalase, hanya bay)
      freeze(11); S.BUILD_U.uInterior.value = 0; const p0 = shoot(r, ortho(r, 60, span, st === 1 ? -0.25 * H : st === 11 ? 0 : 0.1 * H));
      const col = new Array(SZ).fill(0), row = new Array(SZ).fill(0);
      for (let y = 0; y < SZ; y++) for (let x = 0; x < SZ; x++) { const v = lum(p0, (y * SZ + x) * 4); col[x] += v / SZ; row[y] += v / SZ; }
      const h = period(col, mpp, 0.9, 7), v = period(row, mpp, 2.4, 5.5);
      rows.push({ H, W: r.L[2], bay: h.per, bayStr: h.str, fh: v.per }); dispose(r);
    }
    const uniq = (a, q) => new Set(a.map((x) => Math.round(x / q))).size;
    const bays = rows.filter((q) => q.bayStr > 0.15).map((q) => q.bay), fhs = rows.filter((q) => q.fh > 0).map((q) => q.fh);
    const nb = uniq(bays, 0.3), nf = uniq(fhs, 0.2);
    out[`gaya ${st}: ${rows.length} gedung, jarak mullion ${nb} nilai berbeda, tinggi lantai ${nf} nilai berbeda (butuh masing-masing >= 2${st === 11 ? '; podium: lantai tidak diukur' : ''})`] = rows.length >= 3 && nb >= 2 && (st === 11 || nf >= 2);
    rows.forEach((q) => info.push(`gaya ${st} H${q.H.toFixed(0)} W${q.W.toFixed(0)} bay ${q.bay.toFixed(2)} (${q.bayStr.toFixed(2)}) lantai ${q.fh.toFixed(2)}`));
  }
  S.BUILD_U.uInterior.value = 1;
  // INFO: bentangan jendela menyala malam (interior mati, kamera ortografik)
  freeze(20); S.BUILD_U.uInterior.value = 0;
  for (const st of [1, 2, 11]) {
    const ws = [];
    for (const idx of picks[st]) {
      const r = rig('flat', idx, SZ), H = r.L[4], p1 = shoot(r, ortho(r, 60, SPAN, st === 1 ? -0.25 * H : 0.15 * H)), vals = [];
      for (let i = 0; i < SZ * SZ; i++) vals.push(lum(p1, i * 4)); vals.sort((a, b) => a - b); const thr = Math.max(0.02, vals[Math.floor(vals.length * 0.99)] * 0.25), runs = [];
      for (let y = 0; y < SZ; y++) { let start = -1, lastOn = -1;
        for (let x = 0; x <= SZ; x++) { const on = x < SZ && lum(p1, (y * SZ + x) * 4) > thr;
          if (on) { if (start < 0) start = x; lastOn = x; }
          else if (start >= 0 && (x >= SZ || x - lastOn > 1.7 / mpp)) { runs.push((lastOn - start + 1) * mpp); start = -1; } } }
      runs.sort((a, b) => a - b); const u = runs.filter((v) => v > 1.0); ws.push(u.length ? u[Math.floor(u.length * 0.5)].toFixed(1) : '-'); dispose(r);
    }
    info.push(`INFO gaya ${st}: median bentangan jendela menyala malam (m, 16 m = selebar gambar): ${ws.join(' ')}`);
  }
  S.BUILD_U.uInterior.value = 1;
  // 2. jauh tanpa ruangan
  const cases = [1, 0, 2, 11].flatMap((st) => picks[st].slice(0, 2));
  let farDiff = 0, nearDiff = 0, farN = 0; freeze(11);
  for (const idx of cases) {
    const r = rig('flat', idx, 192);
    S.BUILD_U.uInterior.value = 0; const f0 = shoot(r, persp(r, 150, 12)), n0 = shoot(r, persp(r, 14, 38, 0));
    S.BUILD_U.uInterior.value = 1; const f1 = shoot(r, persp(r, 150, 12)), n1 = shoot(r, persp(r, 14, 38, 0));
    for (let i = 0; i < f0.length; i++) { if (f0[i] !== f1[i]) farDiff++; if (n0[i] !== n1[i]) nearDiff++; } farN += f0.length;
    dispose(r);
  }
  out[`150 m: gambar interior hidup = mati untuk gaya 0, 1, 2, 11 (${farDiff} dari ${farN} nilai beda)`] = farDiff === 0;
  out[`14 m: interior mengubah gambar (${nearDiff} nilai beda)`] = nearDiff > 1000;
  // 3. nilai tidak valid
  let bad = 0, nPx = 0;
  for (const hour of [11, 23]) {
    freeze(hour);
    for (const idx of cases) {
      const r = rig('flat', idx, 128);
      for (const d of [15, 60, 150, 800]) { const p = shoot(r, persp(r, d, d < 100 ? 40 : 12, 0)); for (let i = 0; i < p.length; i++) { nPx++; if (!Number.isFinite(p[i]) || p[i] < 0) bad++; } }
      dispose(r);
    }
  }
  out[`siang dan malam di 15 / 60 / 150 / 800 m: tanpa nilai tidak valid (${bad} dari ${nPx})`] = bad === 0;
  out.__info = info;
  return out;
})()
"""

# pantulan ngarai kota (21e): gambar dirender dua kali dalam satu blok sinkron (tanpa frame di antaranya), dengan shader asli dan
# shader yang baris penghalangnya dibuang. Selisih = efek gedung seberang saja (tidak ada kebisingan waktu, awan, atau bayangan)
CANYON = r"""
(async () => {
  const { S, THREE, wait, freeze, rig, shoot, persp, dispose } = await window.__lib(), out = {}, info = [];
  S.teleport('nyc'); await wait(2500);
  const oblique = (r, back, side, y) => {   // kamera miring: back m di depan muka, side m ke samping, menatap titik setinggi y di muka
    const cam = new THREE.PerspectiveCamera(30, 1, 0.5, 6000); cam.up.copy(r.up);
    const tgt = r.ctr.clone().addScaledVector(r.up, y - r.L[4] / 2).addScaledVector(r.out, r.L[3] / 2);
    cam.position.copy(tgt).addScaledVector(r.out, back).addScaledVector(r.rt3, side).addScaledVector(r.up, 1.7 - y); cam.lookAt(tgt); return cam;
  };
  const mat = S.cityMeshes.flat.material, fs0 = mat.fragmentShader, KEY = 'envF = mix(envF, bldC, blkR);';
  if (!fs0.includes(KEY)) return { ['baris penghalang pantulan ditemukan di BUILD_FS']: false };
  const views = [];
  S.BUILD.flat.forEach((q, i) => { if ((q[7] === 11 || q[7] === 2) && q[4] > 14 && q[2] >= 14 && views.filter((v) => v.k === 'shop').length < 4) views.push({ k: 'shop', i }); });
  S.BUILD.flat.forEach((q, i) => { if (q[7] === 1 && q[4] > 120 && views.filter((v) => v.k === 'top').length < 2) views.push({ k: 'top', i }); });
  const rel = { shop: [], top: [] }, rgb = [];
  for (const hour of [11, 22]) {
    for (const v of views) {
      const r = rig('flat', v.i, 96), cam = v.k === 'shop' ? oblique(r, 7, 8, 2.0) : persp(r, 40 + r.L[3] / 2, 20, 90 - r.L[4] / 2);   // etalase dilihat miring sekitar 50 derajat dari mata 1,7 m (pantulan kuat, Fresnel)
      freeze(hour); const a = shoot(r, cam), a2 = shoot(r, cam);
      mat.fragmentShader = fs0.replace(KEY, ''); mat.needsUpdate = true; const b = shoot(r, cam);
      mat.fragmentShader = fs0; mat.needsUpdate = true;
      let d = 0, m = 0, ctl = 0, bad = 0;
      for (let i = 0; i < a.length; i++) { d += Math.abs(a[i] - b[i]); m += b[i]; ctl += Math.abs(a[i] - a2[i]); if (!Number.isFinite(a[i]) || a[i] < 0) bad++; }
      out[`${v.k}:${v.i} jam ${hour}: deterministik dan tanpa nilai tidak valid (${ctl} / ${bad})`] = ctl === 0 && bad === 0;
      if (hour === 11) { rel[v.k].push(d / Math.max(1e-6, m)); const avg = (x, c) => { let s = 0; for (let i = c; i < x.length; i += 4) s += x[i]; return (s / (x.length / 4)).toFixed(4); };
        rgb.push(`${v.k}:${v.i} RGB rata-rata dengan penghalang ${[0, 1, 2].map((c) => avg(a, c)).join(' ')}, tanpa ${[0, 1, 2].map((c) => avg(b, c)).join(' ')}`); }
      dispose(r);
    }
  }
  const f = (x) => x.map((v) => v.toFixed(3)).join(' ');
  out[`etalase lantai dasar (dilihat miring dari trotoar) memantulkan gedung seberang: selisih relatif ${f(rel.shop)} (butuh > 0,05 tiap gedung)`] = rel.shop.length >= 2 && Math.min(...rel.shop) > 0.05;
  out[`kaca lantai 90 m menara > 120 m tetap memantulkan daratan seberang: selisih relatif ${f(rel.top)} (butuh < 0,02)`] = rel.top.length >= 1 && Math.max(...rel.top) < 0.02;
  out.__info = rgb;
  return out;
})()
"""

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
        res = {} if os.environ.get('HANYA_PANTULAN') else await pg.evaluate(UJI)
        info = res.pop('__info', [])
        for k, v in res.items(): print(('OK   ' if v else 'GAGAL'), k)
        for r in info: print('   ', r)
        res = await pg.evaluate(CANYON)
        info = res.pop('__info', [])
        for k, v in res.items(): print(('OK   ' if v else 'GAGAL'), k)
        for r in info: print('    INFO', r)
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())
