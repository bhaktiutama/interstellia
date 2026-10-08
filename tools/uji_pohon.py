"""Uji tahap 12b-2 + 25b-25l (Copper Corn Station): 21 jenis pohon (8 lama + 6 jenis 25b + 3 jenis 25d + 4 konifer 25e; 8 dengan ?pohon=lama),
tinggi jenis baru, persentase pohon berwarna per suasana daun, daun jatuh mati di preset Hemat dan bisa dinyalakan manual.
25j: 42 template tanpa template kosong, tanpa nilai tidak valid (NaN / Infinity) di geometri, instance, dan warna musim, normal daun aCn
tidak nol (normalize() di shader, NaN di Apple M1), aAo 0..1; warna musim per jenis sesuai field fall (Campur / Gugur), konifer selalu hijau;
?pohon=lama identik bit per bit dengan sebelum 25a (sidik jari FNV-1a 16 template dibanding tools/uji_pohon_lama.json).
Pakai: python tools/uji_pohon.py   (butuh: pip install playwright && playwright install chromium; CHROMIUM = path chromium opsional)"""
import asyncio, json, os, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(() => {
  const st = window.__station, T = st.TREES, out = {}, jenis = new Set(T.list.map((t) => T.templates[t.tpl].kind));
  out['21 jenis pohon terpakai (' + [...jenis].join(', ') + ')'] = jenis.size === 21;
  // 25b: jumlah dan tinggi (persentil 10 / 50 / 90, m) per jenis; elm sebagai pembanding
  const pc = (a, q) => a[Math.min(a.length - 1, Math.floor(q * a.length))];
  for (const k of ['elm', 'aspen', 'beech', 'basswood', 'chestnut', 'ash', 'walnut', 'hickory', 'blacklocust', 'honeylocust']) {
    const hs = T.list.filter((t) => !t.forest && T.templates[t.tpl].kind === k).map((t) => T.templates[t.tpl].height * t.sc).sort((a, b) => a - b);
    out[`INFO ${k}: ${hs.length} pohon, tinggi ${[0.1, 0.5, 0.9].map((q) => hs.length ? pc(hs, q).toFixed(1) : '-').join(' / ')} m`] = true;
    if (k !== 'elm') out[`${k}: ada di kota/taman/luar, median tinggi 5-20 m`] = hs.length > 50 && pc(hs, 0.5) > 5 && pc(hs, 0.5) < 20;
  }
  // 25h: pangsa jenis terbanyak per distrik (di luar hutan 14a) paling tinggi 30% (batas CAP; pembulatan ke bawah)
  { const D = new Map(); for (const t of T.list) { if (t.forest) continue; const d = st.districtAt(t.s, t.za), key = d ? d.name : '-';
      let e = D.get(key); if (!e) D.set(key, e = { n: 0, k: {} }); e.n++; const kd = T.templates[t.tpl].kind; e.k[kd] = (e.k[kd] || 0) + 1; }
    let worst = ['', '', 0]; for (const [name, e] of D) for (const [kd, c] of Object.entries(e.k)) if (c / e.n > worst[2]) worst = [name, kd, c / e.n];
    out[`25h: jenis terbanyak per distrik <= 30% (tertinggi ${worst[1]} ${(100 * worst[2]).toFixed(1)}% di ${worst[0]}; dipindah ${T.capMoved})`] = worst[2] <= 0.3 + 1e-9; }
  // 25e: konifer tidak di jalan kota (za < 2600, di luar hutan); jumlah dan tinggi termasuk hutan 14a
  for (const k of ['fir', 'hemlock', 'arborvitae', 'redcedar']) {
    const all = T.list.filter((t) => T.templates[t.tpl].kind === k), hs = all.map((t) => T.templates[t.tpl].height * t.sc).sort((a, b) => a - b);
    const kota = all.filter((t) => !t.forest && t.za < 2600).length, hutan = all.filter((t) => t.forest).length;
    out[`INFO ${k}: ${all.length} pohon (hutan ${hutan}), tinggi ${[0.1, 0.5, 0.9].map((q) => hs.length ? pc(hs, q).toFixed(1) : '-').join(' / ')} m`] = true;
    out[`${k}: ada, tidak di jalan kota (${kota}), median tinggi 4-35 m`] = all.length > 20 && kota === 0 && pc(hs, 0.5) > 4 && pc(hs, 0.5) < 35;
  }
  const pct = (m) => 100 * T.list.filter((t) => st.leafColorFor(t, m)).length / T.list.length;
  const [h, c, g] = [0, 1, 2].map(pct);
  out[`Hijau: hanya pohon bunga (${h.toFixed(1)}%)`] = h < 6;
  out[`Campur: 15-25% berwarna (${c.toFixed(1)}%)`] = c >= 15 && c <= 25;
  out[`Gugur: lebih dari separuh (${g.toFixed(1)}%)`] = g > 50;
  const H = st.PRESETS.findIndex((p) => p.name === 'Hemat'), fu = st.LEAF.fallUser;
  st.LEAF.fallUser = null; st.applyPreset(H); out['Hemat: daun jatuh mati'] = st.FALL.n === 0;
  st.LEAF.fallUser = true; st.applyPreset(H); out['Hemat + nyala manual: daun jatuh ada'] = st.FALL.n > 0;
  st.LEAF.fallUser = fu; st.applyPreset(0); out['Ultra: 3000 daun jatuh'] = st.FALL.n === 3000 || fu === false;
  return out;
})()
"""

# 25j: template, nilai tidak valid, warna musim per jenis
CEK = r"""
(() => {
  const st = window.__station, T = st.TREES, out = {}, SP = st.TREE_SPECIES;
  out[`42 template (${T.templates.length})`] = T.templates.length === 42;
  const fin = (a) => { for (let i = 0; i < a.length; i++) if (!Number.isFinite(a[i])) return false; return true; };
  const bad = [], kosong = [], nol = [], aoOut = [];
  T.templates.forEach((M, i) => {
    const nl = M.leafGeo.index ? M.leafGeo.index.count / 3 : 0, nb = M.barkGeo.index ? M.barkGeo.index.count / 3 : 0;
    if (nl < 50 || nb < 20 || !(M.height > 2) || !(M.halfW > 0.5) || !(M.crownR > 0.3)) kosong.push(`${i} ${M.kind} (${nl}/${nb} segitiga)`);
    for (const [nm, g] of [['leaf', M.leafGeo], ['bark', M.barkGeo]]) {
      for (const [k, a] of Object.entries(g.attributes)) if (!fin(a.array)) bad.push(`${i} ${M.kind} ${nm}.${k}`);
      if (g.index) { const n = g.attributes.position.count; for (const v of g.index.array) if (v >= n) { bad.push(`${i} ${M.kind} ${nm}.index`); break; } }
    }
    const cn = M.leafGeo.attributes.aCn.array, ao = M.leafGeo.attributes.aAo.array, bn = M.barkGeo.attributes.normal.array;
    for (let k = 0; k < cn.length; k += 3) if (Math.hypot(cn[k], cn[k + 1], cn[k + 2]) < 1e-3) { nol.push(`${i} ${M.kind} aCn`); break; }
    for (let k = 0; k < bn.length; k += 3) if (Math.hypot(bn[k], bn[k + 1], bn[k + 2]) < 1e-3) { nol.push(`${i} ${M.kind} normal kulit`); break; }
    for (const v of ao) if (v < 0 || v > 1) { aoOut.push(`${i} ${M.kind}`); break; }
    for (const [nm, m] of [['bark', M.bark], ['leaf', M.leaf], ['imp', M.imp], ['oct', M.oct]]) {
      if (!m) continue;
      if (!fin(m.instanceMatrix.array)) bad.push(`${i} ${M.kind} ${nm}.instanceMatrix`);
      for (const [k, a] of Object.entries(m.geometry.attributes)) if (a.isInstancedBufferAttribute && !fin(a.array)) bad.push(`${i} ${M.kind} ${nm}.${k}`);
    }
  });
  out['tanpa template kosong' + (kosong.length ? ': ' + kosong.join(', ') : '')] = kosong.length === 0;
  out['geometri, instance, aLeafC tanpa NaN / Infinity, indeks dalam rentang' + (bad.length ? ': ' + bad.slice(0, 6).join(', ') : '')] = bad.length === 0;
  out['normal daun aCn dan normal kulit tidak nol' + (nol.length ? ': ' + nol.slice(0, 6).join(', ') : '')] = nol.length === 0;
  out['aAo di 0..1' + (aoOut.length ? ': ' + aoOut.join(', ') : '')] = aoOut.length === 0;
  const badT = T.list.filter((t) => !(Number.isFinite(t.s) && Number.isFinite(t.za) && t.sc > 0 && Number.isFinite(t.sc) && t.tpl >= 0 && t.tpl < T.templates.length));
  out[`${T.list.length} pohon: posisi, skala, template sah (${badT.length} salah)`] = badT.length === 0 && T.list.length > 20000;
  // warna musim: bagian berwarna per jenis mendekati fall.campur / fall.gugur, konifer dan pinus selalu hijau, bunga selalu berwarna
  const per = {}; for (const t of T.list) { const k = T.templates[t.tpl].kind; (per[k] = per[k] || []).push(t); }
  const frac = (k, m) => per[k].filter((t) => st.leafColorFor(t, m)).length / per[k].length;
  const okC = (c) => c === null || (c.length === 4 && c.every(Number.isFinite) && c[3] > 0 && c[3] <= 1 && c.slice(0, 3).every((v) => v >= 0));
  let cBad = 0; for (const t of T.list) for (const m of [0, 1, 2]) if (!okC(st.leafColorFor(t, m))) cBad++;
  out[`warna musim tanpa nilai tidak valid, kekuatan 0..1 (${cBad} salah)`] = cBad === 0;
  const hijau = ['pine', 'fir', 'hemlock', 'arborvitae', 'redcedar'], nC = hijau.map((k) => frac(k, 1) + frac(k, 2)).reduce((a, b) => a + b, 0);
  out['konifer dan pinus hijau di Campur dan Gugur'] = nC === 0;
  out['pohon bunga berwarna di ketiga mode'] = [0, 1, 2].every((m) => frac('bunga', m) === 1);
  for (const [k, S] of Object.entries(SP)) {
    if (!S.fall || !per[k]) continue;
    const n = per[k].length, tol = 0.04 + 2.5 * Math.sqrt(0.25 / n), c = frac(k, 1), g = frac(k, 2);
    out[`${k}: Campur ${(100 * c).toFixed(1)}% (fall ${100 * S.fall.campur}%), Gugur ${(100 * g).toFixed(1)}% (fall ${100 * S.fall.gugur}%), ${n} pohon`] =
      Math.abs(c - S.fall.campur) <= tol && Math.abs(g - S.fall.gugur) <= tol && frac(k, 0) === 0;
  }
  return out;
})()
"""

# sidik jari FNV-1a 16 template (sama dengan alat banding 25a): atribut, indeks, ukuran per template
SIDIK = r"""
(() => {
  const st = window.__station, out = [];
  const fnv = (arr) => { const u = new Uint8Array(arr.buffer, arr.byteOffset, arr.byteLength); let h = 0x811c9dc5;
    for (let i = 0; i < u.length; i++) { h ^= u[i]; h = Math.imul(h, 0x01000193) >>> 0; } return h.toString(16).padStart(8, '0') + ':' + arr.length; };
  const geoHash = (g) => { const o = {}; for (const k of Object.keys(g.attributes).sort()) o[k] = fnv(g.attributes[k].array); o.index = g.index ? fnv(g.index.array) : null; return o; };
  st.TREES.templates.forEach((T, i) => out.push({ i, kind: T.kind, height: +T.height.toFixed(9), halfW: +T.halfW.toFixed(9), crownR: +T.crownR.toFixed(9),
    trunkR: T.trunkR, bark: geoHash(T.barkGeo), leaf: geoHash(T.leafGeo) }));
  return out;
})()
"""

def cetak(hasil):
    for k, v in hasil.items(): print('     ' + k[5:] if k.startswith('INFO ') else ('OK   ' if v else 'GAGAL') + ' ' + k)

async def buka(b, url, errs):
    pg = await b.new_page(viewport={'width': 320, 'height': 200})
    pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
    pg.on('console', lambda m: errs.append(m.type + ': ' + m.text[:200]) if m.type == 'error' else None)
    await pg.goto(url)
    await pg.wait_for_function('window.__stationReady === true', timeout=240000)
    return pg

async def main():
    here = pathlib.Path(__file__).resolve().parent
    page_url = here.parent.joinpath('experiences/cooper-station/index.html').as_uri()
    kw = {'executable_path': os.environ['CHROMIUM']} if os.environ.get('CHROMIUM') else {}
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'], **kw)
        errs = []
        pg = await buka(b, page_url, errs)
        await pg.wait_for_timeout(3000)
        cetak(await pg.evaluate(CEK))
        cetak(await pg.evaluate(UJI))
        await pg.close()
        # ?pohon=lama: 16 template identik dengan sebelum 25a
        pg = await buka(b, page_url + '?pohon=lama', errs)
        rows, base = await pg.evaluate(SIDIK), json.loads(here.joinpath('uji_pohon_lama.json').read_text(encoding='utf-8'))
        beda = [f"{r['i']} {r['kind']}" for r, q in zip(rows, base) if r != q]
        cetak({f"?pohon=lama: {len(rows)} template identik bit per bit dengan sebelum 25a (beda: {', '.join(beda) or 'tidak ada'})": len(rows) == len(base) == 16 and not beda})
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())
