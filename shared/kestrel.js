/* =====================================================================
   Shuttle "Kestrel" KS-07: modul bersama pertama (dipakai Copper Corn Station dan Millar's World).
   Desain orisinal: badan pengangkat 24 m (lofted superellipse), sirip miring ganda, 3 mesin.
   Skrip biasa (bukan modul ES) agar jalan dari file://: memasang window.KESTREL.
   Pakai: <script src="../../shared/kestrel.js"></script> sebelum skrip modul, lalu KESTREL.build(THREE).
   Sumbu model: hidung di -z, atas +y, satuan meter. Geometri berwarna per vertex (atribut color), normal selalu ada.
   build() = v1 (badan pengangkat), identik dengan Copper Corn Station tahap 11d (diuji dengan sidik jari atribut); dipakai Copper
   sampai tahap M3e. buildV3() = KS-07 v3 hibrida (dipilih pemilik), dipakai Millar's World.
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

  window.KESTREL = { build, buildV3, gear, mergeColored, GEAR, L, W, HT, HB };
})();
