/* =====================================================================
   Shuttle "Kestrel" KS-07: modul bersama pertama (dipakai Copper Corn Station dan Millar's World).
   Desain orisinal: badan pengangkat 24 m (lofted superellipse), sirip miring ganda, 3 mesin.
   Skrip biasa (bukan modul ES) agar jalan dari file://: memasang window.KESTREL.
   Pakai: <script src="../../shared/kestrel.js"></script> sebelum skrip modul, lalu KESTREL.build(THREE).
   Sumbu model: hidung di -z, atas +y, satuan meter. Geometri berwarna per vertex (atribut color), normal selalu ada.
   build() = v1 (badan pengangkat), identik dengan Copper Corn Station tahap 11d (diuji dengan sidik jari atribut); dipakai Copper
   sampai tahap M3e. buildV3() = KS-07 v3 hibrida (disimpan). buildV5() = KS-07 v5 kecil gelap doff, dipakai Millar's World (M3d).
   ===================================================================== */
(function () {
  const TAU = Math.PI * 2;
  // penggabung geometri berwarna (normal dijaga per bagian)
  function mergeColored(THREE, parts) {
    const P = [], N = [], C = [];
    for (const { geo, color } of parts) {
      let g = geo.index ? geo.toNonIndexed() : geo;
      if (!g.attributes.normal) g.computeVertexNormals();
      const p = g.attributes.position.array, n = g.attributes.normal.array, c = g.attributes.color ? g.attributes.color.array : null;
      for (let i = 0; i < p.length; i += 3) {
        P.push(p[i], p[i + 1], p[i + 2]); N.push(n[i], n[i + 1], n[i + 2]);
        if (color) C.push(color[0], color[1], color[2]); else C.push(c[i], c[i + 1], c[i + 2]);
      }
    }
    const out = new THREE.BufferGeometry();
    out.setAttribute('position', new THREE.Float32BufferAttribute(P, 3));
    out.setAttribute('normal', new THREE.Float32BufferAttribute(N, 3));
    out.setAttribute('color', new THREE.Float32BufferAttribute(C, 3));
    return out;
  }
  const L = 24;
  const W = (t) => 0.35 + 7.1 * Math.pow(Math.sin(Math.min(t / 0.8, 1) * Math.PI / 2), 0.75);                           // setengah lebar
  const HT = (t) => t < 0.32 ? 0.35 + 2.05 * Math.sin(t / 0.32 * Math.PI / 2) : 2.4 - 1.3 * Math.pow((t - 0.32) / 0.68, 1.4);   // tinggi atas
  const HB = (t) => 0.3 + 1.25 * Math.pow(Math.sin(Math.min(t / 0.35, 1) * Math.PI / 2), 0.6);                          // dalam perut
  const tAt = (z) => Math.min(1, Math.max(0, (z + L / 2) / L));

  function build(THREE) {
    const bx = (sx, sy, sz, x, y, z) => new THREE.BoxGeometry(sx, sy, sz).translate(x, y, z);
    const cylZ = (r0, r1, len, z, seg = 16, open = false) => new THREE.CylinderGeometry(r1, r0, len, seg, 1, open).rotateX(Math.PI / 2).translate(0, 0, z);   // r0 di -z, r1 di +z
    const NS = 44, NR = 36;
    const pos = [], col = [], idx = [];
    for (let i = 0; i <= NS; i++) {
      const t = i / NS, z = -L / 2 + t * L, w = W(t), ht = HT(t), hb = HB(t);
      for (let j = 0; j < NR; j++) {
        const a = j / NR * TAU, c = Math.cos(a), s = Math.sin(a), n = s >= 0 ? 2.4 : 5;
        const x = w * Math.sign(c) * Math.pow(Math.abs(c), 2 / n), y = (s >= 0 ? ht : hb) * Math.sign(s) * Math.pow(Math.abs(s), 2 / n);
        pos.push(x, y, z);
        let C = [0.88, 0.89, 0.9];
        if (y < -hb * 0.5) C = [0.13, 0.13, 0.14];                                            // perisai panas di perut
        else if (y < 0.1 && y > -0.5 && t > 0.12) C = [0.86, 0.42, 0.1];                      // garis aksen jingga
        else if (t > 0.6 && y > ht * 0.7 && Math.abs(x) < w * 0.25) C = [0.55, 0.58, 0.62];  // panel radiator punggung
        if (t > 0.13 && t < 0.27 && y > ht * 0.5 && Math.abs(x) < w * 0.82 && Math.abs(x) > 0.12) C = [0.04, 0.06, 0.09];   // jendela kokpit
        col.push(...C);
      }
    }
    for (let i = 0; i < NS; i++) for (let j = 0; j < NR; j++) {
      const a = i * NR + j, b = i * NR + (j + 1) % NR, c = (i + 1) * NR + j, d = (i + 1) * NR + (j + 1) % NR;
      idx.push(a, b, c, b, d, c);
    }
    const nose = pos.length / 3; pos.push(0, 0, -L / 2 - 0.35); col.push(0.88, 0.89, 0.9);
    const tail = pos.length / 3; pos.push(0, 0.3, L / 2); col.push(0.2, 0.21, 0.23);
    for (let j = 0; j < NR; j++) { idx.push(nose, (j + 1) % NR, j); idx.push(tail, NS * NR + j, NS * NR + (j + 1) % NR); }
    const hullG = new THREE.BufferGeometry();
    hullG.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); hullG.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
    hullG.setIndex(idx); hullG.computeVertexNormals();
    // sayap pendek (strake) dan sirip
    const wingShape = new THREE.Shape([new THREE.Vector2(0, -2), new THREE.Vector2(3.2, 6), new THREE.Vector2(3.2, 9), new THREE.Vector2(0, 10.5)]);
    const wing = new THREE.ExtrudeGeometry(wingShape, { depth: 0.28, bevelEnabled: false }).rotateX(Math.PI / 2);
    const finShape = new THREE.Shape([new THREE.Vector2(0, 0), new THREE.Vector2(5, 0), new THREE.Vector2(5.8, 3.8), new THREE.Vector2(3.6, 3.8)]);
    const fin = () => new THREE.ExtrudeGeometry(finShape, { depth: 0.24, bevelEnabled: false }).rotateY(-Math.PI / 2);
    const WHITE = [0.88, 0.89, 0.9], DARK = [0.2, 0.21, 0.23], ORANGE = [0.86, 0.42, 0.1];
    const parts = [
      { geo: wing.clone().translate(6.9, -0.75, 1.5), color: WHITE },
      { geo: wing.clone().scale(-1, 1, 1).translate(-6.9, -0.75, 1.5), color: WHITE },
      { geo: fin().rotateZ(-0.38).translate(4.3, 1.0, 6.2), color: WHITE },
      { geo: fin().rotateZ(0.38).translate(-4.05, 1.0, 6.2), color: WHITE },
      { geo: bx(0.3, 0.9, 1.2, 5.3, 3.3, 10.6), color: ORANGE }, { geo: bx(0.3, 0.9, 1.2, -5.3, 3.3, 10.6), color: ORANGE },
      ...[[-2.3, -0.2], [2.3, -0.2], [0, 0.75]].map(([x, y]) => ({ geo: cylZ(0.8, 1.22, 1.9, 12.9, 18, true).translate(x, y, 0), color: [0.3, 0.3, 0.32] })),
      { geo: new THREE.TorusGeometry(0.95, 0.14, 6, 24).rotateX(Math.PI / 2).translate(0, 2.16, 1), color: DARK },
      { geo: bx(1.5, 0.05, 1.5, 0, 2.14, 1), color: [0.35, 0.37, 0.4] },
      ...[-1, 1].flatMap((sx) => [{ geo: bx(0.35, 0.3, 0.6, sx * 2.6, 0.7, -8.6), color: DARK }, { geo: bx(0.35, 0.3, 0.6, sx * 6.2, 0.4, 7.5), color: DARK }]),
    ];
    const partsG = mergeColored(THREE, parts);
    const navG = { red: bx(0.3, 0.2, 0.3, -10.1, -0.9, 9.8), green: bx(0.3, 0.2, 0.3, 10.1, -0.9, 9.8), strobe: bx(0.25, 0.25, 0.25, 0, 2.0, 11.2) };
    const glowG = mergeColored(THREE, [[-2.3, -0.2], [2.3, -0.2], [0, 0.75]].map(([x, y]) => ({ geo: new THREE.CircleGeometry(0.8, 18).translate(x, y, 12.05), color: [1, 1, 1] })));
    return { hullG, partsG, navG, glowG, HT, W, HB, L };
  }

  /* Kaki pendarat (dipakai saat mendarat di permukaan, mis. Millar's World): tiga kaki teleskopik (hidung + dua utama)
     dengan penopang diagonal dan tapak lebar. padDrop = jarak dari sumbu badan ke dasar tapak (m, positif).
     Mengembalikan geometri berwarna + posisi tapak (x, z model, untuk tabrakan dan riak). */
  const GEAR = [{ x: 0, z: -7.2 }, { x: -4.4, z: 5.2 }, { x: 4.4, z: 5.2 }];
  function gear(THREE, padDrop) {
    const METAL = [0.5, 0.52, 0.55], DARK = [0.16, 0.17, 0.18], PAD = [0.26, 0.27, 0.28], YEL = [0.9, 0.62, 0.12];
    const P = [];
    const cyl = (r, x0, y0, z0, x1, y1, z1, seg = 10) => {        // silinder dari titik a ke b
      const a = new THREE.Vector3(x0, y0, z0), b = new THREE.Vector3(x1, y1, z1), d = b.clone().sub(a), len = d.length();
      const g = new THREE.CylinderGeometry(r, r, len, seg);
      g.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.normalize()));
      return g.translate((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2);
    };
    const pads = [];
    for (const { x, z } of GEAR) {
      const t = tAt(z), yTop = -HB(t) * 0.92, yPad = -padDrop, main = x !== 0, rr = main ? 1 : 0.8;
      const yKnee = yTop + (yPad - yTop) * 0.45;
      P.push({ geo: new THREE.BoxGeometry(1.1 * rr, 0.3, 1.5 * rr).translate(x, yTop - 0.1, z), color: DARK });                 // rumah kaki di perut
      P.push({ geo: cyl(0.2 * rr, x, yTop, z, x, yKnee, z), color: METAL });                                                     // tabung atas
      P.push({ geo: cyl(0.13 * rr, x, yKnee, z, x, yPad + 0.35, z), color: [0.78, 0.8, 0.82] });                                 // batang teleskop (krom)
      P.push({ geo: cyl(0.23 * rr, x, yKnee - 0.08, z, x, yKnee + 0.12, z), color: YEL });                                         // kerah peringatan
      const bxOff = main ? Math.sign(x) * -1.6 : 0, bzOff = main ? -1.3 : 1.8;                                                   // penopang diagonal ke badan
      P.push({ geo: cyl(0.08 * rr, x + bxOff, -HB(tAt(z + bzOff)) * 0.9, z + bzOff, x, yKnee + 0.1, z), color: METAL });
      P.push({ geo: new THREE.CylinderGeometry(0.62 * rr, 0.75 * rr, 0.16, 16).translate(x, yPad + 0.08, z), color: PAD });       // tapak lebar
      P.push({ geo: cyl(0.1 * rr, x, yPad + 0.16, z, x, yPad + 0.4, z), color: DARK });                                          // sendi tapak
      pads.push({ x, z, r: 0.75 * rr });
    }
    return { geo: mergeColored(THREE, P), pads };
  }


  /* KS-07 v3 (konsep docs/app/konsep-ks07-v3.md, blokout docs/app/kestrel/blokout-ks07-v3.html): geometri disalin dari blokout.
     Mengembalikan satu geometri berwarna (tanpa indeks, normal datar per sisi) + data untuk experience:
     tapak kaki, pintu, lampu navigasi, kotak tabrakan rendah, ukuran. Titik 0 = sumbu badan; tapak di y = PAD_Y. */
  function buildV3(THREE) {
    const PAD_Y = -4.2;
    function oct(w, h, cy = 0, cx = 0, chT = 0.5, chB = 0.3) {   // segi delapan: sudut atas dipotong chT, bawah chB
      const a = w / 2, b = h / 2;
      return [[cx - a + chB, cy - b], [cx + a - chB, cy - b], [cx + a, cy - b + chB], [cx + a, cy + b - chT],
              [cx + a - chT, cy + b], [cx - a + chT, cy + b], [cx - a, cy + b - chT], [cx - a, cy - b + chB]];
    }
    // sisi segi delapan: 0 bawah, 1 bawah-kanan, 2 kanan, 3 atas-kanan, 4 atas, 5 atas-kiri, 6 kiri, 7 bawah-kiri
    function loft(rings, colorFn, caps = true) {
      const pos = [], col = [];
      const push = (p, c) => { pos.push(...p); col.push(...c); };
      const n = rings[0].pts.length;
      for (let r = 0; r < rings.length - 1; r++) {
        const A = rings[r], B = rings[r + 1];
        for (let i = 0; i < n; i++) {
          const j = (i + 1) % n, c = colorFn(i, r, A.z, B.z);
          const a0 = [A.pts[i][0], A.pts[i][1], A.z], a1 = [A.pts[j][0], A.pts[j][1], A.z], b0 = [B.pts[i][0], B.pts[i][1], B.z], b1 = [B.pts[j][0], B.pts[j][1], B.z];
          push(a0, c); push(b0, c); push(a1, c); push(a1, c); push(b0, c); push(b1, c);
        }
      }
      if (caps) for (const [R, flip] of [[rings[0], true], [rings[rings.length - 1], false]]) {
        const c = colorFn(-1, -1, R.z, R.z);
        const cx = R.pts.reduce((s, p) => s + p[0], 0) / n, cy = R.pts.reduce((s, p) => s + p[1], 0) / n;
        for (let i = 0; i < n; i++) {
          const j = (i + 1) % n, p0 = [cx, cy, R.z], p1 = [R.pts[i][0], R.pts[i][1], R.z], p2 = [R.pts[j][0], R.pts[j][1], R.z];
          if (flip) { push(p0, c); push(p1, c); push(p2, c); } else { push(p0, c); push(p2, c); push(p1, c); }
        }
      }
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
      g.computeVertexNormals();
      return g;
    }
    // warna: dasar abu terang dengan beda nada per panel (kesan lapisan panel dan pelapukan)
    const WHITE = [0.78, 0.79, 0.78], GREY = [0.55, 0.57, 0.58], DARK = [0.16, 0.17, 0.18], BELLY = [0.12, 0.12, 0.13],
          ORANGE = [0.85, 0.36, 0.08], METAL = [0.42, 0.44, 0.46], GLASS = [0.05, 0.07, 0.09], GOLD = [0.72, 0.55, 0.2];
    const tone = (c, k) => c.map((v) => Math.min(1, v * k));
    const hash = (a, b) => { const s = Math.sin(a * 127.1 + b * 311.7) * 43758.5453; return s - Math.floor(s); };
    const hullColor = (i, r) => i === 0 || i === 1 || i === 7 ? BELLY : tone(WHITE, 0.93 + 0.1 * hash(i, r));

    function box(w, h, d, x, y, z, c) { const g = new THREE.BoxGeometry(w, h, d); g.translate(x, y, z); return paint(g, c); }
    function cyl(r0, r1, len, x, y, z, c, axis = 'y', seg = 16, open = false) {
      const g = new THREE.CylinderGeometry(r1, r0, len, seg, 1, open);
      if (axis === 'z') g.rotateX(Math.PI / 2); if (axis === 'x') g.rotateZ(-Math.PI / 2);
      g.translate(x, y, z); return paint(g, c);
    }
    function paint(g, c) { g = g.index ? g.toNonIndexed() : g; const n = g.attributes.position.count, a = new Float32Array(n * 3); for (let i = 0; i < n; i++) a.set(c, i * 3); g.setAttribute('color', new THREE.BufferAttribute(a, 3)); if (!g.attributes.normal) g.computeVertexNormals(); return g; }
    function tilt(g, ax, ang, px, py, pz) { g.translate(-px, -py, -pz); if (ax === 'x') g.rotateX(ang); else if (ax === 'y') g.rotateY(ang); else g.rotateZ(ang); g.translate(px, py, pz); return g; }

    const parts = [];
    const SYM = [-1, 1];
    // palet v3: abu-krem lapuk (sketsa spidol), pelat putih dan aksen jingga, rangka mesin gelap di bawah
    const BEIGE = [0.62, 0.59, 0.54], BEIGE2 = [0.5, 0.48, 0.45], PALE = [0.78, 0.77, 0.74], RUST = [0.5, 0.33, 0.19], FRAME = [0.2, 0.2, 0.21];
    const weather = (base, i, r, seed) => (i === 0 || i === 1 || i === 7 ? FRAME : tone(base, 0.88 + 0.16 * hash(i + seed, r)));
    const seamRing = (pts, z, c = tone(BEIGE, 0.62)) => loft([{ z, pts: pts.map(([x, y]) => [x * 1.01 + (x > 0 ? 0.02 : -0.02), y * 1.01]) }, { z: z + 0.1, pts: pts.map(([x, y]) => [x * 1.01 + (x > 0 ? 0.02 : -0.02), y * 1.01]) }], () => c, false);
    // garis karat tegak (bekas aliran air dan panas)
    const rust = (x, y0, y1, z, w = 0.12) => box(0.02, y1 - y0, w, x, (y0 + y1) / 2, z, RUST);

    // ---------- 1. blok belakang bersegi (sketsa): prisma bersudut potong besar, pusat mesin ----------
    {
      const P = (w, h) => oct(w, h, 0.3, 0, 1.4, 1.05);
      parts.push(loft([{ z: 4.6, pts: P(5.4, 3.5) }, { z: 5.8, pts: P(6.8, 4.4) }, { z: 11.0, pts: P(6.8, 4.4) }, { z: 12.3, pts: P(5.6, 3.5) }],
        (i, r) => (i < 0 ? tone(BEIGE2, 0.85) : weather(BEIGE2, i, r, 11))));
      for (const z of [7.6, 9.4]) parts.push(seamRing(P(6.8, 4.4), z));
      for (const sx of SYM) { parts.push(rust(sx * 3.42, -0.6, 1.3, 6.4), rust(sx * 3.42, -1.0, 0.8, 10.3, 0.08)); }
      // muka belakang: 2 x 2 nosel dalam ceruk gelap
      parts.push(box(4.2, 2.6, 0.12, 0, 0.3, 12.32, FRAME));
      for (const sx of SYM) for (const dy of [-0.55, 0.75]) parts.push(cyl(0.45, 0.62, 0.9, sx * 1.1, 0.3 + dy, 12.8, METAL, 'z', 20, true), cyl(0.45, 0.45, 0.1, sx * 1.1, 0.3 + dy, 12.36, DARK, 'z', 20));
    }
    // ---------- 2. badan tengah (tulang punggung awak) dengan dek bersirip di atas ----------
    {
      const P = (w, h, cy) => oct(w, h, cy, 0, 0.6, 0.4);
      parts.push(loft([{ z: -5.8, pts: P(3.8, 2.7, 0.55) }, { z: 5.2, pts: P(3.8, 2.7, 0.55) }], (i, r) => (i < 0 ? BEIGE2 : weather(PALE, i, r, 3))));
      for (const z of [-3.4, 0.4, 3.0]) parts.push(seamRing(P(3.8, 2.7, 0.55), z));
      for (let k = 0; k < 12; k++) parts.push(box(2.4, 0.12, 0.26, 0, 1.97, -2.9 + k * 0.52, k % 3 ? tone(BEIGE, 0.95) : BEIGE2));   // sirip dek (sketsa)
      for (const sx of SYM) for (let k = 0; k < 6; k++) parts.push(box(0.35, 0.14, 0.34, sx * 1.55, 1.75, -4.8 + k * 0.5, DARK));   // deret ventilasi
    }
    // ---------- 3. kokpit di tengah depan (kaca bersekat banyak) ----------
    {
      const rings = [
        { z: -5.8, pts: oct(3.8, 2.7, 0.55, 0, 0.6, 0.4) },
        { z: -7.4, pts: oct(3.4, 2.5, 0.65, 0, 0.9, 0.4) },
        { z: -9.0, pts: oct(2.8, 1.5, 0.25, 0, 0.55, 0.35) },
        { z: -9.8, pts: oct(1.9, 0.6, 0.0, 0, 0.2, 0.15) },
      ];
      parts.push(loft(rings, (i, r) => {
        if (i < 0) return PALE;
        if (r === 1 && (i === 3 || i === 4 || i === 5)) return GLASS;
        if (r === 0 && (i === 3 || i === 5)) return GLASS;
        return i === 0 || i === 1 || i === 7 ? FRAME : weather(PALE, i, r, 17);
      }));
      for (const x of [-0.55, 0.55]) parts.push(tilt(box(0.07, 0.07, 1.9, x, 1.62, -8.2, PALE), 'x', -0.55, x, 1.9, -7.4));   // sekat kaca
      parts.push(box(2.6, 0.07, 0.07, 0, 1.92, -7.4, PALE));
    }
    // ---------- 4. dua lengan depan (garpu): kabin berjendela di ujung, rangka silang di sisi, batang probe ----------
    const PRONG_X = 3.7;
    for (const sx of SYM) {
      const x = sx * PRONG_X, P = (w, h, cy) => oct(w, h, cy, x, 0.5, 0.35);
      parts.push(loft([{ z: 4.8, pts: P(2.2, 2.3, 0.2) }, { z: -10.8, pts: P(2.2, 2.3, 0.2) }, { z: -11.4, pts: P(2.5, 2.8, 0.35) }, { z: -13.6, pts: P(2.5, 2.8, 0.35) }, { z: -14.2, pts: P(2.0, 2.1, 0.25) }],
        (i, r) => (i < 0 ? tone(BEIGE, 0.9) : r >= 2 ? weather(PALE, i, r, 30 + sx) : weather(BEIGE, i, r, 40 + sx))));
      for (const z of [-6.4, -2.2, 1.6]) parts.push(seamRing(P(2.2, 2.3, 0.2), z));
      parts.push(box(1.5, 0.9, 0.08, x, 0.75, -14.25, GLASS), box(0.08, 0.9, 0.1, x, 0.75, -14.27, PALE));      // jendela kabin depan
      for (const dx of [-0.35, 0.35]) parts.push(cyl(0.07, 0.07, 3.0, x + dx, -0.55, -15.7, DARK, 'z', 8), cyl(0.12, 0.12, 0.4, x + dx, -0.55, -14.3, METAL, 'z', 8));   // batang probe kembar (sketsa)
      // rangka silang di sisi luar (sketsa)
      const ox = x + sx * 1.12;
      for (let k = 0; k < 4; k++) {
        const zc = -9.6 + k * 1.8;
        parts.push(box(0.06, 1.2, 0.08, ox, 0.3, zc - 0.85, FRAME), box(0.06, 0.08, 1.7, ox, 0.9, zc, FRAME), box(0.06, 0.08, 1.7, ox, -0.3, zc, FRAME));
        for (const s of [-1, 1]) parts.push(tilt(box(0.05, 0.07, 2.0, ox, 0.3, zc, FRAME), 'x', s * 0.61, ox, 0.3, zc));
      }
      // baki mesin terbuka di bawah lengan (seperti rangka di foto kedua)
      parts.push(box(1.8, 0.5, 13.0, x, -1.2, -4.2, FRAME));
      for (let k = 0; k < 9; k++) parts.push(cyl(0.22, 0.22, 1.2, x, -1.35, -9.5 + k * 1.35, METAL, 'x', 10));
      parts.push(rust(ox, -0.9, 0.2, -1.2), rust(ox, -0.9, 0.6, 2.6, 0.08));
    }
    // penghubung lengan ke badan tengah + dek angkut di antara ujung garpu
    for (const sx of SYM) parts.push(box(1.6, 1.8, 7.0, sx * 2.35, 0.3, 1.2, tone(BEIGE, 0.95)), box(1.4, 0.9, 5.0, sx * 2.35, -0.9, -8.2, FRAME));
    parts.push(box(5.2, 0.25, 3.6, 0, -1.05, -12.0, PALE), box(5.2, 0.5, 0.2, 0, -1.2, -13.8, FRAME));        // pelat dek putih di antara garpu (foto kedua)
    for (let k = 0; k < 5; k++) parts.push(box(5.0, 0.06, 0.08, 0, -0.9, -13.4 + k * 0.8, DARK));
    // ---------- 5. pendorong cakram di sisi blok belakang (sketsa) + sirip kecil bergaris ----------
    for (const sx of SYM) {
      const x = sx * 3.75;
      parts.push(cyl(1.15, 1.15, 0.7, x, 0.4, 6.9, tone(BEIGE2, 0.95), 'x', 24), cyl(0.75, 0.75, 0.76, x, 0.4, 6.9, FRAME, 'x', 24), cyl(0.3, 0.3, 0.8, x, 0.4, 6.9, METAL, 'x', 12));
      const t = new THREE.TorusGeometry(1.15, 0.1, 6, 24); t.rotateY(Math.PI / 2); t.translate(x + sx * 0.36, 0.4, 6.9); parts.push(paint(t, DARK));
      parts.push(box(0.14, 1.9, 0.7, x - sx * 0.1, 2.3, 6.9, PALE));
      for (let k = 0; k < 5; k++) parts.push(box(0.16, 0.06, 0.5, x - sx * 0.1, 1.65 + k * 0.28, 6.9, DARK));
    }
    // ---------- 6. pelat sayap rendah bersudut di sisi blok belakang (foto kedua) ----------
    for (const sx of SYM) {
      const sh = new THREE.Shape([new THREE.Vector2(0, 0), new THREE.Vector2(2.1, 1.2), new THREE.Vector2(2.1, 4.2), new THREE.Vector2(0, 5.6)]);
      const w = new THREE.ExtrudeGeometry(sh, { depth: 0.2, bevelEnabled: false }); w.rotateX(Math.PI / 2);
      if (sx < 0) w.scale(-1, 1, 1);
      w.translate(sx * 3.35, -1.15, 5.8); parts.push(paint(w, tone(PALE, 0.95)));
      parts.push(box(0.06, 0.1, 3.0, sx * 5.4, -1.2, 8.6, ORANGE));
    }
    // ---------- 7. rangka mesin di perut badan tengah dan blok belakang ----------
    parts.push(box(3.0, 0.6, 9.5, 0, -1.2, 0.0, FRAME), box(4.6, 0.5, 5.6, 0, -2.05, 8.4, FRAME));
    for (let k = 0; k < 7; k++) parts.push(cyl(0.25, 0.25, 2.6, 0, -1.4, -4 + k * 1.3, METAL, 'x', 10));
    // ---------- 8. antena, lampu, RCS ----------
    for (const sx of SYM) {
      parts.push(cyl(0.04, 0.04, 1.6, sx * 1.2, 2.9, 10.2, METAL), box(0.3, 0.3, 0.3, sx * 2.6, 2.55, 11.6, DARK), box(0.3, 0.3, 0.3, sx * 4.6, 1.3, -13.0, DARK));
      parts.push(box(0.5, 0.18, 0.18, sx * PRONG_X, -0.2, -14.3, [1, 0.95, 0.8]));
    }
    // ---------- 9. kaki pendarat: dua di bawah lengan, dua di bawah blok belakang ----------
    for (const [x, z, top] of [[-PRONG_X, -8.2, -1.45], [PRONG_X, -8.2, -1.45], [-2.3, 9.2, -2.3], [2.3, 9.2, -2.3]]) {
      parts.push(cyl(0.24, 0.24, top - (PAD_Y + 0.9), x, (top + PAD_Y + 0.9) / 2, z, [0.78, 0.8, 0.82]), cyl(0.3, 0.3, 0.2, x, top - 0.2, z, ORANGE));
      parts.push(cyl(0.85, 0.95, 0.16, x, PAD_Y + 0.08, z, DARK, 'y', 8), cyl(0.12, 0.12, 0.9, x, PAD_Y + 0.5, z, METAL));
      parts.push(tilt(cyl(0.08, 0.08, 1.8, x, top - 0.8, z + 0.7, METAL), 'x', 0.55, x, top - 0.8, z + 0.7));
    }

    // ---------- pintu awak + tangga di sisi luar lengan kiri (dipakai E naik di Millar) ----------
    {
      const ox = -PRONG_X - 1.13;
      parts.push(box(0.06, 1.8, 1.3, ox, -0.05, 1.0, DARK), box(0.07, 1.6, 1.1, ox - 0.01, -0.05, 1.0, tone(BEIGE, 0.85)), box(0.08, 0.12, 0.2, ox - 0.03, -0.1, 0.6, METAL));
      for (let k = 0; k < 5; k++) parts.push(box(0.45, 0.05, 0.8, ox - 0.3, -1.25 - k * 0.55, 1.0, METAL));
      parts.push(box(0.05, 3.4, 0.05, ox - 0.5, -2.55, 0.58, METAL), box(0.05, 3.4, 0.05, ox - 0.5, -2.55, 1.42, METAL));
    }
    const geo = mergeColored(THREE, parts.map((g) => ({ geo: g })));
    return {
      geo, PAD_Y,
      pads: [[-PRONG_X, -8.2], [PRONG_X, -8.2], [-2.3, 9.2], [2.3, 9.2]].map(([x, z]) => ({ x, z, r: 0.95 })),
      door: { x: -PRONG_X - 1.13, y: -0.05, z: 1.0, nx: -1 },                        // pintu, normal ke luar (-x)
      nav: { red: [-PRONG_X - 1.25, 1.1, -13.4], green: [PRONG_X + 1.25, 1.1, -13.4], strobe: [0, 2.75, 10.6] },
      low: [{ x0: -3.45, x1: 3.45, z0: 4.6, z1: 12.4, y: -2.3 }],                    // bagian rendah (blok belakang): pemain tidak bisa lewat di bawahnya
      belly: -1.5,                                                                    // bawah lengan dan badan tengah (bisa dilewati)
      size: { L: 27.5, W: 9.9, H: 7.5 },
    };
  }

  /* KS-07 v5 (konsep docs/app/konsep-ks07-v5.md, blokout docs/app/kestrel/blokout-ks07-v5.html): wahana kecil satu kursi.
     Warna gelap doff, lalu diberi lapisan kotor dan gosong per titik: jelaga di belakang nosel, gosong masuk atmosfer
     bergradasi (putih pudar di bagian terpanas, abu-abu, lalu jelaga hitam, baru cat), noda aliran memanjang. Kaca bernada biru (penanda kaca di shader: biru > merah).
     Mengembalikan badan dan kaki (termasuk tangga) terpisah (kaki ditarik saat terbang). */
  // penampang badan v5 (z, lebar, tinggi, pusat y): dipakai badan luar dan pelapis kokpit
  const V5_RINGS = [[-6.2, 1.5, 0.45, -0.15], [-5.4, 1.9, 0.7, -0.08], [-2.6, 2.2, 1.2, 0.1], [-0.6, 2.4, 1.6, 0.25], [3.0, 2.4, 1.6, 0.25], [4.6, 2.0, 1.2, 0.2]];
  function v5At(z) {                                                   // penampang badan di z (interpolasi garis lurus)
    const R = V5_RINGS; let k = 0; while (k < R.length - 2 && z > R[k + 1][0]) k++;
    const a = R[k], b = R[k + 1], t = Math.min(1, Math.max(0, (z - a[0]) / (b[0] - a[0])));
    return [a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t, a[3] + (b[3] - a[3]) * t];
  }
  function buildV5(THREE) {
    const PAD_Y = -1.9;
    function oct(w, h, cy = 0, cx = 0, chT = 0.5, chB = 0.3) {   // segi delapan: sudut atas dipotong chT, bawah chB
      const a = w / 2, b = h / 2;
      return [[cx - a + chB, cy - b], [cx + a - chB, cy - b], [cx + a, cy - b + chB], [cx + a, cy + b - chT],
              [cx + a - chT, cy + b], [cx - a + chT, cy + b], [cx - a, cy + b - chT], [cx - a, cy - b + chB]];
    }
    // sisi segi delapan: 0 bawah, 1 bawah-kanan, 2 kanan, 3 atas-kanan, 4 atas, 5 atas-kiri, 6 kiri, 7 bawah-kiri
    function loft(rings, colorFn, caps = true) {
      const pos = [], col = [];
      const push = (p, c) => { pos.push(...p); col.push(...c); };
      const n = rings[0].pts.length;
      for (let r = 0; r < rings.length - 1; r++) {
        const A = rings[r], B = rings[r + 1];
        for (let i = 0; i < n; i++) {
          const j = (i + 1) % n, c = colorFn(i, r, A.z, B.z);
          const a0 = [A.pts[i][0], A.pts[i][1], A.z], a1 = [A.pts[j][0], A.pts[j][1], A.z], b0 = [B.pts[i][0], B.pts[i][1], B.z], b1 = [B.pts[j][0], B.pts[j][1], B.z];
          push(a0, c); push(a1, c); push(b0, c); push(a1, c); push(b1, c); push(b0, c);   // normal keluar (dulu terbalik)
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
    // warna: dasar abu terang dengan beda nada per panel (kesan lapisan panel dan pelapukan)
    const WHITE = [0.3, 0.3, 0.29], GREY = [0.22, 0.22, 0.22], DARK = [0.07, 0.07, 0.075], BELLY = [0.06, 0.06, 0.065],
          ORANGE = [0.4, 0.19, 0.07], METAL = [0.26, 0.26, 0.27], GLASS = [0.02, 0.045, 0.085], GOLD = [0.36, 0.28, 0.12];
    const tone = (c, k) => c.map((v) => Math.min(1, v * k));
    const hash = (a, b) => { const s = Math.sin(a * 127.1 + b * 311.7) * 43758.5453; return s - Math.floor(s); };
    const hullColor = (i, r) => i === 0 || i === 1 || i === 7 ? BELLY : tone(WHITE, 0.93 + 0.1 * hash(i, r));

    function box(w, h, d, x, y, z, c) { const g = new THREE.BoxGeometry(w, h, d); g.translate(x, y, z); return paint(g, c); }
    function cyl(r0, r1, len, x, y, z, c, axis = 'y', seg = 16, open = false) {
      const g = new THREE.CylinderGeometry(r1, r0, len, seg, 1, open);
      if (axis === 'z') g.rotateX(Math.PI / 2); if (axis === 'x') g.rotateZ(-Math.PI / 2);
      g.translate(x, y, z); return paint(g, c);
    }
    function paint(g, c) { g = g.index ? g.toNonIndexed() : g; const n = g.attributes.position.count, a = new Float32Array(n * 3); for (let i = 0; i < n; i++) a.set(c, i * 3); g.setAttribute('color', new THREE.BufferAttribute(a, 3)); if (!g.attributes.normal) g.computeVertexNormals(); return g; }
    function tilt(g, ax, ang, px, py, pz) { g.translate(-px, -py, -pz); if (ax === 'x') g.rotateX(ang); else if (ax === 'y') g.rotateY(ang); else g.rotateZ(ang); g.translate(px, py, pz); return g; }

    const parts = [];
    const SYM = [-1, 1];
    // palet v5: keluarga v3 (abu-krem lapuk, jingga), panel berpola gelap di punggung
    const BEIGE = [0.23, 0.23, 0.22], BEIGE2 = [0.16, 0.16, 0.16], PALE = [0.3, 0.3, 0.29], RUST = [0.28, 0.17, 0.1], FRAME = [0.08, 0.08, 0.085];
    const weather = (base, i, r, seed) => (i === 0 || i === 1 || i === 7 ? FRAME : tone(base, 0.88 + 0.16 * hash(i + seed, r)));
    const seamRing = (pts, z, c = tone(BEIGE, 0.62)) => loft([{ z, pts: pts.map(([x, y]) => [x * 1.02, y * 1.02]) }, { z: z + 0.05, pts: pts.map(([x, y]) => [x * 1.02, y * 1.02]) }], () => c, false);

    // ---------- 1. badan: baji bersudut, hidung datar lebar dengan sensor, kokpit satu kursi ----------
    {
      const F = (w, h, cy) => oct(w, h, cy, 0, 0.35, 0.25);
      // cincin z -3,6 disisipkan di garis lurus (bentuk tetap) supaya kaca kokpit memanjang ke depan: pilot bisa melihat melewati hidung
      // cincin tambahan di garis lurus (bentuk tetap) tiap sekitar 0,6 m: gradasi gosong halus di sepanjang perut
      const zs = [...V5_RINGS.map((q) => q[0]), -3.6].sort((a, b) => a - b), rings = [];
      for (let k = 0; k < zs.length - 1; k++) { const n = Math.max(1, Math.ceil((zs[k + 1] - zs[k]) / 0.6)); for (let j = 0; j < n; j++) { const z = zs[k] + (zs[k + 1] - zs[k]) * j / n; rings.push({ z, pts: F(...v5At(z)) }); } }
      rings.push({ z: zs[zs.length - 1], pts: F(...v5At(zs[zs.length - 1])) });
      // kaca: sisi 3, 4, 5 di z -3,6 sampai -0,6; nada panel per pita 1,5 m (dulu per cincin)
      parts.push(loft(rings, (i, r, z0, z1) => { const zm = (z0 + z1) / 2;
        return i < 0 ? FRAME : zm > -3.6 && zm < -0.6 && (i === 3 || i === 4 || i === 5) ? GLASS : weather(zm < -0.6 ? PALE : BEIGE, i, Math.floor((zm + 7) / 1.5), 3); }));
      for (const z of [-4.0, 1.2]) parts.push(seamRing(F(...v5At(z)), z));   // penampang di z itu (dulu memakai penampang belakang: cincin melayang di depan kanopi)
      // rangka kaca kokpit
      parts.push(box(1.2, 0.035, 0.05, 0, 0.9, -1.6, PALE));  // palang kaca (tipis: dari kursi pilot hanya 0,45 m di depan mata)
      // hidung: bibir sensor gelap dan lampu
      parts.push(box(1.3, 0.12, 0.1, 0, -0.18, -6.22, FRAME));
      for (const sx of SYM) parts.push(box(0.14, 0.08, 0.05, sx * 0.45, -0.1, -6.24, [1, 0.95, 0.8]));
      // panel permukaan berpola di punggung (ceruk bersudut gelap)
      for (let k = 0; k < 6; k++) for (const sx of SYM) {
        const z = 0.1 + k * 0.55, w = 0.34 + 0.08 * (k % 2), x = sx * (0.35 + 0.2 * ((k + (sx > 0 ? 1 : 0)) % 2));
        parts.push(tilt(box(w, 0.04, 0.38, x, 1.06, z, FRAME), 'y', sx * 0.3 * (k % 2 ? 1 : -1), x, 1.06, z));
      }
      parts.push(box(0.5, 0.35, 1.8, 0, 1.1, 3.4, BEIGE2), box(0.12, 0.9, 1.3, 0, 1.6, 3.9, PALE));   // punggung belakang + sirip kecil
    }
    // ---------- 2. sayap pendek menyapu dengan kipas angkat tertanam, ujung dengan sirip kecil ----------
    for (const sx of SYM) {
      const sh = new THREE.Shape([new THREE.Vector2(0, -1.2), new THREE.Vector2(3.9, 0.9), new THREE.Vector2(3.9, 2.6), new THREE.Vector2(0, 3.9)]);
      const w = new THREE.ExtrudeGeometry(sh, { depth: 0.22, bevelEnabled: true, bevelThickness: 0.04, bevelSize: 0.04, bevelSegments: 1 }); w.rotateX(Math.PI / 2);
      if (sx < 0) { w.scale(-1, 1, 1); const q = w.index ? w.index.array : null, P = w.attributes; if (q) for (let k = 0; k < q.length; k += 3) [q[k + 1], q[k + 2]] = [q[k + 2], q[k + 1]]; else for (const nm of ['position', 'normal', 'uv']) { const A = P[nm].array, d = P[nm].itemSize; for (let k = 0; k < A.length; k += 3 * d) for (let e = 0; e < d; e++) [A[k + d + e], A[k + 2 * d + e]] = [A[k + 2 * d + e], A[k + d + e]]; } }   // cermin: urutan segitiga dibalik lagi
      w.translate(sx * 1.1, -0.05, -0.3); parts.push(tilt(paint(w, tone(BEIGE, 0.98)), 'z', sx * -0.1, sx * 1.1, 0, 0));
      // kipas angkat (cincin + kisi) di tengah sayap
      const fx = sx * 2.9, fz = 1.3;
      const t = new THREE.TorusGeometry(0.72, 0.08, 6, 24); t.rotateX(Math.PI / 2); t.translate(fx, -0.13, fz); parts.push(paint(t, FRAME));
      parts.push(cyl(0.7, 0.7, 0.06, fx, -0.16, fz, DARK, 'y', 24));
      for (let k = 0; k < 4; k++) parts.push(tilt(box(1.3, 0.03, 0.08, fx, -0.11, fz, METAL), 'y', k * Math.PI / 4, fx, -0.11, fz));
      // sirip kecil di ujung sayap (lampu navigasi)
      parts.push(box(0.12, 0.8, 1.2, sx * 5.0, 0.0, 1.7, PALE), box(0.14, 0.14, 0.14, sx * 5.0, 0.44, 1.3, sx < 0 ? [0.9, 0.1, 0.08] : [0.1, 0.8, 0.2]));
      for (let k = 0; k < 3; k++) parts.push(box(0.03, 0.05, 1.5, sx * (2.0 + k * 0.9), 0.1, 2.6, k % 2 ? FRAME : ORANGE));   // garis jingga
    }
    // ---------- 3. dua mesin di pangkal sayap: saluran masuk berkipas di depan, nosel di belakang ----------
    for (const sx of SYM) {
      const x = sx * 1.75, y = 0.45;
      parts.push(cyl(0.55, 0.6, 3.6, x, y, 2.0, tone(BEIGE2, 1.05), 'z', 16), cyl(0.5, 0.5, 0.06, x, y, 0.18, DARK, 'z', 16));
      for (let k = 0; k < 3; k++) parts.push(tilt(box(0.9, 0.04, 0.05, x, y, 0.22, METAL), 'z', k * Math.PI / 3, x, y, 0.22));   // bilah kipas masuk
      const lip = new THREE.TorusGeometry(0.56, 0.07, 6, 18); lip.translate(x, y, 0.2); parts.push(paint(lip, PALE));
      parts.push(cyl(0.45, 0.62, 0.8, x, y, 4.2, METAL, 'z', 16, true), cyl(0.44, 0.44, 0.05, x, y, 3.82, DARK, 'z', 16));
      for (let k = 0; k < 4; k++) parts.push(box(0.03, 0.09, 0.3, x + sx * 0.6, y, 1.0 + k * 0.6, FRAME));   // kisi samping
    }
    const NBODY = parts.length;
    // ---------- 4. kaki pendarat: satu di hidung, dua di bawah mesin; tapak lebar untuk air ----------
    for (const [x, z, top] of [[0, -3.8, -0.45], [-1.75, 2.4, -0.1], [1.75, 2.4, -0.1]]) {
      parts.push(cyl(0.1, 0.1, top - (PAD_Y + 0.3), x, (top + PAD_Y + 0.3) / 2, z, [0.78, 0.8, 0.82]), cyl(0.13, 0.13, 0.12, x, top - 0.1, z, ORANGE));
      parts.push(box(0.55, 0.08, 0.9, x, PAD_Y + 0.04, z, FRAME), tilt(cyl(0.04, 0.04, 0.9, x, top - 0.45, z + 0.35, METAL), 'x', 0.5, x, top - 0.45, z + 0.35));
    }

    // ---------- tangga di sisi kiri kokpit (ikut kaki: ditarik saat terbang) ----------
    for (let k = 0; k < 4; k++) parts.push(box(0.4, 0.04, 0.5, -1.45, -0.35 - k * 0.38, -1.6, METAL));
    parts.push(box(0.04, 1.6, 0.04, -1.62, -1.1, -1.85, METAL), box(0.04, 1.6, 0.04, -1.62, -1.1, -1.35, METAL));
    const body = mergeColored(THREE, parts.slice(0, NBODY).map((g) => ({ geo: g }))), legs = mergeColored(THREE, parts.slice(NBODY).map((g) => ({ geo: g })));
    // lapisan kotor dan gosong (ditentukan posisi dan normal tiap titik)
    const h3 = (x, y, z) => { const s = Math.sin(x * 12.9898 + y * 78.233 + z * 37.719) * 43758.5453; return s - Math.floor(s); };
    const sm = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
    for (const g of [body, legs]) {
      const p = g.attributes.position.array, n = g.attributes.normal.array, c = g.attributes.color.array;
      for (let i = 0; i < p.length; i += 3) {
        const x = p[i], y = p[i + 1], z = p[i + 2], ny = n[i + 1];
        if (c[i + 2] - c[i] > 0.035 && c[i + 1] < 0.1) continue;                                   // kaca tetap bersih
        let k = 1, warm = 0;
        const soot = sm(2.6, 4.7, z) * Math.max(0, 1 - Math.abs(Math.abs(x) - 1.75) / 1.4);        // jelaga di belakang nosel
        k *= 1 - 0.55 * soot; warm += 0.35 * soot * sm(3.9, 4.7, z);                                  // warna perunggu panas di bibir nosel
        const streak = h3(Math.floor(x * 4), 1.7, 3.1), fall = sm(-2, 4.5, z);                      // noda aliran memanjang ke belakang
        k *= 1 - 0.18 * streak * fall * (ny > 0.3 ? 1 : 0.5);
        k *= 0.9 + 0.2 * h3(Math.floor(x * 2), Math.floor(y * 2), Math.floor(z * 2));               // bintik kotor per panel
        let r = c[i] * k + warm * 0.09, gg = c[i + 1] * k + warm * 0.05, b = c[i + 2] * k + warm * 0.02;
        // gosong masuk atmosfer bergradasi: panas tertinggi (hidung, perut depan, tepi depan) memutih pudar, lalu abu-abu,
        // lalu jelaga hitam di tepi dan di hilir aliran, baru warna cat. Panas turun dari hidung ke belakang, bergaris searah aliran.
        const nz = n[i + 2], hn = sm(4.6, -6.2, z), belly = Math.max(0, -ny), lead = Math.max(0, -nz) * (y < 0.4 ? 1 : 0.4);   // hn: 1 di hidung, 0 di ekor
        let heat = belly * (0.25 + 0.75 * hn) + lead * (0.3 + 0.5 * hn) + 0.4 * hn * hn * sm(-0.2, -0.9, ny);
        heat *= 0.82 + 0.3 * h3(Math.floor(x * 5), 2.3, Math.floor(z * 0.8));                    // garis searah aliran
        heat = Math.min(1, heat);
        const lerp3 = (A, B, t) => [A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t, A[2] + (B[2] - A[2]) * t];
        const BLEACH = [0.5, 0.49, 0.47], ASH = [0.27, 0.265, 0.26], SOOT = [0.045, 0.04, 0.04], base = [r, gg, b];
        const burnt = heat > 0.72 ? lerp3(ASH, BLEACH, sm(0.72, 0.97, heat)) : heat > 0.44 ? lerp3(SOOT, ASH, sm(0.44, 0.72, heat)) : lerp3(base, SOOT, sm(0.16, 0.44, heat));
        c[i] = burnt[0]; c[i + 1] = burnt[1]; c[i + 2] = burnt[2];
      }
    }
    // kaca kanopi dipisah dari badan: dirender satu sisi (dari dalam kokpit tembus pandang)
    const isGlass = (c, i) => c[i + 2] - c[i] > 0.035 && c[i + 1] < 0.1;
    const split = (g) => {
      const p = g.attributes.position.array, n = g.attributes.normal.array, c = g.attributes.color.array, A = [[], [], []], B = [[], [], []];
      for (let i = 0; i < p.length; i += 9) {
        const D = isGlass(c, i) && isGlass(c, i + 3) && isGlass(c, i + 6) ? B : A;
        for (let k = 0; k < 9; k++) { D[0].push(p[i + k]); D[1].push(n[i + k]); D[2].push(c[i + k]); }
      }
      const mk = (D) => { const o = new THREE.BufferGeometry(); ['position', 'normal', 'color'].forEach((nm, j) => o.setAttribute(nm, new THREE.Float32BufferAttribute(D[j], 3))); return o; };
      return [mk(A), mk(B)];
    };
    const [hull, glass] = split(body);
    return {
      geo: hull, glass, legs, PAD_Y,
      pads: [[0, -3.8], [-1.75, 2.4], [1.75, 2.4]].map(([x, z]) => ({ x, z, r: 0.55 })),
      door: { x: -1.95, y: -0.2, z: -2.2, nx: -1 },                                                   // titik naik di kaki tangga (sisi kiri kokpit, di luar kotak tabrakan)
      nav: { red: [-5.0, 0.52, 1.3], green: [5.0, 0.52, 1.3], strobe: [0, 2.1, 3.9] },
      nozzles: [[-1.75, 0.45, 4.62], [1.75, 0.45, 4.62]], fans: [[-2.9, -0.3, 1.3], [2.9, -0.3, 1.3]],
      low: [{ x0: -1.3, x1: 1.3, z0: -6.3, z1: 4.7, y: -0.55 }, { x0: -3.0, x1: 3.0, z0: -1.2, z1: 4.2, y: -0.4 },
            { x0: -5.1, x1: 5.1, z0: 0.3, z1: 4.2, y: -0.4 }],                                          // badan, sayap dalam, sayap luar (menyapu): lebih rendah dari kepala
      belly: -0.55, eye: [0, 0.68, -1.15],                                          // mata pilot (lihat buildCockpitV5)
      size: { L: 10.8, W: 10.1, H: 4.0 },
    };
  }

  /* ---------- Kokpit KS-07 v5 (satu kursi) ----------
     Sumbu sama dengan buildV5 (hidung -z). Pelapis dalam mengikuti badan (skala 0,93 x 0,9), dibuka di bagian kaca.
     Dasbor miring menghadap mata dengan 3 layar MFD (posisi dikembalikan untuk tekstur kanvas di aplikasi),
     konsol kiri (tuas gas) dan kanan (tongkat samping), kursi tegak dengan sabuk jingga, rangka kanopi, sekat belakang.
     Tongkat dan tuas gas dikembalikan terpisah (poros di titik asal) supaya bisa digerakkan mengikuti kendali. */
  function buildCockpitV5(THREE) {
    const SHELL = [0.13, 0.13, 0.135], PANEL = [0.17, 0.17, 0.18], DARKP = [0.06, 0.06, 0.065], SEAT = [0.1, 0.1, 0.11],
          ORANGE = [0.45, 0.2, 0.07], METAL = [0.3, 0.3, 0.31], FRAME = [0.05, 0.05, 0.055], AMBER = [0.6, 0.38, 0.08], TEAL = [0.08, 0.32, 0.3], RED = [0.5, 0.08, 0.06];
    const parts = [];
    const paint = (g, c) => { g = g.index ? g.toNonIndexed() : g; const n = g.attributes.position.count, a = new Float32Array(n * 3); for (let i = 0; i < n; i++) a.set(c, i * 3); g.setAttribute('color', new THREE.BufferAttribute(a, 3)); g.computeVertexNormals(); return g; };
    const box = (w, h, d, x, y, z, c, rx = 0, ry = 0) => { const g = new THREE.BoxGeometry(w, h, d); if (rx) g.rotateX(rx); if (ry) g.rotateY(ry); g.translate(x, y, z); return paint(g, c); };
    const bar = (a, b, r, c, seg = 6) => {                               // batang silinder dari titik a ke titik b
      const A = new THREE.Vector3(...a), B = new THREE.Vector3(...b), d = B.clone().sub(A), L = d.length();
      const g = new THREE.CylinderGeometry(r, r, L, seg); g.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.normalize()));
      g.translate((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2); return paint(g, c);
    };
    const prism = (pts, x0, x1, c) => {                                  // prisma sepanjang x dari penampang (z, y)
      const sh = new THREE.Shape(pts.map(([z, y]) => new THREE.Vector2(-z, y)));
      const g = new THREE.ExtrudeGeometry(sh, { depth: x1 - x0, bevelEnabled: false }); g.rotateY(Math.PI / 2); g.translate(x0, 0, 0); return paint(g, c);
    };
    // penampang pelapis: segi delapan badan diperkecil (sudut potong tetap)
    const SW = 0.93, SH = 0.9;
    const ring = (z) => { const [w, h, cy] = v5At(z), a = w * SW / 2, b = h * SH / 2, chT = 0.3, chB = 0.2;
      return [[-a + chB, cy - b], [a - chB, cy - b], [a, cy - b + chB], [a, cy + b - chT], [a - chT, cy + b], [-a + chT, cy + b], [-a, cy + b - chT], [-a, cy - b + chB]]; };
    // 1. pelapis dalam: normal menghadap ke dalam; sisi 3, 4, 5 (atas) di ruas kaca dibuka
    {
      const Z = [-3.55, -2.6, -0.6, -0.15], pos = [], col = [];
      const tri = (p, q, r, c) => { pos.push(...p, ...q, ...r); col.push(...c, ...c, ...c); };
      for (let k = 0; k < Z.length - 1; k++) {
        const A = ring(Z[k]), B = ring(Z[k + 1]);
        for (let i = 0; i < 8; i++) {
          if (k < 2 && (i === 3 || i === 4 || i === 5)) continue;
          const j = (i + 1) % 8, c = i === 0 ? DARKP : i === 1 || i === 7 ? PANEL : SHELL;
          const a0 = [...A[i], Z[k]], a1 = [...A[j], Z[k]], b0 = [...B[i], Z[k + 1]], b1 = [...B[j], Z[k + 1]];
          tri(a0, b0, a1, c); tri(a1, b0, b1, c);                         // urutan kebalikan loft luar: normal ke dalam
        }
      }
      for (const [z, s] of [[Z[0], 1], [Z[Z.length - 1], -1]]) {           // tutup depan (di bawah dasbor) dan sekat belakang
        const R = ring(z), cy = R.reduce((t, p) => t + p[1], 0) / 8, c = s > 0 ? DARKP : SHELL;
        for (let i = 0; i < 8; i++) { const j = (i + 1) % 8, p0 = [0, cy, z], p1 = [...R[i], z], p2 = [...R[j], z]; if (s > 0) tri(p0, p1, p2, c); else tri(p0, p2, p1, c); }
      }
      const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
      g.computeVertexNormals(); parts.push(g);
      // rangka kanopi: tepi bawah kaca kiri-kanan, lengkung depan, tengah, dan belakang
      for (const sx of [-1, 1]) {
        const e = (z) => { const R = ring(z); return [sx * R[3][0] * 0.99, R[3][1], z]; };
        parts.push(bar(e(-3.55), e(-0.6), 0.025, FRAME));
      }
      for (const z of [-3.5, -2.6, -0.62]) {                              // lengkung z -1,6 = palang kaca luar
        const R = ring(z), pt = (q) => [q[0] * 0.99, q[1] - 0.01, z];
        parts.push(bar(pt(R[3]), pt(R[4]), 0.022, FRAME), bar(pt(R[4]), pt(R[5]), 0.022, FRAME), bar(pt(R[5]), pt(R[6]), 0.022, FRAME));
      }
    }
    // 2. dasbor: penutup silau di atas, muka miring menghadap mata, ceruk lutut di bawah
    const E = [-2.25, -0.12], Ft = [-2.445, 0.3];
    parts.push(prism([[-2.28, 0.37], [-2.95, 0.37], [-2.95, -0.47], [-2.46, -0.47], E, Ft, [-2.3, 0.33]], -0.86, 0.86, PANEL));
    parts.push(box(1.74, 0.025, 0.1, 0, 0.375, -2.31, DARKP));          // bibir penutup silau
    // layar MFD di muka dasbor (sedikit di depan permukaan), layar samping sedikit berputar ke arah pilot
    const tilt = -Math.atan2(E[0] - Ft[0], Ft[1] - E[1]);             // sudut muka dasbor: puncak menjauh dari pilot
    const nY = -Math.sin(tilt), nZ = Math.cos(tilt);
    const scr = (name, x, u, w, h, ry) => {
      const y = E[1] + (Ft[1] - E[1]) * u, z = E[0] + (Ft[0] - E[0]) * u, o = 0.012 + w / 2 * Math.sin(Math.abs(ry));   // layar diputar: tepi dalam tidak tenggelam
      return { name, c: [x, y + nY * o, z + nZ * o], w, h, rx: tilt, ry };
    };
    const screens = [scr('kiri', -0.47, 0.5, 0.3, 0.24, 0.22), scr('tengah', 0, 0.5, 0.36, 0.3, 0), scr('kanan', 0.47, 0.5, 0.3, 0.24, -0.22)];
    for (const S of screens) {                                           // bingkai layar + tombol tepi
      const f = new THREE.BoxGeometry(S.w + 0.05, S.h + 0.05, 0.02); f.rotateX(S.rx); f.rotateY(S.ry);
      f.translate(S.c[0], S.c[1] - nY * 0.013, S.c[2] - nZ * 0.013); parts.push(paint(f, DARKP));
      for (let k = 0; k < 5; k++) {
        const b = new THREE.BoxGeometry(0.026, 0.018, 0.012); b.translate(-S.w / 2 + (k + 0.5) * S.w / 5, -S.h / 2 - 0.018, 0.008);
        b.rotateX(S.rx); b.rotateY(S.ry); b.translate(...S.c); parts.push(paint(b, k === 2 ? AMBER : METAL));
      }
    }
    // panel sakelar di bawah layar dan tombol darurat
    for (let k = 0; k < 8; k++) parts.push(box(0.03, 0.03, 0.03, -0.28 + k * 0.08, -0.07, -2.27, k % 3 === 0 ? TEAL : k === 5 ? AMBER : METAL, tilt));
    parts.push(box(0.07, 0.03, 0.07, 0.0, 0.32 - 0.02, -2.34, RED));
    // 3. konsol samping
    for (const sx of [-1, 1]) {
      parts.push(box(0.36, 0.5, 1.25, sx * 0.8, -0.23, -1.35, PANEL));
      parts.push(box(0.3, 0.02, 1.1, sx * 0.8, 0.03, -1.38, DARKP));
      for (let k = 0; k < 6; k++) parts.push(box(0.035, 0.03, 0.035, sx * (0.7 + 0.07 * (k % 3)), 0.055, -1.85 + 0.1 * Math.floor(k / 3), k === 4 ? AMBER : k === 1 ? TEAL : METAL));
      parts.push(box(0.2, 0.012, 0.14, sx * 0.8, 0.045, -0.95, TEAL));  // pelat label berlampu redup
    }
    // 4. kursi tegak: dudukan, sandaran sedikit miring, sandaran kepala, sabuk jingga, alas kaki
    parts.push(box(0.56, 0.1, 0.55, 0, -0.12, -1.2, SEAT), box(0.5, 0.3, 0.5, 0, -0.33, -1.15, DARKP));
    for (const sx of [-1, 1]) parts.push(box(0.08, 0.1, 0.5, sx * 0.27, -0.05, -1.2, SEAT));
    parts.push(box(0.56, 0.72, 0.1, 0, 0.3, -0.84, SEAT, -0.16), box(0.34, 0.2, 0.1, 0, 0.76, -0.76, SEAT, -0.16));
    for (const sx of [-1, 1]) parts.push(box(0.05, 0.62, 0.012, sx * 0.13, 0.32, -0.9, ORANGE, -0.16));
    parts.push(box(0.5, 0.05, 0.012, 0, -0.03, -1.46, ORANGE));
    parts.push(box(0.6, 0.06, 0.35, 0, -0.43, -2.25, DARKP, 0.35));    // pijakan kaki / pedal
    // 5. sekat belakang: panel peralatan dan pegangan
    parts.push(box(0.9, 0.5, 0.05, 0, 0.35, -0.2, PANEL), box(0.6, 0.12, 0.03, 0, 0.72, -0.22, DARKP));
    for (const sx of [-1, 1]) parts.push(bar([sx * 0.55, 0.9, -0.5], [sx * 0.55, 0.9, -1.0], 0.015, METAL));
    const geo = mergeColored(THREE, parts.map((g) => ({ geo: g })));
    // tongkat samping kanan dan tuas gas kiri (poros di titik asal, sumbu tegak +y)
    const stick = mergeColored(THREE, [
      { geo: new THREE.CylinderGeometry(0.018, 0.022, 0.16, 8).translate(0, 0.08, 0), color: METAL },
      { geo: new THREE.CylinderGeometry(0.03, 0.028, 0.12, 8).rotateX(-0.25).translate(0, 0.21, 0.01), color: SEAT },
      { geo: new THREE.BoxGeometry(0.02, 0.015, 0.02).translate(0, 0.27, -0.01), color: RED },
      { geo: new THREE.CylinderGeometry(0.05, 0.05, 0.02, 12).translate(0, 0.01, 0), color: DARKP },
    ]);
    const throttle = mergeColored(THREE, [
      { geo: new THREE.BoxGeometry(0.03, 0.14, 0.03).translate(0, 0.07, 0), color: METAL },
      { geo: new THREE.BoxGeometry(0.1, 0.05, 0.07).translate(0.02, 0.15, 0), color: SEAT },
      { geo: new THREE.BoxGeometry(0.015, 0.02, 0.02).translate(0.055, 0.17, -0.02), color: AMBER },
    ]);
    return { geo, stick, throttle, stickAt: [0.8, 0.04, -1.5], throttleAt: [-0.8, 0.04, -1.45], screens, eye: [0, 0.68, -1.15] };
  }

  window.KESTREL = { build, buildV3, buildV5, buildCockpitV5, v5At, gear, mergeColored, GEAR, L, W, HT, HB };
})();
