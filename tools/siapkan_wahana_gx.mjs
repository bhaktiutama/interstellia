/* Olah wahana GX-01 (misi Gargantua, tahap G1a, kokpit G2) dari KESTREL.buildV3() di shared/kestrel.js menjadi aset ringkas
   experiences/gargantua/assets/gx01.data.js (window.__GX01 = { n, scale, pos, nrm, col, mat, eye, screens, ... }, base64).
   Gargantua tidak memakai three.js; three.js hanya dipakai di sini untuk membangun geometri.

   Yang dilakukan:
   - buildV3 tidak diubah. Kaki pendarat dilipat: segitiga yang punya titik di bawah y = -2,45 m dibuang (kaki, tapak, tangga bawah);
     pangkal kaki tetap terlihat sebagai rumah roda.
   - G2: kokpit lama v3 (kaca sempit di atas, sekat kaca tepat di depan mata, ujung kedua lengan garpu menutup pandangan)
     dibuang dan diganti pod kaca GX-01 di depan, duduk di pelat dek di antara ujung lengan, disambung leher ke badan tengah:
     kaca depan, atas, dan samping, rangka tipis hanya di sudut, konsol rendah dengan 3 layar MFD. Mata pilot di z -13,0 m,
     sejajar kabin ujung lengan, jadi lengan ada tepat di samping (80-90 derajat) dan pandangan depan bebas.
   - Posisi int16 (langkah 1 mm), normal int8, warna uint8, id material uint8 (0 badan, 1 kaca, 2 interior kokpit).
   - Kerangka: +x kanan, +y atas, -z depan (sama dengan buildV3), titik 0 = sumbu badan.
   Pakai: node tools/siapkan_wahana_gx.mjs   (butuh three@0.186.1: THREE_LOCAL=<folder node_modules/three> atau `npm i three@0.186.1`) */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const local = process.env.THREE_LOCAL;
const THREE = await import(local ? pathToFileURL(path.join(local, 'build/three.module.js')).href : 'three');

const ctx = { window: {}, Math, console };
vm.runInNewContext(fs.readFileSync(path.join(ROOT, 'shared/kestrel.js'), 'utf8'), ctx);
const V3 = ctx.window.KESTREL.buildV3(THREE);
const g = V3.geo, P = g.attributes.position.array, N = g.attributes.normal.array, C = g.attributes.color.array;

const CUT_Y = -2.45;                                           // di bawah ini = kaki pendarat yang dilipat
const GLASS = [0.05, 0.07, 0.09];                              // warna kaca v3 (palet buildV3)
const isGlass = (i) => Math.abs(C[i] - GLASS[0]) < 1e-3 && Math.abs(C[i + 1] - GLASS[1]) < 1e-3 && Math.abs(C[i + 2] - GLASS[2]) < 1e-3;
// kokpit lama v3: semua titik di z -9,85..-5,75, |x| <= 1,95, y >= -0,95 (loft kokpit, sekat kaca, tutup depan badan tengah)
const oldCockpit = (t) => {
  for (let k = 0; k < 3; k++) {
    const i = t * 9 + k * 3, x = P[i], y = P[i + 1], z = P[i + 2];
    if (z < -9.85 || z > -5.75 || Math.abs(x) > 1.95 || y < -0.95) return false;
  }
  return true;
};

// ---------- daftar segitiga keluaran: [p0, p1, p2, normal, warna, material] ----------
const T = [];
let removed = 0;
for (let t = 0; t < P.length / 9; t++) {
  const ymin = Math.min(P[t * 9 + 1], P[t * 9 + 4], P[t * 9 + 7]);
  if (ymin < CUT_Y) continue;
  if (oldCockpit(t)) { removed++; continue; }
  const v = [0, 1, 2].map((k) => [P[t * 9 + k * 3], P[t * 9 + k * 3 + 1], P[t * 9 + k * 3 + 2]]);
  const n = [0, 1, 2].map((k) => [N[t * 9 + k * 3], N[t * 9 + k * 3 + 1], N[t * 9 + k * 3 + 2]]);
  const c = [C[t * 9], C[t * 9 + 1], C[t * 9 + 2]];
  T.push({ v, n, c, m: isGlass(t * 9) ? 1 : 0 });
}

// ---------- alat geometri kokpit GX-01 ----------
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const mul = (a, k) => [a[0] * k, a[1] * k, a[2] * k], dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const norm = (a) => { const l = Math.hypot(...a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
function tri(a, b, c, col, m, outHint) {                        // segitiga datar; outHint = arah luar untuk membetulkan urutan
  let n = norm(cross(sub(b, a), sub(c, a)));
  if (outHint && dot(n, outHint) < 0) { [b, c] = [c, b]; n = mul(n, -1); }
  T.push({ v: [a, b, c], n: [n, n, n], c: col, m });
}
function quad(a, b, c, d, col, m, outHint) { tri(a, b, c, col, m, outHint); tri(a, c, d, col, m, outHint); }
function oct(w, h, cy, chT, chB) {                             // urutan sisi sama dengan buildV3: 0 bawah, 2 kanan, 4 atas, 6 kiri
  const a = w / 2, b = h / 2;
  return [[-a + chB, cy - b], [a - chB, cy - b], [a, cy - b + chB], [a, cy + b - chT],
          [a - chT, cy + b], [-a + chT, cy + b], [-a, cy + b - chT], [-a, cy - b + chB]];
}
const PALE = [0.78, 0.77, 0.74], FRAME = [0.2, 0.2, 0.21], DARK = [0.13, 0.13, 0.14], CAB = [0.16, 0.16, 0.17], CAB2 = [0.24, 0.235, 0.23];
const ORANGE = [0.85, 0.36, 0.08], METAL = [0.42, 0.44, 0.46], STRUT = [0.07, 0.07, 0.075];   // rangka kanopi gelap doff (tidak silau dari kokpit)
function bar(p, q, t, col, m = 0) {                            // batang persegi tipis dari p ke q (tebal t)
  const d = norm(sub(q, p)), up = Math.abs(d[1]) < 0.9 ? [0, 1, 0] : [1, 0, 0];
  const s = mul(norm(cross(d, up)), t / 2), u = mul(norm(cross(s, d)), t / 2);
  const c = [add(s, u), add(mul(s, -1), u), mul(add(s, u), -1), add(s, mul(u, -1))];
  for (let k = 0; k < 4; k++) {
    const a = add(p, c[k]), b = add(p, c[(k + 1) % 4]), e = add(q, c[(k + 1) % 4]), f = add(q, c[k]);
    quad(a, b, e, f, col, m, add(c[k], c[(k + 1) % 4]));
  }
}
function box(cx, cy, cz, sx, sy, sz, col, m = 0, rotX = 0) {    // kotak, bisa dimiringkan di sumbu x (sudut rotX)
  const cs = Math.cos(rotX), sn = Math.sin(rotX);
  const R = (p) => [p[0], p[1] * cs - p[2] * sn, p[1] * sn + p[2] * cs];
  const v = (x, y, z) => add([cx, cy, cz], R([x * sx / 2, y * sy / 2, z * sz / 2]));
  const F = [[[1, -1, -1], [1, 1, -1], [1, 1, 1], [1, -1, 1], [1, 0, 0]], [[-1, -1, 1], [-1, 1, 1], [-1, 1, -1], [-1, -1, -1], [-1, 0, 0]],
             [[-1, 1, -1], [-1, 1, 1], [1, 1, 1], [1, 1, -1], [0, 1, 0]], [[-1, -1, 1], [-1, -1, -1], [1, -1, -1], [1, -1, 1], [0, -1, 0]],
             [[-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1], [0, 0, 1]], [[1, -1, -1], [-1, -1, -1], [-1, 1, -1], [1, 1, -1], [0, 0, -1]]];
  for (const [a, b, c, d, o] of F) quad(v(...a), v(...b), v(...c), v(...d), col, m, R(o));
}

// ---------- kokpit GX-01: pod kaca di depan, di antara ujung garpu ----------
// Kokpit v3 di tengah dibuang. Pod baru duduk di pelat dek di antara kabin ujung lengan (z -11,4..-13,6), hidung di z -15,4,
// melewati ujung lengan (-14,2). Lengan jadi tepat di samping pilot (sudut 80-90 derajat), pandangan depan 160 derajat bebas.
// Leher (z -5,8..-10,4) menyambung pod ke badan tengah; muka depan badan tengah ditutup lagi.
const RINGS = [
  { z: -10.4, s: oct(2.2, 2.0, 0.3, 0.5, 0.35) },
  { z: -11.0, s: oct(3.0, 3.2, 0.7, 1.0, 0.4) },
  { z: -13.6, s: oct(2.9, 3.0, 0.6, 1.1, 0.4) },
  { z: -14.9, s: oct(2.0, 1.2, -0.1, 0.45, 0.3) },               // hidung rendah: atas 0,5 m, tersembunyi di balik panel layar
  { z: -15.4, s: oct(1.0, 0.5, -0.25, 0.15, 0.1) },
];
const GLASS_FACES = { 1: [2, 3, 4, 5, 6], 2: [2, 3, 4, 5, 6] };   // segmen P1-P2 (kanopi) dan P2-P3 (kaca depan miring)
const tone = (c, k) => c.map((x) => Math.min(1, x * k));
function loftRings(RS, glassFaces, capStart, capEnd) {
  for (let r = 0; r < RS.length - 1; r++) {
    const A = RS[r], B = RS[r + 1];
    const cy = (A.s.reduce((q, p) => q + p[1], 0) + B.s.reduce((q, p) => q + p[1], 0)) / 16;
    for (let k = 0; k < 8; k++) {
      const k2 = (k + 1) % 8;
      const a = [A.s[k][0], A.s[k][1], A.z], b = [A.s[k2][0], A.s[k2][1], A.z], c = [B.s[k2][0], B.s[k2][1], B.z], d = [B.s[k][0], B.s[k][1], B.z];
      const mid = mul(add(add(a, b), add(c, d)), 0.25), out = sub(mid, [0, cy, mid[2]]);   // arah luar dari sumbu segmen
      const glass = ((glassFaces || {})[r] || []).includes(k);
      const col = glass ? GLASS : (k === 0 || k === 1 || k === 7) ? FRAME : tone(PALE, 0.9 + 0.08 * ((k * 7 + r * 3) % 5) / 4);
      quad(a, b, c, d, col, glass ? 1 : 0, out);
    }
  }
  for (const [ring, dir, on] of [[RS[0], 1, capStart], [RS[RS.length - 1], -1, capEnd]]) {
    if (!on) continue;
    const cz = ring.z, cy = ring.s.reduce((q, p) => q + p[1], 0) / 8;
    for (let k = 0; k < 8; k++) {
      const k2 = (k + 1) % 8;
      tri([0, cy, cz], [ring.s[k][0], ring.s[k][1], cz], [ring.s[k2][0], ring.s[k2][1], cz], dir > 0 ? PALE : FRAME, 0, [0, 0, dir]);
    }
  }
}
// tutup muka depan badan tengah (ikut terbuang bersama kokpit v3)
{ const S = oct(3.8, 2.7, 0.55, 0.6, 0.4), cy = 0.55;
  for (let k = 0; k < 8; k++) { const k2 = (k + 1) % 8; tri([0, cy, -5.8], [S[k][0], S[k][1], -5.8], [S[k2][0], S[k2][1], -5.8], tone(PALE, 0.92), 0, [0, 0, -1]); } }
// leher: badan tengah ke pod
loftRings([{ z: -5.8, s: oct(1.9, 1.7, 0.45, 0.4, 0.3) }, { z: -10.45, s: oct(1.9, 1.7, 0.45, 0.4, 0.3) }], null, false, false);
for (let k = 0; k < 3; k++) box(0, 1.33, -6.9 - k * 1.3, 1.1, 0.12, 0.5, DARK);                  // sirip pendingin di punggung leher
loftRings(RINGS, GLASS_FACES, true, true);
// rangka kanopi: hanya di sudut (titik 2-7) dan lingkar di P1, P2, P3; tebal 6 cm, gelap doff
for (let r = 1; r <= 2; r++) for (const k of [2, 3, 4, 5, 6, 7]) {
  const A = RINGS[r], B = RINGS[r + 1];
  bar([A.s[k][0], A.s[k][1], A.z], [B.s[k][0], B.s[k][1], B.z], 0.06, STRUT);
}
for (const r of [1, 2, 3]) for (let k = 2; k <= 6; k++) {
  const S = RINGS[r].s;
  bar([S[k][0], S[k][1], RINGS[r].z], [S[k + 1][0], S[k + 1][1], RINGS[r].z], 0.06, STRUT);
}
for (const sx of [-1, 1]) bar([sx * 1.52, -0.52, -11.0], [sx * 1.47, -0.52, -13.6], 0.05, ORANGE);   // garis aksen jingga di bahu pod
// tiang pod ke pelat dek
for (const sx of [-1, 1]) for (const z of [-11.4, -13.2]) bar([sx * 0.9, -0.92, z], [sx * 0.9, -1.0, z], 0.18, METAL);

// ---------- interior kokpit (material 2) ----------
box(0, -0.6, -12.7, 2.6, 0.1, 4.2, CAB, 2);                                     // lantai
box(0, -0.15, -14.45, 2.4, 0.8, 0.7, CAB, 2);                                   // badan konsol (atas 0,25 m)
const BEZ = { c: [0, 0.35, -14.15], tilt: 30 * Math.PI / 180, w: 2.3, h: 0.56 };  // panel layar miring menghadap pilot
box(BEZ.c[0], BEZ.c[1], BEZ.c[2], BEZ.w, BEZ.h, 0.08, CAB2, 2, -BEZ.tilt);
for (const sx of [-1, 1]) {
  bar([sx * 1.4, 0.15, -11.0], [sx * 1.37, 0.15, -13.6], 0.12, CAB2, 2);           // ambang samping kanopi
  box(sx * 1.05, -0.25, -12.2, 0.45, 0.7, 1.6, CAB, 2);                          // konsol samping
}
// layar MFD: di bidang panel, sedikit di depannya; tekstur dari atlas 3 kolom (u0..u1) di halaman
const nB = [0, Math.sin(BEZ.tilt), Math.cos(BEZ.tilt)], upB = [0, Math.cos(BEZ.tilt), -Math.sin(BEZ.tilt)];
const screens = [-0.73, 0, 0.73].map((x, i) => ({
  c: add(add(BEZ.c, [x, 0, 0]), mul(nB, 0.045)), w: 0.66, h: 0.44, n: nB, up: upB, u0: i / 3, u1: (i + 1) / 3,
}));

// ---------- tulis keluaran ----------
const n = T.length * 3, SCALE = 1000;                          // 1 satuan int16 = 1 mm (jangkauan +-32,7 m)
const pos = new Int16Array(n * 3), nrm = new Int8Array(n * 3), col = new Uint8Array(n * 3), mat = new Uint8Array(n);
let v = 0, maxA = 0, glassN = 0, interiorN = 0;
const bb = { min: [1e9, 1e9, 1e9], max: [-1e9, -1e9, -1e9] };
for (const t of T) for (let k = 0; k < 3; k++, v++) {
  for (let a = 0; a < 3; a++) {
    const p = t.v[k][a]; maxA = Math.max(maxA, Math.abs(p));
    bb.min[a] = Math.min(bb.min[a], p); bb.max[a] = Math.max(bb.max[a], p);
    pos[v * 3 + a] = Math.round(p * SCALE);
    nrm[v * 3 + a] = Math.round(Math.max(-1, Math.min(1, t.n[k][a])) * 127);
    col[v * 3 + a] = Math.round(Math.max(0, Math.min(1, t.c[a])) * 255);
  }
  mat[v] = t.m; if (t.m === 1) glassN++; if (t.m === 2) interiorN++;
}
if (maxA * SCALE > 32767) throw new Error('model melebihi jangkauan int16: ' + maxA);
const b64 = (a) => Buffer.from(a.buffer, a.byteOffset, a.byteLength).toString('base64');
const meta = {
  n, scale: 1 / SCALE, name: 'GX-01',
  bbox: bb, eye: [0, 1.0, -13.0],                              // mata pilot di pod depan, di antara ujung lengan garpu
  decals: [{ text: 'GX-01', w: 2.4, h: 0.6, c: [-4.83, 0.55, -3.6], nx: -1 }, { text: 'GX-01', w: 2.4, h: 0.6, c: [4.83, 0.55, -3.6], nx: 1 }],
  screens,
  source: 'KESTREL.buildV3 (shared/kestrel.js), kaki dilipat di y < ' + CUT_Y + ', kokpit v3 diganti kanopi GX-01',
};
const out = `/* Dibuat oleh tools/siapkan_wahana_gx.mjs. Jangan diedit tangan. Wahana GX-01 (desain orisinal, dari blokout v3). */
window.__GX01 = Object.assign(${JSON.stringify(meta)}, {
  pos: '${b64(pos)}',
  nrm: '${b64(nrm)}',
  col: '${b64(col)}',
  mat: '${b64(mat)}',
});
`;
const dst = path.join(ROOT, 'experiences/gargantua/assets/gx01.data.js');
fs.mkdirSync(path.dirname(dst), { recursive: true });
fs.writeFileSync(dst, out);
console.log(`segitiga ${T.length} (kokpit v3 dibuang ${removed}), verteks ${n}, kaca ${glassN}, interior ${interiorN}, ` +
  `bbox ${bb.min.map((x) => x.toFixed(2))} .. ${bb.max.map((x) => x.toFixed(2))}, ${(out.length / 1024).toFixed(0)} KB -> ${path.relative(ROOT, dst)}`);
