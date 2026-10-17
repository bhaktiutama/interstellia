/* Olah paket model orang "Ultimate Modular Men Pack" dan "Ultimate Modular Women Pack" (Quaternius, via Poly Pizza, CC BY / CC0, atribusi wajib)
   menjadi aset ringkas experiences/cooper-station/assets/orang.data.js (window.ORANG_DATA = { v, meta, blob }, base64).
   Rencana: docs/cooper-station/rencana-tahap-28-glb-cooper-station.md (tahap 28G1). Aturan proyek: game tidak memakai GLTFLoader; three.js dan
   GLTFLoader hanya dipakai di sini untuk membaca GLB dan membakar animasi.

   Yang dilakukan per karakter:
   - semua SkinnedMesh digabung; posisi dan normal dibakar ke meter y-atas (matriks dunia mesh); warna titik = warna bahan x COLOR_0 (linear -> sRGB 8 bit);
     tiap titik diberi kelas warna: 0 tetap, 1 kulit, 2 rambut, 3 baju atas, 4 celana, 5 sepatu, 6 mata (dari nama mesh dan bahan).
   - 3 tingkat detail dengan meshoptimizer (simplifyWithAttributes), normal dihitung ulang per titik dari segitiga yang memakainya.
   - posisi uint16 terkuantisasi di kotak batas karakter, normal int8, tulang uint8 x 4, bobot uint8 x 4, warna sRGB8 + kelas.
   Animasi per jenis kelamin (kerangka 62 tulang dibagi semua karakter satu jenis kelamin): klip dicuplik 20 fps, matriks kulit akhir per tulang
   sebagai kuaternion int16 (x 32767) + translasi int16 (x 8192, meter) + 1 pad; posisi pergelangan tangan kiri per frame (untuk payung);
   klip buatan sendiri: Duduk, Jalan_Payung, Diam_Payung, Duduk_Payung (sudut tulang ditimpa di ruang dunia, tinggi pinggul diselesaikan otomatis).
   Rumus kulit di game: titik_dunia = jumlah(bobot_j x (R(q_j) x posisi + t_j)), posisi = posisi bind (meter).

   Pakai:  THREE_LOCAL=<folder node_modules/three> MESHOPT_LOCAL=<folder node_modules/meshoptimizer> \
           node tools/siapkan_orang.mjs --men <folder GLB pria> --women <folder GLB wanita> [--out berkas.js] [--json laporan.json]
   (atau `npm i three@0.186.1 meshoptimizer` di folder kerja dan jalankan dari sana; Node >= 20). Berkas sumber GLB tidak di dalam repo. */
import fs from 'node:fs';
import path from 'node:path';
import { register } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const MEN = arg('men'), WOMEN = arg('women');
const OUT = arg('out', path.join(ROOT, 'experiences/cooper-station/assets/orang.data.js')), JSON_OUT = arg('json');
if (!MEN || !WOMEN) { console.error('Pakai: node tools/siapkan_orang.mjs --men <folder> --women <folder> [--out ...] [--json ...]'); process.exit(2); }

// three: bare import 'three' dipetakan ke THREE_LOCAL agar GLTFLoader (addon) berjalan di Node
const local = process.env.THREE_LOCAL;
const threeUrl = local ? pathToFileURL(path.join(local, 'build/three.module.js')).href : null;
if (threeUrl) register('data:text/javascript,' + encodeURIComponent(`export async function resolve(s,c,n){ if(s==='three') return {url:${JSON.stringify(threeUrl)},shortCircuit:true}; return n(s,c); }`));
const THREE = await import(threeUrl || 'three');
const { GLTFLoader } = await import(local ? pathToFileURL(path.join(local, 'examples/jsm/loaders/GLTFLoader.js')).href : 'three/addons/loaders/GLTFLoader.js');
const MO = process.env.MESHOPT_LOCAL ? await import(pathToFileURL(path.join(process.env.MESHOPT_LOCAL, 'meshopt_simplifier.js')).href) : await import('meshoptimizer');
const Simp = MO.MeshoptSimplifier; await Simp.ready;

// ---------- pilihan karakter ----------
// recolor: baju dan celana boleh diwarnai ulang dari palet kota; skin / hair: kulit dan rambut dari palet (default true)
const CHARS = [
  { id: 'm_business', g: 'm', file: 'Business Man.glb', recolor: { top: false, bottom: false } },
  { id: 'm_casual', g: 'm', file: 'Casual Character.glb', recolor: { top: true, bottom: true } },
  { id: 'm_hoodie', g: 'm', file: 'Hoodie Character.glb', recolor: { top: true, bottom: true } },
  { id: 'm_farmer', g: 'm', file: 'Farmer.glb', recolor: { top: false, bottom: false } },
  { id: 'm_worker', g: 'm', file: 'Worker.glb', recolor: { top: false, bottom: false } },
  { id: 'm_beach', g: 'm', file: 'Beach Character.glb', recolor: { top: true, bottom: true } },
  { id: 'm_astro', g: 'm', file: 'Astronaut.glb', recolor: { top: false, bottom: false }, skin: false, hair: false },
  { id: 'w_suit', g: 'w', file: 'Suit.glb', recolor: { top: false, bottom: false } },
  { id: 'w_woman_a', g: 'w', file: 'Animated Woman.glb', recolor: { top: true, bottom: true } },
  { id: 'w_woman_b', g: 'w', file: 'Animated Woman-nIItLV9nxS.glb', recolor: { top: true, bottom: true } },
  { id: 'w_worker', g: 'w', file: 'Worker.glb', recolor: { top: false, bottom: false } },
  { id: 'w_adventurer', g: 'w', file: 'Adventurer.glb', recolor: { top: false, bottom: false } },
  { id: 'w_punk', g: 'w', file: 'Punk.glb', recolor: { top: false, bottom: false }, hair: false }
];
const LOD_TRIS = [3000, 700, 160], LOD_ERR = [0.06, 0.2, 0.5];   // segitiga sasaran dan galat relatif maksimum meshoptimizer per tingkat
const FPS = 20;
const AW = (process.env.ATTW || '0.1,0.5,0.1').split(',').map(Number);   // bobot atribut simplifikasi: warna, kelas, bobot tulang
const UMB_A = [0.62, 0.25];   // sudut lengan atas dan bawah memegang payung (rad, ke depan)
const SIT_A = 1.40;   // sudut paha dan betis saat duduk (rad): paha sedikit miring di rangka asli, 1,40 membuat lutut sejajar pinggul
const CLS = { FIXED: 0, SKIN: 1, HAIR: 2, TOP: 3, BOTTOM: 4, SHOE: 5, EYE: 6 };

// ---------- baca GLB ----------
async function loadGLB(file) {
  const b = fs.readFileSync(file), ab = b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength);
  return await new Promise((res, rej) => new GLTFLoader().parse(ab, '', res, rej));
}
function classOf(meshName, matName) {
  const part = (/_(Legs|Feet|Body|Head)(_\d+)?$/.exec(meshName) || [])[1], skin = /^Skin/.test(matName);
  if (part === 'Legs') return skin ? CLS.SKIN : CLS.BOTTOM;
  if (part === 'Feet') return skin ? CLS.SKIN : CLS.SHOE;
  if (part === 'Body') return skin ? CLS.SKIN : CLS.TOP;
  if (part === 'Head') return skin ? CLS.SKIN : /^(Hair|Eyebrows)/.test(matName) ? CLS.HAIR : /^Eye$/.test(matName) ? CLS.EYE : CLS.FIXED;
  return CLS.FIXED;
}
const lin2srgb = (c) => (c <= 0.0031308 ? 12.92 * c : 1.055 * Math.pow(c, 1 / 2.4) - 0.055);
const clamp = (x, a, b) => Math.min(b, Math.max(a, x));

function merge(gltf) {
  gltf.scene.updateMatrixWorld(true);
  const meshes = []; gltf.scene.traverse((o) => { if (o.isSkinnedMesh) meshes.push(o); });
  const sk = meshes[0].skeleton, W = meshes[0].matrixWorld.clone(), nb = sk.bones.length;
  for (const m of meshes) {
    if (m.skeleton.bones.length !== nb || m.skeleton.bones.some((b, i) => b.name !== sk.bones[i].name)) throw new Error('kerangka berbeda antar mesh: ' + m.name);
    if (m.matrixWorld.elements.some((v, i) => Math.abs(v - W.elements[i]) > 0.05)) throw new Error('matriks dunia mesh berbeda: ' + m.name);
  }
  const NM = new THREE.Matrix3().getNormalMatrix(W), v = new THREE.Vector3();
  const P = [], N = [], C = [], J = [], Wt = [], K = [], I = []; let base = 0, mn = [1e9, 1e9, 1e9], mx = [-1e9, -1e9, -1e9];
  for (const m of meshes) {
    const g = m.geometry, pa = g.attributes.position, na = g.attributes.normal, ca = g.attributes.color, ja = g.attributes.skinIndex, wa = g.attributes.skinWeight;
    const mat = m.material, col = mat.color, cl = classOf(m.name, mat.name);
    for (let i = 0; i < pa.count; i++) {
      v.fromBufferAttribute(pa, i).applyMatrix4(W); P.push(v.x, v.y, v.z);
      for (let k = 0; k < 3; k++) { mn[k] = Math.min(mn[k], v.getComponent(k)); mx[k] = Math.max(mx[k], v.getComponent(k)); }
      v.fromBufferAttribute(na, i).applyMatrix3(NM).normalize(); N.push(v.x, v.y, v.z);
      const vc = ca ? [ca.getX(i), ca.getY(i), ca.getZ(i)] : [1, 1, 1];
      C.push(col.r * vc[0], col.g * vc[1], col.b * vc[2]);
      J.push(ja.getX(i), ja.getY(i), ja.getZ(i), ja.getW(i)); Wt.push(wa.getX(i), wa.getY(i), wa.getZ(i), wa.getW(i)); K.push(cl);
    }
    const ix = g.index.array; for (let i = 0; i < ix.length; i++) I.push(base + ix[i]); base += pa.count;
  }
  return { meshes, sk, W, nb, pos: Float32Array.from(P), nrm: Float32Array.from(N), col: Float32Array.from(C), joints: Uint16Array.from(J), weights: Float32Array.from(Wt), cls: Uint8Array.from(K), index: Uint32Array.from(I), mn, mx };
}

// ---------- LOD ----------
function simplify(M, targetTris, targetErr) {
  const nv = M.pos.length / 3, att = new Float32Array(nv * 8);   // warna linear 3 + kelas 1 + bobot 4
  for (let i = 0; i < nv; i++) { att[i * 8] = M.col[i * 3]; att[i * 8 + 1] = M.col[i * 3 + 1]; att[i * 8 + 2] = M.col[i * 3 + 2]; att[i * 8 + 3] = M.cls[i] * 0.2; for (let k = 0; k < 4; k++) att[i * 8 + 4 + k] = M.weights[i * 4 + k]; }
  let idx = M.index, err = 0;
  if (idx.length / 3 > targetTris) [idx, err] = Simp.simplifyWithAttributes(M.index, M.pos, 3, att, 8, [AW[0], AW[0], AW[0], AW[1], AW[2], AW[2], AW[2], AW[2]], null, targetTris * 3, targetErr, ['Permissive']);
  // kompak: titik yang dipakai
  const map = new Int32Array(nv).fill(-1); let n = 0; const used = [];
  for (const i of idx) if (map[i] < 0) { map[i] = n++; used.push(i); }
  const o = { pos: new Float32Array(n * 3), col: new Float32Array(n * 3), joints: new Uint16Array(n * 4), weights: new Float32Array(n * 4), cls: new Uint8Array(n), index: new Uint32Array(idx.length), err };
  used.forEach((s, d) => { for (let k = 0; k < 3; k++) { o.pos[d * 3 + k] = M.pos[s * 3 + k]; o.col[d * 3 + k] = M.col[s * 3 + k]; } for (let k = 0; k < 4; k++) { o.joints[d * 4 + k] = M.joints[s * 4 + k]; o.weights[d * 4 + k] = M.weights[s * 4 + k]; } o.cls[d] = M.cls[s]; });
  for (let i = 0; i < idx.length; i++) o.index[i] = map[idx[i]];
  // normal: rata-rata bobot luas dari segitiga yang memakai titik (titik sudah terbelah menurut tepi keras sumber)
  o.nrm = new Float32Array(n * 3);
  for (let t = 0; t < o.index.length; t += 3) {
    const a = o.index[t] * 3, b = o.index[t + 1] * 3, c = o.index[t + 2] * 3, p = o.pos;
    const ux = p[b] - p[a], uy = p[b + 1] - p[a + 1], uz = p[b + 2] - p[a + 2], vx = p[c] - p[a], vy = p[c + 1] - p[a + 1], vz = p[c + 2] - p[a + 2];
    const x = uy * vz - uz * vy, y = uz * vx - ux * vz, z = ux * vy - uy * vx;
    for (const k of [a, b, c]) { o.nrm[k] += x; o.nrm[k + 1] += y; o.nrm[k + 2] += z; }
  }
  for (let i = 0; i < n; i++) { const l = Math.hypot(o.nrm[3 * i], o.nrm[3 * i + 1], o.nrm[3 * i + 2]); if (l > 1e-12) { o.nrm[3 * i] /= l; o.nrm[3 * i + 1] /= l; o.nrm[3 * i + 2] /= l; } else { o.nrm[3 * i + 1] = 1; } }
  return o;
}

// ---------- pengemasan ----------
class Blob {
  constructor() { this.parts = []; this.size = 0; }
  add(typed) { if (this.size % 4) { const pad = 4 - this.size % 4; this.parts.push(new Uint8Array(pad)); this.size += pad; } const off = this.size; const u8 = new Uint8Array(typed.buffer, typed.byteOffset, typed.byteLength); this.parts.push(u8); this.size += u8.length; return off; }
  concat() { const out = new Uint8Array(this.size); let o = 0; for (const p of this.parts) { out.set(p, o); o += p.length; } return out; }
}
function packLod(blob, L, bb) {
  const n = L.pos.length / 3, q = new Uint16Array(n * 3), nr = new Int8Array(n * 3), jt = new Uint8Array(n * 4), wt = new Uint8Array(n * 4), cc = new Uint8Array(n * 4);
  const range = [0, 1, 2].map((k) => Math.max(1e-6, bb.max[k] - bb.min[k]));
  for (let i = 0; i < n; i++) {
    for (let k = 0; k < 3; k++) { q[i * 3 + k] = clamp(Math.round((L.pos[i * 3 + k] - bb.min[k]) / range[k] * 65535), 0, 65535); nr[i * 3 + k] = clamp(Math.round(L.nrm[i * 3 + k] * 127), -127, 127); cc[i * 4 + k] = clamp(Math.round(lin2srgb(clamp(L.col[i * 3 + k], 0, 1)) * 255), 0, 255); }
    cc[i * 4 + 3] = L.cls[i];
    let s = 0; for (let k = 0; k < 4; k++) s += L.weights[i * 4 + k]; const w8 = [0, 0, 0, 0]; let acc = 0;
    for (let k = 0; k < 4; k++) { w8[k] = s > 1e-9 ? Math.round(L.weights[i * 4 + k] / s * 255) : 0; acc += w8[k]; jt[i * 4 + k] = L.joints[i * 4 + k]; }
    if (s <= 1e-9) w8[0] = 255; else w8[w8.indexOf(Math.max(...w8))] += 255 - acc;
    for (let k = 0; k < 4; k++) wt[i * 4 + k] = w8[k];
  }
  const idx = Uint16Array.from(L.index);
  return { nv: n, nt: idx.length / 3, pos: blob.add(q), nrm: blob.add(nr), jnt: blob.add(jt), wgt: blob.add(wt), col: blob.add(cc), idx: blob.add(idx), err: +L.err.toFixed(5) };
}

// ---------- animasi ----------
const X = new THREE.Vector3(1, 0, 0);
function rotWorld(bone, ang) {
  bone.updateWorldMatrix(true, false);
  const pq = bone.parent.getWorldQuaternion(new THREE.Quaternion()), wq = bone.getWorldQuaternion(new THREE.Quaternion());
  const nq = new THREE.Quaternion().setFromAxisAngle(X, ang).multiply(wq);
  bone.quaternion.copy(pq.invert().multiply(nq)); bone.updateWorldMatrix(false, true);
}
function moveWorld(bone, d) {
  bone.updateWorldMatrix(true, false);
  const p = bone.getWorldPosition(new THREE.Vector3()).add(d); bone.parent.worldToLocal(p); bone.position.copy(p); bone.updateWorldMatrix(false, true);
}
const byName = (sk, n) => sk.bones.find((b) => b.name === n.replace('.', ''));   // GLTFLoader tidak mempertahankan titik di nama tulang

function bakeAnimations(gltf, M) {
  const { sk, W } = M, nb = M.nb, root = gltf.scene, mixer = new THREE.AnimationMixer(root), Winv = W.clone().invert();
  const clip = (n) => THREE.AnimationClip.findByName(gltf.animations, 'CharacterArmature|' + n);
  const sm = M.meshes[0], tmp = new THREE.Matrix4(), mm = new THREE.Matrix4(), pp = new THREE.Vector3(), qq = new THREE.Quaternion(), ss = new THREE.Vector3();
  const wristL = byName(sk, 'Wrist.L'), footL = byName(sk, 'Foot.L'), footR = byName(sk, 'Foot.R');
  const ULL = byName(sk, 'UpperLeg.L'), ULR = byName(sk, 'UpperLeg.R'), LLL = byName(sk, 'LowerLeg.L'), LLR = byName(sk, 'LowerLeg.R'), hips = byName(sk, 'Hips');
  const UAL = byName(sk, 'UpperArm.L'), UAR = byName(sk, 'UpperArm.R'), LAL = byName(sk, 'LowerArm.L'), LAR = byName(sk, 'LowerArm.R');
  let maxScaleErr = 0;
  // pose diam semua tulang: dikembalikan sebelum tiap cuplikan (tulang tanpa trek animasi tidak boleh menyimpan timpaan frame sebelumnya)
  const restPose = sk.bones.map((b) => ({ p: b.position.clone(), q: b.quaternion.clone(), s: b.scale.clone() }));
  const restore = () => { sk.bones.forEach((b, i) => { b.position.copy(restPose[i].p); b.quaternion.copy(restPose[i].q); b.scale.copy(restPose[i].s); }); };
  const frames = [], hand = [];
  // sample: nama klip sumber, jumlah frame, modifikasi (sit, umb)
  function sample(src, mod, sitDy) {
    const c = clip(src), n = Math.max(2, Math.round(c.duration * FPS)), act = mixer.clipAction(c), out = [], h = [];
    act.reset().play();
    for (let i = 0; i < n; i++) {
      restore(); mixer.setTime(i * c.duration / n); root.updateMatrixWorld(true);
      if (mod) mod(sitDy);
      root.updateMatrixWorld(true); sk.update();
      const fr = new Float32Array(nb * 7);
      for (let j = 0; j < nb; j++) {
        tmp.fromArray(sk.boneMatrices, j * 16);
        mm.copy(sm.matrixWorld).multiply(sm.bindMatrixInverse).multiply(tmp).multiply(sm.bindMatrix).multiply(Winv);
        mm.decompose(pp, qq, ss); maxScaleErr = Math.max(maxScaleErr, Math.abs(ss.x - 1), Math.abs(ss.y - 1), Math.abs(ss.z - 1));
        if (![qq.x, qq.y, qq.z, qq.w, pp.x, pp.y, pp.z].every(Number.isFinite)) throw new Error(`nilai tidak valid: klip ${src} frame ${i} tulang ${sk.bones[j].name}`);
        if (qq.w < 0) qq.set(-qq.x, -qq.y, -qq.z, -qq.w);
        fr.set([qq.x, qq.y, qq.z, qq.w, pp.x, pp.y, pp.z], j * 7);
      }
      out.push(fr); const wp = wristL.getWorldPosition(new THREE.Vector3()); h.push([wp.x, wp.y, wp.z]);
    }
    act.stop(); return { out, h, dur: c.duration, n };
  }
  // Foot.L / Foot.R / PT.L / PT.R adalah tulang gaya IK (induknya Root, bukan betis): saat duduk pergelangan dipindah ke ujung betis yang baru
  const body = byName(sk, 'Body'), PTL = byName(sk, 'PT.L'), PTR = byName(sk, 'PT.R'), vv = new THREE.Vector3();
  const sitMod = (dy) => {
    const legs = [[ULL, LLL, footL, PTL], [ULR, LLR, footR, PTR]], loc = legs.map(([, ll, ft]) => ll.worldToLocal(ft.getWorldPosition(new THREE.Vector3()))), idle = legs.map(([, , ft, pt]) => [ft.getWorldPosition(new THREE.Vector3()), pt.getWorldPosition(new THREE.Vector3())]);
    for (const [ul, ll] of legs) { rotWorld(ul, -SIT_A); rotWorld(ll, SIT_A); }
    for (const [b, a] of [[UAL, -0.35], [UAR, -0.35]]) rotWorld(b, a);
    for (const [b, a] of [[LAL, -0.5], [LAR, -0.5]]) rotWorld(b, a);
    moveWorld(body, new THREE.Vector3(0, dy, 0));   // paha adalah anak Body (bukan Hips): geser Body agar seluruh tubuh turun
    legs.forEach(([, ll, ft, pt], i) => {
      ll.updateWorldMatrix(true, false); const ank = ll.localToWorld(loc[i].clone());
      moveWorld(ft, vv.copy(ank).sub(idle[i][0])); moveWorld(pt, vv.copy(ank).sub(idle[i][0]));
    });
  };
  sitMod.solve = () => {   // dy: pergelangan hasil rotasi paha dan betis kembali ke tinggi pergelangan berdiri
    const loc = footL.parent && LLL.worldToLocal(footL.getWorldPosition(new THREE.Vector3())), y0 = footL.getWorldPosition(new THREE.Vector3()).y;
    rotWorld(ULL, -SIT_A); rotWorld(LLL, SIT_A); LLL.updateWorldMatrix(true, false);
    return y0 - LLL.localToWorld(loc.clone()).y;
  };
  // lengan kiri memegang payung: lengan dikunci ke pose menggantung Idle_Neutral frame 0 (tidak ikut ayunan jalan), lalu diputar maju di ruang dunia
  const armQ = {};
  const lockArm = () => { UAL.quaternion.copy(armQ.ua); LAL.quaternion.copy(armQ.la); UAL.updateWorldMatrix(false, true); };
  const umbMod = () => { lockArm(); rotWorld(UAL, -UMB_A[0]); rotWorld(LAL, -UMB_A[1]); };
  // tinggi pinggul duduk: pergelangan menapak di tinggi yang sama dengan berdiri (Idle_Neutral frame 0)
  restore(); mixer.clipAction(clip('Idle_Neutral')).reset().play(); mixer.setTime(0); root.updateMatrixWorld(true);
  armQ.ua = UAL.quaternion.clone(); armQ.la = LAL.quaternion.clone();
  const hipY0 = hips.getWorldPosition(new THREE.Vector3()).y, dy = sitMod.solve();
  mixer.stopAllAction();
  const defs = [['Jalan', 'Walk', null], ['Diam', 'Idle_Neutral', null], ['Lambai', 'Wave', null], ['Interaksi', 'Interact', null], ['Duduk', 'Idle_Neutral', () => sitMod(dy)],
    ['Jalan_Payung', 'Walk', umbMod], ['Diam_Payung', 'Idle_Neutral', umbMod], ['Duduk_Payung', 'Idle_Neutral', () => { sitMod(dy); lockArm(); rotWorld(UAL, -UMB_A[0] * 0.8); rotWorld(LAL, -UMB_A[1] * 0.8); }]];
  const clips = [], F = [], H = []; let off = 0;
  for (const [name, src, mod] of defs) {
    mixer.stopAllAction(); const r = sample(src, mod ? () => mod(dy) : null, dy);
    clips.push({ name, src, frames: r.n, dur: +r.dur.toFixed(3), start: off }); off += r.n; F.push(...r.out); H.push(...r.h);
  }
  // panjang langkah Walk: kecepatan kaki tumpu (z dunia) dari rata-rata kecepatan titik terendah
  const walk = clips[0]; mixer.stopAllAction(); const wc = clip('Walk'), wa = mixer.clipAction(wc); wa.reset().play();
  let sumv = 0, cnt = 0, prev = null; const N = walk.frames;
  for (let i = 0; i <= N; i++) { mixer.setTime(i / N * wc.duration); root.updateMatrixWorld(true);
    const pl = footL.getWorldPosition(new THREE.Vector3()), pr = footR.getWorldPosition(new THREE.Vector3()); const st = pl.y < pr.y ? ['L', pl] : ['R', pr];
    if (prev && prev[0] === st[0]) { sumv += (prev[1].z - st[1].z) / (wc.duration / N); cnt++; } prev = st; }
  wa.stop();
  const walkSpeed = cnt ? sumv / cnt : 0;
  const hr0 = (ci) => { const c = clips[ci]; let m = [0, 0, 0], lo = [1e9, 1e9, 1e9], hi = [-1e9, -1e9, -1e9]; for (let f = 0; f < c.frames; f++) for (let k = 0; k < 3; k++) { const v = H[c.start + f][k]; m[k] += v / c.frames; lo[k] = Math.min(lo[k], v); hi[k] = Math.max(hi[k], v); } return { mean: m.map((v) => +v.toFixed(3)), span: lo.map((v, k) => +(hi[k] - v).toFixed(3)) }; };
  const handStat = { Jalan_Payung: hr0(5), Diam_Payung: hr0(6), Duduk_Payung: hr0(7) };
  // kuantisasi: q int16 x 32767, t int16 x 8192, 8 int16 per tulang per frame (pad)
  const data = new Int16Array(F.length * nb * 8);
  F.forEach((fr, f) => { for (let j = 0; j < nb; j++) { const o = (f * nb + j) * 8; for (let k = 0; k < 4; k++) data[o + k] = clamp(Math.round(fr[j * 7 + k] * 32767), -32767, 32767); for (let k = 0; k < 3; k++) data[o + 4 + k] = clamp(Math.round(fr[j * 7 + 4 + k] * 8192), -32767, 32767); } });
  const hd = new Int16Array(H.length * 4); H.forEach((p, i) => { for (let k = 0; k < 3; k++) hd[i * 4 + k] = clamp(Math.round(p[k] * 8192), -32767, 32767); });
  return { clips, data, hand: hd, bones: sk.bones.map((b) => b.name), nb, fps: FPS, handStat, sitDy: +dy.toFixed(4), hipY0: +hipY0.toFixed(4), walkSpeed: +walkSpeed.toFixed(4), strideM: +(walkSpeed * walk.dur).toFixed(3), maxScaleErr: +maxScaleErr.toExponential(2), frames: F.length };
}

// ---------- jalan ----------
const blob = new Blob(), meta = { chars: [], anim: {}, lodTris: LOD_TRIS, fps: FPS, cls: CLS }, report = [];
const animDone = {};
for (const cfg of CHARS) {
  const file = path.join(cfg.g === 'm' ? MEN : WOMEN, cfg.file);
  const gltf = await loadGLB(file), M = merge(gltf);
  const bb = { min: M.mn, max: M.mx };
  const lods = LOD_TRIS.map((t, i) => simplify(M, t, LOD_ERR[i])), packed = lods.map((L) => packLod(blob, L, bb));
  // kecerahan rata-rata per kelas (untuk warna ulang: warna palet x kecerahan titik / rata-rata)
  const lum = new Array(7).fill(0), cn = new Array(7).fill(0);
  for (let i = 0; i < M.cls.length; i++) { const l = 0.2126 * M.col[i * 3] + 0.7152 * M.col[i * 3 + 1] + 0.0722 * M.col[i * 3 + 2]; lum[M.cls[i]] += l; cn[M.cls[i]]++; }
  const lumAvg = lum.map((s, k) => +(cn[k] ? s / cn[k] : 0).toFixed(4));
  meta.chars.push({ id: cfg.id, g: cfg.g, file: cfg.file, recolor: { top: !!cfg.recolor.top, bottom: !!cfg.recolor.bottom, skin: cfg.skin !== false, hair: cfg.hair !== false }, bbox: { min: bb.min.map((v) => +v.toFixed(5)), max: bb.max.map((v) => +v.toFixed(5)) }, height: +(bb.max[1] - bb.min[1]).toFixed(3), lum: lumAvg, src: { tris: M.index.length / 3, verts: M.pos.length / 3 }, lods: packed });
  report.push(`${cfg.id}: sumber ${M.index.length / 3} segitiga -> ${packed.map((p) => p.nt + '/' + p.nv).join(' | ')} (galat meshopt ${packed.map((p) => p.err).join(', ')}), tinggi ${(bb.max[1] - bb.min[1]).toFixed(2)} m`);
  if (!animDone[cfg.g]) { animDone[cfg.g] = true; const A = bakeAnimations(gltf, M);
    meta.anim[cfg.g] = { handStat: A.handStat, bones: A.bones, nb: A.nb, fps: A.fps, clips: A.clips, frames: A.frames, sitDy: A.sitDy, hipY0: A.hipY0, walkSpeed: A.walkSpeed, strideM: A.strideM, maxScaleErr: A.maxScaleErr, data: blob.add(A.data), hand: blob.add(A.hand) };
    report.push(`tangan payung ${cfg.g}: ${JSON.stringify(A.handStat)}`); report.push(`anim ${cfg.g}: ${A.clips.map((c) => c.name + ' ' + c.frames + 'f').join(', ')}; tinggi pinggul duduk ${A.sitDy} m (lama -0,38); langkah ${A.walkSpeed} m/s, ${A.strideM} m per siklus; galat skala tulang ${A.maxScaleErr}`);
  }
  console.log(report[report.length - 1].startsWith('anim') ? report.slice(-2).join('\n') : report[report.length - 1]);
}
const bytes = blob.concat(); meta.blobBytes = bytes.length;
const b64 = Buffer.from(bytes).toString('base64');
const header = '/* Dibuat oleh tools/siapkan_orang.mjs. Model: "Ultimate Modular Men Pack" dan "Ultimate Modular Women Pack" oleh Quaternius (https://quaternius.com), via Poly Pizza (https://poly.pizza), lisensi CC BY / CC0, atribusi wajib (lihat assets/KREDIT.md). Jangan diedit tangan. */\n';
fs.writeFileSync(OUT, header + 'window.ORANG_DATA = ' + JSON.stringify({ v: 1, meta, blob: b64 }) + ';\n');
console.log(`\nTulis ${path.relative(ROOT, OUT)}: ${(fs.statSync(OUT).size / 1e6).toFixed(2)} MB (biner ${(bytes.length / 1e6).toFixed(2)} MB)`);
if (JSON_OUT) fs.writeFileSync(JSON_OUT, JSON.stringify({ meta, report }, null, 1));
