/* shared/post.js: alat post-processing bersama (V0 rencana realisme visual).
   Skrip biasa (bukan modul) agar jalan dari file://, mengisi window.POSTKIT.
   - POSTKIT.wb(kelvin, tint): pengali RGB linear untuk white balance, relatif 6.500 K, luminans tetap.
     6.500 K dan tint 0 = tepat [1, 1, 1] (gambar identik dengan sebelum V0).
   - POSTKIT.dynRes(opt): pengendali resolusi dinamis (skala render naik-turun per langkah mengikuti FPS).
   - V5: POSTKIT.halton, POSTKIT.lensDirt(THREE) tekstur noda lensa, POSTKIT.TAA_FS shader resolve TAA (Copper dan Millar).
   Tiap experience tetap memakai kurva ACES dan pipeline post miliknya sendiri (beda kurva = beda tampilan,
   jadi tidak disamakan tanpa diminta). */
(function () {
  'use strict';

  // Suhu warna -> RGB sRGB 0..1 (pendekatan Tanner Helland, 1.000-40.000 K)
  function kelvinRGB(k) {
    const t = Math.min(400, Math.max(10, k / 100));
    let r, g, b;
    if (t <= 66) { r = 255; g = 99.4708025861 * Math.log(t) - 161.1195681661; }
    else { r = 329.698727446 * Math.pow(t - 60, -0.1332047592); g = 288.1221695283 * Math.pow(t - 60, -0.0755148492); }
    if (t >= 66) b = 255; else if (t <= 19) b = 0; else b = 138.5177312231 * Math.log(t - 10) - 305.0447927307;
    const c = (v) => Math.pow(Math.min(255, Math.max(0, v)) / 255, 2.2);   // ke linear
    return [c(r), c(g), c(b)];
  }

  // White balance: kelvin = suhu yang ingin dinetralkan (lebih rendah = gambar lebih dingin), tint + = magenta, - = hijau
  function wb(kelvin, tint) {
    tint = tint || 0;
    if (kelvin === 6500 && tint === 0) return [1, 1, 1];
    const a = kelvinRGB(kelvin), n = kelvinRGB(6500);
    const m = [n[0] / Math.max(a[0], 1e-4), n[1] / Math.max(a[1], 1e-4), n[2] / Math.max(a[2], 1e-4)];
    m[1] *= 1 - tint * 0.1;
    const l = 0.2126 * m[0] + 0.7152 * m[1] + 0.0722 * m[2];         // luminans tetap: hanya warna yang bergeser
    return [m[0] / l, m[1] / l, m[2] / l];
  }

  // Resolusi dinamis: update(dt, fps) dipanggil tiap frame; kembali true bila skala berubah (lalu panggil resize)
  function dynRes(opt) {
    const o = Object.assign({ min: 0.7, max: 1.0, step: 0.1, lowFps: 45, highFps: 57, window: 2.0, on: true }, opt || {});
    const D = { scale: o.max, opt: o, low: 0, high: 0,
      update(dt, fps) {
        if (!o.on) { if (D.scale !== o.max) { D.scale = o.max; return true; } return false; }
        if (fps < o.lowFps) { D.low += dt; D.high = 0; } else if (fps > o.highFps) { D.high += dt; D.low = 0; } else { D.low = D.high = 0; }
        if (D.low >= o.window && D.scale > o.min + 1e-6) { D.scale = Math.max(o.min, +(D.scale - o.step).toFixed(2)); D.low = 0; return true; }
        if (D.high >= o.window && D.scale < o.max - 1e-6) { D.scale = Math.min(o.max, +(D.scale + o.step).toFixed(2)); D.high = 0; return true; }
        return false;
      },
      atMin() { return D.scale <= o.min + 1e-6; },
      reset() { D.scale = o.max; D.low = D.high = 0; } };
    return D;
  }


  // V5: urutan Halton (geser sub-piksel TAA): halton(i, 2) dan halton(i, 3) untuk i = 1..8
  function halton(i, b) { let f = 1, r = 0; while (i > 0) { f /= b; r += f * (i % b); i = Math.floor(i / b); } return r; }

  // V5: noda lensa prosedural (kanal r): gumpalan berminyak, bintik debu, usapan; acak tetap. Dikali bloom lebar di komposit
  function lensDirt(THREE) {
    const S = 512, cv = document.createElement('canvas'); cv.width = cv.height = S;
    const g = cv.getContext('2d'); g.fillStyle = '#000'; g.fillRect(0, 0, S, S);
    let sd = 9137; const r = () => ((sd = (sd * 16807) % 2147483647) / 2147483647);
    g.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 46; i++) {                                      // noda besar
      const x = r() * S, y = r() * S, rad = 18 + r() * 70, a = 0.05 + 0.1 * r();
      const gr = g.createRadialGradient(x, y, 0, x, y, rad); gr.addColorStop(0, `rgba(255,255,255,${a})`); gr.addColorStop(0.6, `rgba(255,255,255,${a * 0.5})`); gr.addColorStop(1, 'rgba(255,255,255,0)');
      g.fillStyle = gr; g.beginPath(); g.arc(x, y, rad, 0, 6.2832); g.fill();
    }
    for (let i = 0; i < 260; i++) {                                     // debu
      const x = r() * S, y = r() * S, rad = 0.8 + r() * r() * 5, a = 0.12 + 0.45 * r();
      const gr = g.createRadialGradient(x, y, 0, x, y, rad); gr.addColorStop(0, `rgba(255,255,255,${a})`); gr.addColorStop(1, 'rgba(255,255,255,0)');
      g.fillStyle = gr; g.beginPath(); g.arc(x, y, rad, 0, 6.2832); g.fill();
    }
    g.lineCap = 'round';
    for (let i = 0; i < 7; i++) {                                       // usapan
      const x = r() * S, y = r() * S, a0 = r() * 6.2832, L = 60 + r() * 140;
      g.strokeStyle = `rgba(255,255,255,${0.025 + 0.03 * r()})`; g.lineWidth = 6 + r() * 14;
      g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + Math.cos(a0 + 0.6) * L * 0.6, y + Math.sin(a0 + 0.6) * L * 0.6, x + Math.cos(a0) * L, y + Math.sin(a0) * L); g.stroke();
    }
    const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.NoColorSpace; tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
    return tex;
  }

  // V5: shader resolve TAA (fragment, varying vUv). Masukan: tCur (gambar frame ini, sudah tone map, digeser sub-piksel),
  // tHist (riwayat), tDepth (kedalaman frame ini), uProjInv (invers proyeksi bergeser), uCamWorld, uPrevVP (proyeksi x view
  // frame lalu tanpa geser), uTexel, uValid. Proyeksi ulang dari kedalaman terdekat 3x3, riwayat Catmull-Rom, dijepit ke
  // sebaran tetangga di YCoCg, bobot frame baru 0,09-0,3 (naik saat gerak cepat). Keluaran a = luma.
  const TAA_FS = `
  uniform sampler2D tCur, tHist, tDepth; uniform mat4 uProjInv, uCamWorld, uPrevVP; uniform vec2 uTexel; uniform float uValid;
  varying vec2 vUv;
  vec3 yc(vec3 c) { return vec3(dot(c, vec3(0.25, 0.5, 0.25)), dot(c, vec3(0.5, 0.0, -0.5)), dot(c, vec3(-0.25, 0.5, -0.25))); }
  vec3 rgb(vec3 c) { return vec3(c.x + c.y - c.z, c.x + c.z, c.x - c.y - c.z); }
  vec3 hist(vec2 uv) {                                               // Catmull-Rom 5 sampel bilinear (riwayat tidak kabur)
    vec2 sz = 1.0 / uTexel, p = uv * sz, tc = floor(p - 0.5) + 0.5, f = p - tc;
    vec2 w0 = f * (-0.5 + f * (1.0 - 0.5 * f)), w1 = 1.0 + f * f * (-2.5 + 1.5 * f), w2 = f * (0.5 + f * (2.0 - 1.5 * f)), w3 = f * f * (-0.5 + 0.5 * f);
    vec2 w12 = w1 + w2, t0 = (tc - 1.0) * uTexel, t3 = (tc + 2.0) * uTexel, t12 = (tc + w2 / w12) * uTexel;
    vec3 s = textureLod(tHist, vec2(t12.x, t0.y), 0.0).rgb * (w12.x * w0.y) + textureLod(tHist, vec2(t0.x, t12.y), 0.0).rgb * (w0.x * w12.y)
           + textureLod(tHist, t12, 0.0).rgb * (w12.x * w12.y) + textureLod(tHist, vec2(t3.x, t12.y), 0.0).rgb * (w3.x * w12.y)
           + textureLod(tHist, vec2(t12.x, t3.y), 0.0).rgb * (w12.x * w3.y);
    float ws = w12.x * w0.y + w0.x * w12.y + w12.x * w12.y + w3.x * w12.y + w12.x * w3.y;
    return max(s / ws, vec3(0.0));
  }
  void main() {
    vec3 c = textureLod(tCur, vUv, 0.0).rgb, m1 = vec3(0.0), m2 = vec3(0.0);
    float dmin = 2.0; vec2 duv = vUv;
    for (int k = 0; k < 9; k++) {
      vec2 o = vec2(float(k - (k / 3) * 3) - 1.0, float(k / 3) - 1.0), uv = vUv + o * uTexel;
      vec3 s = yc(textureLod(tCur, uv, 0.0).rgb); m1 += s; m2 += s * s;
      float d = textureLod(tDepth, uv, 0.0).r; if (d < dmin) { dmin = d; duv = uv; }   // kedalaman terdekat: tepi objek ikut gerak objek
    }
    vec3 mu = m1 / 9.0, sg = sqrt(max(m2 / 9.0 - mu * mu, vec3(0.0)));
    vec4 v = uProjInv * vec4(duv * 2.0 - 1.0, dmin * 2.0 - 1.0, 1.0); vec3 vp = v.xyz / v.w;
    vec4 wp = dmin >= 0.99999 ? vec4(mat3(uCamWorld) * vp, 0.0) : uCamWorld * vec4(vp, 1.0);   // langit: arah saja
    vec4 pc = uPrevVP * wp;
    vec2 pv = vUv + (pc.xy / max(pc.w, 1e-6) * 0.5 + 0.5 - duv);
    if (uValid < 0.5 || pc.w <= 0.0 || any(lessThan(pv, vec2(0.0))) || any(greaterThan(pv, vec2(1.0)))) { gl_FragColor = vec4(c, dot(c, vec3(0.299, 0.587, 0.114))); return; }
    vec3 h = yc(hist(pv)), cy = yc(c);
    vec3 lo = mu - 1.25 * sg, hi = mu + 1.25 * sg;                    // jepit riwayat ke kotak sebaran (clip ke arah pusat)
    vec3 e = 0.5 * (hi - lo) + 1e-4, dd = h - 0.5 * (hi + lo), a3 = abs(dd / e);
    float ma = max(a3.x, max(a3.y, a3.z));
    if (ma > 1.0) h = 0.5 * (hi + lo) + dd / ma;
    float sp = length((pv - vUv) / uTexel), al = mix(0.09, 0.3, clamp(sp / 30.0, 0.0, 1.0));   // gerak cepat = riwayat lebih pendek
    vec3 o = rgb(mix(h, cy, al));
    gl_FragColor = vec4(o, dot(o, vec3(0.299, 0.587, 0.114)));
  }`;

  window.POSTKIT = { kelvinRGB, wb, dynRes, halton, lensDirt, TAA_FS };
})();
