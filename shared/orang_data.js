/* Tahap 28G (docs/cooper-station/rencana-tahap-28-glb-cooper-station.md): pembaca data orang olahan (assets/orang.data.js, dibuat oleh
   tools/siapkan_orang.mjs) dan kulit CPU kembaran vertex shader pejalan kaki. window.ORANGKIT (skrip biasa, tanpa three.js; Node: module.exports).
   decode(D)  -> { chars, anim, cls, fps }  (D = window.ORANG_DATA)
     chars[i] = { id, g ('m' | 'w'), recolor {top, bottom, skin, hair}, lum[7], bbox, height, lods[3] }
     lods[k]  = { nv, nt, pos Float32 (meter, bind), nrm Float32, joints Uint8 x 4, weights Float32 x 4, col Float32 (sRGB 0..1) x 3, cls Uint8, index Uint16 }
     anim[g]  = { nb, bones, clips [{ name, frames, dur, start }], byName, q Float32 (frame x tulang x 7: qx qy qz qw tx ty tz), hand Float32 (frame x 3) }
   skin(lod, A, f0, f1, t, outP, outN)  kulit: titik = jumlah(bobot x (R(q) x posisi + trans)); frame f0 dan f1 (indeks global) dicampur t (nlerp kuaternion)
   Kelas warna (cls): 0 tetap, 1 kulit, 2 rambut, 3 baju atas, 4 celana, 5 sepatu, 6 mata. */
(function () {
  'use strict';
  const CLS = { FIXED: 0, SKIN: 1, HAIR: 2, TOP: 3, BOTTOM: 4, SHOE: 5, EYE: 6 };
  const b64 = (s) => {
    if (typeof Buffer !== 'undefined') { const b = Buffer.from(s, 'base64'); const u = new Uint8Array(b.length); u.set(b); return u; }
    const bin = atob(s), u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return u;
  };
  function decode(D) {
    const bytes = b64(D.blob), buf = bytes.buffer, M = D.meta, ab = (T, off, n) => new T(buf, bytes.byteOffset + off, n);
    const chars = M.chars.map((c) => {
      const bb = c.bbox, range = [0, 1, 2].map((k) => bb.max[k] - bb.min[k]);
      const lods = c.lods.map((L) => {
        const q = ab(Uint16Array, L.pos, L.nv * 3), n8 = ab(Int8Array, L.nrm, L.nv * 3), j = ab(Uint8Array, L.jnt, L.nv * 4), w8 = ab(Uint8Array, L.wgt, L.nv * 4), cc = ab(Uint8Array, L.col, L.nv * 4);
        const pos = new Float32Array(L.nv * 3), nrm = new Float32Array(L.nv * 3), wt = new Float32Array(L.nv * 4), col = new Float32Array(L.nv * 3), cls = new Uint8Array(L.nv);
        for (let i = 0; i < L.nv; i++) {
          for (let k = 0; k < 3; k++) { pos[i * 3 + k] = bb.min[k] + q[i * 3 + k] / 65535 * range[k]; nrm[i * 3 + k] = n8[i * 3 + k] / 127; col[i * 3 + k] = cc[i * 4 + k] / 255; }
          for (let k = 0; k < 4; k++) wt[i * 4 + k] = w8[i * 4 + k] / 255; cls[i] = cc[i * 4 + 3];
        }
        return { nv: L.nv, nt: L.nt, pos, nrm, joints: j, weights: wt, col, cls, index: ab(Uint16Array, L.idx, L.nt * 3), err: L.err };
      });
      return { id: c.id, g: c.g, recolor: c.recolor, lum: c.lum, bbox: bb, height: c.height, lods };
    });
    const anim = {};
    for (const g of Object.keys(M.anim)) {
      const a = M.anim[g], n = a.frames * a.nb, raw = ab(Int16Array, a.data, n * 8), hr = ab(Int16Array, a.hand, a.frames * 4), q = new Float32Array(n * 7), hand = new Float32Array(a.frames * 3);
      for (let i = 0; i < n; i++) { for (let k = 0; k < 4; k++) q[i * 7 + k] = raw[i * 8 + k] / 32767; for (let k = 0; k < 3; k++) q[i * 7 + 4 + k] = raw[i * 8 + 4 + k] / 8192; }
      for (let i = 0; i < a.frames; i++) for (let k = 0; k < 3; k++) hand[i * 3 + k] = hr[i * 4 + k] / 8192;
      const byName = {}; a.clips.forEach((c) => { byName[c.name] = c; });
      anim[g] = { nb: a.nb, bones: a.bones, clips: a.clips, byName, q, hand, frames: a.frames, sitDy: a.sitDy, walkSpeed: a.walkSpeed, strideM: a.strideM, fps: M.fps };
    }
    return { chars, anim, cls: CLS, fps: M.fps, meta: M };
  }
  // satu tulang: matriks dari kuaternion + translasi pada frame f (indeks global), tulang j -> [qx,qy,qz,qw,tx,ty,tz]
  function skin(lod, A, f0, f1, t, outP, outN) {
    const nb = A.nb, Q = A.q, nv = lod.nv, J = lod.joints, W = lod.weights, P = lod.pos, N = lod.nrm, a = (1 - t), b = t;
    const m = new Float32Array(nb * 7);
    for (let j = 0; j < nb; j++) {   // campur nlerp antar frame
      const o0 = (f0 * nb + j) * 7, o1 = (f1 * nb + j) * 7;
      let dot = Q[o0] * Q[o1] + Q[o0 + 1] * Q[o1 + 1] + Q[o0 + 2] * Q[o1 + 2] + Q[o0 + 3] * Q[o1 + 3], s = dot < 0 ? -1 : 1;
      let x = a * Q[o0] + b * s * Q[o1], y = a * Q[o0 + 1] + b * s * Q[o1 + 1], z = a * Q[o0 + 2] + b * s * Q[o1 + 2], w = a * Q[o0 + 3] + b * s * Q[o1 + 3];
      const l = Math.hypot(x, y, z, w) || 1; x /= l; y /= l; z /= l; w /= l;
      m.set([x, y, z, w, a * Q[o0 + 4] + b * Q[o1 + 4], a * Q[o0 + 5] + b * Q[o1 + 5], a * Q[o0 + 6] + b * Q[o1 + 6]], j * 7);
    }
    for (let v = 0; v < nv; v++) {
      const px = P[3 * v], py = P[3 * v + 1], pz = P[3 * v + 2], nx = N[3 * v], ny = N[3 * v + 1], nz = N[3 * v + 2];
      let ox = 0, oy = 0, oz = 0, mx = 0, my = 0, mz = 0;
      for (let k = 0; k < 4; k++) {
        const w = W[4 * v + k]; if (w <= 0) continue;
        const o = J[4 * v + k] * 7, qx = m[o], qy = m[o + 1], qz = m[o + 2], qw = m[o + 3];
        // R(q) x p = p + 2 w (u x p) + 2 u x (u x p)
        let cx = qy * pz - qz * py, cy = qz * px - qx * pz, cz = qx * py - qy * px;
        ox += w * (px + 2 * (qw * cx + qy * cz - qz * cy) + m[o + 4]); oy += w * (py + 2 * (qw * cy + qz * cx - qx * cz) + m[o + 5]); oz += w * (pz + 2 * (qw * cz + qx * cy - qy * cx) + m[o + 6]);
        cx = qy * nz - qz * ny; cy = qz * nx - qx * nz; cz = qx * ny - qy * nx;
        mx += w * (nx + 2 * (qw * cx + qy * cz - qz * cy)); my += w * (ny + 2 * (qw * cy + qz * cx - qx * cz)); mz += w * (nz + 2 * (qw * cz + qx * cy - qy * cx));
      }
      outP[3 * v] = ox; outP[3 * v + 1] = oy; outP[3 * v + 2] = oz;
      const l = Math.hypot(mx, my, mz); if (l > 1e-6) { outN[3 * v] = mx / l; outN[3 * v + 1] = my / l; outN[3 * v + 2] = mz / l; } else { outN[3 * v] = N[3 * v]; outN[3 * v + 1] = N[3 * v + 1]; outN[3 * v + 2] = N[3 * v + 2]; }
    }
  }
  const PAL = {   // palet pejalan kaki di index.html
    shirt: ['#c8413b', '#2f5f9e', '#e8e4d8', '#3d7a4a', '#d9a43a', '#6b4a8a', '#1f2328', '#e07a4f', '#4a90a8', '#b8b2a6', '#8a2d4a', '#f2f0ea', '#556b2f', '#d86f9b'],
    pants: ['#1f2a44', '#2b2b2e', '#5a4a3a', '#6d737a', '#2e4a6b', '#8c7a5c', '#3a3f2e', '#15171a'],
    skin: ['#f1c9a5', '#e0ac85', '#c68863', '#9c6644', '#6e452c', '#f6d8bd'],
    hair: ['#2a1d15', '#4a3020', '#1a1a1a', '#8a6a3a', '#c9a15a', '#6a6a6a']
  };
  const api = { CLS, decode, skin, PAL };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else window.ORANGKIT = api;
})();
