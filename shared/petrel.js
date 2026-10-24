/* PR-11 Petrel (konsep docs/app/konsep-petrel-pr11.md, blokout docs/app/kestrel/blokout-petrel-pr11.html): wahana dua awak,
   putih krem lapuk dengan karat jingga dan garis salem. Badan panah (delta), dua pod samping panjang, dek lebar berpanel, dua blok
   saluran masuk, dua blok pendorong terpisah di belakang, tiang antena punggung, 3 kaki + tangga, 4 kipas angkat di perut pod.
   Skrip biasa (bukan modul ES): memasang window.PETREL. Butuh window.KESTREL (shared/kestrel.js) untuk mergeColored dan kokpit.
   Keluaran buildPetrel mengikuti buildV5 (geo, glass, legs, PAD_Y, pads, door, nav, nozzles, fans, low, belly, eye, size) sehingga
   kode yang memakai KS-07 v5 bisa memakai Petrel tanpa perubahan bentuk data. Nosel dan kipas berbentuk [x, y, z, radius].
   Konvensi warna shader Millar: kaca = biru lebih besar dari merah dan hijau < 0,1; warna lain tidak boleh memenuhi itu. */
(function () {
  'use strict';
  const RINGS = [[-9.0, 0.3, 0.3, -0.1], [-7.2, 1.0, 0.75, -0.02], [-5.0, 2.2, 1.15, 0.1], [-1.5, 3.4, 1.7, 0.2], [2.0, 4.4, 1.8, 0.15], [5.5, 4.4, 1.8, 0.15], [7.0, 3.6, 1.5, 0.1]];
  const COCKPIT_DZ = -1.45;               // kokpit v5 digeser ke depan: pelapis dan sumbu kaca v5 (z -3,55..-0,15) jatuh di z -5,0..-1,6
  function petrelAt(z) {                  // penampang badan di z (lebar, tinggi, pusat y), garis lurus antar cincin
    let k = 0; while (k < RINGS.length - 2 && z > RINGS[k + 1][0]) k++;
    const a = RINGS[k], b = RINGS[k + 1], t = Math.min(1, Math.max(0, (z - a[0]) / (b[0] - a[0])));
    return [a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t, a[3] + (b[3] - a[3]) * t];
  }

  function buildPetrel(THREE) {
    const K = window.KESTREL, PAD_Y = -3.0;
    function oct(w, h, cy = 0, cx = 0, chT = 0.5, chB = 0.3) {   // segi delapan: sudut atas dipotong chT, bawah chB
      const a = w / 2, b = h / 2;
      return [[cx - a + chB, cy - b], [cx + a - chB, cy - b], [cx + a, cy - b + chB], [cx + a, cy + b - chT],
              [cx + a - chT, cy + b], [cx - a + chT, cy + b], [cx - a, cy + b - chT], [cx - a, cy - b + chB]];
    }
    // sisi: 0 bawah, 1 bawah-kanan, 2 kanan, 3 atas-kanan, 4 atas, 5 atas-kiri, 6 kiri, 7 bawah-kiri
    function loft(rings, colorFn, caps = true) {
      const pos = [], col = [];
      const push = (p, c) => { pos.push(...p); col.push(...c); };
      const n = rings[0].pts.length;
      for (let r = 0; r < rings.length - 1; r++) {
        const A = rings[r], B = rings[r + 1];
        for (let i = 0; i < n; i++) {
          const j = (i + 1) % n, c = colorFn(i, r, A.z, B.z);
          const a0 = [A.pts[i][0], A.pts[i][1], A.z], a1 = [A.pts[j][0], A.pts[j][1], A.z], b0 = [B.pts[i][0], B.pts[i][1], B.z], b1 = [B.pts[j][0], B.pts[j][1], B.z];
          push(a0, c); push(a1, c); push(b0, c); push(a1, c); push(b1, c); push(b0, c);   // normal keluar
        }
      }
      if (caps) for (const [R, flip] of [[rings[0], true], [rings[rings.length - 1], false]]) {
        const c = colorFn(-1, -1, R.z, R.z);
        const cx = R.pts.reduce((s, p) => s + p[0], 0) / n, cy = R.pts.reduce((s, p) => s + p[1], 0) / n;
        for (let i = 0; i < n; i++) {
          const j = (i + 1) % n, p0 = [cx, cy, R.z], p1 = [R.pts[i][0], R.pts[i][1], R.z], p2 = [R.pts[j][0], R.pts[j][1], R.z];
          if (flip) { push(p0, c); push(p2, c); push(p1, c); } else { push(p0, c); push(p1, c); push(p2, c); }
        }
      }
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
      g.computeVertexNormals();
      return g;
    }
    const CREAM = [0.62, 0.6, 0.56], CREAM2 = [0.5, 0.49, 0.46], PALE = [0.68, 0.67, 0.64], SALMON = [0.66, 0.36, 0.3], RUST = [0.55, 0.32, 0.14],
          FRAME = [0.12, 0.12, 0.13], BELLY = [0.09, 0.09, 0.1], DARK = [0.07, 0.07, 0.08], METAL = [0.34, 0.35, 0.37], ORANGE = [0.7, 0.3, 0.07],
          GLASS = [0.02, 0.045, 0.085], WARM = [1, 0.85, 0.55];
    const tone = (c, k) => c.map((v) => Math.min(1, v * k));
    const hash = (a, b) => { const s = Math.sin(a * 127.1 + b * 311.7) * 43758.5453; return s - Math.floor(s); };
    function paint(g, c) { g = g.index ? g.toNonIndexed() : g; const n = g.attributes.position.count, a = new Float32Array(n * 3); for (let i = 0; i < n; i++) a.set(c, i * 3); g.setAttribute('color', new THREE.BufferAttribute(a, 3)); if (!g.attributes.normal) g.computeVertexNormals(); return g; }
    const box = (w, h, d, x, y, z, c) => paint(new THREE.BoxGeometry(w, h, d).translate(x, y, z), c);
    function cyl(r0, r1, len, x, y, z, c, axis = 'y', seg = 16, open = false) {
      const g = new THREE.CylinderGeometry(r1, r0, len, seg, 1, open);
      if (axis === 'z') g.rotateX(Math.PI / 2); if (axis === 'x') g.rotateZ(-Math.PI / 2);
      g.translate(x, y, z); return paint(g, c);
    }
    function tilt(g, ax, ang, px, py, pz) { g.translate(-px, -py, -pz); if (ax === 'x') g.rotateX(ang); else if (ax === 'y') g.rotateY(ang); else g.rotateZ(ang); g.translate(px, py, pz); return g; }
    const weather = (base, i, r, seed) => {
      if (i === 0 || i === 1 || i === 7) return BELLY;
      const h = hash(i + seed, r * 1.7);
      return h > 0.86 ? tone(RUST, 0.8 + 0.4 * hash(r, i)) : tone(base, 0.9 + 0.14 * h);
    };
    const SYM = [-1, 1], parts = [];
    const POD_R = [[-8.4, 0.25, 0.25], [-7.0, 1.0, 0.9], [-4.4, 1.9, 1.7], [-1.6, 2.6, 2.2], [2.4, 2.8, 2.3], [4.6, 2.2, 1.9]];
    const podTop = (z) => { let k = 0; while (k < POD_R.length - 2 && z > POD_R[k + 1][0]) k++; const a = POD_R[k], b = POD_R[k + 1], u = Math.min(1, Math.max(0, (z - a[0]) / (b[0] - a[0]))); return -0.1 + (a[2] + (b[2] - a[2]) * u) / 2; };   // puncak pod di z
    const F = (w, h, cy) => oct(w, h, cy, 0, Math.min(0.45, w * 0.3), Math.min(0.35, w * 0.3));

    // ---------- 1. badan panah: hidung runcing, melebar ke belakang; atap kaca di atas kokpit (z -5,0..-2,0) ----------
    {
      const zs = RINGS.map((q) => q[0]), rings = [];
      for (let k = 0; k < zs.length - 1; k++) { const n = Math.max(1, Math.ceil((zs[k + 1] - zs[k]) / 1.0)); for (let j = 0; j < n; j++) { const z = zs[k] + (zs[k + 1] - zs[k]) * j / n; rings.push({ z, pts: F(...petrelAt(z)) }); } }
      rings.push({ z: zs[zs.length - 1], pts: F(...petrelAt(zs[zs.length - 1])) });
      parts.push(loft(rings, (i, r, z0, z1) => { const zm = (z0 + z1) / 2;
        return i < 0 ? FRAME : zm > -5.0 && zm < -2.0 && (i === 3 || i === 4 || i === 5) ? GLASS : weather(CREAM, i, Math.floor((zm + 10) / 1.5), 2); }));
      parts.push(box(0.14, 0.14, 1.6, 0, -0.1, -9.6, METAL));                    // lembing hidung
      // revisi Bhakti: garis salem dan bilah punggung yang melayang di atas badan dihapus
      // revisi Bhakti: kubah kanopi dan rangkanya dihapus; atap kokpit = satu bidang kaca datar (sisi atas badan z -5,0..-2,0 berwarna kaca)
      parts.push(box(1.2, 0.04, 0.5, 0, 1.03, -0.7, FRAME));                     // kisi dan pintu dermaga di belakang kokpit
      for (let k = 0; k < 4; k++) parts.push(box(1.1, 0.04, 0.1, 0, 1.07, -1.0 + k * 0.28 + 0.9, METAL));
      parts.push(box(1.1, 0.04, 0.5, 0, 1.06, 1.45, SALMON));
    }
    // ---------- 2. dek: pelat delta lebar dengan ceruk panel gelap, garis salem, noda karat ----------
    for (const sx of SYM) {
      const sh = new THREE.Shape([[1.1, -5.2], [4.5, -1.4], [4.5, 5.6], [2.8, 7.2], [1.1, 7.2]].map(([x, z]) => new THREE.Vector2(x, z)));
      const d = new THREE.ExtrudeGeometry(sh, { depth: 0.34, bevelEnabled: true, bevelThickness: 0.04, bevelSize: 0.04, bevelSegments: 1 }); d.rotateX(Math.PI / 2);
      if (sx < 0) { d.scale(-1, 1, 1); const q = d.index ? d.index.array : null, P = d.attributes; if (q) for (let k = 0; k < q.length; k += 3) [q[k + 1], q[k + 2]] = [q[k + 2], q[k + 1]]; else for (const nm of ['position', 'normal', 'uv']) { const A = P[nm].array, dd = P[nm].itemSize; for (let k = 0; k < A.length; k += 3 * dd) for (let e = 0; e < dd; e++) [A[k + dd + e], A[k + 2 * dd + e]] = [A[k + 2 * dd + e], A[k + dd + e]]; } }
      d.translate(0, 0.14, 0); parts.push(paint(d, tone(CREAM2, 1.03)));
      for (let k = 0; k < 7; k++) {
        const z = -0.6 + k * 1.05, x = sx * (2.0 + 1.7 * hash(k, 3 * sx)), w = 0.7 + 0.8 * hash(k, 9), d2 = 0.5 + 0.5 * hash(k + 4, 2);
        if (Math.abs(x) > 3.4 && z > -0.2 && z < 2.8) continue;                      // ruang untuk blok saluran masuk
        parts.push(tilt(box(w, 0.03, d2, x, 0.145, z, k % 3 ? FRAME : tone(CREAM, 0.55)), 'y', sx * 0.35 * (k % 2 ? 1 : -1), x, 0.145, z));
      }
      parts.push(box(2.6, 0.03, 0.2, sx * 2.9, 0.15, 4.4, SALMON), tilt(box(2.2, 0.03, 0.18, sx * 2.3, 0.15, -2.2, SALMON), 'y', sx * 0.7, sx * 2.3, 0.15, -2.2));
      for (let k = 0; k < 5; k++) parts.push(box(0.5 + 0.7 * hash(k, 21), 0.025, 0.4 + 0.5 * hash(k, 22), sx * (1.6 + 2.6 * hash(k, 23)), 0.155, 3.8 + 3 * hash(k, 24) - 3.6 * (k % 2), RUST));   // noda karat
      parts.push(box(0.1, 0.22, 0.9, sx * 4.45, 0.0, -0.9, WARM));   // lampu sorot tepi dek (yang di ujung depan dihapus: melayang di luar dek)
    }
    // ---------- 3. dua blok saluran masuk di dek (bukaan gelap berbilah menghadap depan) ----------
    for (const sx of SYM) {
      const x = sx * 3.15, z = 1.0;
      parts.push(box(2.1, 1.1, 2.4, x, 0.75, z, tone(CREAM2, 0.98)), box(2.2, 0.12, 2.5, x, 1.34, z, CREAM));
      parts.push(box(1.7, 0.55, 0.1, x, 0.62, z - 1.2, DARK));
      for (let k = 0; k < 3; k++) parts.push(box(1.6, 0.04, 0.12, x, 0.5 + k * 0.14, z - 1.24, METAL));
      parts.push(box(0.04, 0.9, 2.3, x - sx * 1.06, 0.78, z, FRAME), box(0.04, 0.9, 2.3, x + sx * 1.06, 0.78, z, FRAME));
      parts.push(box(0.9, 0.03, 0.9, x, 1.41, z + 0.2, tone(RUST, 0.9)));
    }
    // ---------- 4. dua pod samping: kisi ventilasi, probe ujung, nosel belakang, 2 kipas angkat di perut ----------
    for (const sx of SYM) {
      const X = sx * 5.5;
      const R = POD_R;
      const g = loft(R.map(([z, w, h]) => ({ z, pts: oct(w, h, -0.1, 0, Math.min(0.7, w * 0.3), Math.min(0.6, w * 0.3)) })), (i, r) => (i < 0 ? FRAME : weather(CREAM, i, r, 11 + (sx > 0 ? 5 : 0))));
      g.translate(X, 0, 0); parts.push(g);
      parts.push(box(0.1, 0.1, 1.9, X, -0.1, -9.2, METAL), box(0.12, 0.12, 0.3, X, -0.1, -8.3, SALMON));
      for (const [zc, w, d] of [[-2.3, 1.15, 0.95], [0.5, 1.2, 1.0]]) {
        const yt = podTop(zc);                                                     // ventilasi menempel di permukaan pod (dulu melayang)
        parts.push(box(w * 0.9, 0.06, d, X, yt - 0.01, zc, tone(CREAM2, 0.9)), box(w * 0.8, 0.04, d * 0.85, X, yt + 0.02, zc, DARK));
        for (let k = 0; k < 5; k++) parts.push(box(w * 0.75, 0.03, 0.05, X, yt + 0.045, zc - d * 0.3 + k * d * 0.15, METAL));
      }
      parts.push(box(0.8, 0.04, 0.3, X, podTop(1.9) + 0.0, 1.9, SALMON), box(0.7, 0.04, 0.3, X, podTop(-4.6) + 0.0, -4.6, SALMON));
      parts.push(box(0.4, 0.3, 0.6, X - sx * 0.95, 0.5, -0.9, FRAME), box(0.4, 0.26, 0.5, X - sx * 0.95, 0.5, 2.9, FRAME));
      parts.push(cyl(0.7, 0.95, 0.9, X, -0.1, 5.0, METAL, 'z', 18, true), cyl(0.7, 0.7, 0.05, X, -0.1, 4.6, DARK, 'z', 18));
      const rg = new THREE.TorusGeometry(0.97, 0.06, 6, 20); rg.translate(X, -0.1, 5.44); parts.push(paint(rg, FRAME));
      for (const fz of [-1.2, 3.6]) {                                                // kipas angkat tertanam di perut pod
        const t = new THREE.TorusGeometry(0.62, 0.07, 6, 24); t.rotateX(Math.PI / 2); t.translate(X, -1.26, fz); parts.push(paint(t, FRAME));
        parts.push(cyl(0.6, 0.6, 0.06, X, -1.27, fz, DARK, 'y', 24));
        for (let k = 0; k < 4; k++) parts.push(tilt(box(1.1, 0.03, 0.07, X, -1.24, fz, METAL), 'y', k * Math.PI / 4, X, -1.24, fz));
      }
    }
    // ---------- 5. dua blok pendorong terpisah di belakang (penopang pendek) dan tiang antena punggung ----------
    for (const sx of SYM) {
      const x = sx * 2.0, z = 9.0;
      parts.push(box(1.7, 1.35, 2.0, x, 0.35, z, tone(CREAM2, 1.0)), box(1.8, 0.14, 2.1, x, 1.06, z, CREAM));
      parts.push(box(1.3, 0.7, 0.1, x, 0.3, z + 1.02, DARK));
      for (let k = 0; k < 5; k++) parts.push(box(1.2, 0.04, 0.12, x, 0.1 + k * 0.12, z + 1.06, METAL));
      parts.push(box(0.35, 0.28, 1.4, x * 0.55, 0.15, 7.7, FRAME), box(0.35, 0.28, 1.4, x * 1.3, 0.15, 7.7, FRAME), box(1.5, 0.05, 0.3, x, 0.3, z - 0.95, RUST));
    }
    // antena punggung: cambuk tipis pendek (dulu tiang 4 m berbalok krem)
    parts.push(box(0.3, 0.1, 0.3, 0, 1.05, 5.7, FRAME), cyl(0.03, 0.045, 1.3, 0, 1.7, 5.7, METAL, 'y', 6), box(0.09, 0.09, 0.09, 0, 2.38, 5.7, SALMON));
    const NBODY = parts.length;
    // ---------- 6. kaki pendarat: satu di hidung, dua di bawah pod; tapak lebar untuk air ----------
    for (const [x, z, top] of [[0, -5.6, -0.5], [-5.5, 1.5, -1.2], [5.5, 1.5, -1.2]]) {
      parts.push(cyl(0.12, 0.12, top - (PAD_Y + 0.3), x, (top + PAD_Y + 0.3) / 2, z, [0.78, 0.8, 0.82]), cyl(0.16, 0.16, 0.14, x, top - 0.1, z, RUST));
      parts.push(box(0.7, 0.09, 1.1, x, PAD_Y + 0.045, z, FRAME), tilt(cyl(0.05, 0.05, 1.1, x, top - 0.6, z + 0.4, METAL), 'x', 0.5, x, top - 0.6, z + 0.4));
    }
    // tangga di sisi kiri kokpit (ikut kaki: ditarik saat terbang)
    for (let k = 0; k < 5; k++) parts.push(box(0.5, 0.04, 0.45, -1.74, -0.35 - k * 0.55, -4.6, METAL));
    parts.push(box(0.04, 2.7, 0.04, -1.99, -1.55, -4.8, METAL), box(0.04, 2.7, 0.04, -1.99, -1.55, -4.4, METAL));

    const body = K.mergeColored(THREE, parts.slice(0, NBODY).map((g) => ({ geo: g }))), legs = K.mergeColored(THREE, parts.slice(NBODY).map((g) => ({ geo: g })));
    // lapisan kotor dan gosong per titik: jelaga di belakang nosel dan pendorong, noda aliran, gosong masuk atmosfer di hidung dan ujung pod
    const h3 = (x, y, z) => { const s = Math.sin(x * 12.9898 + y * 78.233 + z * 37.719) * 43758.5453; return s - Math.floor(s); };
    const sm = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
    const lerp3 = (A, B, t) => [A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t, A[2] + (B[2] - A[2]) * t];
    const BLEACH = [0.5, 0.49, 0.47], ASH = [0.27, 0.265, 0.26], SOOT = [0.045, 0.04, 0.04];
    for (const g of [body, legs]) {
      const p = g.attributes.position.array, n = g.attributes.normal.array, c = g.attributes.color.array;
      for (let i = 0; i < p.length; i += 3) {
        const x = p[i], y = p[i + 1], z = p[i + 2], ny = n[i + 1], nz = n[i + 2];
        if (c[i + 2] - c[i] > 0.035 && c[i + 1] < 0.1) continue;                                   // kaca tetap bersih
        let k = 1, warm = 0;
        const soot = Math.max(sm(3.2, 5.4, z) * Math.max(0, 1 - Math.abs(Math.abs(x) - 5.5) / 1.8), sm(8.4, 10.0, z) * Math.max(0, 1 - Math.abs(Math.abs(x) - 2.0) / 1.3));
        k *= 1 - 0.55 * soot; warm += 0.35 * soot * sm(4.9, 5.6, z);
        const streak = h3(Math.floor(x * 3), 1.7, 3.1), fall = sm(-4, 6, z);
        k *= 1 - 0.18 * streak * fall * (ny > 0.3 ? 1 : 0.5);
        k *= 0.9 + 0.2 * h3(Math.floor(x * 2), Math.floor(y * 2), Math.floor(z * 2));
        const base = [c[i] * k + warm * 0.09, c[i + 1] * k + warm * 0.05, c[i + 2] * k + warm * 0.02];
        const hn = sm(7.0, -9.0, z), belly = Math.max(0, -ny), lead = Math.max(0, -nz) * (y < 0.6 ? 1 : 0.4);
        let heat = belly * (0.2 + 0.7 * hn) + lead * (0.3 + 0.5 * hn) + 0.35 * hn * hn * sm(-0.2, -0.9, ny);
        heat = Math.min(1, heat * (0.82 + 0.3 * h3(Math.floor(x * 5), 2.3, Math.floor(z * 0.8))));
        const burnt = heat > 0.72 ? lerp3(ASH, BLEACH, sm(0.72, 0.97, heat)) : heat > 0.44 ? lerp3(SOOT, ASH, sm(0.44, 0.72, heat)) : lerp3(base, SOOT, sm(0.16, 0.44, heat));
        c[i] = burnt[0]; c[i + 1] = burnt[1]; c[i + 2] = burnt[2];
      }
    }
    // kaca dipisah dari badan (dirender satu sisi)
    const isGlass = (c, i) => c[i + 2] - c[i] > 0.035 && c[i + 1] < 0.1;
    const p = body.attributes.position.array, nn = body.attributes.normal.array, cc = body.attributes.color.array, A = [[], [], []], B = [[], [], []];
    for (let i = 0; i < p.length; i += 9) {
      const D = isGlass(cc, i) && isGlass(cc, i + 3) && isGlass(cc, i + 6) ? B : A;
      for (let k = 0; k < 9; k++) { D[0].push(p[i + k]); D[1].push(nn[i + k]); D[2].push(cc[i + k]); }
    }
    const mk = (D) => { const o = new THREE.BufferGeometry(); ['position', 'normal', 'color'].forEach((nm, j) => o.setAttribute(nm, new THREE.Float32BufferAttribute(D[j], 3))); return o; };
    const cockpit = buildCockpitPetrel(THREE);
    return {
      id: 'pr11', geo: mk(A), glass: mk(B), legs, PAD_Y,
      pads: [[0, -5.6], [-5.5, 1.5], [5.5, 1.5]].map(([x, z]) => ({ x, z, r: 0.6 })),
      door: { x: -2.35, y: -1.3, z: -4.6, nx: -1 },
      nav: { red: [-6.4, 0.68, 0.5], green: [6.4, 0.68, 0.5], strobe: [0, 2.5, 5.7] },
      nozzles: [[-5.5, -0.1, 5.47, 0.7], [5.5, -0.1, 5.47, 0.7], [-2.0, 0.3, 10.05, 0.5], [2.0, 0.3, 10.05, 0.5]],
      fans: [[-5.5, -1.3, -1.2, 0.62], [5.5, -1.3, -1.2, 0.62], [-5.5, -1.3, 3.6, 0.62], [5.5, -1.3, 3.6, 0.62]],
      low: [{ x0: -6.9, x1: -4.1, z0: -8.4, z1: 4.6, y: -1.25 }, { x0: 4.1, x1: 6.9, z0: -8.4, z1: 4.6, y: -1.25 }],   // pod: bawahnya di bawah kepala
      belly: -1.25, eye: cockpit.eye, cockpit,
      size: { L: 19, W: 13.8, H: 9.3 },
      fly: { climb: 0.9, fwd: 0.9, acc: 0.8, yawRate: 0.75, spool: 1.2 },                // pengali terhadap CONFIG.fly (inferensi: lebih besar dan berat dari v5, belum diukur)
    };
  }

  /* Kokpit Petrel = kokpit KS-07 v5 (buildCockpitV5, geometri tidak diubah supaya cahaya kanopi di shader tetap cocok) yang diletakkan
     di grup dengan offset COCKPIT_DZ: pelapis jatuh di z -5,0..-1,6 sejajar atap kaca badan Petrel. `eye` sudah dalam koordinat wahana. */
  function buildCockpitPetrel(THREE) {
    const C = window.KESTREL.buildCockpitV5(THREE);
    return Object.assign({}, C, { offset: [0, 0, COCKPIT_DZ], eye: [C.eye[0], C.eye[1], C.eye[2] + COCKPIT_DZ] });
  }

  window.PETREL = { buildPetrel, buildCockpitPetrel, petrelAt, RINGS, COCKPIT_DZ };
})();
