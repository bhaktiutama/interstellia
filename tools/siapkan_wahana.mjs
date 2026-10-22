/* Olah wahana KS-07 Kestrel (v5) dan PR-11 Petrel menjadi blob ringkas untuk Gargantua (pilihan wahana, rencana docs/app/rencana-pilihan-wahana.md W6):
   shared/wahana/ks07.data.js dan shared/wahana/pr11.data.js (window.__SHIPDATA = { n, scale, name, bbox, eye, decals, screens, nStatic, canopy, chase, aim,
   pos, nrm, col, mat }, base64). Format sama dengan gx01.data.js (tools/siapkan_wahana_gx.mjs, GX-01 tidak diolah ulang di sini); medan opsional
   parts, hud, panels, labels, ind tidak ada (Gargantua melewatinya: tanpa HUD kanopi, tanpa label tombol, tongkat dan tuas statis).
   Isi: badan + kaca (kaki tidak ikut: Gargantua melipat kaki) dan interior kokpit (id bahan 2) + tongkat dan tuas pada posisi netral.
   Posisi int16 (1 mm), normal int8, warna uint8, id bahan uint8 (0 badan, 1 kaca, 2 interior). Kerangka: +x kanan, +y atas, -z depan.
   Pakai: node tools/siapkan_wahana.mjs [ks07] [pr11]   (butuh three@0.186.1: THREE_LOCAL=<folder node_modules/three> atau `npm i three@0.186.1`) */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const local = process.env.THREE_LOCAL;
const THREE = await import(local ? pathToFileURL(path.join(local, 'build/three.module.js')).href : 'three');

const ctx = { window: {}, Math, console };
for (const f of ['kestrel.js', 'petrel.js', 'armada.js']) vm.runInNewContext(fs.readFileSync(path.join(ROOT, 'shared', f), 'utf8'), ctx);
const ids = process.argv.slice(2).filter((a) => !a.startsWith('-'));
if (!ids.length) ids.push('ks07', 'pr11');

const NAME = { ks07: 'KS-07', pr11: 'PR-11' };
const GLASS_ID = 1, INNER_ID = 2;

function tris(geo, off, mat, T) {                              // geometri tanpa indeks (normal datar) -> daftar segitiga
  const g = geo.index ? geo.toNonIndexed() : geo, P = g.attributes.position.array, N = g.attributes.normal.array, C = g.attributes.color.array;
  for (let t = 0; t < P.length / 9; t++) {
    const v = [0, 1, 2].map((k) => [P[t * 9 + k * 3] + off[0], P[t * 9 + k * 3 + 1] + off[1], P[t * 9 + k * 3 + 2] + off[2]]);
    const n = [0, 1, 2].map((k) => [N[t * 9 + k * 3], N[t * 9 + k * 3 + 1], N[t * 9 + k * 3 + 2]]);
    T.push({ v, n, c: [C[t * 9], C[t * 9 + 1], C[t * 9 + 2]], m: mat });
  }
}

for (const id of ids) {
  const S = ctx.window.FLEET.build(THREE, id), CK = S.cockpit, off = CK.offset, T = [];
  tris(S.geo, [0, 0, 0], 0, T);
  tris(S.glass, [0, 0, 0], GLASS_ID, T);
  tris(CK.geo, off, INNER_ID, T);
  const at = (p) => [p[0] + off[0], p[1] + off[1], p[2] + off[2]];
  tris(CK.stick, at(CK.stickAt), INNER_ID, T);                  // tongkat dan tuas: pose netral, statis
  tris(CK.throttle, at(CK.throttleAt), INNER_ID, T);

  // layar: kerangka layar kokpit (Euler YXZ rx, ry) -> normal dan atas di ruang wahana; atlas kolom sama lebar
  const e = new THREE.Euler(), vN = new THREE.Vector3(), vU = new THREE.Vector3();
  const screens = CK.screens.map((s, i, a) => {
    e.set(s.rx, s.ry, 0, 'YXZ'); vN.set(0, 0, 1).applyEuler(e); vU.set(0, 1, 0).applyEuler(e);
    return { c: at(s.c), w: s.w, h: s.h, n: [vN.x, vN.y, vN.z], up: [vU.x, vU.y, vU.z], u0: i / a.length, u1: (i + 1) / a.length };
  });

  const n = T.length * 3, SCALE = 1000;
  const pos = new Int16Array(n * 3), nrm = new Int8Array(n * 3), col = new Uint8Array(n * 3), mat = new Uint8Array(n);
  const bb = { min: [1e9, 1e9, 1e9], max: [-1e9, -1e9, -1e9] };
  let v = 0, maxA = 0, glassN = 0, innerN = 0;
  for (const t of T) for (let k = 0; k < 3; k++, v++) {
    for (let a = 0; a < 3; a++) {
      const p = t.v[k][a]; maxA = Math.max(maxA, Math.abs(p));
      bb.min[a] = Math.min(bb.min[a], p); bb.max[a] = Math.max(bb.max[a], p);
      pos[v * 3 + a] = Math.round(p * SCALE);
      nrm[v * 3 + a] = Math.round(Math.max(-1, Math.min(1, t.n[k][a])) * 127);
      col[v * 3 + a] = Math.round(Math.max(0, Math.min(1, t.c[a])) * 255);
    }
    mat[v] = t.m; if (t.m === GLASS_ID) glassN++; if (t.m === INNER_ID) innerN++;
  }
  if (maxA * SCALE > 32767) throw new Error('model melebihi jangkauan int16: ' + maxA);
  const k = S.size.L / 27.5;                                    // kamera luar mengikuti ukuran (GX-01 27,5 m: [0, 7,5, 40], bidik [0, 0, -6])
  const meta = {
    n, scale: 1 / SCALE, name: NAME[id], bbox: bb, eye: S.eye, decals: [], screens, nStatic: n, canopy: 'gen',
    chase: [0, +(7.5 * k).toFixed(2), +(40 * k).toFixed(2)], aim: [0, 0, +(-6 * k).toFixed(2)], size: S.size,
    source: 'FLEET.build(' + id + ') (shared/armada.js), kaki tidak ikut, kokpit = ' + (id === 'pr11' ? 'kokpit v5 digeser ke depan' : 'kokpit v5'),
  };
  const b64 = (a) => Buffer.from(a.buffer, a.byteOffset, a.byteLength).toString('base64');
  const out = `/* Dibuat oleh tools/siapkan_wahana.mjs. Jangan diedit tangan. Wahana ${NAME[id]} untuk Gargantua (desain orisinal). */
window.__SHIPDATA = Object.assign(${JSON.stringify(meta)}, {
  pos: '${b64(pos)}',
  nrm: '${b64(nrm)}',
  col: '${b64(col)}',
  mat: '${b64(mat)}',
});
`;
  const dst = path.join(ROOT, 'shared/wahana', id + '.data.js');
  fs.mkdirSync(path.dirname(dst), { recursive: true });
  fs.writeFileSync(dst, out);
  console.log(`${id}: segitiga ${T.length}, verteks ${n}, kaca ${glassN}, interior ${innerN}, bbox ${bb.min.map((x) => x.toFixed(2))} .. ${bb.max.map((x) => x.toFixed(2))}, ${(out.length / 1024).toFixed(0)} KB -> ${path.relative(ROOT, dst)}`);
}
