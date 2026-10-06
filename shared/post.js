/* shared/post.js: alat post-processing bersama (V0 rencana realisme visual).
   Skrip biasa (bukan modul) agar jalan dari file://, mengisi window.POSTKIT.
   - POSTKIT.wb(kelvin, tint): pengali RGB linear untuk white balance, relatif 6.500 K, luminans tetap.
     6.500 K dan tint 0 = tepat [1, 1, 1] (gambar identik dengan sebelum V0).
   - POSTKIT.dynRes(opt): pengendali resolusi dinamis (skala render naik-turun per langkah mengikuti FPS).
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

  window.POSTKIT = { kelvinRGB, wb, dynRes };
})();
