/* Olah wahana GX-01 (misi Gargantua, tahap G1a) dari KESTREL.buildV3() di shared/kestrel.js menjadi aset ringkas
   experiences/gargantua/assets/gx01.data.js (window.__GX01 = { n, scale, pos, nrm, col, mat, eye, ... }, base64).
   Gargantua tidak memakai three.js; three.js hanya dipakai di sini untuk membangun geometri.

   Yang dilakukan:
   - buildV3 tidak diubah. Kaki pendarat dilipat: segitiga yang punya titik di bawah y = -2,45 m dibuang (kaki, tapak, tangga bawah);
     pangkal kaki tetap terlihat sebagai rumah roda.
   - Posisi int16 (langkah 1 mm), normal int8, warna uint8, id material uint8 (0 badan, 1 kaca kokpit).
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
const keep = [];
for (let t = 0; t < P.length / 9; t++) {
  const ymin = Math.min(P[t * 9 + 1], P[t * 9 + 4], P[t * 9 + 7]);
  if (ymin >= CUT_Y) keep.push(t);
}
const n = keep.length * 3, SCALE = 1000;                       // 1 satuan int16 = 1 mm (jangkauan +-32,7 m)
const pos = new Int16Array(n * 3), nrm = new Int8Array(n * 3), col = new Uint8Array(n * 3), mat = new Uint8Array(n);
let v = 0, maxA = 0;
const bb = { min: [1e9, 1e9, 1e9], max: [-1e9, -1e9, -1e9] };
for (const t of keep) for (let k = 0; k < 3; k++, v++) {
  const i = (t * 3 + k) * 3;
  for (let a = 0; a < 3; a++) {
    const p = P[i + a]; maxA = Math.max(maxA, Math.abs(p));
    bb.min[a] = Math.min(bb.min[a], p); bb.max[a] = Math.max(bb.max[a], p);
    pos[v * 3 + a] = Math.round(p * SCALE);
    nrm[v * 3 + a] = Math.round(Math.max(-1, Math.min(1, N[i + a])) * 127);
    col[v * 3 + a] = Math.round(Math.max(0, Math.min(1, C[i + a])) * 255);
  }
  mat[v] = isGlass(i) ? 1 : 0;
}
if (maxA * SCALE > 32767) throw new Error('model melebihi jangkauan int16: ' + maxA);
const b64 = (a) => Buffer.from(a.buffer, a.byteOffset, a.byteLength).toString('base64');
const meta = {
  n, scale: 1 / SCALE, name: 'GX-01',
  bbox: bb, eye: [0, 1.25, -7.2],                             // mata pilot di kokpit kaca tengah depan (garis pandang datar lewat kaca atas)
  decals: [{ text: 'GX-01', w: 2.4, h: 0.6, c: [-4.83, 0.55, -3.6], nx: -1 }, { text: 'GX-01', w: 2.4, h: 0.6, c: [4.83, 0.55, -3.6], nx: 1 }],
  source: 'KESTREL.buildV3 (shared/kestrel.js), kaki dilipat di y < ' + CUT_Y,
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
console.log(`segitiga ${keep.length} dari ${P.length / 9}, verteks ${n}, kaca ${mat.reduce((s, x) => s + x, 0)}, ` +
  `bbox ${bb.min.map((x) => x.toFixed(2))} .. ${bb.max.map((x) => x.toFixed(2))}, ${(out.length / 1024).toFixed(0)} KB -> ${path.relative(ROOT, dst)}`);
