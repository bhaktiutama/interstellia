/* =====================================================================
   XR tiruan untuk uji otomatis VR (rencana VR, docs/app/rencana-vr.md, tahap VR7). Disuntik sebelum skrip halaman
   (Playwright add_init_script). Tidak dipakai halaman mana pun secara langsung.

   Meniru WebXR secukupnya untuk three.js 0.186.1 (jalur XRWebGLLayer) dan WebGL mentah:
   - navigator.xr.isSessionSupported('immersive-vr') = true, requestSession() -> XRSession tiruan
   - XRWebGLLayer: framebuffer biasa (warna + kedalaman) selebar dua mata sisi-ke-sisi (bawaan 2 x 320 x 360)
   - frame.getViewerPose(): dua mata dengan IPD 0,064 m, frustum tidak simetris seperti Rift (sisi luar lebih lebar)
   - dua kontroler Touch (gamepad xr-standard: 0 picu, 1 genggam, 3 stik ditekan, 4 A/X, 5 B/Y; sumbu 2-3 = stik)
   - XRWebGLBinding dihapus agar three.js memakai XRWebGLLayer (bukan lapisan proyeksi)
   Kendali uji lewat window.__xrTiruan: head { p: [x, y, z], yaw, pitch }, pad(h, i, nilai), axes(h, x, y),
   sel(h) (event select), readEye(i) -> { w, h, rgba } dan stats { frames, lastViews }.
   ===================================================================== */
(() => {
  'use strict';
  const W = 320, H = 360, IPD = 0.064, NEAR_FALLBACK = 0.05;
  const T = window.__xrTiruan = {
    head: { p: [0, 1.6, 0], yaw: 0, pitch: 0 }, size: [W, H], frames: 0, lastViews: null, session: null, gl: null, fb: null,
    hands: {
      left: { p: [-0.2, 1.2, -0.35], buttons: Array.from({ length: 7 }, () => ({ pressed: false, touched: false, value: 0 })), axes: [0, 0, 0, 0] },
      right: { p: [0.2, 1.2, -0.35], buttons: Array.from({ length: 7 }, () => ({ pressed: false, touched: false, value: 0 })), axes: [0, 0, 0, 0] },
    },
    pad(h, i, v) { const b = T.hands[h].buttons[i]; b.value = v; b.pressed = v > 0.5; b.touched = v > 0; },
    axes(h, x, y) { const a = T.hands[h].axes; a[2] = x; a[3] = y; },
    sel(h) { const s = T.session; if (!s) return; const src = s.inputSources.find((x) => x.handedness === h); for (const t of ['selectstart', 'select', 'selectend']) s._emit(t, { inputSource: src, frame: s._lastFrame }); },
    readEye(i) {
      const gl = T.gl; if (!gl || !T.fb) return null;
      const px = new Uint8Array(W * H * 4), prev = gl.getParameter(gl.FRAMEBUFFER_BINDING);
      gl.bindFramebuffer(gl.FRAMEBUFFER, T.fb); gl.readPixels(i * W, 0, W, H, gl.RGBA, gl.UNSIGNED_BYTE, px); gl.bindFramebuffer(gl.FRAMEBUFFER, prev);
      return { w: W, h: H, rgba: Array.from(px) };
    },
  };
  // --- matematika kecil (kolom-mayor seperti WebXR / WebGL) ---
  const mul = (a, b) => { const o = new Array(16).fill(0); for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) for (let k = 0; k < 4; k++) o[c * 4 + r] += a[k * 4 + r] * b[c * 4 + k]; return o; };
  const rigid = (p, yaw, pitch) => {                                   // rotasi yaw (sumbu y) lalu pitch (sumbu x), lalu translasi
    const cy = Math.cos(yaw), sy = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch);
    const Ry = [cy, 0, -sy, 0, 0, 1, 0, 0, sy, 0, cy, 0, 0, 0, 0, 1], Rx = [1, 0, 0, 0, 0, cp, sp, 0, 0, -sp, cp, 0, 0, 0, 0, 1];
    const m = mul(Ry, Rx); m[12] = p[0]; m[13] = p[1]; m[14] = p[2]; return m;
  };
  const inv = (m) => {                                                 // invers transformasi kaku
    const r = [m[0], m[4], m[8], 0, m[1], m[5], m[9], 0, m[2], m[6], m[10], 0, 0, 0, 0, 1], t = [m[12], m[13], m[14]];
    r[12] = -(r[0] * t[0] + r[4] * t[1] + r[8] * t[2]); r[13] = -(r[1] * t[0] + r[5] * t[1] + r[9] * t[2]); r[14] = -(r[2] * t[0] + r[6] * t[1] + r[10] * t[2]);
    return r;
  };
  const quatOf = (m) => {
    const tr = m[0] + m[5] + m[10]; let x, y, z, w;
    if (tr > 0) { const s = Math.sqrt(tr + 1) * 2; w = 0.25 * s; x = (m[6] - m[9]) / s; y = (m[8] - m[2]) / s; z = (m[1] - m[4]) / s; }
    else if (m[0] > m[5] && m[0] > m[10]) { const s = Math.sqrt(1 + m[0] - m[5] - m[10]) * 2; w = (m[6] - m[9]) / s; x = 0.25 * s; y = (m[4] + m[1]) / s; z = (m[8] + m[2]) / s; }
    else if (m[5] > m[10]) { const s = Math.sqrt(1 + m[5] - m[0] - m[10]) * 2; w = (m[8] - m[2]) / s; x = (m[4] + m[1]) / s; y = 0.25 * s; z = (m[9] + m[6]) / s; }
    else { const s = Math.sqrt(1 + m[10] - m[0] - m[5]) * 2; w = (m[1] - m[4]) / s; x = (m[8] + m[2]) / s; y = (m[9] + m[6]) / s; z = 0.25 * s; }
    return { x, y, z, w };
  };
  const frustum = (l, r, b, t, n, f) => [2 * n / (r - l), 0, 0, 0, 0, 2 * n / (t - b), 0, 0, (r + l) / (r - l), (t + b) / (t - b), -(f + n) / (f - n), -1, 0, 0, -2 * f * n / (f - n), 0];
  class RigidT {
    constructor(m) { this.matrix = new Float32Array(m); this.position = { x: m[12], y: m[13], z: m[14], w: 1 }; this.orientation = quatOf(m); }
    get inverse() { return new RigidT(inv(Array.from(this.matrix))); }
  }
  class Space { constructor(kind, h) { this.kind = kind; this.h = h; } getOffsetReferenceSpace() { return this; } addEventListener() {} removeEventListener() {} }
  class Session extends EventTarget {
    constructor(mode) {
      super(); this.mode = mode; this.renderState = { baseLayer: null, depthNear: 0.1, depthFar: 1000, inlineVerticalFieldOfView: null };
      this.environmentBlendMode = 'opaque'; this.visibilityState = 'visible'; this.enabledFeatures = ['local', 'local-floor', 'viewer'];
      this.inputSources = ['left', 'right'].map((h) => ({ handedness: h, targetRayMode: 'tracked-pointer', profiles: ['oculus-touch', 'generic-trigger-squeeze-thumbstick'],
        targetRaySpace: new Space('ray', h), gripSpace: new Space('grip', h), hand: null,
        gamepad: { id: 'tiruan', mapping: 'xr-standard', connected: true, buttons: T.hands[h].buttons, axes: T.hands[h].axes, hapticActuators: [] } }));
      this._cbs = []; this._id = 0; this._ended = false; this._lastFrame = null; T.session = this;
      setTimeout(() => this._emit('inputsourceschange', { added: this.inputSources, removed: [] }), 0);
    }
    _emit(type, extra) { const e = new Event(type); Object.assign(e, extra || {}, { session: this }); this.dispatchEvent(e); const h = this['on' + type]; if (typeof h === 'function') h.call(this, e); }
    updateRenderState(s) { Object.assign(this.renderState, s); }
    requestReferenceSpace(type) { return Promise.resolve(new Space(type)); }
    supportedFrameRates = new Float32Array([90]);
    updateTargetFrameRate() { return Promise.resolve(); }
    requestAnimationFrame(cb) {
      const id = ++this._id; this._cbs.push([id, cb]);
      if (this._cbs.length === 1) window.requestAnimationFrame((t) => this._tick(t));
      return id;
    }
    cancelAnimationFrame(id) { this._cbs = this._cbs.filter((c) => c[0] !== id); }
    _tick(t) {
      if (this._ended) return;
      const cbs = this._cbs; this._cbs = [];
      const frame = new Frame(this); this._lastFrame = frame; T.frames++;
      for (const [, cb] of cbs) { try { cb(t, frame); } catch (e) { setTimeout(() => { throw e; }); } }
      frame.active = false;
      if (T.mirror !== false && T.fb && T.gl) {                       // salinan ke kanvas agar tangkapan layar menampilkan kedua mata
        const gl = T.gl, prevR = gl.getParameter(gl.READ_FRAMEBUFFER_BINDING), prevD = gl.getParameter(gl.DRAW_FRAMEBUFFER_BINDING);
        gl.bindFramebuffer(gl.READ_FRAMEBUFFER, T.fb); gl.bindFramebuffer(gl.DRAW_FRAMEBUFFER, null);
        gl.blitFramebuffer(0, 0, 2 * W, H, 0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight, gl.COLOR_BUFFER_BIT, gl.LINEAR);
        gl.bindFramebuffer(gl.READ_FRAMEBUFFER, prevR); gl.bindFramebuffer(gl.DRAW_FRAMEBUFFER, prevD);
      }
    }
    end() { if (this._ended) return Promise.resolve(); this._ended = true; T.session = null; this._emit('end'); return Promise.resolve(); }
  }
  class Frame {
    constructor(session) { this.session = session; this.active = true; this.predictedDisplayTime = performance.now(); }
    _head() { const h = T.head; return rigid(h.p, h.yaw, h.pitch); }
    getViewerPose() {
      const hm = this._head(), n = this.session.renderState.depthNear || NEAR_FALLBACK, f = this.session.renderState.depthFar || 1000;
      const views = [-1, 1].map((sgn, i) => {
        const em = mul(hm, [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, sgn * IPD / 2, 0, 0, 1]);
        const tin = 0.85, tout = 1.15, tv = 1.1;                       // tan setengah sudut: sisi dalam / luar / atas-bawah (frustum tidak simetris)
        const l = sgn < 0 ? -tout : -tin, r = sgn < 0 ? tin : tout;
        return { eye: sgn < 0 ? 'left' : 'right', projectionMatrix: new Float32Array(frustum(l * n, r * n, -tv * n, tv * n, n, f)), transform: new RigidT(em), recommendedViewportScale: 1, requestViewportScale() {}, _i: i };
      });
      T.lastViews = views.map((v) => ({ eye: v.eye, p: Array.from(v.projectionMatrix), m: Array.from(v.transform.matrix) }));
      return { transform: new RigidT(hm), views, emulatedPosition: false };
    }
    getPose(space) {
      if (!space || !space.h) return { transform: new RigidT(this._head()), emulatedPosition: false };
      const H = T.hands[space.h], m = rigid(H.p, T.head.yaw, space.kind === 'ray' ? -0.6 : 0);
      return { transform: new RigidT(m), emulatedPosition: false, linearVelocity: null, angularVelocity: null };
    }
    getJointPose() { return null; }
    fillPoses() { return false; }
  }
  class Layer {
    constructor(session, gl, opt) {
      T.gl = gl; this.antialias = !!(opt && opt.antialias); this.ignoreDepthValues = false; this.fixedFoveation = 0;
      this.framebufferWidth = 2 * W; this.framebufferHeight = H;
      const fb = gl.createFramebuffer(), c = gl.createRenderbuffer(), d = gl.createRenderbuffer(), prev = gl.getParameter(gl.FRAMEBUFFER_BINDING);
      gl.bindRenderbuffer(gl.RENDERBUFFER, c); gl.renderbufferStorage(gl.RENDERBUFFER, gl.RGBA8, 2 * W, H);
      gl.bindRenderbuffer(gl.RENDERBUFFER, d); gl.renderbufferStorage(gl.RENDERBUFFER, gl.DEPTH24_STENCIL8, 2 * W, H);
      gl.bindFramebuffer(gl.FRAMEBUFFER, fb);
      gl.framebufferRenderbuffer(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.RENDERBUFFER, c);
      gl.framebufferRenderbuffer(gl.FRAMEBUFFER, gl.DEPTH_STENCIL_ATTACHMENT, gl.RENDERBUFFER, d);
      gl.bindFramebuffer(gl.FRAMEBUFFER, prev);
      this.framebuffer = fb; T.fb = fb;
    }
    getViewport(view) { return { x: view._i * W, y: 0, width: W, height: H }; }
    static getNativeFramebufferScaleFactor() { return 1; }
  }
  try { delete window.XRWebGLBinding; } catch (e) { /* abaikan */ }
  window.XRWebGLBinding = undefined;
  window.XRWebGLLayer = Layer;
  window.XRRigidTransform = RigidT;
  const xr = new EventTarget();
  xr.isSessionSupported = (mode) => Promise.resolve(mode === 'immersive-vr' || mode === 'inline');
  xr.requestSession = (mode) => Promise.resolve(new Session(mode));
  Object.defineProperty(navigator, 'xr', { value: xr, configurable: true });
  // Chrome punya makeXRCompatible asli yang menolak tanpa perangkat XR: selalu diganti di tiruan
  for (const C of [WebGLRenderingContext, WebGL2RenderingContext]) C.prototype.makeXRCompatible = function () { return Promise.resolve(); };
})();
