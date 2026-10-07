/* shared/camera.js: kamera rangefinder bersama (Rencana K, docs/app/rencana-kamera-rangefinder.md).
   Skrip biasa (bukan modul) agar jalan dari file://, mengisi window.CAMKIT. Tanpa three.js.
   Isi: tabel lensa / aperture / rana / ISO, rumus eksposur dan lensa, setelan tersimpan (localStorage lazarus.camera),
   nilai uniform shader (CAMKIT.U, dipakai GLSL CAMKIT.GLSL_U + CAMKIT.GLSL_F), overlay jendela bidik (garis bingkai, patch,
   HUD LED) dan live view, panel, bantuan, tombol lokal, rencana subframe tangkap foto, simpan PNG / JPEG + metadata,
   perekam video (MediaRecorder + audio), bunyi rana.
   Tiap experience menyediakan adaptor lewat CAMKIT.init(A):
     A.app (nama berkas), A.canvas, A.lang() 'id' | 'en', A.ev0 (EV100 saat luminans meter = A.key), A.key,
     A.exit() keluar mode kamera, A.isLocked(), A.unlock(), A.audio() -> { ctx, node } | null (rekam suara),
     A.quality() -> jumlah subframe dasar, A.freeMode() (opsional, pindah ke Foto bebas), A.minFocus (opsional).
   Satuan jarak meter. Kalibrasi eksposur relatif terhadap tampilan sekarang (lihat rencana), bukan luminans fisik. */
(function () {
  'use strict';

  // ---------- tabel ----------
  const LENSES = [
    { f: 21, nMax: 2.8, minF: 0.7, pair: null },
    { f: 28, nMax: 2.8, minF: 0.7, pair: 90 },
    { f: 35, nMax: 1.4, minF: 0.7, pair: 135 },
    { f: 50, nMax: 1.4, minF: 0.7, pair: 75 },
    { f: 75, nMax: 2, minF: 0.7, pair: 50 },
    { f: 90, nMax: 2.4, minF: 1.0, pair: 28 },
  ];
  const APERTURES = [1.4, 1.7, 2, 2.4, 2.8, 3.4, 4, 4.8, 5.6, 6.7, 8, 9.5, 11, 13, 16];
  const SHUTTERS = [1 / 4000, 1 / 2000, 1 / 1000, 1 / 500, 1 / 250, 1 / 125, 1 / 60, 1 / 30, 1 / 15, 1 / 8, 1 / 4, 1 / 2, 1, 2, 4, 8, Infinity];   // Infinity = B
  const ISOS = [100, 125, 160, 200, 250, 320, 400, 500, 640, 800, 1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6400, 8000, 10000, 12800];
  const THIRDS = [4000, 3200, 2500, 2000, 1600, 1250, 1000, 800, 640, 500, 400, 320, 250, 200, 160, 125, 100, 80, 60, 50, 40, 30, 25, 20, 15, 13, 10, 8, 6, 5, 4, 3];
  const LONG = [0.4, 0.5, 0.6, 0.8, 1, 1.3, 1.6, 2, 2.5, 3.2, 4, 5, 6, 8, 10, 13, 15, 20, 25, 30];
  const BLADES = 9, BASE_RF = 0.05, LENS_OFF = [0.042, -0.022];   // basis rangefinder efektif (m), lensa relatif jendela bidik (kanan, atas) m
  const FIELD_T = Math.tan(34 * Math.PI / 180);                    // setengah bidang jendela pada pembesaran 0,72x
  const NOISE_A = 1e-4, NOISE_B = 6e-9;                            // nilai awal derau (disetel pemilik)
  const BULB_MAX = 30, REC_MAX = 600;

  // ---------- rumus (dipakai uji Node juga) ----------
  const log2 = Math.log2;
  function ev100(N, t, iso) { return log2(N * N / t) - log2(iso / 100); }
  function cocMM(fmm, N, s, d) { const f = fmm / 1000; return f * f / (N * (s - f)) * Math.abs(d - s) / d * 1000; }
  function hyperfocal(fmm, N, c0) { const f = fmm / 1000; return f * f / (N * ((c0 || 0.03) / 1000)) + f; }
  function apertureR(fmm, N) { return fmm / 1000 / (2 * N); }      // jari-jari bukaan (m)
  function fovV(fmm, aspect) { return 2 * Math.atan(18 / fmm / aspect) * 180 / Math.PI; }   // bidang vertikal bila lebar 36 mm menutup aspek
  function fovH(fmm) { return 2 * Math.atan(18 / fmm) * 180 / Math.PI; }
  function rfShift(B, d, s) { return B * (1 / d - 1 / s); }          // radian
  function dofRange(fmm, N, s) {                                     // batas tajam dekat / jauh (m), c0 0,03 mm
    const H = hyperfocal(fmm, N), f = fmm / 1000;
    if (!isFinite(s)) return [H, Infinity];
    const near = s * (H - f) / (H + s - 2 * f), far = s >= H ? Infinity : s * (H - f) / (H - s);
    return [near, far];
  }
  function halton(i, b) { let f = 1, r = 0; while (i > 0) { f /= b; r += f * (i % b); i = Math.floor(i / b); } return r; }
  function bladeSample(i, N, nMax) {                                 // titik di bukaan berbilah (koordinat satuan, jari-jari 1)
    const u = halton(i + 1, 5) * 2 - 1, v = halton(i + 1, 7) * 2 - 1;
    if (u === 0 && v === 0) return [0, 0];
    let r, a;                                                        // pemetaan konsentris Shirley (cakram merata)
    if (Math.abs(u) > Math.abs(v)) { r = u; a = Math.PI / 4 * (v / u); } else { r = v; a = Math.PI / 2 - Math.PI / 4 * (u / v); }
    const x = r * Math.cos(a), y = r * Math.sin(a), ang = Math.atan2(y, x);
    const round = Math.max(0, Math.min(1, 1 - log2(N / nMax) / 2.5));   // bukaan penuh = bulat, diciutkan = poligon 9 sisi
    const seg = 2 * Math.PI / BLADES, m = (((ang + 0.3) % seg) + seg) % seg - seg / 2;
    const k = round + (1 - round) * Math.cos(seg / 2) / Math.cos(m);  // jari-jari tepi poligon (titik sudut di lingkaran)
    return [x * k, y * k];
  }
  function shutterLabel(t) {
    if (!isFinite(t)) return 'B';
    if (t >= 0.35) { let b = LONG[0]; for (const x of LONG) if (Math.abs(log2(x / t)) < Math.abs(log2(b / t))) b = x; return String(b).replace('.', ',') + 's'; }
    let b = THIRDS[0]; for (const x of THIRDS) if (Math.abs(log2(t * x)) < Math.abs(log2(t * b))) b = x;
    return '1/' + b;
  }
  function fmtF(N) { return String(N).replace('.', ','); }
  function fmtDist(d) { return !isFinite(d) || d > 999 ? '∞' : d < 10 ? d.toFixed(1).replace('.', ',') + ' m' : Math.round(d) + ' m'; }

  // ---------- teks (dua bahasa, tidak lewat kamus experience) ----------
  const STR = {
    title: ['Kamera rangefinder', 'Rangefinder camera'], mode: ['Mode', 'Mode'], lens: ['Lensa', 'Lens'], ap: ['Aperture', 'Aperture'],
    sh: ['Rana', 'Shutter'], iso: ['ISO', 'ISO'], comp: ['Kompensasi', 'Compensation'], focus: ['Fokus', 'Focus'],
    kind: ['Rekam', 'Capture'], photo: ['Foto', 'Photo'], video: ['Video', 'Video'], view: ['Tampilan', 'View'],
    finder: ['Jendela bidik', 'Viewfinder'], live: ['Live view', 'Live view'], mag: ['Pembesaran', 'Magnification'],
    tripod: ['Tripod', 'Tripod'], shake: ['Getar tangan', 'Hand shake'], fmt: ['Format', 'Format'], fps: ['Video fps', 'Video fps'],
    rate: ['Bitrate', 'Bitrate'], on: ['nyala', 'on'], off: ['mati', 'off'], free: ['Foto bebas', 'Free photo'], exit: ['Keluar (F)', 'Exit (F)'],
    help: ['Bantuan (?)', 'Help (?)'], dof: ['Tajam', 'In focus'], saved: ['Tersimpan', 'Saved'], busy: ['Memproses...', 'Processing...'],
    recSaved: ['Video tersimpan', 'Video saved'], noRec: ['Perekam video tidak didukung browser ini', 'Video recording is not supported by this browser'],
    recMax: ['Batas 10 menit tercapai', '10 minute limit reached'], ael: ['AE-L', 'AE-L'], hold: ['tahan', 'hold'],
    helpTitle: ['Tombol kamera', 'Camera keys'],
    keys: [[
      ['Klik kiri / Enter', 'Rana (foto) atau mulai / berhenti rekam (video); rana B: tahan'],
      ['Roda mouse', 'Cincin fokus: satukan dua gambar di patch tengah'], ['Shift + roda, atau , .', 'Aperture'],
      ['[ ]', 'Kecepatan rana (mode A / P pindah ke M)'], ['- =', 'ISO'], ['Shift + - =', 'Kompensasi eksposur (mode A dan P)'],
      ['1-6', 'Lensa 21 / 28 / 35 / 50 / 75 / 90 mm'], ['Tab', 'Foto / video'], ['V', 'Jendela bidik optik / live view'],
      ['Klik kanan tahan', 'Kunci eksposur (AE-L)'], ['H', 'Sembunyikan HUD'], ['`', 'Panel kamera'], ['WASD, Shift, mouse, Z', 'Tetap: jalan, lari, menoleh, kecepatan waktu'],
      ['F / Esc', 'Keluar mode kamera'],
    ], [
      ['Left click / Enter', 'Shutter (photo) or start / stop recording (video); B shutter: hold'],
      ['Mouse wheel', 'Focus ring: merge the two images in the centre patch'], ['Shift + wheel, or , .', 'Aperture'],
      ['[ ]', 'Shutter speed (A / P mode switches to M)'], ['- =', 'ISO'], ['Shift + - =', 'Exposure compensation (A and P)'],
      ['1-6', 'Lens 21 / 28 / 35 / 50 / 75 / 90 mm'], ['Tab', 'Photo / video'], ['V', 'Optical viewfinder / live view'],
      ['Right click hold', 'Exposure lock (AE-L)'], ['H', 'Hide HUD'], ['`', 'Camera panel'], ['WASD, Shift, mouse, Z', 'Unchanged: walk, run, look, time speed'],
      ['F / Esc', 'Exit camera mode'],
    ]],
  };

  const K = {
    LENSES, APERTURES, SHUTTERS, ISOS, BLADES, BASE_RF, LENS_OFF, FIELD_T, NOISE_A, NOISE_B,
    ev100, cocMM, hyperfocal, apertureR, fovV, fovH, rfShift, dofRange, halton, bladeSample, shutterLabel,
    on: false, A: null, cap: null, rec: null, L: null, lock: null, hud: true, panel: false, helpOn: false, seed: 0,
    st: { lens: 3, N: 2.8, sh: 5, iso: 200, mode: 'A', comp: 0, invS: 1 / 3, video: false, live: false, mag: 0.72,
      tripod: false, shake: true, fmt: 'png', fps: 30, mbps: 8 },
    U: { E: [0, 1, 0, 0], L: [0, 0, 0, 0], R: [0, 0, 0, 0], M: [0, 0, 0, 0] },
  };
  try { const s = JSON.parse(localStorage.getItem('lazarus.camera') || 'null'); if (s && typeof s === 'object') Object.assign(K.st, s); } catch (e) { /* abaikan */ }
  K.st.live = false;
  function save() { try { localStorage.setItem('lazarus.camera', JSON.stringify(K.st)); } catch (e) { /* abaikan */ } }
  const T = (k) => { const s = STR[k]; return s ? s[K.A && K.A.lang && K.A.lang() === 'en' ? 1 : 0] : k; };
  const lens = () => LENSES[Math.max(0, Math.min(LENSES.length - 1, K.st.lens | 0))];

  // ---------- eksposur ----------
  // EV meter: EV0 saat luminans adaptasi = key; tiap kali luminans x2 = +1 EV. Pengali gambar = 2^(EV0 - EV setelan)
  // (setelan = meter -> sama dengan adaptasi penuh key / L). Mode A: rana tanpa langkah; P: garis program sederhana.
  function evMeter() { const A = K.A, L = K.lock != null ? K.lock : (K.L || A.key); return A.ev0 + log2(Math.max(L, 1e-6) / A.key); }
  function clampN(N) { return Math.max(lens().nMax, Math.min(16, N)); }
  function cur() {
    const s = K.st, Ln = lens(), evm = evMeter(), isoK = log2(s.iso / 100);
    let N = clampN(s.N), t = SHUTTERS[s.sh], mode = s.mode;
    if (mode === 'A') t = N * N / Math.pow(2, evm - s.comp + isoK);
    else if (mode === 'P') {
      const target = evm - s.comp + isoK, tt = 1 / Math.max(60, Ln.f);
      N = clampN(Math.sqrt(tt * Math.pow(2, target))); N = APERTURES.reduce((b, x) => (Math.abs(log2(x / N)) < Math.abs(log2(b / N)) ? x : b), APERTURES[APERTURES.length - 1]); N = clampN(N);
      t = N * N / Math.pow(2, target);
    }
    if (mode !== 'M' || isFinite(t)) t = Math.max(1 / 4000, Math.min(8, t));
    if (K.st.video) t = Math.min(t, 1 / K.st.fps);                  // video: rana tidak lebih lambat dari satu frame
    const bulb = !isFinite(t);
    const ev = bulb ? NaN : ev100(N, t, s.iso);
    return { f: Ln.f, nMax: Ln.nMax, minF: Ln.minF, N, t, iso: s.iso, mode, evm, ev, bulb, over: bulb ? 0 : evm - ev,
      mul: Math.pow(2, K.A.ev0 - (bulb ? ev100(N, 1, s.iso) : ev)) };
  }
  K.cur = () => cur();
  K.meter = (L) => { if (L > 0 && isFinite(L)) K.L = L; };

  // ---------- geometri layar ----------
  function finderGeo(W, H) {                                         // jendela bidik di tengah kanvas (px CSS)
    const wh = H * 0.9, ww = Math.min(W * 0.96, wh * 1.62);
    return { ww, wh, cx: W / 2, cy: H / 2, T: FIELD_T * 0.72 / K.st.mag };
  }
  function frameRect(W, H) {                                         // bingkai foto 3:2 / video (seluruh kanvas) dalam piksel
    if (K.st.video) return { x: 0, y: 0, w: W, h: H };
    const a = W / H;
    if (a >= 1.5) { const w = H * 1.5; return { x: (W - w) / 2, y: 0, w, h: H }; }
    const h = W / 1.5; return { x: 0, y: (H - h) / 2, w: W, h };
  }
  function liveTanV(W, H) {                                          // tan setengah bidang vertikal live view / tangkap
    const f = lens().f, a = W / H;
    if (K.st.video) return 18 / f / a;
    return a >= 1.5 ? 12 / f : 18 / f / a;
  }
  K.frameRect = frameRect;

  // Parameter render frame ini. W, H = ukuran target render (piksel). Keluaran: vfov (derajat), eye (offset lensa m
  // dalam basis kamera: kanan, atas), live, dan K.U terisi untuk shader.
  K.view = function (W, H, capturing) {
    const s = K.st, c = cur(), live = capturing || s.live || s.video, A = K.A, U = K.U;
    const cw = A.canvas.clientWidth || W, ch = A.canvas.clientHeight || H, G = finderGeo(cw, ch);
    let tanV, eye = [0, 0];
    if (live) { tanV = liveTanV(W, H); eye = LENS_OFF.slice(); } else tanV = G.T * ch / G.ww;
    const invS = Math.max(0, Math.min(1 / c.minF, s.invS));
    // eksposur + derau: jendela bidik optik = mata biasa
    if (live) {
      U.E[0] = 1; U.E[1] = c.mul; U.E[2] = NOISE_A * c.iso / 100; U.E[3] = NOISE_B * Math.pow(c.iso / 100, 2);
    } else { U.E[0] = 0; U.E[1] = 1; U.E[2] = 0; U.E[3] = 0; }
    // DOF real-time (live view saja, tangkap foto memakai sampel bukaan)
    const fr = frameRect(W, H), hs = s.video ? 0.036 / (W / H) : 0.024, fm = c.f / 1000;
    const k = fm * fm / (c.N * Math.max(1e-3, 1 - fm * invS));
    U.L[0] = live && !capturing ? 1 : 0; U.L[1] = k * fr.h / hs; U.L[2] = invS; U.L[3] = 0.035 * H;
    // patch rangefinder (jendela bidik optik)
    U.R[0] = !live && K.hud ? 1 : 0; U.R[1] = 0.035 * G.ww / cw; U.R[2] = 0.026 * G.ww / ch; U.R[3] = BASE_RF / G.T * (G.ww / 2) / cw;
    // motion blur video (bagian frame yang terbuka), benih derau, vinyet lensa
    U.M[0] = live && s.video && !capturing ? Math.min(1, c.t * s.fps) : 0;
    U.M[1] = capturing ? K.seed : (K.seed = (K.seed + 1) % 997);
    const open = Math.max(0, Math.min(1, 1 - log2(c.N / c.nMax) / 2));
    U.M[2] = live ? (0.04 * 35 / c.f + 0.15 * open * Math.min(1.3, 35 / c.f)) : 0;
    U.M[3] = capturing ? 1 : 0;
    return { vfov: 2 * Math.atan(tanV) * 180 / Math.PI, eye, live, invS, c };
  };

  // ---------- GLSL bersama ----------
  // Host mendefinisikan (sesudah GLSL_U, sebelum GLSL_F): vec3 camHdr(vec2 uv), float camDist(vec2 uv) (m, langit besar),
  // vec2 camPrevUv(vec2 uv) (posisi layar frame lalu; boleh kembalikan uv bila tanpa motion blur).
  K.GLSL_U = `
  uniform vec4 uCamE;   // x mode (0 mata, 1 kamera), y pengali eksposur, z derau a, w derau b
  uniform vec4 uCamL;   // x DOF real-time, y diameter CoC px per dioptri, z 1/s, w jari-jari maks px
  uniform vec4 uCamR;   // x patch rangefinder, y / z setengah ukuran (uv), w geser uv per dioptri
  uniform vec4 uCamM;   // x motion blur (bagian frame), y benih derau, z vinyet lensa, w 1 = tangkap
  uniform vec2 uCamT;   // texel target`;
  K.GLSL_F = `
  float camH(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
  float camCoc(float d) { return min(0.5 * uCamL.y * abs(uCamL.z - 1.0 / max(d, 0.05)), uCamL.w); }
  vec3 camDof(vec2 uv, vec3 c0) {                                  // gather 32 tap; tap tajam tidak bocor ke latar kabur
    float r0 = camCoc(camDist(uv));
    if (r0 < 0.6) return c0;
    vec3 s = c0; float ws = 1.0;
    for (int k = 0; k < 32; k++) {
      float rk = sqrt((float(k) + 0.5) / 32.0) * r0, a = float(k) * 2.39996323;
      vec2 tuv = uv + vec2(cos(a), sin(a)) * rk * uCamT;
      float w = clamp(camCoc(camDist(tuv)) - rk + 1.0, 0.0, 1.0);
      s += camHdr(tuv) * w; ws += w;
    }
    return s / ws;
  }
  vec3 camRf(vec2 uv, vec3 c) {                                    // patch tengah: gambar kedua bergeser B (1/d - 1/s)
    vec2 q = abs(uv - 0.5);
    float m = (1.0 - smoothstep(uCamR.y * 0.9, uCamR.y, q.x)) * (1.0 - smoothstep(uCamR.z * 0.85, uCamR.z, q.y));
    if (m <= 0.0) return c;
    float sh = uCamR.w * (1.0 / max(camDist(uv), 0.05) - uCamL.z);
    vec2 su = clamp(uv + vec2(sh, 0.0), vec2(0.0), vec2(1.0));
    sh = uCamR.w * (1.0 / max(camDist(su), 0.05) - uCamL.z);       // satu iterasi: kedalaman titik yang benar-benar tampil
    su = clamp(uv + vec2(sh, 0.0), vec2(0.0), vec2(1.0));
    vec3 p = (0.58 * c + 0.58 * camHdr(su)) * vec3(1.07, 1.0, 0.74);
    return mix(c, p, m);
  }
  vec3 camMB(vec2 uv, vec3 c) {                                    // blur kamera video dari proyeksi ulang kedalaman
    vec2 v = (uv - camPrevUv(uv)) * uCamM.x;
    if (dot(v / uCamT, v / uCamT) < 1.0) return c;
    v = clamp(v, -0.08, 0.08);
    vec3 s = vec3(0.0);
    for (int k = 0; k < 8; k++) s += camHdr(uv + v * ((float(k) + 0.5) / 8.0 - 0.5));
    return s / 8.0;
  }
  vec3 camPre(vec2 uv, vec3 c) {                                   // di HDR sebelum bloom / eksposur
    if (uCamM.x > 0.0) c = camMB(uv, c);
    else if (uCamL.x > 0.5) c = camDof(uv, c);
    if (uCamR.x > 0.5) c = camRf(uv, c);
    return c;
  }
  float camMul(float eye) { return uCamE.x > 0.5 ? uCamE.y : eye; }
  vec3 camPost(vec2 uv, vec3 x) {                                  // sesudah eksposur, sebelum tone map: vinyet lensa + derau ISO
    if (uCamE.x < 0.5) return x;
    vec2 q = (uv - 0.5) * vec2(uCamT.y / max(uCamT.x, 1e-6), 1.0);
    float r2 = dot(q, q) / max(0.25 * (1.0 + (uCamT.y * uCamT.y) / max(uCamT.x * uCamT.x, 1e-12)), 1e-6);
    x *= 1.0 - uCamM.z * clamp(r2, 0.0, 1.0);
    vec2 p = gl_FragCoord.xy + uCamM.y * vec2(37.0, 17.0);
    float g = (camH(p) + camH(p + 3.1) + camH(p + 7.7) + camH(p + 11.3) - 2.0) * 1.732;   // kira-kira normal(0, 1)
    vec3 gc = vec3(camH(p + 19.1), camH(p + 23.3), camH(p + 29.9)) - 0.5;
    float l = max(dot(x, vec3(0.2126, 0.7152, 0.0722)), 0.0);
    float sg = sqrt(max(uCamE.z * l + uCamE.w, 0.0));               // varians = a x + b (tidak pernah negatif)
    return max(x + sg * (vec3(g) + gc * 1.2), vec3(0.0));
  }`;

  // ---------- tangkap foto: rencana subframe ----------
  K.shutterPress = function () {
    if (!K.on || K.cap || K.armed) return;
    if (K.st.video) { K.rec ? K.recStop() : K.recStart(); return; }
    K.armed = true; click(0);
  };
  K.shutterRelease = function () { if (K.cap && K.cap.bulb && !K.cap.done) K.cap.release = true; };
  function plan() {
    const c = cur(), A = K.A, base = Math.max(4, Math.min(64, (A.quality && A.quality()) || 16));
    const moving = c.bulb || c.t >= 1 / 500;
    const N = c.bulb ? Infinity : moving ? Math.max(base, Math.min(256, Math.round(c.t * 120))) : base;
    const ph = [0, 1, 2, 3].map(() => Math.random() * 6.2832);
    const shakeK = K.st.tripod || !K.st.shake ? 0 : 1;
    return { c, N, i: 0, bulb: c.bulb, t: c.t, dt: c.bulb ? 0 : moving ? c.t / N : 0, moving, elapsed: 0, release: false, done: false,
      invS: Math.max(0, Math.min(1 / c.minF, K.st.invS)), apR: apertureR(c.f, c.N), ph, shakeK, mul: c.mul, t0: performance.now() };
  }
  // Dipanggil adaptor di akhir frame biasa (setelah gambar tampil di kanvas, tugas yang sama)
  K.afterFrame = function (canvas) {
    if (K.unfreeze) { K.unfreeze = false; freezeEl.hidden = true; }
    if (K.armed) {
      K.armed = false;
      try { const g = freezeEl.getContext('2d'); freezeEl.width = canvas.width; freezeEl.height = canvas.height; g.drawImage(canvas, 0, 0); freezeEl.hidden = false; } catch (e) { /* abaikan */ }
      K.seed = (Math.random() * 997) | 0;
      K.cap = plan();
    }
  };
  // Subframe berikut: offset Halton (piksel), bukaan (m, basis kamera), getar (rad), dt dunia sebelum subframe ini
  K.sub = function (dtReal) {
    const P = K.cap, i = P.i, s = { i, jx: halton(i + 1, 2) - 0.5, jy: halton(i + 1, 3) - 0.5, ax: 0, ay: 0, yaw: 0, pitch: 0, dt: 0, invS: P.invS };
    const b = bladeSample(i, P.c.N, P.c.nMax); s.ax = b[0] * P.apR; s.ay = b[1] * P.apR;
    if (P.bulb) { s.dt = i === 0 ? 0 : dtReal; P.elapsed += s.dt; } else s.dt = P.moving ? P.dt : 0;
    const tau = P.bulb ? P.elapsed : (i + 0.5) / P.N * P.t;
    if (P.shakeK > 0) {                                              // tremor 6-9 Hz + ayunan napas 0,35 Hz (rad)
      const tr = 0.00055, dr = 0.0016 * Math.min(1, tau / 1.5);
      s.yaw = P.shakeK * (tr * (Math.sin(53.4 * tau + P.ph[0]) - Math.sin(P.ph[0]) + 0.6 * (Math.sin(38.3 * tau + P.ph[1]) - Math.sin(P.ph[1]))) + dr * (Math.sin(2.2 * tau + P.ph[2]) - Math.sin(P.ph[2])));
      s.pitch = P.shakeK * (tr * (Math.sin(47.1 * tau + P.ph[1]) - Math.sin(P.ph[1])) + dr * 0.7 * (Math.sin(2.2 * tau + P.ph[3]) - Math.sin(P.ph[3])));
    }
    P.i++;
    if (P.bulb ? (P.release && P.i > 1) || P.elapsed >= BULB_MAX : P.i >= P.N) P.done = true;
    return s;
  };
  K.weight = () => 1;                                                 // rata-rata sama
  // Pengali eksposur akhir (B: dari lama tahan sebenarnya)
  K.capMul = function () { const P = K.cap; if (!P.bulb) return P.mul; const t = Math.max(1 / 30, P.elapsed); return Math.pow(2, K.A.ev0 - ev100(P.c.N, t, P.c.iso)); };
  // Dipanggil adaptor tepat setelah gambar akhir digambar ke kanvas (tugas yang sama): potong bingkai, simpan
  K.finish = function (canvas) {
    const P = K.cap; K.cap = null; K.unfreeze = true;
    if (P.bulb) P.t = Math.max(1 / 30, P.elapsed);
    click(1);
    const r = frameRect(canvas.width, canvas.height), cv = document.createElement('canvas');
    cv.width = Math.round(r.w); cv.height = Math.round(r.h);
    cv.getContext('2d').drawImage(canvas, Math.round(r.x), Math.round(r.y), cv.width, cv.height, 0, 0, cv.width, cv.height);
    const name = fileName(P), jpg = K.st.fmt === 'jpg';
    const meta = { Software: 'Interstellia', Title: K.A.app, Lens: P.c.f + ' mm', FNumber: 'f/' + P.c.N, ExposureTime: shutterLabel(P.t), ISO: String(P.c.iso),
      FocusDistance: fmtDist(P.invS > 0 ? 1 / P.invS : Infinity), CreationTime: new Date().toISOString() };
    review(cv);
    cv.toBlob(async (blob) => {
      if (!blob) return;
      let out = blob;
      if (!jpg) { try { out = await pngWithText(blob, meta); } catch (e) { out = blob; } }
      download(out, name + (jpg ? '.jpg' : '.png'));
      toast(T('saved') + ': ' + name);
      if (K.onSaved) K.onSaved(out, name);
    }, jpg ? 'image/jpeg' : 'image/png', 0.92);
  };
  function fileName(P) {
    const d = new Date(), p2 = (n) => String(n).padStart(2, '0');
    return `${K.A.app}-${d.getFullYear()}${p2(d.getMonth() + 1)}${p2(d.getDate())}-${p2(d.getHours())}${p2(d.getMinutes())}${p2(d.getSeconds())}`
      + `-${P.c.f}mm-f${String(P.c.N).replace('.', '_')}-${shutterLabel(P.t).replace('/', '-').replace(',', '_')}-iso${P.c.iso}`;
  }
  function download(blob, name) {
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 4000);
  }
  // PNG: sisip chunk tEXt sesudah IHDR (CRC32)
  const CRC = (() => { const t = new Uint32Array(256); for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; } return t; })();
  function crc32(b) { let c = 0xffffffff; for (let i = 0; i < b.length; i++) c = CRC[(c ^ b[i]) & 255] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; }
  function textChunk(key, val) {
    const enc = new TextEncoder(), k = enc.encode(key), v = enc.encode(val.replace(/[^\x20-\x7e]/g, '?'));
    const data = new Uint8Array(4 + k.length + 1 + v.length);
    data.set([0x74, 0x45, 0x58, 0x74], 0); data.set(k, 4); data[4 + k.length] = 0; data.set(v, 5 + k.length);
    const out = new Uint8Array(12 + data.length - 4), dv = new DataView(out.buffer);
    dv.setUint32(0, data.length - 4); out.set(data, 4); dv.setUint32(8 + data.length - 4, crc32(data));
    return out;
  }
  async function pngWithText(blob, meta) {
    const src = new Uint8Array(await blob.arrayBuffer()), at = 33;     // 8 tanda tangan + IHDR 25
    const parts = Object.entries(meta).map(([k, v]) => textChunk(k, String(v)));
    const n = parts.reduce((s, p) => s + p.length, 0), out = new Uint8Array(src.length + n);
    out.set(src.subarray(0, at), 0); let o = at; for (const p of parts) { out.set(p, o); o += p.length; } out.set(src.subarray(at), o);
    return new Blob([out], { type: 'image/png' });
  }
  function readPngText(u8) {                                          // untuk uji
    const r = {}; let o = 8; const dv = new DataView(u8.buffer, u8.byteOffset, u8.byteLength), dec = new TextDecoder();
    while (o + 8 <= u8.length) {
      const len = dv.getUint32(o), type = dec.decode(u8.subarray(o + 4, o + 8));
      if (type === 'tEXt') { const d = u8.subarray(o + 8, o + 8 + len), z = d.indexOf(0); r[dec.decode(d.subarray(0, z))] = dec.decode(d.subarray(z + 1)); }
      if (type === 'IEND') break; o += 12 + len;
    }
    return r;
  }
  K.pngWithText = pngWithText; K.readPngText = readPngText; K.crc32 = crc32;

  // ---------- video ----------
  K.recStart = function () {
    if (K.rec || !K.A) return;
    const cv = K.A.canvas;
    if (!window.MediaRecorder || !cv.captureStream) { toast(T('noRec')); return; }
    const stream = cv.captureStream(K.st.fps);
    let dest = null, node = null;
    try { const a = K.A.audio && K.A.audio(); if (a && a.ctx && a.node) { dest = a.ctx.createMediaStreamDestination(); a.node.connect(dest); node = a.node; dest.stream.getAudioTracks().forEach((t) => stream.addTrack(t)); } } catch (e) { dest = null; }
    const types = ['video/mp4;codecs=avc1.640028,mp4a.40.2', 'video/mp4', 'video/webm;codecs=vp9,opus', 'video/webm;codecs=vp8,opus', 'video/webm'];
    const mime = types.find((t) => MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(t)) || '';
    let mr;
    try { mr = new MediaRecorder(stream, mime ? { mimeType: mime, videoBitsPerSecond: K.st.mbps * 1e6 } : { videoBitsPerSecond: K.st.mbps * 1e6 }); } catch (e) { toast(T('noRec')); return; }
    const R = { mr, chunks: [], t0: performance.now(), mime: mr.mimeType || mime || 'video/webm', dest, node, stream };
    mr.ondataavailable = (e) => { if (e.data && e.data.size) R.chunks.push(e.data); };
    mr.onstop = () => {
      const blob = new Blob(R.chunks, { type: R.mime.split(';')[0] });
      const d = new Date(), p2 = (n) => String(n).padStart(2, '0');
      const name = `${K.A.app}-${d.getFullYear()}${p2(d.getMonth() + 1)}${p2(d.getDate())}-${p2(d.getHours())}${p2(d.getMinutes())}${p2(d.getSeconds())}-${cur().f}mm-${K.st.fps}p`;
      if (blob.size) download(blob, name + (R.mime.includes('mp4') ? '.mp4' : '.webm'));
      toast(T('recSaved'));
      if (K.onRecorded) K.onRecorded(blob);
    };
    mr.start(1000); K.rec = R; beep(880);
  };
  K.recStop = function () {
    const R = K.rec; if (!R) return; K.rec = null;
    try { R.mr.stop(); } catch (e) { /* abaikan */ }
    try { if (R.node && R.dest) R.node.disconnect(R.dest); } catch (e) { /* abaikan */ }
    R.stream.getVideoTracks().forEach((t) => setTimeout(() => t.stop(), 500));
    beep(660);
  };

  // ---------- bunyi (AudioContext sendiri: tidak ikut terekam) ----------
  let actx = null;
  function ac() { if (!actx) { const C = window.AudioContext || window.webkitAudioContext; if (C) actx = new C(); } if (actx && actx.state === 'suspended') actx.resume(); return actx; }
  function click(phase) {                                            // rana kain: buka (0) dan tutup (1) lembut
    const c = ac(); if (!c) return;
    const n = Math.floor(c.sampleRate * 0.03), b = c.createBuffer(1, n, c.sampleRate), d = b.getChannelData(0);
    for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * Math.exp(-i / (n * (phase ? 0.18 : 0.12)));
    const s = c.createBufferSource(); s.buffer = b;
    const f = c.createBiquadFilter(); f.type = 'bandpass'; f.frequency.value = phase ? 2600 : 3400; f.Q.value = 1.2;
    const g = c.createGain(); g.gain.value = phase ? 0.35 : 0.28;
    s.connect(f).connect(g).connect(c.destination); s.start();
  }
  function beep(hz) {
    const c = ac(); if (!c) return;
    const o = c.createOscillator(), g = c.createGain(); o.frequency.value = hz; g.gain.value = 0.0001;
    g.gain.setTargetAtTime(0.06, c.currentTime, 0.005); g.gain.setTargetAtTime(0.0001, c.currentTime + 0.08, 0.02);
    o.connect(g).connect(c.destination); o.start(); o.stop(c.currentTime + 0.25);
  }

  // ---------- DOM: overlay, beku, tinjau, panel, bantuan, toast ----------
  let ov, freezeEl, revEl, panelEl, helpEl, toastEl, touchEl, styleEl;
  function el(tag, id, parent) { const e = document.createElement(tag); if (id) e.id = id; (parent || document.body).appendChild(e); return e; }
  function buildDom() {
    styleEl = el('style'); styleEl.textContent = `
      #camFreeze, #camOv { position: fixed; inset: 0; width: 100vw; height: 100vh; pointer-events: none; }
      #camFreeze { z-index: 30; object-fit: fill; } #camOv { z-index: 31; }
      #camRev { position: fixed; right: 18px; bottom: 18px; z-index: 33; max-width: 26vw; max-height: 26vh; border: 2px solid #ddd; box-shadow: 0 4px 20px #000a; transition: opacity .6s; pointer-events: none; }
      #camPanel { position: fixed; top: 12px; right: 12px; z-index: 34; width: 290px; max-width: calc(100vw - 32px); max-height: calc(100vh - 24px); overflow: auto;
        padding: 10px 12px; background: rgba(14,16,20,.92); color: #e8e6e0; border: 1px solid #444; border-radius: 8px; font: 12px/1.35 system-ui, sans-serif; }
      #camPanel h3 { margin: 0 0 6px; font-size: 13px; color: #ffb36b; display: flex; justify-content: space-between; }
      #camPanel .r { display: grid; grid-template-columns: 92px 1fr; align-items: center; gap: 4px; margin: 5px 0; }
      #camPanel .g { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; }
      #camPanel button { font: inherit; color: #e8e6e0; background: #ffffff10; border: 1px solid #555; border-radius: 5px; padding: 3px 7px; cursor: pointer; }
      #camPanel button.on { background: #ffb36b33; border-color: #ffb36b; color: #fff; }
      #camPanel output { min-width: 58px; text-align: center; color: #fff; font-variant-numeric: tabular-nums; }
      #camPanel input[type=range] { width: 100%; }
      #camPanel .note { color: #999; font-size: 11px; margin-top: 6px; }
      #camHelp { position: fixed; inset: 0; z-index: 35; display: flex; align-items: center; justify-content: center; background: #0008; }
      #camHelp .box { background: rgba(14,16,20,.96); color: #e8e6e0; border: 1px solid #555; border-radius: 10px; padding: 14px 18px; max-width: 560px; font: 13px/1.5 system-ui, sans-serif; }
      #camHelp td { padding: 2px 10px 2px 0; vertical-align: top; } #camHelp td:first-child { color: #ffb36b; white-space: nowrap; }
      #camToast { position: fixed; left: 50%; top: 16px; transform: translateX(-50%); z-index: 36; background: rgba(0,0,0,.75); color: #fff; padding: 6px 12px; border-radius: 6px; font: 13px system-ui, sans-serif; transition: opacity .5s; pointer-events: none; }
      #camTouch { position: fixed; right: 18px; bottom: 50%; z-index: 33; display: flex; flex-direction: column; gap: 10px; }
      #camTouch button { width: 64px; height: 64px; border-radius: 50%; border: 3px solid #ddd; background: #c0392baa; color: #fff; font: 12px system-ui; }
      #camTouch button.s { width: 48px; height: 48px; background: #0008; }`;
    freezeEl = el('canvas', 'camFreeze'); freezeEl.hidden = true;
    ov = el('canvas', 'camOv'); ov.hidden = true;
    revEl = el('img', 'camRev'); revEl.hidden = true;
    toastEl = el('div', 'camToast'); toastEl.hidden = true;
    panelEl = el('div', 'camPanel'); panelEl.hidden = true;
    helpEl = el('div', 'camHelp'); helpEl.hidden = true;
    helpEl.addEventListener('click', () => { helpEl.hidden = true; K.helpOn = false; });
    touchEl = el('div', 'camTouch'); touchEl.hidden = true;
    const tb = (txt, cls, fn) => { const b = document.createElement('button'); b.textContent = txt; if (cls) b.className = cls; b.addEventListener('click', (e) => { e.stopPropagation(); fn(); }); touchEl.appendChild(b); return b; };
    tb('●', '', () => K.shutterPress()); tb('⚙', 's', () => togglePanel()); tb('×', 's', () => K.A.exit());
    panelEl.addEventListener('mousedown', (e) => e.stopPropagation()); panelEl.addEventListener('wheel', (e) => e.stopPropagation());
  }
  let toastT = 0;
  function toast(s) { if (!toastEl) return; toastEl.textContent = s; toastEl.hidden = false; toastEl.style.opacity = 1; clearTimeout(toastT); toastT = setTimeout(() => { toastEl.style.opacity = 0; setTimeout(() => { toastEl.hidden = true; }, 600); }, 2200); }
  K.toast = toast;
  let revT = 0;
  function review(cv) {
    try { revEl.src = cv.toDataURL('image/jpeg', 0.7); } catch (e) { return; }
    revEl.hidden = false; revEl.style.opacity = 1; clearTimeout(revT);
    revT = setTimeout(() => { revEl.style.opacity = 0; setTimeout(() => { revEl.hidden = true; }, 700); }, 2500);
  }

  // ---------- panel ----------
  function stepIn(arr, v, d) { let i = 0, b = Infinity; arr.forEach((x, k) => { const e = Math.abs(log2(x / v)); if (e < b) { b = e; i = k; } }); return arr[Math.max(0, Math.min(arr.length - 1, i + d))]; }
  const ACT = {
    lens(i) { K.st.lens = Math.max(0, Math.min(LENSES.length - 1, i)); K.st.N = clampN(K.st.N); K.st.invS = Math.min(K.st.invS, 1 / lens().minF); },
    ap(d) { if (K.st.mode === 'P') K.st.mode = 'A'; K.st.N = clampN(stepIn(APERTURES.filter((x) => x >= lens().nMax - 1e-6), clampN(K.st.N), d)); },
    sh(d) { if (K.st.mode !== 'M') { const c = cur(); K.st.mode = 'M'; K.st.N = c.N; K.st.sh = SHUTTERS.findIndex((x) => x >= c.t * 0.84) ; if (K.st.sh < 0) K.st.sh = 15; } K.st.sh = Math.max(0, Math.min(SHUTTERS.length - 1, K.st.sh + d)); },
    iso(d) { K.st.iso = stepIn(ISOS, K.st.iso, d); },
    comp(d) { K.st.comp = Math.max(-3, Math.min(3, Math.round((K.st.comp + d / 3) * 3) / 3)); },
    mode(m) { if (m === 'M' && K.st.mode !== 'M') { const c = cur(); K.st.N = c.N; K.st.sh = Math.max(0, SHUTTERS.findIndex((x) => x >= c.t * 0.84)); } K.st.mode = m; },
    focus(dv) { K.st.invS = Math.max(0, Math.min(1 / lens().minF, K.st.invS + dv)); },
  };
  function setS(fn) { fn(); save(); if (K.panel) buildPanel(); }
  K.act = (name, v) => setS(() => ACT[name](v));
  function buildPanel() {
    const c = cur(), s = K.st, b = (lbl, on, fn) => { const x = document.createElement('button'); x.textContent = lbl; if (on) x.className = 'on'; x.addEventListener('click', () => setS(fn)); return x; };
    panelEl.textContent = '';
    const h = document.createElement('h3'); h.innerHTML = `<span>${T('title')}</span>`; const x = b('×', false, () => togglePanel()); h.appendChild(x); panelEl.appendChild(h);
    const row = (lbl, ...kids) => { const r = document.createElement('div'); r.className = 'r'; const l = document.createElement('span'); l.textContent = lbl; const g = document.createElement('div'); g.className = 'g'; kids.forEach((k) => g.appendChild(k)); r.append(l, g); panelEl.appendChild(r); };
    const out = (v) => { const o = document.createElement('output'); o.textContent = v; return o; };
    row(T('mode'), ...['M', 'A', 'P'].map((m) => b(m, s.mode === m, () => ACT.mode(m))));
    row(T('lens'), ...LENSES.map((L, i) => b(L.f, s.lens === i, () => ACT.lens(i))));
    row(T('ap'), b('-', false, () => ACT.ap(1)), out('f/' + fmtF(c.N)), b('+', false, () => ACT.ap(-1)));
    row(T('sh'), b('-', false, () => ACT.sh(1)), out((s.mode === 'M' ? '' : s.mode + ' ') + shutterLabel(c.t)), b('+', false, () => ACT.sh(-1)));
    row(T('iso'), b('-', false, () => ACT.iso(-1)), out(String(s.iso)), b('+', false, () => ACT.iso(1)));
    row(T('comp'), b('-', false, () => ACT.comp(-1)), out((s.comp > 0 ? '+' : '') + s.comp.toFixed(1).replace('.', ',')), b('+', false, () => ACT.comp(1)));
    const fr = document.createElement('input'); fr.type = 'range'; fr.min = 0; fr.max = 1; fr.step = 0.001; fr.value = s.invS * c.minF;
    const fo = out(fmtDist(s.invS > 0 ? 1 / s.invS : Infinity));
    fr.addEventListener('input', () => { K.st.invS = parseFloat(fr.value) / lens().minF; fo.textContent = fmtDist(K.st.invS > 0 ? 1 / K.st.invS : Infinity); save(); });
    row(T('focus'), fo); panelEl.appendChild(fr);
    row(T('kind'), b(T('photo'), !s.video, () => { if (K.rec) K.recStop(); K.st.video = false; }), b(T('video'), s.video, () => { K.st.video = true; }));
    row(T('view'), b(T('finder'), !s.live && !s.video, () => { K.st.live = false; }), b(T('live'), s.live || s.video, () => { K.st.live = true; }));
    row(T('mag'), ...[0.58, 0.72, 0.85].map((m) => b(String(m).replace('.', ','), s.mag === m, () => { K.st.mag = m; })));
    row(T('tripod'), b(T(s.tripod ? 'on' : 'off'), s.tripod, () => { K.st.tripod = !K.st.tripod; }));
    row(T('shake'), b(T(s.shake ? 'on' : 'off'), s.shake, () => { K.st.shake = !K.st.shake; }));
    row(T('fmt'), b('PNG', s.fmt !== 'jpg', () => { K.st.fmt = 'png'; }), b('JPEG', s.fmt === 'jpg', () => { K.st.fmt = 'jpg'; }));
    row(T('fps'), ...[24, 30, 60].map((f) => b(f, s.fps === f, () => { K.st.fps = f; })));
    row(T('rate'), ...[8, 16, 32].map((m) => b(m + ' Mbps', s.mbps === m, () => { K.st.mbps = m; })));
    const btns = [];
    if (K.A.freeMode) btns.push(b(T('free'), false, () => { togglePanel(); K.A.freeMode(); }));
    btns.push(b(T('help'), false, () => { toggleHelp(); }), b(T('exit'), false, () => K.A.exit()));
    row('', ...btns);
    const dr = dofRange(c.f, c.N, s.invS > 0 ? 1 / s.invS : Infinity), n = document.createElement('div'); n.className = 'note';
    n.textContent = `${T('dof')}: ${fmtDist(dr[0])} - ${fmtDist(dr[1])} · EV ${isFinite(c.ev) ? c.ev.toFixed(1).replace('.', ',') : 'B'} · meter EV ${c.evm.toFixed(1).replace('.', ',')}`;
    panelEl.appendChild(n);
  }
  function togglePanel() {
    K.panel = !K.panel; panelEl.hidden = !K.panel;
    if (K.panel) { buildPanel(); if (K.A.unlock) K.A.unlock(); }
  }
  function toggleHelp() {
    K.helpOn = !K.helpOn; helpEl.hidden = !K.helpOn;
    if (K.helpOn) {
      const rows = STR.keys[K.A.lang && K.A.lang() === 'en' ? 1 : 0].map(([k, v]) => `<tr><td>${k}</td><td>${v}</td></tr>`).join('');
      helpEl.innerHTML = `<div class="box"><b>${T('helpTitle')}</b><table>${rows}</table></div>`;
      if (K.A.unlock) K.A.unlock();
    }
  }
  K.togglePanel = togglePanel; K.toggleHelp = toggleHelp;

  // ---------- gambar overlay ----------
  const LED = '#ff4a26';
  K.draw = function () {
    if (!K.on || !ov) return;
    const dpr = Math.min(2, window.devicePixelRatio || 1), W = window.innerWidth, H = window.innerHeight;
    if (ov.width !== Math.round(W * dpr) || ov.height !== Math.round(H * dpr)) { ov.width = Math.round(W * dpr); ov.height = Math.round(H * dpr); }
    const g = ov.getContext('2d'); g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, W, H);
    const s = K.st, c = cur(), live = s.live || s.video;
    if (!live) drawFinder(g, W, H, c); else drawLive(g, W, H, c);
    if (K.cap) {                                                     // kemajuan tangkap
      const P = K.cap, f = P.bulb ? Math.min(1, P.elapsed / BULB_MAX) : P.i / P.N;
      g.fillStyle = '#ffffff22'; g.fillRect(W * 0.3, H - 10, W * 0.4, 3); g.fillStyle = LED; g.fillRect(W * 0.3, H - 10, W * 0.4 * f, 3);
    }
  };
  function ledText(g, s, x, y, align, a) {
    g.font = '600 15px ui-monospace, Menlo, Consolas, monospace'; g.textAlign = align; g.textBaseline = 'middle';
    g.shadowColor = LED; g.shadowBlur = 8; g.fillStyle = a === undefined ? LED : `rgba(255,74,38,${a})`; g.fillText(s, x, y); g.shadowBlur = 0;
  }
  function drawFinder(g, W, H, c) {
    const G = finderGeo(W, H), x0 = G.cx - G.ww / 2, y0 = G.cy - G.wh / 2, rad = Math.min(G.ww, G.wh) * 0.035;
    // masker okuler: gelap di luar jendela, sudut membulat, vinyet dalam
    g.save(); g.fillStyle = '#050505'; g.beginPath(); g.rect(0, 0, W, H);
    g.moveTo(x0 + rad, y0); g.arcTo(x0, y0, x0, y0 + rad, rad); g.lineTo(x0, y0 + G.wh - rad); g.arcTo(x0, y0 + G.wh, x0 + rad, y0 + G.wh, rad);
    g.lineTo(x0 + G.ww - rad, y0 + G.wh); g.arcTo(x0 + G.ww, y0 + G.wh, x0 + G.ww, y0 + G.wh - rad, rad); g.lineTo(x0 + G.ww, y0 + rad);
    g.arcTo(x0 + G.ww, y0, x0 + G.ww - rad, y0, rad); g.closePath(); g.fill('evenodd');
    const vg = g.createRadialGradient(G.cx, G.cy, G.wh * 0.42, G.cx, G.cy, G.ww * 0.62); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.38)');
    g.fillStyle = vg; g.fillRect(x0, y0, G.ww, G.wh); g.restore();
    if (!K.hud) return;
    // garis bingkai berpasangan + paralaks (lensa di kanan bawah jendela bidik)
    const invS = Math.max(0, Math.min(1 / c.minF, K.st.invS)), k = (G.ww / 2) / G.T;
    const ox = G.cx + LENS_OFF[0] * invS * k, oy = G.cy - LENS_OFF[1] * invS * k;
    const frames = [];
    const L = lens();
    if (L.f === 21) frames.push([21, 1]); else { frames.push([L.f, 1]); if (L.pair) frames.push([L.pair, 0.55]); }
    for (const [f, a] of frames) {
      const hx = (18 / f) * k, hy = (12 / f) * k;
      if (f === 21) { g.strokeStyle = 'rgba(244,240,220,0.5)'; g.lineWidth = 1.2; g.strokeRect(x0 + 6, y0 + 6, G.ww - 12, G.wh - 12); continue; }
      frameLines(g, ox - hx, oy - hy, 2 * hx, 2 * hy, a);
    }
    // tepi patch rangefinder (samar)
    const pw = 0.035 * G.ww, ph = 0.026 * G.ww;
    g.strokeStyle = 'rgba(255,230,170,0.18)'; g.lineWidth = 1; g.strokeRect(G.cx - pw, G.cy - ph, 2 * pw, 2 * ph);
    // HUD LED di tepi bawah jendela
    const y = y0 + G.wh - 20, s = K.st;
    const tl = c.bulb ? 'B' : shutterLabel(c.t);
    ledText(g, (s.mode !== 'M' ? s.mode + ' ' : '') + tl, G.cx - G.ww * 0.33, y, 'center');
    ledText(g, 'f' + fmtF(c.N), G.cx - G.ww * 0.18, y, 'center');
    ledText(g, 'ISO' + s.iso, G.cx - G.ww * 0.04, y, 'center');
    const ov2 = c.bulb ? 0 : c.over;                                 // + = terlalu terang
    const blink = (performance.now() / 300 | 0) % 2 === 0;
    ledText(g, '◀', G.cx + G.ww * 0.1, y, 'center', ov2 > 0.34 ? 1 : 0.15);
    ledText(g, '●', G.cx + G.ww * 0.13, y, 'center', Math.abs(ov2) <= 0.34 || (s.mode !== 'M') ? 1 : 0.15);
    ledText(g, '▶', G.cx + G.ww * 0.16, y, 'center', ov2 < -0.34 ? 1 : 0.15);
    if (s.comp) ledText(g, (s.comp > 0 ? '+' : '') + s.comp.toFixed(1).replace('.', ','), G.cx + G.ww * 0.22, y, 'center');
    ledText(g, fmtDist(invS > 0 ? 1 / invS : Infinity), G.cx + G.ww * 0.33, y, 'center', 0.75);
    if (K.lock != null) ledText(g, T('ael'), G.cx + G.ww * 0.42, y, 'center');
    if (s.tripod) ledText(g, '△', G.cx - G.ww * 0.44, y, 'center', 0.8);
    if (K.cap) ledText(g, blink ? 'busy' : '', G.cx, y0 + 22, 'center');
  }
  function frameLines(g, x, y, w, h, a) {
    const L = Math.min(w, h) * 0.22;
    g.save(); g.strokeStyle = `rgba(250,246,226,${0.95 * a})`; g.shadowColor = 'rgba(255,250,220,0.6)'; g.shadowBlur = 4; g.lineWidth = 1.6;
    g.beginPath();
    g.moveTo(x, y + L); g.lineTo(x, y); g.lineTo(x + L, y); g.moveTo(x + w - L, y); g.lineTo(x + w, y); g.lineTo(x + w, y + L);
    g.moveTo(x + w, y + h - L); g.lineTo(x + w, y + h); g.lineTo(x + w - L, y + h); g.moveTo(x + L, y + h); g.lineTo(x, y + h); g.lineTo(x, y + h - L);
    g.stroke();
    g.strokeStyle = `rgba(250,246,226,${0.35 * a})`; g.lineWidth = 1; g.shadowBlur = 0; g.strokeRect(x, y, w, h);
    g.restore();
  }
  function drawLive(g, W, H, c) {
    const s = K.st, r = frameRect(W, H);
    g.fillStyle = '#000'; if (r.x > 0) { g.fillRect(0, 0, r.x, H); g.fillRect(r.x + r.w, 0, W - r.x - r.w, H); } if (r.y > 0) { g.fillRect(0, 0, W, r.y); g.fillRect(0, r.y + r.h, W, H - r.y - r.h); }
    if (!K.hud) return;
    g.font = '600 14px system-ui, sans-serif'; g.textBaseline = 'middle'; g.fillStyle = '#f2f2f2'; g.shadowColor = '#000'; g.shadowBlur = 4;
    const y = r.y + r.h - 18, invS = Math.max(0, Math.min(1 / c.minF, s.invS));
    const items = [s.mode, c.bulb ? 'B' : shutterLabel(c.t), 'F' + fmtF(c.N), 'ISO ' + s.iso, (s.comp > 0 ? '+' : '') + s.comp.toFixed(1).replace('.', ','), c.f + 'mm', fmtDist(invS > 0 ? 1 / invS : Infinity)];
    if (s.video) items.push(s.fps + 'p');
    g.textAlign = 'center'; items.forEach((t, i) => g.fillText(t, r.x + r.w * (0.14 + i * (0.72 / (items.length - 1))), y));
    if (K.lock != null) { g.textAlign = 'left'; g.fillText(T('ael'), r.x + 14, r.y + 18); }
    if (s.video) {
      g.textAlign = 'left';
      if (K.rec) {
        const t = (performance.now() - K.rec.t0) / 1000, mm = Math.floor(t / 60), ss = Math.floor(t % 60);
        if ((performance.now() / 500 | 0) % 2 === 0) { g.fillStyle = '#e8312a'; g.beginPath(); g.arc(r.x + 22, r.y + 22, 7, 0, 6.2832); g.fill(); }
        g.fillStyle = '#fff'; g.fillText(`REC ${String(mm).padStart(2, '0')}:${String(ss).padStart(2, '0')}`, r.x + 36, r.y + 22);
        if (t > REC_MAX - 60) g.fillText('−' + Math.ceil(REC_MAX - t) + 's', r.x + 140, r.y + 22);
      } else g.fillText('STBY', r.x + 16, r.y + 22);
    }
    // garis pertiga tipis
    g.shadowBlur = 0; g.strokeStyle = 'rgba(255,255,255,0.12)'; g.lineWidth = 1; g.beginPath();
    for (const f of [1 / 3, 2 / 3]) { g.moveTo(r.x + r.w * f, r.y); g.lineTo(r.x + r.w * f, r.y + r.h); g.moveTo(r.x, r.y + r.h * f); g.lineTo(r.x + r.w, r.y + r.h * f); }
    g.stroke();
  }

  // ---------- masuk / keluar ----------
  K.enter = function () {
    if (!K.A) return;
    K.on = true; ov.hidden = false; touchEl.hidden = !(matchMedia('(pointer: coarse)').matches);
    K.st.live = false; K.lock = null; K.hud = true;
  };
  K.leave = function () {
    if (K.rec) K.recStop();
    K.on = false; K.cap = null; K.armed = false; K.lock = null;
    ov.hidden = true; freezeEl.hidden = true; touchEl.hidden = true; panelEl.hidden = true; helpEl.hidden = true; K.panel = false; K.helpOn = false;
  };
  K.busy = () => !!(K.cap || K.armed);
  K.recording = () => !!K.rec;
  // Dipanggil tiap frame oleh adaptor: batas rekam
  K.tick = function () {
    if (K.rec && (performance.now() - K.rec.t0) / 1000 > REC_MAX) { K.recStop(); toast(T('recMax')); }
    const ae = document.activeElement;                              // panel diperbarui (mode A / P) kecuali sedang digeser
    if (K.panel && (performance.now() / 500 | 0) !== K._pt && !(ae && panelEl.contains(ae) && ae.tagName === 'INPUT')) { K._pt = performance.now() / 500 | 0; if (K.st.mode !== 'M') buildPanel(); }
  };

  // ---------- input (fase tangkap di window: dijalankan sebelum handler experience) ----------
  function inForm(e) { const t = e.target; return t && (t.tagName === 'INPUT' || t.tagName === 'SELECT' || t.tagName === 'TEXTAREA'); }
  function onKey(e) {
    if (!K.on || inForm(e)) return;
    const c = e.code; let used = true;
    if (K.helpOn && (c === 'Escape' || c === 'Slash' || c === 'F1')) toggleHelp();
    else if (K.panel && c === 'Escape') togglePanel();
    else if (c === 'KeyF' || c === 'Escape') { if (!e.repeat) K.A.exit(); }
    else if (c === 'Enter' || c === 'NumpadEnter') { if (!e.repeat) K.shutterPress(); }
    else if (c === 'BracketLeft') K.act('sh', 1);
    else if (c === 'BracketRight') K.act('sh', -1);
    else if (c === 'Comma') K.act('ap', 1);
    else if (c === 'Period') K.act('ap', -1);
    else if (c === 'Minus' || c === 'NumpadSubtract') K.act(e.shiftKey ? 'comp' : 'iso', -1);
    else if (c === 'Equal' || c === 'NumpadAdd') K.act(e.shiftKey ? 'comp' : 'iso', 1);
    else if (/^Digit[0-9]$/.test(c)) { const d = +c.slice(5); if (d >= 1 && d <= 6) K.act('lens', d - 1); }
    else if (c === 'Tab') { if (!e.repeat) setS(() => { if (K.rec) K.recStop(); K.st.video = !K.st.video; }); }
    else if (c === 'KeyV') { if (!e.repeat) setS(() => { if (!K.st.video) K.st.live = !K.st.live; }); }
    else if (c === 'KeyH') K.hud = !K.hud;
    else if (c === 'Backquote') { if (!e.repeat) togglePanel(); }
    else if (c === 'Slash' || c === 'F1') toggleHelp();
    else used = false;
    if (used) { e.preventDefault(); e.stopImmediatePropagation(); }
  }
  function onKeyUp(e) { if (K.on && (e.code === 'Enter' || e.code === 'NumpadEnter')) K.shutterRelease(); }
  function onCanvas(e) { return e.target === K.A.canvas || e.target === ov || e.target === document.body || e.target === document.documentElement || (K.A.isLocked && K.A.isLocked()); }
  function onDown(e) {
    if (!K.on || !onCanvas(e) || K.panel || K.helpOn) return;
    if (e.button === 0 && K.A.isLocked && K.A.isLocked()) { K.shutterPress(); e.preventDefault(); e.stopImmediatePropagation(); }
    else if (e.button === 2) { K.lock = K.L || K.A.key; e.preventDefault(); e.stopImmediatePropagation(); }
  }
  function onUp(e) {
    if (!K.on) return;
    if (e.button === 0) K.shutterRelease();
    if (e.button === 2 && K.lock != null) { K.lock = null; e.stopImmediatePropagation(); }
  }
  function onWheel(e) {
    if (!K.on || K.panel || !onCanvas(e)) return;
    const d = e.deltaMode === 1 ? e.deltaY * 33 : e.deltaY;
    if (e.shiftKey) { K._ap = (K._ap || 0) + d; if (Math.abs(K._ap) > 60) { K.act('ap', K._ap > 0 ? 1 : -1); K._ap = 0; } }
    else { ACT.focus(-(d / 100) * (0.015 + 0.04 * K.st.invS)); save(); }   // langkah dioptri membesar ke jarak dekat (sekitar 40 klik tak hingga - 0,7 m)
    e.preventDefault(); e.stopImmediatePropagation();
  }
  K.init = function (A) {
    K.A = A;
    if (!ov) buildDom();
    window.addEventListener('keydown', onKey, true);
    window.addEventListener('keyup', onKeyUp, true);
    window.addEventListener('mousedown', onDown, true);
    window.addEventListener('mouseup', onUp, true);
    window.addEventListener('wheel', onWheel, { capture: true, passive: false });
    window.addEventListener('contextmenu', (e) => { if (K.on) e.preventDefault(); }, true);
    window.addEventListener('blur', () => { if (K.cap && K.cap.bulb) K.cap.release = true; });
  };
  K.T = T;
  window.CAMKIT = K;
})();
