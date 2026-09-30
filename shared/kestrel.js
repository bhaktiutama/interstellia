/* =====================================================================
   Shuttle "Kestrel" KS-07: modul bersama pertama (dipakai Copper Corn Station dan Millar's World).
   Desain orisinal: badan pengangkat 24 m (lofted superellipse), sirip miring ganda, 3 mesin.
   Skrip biasa (bukan modul ES) agar jalan dari file://: memasang window.KESTREL.
   Pakai: <script src="../../shared/kestrel.js"></script> sebelum skrip modul, lalu KESTREL.build(THREE).
   Sumbu model: hidung di -z, atas +y, satuan meter. Geometri berwarna per vertex (atribut color), normal selalu ada.
   Geometri build() identik dengan versi Copper Corn Station tahap 11d (diuji dengan sidik jari atribut).
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

  window.KESTREL = { build, gear, mergeColored, GEAR, L, W, HT, HB };
})();
