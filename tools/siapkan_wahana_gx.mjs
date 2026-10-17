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
   - Posisi int16 (langkah 1 mm), normal int8, warna uint8, id material uint8 (0 badan, 1 kaca, 2 interior panel, 3 LED, 4 logam, 5 karet, 6 kain, 7 plastik, 10 + k indikator).
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
// rangka kanopi: hanya di sudut (titik 2-7) dan lingkar di P1, P2, P3. K2: profil dua lapis: luar 8,5 cm gelap doff (badan),
// lis dalam 3,5 cm abu interior digeser 5,5 cm ke sumbu pod (dicahayai seperti interior, terlihat jelas dari kokpit)
const LIP = [0.27, 0.27, 0.28];
function frameBar(p, q) {
  bar(p, q, 0.085, STRUT);
  const mid = mul(add(p, q), 0.5), inw = norm(sub([0, 0.6, mid[2]], [mid[0], mid[1], mid[2]]));
  bar(add(p, mul(inw, 0.055)), add(q, mul(inw, 0.055)), 0.035, LIP, 2);
}
for (let r = 1; r <= 2; r++) for (const k of [2, 3, 4, 5, 6, 7]) {
  const A = RINGS[r], B = RINGS[r + 1];
  frameBar([A.s[k][0], A.s[k][1], A.z], [B.s[k][0], B.s[k][1], B.z]);
}
for (const r of [1, 2, 3]) for (let k = 2; k <= 6; k++) {
  const S = RINGS[r].s;
  frameBar([S[k][0], S[k][1], RINGS[r].z], [S[k + 1][0], S[k + 1][1], RINGS[r].z]);
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

// ---------- K2 / K3: kokpit lebih padat ----------
// Material: 2 interior, 3 memancar tetap (LED, warna verteks = warna cahaya), 10 + k lampu indikator k (warna dan nyala dari halaman).
const BTN = [0.33, 0.33, 0.34], BTN2 = [0.2, 0.2, 0.21], SEAT = [0.11, 0.11, 0.12], SEAT2 = [0.19, 0.18, 0.17], RUB = [0.08, 0.08, 0.085];
const LED_C = [0.25, 0.62, 0.85], LED_A = [0.95, 0.55, 0.18], LED_R = [0.9, 0.12, 0.08];
function obox(c, R, U, F, sx, sy, sz, col, m = 2) {             // kotak berorientasi: R, U, F sumbu satuan, ukuran penuh
  const hx = mul(R, sx / 2), hy = mul(U, sy / 2), hz = mul(F, sz / 2);
  const v = (a, b, d) => add(add(add(c, mul(hx, a)), mul(hy, b)), mul(hz, d));
  const faces = [[[1, -1, -1], [1, 1, -1], [1, 1, 1], [1, -1, 1], hx], [[-1, -1, 1], [-1, 1, 1], [-1, 1, -1], [-1, -1, -1], mul(hx, -1)],
                 [[-1, 1, -1], [-1, 1, 1], [1, 1, 1], [1, 1, -1], hy], [[-1, -1, 1], [-1, -1, -1], [1, -1, -1], [1, -1, 1], mul(hy, -1)],
                 [[-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1], hz], [[1, -1, -1], [-1, -1, -1], [-1, 1, -1], [1, 1, -1], mul(hz, -1)]];
  for (const [a, b, d, e, o] of faces) quad(v(...a), v(...b), v(...d), v(...e), col, m, o);
}
function slab(P4, th, col, m = 2) {                             // pelat dari 4 titik atas (urut keliling), tebal th ke bawah normalnya
  const n = norm(cross(sub(P4[1], P4[0]), sub(P4[3], P4[0]))), up = n[1] < 0 ? mul(n, -1) : n, D = P4.map((p) => sub(p, mul(up, th)));
  quad(P4[0], P4[1], P4[2], P4[3], col, m, up); quad(D[3], D[2], D[1], D[0], col, m, mul(up, -1));
  for (let k = 0; k < 4; k++) { const k2 = (k + 1) % 4, mid = mul(add(P4[k], P4[k2]), 0.5), cen = mul(P4.reduce((a, b) => add(a, b)), 0.25);
    quad(P4[k], P4[k2], D[k2], D[k], col, m, sub(mid, cen)); }
}
const basis = (n, upHint = [0, 1, 0]) => { const F = norm(n), U = norm(sub(upHint, mul(F, dot(upHint, F)))), R = norm(cross(U, F)); return { R, U, F }; };
const EYE = [0, 1.0, -13.0];

// glare shield: tudung di atas panel layar (di atas garis pandang ke tepi atas layar), tepi depan sempit agar tidak menembus kaca
slab([[-1.1, 0.74, -14.05], [1.1, 0.74, -14.05], [0.7, 0.68, -14.55], [-0.7, 0.68, -14.55]], 0.035, CAB);
obox([0, 0.7, -14.07], [1, 0, 0], [0, 1, 0], [0, 0, 1], 1.9, 0.008, 0.012, LED_C, 3);              // lampu strip bawah tudung (menyinari layar)
// combiner HUD: dua tiang tipis dan palang atas, kaca combiner tidak digambar (simbol HUD digambar di lapisan halaman)
const HUD = (() => { const tilt = 15 * Math.PI / 180, B = basis([0, Math.sin(tilt), Math.cos(tilt)]);
  return { c: [0, 0.93, -14.22], w: 0.68, h: 0.34, n: B.F, up: B.U }; })();
for (const sx of [-1, 1]) bar([sx * 0.36, 0.73, -14.2], add(add(HUD.c, [sx * 0.36, 0, 0]), mul(HUD.up, HUD.h / 2)), 0.014, RUB, 2);
bar(add(add(HUD.c, [-0.36, 0, 0]), mul(HUD.up, HUD.h / 2)), add(add(HUD.c, [0.36, 0, 0]), mul(HUD.up, HUD.h / 2)), 0.014, RUB, 2);

// bezel per layar utama: bingkai 2,5 cm menonjol + 5 tombol tepi di bawah tiap layar
const IND = [];                                                 // lampu indikator: { k, kind } (urutan k = indeks uInd di halaman)
for (const S of screens) {
  const B = { R: norm(cross(mul(S.n, -1), S.up)), U: S.up, F: S.n }, c0 = add(S.c, mul(S.n, 0.004)), bw = 0.025;
  for (const [dx, dy, sx, sy] of [[0, S.h / 2 + bw / 2, S.w + 2 * bw, bw], [0, -S.h / 2 - bw / 2, S.w + 2 * bw, bw], [S.w / 2 + bw / 2, 0, bw, S.h], [-S.w / 2 - bw / 2, 0, bw, S.h]])
    obox(add(add(c0, mul(B.R, dx)), mul(B.U, dy)), B.R, B.U, B.F, sx, sy, 0.018, RUB);
  for (let i = 0; i < 5; i++) obox(add(add(c0, mul(B.R, (i - 2) * 0.11)), mul(B.U, -S.h / 2 - 0.045)), B.R, B.U, B.F, 0.06, 0.022, 0.014, BTN2);
}
// panel tengah bawah: 6 tombol fungsi dengan lampu indikator (AP, sikap X: pusat / mendatar / lintasan / bebas, suar)
const LBL = [];                                                 // label tombol (atlas kanvas di halaman): { text, c, w, h, n, up }
{
  const tilt = 20 * Math.PI / 180, B = basis([0, Math.cos(tilt), Math.sin(tilt)], [0, Math.sin(tilt), -Math.cos(tilt)]);
  // B.F = normal panel (atas, sedikit ke pilot), B.U = arah "atas" label (menjauhi pilot di bidang panel)
  const c = [0, 0.02, -13.74]; obox(c, [1, 0, 0], B.U, B.F, 0.92, 0.3, 0.04, CAB2);
  box(0, -0.27, -13.8, 0.6, 0.55, 0.2, CAB, 2);                                  // kaki panel
  const top = add(c, mul(B.F, 0.02)), names = ['AP', 'CTR', 'LVL', 'TRK', 'FREE', 'FLR'];
  names.forEach((t, i) => {
    const p = add(top, [(i - 2.5) * 0.14, 0, 0]);
    obox(add(p, mul(B.U, -0.03)), [1, 0, 0], B.U, B.F, 0.09, 0.07, 0.024, BTN);
    obox(add(add(p, mul(B.U, 0.05)), mul(B.F, 0.004)), [1, 0, 0], B.U, B.F, 0.05, 0.012, 0.01, [1, 1, 1], 10 + i); IND.push({ k: i, name: t });
    LBL.push({ text: t, c: add(add(p, mul(B.U, 0.09)), mul(B.F, 0.0015)), w: 0.11, h: 0.03, n: B.F, up: B.U });
  });
}
// konsol samping diperpanjang ke depan + layar samping menghadap pilot + deret tombol + lampu peringatan
const SIDE = [];
for (const sx of [-1, 1]) {
  box(sx * 1.05, -0.25, -13.35, 0.45, 0.7, 0.7, CAB, 2);                         // perpanjangan konsol (z -13,0..-13,7)
  const c = [sx * 1.0, 0.33, -13.45], B = basis(sub(EYE, c)), w = 0.33, h = 0.22;
  obox(add(c, mul(B.F, -0.035)), B.R, B.U, B.F, w + 0.06, h + 0.06, 0.06, CAB2);  // rumah layar
  obox([sx * 1.05, 0.16, -13.5], [1, 0, 0], [0, 1, 0], [0, 0, 1], 0.08, 0.12, 0.08, CAB);   // tiang rumah layar
  SIDE.push({ c: add(c, mul(B.F, 0.002)), w, h, n: B.F, up: B.U });
  // deret tombol 3 x 4 di atas konsol (bagian belakang), sebagian berlampu kecil
  for (let a = 0; a < 3; a++) for (let b = 0; b < 4; b++) {
    const p = [sx * (0.9 + 0.1 * a), 0.115, -12.25 + 0.1 * b];
    obox(p, [1, 0, 0], [0, 1, 0], [0, 0, 1], 0.06, 0.02, 0.06, (a + b) % 3 ? BTN2 : BTN);
    if ((a * 4 + b) % 5 === 1) obox(add(p, [0, 0.012, 0.022]), [1, 0, 0], [0, 1, 0], [0, 0, 1], 0.02, 0.004, 0.008, (a + b) % 2 ? LED_A : LED_C, 3);
  }
  LBL.push({ text: sx < 0 ? 'COMMS  RELAY' : 'NAV  FUNNEL', c: [sx * 1.0, 0.1015, -12.4], w: 0.3, h: 0.04, n: [0, 1, 0], up: [0, 0, -1] });
}
// lampu peringatan di sisi panel tengah: kanopi (6), dalam horizon (7)
obox([-0.6, 0.1, -13.82], [1, 0, 0], [0, 1, 0], [0, 0, 1], 0.08, 0.03, 0.02, [1, 1, 1], 16); IND.push({ k: 6, name: 'CANOPY' });
obox([0.6, 0.1, -13.82], [1, 0, 0], [0, 1, 0], [0, 0, 1], 0.08, 0.03, 0.02, [1, 1, 1], 17); IND.push({ k: 7, name: 'HORIZON' });
LBL.push({ text: 'CANOPY', c: [-0.6, 0.1155, -13.76], w: 0.12, h: 0.025, n: [0, 1, 0], up: [0, 0, -1] });
LBL.push({ text: 'HORIZON', c: [0.6, 0.1155, -13.76], w: 0.12, h: 0.025, n: [0, 1, 0], up: [0, 0, -1] });
// konsol atas (di kanopi atas belakang kepala): pelat dengan lampu kecil
slab([[-0.35, 2.12, -11.15], [0.35, 2.12, -11.15], [0.35, 2.0, -11.9], [-0.35, 2.0, -11.9]], 0.05, CAB);
for (let i = 0; i < 6; i++) obox([(i - 2.5) * 0.1, 1.99, -11.6], [1, 0, 0], [0, 1, 0], [0, 0, 1], 0.04, 0.01, 0.03, i % 2 ? LED_A : LED_C, 3);
// kursi: dudukan, sandaran, sandaran kepala, sayap bahu
box(0, -0.25, -12.75, 0.56, 0.1, 0.5, SEAT, 2);
obox([0, 0.42, -12.45], [1, 0, 0], norm([0, 1, 0.12]), norm([0, -0.12, 1]), 0.52, 1.25, 0.1, SEAT, 2);
obox([0, 1.15, -12.5], [1, 0, 0], [0, 1, 0], [0, 0, 1], 0.32, 0.24, 0.12, SEAT2, 2);
for (const sx of [-1, 1]) obox([sx * 0.29, 0.55, -12.55], [1, 0, 0], [0, 1, 0], [0, 0, 1], 0.06, 0.6, 0.2, SEAT2, 2);
// lantai: pelat injakan bergaris dan sandaran kaki
for (let i = 0; i < 4; i++) box(0, -0.545, -13.2 - 0.25 * i, 1.4, 0.01, 0.04, RUB, 2);
// strip LED lantai di kaki konsol samping (cahaya kabin redup)
for (const sx of [-1, 1]) obox([sx * 0.82, -0.53, -12.6], [1, 0, 0], [0, 1, 0], [0, 0, 1], 0.01, 0.01, 1.6, LED_A, 3);

// layar: 3 utama + 2 samping, atlas 5 kolom
const SCR = screens.concat(SIDE).map((S, i, a) => ({ ...S, u0: i / a.length, u1: (i + 1) / a.length }));

// panel tempel kaca (K6): dua quad tembus di kaca depan kiri dan kanan, menghadap pilot
const PANELS = [-1, 1].map((sx, i) => { const c = [sx * 0.78, 0.92, -13.9], B = basis(sub(EYE, c)); return { c, w: 0.4, h: 0.24, n: B.F, up: B.U, u0: i / 2, u1: (i + 1) / 2 }; });

// ---------- AO per verteks interior (material 2): sinar pendek ke belahan normal, penghalang = semua segitiga tak tembus di kokpit ----------
{
  const inBox = (p) => p[2] < -10.3 && Math.abs(p[0]) < 1.8 && p[1] > -1.0 && p[1] < 2.5;
  const occ = T.filter((t) => t.m !== 1 && t.v.some(inBox)).map((t) => ({ a: t.v[0], e1: sub(t.v[1], t.v[0]), e2: sub(t.v[2], t.v[0]),
    c: mul(add(add(t.v[0], t.v[1]), t.v[2]), 1 / 3), r: Math.max(...t.v.map((v) => Math.hypot(...sub(v, mul(add(add(t.v[0], t.v[1]), t.v[2]), 1 / 3))))) }));
  const NR = 24, DIRS = [];                                    // arah Fibonacci di belahan +z, dipakai dengan basis normal
  for (let i = 0; i < NR; i++) { const z = 1 - (i + 0.5) / NR, r = Math.sqrt(1 - z * z), ph = i * 2.39996; DIRS.push([r * Math.cos(ph), r * Math.sin(ph), z]); }
  const MAXD = 0.45;
  const hit = (o, d, cand) => {
    for (const q of cand) {
      const pv = cross(d, q.e2), det = dot(q.e1, pv); if (Math.abs(det) < 1e-9) continue;
      const iv = 1 / det, tv = sub(o, q.a), u = dot(tv, pv) * iv; if (u < 0 || u > 1) continue;
      const qv = cross(tv, q.e1), v = dot(d, qv) * iv; if (v < 0 || u + v > 1) continue;
      const t = dot(q.e2, qv) * iv; if (t > 1e-4 && t < MAXD) return true;
    }
    return false;
  };
  let nAO = 0;
  for (const t of T) {
    if (t.m !== 2) continue;
    const n = t.n[0], cen = mul(add(add(t.v[0], t.v[1]), t.v[2]), 1 / 3), B = basis(n, Math.abs(n[1]) < 0.9 ? [0, 1, 0] : [1, 0, 0]);
    const cand = occ.filter((q) => Math.hypot(...sub(q.c, cen)) < MAXD + q.r + 0.3);
    const ks = t.v.map((v) => {
      const o = add(add(v, mul(sub(cen, v), 0.08)), mul(n, 0.002));
      let blocked = 0;
      for (const d0 of DIRS) { const d = add(add(mul(B.R, d0[0]), mul(B.U, d0[1])), mul(B.F, d0[2])); if (hit(o, d, cand)) blocked += d0[2]; }
      const tot = DIRS.reduce((a, d0) => a + d0[2], 0);
      return 1 - 0.7 * blocked / tot;
    });
    t.ao = ks; nAO++;
  }
  console.log(`AO interior: ${nAO} segitiga, ${occ.length} penghalang`);
}

// ---------- K3: bagian bergerak (tongkat kanan, tuas gas kiri), disimpan di ujung buffer dengan titik putarnya ----------
const nStatic = T.length, PARTS = {};
function part(name, pivot, build) { const s0 = T.length; build(); PARTS[name] = { pivot, start: s0 * 3, count: (T.length - s0) * 3 }; }
for (const sx of [-1, 1]) obox([sx * 1.0, 0.1, -12.62], [1, 0, 0], [0, 1, 0], [0, 0, 1], 0.12, 0.03, 0.14, RUB);   // dudukan
part('stick', [1.0, 0.12, -12.62], () => {
  bar([1.0, 0.12, -12.62], [1.0, 0.33, -12.62], 0.026, METAL, 2);
  obox([1.0, 0.38, -12.625], [1, 0, 0], [0, 1, 0], [0, 0, 1], 0.045, 0.1, 0.055, RUB);
  obox([1.0, 0.432, -12.64], [1, 0, 0], [0, 1, 0], [0, 0, 1], 0.016, 0.006, 0.016, LED_R, 3);
});
part('throttle', [-1.0, 0.12, -12.62], () => {
  bar([-1.0, 0.12, -12.62], [-1.0, 0.27, -12.66], 0.022, METAL, 2);
  obox([-1.0, 0.29, -12.67], [1, 0, 0], [0, 1, 0], [0, 0, 1], 0.12, 0.04, 0.05, RUB);
  obox([-0.95, 0.312, -12.67], [1, 0, 0], [0, 1, 0], [0, 0, 1], 0.012, 0.005, 0.012, LED_A, 3);
});

// ---------- K7: id bahan interior dari warna dasar (2 panel komposit, 4 logam, 5 karet, 6 kain kursi, 7 plastik tombol) ----------
const same = (a, b) => Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]) + Math.abs(a[2] - b[2]) < 1e-6;
function bahan(c) {
  if (same(c, METAL) || same(c, LIP)) return 4;
  if (same(c, RUB)) return 5;
  if (same(c, SEAT) || same(c, SEAT2)) return 6;
  if (same(c, BTN) || same(c, BTN2)) return 7;
  return 2;
}

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
    col[v * 3 + a] = Math.round(Math.max(0, Math.min(1, t.c[a] * (t.ao ? t.ao[k] : 1))) * 255);
  }
  mat[v] = t.m === 2 ? bahan(t.c) : t.m; if (t.m === 1) glassN++; if (t.m >= 2) interiorN++;
}
if (maxA * SCALE > 32767) throw new Error('model melebihi jangkauan int16: ' + maxA);
const b64 = (a) => Buffer.from(a.buffer, a.byteOffset, a.byteLength).toString('base64');
const meta = {
  n, scale: 1 / SCALE, name: 'GX-01',
  bbox: bb, eye: [0, 1.0, -13.0],                              // mata pilot di pod depan, di antara ujung lengan garpu
  decals: [{ text: 'GX-01', w: 2.4, h: 0.6, c: [-4.83, 0.55, -3.6], nx: -1 }, { text: 'GX-01', w: 2.4, h: 0.6, c: [4.83, 0.55, -3.6], nx: 1 }],
  screens: SCR, nStatic: nStatic * 3, parts: PARTS, hud: HUD, panels: PANELS, labels: LBL, ind: IND,
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
