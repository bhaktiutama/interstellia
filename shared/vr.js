/* =====================================================================
   VRKIT (rencana VR, docs/app/rencana-vr.md, tahap VR1): dukungan WebXR immersive-vr bersama ketiga experience.
   Skrip biasa, tanpa three.js (objek three dibuat host lewat VRKIT.three(THREE)). Mati total bila browser tidak punya
   navigator.xr atau tidak mendukung immersive-vr: tombol tidak muncul, tidak ada yang berubah.

   Jalur render (keputusan VR1, calon B rencana): tiap mata dirender terpisah dengan rantai efek layar host yang lama,
   ke target seukuran satu mata; pass akhir yang biasanya ke kanvas diarahkan ke viewport mata di framebuffer XR
   (VRKIT.eyeTarget(i) untuk three.js, VRKIT.fb + eye.vp untuk WebGL mentah). Host three.js mematikan renderer.xr.enabled
   selama render mata (three.js 0.186.1 selalu mengganti kamera dengan ArrayCamera XR saat presenting) lalu menyalakannya lagi.

   Host memanggil VRKIT.init(A):
     A.backend 'three' (A.renderer) atau 'raw' (A.gl)
     A.frame(t, eyes, xrFrame)  dipanggil tiap frame XR; eyes[i] = { i, eye, world (Float32Array 16, ruang acuan),
                                 proj (Float32Array 16), vp { x, y, w, h } }; host menggabungkan world dengan rig-nya sendiri
     A.start() / A.end()        sesi mulai / selesai (host menyesuaikan ukuran efek layar, mematikan gerak kepala dsb.)
     A.items()                  baris tambahan panel menu VR: [{ label() -> teks, act() }]
     A.root                     elemen tempat tombol "Masuk VR" ditaruh (bawaan document.body, pojok kanan bawah)
     A.lang()                   'id' / 'en'
   Input tiap frame: VRKIT.in = { move [x, y] stik kiri, look [x, y] stik kanan, trig, grip, a, b, x, y, ls, rs (tekan stik),
     down { nama: true saat baru ditekan }, turn (radian belok patah frame ini), ray (sinar kontroler kanan: o, d ruang acuan) }.
   Kenyamanan: VRKIT.motion(v) host melapor kecepatan gerak semu (m/s) -> VRKIT.vig 0..1 (kuat vinyet terowongan);
     belok patah 30 / 45 derajat atau halus; pusatkan ulang (Y) -> VRKIT.recenter = { yaw, p } dikurangkan dari pose kepala.
   Setelan di localStorage 'lazarus.vr': { turn: 30 | 45 | 0 (halus), vig: 0 | 1 | 2, scale: 0,7 | 0,85 | 1 }.
   ===================================================================== */
(function () {
  'use strict';
  const STR = {
    enter: ['Masuk VR', 'Enter VR'], exit: ['Keluar VR', 'Exit VR'], inVR: ['Sedang di VR. Lepas headset atau tekan Keluar VR.', 'In VR. Take off the headset or press Exit VR.'],
    menu: ['Menu VR', 'VR menu'], recenter: ['Pusatkan ulang (Y)', 'Recenter (Y)'], turn: ['Belok', 'Turn'], smooth: ['halus', 'smooth'],
    vig: ['Vinyet saat bergerak', 'Vignette when moving'], vigL: [['mati', 'tipis', 'kuat'], ['off', 'light', 'strong']],
    scale: ['Resolusi (sesi berikut)', 'Resolution (next session)'], close: ['Tutup menu (X)', 'Close menu (X)'],
    back: ['Kembali ke menu utama', 'Back to main menu'], hint: ['Picu kanan = pilih', 'Right trigger = select'],
    err: ['VR gagal dibuka: ', 'VR failed to start: '],
  };
  const K = window.VRKIT = {
    ok: false, on: false, session: null, A: null, eyes: [], vig: 0, in: null, menu: false, fb: null, layer: null, ref: null,
    recenter: { yaw: 0, p: [0, 0, 0] }, st: { turn: 30, vig: 1, scale: 1 }, STR,
  };
  try { Object.assign(K.st, JSON.parse(localStorage.getItem('lazarus.vr') || '{}')); } catch (e) { /* abaikan */ }
  const save = () => { try { localStorage.setItem('lazarus.vr', JSON.stringify(K.st)); } catch (e) { /* abaikan */ } };
  const L = () => (K.A && K.A.lang && K.A.lang() === 'en' ? 1 : 0);
  const T = (k) => STR[k][L()];
  K.T = T;

  // ---------- matematika kecil (kolom-mayor) ----------
  const M4 = K.m4 = {
    mul(a, b, o = new Float32Array(16)) { const r = new Float32Array(16); for (let c = 0; c < 4; c++) for (let w = 0; w < 4; w++) r[c * 4 + w] = a[w] * b[c * 4] + a[4 + w] * b[c * 4 + 1] + a[8 + w] * b[c * 4 + 2] + a[12 + w] * b[c * 4 + 3]; o.set(r); return o; },
    invRigid(m, o = new Float32Array(16)) {
      const r = [m[0], m[4], m[8], 0, m[1], m[5], m[9], 0, m[2], m[6], m[10], 0, 0, 0, 0, 1];
      r[12] = -(r[0] * m[12] + r[4] * m[13] + r[8] * m[14]); r[13] = -(r[1] * m[12] + r[5] * m[13] + r[9] * m[14]); r[14] = -(r[2] * m[12] + r[6] * m[13] + r[10] * m[14]);
      o.set(r); return o;
    },
    yaw(a, o = new Float32Array(16)) { const c = Math.cos(a), s = Math.sin(a); o.set([c, 0, -s, 0, 0, 1, 0, 0, s, 0, c, 0, 0, 0, 0, 1]); return o; },
    pt(m, p) { return [m[0] * p[0] + m[4] * p[1] + m[8] * p[2] + m[12], m[1] * p[0] + m[5] * p[1] + m[9] * p[2] + m[13], m[2] * p[0] + m[6] * p[1] + m[10] * p[2] + m[14]]; },
    dir(m, d) { return [m[0] * d[0] + m[4] * d[1] + m[8] * d[2], m[1] * d[0] + m[5] * d[1] + m[9] * d[2], m[2] * d[0] + m[6] * d[1] + m[10] * d[2]]; },
  };
  // pose ruang acuan setelah pusatkan ulang: R(-yaw0) * (pose - p0)
  function recentered(m) {
    const o = new Float32Array(m); o[12] -= K.recenter.p[0]; o[14] -= K.recenter.p[2];
    return M4.mul(M4.yaw(-K.recenter.yaw), o);
  }

  // ---------- tombol di monitor ----------
  let btn = null, note = null;
  function ui() {
    if (btn) return;
    const root = (K.A && K.A.root) || document.body;
    btn = document.createElement('button'); btn.type = 'button'; btn.id = 'vrBtn';
    btn.style.cssText = 'position:fixed;right:16px;bottom:16px;z-index:60;font:600 14px system-ui,sans-serif;padding:10px 14px;border-radius:10px;border:1px solid #e8b765;background:rgba(20,18,12,.78);color:#fff;cursor:pointer';
    btn.addEventListener('click', (e) => { e.stopPropagation(); K.on ? K.exit() : K.enter(); });
    note = document.createElement('div'); note.id = 'vrNote'; note.hidden = true;
    note.style.cssText = 'position:fixed;inset:0;z-index:59;display:grid;place-items:center;background:rgba(5,6,9,.86);color:#dfe3ea;font:16px system-ui,sans-serif;text-align:center;padding:24px';
    root.appendChild(note); root.appendChild(btn);
    label();
  }
  function label() { if (btn) btn.textContent = K.on ? T('exit') : T('enter'); if (note) note.textContent = T('inVR'); }
  K.label = label;

  K.init = async function (A) {
    K.A = A;
    if (!navigator.xr || !navigator.xr.isSessionSupported) return false;
    try { K.ok = await navigator.xr.isSessionSupported('immersive-vr'); } catch (e) { K.ok = false; }
    if (K.ok) ui();
    return K.ok;
  };

  // ---------- sesi ----------
  K.enter = async function () {
    if (K.on || !K.ok) return;
    const A = K.A;
    let s;
    try { s = await navigator.xr.requestSession('immersive-vr', { optionalFeatures: ['local-floor'] }); }
    catch (e) { alert(T('err') + (e && e.message)); return; }
    K.session = s; K.on = true; K.menu = false; K.vig = 0; prevBtn = {}; K.in = blankIn();
    s.addEventListener('end', onEnd);
    try {
      if (A.backend === 'three') {
        const xr = A.renderer.xr;
        xr.enabled = true; xr.setReferenceSpaceType('local'); xr.setFramebufferScaleFactor(K.st.scale || 1);
        await xr.setSession(s);
        K.ref = xr.getReferenceSpace();
        A.renderer.setAnimationLoop((t, f) => tick(t, f));
      } else {
        const gl = A.gl;
        if (gl.makeXRCompatible) await gl.makeXRCompatible();
        K.layer = new XRWebGLLayer(s, gl, { antialias: false, depth: true, framebufferScaleFactor: K.st.scale || 1 });
        s.updateRenderState({ baseLayer: K.layer, depthNear: 0.02, depthFar: 1000 });
        K.ref = await s.requestReferenceSpace('local');
        s.requestAnimationFrame(rawTick);
      }
    } catch (e) { alert(T('err') + (e && e.message)); try { s.end(); } catch (e2) { /* abaikan */ } return; }
    if (note) note.hidden = false;
    label();
    if (A.start) A.start();
  };
  K.exit = function () { if (K.session) K.session.end(); };
  function onEnd() {
    const A = K.A;
    K.on = false; K.session = null; K.layer = null; K.fb = null; K.eyes = []; K.menu = false;
    if (A.backend === 'three') { A.renderer.setAnimationLoop(null); }
    if (note) note.hidden = true;
    label();
    if (A.end) A.end();
  }

  // ---------- frame ----------
  function rawTick(t, frame) {
    const s = frame.session; if (!K.on) return;
    s.requestAnimationFrame(rawTick);
    const pose = frame.getViewerPose(K.ref); if (!pose) return;
    K.fb = K.layer.framebuffer;
    K.eyes = pose.views.map((v, i) => { const vp = K.layer.getViewport(v); return { i, eye: v.eye, world: recentered(v.transform.matrix), proj: v.projectionMatrix, vp: { x: vp.x, y: vp.y, w: vp.width, h: vp.height } }; });
    step(t, frame);
  }
  function tick(t, frame) {
    if (!K.on || !frame) return;
    const A = K.A, cams = A.renderer.xr.getCamera().cameras;
    K.xrTarget = A.renderer.getRenderTarget();                       // target XR yang sudah diikat three.js untuk frame ini
    K.eyes = cams.map((c, i) => ({ i, eye: i ? 'right' : 'left', world: recentered(c.matrix.elements), proj: new Float32Array(c.projectionMatrix.elements),
      vp: { x: c.viewport.x, y: c.viewport.y, w: c.viewport.z, h: c.viewport.w } }));
    step(t, frame);
  }
  let lastT = 0;
  function step(t, frame) {
    const dt = lastT ? Math.min(0.1, (t - lastT) / 1000) : 0; lastT = t;
    readInput(frame, dt);
    if (K.in.down.y) K.recenterNow();
    if (K.in.down.x) K.menu = !K.menu;
    if (K.menu && K.in.down.trig) panelClick();
    K.vig += ((K.st.vig ? K.vigTarget * (K.st.vig === 2 ? 1 : 0.6) : 0) - K.vig) * Math.min(1, dt * 6);
    K.vigTarget = 0;
    K.A.frame(t, K.eyes, frame, dt);
  }
  K.vigTarget = 0;
  K.motion = function (v) { K.vigTarget = Math.max(K.vigTarget, Math.min(1, Math.max(0, (v - 0.5) / 4))); };
  K.recenterNow = function () {
    const e = K.eyes[0]; if (!e) return;
    // pose kepala tanpa pusatkan ulang = rata-rata dua mata, dihitung balik dari pose yang sudah dipusatkan
    const raw = M4.mul(M4.yaw(K.recenter.yaw), e.world); raw[12] += K.recenter.p[0]; raw[14] += K.recenter.p[2];
    const fwd = M4.dir(raw, [0, 0, -1]);
    K.recenter = { yaw: Math.atan2(-fwd[0], -fwd[2]), p: [raw[12], 0, raw[14]] };
  };

  // ---------- input: kontroler Touch (gamepad xr-standard) ----------
  let prevBtn = {}, smoothArm = true;
  function blankIn() { return { move: [0, 0], look: [0, 0], trig: 0, grip: 0, a: 0, b: 0, x: 0, y: 0, ls: 0, rs: 0, gripL: 0, trigL: 0, down: {}, turn: 0, ray: null }; }
  function readInput(frame, dt) {
    const I = blankIn(), s = frame.session;
    for (const src of s.inputSources) {
      const g = src.gamepad; if (!g) continue;
      const b = (i) => (g.buttons[i] ? g.buttons[i].value || (g.buttons[i].pressed ? 1 : 0) : 0), ax = (i) => g.axes[i] || 0;
      if (src.handedness === 'left') { I.move = [ax(2), ax(3)]; I.trigL = b(0); I.gripL = b(1); I.ls = b(3); I.x = b(4); I.y = b(5); }
      else { I.look = [ax(2), ax(3)]; I.trig = b(0); I.grip = b(1); I.rs = b(3); I.a = b(4); I.b = b(5);
        const p = src.targetRaySpace && frame.getPose(src.targetRaySpace, K.ref);
        if (p) { const m = recentered(p.transform.matrix); I.ray = { o: [m[12], m[13], m[14]], d: M4.dir(m, [0, 0, -1]), m }; } }
    }
    for (const k of ['trig', 'grip', 'a', 'b', 'x', 'y', 'ls', 'rs', 'trigL', 'gripL']) { const on = I[k] > 0.5; if (on && !prevBtn[k]) I.down[k] = true; prevBtn[k] = on; }
    // belok: patah (30 / 45 derajat, sekali per dorongan stik) atau halus (90 derajat/s)
    const lx = I.look[0];
    if (!K.menu) {
      if (K.st.turn) { if (Math.abs(lx) > 0.7 && smoothArm) { I.turn = -Math.sign(lx) * K.st.turn * Math.PI / 180; smoothArm = false; } if (Math.abs(lx) < 0.3) smoothArm = true; }
      else if (Math.abs(lx) > 0.15) I.turn = -lx * Math.PI / 2 * dt;
    }
    K.in = I;
  }

  // ---------- panel menu VR (kanvas 2D, ditaruh 1,2 m di depan saat dibuka, sinar kontroler kanan) ----------
  const PW = 640, PH = 400, PANEL = { w: 0.96, h: 0.6 };
  K.panel = { canvas: null, dirty: true, m: null, hover: -1, rows: [] };
  function rows() {
    const A = K.A, r = [
      { label: () => T('recenter'), act: () => K.recenterNow() },
      { label: () => `${T('turn')}: ${K.st.turn ? K.st.turn + '°' : T('smooth')}`, act: () => { K.st.turn = { 30: 45, 45: 0, 0: 30 }[K.st.turn] ?? 30; save(); } },
      { label: () => `${T('vig')}: ${STR.vigL[L()][K.st.vig]}`, act: () => { K.st.vig = (K.st.vig + 1) % 3; save(); } },
      { label: () => `${T('scale')}: ${Math.round((K.st.scale || 1) * 100)}%`, act: () => { K.st.scale = { 1: 0.7, 0.7: 0.85, 0.85: 1 }[K.st.scale] || 1; save(); } },
      ...((A.items && A.items()) || []),
      { label: () => T('close'), act: () => { K.menu = false; } },
      { label: () => T('exit'), act: () => K.exit() },
    ];
    return r;
  }
  K.drawPanel = function () {
    const P = K.panel; if (!P.canvas) { P.canvas = document.createElement('canvas'); P.canvas.width = PW; P.canvas.height = PH; }
    P.rows = rows();
    const g = P.canvas.getContext('2d'), n = P.rows.length, rh = Math.min(48, (PH - 70) / n);
    g.fillStyle = 'rgba(12,14,18,0.92)'; g.fillRect(0, 0, PW, PH);
    g.strokeStyle = '#e8b765'; g.lineWidth = 3; g.strokeRect(1.5, 1.5, PW - 3, PH - 3);
    g.fillStyle = '#e8b765'; g.font = '600 26px system-ui, sans-serif'; g.fillText(T('menu'), 24, 40);
    g.fillStyle = '#8a919c'; g.font = '18px system-ui, sans-serif'; g.fillText(T('hint'), PW - 24 - g.measureText(T('hint')).width, 40);
    P.rows.forEach((r, i) => {
      const y = 60 + i * rh;
      if (i === P.hover) { g.fillStyle = 'rgba(232,183,101,0.22)'; g.fillRect(12, y, PW - 24, rh - 4); }
      g.fillStyle = '#dfe3ea'; g.font = '22px system-ui, sans-serif'; g.fillText(r.label(), 28, y + rh * 0.66);
    });
    P.dirty = false; P.rh = rh;
    return P.canvas;
  };
  // pose panel di ruang acuan (dipusatkan): ditaruh saat menu dibuka, 1,2 m di depan kepala, tegak
  K.panelPose = function () {
    const P = K.panel;
    if (!K.menu) { P.m = null; return null; }
    if (!P.m && K.eyes[0]) {
      const h = K.eyes[0].world, f = M4.dir(h, [0, 0, -1]), yaw = Math.atan2(-f[0], -f[2]), c = Math.cos(yaw), s = Math.sin(yaw);
      P.m = new Float32Array([c, 0, -s, 0, 0, 1, 0, 0, s, 0, c, 0, h[12] - s * 1.2, h[13] - 0.15, h[14] - c * 1.2, 1]);
      P.dirty = true;
    }
    // sinar kontroler kanan ke bidang panel -> baris yang disorot
    const I = K.in, old = P.hover; P.hover = -1; P.hit = null;
    if (I && I.ray && P.m) {
      const inv = M4.invRigid(P.m), o = M4.pt(inv, I.ray.o), d = M4.dir(inv, I.ray.d);
      if (d[2] < -1e-4) {
        const t = -o[2] / d[2], x = o[0] + d[0] * t, y = o[1] + d[1] * t, u = x / PANEL.w + 0.5, v = 0.5 - y / PANEL.h;
        if (t > 0 && u >= 0 && u <= 1 && v >= 0 && v <= 1) { P.hit = [x, y, 0, t]; const py = v * PH; if (py > 60) P.hover = Math.floor((py - 60) / (P.rh || 40)); if (P.hover >= (P.rows.length || 0)) P.hover = -1; }
      }
    }
    if (P.hover !== old) P.dirty = true;
    return { m: P.m, w: PANEL.w, h: PANEL.h };
  };
  function panelClick() { const P = K.panel; if (P.hover >= 0 && P.rows[P.hover]) { P.rows[P.hover].act(); P.dirty = true; } }

  // ---------- three.js: target mata, panel, sinar, vinyet ----------
  // eyeTarget(i): target XR dengan viewport mata i; dipakai pass akhir host (pengganti setRenderTarget(null))
  K.eyeTarget = function (i) {
    const t = K.xrTarget, e = K.eyes[i]; if (!t || !e) return null;
    t.viewport.set(e.vp.x, e.vp.y, e.vp.w, e.vp.h); t.scissor.set(e.vp.x, e.vp.y, e.vp.w, e.vp.h); t.scissorTest = true;
    return t;
  };
  K.eyeTargetDone = function () { const t = K.xrTarget; if (t) { t.viewport.set(0, 0, t.width, t.height); t.scissor.set(0, 0, t.width, t.height); t.scissorTest = false; } };
  // vinyet terowongan (dan layar gelap saat pindah): kuat = 0..1, gelap = 0..1
  K.VIG_FS = `
    uniform float uK, uDark; varying vec2 vUv;
    void main() {
      float r = length((vUv - 0.5) * vec2(1.0, 1.15)) * 2.0;
      float a = max(uDark, uK * smoothstep(0.95 - 0.5 * uK, 1.25 - 0.45 * uK, r));
      gl_FragColor = vec4(0.0, 0.0, 0.0, clamp(a, 0.0, 1.0));
    }`;
  K.three = function (THREE) {
    if (K._three) return K._three;
    const P = K.panel;
    const panelTex = new THREE.CanvasTexture(K.drawPanel());
    panelTex.colorSpace = THREE.SRGBColorSpace;
    const panel = new THREE.Mesh(new THREE.PlaneGeometry(PANEL.w, PANEL.h), new THREE.MeshBasicMaterial({ map: panelTex, toneMapped: false, depthTest: false, transparent: true }));
    panel.renderOrder = 1e6; panel.matrixAutoUpdate = false; panel.frustumCulled = false;
    const rayG = new THREE.BufferGeometry().setAttribute('position', new THREE.Float32BufferAttribute([0, 0, 0, 0, 0, -1], 3));
    const ray = new THREE.Line(rayG, new THREE.LineBasicMaterial({ color: 0xe8b765, depthTest: false, transparent: true, toneMapped: false }));
    ray.renderOrder = 1e6 + 1; ray.matrixAutoUpdate = false; ray.frustumCulled = false;
    const ui = new THREE.Scene(); ui.add(panel, ray);
    const vig = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({ uniforms: { uK: { value: 0 }, uDark: { value: 0 } }, transparent: true, depthTest: false, depthWrite: false,
      vertexShader: 'varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }', fragmentShader: K.VIG_FS }));
    vig.frustumCulled = false;
    const vigS = new THREE.Scene(); vigS.add(vig);
    const ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1), m4 = new THREE.Matrix4(), cam = new THREE.PerspectiveCamera();
    cam.matrixAutoUpdate = false; cam.matrixWorldAutoUpdate = false; ui.matrixWorldAutoUpdate = false;   // matriks diisi manual tiap mata
    K._three = {
      panel, ray, ui, vig, vigS,
      // gambar panel menu + sinar ke mata i (setelah pass akhir), rig = Matrix4 dunia dari ruang acuan
      overlay(renderer, i, rig, dark = 0) {
        const e = K.eyes[i], t = K.eyeTarget(i); if (!e || !t) return;
        const ac = renderer.autoClear; renderer.autoClear = false;      // lapisan di atas gambar mata (tanpa membersihkan)
        renderer.setRenderTarget(t);
        const pp = K.panelPose();
        if (pp) {
          if (P.dirty) { K.drawPanel(); panelTex.needsUpdate = true; }
          panel.matrix.copy(rig).multiply(m4.fromArray(pp.m)); panel.matrixWorld.copy(panel.matrix); panel.visible = true;
          const I = K.in;
          if (I && I.ray) { ray.matrix.copy(rig).multiply(m4.fromArray(I.ray.m)).multiply(new THREE.Matrix4().makeScale(1, 1, P.hit ? P.hit[3] : 3)); ray.matrixWorld.copy(ray.matrix); ray.visible = true; } else ray.visible = false;
          cam.matrixWorld.copy(rig).multiply(m4.fromArray(e.world)); cam.matrixWorldInverse.copy(cam.matrixWorld).invert(); cam.projectionMatrix.fromArray(e.proj); cam.projectionMatrixInverse.copy(cam.projectionMatrix).invert();
          renderer.render(ui, cam);
        }
        if (K.vig > 0.01 || dark > 0.001) { vig.material.uniforms.uK.value = K.vig; vig.material.uniforms.uDark.value = dark; renderer.render(vigS, ortho); }
        renderer.autoClear = ac;
      },
    };
    return K._three;
  };
})();
