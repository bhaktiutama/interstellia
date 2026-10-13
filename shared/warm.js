/* =====================================================================
   WARMKIT (rencana P1-P4, docs/app/rencana-performa.md): kompilasi shader three.js di layar muat,
   bukan di frame pertama atau saat tombol ditekan. Skrip biasa, tanpa three.js (memakai renderer milik host).

   Kunci program three.js ikut target render yang aktif saat material disiapkan (kanvas vs target: ruang warna
   keluaran dan tone mapping). Karena itu tiap job menyebut target yang sama dengan saat objek itu digambar.

   WARMKIT.compile(renderer, jobs, onStep, opt) -> Promise<{ programs, ready, parallel }>
     jobs: [{ scene, camera, target, targetScene, before, after }]   target null = kanvas; targetScene = scene asal
           bila scene hanya satu objek (kabut dan cahaya dibaca dari scene asal); before/after dipanggil di sekitar
           renderer.compile (mis. memasang material ke quad layar penuh lalu mengembalikannya)
     onStep(frac): dipanggil berulang sampai semua program siap; WAJIB memberi jeda (mis. menunggu satu frame)
     opt.maxMs (bawaan 20000): batas tunggu; program yang belum siap dikompilasi saat dipakai seperti biasa
     opt.batch (bawaan 6): tanpa KHR_parallel_shader_compile, jumlah program yang ditunggu per langkah
   Dengan KHR_parallel_shader_compile: GPU mengompilasi paralel, halaman tidak beku; tiap program yang sudah siap
   "dipakai pertama" (getUniforms: cek galat, baca lokasi uniform) agar frame pertama tidak menunggu lagi.

   WARMKIT.background(renderer, jobs, force) -> jumlah material
     Kompilasi tanpa menunggu (compileAsync), untuk varian yang belum dipakai (mis. mode efek layar lain).
     Hanya bila ada kompilasi paralel (tanpa itu GPU memblokir frame); force = true untuk uji di sandbox.
   ===================================================================== */
(function () {
  'use strict';
  const yieldFrame = () => new Promise((r) => requestAnimationFrame(() => setTimeout(r, 0)));
  function collect(renderer, jobs) {
    const mats = new Set(), rt0 = renderer.getRenderTarget();
    try {
      for (const j of jobs) {
        if (j.before) j.before();
        try {
          renderer.setRenderTarget(j.target == null ? null : j.target);
          renderer.compile(j.scene, j.camera, j.targetScene || null).forEach((m) => mats.add(m));
        } finally { if (j.after) j.after(); }
      }
    } finally { renderer.setRenderTarget(rt0); }
    return mats;
  }
  window.WARMKIT = {
    async compile(renderer, jobs, onStep = yieldFrame, opt = {}) {
      const par = renderer.extensions.has('KHR_parallel_shader_compile');
      const mats = collect(renderer, jobs);
      const progs = [...new Set([...mats].map((m) => renderer.properties.get(m).currentProgram).filter(Boolean))];
      const done = new Set(), t0 = performance.now(), max = opt.maxMs || 20000, batch = opt.batch || 6;
      while (done.size < progs.length && performance.now() - t0 < max) {
        let k = 0;
        for (const p of progs) {
          if (done.has(p)) continue;
          if (par ? p.isReady() : k++ < batch) { p.getUniforms(); done.add(p); }
        }
        await onStep(done.size / Math.max(1, progs.length));
      }
      return { programs: progs.length, ready: done.size, parallel: par };
    },
    background(renderer, jobs, force) {
      if (!force && !renderer.extensions.has('KHR_parallel_shader_compile')) return 0;
      let n = 0;
      try {
        for (const j of jobs) {
          if (j.before) j.before();
          const rt0 = renderer.getRenderTarget();
          try { renderer.setRenderTarget(j.target == null ? null : j.target); n += renderer.compile(j.scene, j.camera, j.targetScene || null).size; }
          finally { renderer.setRenderTarget(rt0); if (j.after) j.after(); }
        }
      } catch (e) { /* abaikan: varian dikompilasi saat dipakai seperti dulu */ }
      return n;
    },
  };
})();
