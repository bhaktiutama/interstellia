/* =====================================================================
   PROFKIT (rencana P0, docs/app/rencana-performa.md): alat ukur muat dan tersendat.
   Skrip biasa (bukan modul), dimuat sebelum skrip experience agar sempat membungkus WebGL2.
   Mati total tanpa ?prof=1: tidak membungkus apa pun, tidak menggambar apa pun.

   Yang dicatat (waktu dalam ms sejak navigasi, performance.now()):
   - tahap muat: PROFKIT.mark(label) dari host (Copper bootStep, Millar, Gargantua)
   - program shader: tiap linkProgram (waktu, fase), lama menunggu program selesai
     (getProgramParameter / getShaderParameter / getActiveUniform / getUniformLocation yang memblokir > 1 ms)
   - long task (PerformanceObserver), 600 frame pertama (lama callback requestAnimationFrame + jarak antar frame)
   - tombol: tiap keydown, program baru dan frame terpanjang dalam 3 s sesudahnya
   - fase: 'muat' sampai PROFKIT.ready() dipanggil host, lalu 'frame1' untuk frame pertama sesudahnya,
     lalu 'main' (bermain); host boleh memanggil PROFKIT.phase(nama) sendiri (mis. 'mulai')
   Hasil: window.PROFKIT.data(), panel kecil di kiri bawah dengan tombol Salin (JSON) dan Sembunyikan.
   ===================================================================== */
(function () {
  'use strict';
  const on = /[?&]prof=1\b/.test(location.search);
  const now = () => performance.now();
  const P = window.PROFKIT = {
    on, marks: [], links: [], waits: [], longs: [], frames: [], keys: [], phases: [['muat', 0]], cur: 'muat',
    readyAt: null, gl: null,
    mark() {}, ready() {}, phase() {}, data() { return null; },
  };
  if (!on) return;

  P.mark = (label) => { P.marks.push([Math.round(now()), String(label)]); };
  P.phase = (name) => { P.cur = name; P.phases.push([name, Math.round(now())]); };
  P.ready = () => { if (P.readyAt == null) { P.readyAt = Math.round(now()); P.phase('frame1'); } };

  // --- WebGL2: program dan waktu menunggu ---------------------------------------------------
  const G = window.WebGL2RenderingContext && WebGL2RenderingContext.prototype;
  if (G) {
    const wrapWait = (name) => {
      const f = G[name];
      G[name] = function (...a) {
        const t = now(), r = f.apply(this, a), d = now() - t;
        if (d > 1) P.waits.push([Math.round(t), Math.round(d * 10) / 10, name, P.cur]);
        return r;
      };
    };
    ['getProgramParameter', 'getShaderParameter', 'getActiveUniform', 'getUniformLocation', 'getProgramInfoLog', 'getShaderInfoLog'].forEach(wrapWait);
    const link = G.linkProgram;
    G.linkProgram = function (p) { P.links.push([Math.round(now()), P.cur]); return link.call(this, p); };
    const gc = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function (type, ...a) {
      const c = gc.call(this, type, ...a);
      if (c && type === 'webgl2' && !P.gl) {
        P.gl = c;
        try {
          const ext = c.getExtension('WEBGL_debug_renderer_info');
          P.gpu = ext ? c.getParameter(ext.UNMASKED_RENDERER_WEBGL) : c.getParameter(c.RENDERER);
          P.parallel = !!c.getExtension('KHR_parallel_shader_compile');
        } catch (e) { /* abaikan */ }
      }
      return c;
    };
  }

  // --- long task dan frame -------------------------------------------------------------------
  try {
    new PerformanceObserver((l) => { for (const e of l.getEntries()) P.longs.push([Math.round(e.startTime), Math.round(e.duration), P.cur]); })
      .observe({ type: 'longtask', buffered: true });
  } catch (e) { /* tidak didukung */ }
  // Satu "frame" = semua callback dengan timestamp rAF yang sama (satu tick); beberapa loop bisa berbagi tick.
  // Fase frame1 berakhir saat tick berikutnya dimulai, bukan setelah callback pertama.
  const raf = window.requestAnimationFrame.bind(window);
  let tick = null, f1ts = null;
  window.requestAnimationFrame = (cb) => raf((ts) => {
    if (!tick || tick.ts !== ts) {
      if (P.cur === 'frame1' && f1ts != null && ts !== f1ts) P.phase('main');
      if (P.cur === 'frame1' && f1ts == null) f1ts = ts;
      const t = now();
      tick = { ts, f: [Math.round(t), 0, tick ? Math.round(t - tick.f[0]) : 0, P.cur] };
      if (P.frames.length < 600) P.frames.push(tick.f);
    }
    const t = now();
    try { cb(ts); } finally { tick.f[1] = Math.round((tick.f[1] + now() - t) * 10) / 10; }
  });

  // --- tombol --------------------------------------------------------------------------------
  addEventListener('keydown', (e) => {
    if (e.repeat) return;
    const k = { key: e.code, t: Math.round(now()), n0: P.links.length };
    P.keys.push(k);
    setTimeout(() => {
      k.programs = P.links.length - k.n0;
      k.maxFrame = Math.max(0, ...P.frames.filter((f) => f[0] >= k.t && f[0] < k.t + 3000).map((f) => f[1]));
      k.maxLong = Math.max(0, ...P.longs.filter((l) => l[0] >= k.t - 50 && l[0] < k.t + 3000).map((l) => l[1]));
      delete k.n0;
    }, 3000);
  }, true);

  // --- ringkasan -----------------------------------------------------------------------------
  const sum = (a) => a.reduce((x, y) => x + y, 0);
  P.data = () => {
    const byPhase = {};
    for (const [, ph] of P.links) byPhase[ph] = (byPhase[ph] || 0) + 1;
    const waitByPhase = {};
    for (const w of P.waits) waitByPhase[w[3]] = Math.round((waitByPhase[w[3]] || 0) + w[1]);
    const f1 = P.frames.find((f) => P.readyAt != null && f[0] >= P.readyAt);
    return {
      url: location.pathname.split('/').slice(-2).join('/') + location.search, ua: navigator.userAgent, gpu: P.gpu || '?', parallel: !!P.parallel,
      readyAt: P.readyAt, firstFrameMs: f1 ? f1[1] : null, programs: P.links.length, programsByPhase: byPhase, waitMsByPhase: waitByPhase,
      longMax: P.longs.length ? Math.max(...P.longs.map((l) => l[1])) : 0,
      marks: P.marks, phases: P.phases, longs: P.longs, keys: P.keys.filter((k) => k.programs != null),
      frames: P.frames.slice(0, 120),
    };
  };

  function panel() {
    const el = document.createElement('div');
    el.id = 'profkit';
    el.style.cssText = 'position:fixed;left:8px;bottom:8px;z-index:99999;background:rgba(0,0,0,.78);color:#cfe;font:11px/1.35 monospace;padding:6px 8px;border-radius:6px;max-width:46vw;pointer-events:auto;white-space:pre';
    const txt = document.createElement('div');
    const b1 = document.createElement('button'), b2 = document.createElement('button');
    b1.textContent = 'Salin hasil'; b2.textContent = 'Sembunyikan';
    for (const b of [b1, b2]) { b.type = 'button'; b.style.cssText = 'margin:4px 6px 0 0;font:11px monospace'; }
    b1.addEventListener('click', (e) => {
      e.stopPropagation();
      const s = JSON.stringify(P.data());
      (navigator.clipboard ? navigator.clipboard.writeText(s) : Promise.reject()).then(() => { b1.textContent = 'Tersalin'; }, () => { console.log(s); b1.textContent = 'Lihat konsol'; });
    });
    b2.addEventListener('click', (e) => { e.stopPropagation(); el.remove(); clearInterval(iv); });
    el.append(txt, b1, b2);
    document.body.appendChild(el);
    const iv = setInterval(() => {
      const d = P.data(), ph = d.programsByPhase, w = d.waitMsByPhase;
      const lastKeys = d.keys.slice(-4).map((k) => `${k.key}: ${k.programs} prog, frame maks ${Math.round(k.maxFrame)} ms`).join('\n');
      txt.textContent = `PROFKIT ${d.parallel ? '(kompilasi paralel ada)' : '(tanpa kompilasi paralel)'}\n` +
        `GPU: ${String(d.gpu).slice(0, 60)}\n` +
        `siap: ${d.readyAt != null ? (d.readyAt / 1000).toFixed(2) + ' s' : '-'}, frame pertama: ${d.firstFrameMs != null ? Math.round(d.firstFrameMs) + ' ms' : '-'}\n` +
        `program: muat ${ph.muat || 0}, frame1 ${ph.frame1 || 0}, bermain ${(ph.main || 0) + (ph.mulai || 0)}\n` +
        `tunggu program (ms): muat ${w.muat || 0}, frame1 ${w.frame1 || 0}, bermain ${(w.main || 0) + (w.mulai || 0)}\n` +
        `long task maks: ${d.longMax} ms` + (lastKeys ? '\n' + lastKeys : '');
    }, 1000);
  }
  if (document.body) panel(); else addEventListener('DOMContentLoaded', panel);
})();
