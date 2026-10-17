// Uji generator bentuk orang (rencana tahap 28b, shared/orang.js), tanpa browser: node tools/uji_orang_bentuk.cjs
const K = require('../shared/orang.js');
const out = []; const cek = (nama, ok, info) => { out.push(ok); console.log((ok ? 'LOLOS ' : 'GAGAL ') + nama + (info ? ' | ' + info : '')); };
const BUDGET = [2500, 750, 250];
const NB = K.old.parts().length;
// model lama (17 kotak) sebagai acuan indeks kotak
const parts = K.old.parts(), pos = [], idx = [];
for (const [sx, sy, sz, x, y, z] of parts) { const b = pos.length / 3; for (const X of [-1, 1]) for (const Y of [-1, 1]) for (const Z of [-1, 1]) pos.push(x + X * sx / 2, y + Y * sy / 2, z + Z * sz / 2);
  for (const q of [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]) idx.push(b + q[0], b + q[1], b + q[2], b + q[0], b + q[2], b + q[3]); }
const lama = K.edgeStats(Float32Array.from(pos), Uint16Array.from(idx), 50);
cek('model lama: ' + NB + ' kotak', NB === 17, 'indeks kotak ' + lama.persen.toFixed(1) + '% tepi keras');
const G = [0, 1, 2].map((l) => K.shape(l));
const poses = [['jalan', 0], ['jalan', 0.8], ['jalan', 1.6], ['jalan', 2.4], ['jalan', 3.14], ['jalan', 4.7], ['duduk', 0], ['berdiri', 1.3]];
G.forEach((g, l) => {
  const st = K.edgeStats(g.position, g.index, 50, g.capMask);
  let bad = 0, nz = 0, wbad = 0, ibad = 0, aobad = 0, idbad = 0;
  for (const a of [g.position, g.normal, g.ao, g.sk]) for (const v of a) if (!isFinite(v)) bad++;
  for (let i = 0; i < g.titik; i++) { const L = Math.hypot(g.normal[3 * i], g.normal[3 * i + 1], g.normal[3 * i + 2]); if (Math.abs(L - 1) > 1e-3) nz++;
    const a = g.sk[3 * i], b = g.sk[3 * i + 1], w = g.sk[3 * i + 2]; if (!(w >= 0 && w <= 1)) wbad++; if (!(a >= 0 && a <= 10 && b >= 0 && b <= 10 && Number.isInteger(a) && Number.isInteger(b))) ibad++;
    if (!(g.ao[i] >= 0.449 && g.ao[i] <= 1.0001)) aobad++; if (!(g.part[i] >= 0 && g.part[i] <= 8)) idbad++; }
  let idxbad = 0; for (const v of g.index) if (v >= g.titik) idxbad++;
  cek('L' + l + ' segitiga <= ' + BUDGET[l], g.tris <= BUDGET[l] && g.tris > 0, g.tris + ' segitiga, ' + g.titik + ' titik (lama 204 / 408)');
  cek('L' + l + ' nilai valid, normal satuan, bobot 0..1, tulang 0..10, AO 0,45..1, id 0..8, indeks sah', bad === 0 && nz === 0 && wbad === 0 && ibad === 0 && aobad === 0 && idbad === 0 && idxbad === 0, `tidak valid ${bad}, normal ${nz}, bobot ${wbad}, tulang ${ibad}, ao ${aobad}, id ${idbad}, indeks ${idxbad}`);
  const lim = [8, 30, 45][l]; cek('L' + l + ' indeks kotak <= ' + lim + '% (lama ' + lama.persen.toFixed(1) + '%)', st.persen <= lim, st.persen.toFixed(2) + '% (' + st.keras + ' dari ' + st.bersama + ' tepi), tepi terbuka ' + st.terbuka + ' (sambungan tersembunyi)');
  let ymin = 9, ymax = -9, xw = 0, zmin = 9, zmax = -9;
  for (let i = 0; i < g.titik; i++) { const x = g.position[3 * i], y = g.position[3 * i + 1], z = g.position[3 * i + 2]; ymin = Math.min(ymin, y); ymax = Math.max(ymax, y); zmin = Math.min(zmin, z); zmax = Math.max(zmax, z); if (g.part[i] !== 6 && z > -0.14) xw = Math.max(xw, Math.abs(x)); }
  cek('L' + l + ' ukuran: tinggi 1,70-1,80 m, telapak di y = 0, lebar tanpa tas <= 1,15 x lama (0,30 m)', ymax >= 1.70 && ymax <= 1.80 && ymin > -0.01 && ymin < 0.012 && xw <= 0.30 * 1.15, `y ${ymin.toFixed(3)}..${ymax.toFixed(3)}, setengah lebar ${xw.toFixed(3)}, z ${zmin.toFixed(3)}..${zmax.toFixed(3)}`);
  // pose: nilai valid, sambungan rapat, panjang tepi
  let pbad = 0, seam = 0, worst = 1, worstW = 1, nseam = 0, wp = '', wr = 0;
  const P = new Float32Array(g.position.length), N = new Float32Array(g.position.length);
  const map = new Map(); for (let i = 0; i < g.titik; i++) { const k = [0, 1, 2].map((c) => Math.round(g.position[3 * i + c] * 1e4)).join(','); if (!map.has(k)) map.set(k, []); map.get(k).push(i); }
  for (const [nm, ph] of poses) {
    K.pose(g, K.poseOf(nm, ph), P, N);
    for (const v of P) if (!isFinite(v)) pbad++; for (const v of N) if (!isFinite(v)) pbad++;
    for (const arr of map.values()) if (arr.length > 1) for (let j = 1; j < arr.length; j++) { const a = arr[0], b = arr[j]; const d = Math.hypot(P[3 * a] - P[3 * b], P[3 * a + 1] - P[3 * b + 1], P[3 * a + 2] - P[3 * b + 2]); nseam++; if (d > 1e-4) seam++; }
    for (let t = 0; t < g.index.length; t += 3) for (let e = 0; e < 3; e++) { const a = g.index[t + e], b = g.index[t + (e + 1) % 3];
      const r0 = Math.hypot(g.position[3 * a] - g.position[3 * b], g.position[3 * a + 1] - g.position[3 * b + 1], g.position[3 * a + 2] - g.position[3 * b + 2]);
      const r1 = Math.hypot(P[3 * a] - P[3 * b], P[3 * a + 1] - P[3 * b + 1], P[3 * a + 2] - P[3 * b + 2]); if (r0 > 0.01 && r1 / r0 > worst) { worst = r1 / r0; wp = nm + ' ' + ph; } if (nm !== 'duduk' && r0 > 0.01) worstW = Math.max(worstW, r1 / r0); }
  }
  cek('L' + l + ' pose (8 keadaan) tanpa nilai tidak valid, sambungan berimpit tetap rapat', pbad === 0 && seam === 0, `tidak valid ${pbad}, sambungan retak ${seam} dari ${nseam}`);
  cek('L' + l + ' kulit tidak robek: tepi terpanjang <= 1,3x pose ikat saat jalan / berdiri, <= 1,7x saat duduk (lutut 86 derajat, batas kulit dua tulang)', worstW <= 1.3 && worst <= 1.7, 'jalan/berdiri ' + worstW.toFixed(3) + 'x, terburuk ' + worst.toFixed(3) + 'x (' + wp + ')');
});
console.log('\n' + (out.every(Boolean) ? 'HASIL: LOLOS' : 'HASIL: GAGAL'), out.filter(Boolean).length + '/' + out.length);
process.exit(out.every(Boolean) ? 0 : 1);
