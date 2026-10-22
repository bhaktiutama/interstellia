/* Armada: pilihan wahana bersama Millar dan Gargantua (rencana docs/app/rencana-pilihan-wahana.md, langkah W1).
   Skrip biasa (bukan modul ES), jalan dari file://: memasang window.FLEET.
   Tiga wahana: ks07 (KS-07 Kestrel v5, satu kursi), pr11 (PR-11 Petrel, dua awak), gx01 (GX-01 Ambang, kokpit pod kaca).
   Pilihan dibaca saat halaman dimuat: ?ship= lalu localStorage lazarus.ship lalu bawaan experience; mengganti wahana = simpan lalu muat ulang
   (semua kode jauh membangun adegan dari satu deskriptor, jadi muat ulang paling aman).
   Deskriptor wahana (untuk Millar, three.js): geo, glass, legs, PAD_Y, pads, door, nav, nozzles [x, y, z, r], fans [x, y, z, r], low, belly, eye,
   size, fly (pengali CONFIG.fly), orb (data plasma orbit), cockpit { geo, stick, throttle, stickAt, throttleAt, screens, eye, offset, canopy }.
   Layar kokpit: { name, c, w, h, rx, ry } atau { name, c, w, h, q: [x, y, z, w] } (kuaternion). */
(function () {
  'use strict';
  const INFO = {
    ks07: { id: 'ks07', name: 'KS-07 Kestrel', short: 'KS-07', crew: 1, size: { L: 10.8, W: 10.1, H: 4.0 }, thumb: 'ks07.jpg', callsign: 'KESTREL' },
    pr11: { id: 'pr11', name: 'PR-11 Petrel', short: 'PR-11', crew: 2, size: { L: 19, W: 13.8, H: 9.3 }, thumb: 'pr11.jpg', callsign: 'PETREL' },
    gx01: { id: 'gx01', name: 'GX-01 Ambang', short: 'GX-01', crew: 2, size: { L: 27.5, W: 9.9, H: 7.5 }, thumb: 'gx01.jpg', callsign: 'AMBANG' },
  };
  const IDS = ['ks07', 'pr11', 'gx01'];
  const KEY = 'lazarus.ship';

  function current(def) {                         // ?ship= lalu localStorage lalu bawaan
    let id = null;
    try { id = new URLSearchParams(location.search).get('ship'); } catch (e) { /* abaikan */ }
    if (!INFO[id]) { try { id = localStorage.getItem(KEY); } catch (e) { id = null; } }
    return INFO[id] ? id : (INFO[def] ? def : IDS[0]);
  }
  function set(id) {                              // simpan, buang ?ship= dari alamat, muat ulang
    if (!INFO[id]) return;
    try { localStorage.setItem(KEY, id); } catch (e) { /* abaikan */ }
    const u = new URL(location.href); u.searchParams.delete('ship'); location.href = u.toString();
  }
  /* Isi elemen el dengan tombol pilihan (kelas cls, kelas aktif act). opt.base = folder gambar kecil, opt.label(info) = teks tombol. */
  function mountPicker(el, id, opt) {
    opt = opt || {}; el.textContent = '';
    for (const k of IDS) {
      const b = document.createElement('button'); b.type = 'button'; b.dataset.ship = k;
      if (opt.cls) b.className = opt.cls; if (k === id && opt.act) b.classList.add(opt.act);
      b.textContent = opt.label ? opt.label(INFO[k]) : INFO[k].name;
      b.title = `${INFO[k].name} · ${INFO[k].size.L} x ${INFO[k].size.W} m`;
      b.addEventListener('click', () => { if (k !== id) set(k); });
      el.appendChild(b);
    }
  }

  // ---------- KS-07 v5 ----------
  function buildKS07(THREE) {
    const K = window.KESTREL, S = K.buildV5(THREE), C = K.buildCockpitV5(THREE);
    return Object.assign({ id: 'ks07' }, S, { nozzles: S.nozzles.map((p) => [p[0], p[1], p[2], 0.42]), fans: S.fans.map((p) => [p[0], p[1], p[2], 0.62]),
      cockpit: Object.assign({ offset: [0, 0, 0], canopy: 'v5' }, C), fly: { climb: 1, fwd: 1, acc: 1, yawRate: 1, spool: 1 }, orb: null });
  }

  // ---------- PR-11 Petrel ----------
  function buildPR11(THREE) {
    if (!window.PETREL) throw new Error('shared/petrel.js tidak termuat');
    const S = window.PETREL.buildPetrel(THREE);
    S.cockpit.canopy = 'v5';
    S.orb = { zA: 7.0, zB: -9.0, src: [[-5.5, -0.1, -8.4, 24], [5.5, -0.1, -8.4, 20], [-6.8, 0.9, 0.5, 10], [6.8, 0.9, 0.5, 12], [0, -0.1, -9.6, 30], [-4.0, -1.25, -1, 14], [4.0, -1.25, -1, 18]] };
    return S;
  }

  // ---------- GX-01: badan dan kokpit dari blob gx01.data.js (window.__GX01), kaki dari KESTREL.buildV3 ----------
  const CUT_Y = -2.45;                            // sama dengan tools/siapkan_wahana_gx.mjs: segitiga di bawah ini = kaki pendarat
  function buildGX01(THREE) {
    const D = window.__GX01;
    if (!D) throw new Error('assets/gx01.data.js tidak termuat');
    const raw = (b) => Uint8Array.from(atob(b), (ch) => ch.charCodeAt(0));
    const P = new Int16Array(raw(D.pos).buffer), N = new Int8Array(raw(D.nrm).buffer), C = raw(D.col), M = raw(D.mat), sc = D.scale, nS = D.nStatic || D.n;
    const mk = (idx, off) => {                    // idx = daftar awal segitiga (indeks verteks), off = titik putar yang dikurangkan
      const pos = new Float32Array(idx.length * 9), nrm = new Float32Array(idx.length * 9), col = new Float32Array(idx.length * 9);
      idx.forEach((v0, t) => { for (let k = 0; k < 3; k++) { const v = v0 + k;
        for (let a = 0; a < 3; a++) { pos[t * 9 + k * 3 + a] = P[v * 3 + a] * sc - (off ? off[a] : 0); nrm[t * 9 + k * 3 + a] = N[v * 3 + a] / 127; col[t * 9 + k * 3 + a] = C[v * 3 + a] / 255; } } });
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('normal', new THREE.BufferAttribute(nrm, 3)); g.setAttribute('color', new THREE.BufferAttribute(col, 3));
      return g;
    };
    const hull = [], glass = [], inner = [];
    for (let v = 0; v + 2 < nS; v += 3) (M[v] === 0 ? hull : M[v] === 1 ? glass : inner).push(v);
    const part = (name) => { const p = D.parts[name], idx = []; for (let v = p.start; v < p.start + p.count; v += 3) idx.push(v); return mk(idx, p.pivot); };
    // kaki: segitiga badan v3 yang punya titik di bawah CUT_Y (persis yang dibuang alat olah)
    const V3 = window.KESTREL.buildV3(THREE), g3 = V3.geo, p3 = g3.attributes.position.array, n3 = g3.attributes.normal.array, c3 = g3.attributes.color.array, L = [[], [], []];
    for (let t = 0; t < p3.length / 9; t++) {
      if (Math.min(p3[t * 9 + 1], p3[t * 9 + 4], p3[t * 9 + 7]) >= CUT_Y) continue;
      for (let k = 0; k < 9; k++) { L[0].push(p3[t * 9 + k]); L[1].push(n3[t * 9 + k]); L[2].push(c3[t * 9 + k]); }
    }
    const legs = new THREE.BufferGeometry();
    ['position', 'normal', 'color'].forEach((nm, j) => legs.setAttribute(nm, new THREE.Float32BufferAttribute(L[j], 3)));
    const NAMES = ['kiri', 'tengah', 'kanan', 'sisiK', 'sisiR'], m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), v1 = new THREE.Vector3(), v2 = new THREE.Vector3(), v3 = new THREE.Vector3();
    const screens = D.screens.map((s, i) => {      // basis pelat layar: +z = normal, +y = atas, +x = silang
      v3.set(...s.n).normalize(); v2.set(...s.up).normalize(); v1.crossVectors(v2, v3).normalize(); v2.crossVectors(v3, v1);
      q.setFromRotationMatrix(m4.makeBasis(v1, v2, v3));
      return { name: NAMES[i] || 'x' + i, c: s.c, w: s.w, h: s.h, q: [q.x, q.y, q.z, q.w] };
    });
    const sp = D.parts.stick.pivot, tp = D.parts.throttle.pivot;
    return {
      id: 'gx01', geo: mk(hull), glass: mk(glass), legs, PAD_Y: V3.PAD_Y,
      pads: V3.pads, door: { x: V3.door.x - 1.1, y: V3.door.y - 3, z: V3.door.z, nx: -1 }, nav: V3.nav,
      nozzles: [[-1.1, -0.25, 12.82, 0.45], [-1.1, 1.05, 12.82, 0.45], [1.1, -0.25, 12.82, 0.45], [1.1, 1.05, 12.82, 0.45]],
      fans: [[-3.7, -1.55, -3.0, 0.9], [3.7, -1.55, -3.0, 0.9], [-2.3, -1.95, 8.0, 0.9], [2.3, -1.95, 8.0, 0.9]],
      low: V3.low, belly: V3.belly, eye: D.eye, size: V3.size,
      cockpit: { geo: mk(inner), stick: part('stick'), throttle: part('throttle'), stickAt: sp.slice(), throttleAt: tp.slice(), screens, eye: D.eye.slice(), offset: [0, 0, 0], canopy: 'gen' },
      fly: { climb: 0.7, fwd: 0.7, acc: 0.55, yawRate: 0.5, spool: 1.6 },
      orb: { zA: 12.0, zB: -15.0, src: [[-3.7, 0, -14.3, 26], [3.7, 0, -14.3, 20], [-4.6, 1.3, -13, 10], [4.6, 1.3, -13, 12], [0, -0.25, -15.4, 30], [-3.4, -1.0, 12, 15], [3.4, -1.0, 12, 19]] },
    };
  }

  function build(THREE, id) {
    id = id || current();
    return id === 'pr11' ? buildPR11(THREE) : id === 'gx01' ? buildGX01(THREE) : buildKS07(THREE);
  }

  window.FLEET = { ids: IDS, info: INFO, current, set, mountPicker, build, KEY };
})();
