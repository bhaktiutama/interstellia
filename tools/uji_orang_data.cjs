// Uji data orang olahan (rencana tahap 28G1): node tools/uji_orang_data.cjs   (tanpa browser)
// Membaca experiences/cooper-station/assets/orang.data.js, mendekode lewat shared/orang_data.js, dan memeriksa data dan kulit CPU.
const fs = require('fs'), path = require('path'), vm = require('vm');
const ROOT = path.resolve(__dirname, '..');
const win = {}; vm.runInNewContext(fs.readFileSync(path.join(ROOT, 'experiences/cooper-station/assets/orang.data.js'), 'utf8'), { window: win });
const K = require(path.join(ROOT, 'shared/orang_data.js')), D = K.decode(win.ORANG_DATA);
const out = []; const cek = (nama, ok, info) => { out.push(ok); console.log((ok ? 'LOLOS ' : 'GAGAL ') + nama + (info ? ' | ' + info : '')); };
const BUD = [3000, 750, 180], MAXB = 4.5e6;
const size = fs.statSync(path.join(ROOT, 'experiences/cooper-station/assets/orang.data.js')).size;
cek('ukuran berkas orang.data.js <= 4,5 MB', size <= MAXB, (size / 1e6).toFixed(2) + ' MB, biner ' + (win.ORANG_DATA.meta.blobBytes / 1e6).toFixed(2) + ' MB');
cek('jumlah karakter 13 (7 pria, 6 wanita)', D.chars.length === 13 && D.chars.filter((c) => c.g === 'm').length === 7, D.chars.map((c) => c.id).join(' '));
const lodNames = ['L0', 'L1', 'L2'];
for (const c of D.chars) {
  const A = D.anim[c.g], nb = A.nb; let bad = 0, wbad = 0, jbad = 0, ibad = 0, nzero = 0, tr = [];
  c.lods.forEach((L, li) => {
    tr.push(L.nt);
    for (const a of [L.pos, L.nrm, L.weights, L.col]) for (const v of a) if (!Number.isFinite(v)) bad++;
    for (let i = 0; i < L.nv; i++) {
      let s = 0; for (let k = 0; k < 4; k++) { s += L.weights[i * 4 + k]; if (L.weights[i * 4 + k] > 0 && L.joints[i * 4 + k] >= nb) jbad++; }
      if (Math.abs(s - 1) > 0.012) wbad++;
      if (Math.abs(Math.hypot(L.nrm[i * 3], L.nrm[i * 3 + 1], L.nrm[i * 3 + 2]) - 1) > 0.03) nzero++;
    }
    for (const v of L.index) if (v >= L.nv) ibad++;
  });
  cek(c.id + ': segitiga ' + tr.join('/') + ' <= ' + BUD.join('/') + ', nilai valid, bobot 1, tulang < ' + nb + ', normal satuan, indeks sah', tr.every((t, i) => t <= BUD[i]) && bad === 0 && wbad === 0 && jbad === 0 && nzero === 0 && ibad === 0, `tidak valid ${bad}, bobot ${wbad}, tulang ${jbad}, normal ${nzero}, indeks ${ibad}`);
  const L0 = c.lods[0]; let ymin = 9, ymax = -9; for (let i = 0; i < L0.nv; i++) { ymin = Math.min(ymin, L0.pos[i * 3 + 1]); ymax = Math.max(ymax, L0.pos[i * 3 + 1]); }
  cek(c.id + ': tinggi bind 1,55-2,0 m, telapak di y = 0', ymax - ymin >= 1.55 && ymax - ymin <= 2.0 && Math.abs(ymin) < 0.05, `y ${ymin.toFixed(3)}..${ymax.toFixed(3)}`);
}
// animasi: kuaternion satuan, frame berhingga, loop mulus, tinggi duduk, langkah
for (const g of ['m', 'w']) {
  const A = D.anim[g]; let qb = 0, tb = 0;
  for (let f = 0; f < A.frames; f++) for (let j = 0; j < A.nb; j++) { const o = (f * A.nb + j) * 7, l = Math.hypot(A.q[o], A.q[o + 1], A.q[o + 2], A.q[o + 3]); if (Math.abs(l - 1) > 0.002) qb++; for (let k = 4; k < 7; k++) if (!Number.isFinite(A.q[o + k]) || Math.abs(A.q[o + k]) > 3.9) tb++; }
  cek('anim ' + g + ': ' + A.frames + ' frame x ' + A.nb + ' tulang, kuaternion satuan, translasi dalam jangkauan', qb === 0 && tb === 0, `kuaternion salah ${qb}, translasi salah ${tb}`);
  // loop mulus: jarak titik kulit frame terakhir ke frame pertama tidak lebih dari 1,5x langkah terbesar antar frame berurutan (karakter pertama jenis ini, L1)
  const c0 = D.chars.find((c) => c.g === g), L = c0.lods[1], w = A.byName.Jalan, fr = [];
  for (let f = 0; f < w.frames; f++) { const p = new Float32Array(L.nv * 3), n = new Float32Array(L.nv * 3); K.skin(L, A, w.start + f, w.start + f, 0, p, n); fr.push(p); }
  const dist = (a, b) => { let m = 0; for (let i = 0; i < a.length; i += 3) m = Math.max(m, Math.hypot(a[i] - b[i], a[i + 1] - b[i + 1], a[i + 2] - b[i + 2])); return m; };
  let stepMax = 0; for (let f = 0; f < w.frames - 1; f++) stepMax = Math.max(stepMax, dist(fr[f], fr[f + 1])); const closeD = dist(fr[w.frames - 1], fr[0]);
  cek('anim ' + g + ': Jalan mulus (loncatan penutup siklus <= 1,5x langkah antar frame)', closeD <= 1.5 * stepMax, 'penutup ' + (closeD * 100).toFixed(1) + ' cm, langkah terbesar ' + (stepMax * 100).toFixed(1) + ' cm');
  cek('anim ' + g + ': pinggul duduk turun 0,30-0,55 m (model lama 0,38)', A.sitDy < -0.30 && A.sitDy > -0.55, A.sitDy + ' m');
  cek('anim ' + g + ': langkah Jalan 1,0-1,6 m per siklus (game: 1,45)', A.strideM >= 1.0 && A.strideM <= 1.6, A.strideM + ' m per siklus, ' + A.walkSpeed + ' m/s');
  const hs = D.meta.anim[g].handStat.Jalan_Payung; cek('anim ' + g + ': tangan payung 0,9-1,3 m tinggi, 0,3-0,6 m depan, ayun <= 15 cm', hs.mean[1] > 0.9 && hs.mean[1] < 1.3 && hs.mean[2] > 0.3 && hs.mean[2] < 0.6 && Math.max(...hs.span) < 0.15, JSON.stringify(hs));
}
// kulit: semua karakter x 3 LOD x klip (pertengahan): nilai valid, tinggi wajar, LOD vs L0 dekat
let sk_bad = 0, hmax = 0, hmin = 9; const P0 = [], N0 = [];
for (const c of D.chars) {
  const A = D.anim[c.g]; const outs = c.lods.map((L) => [new Float32Array(L.nv * 3), new Float32Array(L.nv * 3)]);
  for (const cl of A.clips) {
    const f = cl.start + Math.floor(cl.frames / 2);
    c.lods.forEach((L, i) => { K.skin(L, A, f, f, 0, outs[i][0], outs[i][1]); for (const v of outs[i][0]) if (!Number.isFinite(v)) sk_bad++; for (const v of outs[i][1]) if (!Number.isFinite(v)) sk_bad++; });
    if (cl.name === 'Jalan' || cl.name === 'Duduk') { let y = -9; for (let i = 0; i < c.lods[0].nv; i++) y = Math.max(y, outs[0][0][i * 3 + 1]); if (cl.name === 'Jalan') { hmax = Math.max(hmax, y); hmin = Math.min(hmin, y); } }
  }
}
cek('kulit: 13 karakter x 3 LOD x 8 klip tanpa nilai tidak valid', sk_bad === 0, 'tidak valid ' + sk_bad);
cek('kulit: tinggi kepala saat Jalan 1,6-2,05 m', hmin > 1.6 && hmax < 2.05, hmin.toFixed(3) + '..' + hmax.toFixed(3) + ' m');
// L1 dan L2 dekat L0: jarak rata-rata titik L0 ke titik terdekat L1 / L2 (pose Jalan tengah)
for (const c of D.chars) {
  const A = D.anim[c.g], cl = A.byName.Jalan, f = cl.start + 7; const P = c.lods.map((L) => { const p = new Float32Array(L.nv * 3), n = new Float32Array(L.nv * 3); K.skin(L, A, f, f, 0, p, n); return p; });
  const near = (a, b, step) => { let s = 0, mx = 0, n = 0; for (let i = 0; i < a.length / 3; i += step) { let best = 1e9; for (let j = 0; j < b.length / 3; j++) { const d = (a[i * 3] - b[j * 3]) ** 2 + (a[i * 3 + 1] - b[j * 3 + 1]) ** 2 + (a[i * 3 + 2] - b[j * 3 + 2]) ** 2; if (d < best) best = d; } best = Math.sqrt(best); s += best; mx = Math.max(mx, best); n++; } return { avg: s / n, max: mx }; };
  const e1 = near(P[0], P[1], 11), e2 = near(P[0], P[2], 11);
  cek(c.id + ': bentuk L1 dan L2 mengikuti L0 (rata-rata titik L0 ke titik L1 <= 3 cm, L2 <= 6 cm)', e1.avg <= 0.03 && e2.avg <= 0.06, `L1 ${(e1.avg * 100).toFixed(1)} / maks ${(e1.max * 100).toFixed(1)} cm, L2 ${(e2.avg * 100).toFixed(1)} / maks ${(e2.max * 100).toFixed(1)} cm`);
}
console.log('\n' + (out.every(Boolean) ? 'HASIL: LOLOS' : 'HASIL: GAGAL'), out.filter(Boolean).length + '/' + out.length);
process.exit(out.every(Boolean) ? 0 : 1);
