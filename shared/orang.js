/* Rencana tahap 28 (docs/cooper-station/rencana-tahap-28-cooper-station.md): generator bentuk orang tanpa kotak.
   window.PEDKIT (skrip biasa, jalan dari file://, tanpa three.js; di Node lewat module.exports).
   shape(level) -> { position, normal, part, sk, ao, index, tris, titik }  level 0 dekat, 1 menengah, 2 jauh
     part  id warna (ID), sk = (tulang A, tulang B, bobot A) per titik, ao 0..1 dipanggang saat bangun.
   pose(g, A, outP, outN)  kulit dua tulang di CPU: kembaran vertex shader pejalan kaki (ubah bersama di tahap 28c).
   poseOf(nama, fase)      sudut sendi untuk jalan / berdiri / duduk (kembaran VS lama + sendi baru).
   edgeStats(position, index, derajat)  indeks kotak: persen tepi bersama yang sudut antar-normalnya melebihi derajat.
   old                     model kotak lama (17 kotak) dan pose kakunya, untuk banding.
   Kerangka lama tetap: pinggul y 0,90, lutut 0,48, bahu (+-0,25; 1,44); tinggi sekitar 1,78 m; +z = depan, +y = atas. */
(function () {
  'use strict';
  const TAU = Math.PI * 2;
  const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  const sm = (a, b, x) => { const u = clamp((x - a) / (b - a), 0, 1); return u * u * (3 - 2 * u); };   // a > b boleh (naik saat x turun)

  // id warna per titik (dipilih shader dari palet): 0 kemeja, 1 kulit, 2 rambut, 3 celana, 4 sepatu, 5 sol, 6 tas, 7 lengan bawah (lengan baju atau kulit), 8 rambut panjang (opsional)
  const ID = { SHIRT: 0, SKIN: 1, HAIR: 2, PANTS: 3, SHOE: 4, SOLE: 5, BAG: 6, FORE: 7, HAIRL: 8 };
  // tulang: 0 panggul (akar), 1 badan atas, 2 kepala, lalu per sisi i (0 = x negatif, 1 = x positif): paha 3 + 2i, betis 4 + 2i, lengan atas 7 + 2i, lengan bawah 8 + 2i
  const BONE = { PELVIS: 0, CHEST: 1, HEAD: 2 };
  const thigh = (i) => 3 + 2 * i, shin = (i) => 4 + 2 * i, uarm = (i) => 7 + 2 * i, farm = (i) => 8 + 2 * i;
  const RIG = { hipY: 0.90, hipX: 0.10, kneeY: 0.48, shY: 1.44, shX: 0.248, elY: 1.15, neckY: 1.50 };

  // ---------- loft ----------
  // sec: [{ p:[x,y,z], ru, rv, id }]; ref = arah sumbu u (diproyeksikan tegak lurus sumbu), n = eksponen penampang (2 elips, > 2 mendekati persegi membulat)
  function loft(B, sec, S, o) {
    o = o || {}; const ref = o.ref || [1, 0, 0], ne = o.n || 2, base = B.pos.length / 3, N = sec.length, ctr = [];
    const sg = (x) => (x < 0 ? -1 : 1), pw = (c) => (ne === 2 ? c : sg(c) * Math.pow(Math.abs(c), 2 / ne));
    for (let i = 0; i < N; i++) {
      const a = sec[Math.max(0, i - 1)].p, b = sec[Math.min(N - 1, i + 1)].p;
      let t = [b[0] - a[0], b[1] - a[1], b[2] - a[2]]; const tl = Math.hypot(t[0], t[1], t[2]) || 1; t = t.map((v) => v / tl);
      const d = ref[0] * t[0] + ref[1] * t[1] + ref[2] * t[2]; let u = [ref[0] - d * t[0], ref[1] - d * t[1], ref[2] - d * t[2]];
      const ul = Math.hypot(u[0], u[1], u[2]) || 1; u = u.map((v) => v / ul);
      const v = [t[1] * u[2] - t[2] * u[1], t[2] * u[0] - t[0] * u[2], t[0] * u[1] - t[1] * u[0]];
      const s = sec[i]; ctr.push(s.p);
      for (let k = 0; k < S; k++) {
        const an = (k + 0.5) / S * TAU, c = pw(Math.cos(an)) * s.ru, e = pw(Math.sin(an)) * s.rv;
        B.pos.push(s.p[0] + u[0] * c + v[0] * e, s.p[1] + u[1] * c + v[1] * e, s.p[2] + u[2] * c + v[2] * e); B.id.push(s.id); B.tag.push(o.tag);
      }
    }
    const tri = (a, b, c, ref3) => {   // urutan segitiga mengikuti arah luar ref3
      const P = B.pos, ax = P[3 * b] - P[3 * a], ay = P[3 * b + 1] - P[3 * a + 1], az = P[3 * b + 2] - P[3 * a + 2], bx = P[3 * c] - P[3 * a], by = P[3 * c + 1] - P[3 * a + 1], bz = P[3 * c + 2] - P[3 * a + 2];
      const nx = ay * bz - az * by, ny = az * bx - ax * bz, nz = ax * by - ay * bx;
      if (nx * ref3[0] + ny * ref3[1] + nz * ref3[2] < 0) B.idx.push(a, c, b); else B.idx.push(a, b, c);
    };
    const P = B.pos;
    for (let i = 0; i < N - 1; i++) for (let k = 0; k < S; k++) {
      const a = base + i * S + k, b = base + i * S + (k + 1) % S, c = base + (i + 1) * S + k, d = base + (i + 1) * S + (k + 1) % S;
      const m = [(P[3 * a] + P[3 * b] + P[3 * c] + P[3 * d]) / 4 - ctr[i][0], (P[3 * a + 1] + P[3 * b + 1] + P[3 * c + 1] + P[3 * d + 1]) / 4 - ctr[i][1], (P[3 * a + 2] + P[3 * b + 2] + P[3 * c + 2] + P[3 * d + 2]) / 4 - ctr[i][2]];
      tri(a, b, c, m); tri(b, d, c, m);
    }
    const cap = (i, dir) => {
      const c0 = B.pos.length / 3, p = sec[i].p; B.pos.push(p[0], p[1], p[2]); B.id.push(sec[i].id); B.tag.push(o.tag);
      const j = i === 0 ? 1 : N - 2, q = sec[j].p, out = [dir * (sec[i].p[0] - q[0]), dir * (sec[i].p[1] - q[1]), dir * (sec[i].p[2] - q[2])];
      for (let k = 0; k < S; k++) { B.capT.push(B.idx.length / 3); tri(c0, base + i * S + k, base + i * S + (k + 1) % S, [out[0] * dir, out[1] * dir, out[2] * dir]); }
    };
    if (o.cap0 !== false) cap(0, 1); if (o.cap1 !== false) cap(N - 1, 1);
  }

  // baris [y, cz, rx, rz, id] di sumbu tegak pada x = cx
  const vsec = (cx, rows) => rows.map((r) => ({ p: [cx, r[0], r[1]], ru: r[2], rv: r[3], id: r[4] }));
  // baris [z, yc, ru(x), rv(y), id] di sumbu depan pada x = cx
  const zsec = (cx, rows) => rows.map((r) => ({ p: [cx, r[1], r[0]], ru: r[2], rv: r[3], id: r[4] }));
  const pick = (rows, ix) => (ix ? ix.map((k) => rows[k]) : rows);

  // ---------- data penampang (m). Baris: [y, cz, rx, rz, id] ----------
  const TORSO = [
    [0.835, 0.000, 0.110, 0.090, 3], [0.870, 0.000, 0.160, 0.113, 3], [0.920, 0.000, 0.178, 0.121, 3], [0.972, 0.000, 0.171, 0.118, 3],
    [0.992, 0.000, 0.176, 0.121, 0], [1.060, 0.004, 0.156, 0.108, 0], [1.140, 0.010, 0.160, 0.108, 0], [1.220, 0.018, 0.176, 0.117, 0],
    [1.300, 0.022, 0.191, 0.121, 0], [1.380, 0.018, 0.212, 0.114, 0], [1.430, 0.008, 0.230, 0.101, 0], [1.470, 0.000, 0.165, 0.086, 0],
    [1.505, 0.000, 0.092, 0.078, 0], [1.526, 0.000, 0.080, 0.071, 0]];
  const HEAD = [   // leher + kepala (kulit)
    [1.455, 0.000, 0.058, 0.060, 1], [1.510, 0.000, 0.050, 0.054, 1], [1.540, 0.020, 0.052, 0.072, 1], [1.575, 0.014, 0.072, 0.090, 1],
    [1.620, 0.006, 0.080, 0.100, 1], [1.675, 0.000, 0.081, 0.101, 1], [1.725, -0.004, 0.072, 0.092, 1], [1.757, -0.006, 0.048, 0.064, 1], [1.772, -0.006, 0.020, 0.030, 1]];
  const HAIR = [   // cangkang rambut pendek (tepi bawah diangkat di dahi dan diturunkan di tengkuk oleh hairShape)
    [1.640, -0.004, 0.090, 0.108, 2], [1.690, -0.004, 0.091, 0.113, 2], [1.735, -0.006, 0.081, 0.104, 2], [1.765, -0.007, 0.057, 0.075, 2], [1.786, -0.007, 0.022, 0.034, 2]];
  const UARM = [[1.482, 0.004, 0.030, 0.030, 0], [1.458, 0.004, 0.054, 0.054, 0], [1.400, 0.004, 0.058, 0.058, 0], [1.320, 0.005, 0.052, 0.053, 0],
    [1.240, 0.006, 0.047, 0.048, 0], [1.180, 0.007, 0.042, 0.044, 0], [1.150, 0.008, 0.040, 0.042, 0]];
  const FARM = [[1.150, 0.008, 0.040, 0.042, 7], [1.105, 0.010, 0.046, 0.047, 7], [1.030, 0.012, 0.042, 0.041, 7], [0.950, 0.014, 0.034, 0.032, 7], [0.895, 0.016, 0.029, 0.027, 7]];
  const HAND = [[0.895, 0.016, 0.029, 0.027, 1], [0.868, 0.017, 0.036, 0.024, 1], [0.820, 0.019, 0.040, 0.023, 1], [0.780, 0.022, 0.038, 0.021, 1],
    [0.742, 0.027, 0.034, 0.018, 1], [0.708, 0.032, 0.027, 0.014, 1], [0.684, 0.036, 0.013, 0.009, 1]];
  const THIGH = [[0.935, 0.000, 0.060, 0.065, 3], [0.900, 0.000, 0.086, 0.090, 3], [0.820, 0.003, 0.087, 0.092, 3], [0.720, 0.006, 0.079, 0.084, 3],
    [0.610, 0.005, 0.068, 0.073, 3], [0.520, 0.003, 0.056, 0.062, 3], [0.480, 0.000, 0.052, 0.056, 3]];
  const SHIN = [[0.480, 0.000, 0.052, 0.056, 3], [0.430, -0.003, 0.054, 0.060, 3], [0.360, -0.010, 0.056, 0.066, 3], [0.280, -0.006, 0.048, 0.056, 3],
    [0.190, 0.000, 0.039, 0.044, 3], [0.120, 0.003, 0.034, 0.038, 3], [0.090, 0.003, 0.032, 0.036, 3]];
  const SHOE = [   // [z, yc, ru, rv, id] sepanjang telapak
    [-0.075, 0.062, 0.030, 0.050, 4], [-0.055, 0.062, 0.042, 0.056, 4], [0.010, 0.066, 0.046, 0.058, 4], [0.080, 0.050, 0.049, 0.044, 4],
    [0.140, 0.036, 0.050, 0.034, 4], [0.190, 0.028, 0.042, 0.027, 4], [0.212, 0.024, 0.026, 0.020, 4]];
  const SOLE = [[-0.072, 0.011, 0.030, 0.011, 5], [-0.050, 0.011, 0.044, 0.012, 5], [0.010, 0.011, 0.048, 0.012, 5], [0.080, 0.011, 0.051, 0.012, 5],
    [0.140, 0.011, 0.052, 0.012, 5], [0.190, 0.011, 0.044, 0.012, 5], [0.209, 0.011, 0.030, 0.011, 5]];

  // tingkat detail: sisi penampang S dan indeks baris yang dipakai (null = semua)
  const LV = [
    { torso: [12, null], head: [12, null], hair: [12, null], uarm: [8, null], farm: [8, null], hand: [8, null], thigh: [10, null], shin: [10, null], shoe: [8, null], sole: [8, [0, 2, 3, 5, 6]], bag: [8, 6], nose: 6, ear: 6, thumb: 5, hairl: 6, bagN: 3.2 },
    { torso: [8, [0, 2, 4, 6, 8, 11, 13]], head: [8, [0, 2, 4, 6, 8]], hair: [6, [0, 2, 4]], uarm: [6, [0, 1, 3, 6]], farm: [6, [0, 2, 4]], hand: [6, [0, 2, 6]], thigh: [6, [0, 1, 3, 6]], shin: [6, [0, 2, 4, 6]], shoe: [5, [0, 2, 4, 6]], sole: [0], bag: [6, 3], nose: 0, ear: 0, thumb: 0, hairl: 6, bagN: 3.2 }];

  // ---------- bobot tulang (A, B, bobot A) ----------
  const W = {
    torso: (x, y) => { const i = x < 0 ? 0 : 1; if (y >= 0.95) return [BONE.PELVIS, BONE.CHEST, 1 - sm(0.98, 1.14, y)]; return [BONE.PELVIS, thigh(i), 1 - 0.35 * sm(0.03, 0.15, Math.abs(x)) * sm(0.95, 0.835, y)]; },
    head: (x, y) => [BONE.CHEST, BONE.HEAD, 1 - sm(1.49, 1.55, y)],
    headOnly: () => [BONE.HEAD, BONE.HEAD, 1],
    hairL: (x, y) => [BONE.HEAD, BONE.CHEST, sm(1.35, 1.55, y)],
    arm: (i) => (x, y) => [uarm(i), farm(i), sm(1.09, 1.21, y)],
    hand: (i) => () => [farm(i), farm(i), 1],
    leg: (i) => (x, y) => [thigh(i), shin(i), sm(0.41, 0.55, y)],
    foot: (i) => () => [shin(i), shin(i), 1],
    bag: () => [BONE.PELVIS, BONE.PELVIS, 1]
  };

  // ---------- bangun ----------
  function build(level) {
    const L = LV[Math.min(level, 1)], B = { pos: [], id: [], tag: [], idx: [], capT: [] }, defs = [];
    const add = (tag, wfn, fn) => { const n0 = B.pos.length / 3; fn(); defs.push({ tag, wfn, a: n0, b: B.pos.length / 3 }); };
    // badan
    add('torso', W.torso, () => loft(B, vsec(0, pick(TORSO, L.torso[1])), L.torso[0], { n: 2.3, tag: 'torso' }));
    add('head', W.head, () => {
      const rows = pick(HEAD, L.head[1]);
      loft(B, vsec(0, rows), L.head[0], { tag: 'head' });
    });
    // rambut: tepi bawah naik di dahi, turun di tengkuk
    add('hair', W.headOnly, () => {
      const n0 = B.pos.length / 3, S = L.hair[0]; loft(B, vsec(0, pick(HAIR, L.hair[1])), S, { tag: 'hair', cap0: false });
      const rows = pick(HAIR, L.hair[1]).length;
      for (let k = 0; k < S; k++) { const an = (k + 0.5) / S * TAU, fz = -Math.sin(an), j = n0 + k;   // sumbu naik: v = -z, jadi sin < 0 = depan
        const f = fz > 0 ? 0.075 * sm(0.15, 0.9, fz) : -0.05 * sm(0.15, 0.9, -fz);
        B.pos[3 * j + 1] += f; if (rows > 1) B.pos[3 * (j + S) + 1] += f * 0.35; }
    });
    if (level === 0) {
      add('hairl', W.hairL, () => loft(B, [{ p: [0, 1.66, -0.075], ru: 0.055, rv: 0.032, id: 8 }, { p: [0, 1.58, -0.108], ru: 0.050, rv: 0.036, id: 8 }, { p: [0, 1.46, -0.122], ru: 0.044, rv: 0.032, id: 8 }, { p: [0, 1.33, -0.118], ru: 0.030, rv: 0.024, id: 8 }, { p: [0, 1.27, -0.112], ru: 0.012, rv: 0.010, id: 8 }], L.hairl, { tag: 'hairl' }));
      add('nose', W.headOnly, () => loft(B, [{ p: [0, 1.625, 0.098], ru: 0.012, rv: 0.022, id: 1 }, { p: [0, 1.613, 0.117], ru: 0.013, rv: 0.016, id: 1 }, { p: [0, 1.609, 0.128], ru: 0.007, rv: 0.009, id: 1 }], L.nose, { tag: 'nose', ref: [1, 0, 0] }));
      for (const s of [-1, 1]) add('ear', W.headOnly, () => loft(B, [{ p: [s * 0.078, 1.627, -0.004], ru: 0.022, rv: 0.030, id: 1 }, { p: [s * 0.093, 1.627, -0.004], ru: 0.020, rv: 0.027, id: 1 }], L.ear, { tag: 'ear', ref: [0, 0, 1] }));
    }
    for (let i = 0; i < 2; i++) {
      const s = i ? 1 : -1, ax = s * RIG.shX;
      add('uarm', W.arm(i), () => loft(B, vsec(ax, pick(UARM, L.uarm[1])), L.uarm[0], { tag: 'uarm' }));
      add('farm', W.arm(i), () => loft(B, vsec(ax, pick(FARM, L.farm[1])), L.farm[0], { tag: 'farm', cap1: false }));
      add('hand', W.hand(i), () => loft(B, vsec(ax, pick(HAND, L.hand[1])), L.hand[0], { tag: 'hand', cap0: false }));
      if (level === 0) add('thumb', W.hand(i), () => loft(B, [{ p: [ax - s * 0.028, 0.862, 0.020], ru: 0.013, rv: 0.012, id: 1 }, { p: [ax - s * 0.030, 0.822, 0.038], ru: 0.012, rv: 0.011, id: 1 }, { p: [ax - s * 0.027, 0.788, 0.052], ru: 0.009, rv: 0.008, id: 1 }, { p: [ax - s * 0.024, 0.772, 0.057], ru: 0.004, rv: 0.004, id: 1 }], L.thumb, { tag: 'thumb', ref: [1, 0, 0] }));
      const lx = s * RIG.hipX;
      add('thigh', W.leg(i), () => loft(B, vsec(lx, pick(THIGH, L.thigh[1])), L.thigh[0], { tag: 'thigh' }));
      add('shin', W.leg(i), () => loft(B, vsec(lx, pick(SHIN, L.shin[1])), L.shin[0], { tag: 'shin', cap1: false }));
      add('shoe', W.foot(i), () => loft(B, zsec(lx, pick(SHOE, L.shoe[1])), L.shoe[0], { tag: 'shoe', ref: [1, 0, 0] }));
      if (L.sole[0]) add('sole', W.foot(i), () => loft(B, zsec(lx, pick(SOLE, L.sole[1])), L.sole[0], { tag: 'sole', ref: [1, 0, 0] }));
    }
    // tas samping (hanya dipakai orang yang membawa tas: shader membuang bila aJ.z < 0,5)
    add('bag', W.bag, () => {
      const [S, V] = L.bag, rows = []; for (let k = 0; k <= V; k++) { const ph = -Math.PI / 2 + Math.PI * k / V, c = Math.max(0.04, Math.pow(Math.max(0, Math.cos(ph)), 2 / L.bagN)), y = Math.sign(Math.sin(ph)) * Math.pow(Math.abs(Math.sin(ph)), 2 / L.bagN);
        rows.push({ p: [0.305, 1.02 + 0.15 * y, -0.06], ru: 0.045 * c, rv: 0.12 * c, id: 6 }); }
      loft(B, rows, S, { tag: 'bag', n: L.bagN, ref: [1, 0, 0] });
    });
    return finish(B, defs);
  }

  // jauh: bentuk kasar (sekitar 250 segitiga)
  function buildFar() {
    const B = { pos: [], id: [], tag: [], idx: [], capT: [] }, defs = [];
    const add = (tag, wfn, fn) => { const n0 = B.pos.length / 3; fn(); defs.push({ tag, wfn, a: n0, b: B.pos.length / 3 }); };
    add('torso', W.torso, () => loft(B, vsec(0, [[0.84, 0, 0.12, 0.09, 3], [0.995, 0, 0.175, 0.12, 0], [1.43, 0.01, 0.215, 0.10, 0], [1.50, 0, 0.09, 0.08, 0]]), 6, { n: 2.3, tag: 'torso' }));
    add('head', W.head, () => loft(B, vsec(0, [[1.50, 0, 0.05, 0.055, 1], [1.62, 0.006, 0.08, 0.10, 1], [1.72, -0.004, 0.07, 0.09, 2], [1.785, -0.006, 0.012, 0.016, 2]]), 5, { tag: 'head' }));
    for (let i = 0; i < 2; i++) {
      const s = i ? 1 : -1;
      add('uarm', W.arm(i), () => loft(B, vsec(s * RIG.shX, [[1.47, 0.004, 0.045, 0.045, 0], [1.17, 0.008, 0.041, 0.043, 0], [1.13, 0.008, 0.04, 0.042, 7], [0.90, 0.016, 0.032, 0.03, 7], [0.69, 0.034, 0.012, 0.008, 1]]), 4, { tag: 'uarm' }));
      add('leg', W.leg(i), () => loft(B, vsec(s * RIG.hipX, [[0.93, 0, 0.08, 0.085, 3], [0.36, -0.01, 0.056, 0.066, 3], [0.09, 0.003, 0.034, 0.038, 3]]), 4, { tag: 'leg', cap1: false }));
      add('foot', W.foot(i), () => loft(B, zsec(s * RIG.hipX, [[-0.07, 0.05, 0.034, 0.05, 4], [0.21, 0.025, 0.028, 0.022, 4]]), 4, { ref: [1, 0, 0], tag: 'foot' }));
    }
    return finish(B, defs);
  }

  function finish(B, defs) {
    const n = B.pos.length / 3, pos = Float32Array.from(B.pos), idx = n > 65535 ? Uint32Array.from(B.idx) : Uint16Array.from(B.idx);
    const nrm = normals(pos, idx), sk = new Float32Array(3 * n), ao = new Float32Array(n), part = new Float32Array(n);
    for (const d of defs) for (let v = d.a; v < d.b; v++) { const w = d.wfn(pos[3 * v], pos[3 * v + 1], pos[3 * v + 2]); sk[3 * v] = w[0]; sk[3 * v + 1] = w[1]; sk[3 * v + 2] = clamp(w[2], 0, 1); part[v] = B.id[v]; ao[v] = aoOf(d.tag, pos[3 * v], pos[3 * v + 1], pos[3 * v + 2], nrm[3 * v], nrm[3 * v + 1], nrm[3 * v + 2]); }
    const capMask = new Uint8Array(idx.length / 3); for (const t of B.capT) capMask[t] = 1;
    return { position: pos, normal: nrm, part, sk, ao, index: idx, capMask, tris: idx.length / 3, titik: n };
  }
  function normals(pos, idx) {
    const n = new Float32Array(pos.length);
    for (let t = 0; t < idx.length; t += 3) {
      const a = idx[t] * 3, b = idx[t + 1] * 3, c = idx[t + 2] * 3;
      const ux = pos[b] - pos[a], uy = pos[b + 1] - pos[a + 1], uz = pos[b + 2] - pos[a + 2], vx = pos[c] - pos[a], vy = pos[c + 1] - pos[a + 1], vz = pos[c + 2] - pos[a + 2];
      const x = uy * vz - uz * vy, y = uz * vx - ux * vz, z = ux * vy - uy * vx;   // bobot luas
      for (const k of [a, b, c]) { n[k] += x; n[k + 1] += y; n[k + 2] += z; }
    }
    for (let i = 0; i < n.length; i += 3) { const l = Math.hypot(n[i], n[i + 1], n[i + 2]); if (l > 1e-12) { n[i] /= l; n[i + 1] /= l; n[i + 2] /= l; } else { n[i] = 0; n[i + 1] = 1; n[i + 2] = 0; } }   // tidak pernah normal nol
    return n;
  }
  // oklusi ambien yang dipanggang (0,45..1): bawah anggota badan, pangkal paha, ketiak, bawah dagu, belakang lutut, dasar sepatu
  function aoOf(tag, x, y, z, nx, ny, nz) {
    let a = 1 - 0.18 * Math.max(0, -ny);
    const ax = Math.abs(x);
    if (tag === 'thigh' || tag === 'torso' || tag === 'leg') a -= 0.35 * sm(0.07, 0.015, ax) * sm(1.0, 0.75, y);
    if (tag === 'uarm' || tag === 'farm' || tag === 'torso') a -= 0.30 * sm(0.235, 0.205, ax) * sm(1.18, 1.32, y) * (tag === 'torso' ? 0.5 : 1);
    if (tag === 'head') a -= 0.32 * sm(1.565, 1.50, y);
    if (tag === 'torso') a -= 0.15 * sm(1.52, 1.47, y) * (nz > 0 ? 0 : 1);
    if (tag === 'shin' || tag === 'thigh') a -= 0.18 * sm(0.09, 0, Math.abs(y - 0.48)) * (nz < 0 ? 1 : 0);
    if (tag === 'shoe' || tag === 'foot') a -= 0.25 * sm(0.035, 0.0, y);
    if (tag === 'hair') a -= 0.18 * sm(1.70, 1.62, y);
    return clamp(a, 0.45, 1);
  }

  // ---------- pose (kulit dua tulang) ----------
  const rx = (P, cy, a) => { const s = Math.sin(a), c = Math.cos(a), y = P[1] - cy, z = P[2]; P[1] = cy + y * c - z * s; P[2] = y * s + z * c; };
  const ry = (P, a) => { const s = Math.sin(a), c = Math.cos(a), x = P[0], z = P[2]; P[0] = x * c + z * s; P[2] = -x * s + z * c; };
  // vec = true: vektor (tanpa pivot)
  function chain(b, P, A, vec) {
    const c = (y) => (vec ? 0 : y);
    switch (b) {
      case 0: break;
      case 1: ry(P, A.twist); break;
      case 2: rx(P, c(RIG.neckY), A.nod); ry(P, A.turn); ry(P, A.twist); break;
      default: {
        const j = b >= 7 ? b - 7 : b - 3, side = (j >> 1) & 1, kind = j & 1;
        if (b < 7) { if (kind === 1) rx(P, c(RIG.kneeY), A.knee[side]); rx(P, c(RIG.hipY), A.hip[side]); }
        else { if (kind === 1) rx(P, c(RIG.elY), -A.el[side]); rx(P, c(RIG.shY), A.sh[side]); ry(P, A.twist); }
      }
    }
  }
  const POSE0 = () => ({ hip: [0, 0], knee: [0, 0], sh: [0, 0], el: [0.1, 0.1], nod: 0, turn: 0, twist: 0, dy: 0 });
  function pose(g, A, outP, outN) {
    const n = g.titik, P = [0, 0, 0], Q = [0, 0, 0], N1 = [0, 0, 0], N2 = [0, 0, 0];
    for (let v = 0; v < n; v++) {
      const a = g.sk[3 * v], b = g.sk[3 * v + 1], w = g.sk[3 * v + 2], k = 3 * v;
      P[0] = g.position[k]; P[1] = g.position[k + 1]; P[2] = g.position[k + 2]; chain(a, P, A, false);
      Q[0] = g.position[k]; Q[1] = g.position[k + 1]; Q[2] = g.position[k + 2]; chain(b, Q, A, false);
      N1[0] = g.normal[k]; N1[1] = g.normal[k + 1]; N1[2] = g.normal[k + 2]; chain(a, N1, A, true);
      N2[0] = g.normal[k]; N2[1] = g.normal[k + 1]; N2[2] = g.normal[k + 2]; chain(b, N2, A, true);
      outP[k] = w * P[0] + (1 - w) * Q[0]; outP[k + 1] = w * P[1] + (1 - w) * Q[1] + A.dy; outP[k + 2] = w * P[2] + (1 - w) * Q[2];
      let x = w * N1[0] + (1 - w) * N2[0], y = w * N1[1] + (1 - w) * N2[1], z = w * N1[2] + (1 - w) * N2[2]; const l = Math.hypot(x, y, z);
      if (l > 1e-6) { outN[k] = x / l; outN[k + 1] = y / l; outN[k + 2] = z / l; } else { outN[k] = g.normal[k]; outN[k + 1] = g.normal[k + 1]; outN[k + 2] = g.normal[k + 2]; }
    }
  }
  // sudut sendi per keadaan (jalan = VS lama: pinggul 0,42 sin(fase), lutut 1,3 x maks(0, pinggul), lengan -0,8 x pinggul; sendi siku baru)
  function poseOf(nama, ph) {
    const A = POSE0();
    if (nama === 'jalan') {
      const sw = Math.sin(ph);
      for (let i = 0; i < 2; i++) { A.hip[i] = (i ? 1 : -1) * 0.42 * sw; A.knee[i] = Math.max(0.06, A.hip[i]) * 1.3; A.sh[i] = -A.hip[i] * 0.8; A.el[i] = 0.12 + 0.9 * Math.max(0, -A.sh[i]); }
      A.dy = 0.03 * Math.abs(Math.cos(ph)); A.twist = -0.1 * sw; A.turn = 0.05 * Math.sin(ph * 0.5); A.nod = 0.03 * Math.cos(ph * 2);
    } else if (nama === 'duduk') {
      for (let i = 0; i < 2; i++) { A.hip[i] = -1.5; A.knee[i] = 1.5; A.sh[i] = -0.35; A.el[i] = 0.5; }
      A.dy = -0.38; A.nod = 0.1;
    } else { for (let i = 0; i < 2; i++) { A.sh[i] = 0.05 * Math.sin(ph + i); A.el[i] = 0.12; A.knee[i] = 0.06; } }
    return A;
  }

  // ---------- indeks kotak ----------
  function edgeStats(pos, idx, deg, capMask) {
    const q = (v) => Math.round(v * 1e4), key = new Map(), vid = [];
    for (let i = 0; i < pos.length; i += 3) { const k = q(pos[i]) + ',' + q(pos[i + 1]) + ',' + q(pos[i + 2]); if (!key.has(k)) key.set(k, key.size); vid.push(key.get(k)); }
    const fn = [], E = new Map();
    for (let t = 0; t < idx.length; t += 3) {
      const a = idx[t] * 3, b = idx[t + 1] * 3, c = idx[t + 2] * 3;
      const ux = pos[b] - pos[a], uy = pos[b + 1] - pos[a + 1], uz = pos[b + 2] - pos[a + 2], vx = pos[c] - pos[a], vy = pos[c + 1] - pos[a + 1], vz = pos[c + 2] - pos[a + 2];
      let x = uy * vz - uz * vy, y = uz * vx - ux * vz, z = ux * vy - uy * vx; const l = Math.hypot(x, y, z); fn.push(l > 1e-14 ? [x / l, y / l, z / l] : null);
      const v = [vid[idx[t]], vid[idx[t + 1]], vid[idx[t + 2]]];
      for (let e = 0; e < 3; e++) { const p = v[e], r = v[(e + 1) % 3], k = p < r ? p + '_' + r : r + '_' + p; if (!E.has(k)) E.set(k, []); E.get(k).push(t / 3); }
    }
    let shared = 0, hard = 0, open = 0; const cs = Math.cos(deg * Math.PI / 180);
    for (const f of E.values()) {
      if (f.length === 1) { open++; continue; }
      if (f.length !== 2 || !fn[f[0]] || !fn[f[1]]) continue;
      if (capMask && (capMask[f[0]] || capMask[f[1]])) continue;   // tutup ujung (tersembunyi di dalam sendi) tidak dihitung
      shared++; const a = fn[f[0]], b = fn[f[1]]; if (a[0] * b[0] + a[1] * b[1] + a[2] * b[2] < cs) hard++;
    }
    return { bersama: shared, keras: hard, terbuka: open, persen: shared ? 100 * hard / shared : 0 };
  }

  // ---------- model kotak lama (17 kotak): [sx, sy, sz, x, y, z, bagian] ----------
  function oldParts() {
    const p = [];
    for (const [side, L] of [[-1, 0], [1, 1]]) {
      p.push([0.15, 0.42, 0.17, side * 0.1, 0.69, 0, 3 + L], [0.13, 0.44, 0.15, side * 0.1, 0.26, 0, 5 + L], [0.12, 0.08, 0.25, side * 0.1, 0.04, 0.05, 5 + L], [0.1, 0.58, 0.12, side * 0.25, 1.16, 0, 7 + L], [0.09, 0.1, 0.1, side * 0.25, 0.83, 0, 12 + L]);
    }
    p.push([0.38, 0.56, 0.22, 0, 1.2, 0, 0], [0.36, 0.14, 0.2, 0, 0.93, 0, 10], [0.1, 0.07, 0.1, 0, 1.51, 0, 11], [0.19, 0.23, 0.21, 0, 1.64, 0, 1], [0.21, 0.08, 0.23, 0, 1.76, -0.01, 2], [0.21, 0.14, 0.06, 0, 1.68, -0.09, 2], [0.07, 0.3, 0.26, 0.29, 1.02, 0, 9]);
    return p;
  }
  // pose kaku lama (kembaran VS lama) untuk satu titik bagian id
  function oldPoint(id, P, ph, nama) {
    const sideL = (id === 3 || id === 5 || id === 7 || id === 12) ? 1 : 0, pose = nama === 'duduk' ? 2 : nama === 'berdiri' ? 1 : 0, sw = pose < 0.5 ? Math.sin(ph) : 0;
    let hip = 0, knee = 0, arm = 0, yOff = 0;
    if (pose < 0.5) { hip = (sideL ? 1 : -1) * 0.42 * sw; knee = Math.max(0, hip) * 1.3; arm = -hip * 0.8; yOff = 0.03 * Math.abs(Math.cos(ph)); }
    else if (pose > 1.5) { hip = -1.5; knee = 1.5; arm = -0.35; yOff = -0.38; } else arm = 0.05 * Math.sin(ph);
    const o = P.slice();
    if (id > 4.5 && id < 6.5) rx(o, 0.48, knee);
    if (id > 2.5 && id < 6.5) rx(o, 0.9, hip);
    if ((id > 6.5 && id < 8.5) || id > 11.5) rx(o, 1.44, arm);
    o[1] += yOff; return o;
  }

  const api = {
    ID, BONE, RIG, LV,
    shape: (level) => (level >= 2 ? buildFar() : build(level)),
    pose, poseOf, POSE0, edgeStats, normals,
    old: { parts: oldParts, point: oldPoint },
    PAL: {   // palet sama dengan uniform pejalan kaki di index.html
      shirt: ['#c8413b', '#2f5f9e', '#e8e4d8', '#3d7a4a', '#d9a43a', '#6b4a8a', '#1f2328', '#e07a4f', '#4a90a8', '#b8b2a6', '#8a2d4a', '#f2f0ea', '#556b2f', '#d86f9b'],
      pants: ['#1f2a44', '#2b2b2e', '#5a4a3a', '#6d737a', '#2e4a6b', '#8c7a5c', '#3a3f2e', '#15171a'],
      skin: ['#f1c9a5', '#e0ac85', '#c68863', '#9c6644', '#6e452c', '#f6d8bd'],
      hair: ['#2a1d15', '#4a3020', '#1a1a1a', '#8a6a3a', '#c9a15a', '#6a6a6a']
    }
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else window.PEDKIT = api;
})();
