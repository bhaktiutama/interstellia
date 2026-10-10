/* AUDIOKIT: fondasi suara bersama (S1, docs/app/rencana-suara.md). Skrip biasa (window.AUDIOKIT), tanpa berkas audio, jalan dari file://.
   Semua fungsi menerima BaseAudioContext, jadi bisa dipakai AudioContext biasa maupun OfflineAudioContext (alat ukur S0).
   Isi: RNG berbenih, bank noise panjang tanpa sambungan terdengar, respons impuls buatan per tempat + ruang konvolusi,
   rantai master (EQ, kompresor lem, limiter), pengubah halus acak (drift), bunyi modus (benda padat dipukul), letupan noise tersaring,
   pembatas jumlah suara, dan analisis buffer (angka "kedataran" untuk tools/ukur_suara.cjs). */
(function () {
  'use strict';
  const K = {};
  // RNG berbenih (mulberry32): hasil sama tiap muat, jadi pengukuran bisa diulang
  K.rng = (seed) => {
    let a = (seed >>> 0) || 1;
    return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  };
  const cache = new WeakMap();
  const store = (ctx) => { let s = cache.get(ctx); if (!s) { s = {}; cache.set(ctx, s); } return s; };

  /* Bank noise: putih, pink (Paul Kellet), cokelat. Panjang 12 s (dulu 2-6 s: pola berulang terdengar), ujung disilang 50 ms ke awal
     sehingga loop tanpa klik. ch 2 = kiri dan kanan tidak berkorelasi (lebar stereo). Disimpan per konteks. */
  K.noise = (ctx, kind = 'pink', sec = 12, ch = 1) => {
    const S = store(ctx), key = `${kind}|${sec}|${ch}`; if (S[key]) return S[key];
    const sr = ctx.sampleRate, n = Math.floor(sr * sec), f = Math.floor(sr * 0.05), b = ctx.createBuffer(ch, n, sr), tmp = new Float32Array(n + f);
    for (let c = 0; c < ch; c++) {
      const r = K.rng(11 + 7919 * c + 131 * kind.length + sec);
      let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0, last = 0;
      for (let i = 0; i < n + f; i++) {
        const w = r() * 2 - 1;
        if (kind === 'pink') {
          b0 = 0.99886 * b0 + w * 0.0555179; b1 = 0.99332 * b1 + w * 0.0750759; b2 = 0.969 * b2 + w * 0.153852;
          b3 = 0.8665 * b3 + w * 0.3104856; b4 = 0.55 * b4 + w * 0.5329522; b5 = -0.7616 * b5 - w * 0.016898;
          tmp[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + w * 0.5362) * 0.11; b6 = w * 0.115926;
        } else if (kind === 'brown') { last = (last + 0.02 * w) / 1.02; tmp[i] = last * 3.5; }
        else tmp[i] = w;
      }
      const d = b.getChannelData(c);
      for (let i = 0; i < n; i++) d[i] = i < f ? tmp[i] * (i / f) + tmp[n + i] * (1 - i / f) : tmp[i];
    }
    return (S[key] = b);
  };
  // sumber loop dari buffer, mulai di titik acak (dua lapisan dari buffer yang sama tidak sefase)
  K.loop = (ctx, buf, r = Math.random) => { const s = ctx.createBufferSource(); s.buffer = buf; s.loop = true; s.start(0, r() * buf.duration); return s; };
  K.filt = (ctx, type, f, q = 0.7, gain = 0) => { const b = ctx.createBiquadFilter(); b.type = type; b.frequency.value = f; b.Q.value = q; b.gain.value = gain; return b; };
  K.gain = (ctx, v = 0) => { const g = ctx.createGain(); g.gain.value = v; return g; };
  K.chain = (...nodes) => { for (let i = 0; i < nodes.length - 1; i++) nodes[i].connect(nodes[i + 1]); return nodes[nodes.length - 1]; };
  // pembentuk lunak (tanh): sedikit distorsi untuk "kasar" mesin; drive 1 = hampir linear
  K.shaper = (ctx, drive = 2) => {
    const w = ctx.createWaveShaper(), n = 1024, c = new Float32Array(n), k = Math.tanh(drive);
    for (let i = 0; i < n; i++) { const x = (i / (n - 1)) * 2 - 1; c[i] = Math.tanh(drive * x) / k; }
    w.curve = c; w.oversample = '2x'; return w;
  };

  /* Respons impuls buatan: pantulan awal (er: [[detik, gain], ...]) + ekor noise meluruh -60 dB dalam `decay` detik,
     makin lama makin gelap (lowpass satu kutub dari `bright` turun ke `damp` Hz). Energi tiap kanal dinormalkan ke 1,
     jadi besar gema = gain kirim (wet) dan bisa diperkirakan. */
  K.ROOMS = {
    cabin: { dur: 0.5, decay: 0.38, pre: 0.0015, bright: 7000, damp: 1100, er: [[0.0029, 0.55], [0.0043, 0.45], [0.0061, 0.38], [0.0082, 0.3], [0.0113, 0.24], [0.0151, 0.18]] },
    helmet: { dur: 0.16, decay: 0.07, pre: 0.0004, bright: 6500, damp: 2600, er: [[0.0008, 0.7], [0.0014, 0.5], [0.0021, 0.35]] },
    hall: { dur: 3.6, decay: 2.6, pre: 0.018, bright: 9000, damp: 1500, er: [[0.021, 0.5], [0.034, 0.42], [0.047, 0.36], [0.062, 0.3], [0.081, 0.24]] },
    void: { dur: 4.5, decay: 4, pre: 0.03, bright: 6000, damp: 700, er: [] },
  };
  K.ir = (ctx, o, seed = 5) => {
    const sr = ctx.sampleRate, n = Math.max(1, Math.floor(sr * o.dur)), b = ctx.createBuffer(2, n, sr), pre = Math.floor(sr * (o.pre || 0));
    for (let ch = 0; ch < 2; ch++) {
      const d = b.getChannelData(ch), r = K.rng(seed + 977 * ch);
      let y = 0, e = 0;
      for (let i = pre; i < n; i++) {
        const t = (i - pre) / sr, fc = o.damp + (o.bright - o.damp) * Math.exp(-3 * t / o.decay), a = Math.exp(-2 * Math.PI * fc / sr);
        y = (1 - a) * (r() * 2 - 1) + a * y;
        const fade = Math.min(1, (n - i) / (0.05 * sr));                       // ujung buffer tanpa potongan
        d[i] = y * Math.exp(-6.91 * t / o.decay) * Math.min(1, t / 0.004) * fade;
      }
      for (const [t, g] of o.er || []) {                                      // pantulan awal: impuls tersebar 0,3 ms, tanda acak per kanal
        const i0 = pre + Math.floor(t * sr * (1 + 0.04 * (r() - 0.5))), s = r() < 0.5 ? -1 : 1, w = Math.max(2, Math.floor(sr * 0.0003));
        for (let k = 0; k < w && i0 + k < n; k++) d[i0 + k] += s * g * (1 - k / w) * 0.9;
      }
      for (let i = 0; i < n; i++) e += d[i] * d[i];
      const k = 1 / Math.sqrt(e || 1); for (let i = 0; i < n; i++) d[i] *= k;
    }
    return b;
  };
  // ruang: send (masukan kirim, dijumlah jadi mono) -> convolver -> out (stereo dari IR). out disambungkan ke tujuan oleh pemanggil.
  K.room = (ctx, preset, wet = 1) => {
    const S = store(ctx), key = 'ir|' + preset;
    const cv = ctx.createConvolver(); cv.normalize = false; cv.buffer = S[key] || (S[key] = K.ir(ctx, K.ROOMS[preset]));
    const send = K.gain(ctx, 1), out = K.gain(ctx, wet);
    send.channelCount = 1; send.channelCountMode = 'explicit';                // masukan mono: konvolusi 2 jalur (IR stereo), bukan 4
    send.connect(cv); cv.connect(out);
    return { send, out };
  };

  /* Rantai master: highpass 22 Hz (buang infrasonik yang hanya memakan headroom), rak rendah / tinggi, kompresor lem (seperti kompresor
     lama: -14 dB, 3:1), limiter puncak -2 dBFS. input = GainNode yang dipakai tombol bisu dan volume; out = sinyal akhir (untuk rekaman). */
  K.master = (ctx, dest, o = {}) => {
    const input = K.gain(ctx, o.gain ?? 1), hp = K.filt(ctx, 'highpass', 22, 0.7);
    const lo = K.filt(ctx, 'lowshelf', o.lowF ?? 110, 0.7, o.low ?? 0), hi = K.filt(ctx, 'highshelf', o.highF ?? 7000, 0.7, o.high ?? 0);
    const glue = ctx.createDynamicsCompressor(); glue.threshold.value = o.thr ?? -14; glue.ratio.value = o.ratio ?? 3; glue.knee.value = 8; glue.attack.value = 0.01; glue.release.value = 0.25;
    const lim = ctx.createDynamicsCompressor(); lim.threshold.value = -2; lim.ratio.value = 20; lim.knee.value = 0; lim.attack.value = 0.002; lim.release.value = 0.12;
    const out = K.gain(ctx, 1);
    K.chain(input, hp, lo, hi, glue, lim, out); out.connect(dest);
    return { input, out, glue, lim };
  };

  // Pengubah halus acak 0..1: jumlah 3 sinus berfrekuensi tak sebanding (hembusan, napas, berkedip pelan); rate = kira-kira siklus per detik
  K.drift = (seed, rate = 0.2) => {
    const r = K.rng(seed), f = [1, 1.618, 2.718].map((k) => k * rate * (0.8 + 0.4 * r())), p = f.map(() => r() * 6.283), w = [0.5, 0.3, 0.2];
    return (t) => 0.5 + 0.5 * (w[0] * Math.sin(6.283 * f[0] * t + p[0]) + w[1] * Math.sin(6.283 * f[1] * t + p[1]) + w[2] * Math.sin(6.283 * f[2] * t + p[2]));
  };

  /* Bunyi modus: benda padat yang dipukul = beberapa parsial sinus tak harmonis yang meluruh sendiri-sendiri (modes: [[Hz, gain, detik -80 dB], ...])
     + transien noise singkat (click: gain, clickF: highpass Hz, clickD: detik). Mengembalikan detik akhir bunyi. */
  K.modal = (ctx, dest, t, modes, o = {}) => {
    const out = K.gain(ctx, o.gain ?? 1); out.connect(dest);
    let end = t + 0.05; const ny = ctx.sampleRate / 2 - 200, att = o.att ?? 0.0012;
    for (const [f, g, d] of modes) {
      if (!(f > 20 && f < ny) || !(g > 0)) continue;
      const os = ctx.createOscillator(), e = ctx.createGain(); os.type = o.type || 'sine'; os.frequency.value = f;
      if (o.bend) os.frequency.setTargetAtTime(f * o.bend, t, d * 0.4);       // nada sedikit turun saat meluruh (logam tebal, kayu)
      e.gain.setValueAtTime(0, t); e.gain.linearRampToValueAtTime(g, t + att); e.gain.exponentialRampToValueAtTime(1e-4 * g, t + att + d);
      os.connect(e).connect(out); os.start(t); os.stop(t + att + d + 0.02); end = Math.max(end, t + att + d + 0.02);
    }
    if (o.click) K.burst(ctx, out, t, { buf: K.noise(ctx, 'white'), type: 'highpass', f0: o.clickF ?? 3000, q: 0.7, att: 0.0005, dur: o.clickD ?? 0.006, peak: o.click });
    return end;
  };
  /* Letupan noise tersaring: o = { buf, type, f0, f1 (sapuan), q, att, dur, peak, pan, delay, r } */
  K.burst = (ctx, dest, t, o) => {
    t += o.delay || 0;
    const s = ctx.createBufferSource(), f = K.filt(ctx, o.type || 'bandpass', o.f0, o.q ?? 0.7), g = ctx.createGain(), r = o.r || Math.random;
    s.buffer = o.buf || K.noise(ctx, 'white');
    if (o.f1) { f.frequency.setValueAtTime(o.f0, t); f.frequency.exponentialRampToValueAtTime(o.f1, t + o.dur); }
    const att = o.att ?? 0.005, pk = Math.max(o.peak, 1e-5);
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(pk, t + att); g.gain.exponentialRampToValueAtTime(pk * 1e-4, t + att + o.dur);
    let last = g;
    if (o.pan && ctx.createStereoPanner) { const p = ctx.createStereoPanner(); p.pan.value = Math.max(-1, Math.min(1, o.pan)); g.connect(p); last = p; }
    s.connect(f).connect(g); last.connect(dest);
    s.start(t, r() * Math.max(0, s.buffer.duration - att - o.dur - 0.1), att + o.dur + 0.05);
    return t + att + o.dur;
  };
  // getar acak: noise lowpass `f` Hz -> param (pengganti LFO berkecepatan tetap yang terdengar seperti tremolo mesin mainan)
  K.flutter = (ctx, prm, f = 10, depth = 0.1, r = Math.random) => { const s = K.loop(ctx, K.noise(ctx, 'white'), r), l = K.filt(ctx, 'lowpass', f, 0.5), g = K.gain(ctx, depth * Math.sqrt(ctx.sampleRate / (2 * f)) * 0.6); K.chain(s, l, g); g.connect(prm); return g; };
  // panner kiri / kanan sederhana (StereoPanner bila ada)
  K.pan = (ctx, dest, v) => { if (!ctx.createStereoPanner) return dest; const p = ctx.createStereoPanner(); p.pan.value = Math.max(-1, Math.min(1, v)); p.connect(dest); return p; };
  // pembatas suara: ok(t, sampai) = boleh memulai bunyi baru bila yang masih berbunyi < max (efek padat seperti tumbukan debu)
  K.voices = (max) => { const ends = []; return { ok(t, until) { for (let i = ends.length - 1; i >= 0; i--) if (ends[i] <= t) ends.splice(i, 1); if (ends.length >= max) return false; ends.push(until); return true; }, get n() { return ends.length; } }; };

  /* Analisis buffer (S0): angka bantu, bukan bukti bagus.
     rms / peak (dBFS), dyn = simpangan baku kekerasan jendela 400 ms (dB; latar diam ~0), flux = perubahan bentuk spektrum per 21 ms
     (0..2, ternormalisasi kekerasan), centroid (Hz), loop = korelasi tertinggi tekstur selubung (Hann 40 ms, langkah 10 ms, tren 0,5 s dibuang) pada jeda 1-8 s (loop noise yang berulang
     mendekati 1), corr = korelasi kiri / kanan (1 = mono). */
  K.analyze = (buf, skip = 1) => {
    const sr = buf.sampleRate, L = buf.getChannelData(0), R = buf.numberOfChannels > 1 ? buf.getChannelData(1) : L;
    const i0 = Math.floor(skip * sr), n = L.length - i0, m = new Float32Array(n);
    let ss = 0, pk = 0, lr = 0, ll = 0, rr = 0;
    for (let i = 0; i < n; i++) { const a = L[i0 + i], b = R[i0 + i]; m[i] = 0.5 * (a + b); ss += m[i] * m[i]; pk = Math.max(pk, Math.abs(a), Math.abs(b)); lr += a * b; ll += a * a; rr += b * b; }
    const db = (x) => 10 * Math.log10(x + 1e-20);
    // kekerasan 400 ms, langkah 100 ms
    const W = Math.floor(0.4 * sr), H = Math.floor(0.1 * sr), st = [];
    for (let a = 0; a + W <= n; a += H) { let s = 0; for (let i = a; i < a + W; i++) s += m[i] * m[i]; const v = db(s / W); if (v > -80) st.push(v); }
    const mean = st.reduce((x, y) => x + y, 0) / Math.max(1, st.length), dyn = Math.sqrt(st.reduce((x, y) => x + (y - mean) ** 2, 0) / Math.max(1, st.length));
    // spektrum: FFT 2048, langkah 1024
    const N = 2048, win = new Float32Array(N); for (let i = 0; i < N; i++) win[i] = 0.5 - 0.5 * Math.cos(2 * Math.PI * i / N);
    const re = new Float32Array(N), im = new Float32Array(N); let prev = null, flux = 0, nf = 0, cen = 0, nc = 0;
    for (let a = 0; a + N <= n; a += N / 2) {
      for (let i = 0; i < N; i++) { re[i] = m[a + i] * win[i]; im[i] = 0; }
      fft(re, im);
      const mag = new Float32Array(N / 2); let tot = 0, wf = 0;
      for (let k = 1; k < N / 2; k++) { mag[k] = Math.hypot(re[k], im[k]); tot += mag[k]; wf += mag[k] * k * sr / N; }
      if (tot < 1e-6) { prev = null; continue; }
      for (let k = 1; k < N / 2; k++) mag[k] /= tot;
      cen += wf / tot; nc++;
      if (prev) { let d = 0; for (let k = 1; k < N / 2; k++) d += Math.abs(mag[k] - prev[k]); flux += d; nf++; }
      prev = mag;
    }
    // pengulangan: selubung RMS berjendela Hann 40 ms tiap 10 ms (jendela Hann membuang riak dari nada tetap seperti dengung 55 Hz,
    // jadi yang terukur hanya pola naik-turun yang benar-benar berulang), korelasi ternormalisasi pada jeda 1-8 s
    const E = Math.floor(0.01 * sr), EW = 4 * E, hw = new Float32Array(EW); for (let i = 0; i < EW; i++) hw[i] = 0.5 - 0.5 * Math.cos(2 * Math.PI * (i + 0.5) / EW);
    const env = []; for (let a = 0; a + EW <= n; a += E) { let s = 0; for (let i = 0; i < EW; i++) s += hw[i] * m[a + i] * m[a + i]; env.push(Math.sqrt(s / EW)); }
    // buang tren lambat (rata-rata bergerak 0,5 s): hembusan dan naik-turun pelan yang disengaja tidak dihitung sebagai pengulangan;
    // yang tersisa = tekstur halus selubung, yang hanya sama persis bila buffer noise yang sama diulang
    const ev = env.map((_, i) => { let s = 0, k = 0; for (let j = Math.max(0, i - 25); j <= Math.min(env.length - 1, i + 25); j++) { s += env[j]; k++; } return env[i] - s / k; });
    let loop = 0;
    for (let lag = 100; lag <= 800 && lag < ev.length / 2; lag++) {
      let s = 0, a2 = 0, b2 = 0; for (let i = 0; i + lag < ev.length; i++) { s += ev[i] * ev[i + lag]; a2 += ev[i] * ev[i]; b2 += ev[i + lag] * ev[i + lag]; }
      if (a2 > 0 && b2 > 0) loop = Math.max(loop, s / Math.sqrt(a2 * b2));
    }
    const r1 = (x) => Math.round(x * 10) / 10, r3 = (x) => Math.round(x * 1000) / 1000;
    return { rms: r1(db(ss / n)), peak: r1(20 * Math.log10(pk + 1e-12)), dyn: r1(dyn), flux: r3(nf ? flux / nf : 0), centroid: Math.round(nc ? cen / nc : 0), loop: r3(loop), corr: r3(ll && rr ? lr / Math.sqrt(ll * rr) : 1) };
  };
  function fft(re, im) {                                                      // radix-2 di tempat
    const n = re.length;
    for (let i = 1, j = 0; i < n; i++) { let bit = n >> 1; for (; j & bit; bit >>= 1) j ^= bit; j ^= bit; if (i < j) { [re[i], re[j]] = [re[j], re[i]]; [im[i], im[j]] = [im[j], im[i]]; } }
    for (let len = 2; len <= n; len <<= 1) {
      const a = -2 * Math.PI / len, wr = Math.cos(a), wi = Math.sin(a);
      for (let i = 0; i < n; i += len) {
        let cr = 1, ci = 0;
        for (let k = 0; k < len / 2; k++) {
          const u = i + k, v = u + len / 2, tr = re[v] * cr - im[v] * ci, ti = re[v] * ci + im[v] * cr;
          re[v] = re[u] - tr; im[v] = im[u] - ti; re[u] += tr; im[u] += ti;
          const nr = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = nr;
        }
      }
    }
  }

  /* Render offline untuk pengukuran: build(ctx) membangun graf dan mengembalikan objek, step(obj, ctx, t, dt) dipanggil tiap 1/30 s
     (OfflineAudioContext.suspend), lalu hasil dianalisis. */
  K.measure = async (build, step, sec = 12, skip = 1, sr = 48000) => {
    const c = new OfflineAudioContext(2, Math.floor(sec * sr), sr), o = build(c), dt = 1 / 30;
    for (let t = dt; t < sec - dt; t += dt) { const tt = t; c.suspend(Math.round(tt * sr) / sr).then(() => { step(o, c, tt, dt); c.resume(); }); }
    step(o, c, 0, dt);
    const buf = await c.startRendering();
    return K.analyze(buf, skip);
  };

  window.AUDIOKIT = K;
})();
