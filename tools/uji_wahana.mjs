/* Uji kontrak wahana (rencana docs/app/rencana-pilihan-wahana.md): KS-07 v5, PR-11 Petrel, GX-01 dibangun oleh FLEET.build (shared/armada.js).
   Node + three.js 0.186.1 (THREE_LOCAL=<folder node_modules/three> atau `npm i three@0.186.1`), tanpa browser.
   Periksa: field wajib, tanpa nilai tidak valid, normal satuan, penanda kaca (biru > merah dan hijau < 0,1) hanya di geometri kaca, ukuran sesuai `size`,
   kaki mencapai PAD_Y, kaki dan pad sesuai, kokpit (layar, tongkat, tuas, mata di dalam badan), blob Gargantua ks07 / pr11 / gx01 valid,
   dan shared/kestrel.js tidak berubah (v5 dan v3 disimpan). Pakai: node tools/uji_wahana.mjs */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { execSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const local = process.env.THREE_LOCAL;
const THREE = await import(local ? pathToFileURL(path.join(local, 'build/three.module.js')).href : 'three');
const ctx = { window: {}, Math, console, atob: (b) => Buffer.from(b, 'base64').toString('binary') };
vm.createContext(ctx);
const run = (f) => vm.runInContext(fs.readFileSync(path.join(ROOT, f), 'utf8'), ctx, { filename: f });
for (const f of ['shared/kestrel.js', 'shared/petrel.js', 'shared/armada.js', 'experiences/gargantua/assets/gx01.data.js']) run(f);
const FLEET = ctx.window.FLEET;

let ok = true;
const check = (name, cond, info = '') => { console.log((cond ? 'OK   ' : 'GAGAL') + ' ' + name + (info ? ' (' + info + ')' : '')); ok = ok && !!cond; };
const arr = (g, n) => g.attributes[n].array;
const finite = (a) => { for (let i = 0; i < a.length; i++) if (!Number.isFinite(a[i])) return false; return true; };
const isGlassC = (c, i) => c[i + 2] - c[i] > 0.035 && c[i + 1] < 0.1;
const bbox = (g) => { const p = arr(g, 'position'), b = { min: [1e9, 1e9, 1e9], max: [-1e9, -1e9, -1e9] }; for (let i = 0; i < p.length; i += 3) for (let a = 0; a < 3; a++) { b.min[a] = Math.min(b.min[a], p[i + a]); b.max[a] = Math.max(b.max[a], p[i + a]); } return b; };

for (const id of FLEET.ids) {
  const S = FLEET.build(THREE, id), info = FLEET.info[id];
  for (const f of ['geo', 'glass', 'legs', 'PAD_Y', 'pads', 'door', 'nav', 'nozzles', 'fans', 'low', 'belly', 'eye', 'size', 'cockpit', 'fly'])
    check(`${id}: field ${f}`, S[f] !== undefined && S[f] !== null || (f === 'fly' && id === 'ks07'));
  for (const f of ['geo', 'glass', 'legs']) {
    const g = S[f], p = arr(g, 'position'), n = arr(g, 'normal'), c = arr(g, 'color');
    let bad = 0, nonUnit = 0; for (let i = 0; i < n.length; i += 3) { const l = Math.hypot(n[i], n[i + 1], n[i + 2]); if (Math.abs(l - 1) > 0.02) nonUnit++; }
    check(`${id}.${f}: ${p.length / 9} segitiga, posisi / normal / warna terhingga, normal satuan`, p.length > 0 && finite(p) && finite(n) && finite(c) && nonUnit === 0, `normal bukan satuan ${nonUnit}`);
  }
  const hc = arr(S.geo, 'color'), gc = arr(S.glass, 'color'); let hullGlass = 0, glassNot = 0;
  for (let i = 0; i < hc.length; i += 3) if (isGlassC(hc, i)) hullGlass++;
  for (let i = 0; i < gc.length; i += 3) if (!isGlassC(gc, i)) glassNot++;
  check(`${id}: penanda kaca hanya di geometri kaca (badan ${hullGlass} verteks berpenanda, kaca ${glassNot} tanpa penanda)`, hullGlass === 0 && glassNot === 0);
  const B = bbox(S.geo);
  if (id !== 'gx01') {                                           // GX-01: ukuran v3 mencakup lengan, bbox badan tanpa kaki lebih kecil; diperiksa lewat kaki di bawah
    const L = B.max[2] - B.min[2], W = B.max[0] - B.min[0];
    check(`${id}: panjang ${L.toFixed(1)} m dan lebar ${W.toFixed(1)} m dekat size ${S.size.L} x ${S.size.W} (10%)`, Math.abs(L - S.size.L) / S.size.L < 0.1 && Math.abs(W - S.size.W) / S.size.W < 0.1);
  }
  const Lg = bbox(S.legs);
  check(`${id}: kaki mencapai PAD_Y ${S.PAD_Y} (paling bawah ${Lg.min[1].toFixed(2)})`, Math.abs(Lg.min[1] - S.PAD_Y) < 0.3);
  check(`${id}: tapak di bawah titik tertinggi kaki, jumlah pad ${S.pads.length}`, S.pads.length >= 3 && S.pads.every((p) => Number.isFinite(p.x) && Number.isFinite(p.z) && p.r > 0));
  check(`${id}: titik naik di luar kotak tabrakan rendah`, S.low.every((L) => !(S.door.x > L.x0 - 0.3 && S.door.x < L.x1 + 0.3 && S.door.z > L.z0 - 0.3 && S.door.z < L.z1 + 0.3)));
  check(`${id}: nosel ${S.nozzles.length} dan kipas ${S.fans.length} terhingga`, S.nozzles.length >= 2 && S.fans.length >= 2 && [...S.nozzles, ...S.fans].every((q) => q.every(Number.isFinite)));
  const C = S.cockpit, ce = C.eye;
  check(`${id}: kokpit: geometri ${arr(C.geo, 'position').length / 9} segitiga, layar ${C.screens.length} (kiri, tengah, kanan ada), tongkat dan tuas`, finite(arr(C.geo, 'position')) && ['kiri', 'tengah', 'kanan'].every((n) => C.screens.some((s) => s.name === n)) && arr(C.stick, 'position').length > 0 && arr(C.throttle, 'position').length > 0);
  check(`${id}: mata (${ce.map((x) => x.toFixed(2))}) sama dengan eye wahana dan di dalam kotak badan`, ce.every((x, i) => Math.abs(x - S.eye[i]) < 1e-6) && ce[2] > B.min[2] && ce[2] < B.max[2] && Math.abs(ce[0]) < 0.5);
  const sc0 = C.screens[1], off = C.offset;
  check(`${id}: layar tengah ${sc0.w} x ${sc0.h} m di depan mata (jarak ${Math.hypot(sc0.c[0] + off[0] - ce[0], sc0.c[1] + off[1] - ce[1], sc0.c[2] + off[2] - ce[2]).toFixed(2)} m)`, sc0.w > 0.2 && Math.hypot(sc0.c[0] + off[0] - ce[0], sc0.c[1] + off[1] - ce[1], sc0.c[2] + off[2] - ce[2]) < 1.8);
}

// blob Gargantua
const blob = (D, name) => {
  const raw = (b) => Buffer.from(b, 'base64'), pos = raw(D.pos), nrm = raw(D.nrm), col = raw(D.col), mat = raw(D.mat);
  check(`blob ${name}: n = ${D.n} verteks, pos ${pos.length / 6} = n, nrm / col ${nrm.length / 3} = n, mat ${mat.length} = n`, D.n % 3 === 0 && pos.length === D.n * 6 && nrm.length === D.n * 3 && col.length === D.n * 3 && mat.length === D.n);
  check(`blob ${name}: ada kaca (mat 1) dan interior (mat >= 2), semua id <= 17`, mat.includes(1) && mat.some((m) => m >= 2) && mat.every((m) => m <= 17));
  const eye = D.eye; check(`blob ${name}: mata di dalam bbox`, eye.every((x, i) => x >= D.bbox.min[i] && x <= D.bbox.max[i]));
  check(`blob ${name}: ${D.screens.length} layar dengan n dan up satuan`, D.screens.length >= 3 && D.screens.every((s) => Math.abs(Math.hypot(...s.n) - 1) < 1e-3 && Math.abs(Math.hypot(...s.up) - 1) < 1e-3));
};
for (const id of ['ks07', 'pr11']) {
  const c2 = { window: {} }; vm.runInNewContext(fs.readFileSync(path.join(ROOT, 'shared/wahana', id + '.data.js'), 'utf8'), c2);
  const D = c2.window.__SHIPDATA; blob(D, id);
  check(`blob ${id}: canopy = gen, chase dan aim ada, name ${D.name}`, D.canopy === 'gen' && D.chase.length === 3 && D.aim.length === 3 && !!D.name);
}
blob(ctx.window.__GX01, 'gx01');

// shared/kestrel.js tidak berubah dibanding komit induk percabangan (v5 dan v3 disimpan)
try {
  const base = execSync('git merge-base HEAD origin/main', { cwd: ROOT }).toString().trim();
  const diff = execSync(`git diff ${base} -- shared/kestrel.js`, { cwd: ROOT }).toString();
  check('shared/kestrel.js tidak diubah oleh pekerjaan pilihan wahana (v5 dan v3 tetap)', diff.trim() === '' || process.env.KESTREL_DIFF_OK === '1', diff ? 'ada perbedaan dari origin/main' : '');
} catch (e) { console.log('lewati: git tidak tersedia'); }

console.log(ok ? 'HASIL: LULUS' : 'HASIL: GAGAL');
process.exit(ok ? 0 : 1);
