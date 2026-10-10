// S0 rencana suara (docs/app/rencana-suara.md): ukur suara bawaan secara offline, lama (?snd=0) vs baru, per keadaan.
// Pakai: node tools/ukur_suara.cjs [gargantua] [--md]   (butuh paket playwright; CHROMIUM opsional = path Chromium)
// Tiap keadaan dirender 12 s di OfflineAudioContext (detik pertama dibuang), lalu AUDIOKIT.analyze():
//   rms / peak dBFS, dyn = simpangan baku kekerasan 400 ms (dB), flux = perubahan bentuk spektrum (0..2), centroid Hz,
//   loop = korelasi selubung pada jeda 1-8 s (loop berulang mendekati 1), corr = korelasi kiri / kanan (1 = mono).
// Angka ini alat bantu untuk telinga yang tidak ada (Claude tidak bisa mendengar), bukan bukti suaranya bagus.
const { chromium } = require('playwright');
const path = require('path');
const root = path.resolve(__dirname, '..');

// keadaan per experience: [nama, mix (nilai atau teks fungsi t), events [[detik, jenis, vk]]]
const SCEN = {
  gargantua: [
    ['kabin diam', { hum: 1 }, []],
    ['pendorong (W)', { hum: 1, thr: 0.5 }, []],
    ['mesin utama (Shift)', { hum: 1, thr: 1, main: 1 }, []],
    ['susur piringan + tumbukan', { hum: 1, roar: 0.8, roarCut: 1800 }, 'impacts'],
    ['ping relai melambat', { hum: 1, ping: 't => Math.max(0.05, 1 - t / 13)' }, []],
    ['pasang surut dalam horizon', { hum: 1, tidal: 0.7, tidalF: 't => 60 + 12 * t' }, []],
    ['tesseract', { tess: 1, tT: 't => t' }, []],
    ['suar x2', { hum: 1 }, [[1.5, 'flare'], [6, 'flare']]],
    ['kaca pecah', { hum: 1 }, [[2, 'shatter']]],
  ],
};
const PAGE = { gargantua: ['experiences/gargantua/index.html', 'window.__gargantua !== undefined', 'window.__gargantua'] };

(async () => {
  const ids = process.argv.slice(2).filter((a) => !a.startsWith('--')), md = process.argv.includes('--md');
  const exe = process.env.CHROMIUM || undefined;
  const b = await chromium.launch({ executablePath: exe, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  for (const id of ids.length ? ids : Object.keys(SCEN)) {
    const [file, ready, api] = PAGE[id];
    const pg = await b.newPage({ viewport: { width: 320, height: 200 } });
    const errs = []; pg.on('pageerror', (e) => errs.push(String(e)));
    await pg.goto('file://' + path.join(root, file) + '?lang=id');
    await pg.waitForFunction(ready, null, { timeout: 120000 });
    const rows = [];
    for (const [name, mix, events] of SCEN[id]) {
      const res = {};
      for (const which of ['old', 'new']) {
        res[which] = await pg.evaluate(async ({ api, mix, events, which }) => {
          const G = eval(api), mx = {};
          for (const k in mix) mx[k] = typeof mix[k] === 'string' ? eval(mix[k]) : mix[k];
          let ev = events;
          if (ev === 'impacts') { ev = []; const r = window.AUDIOKIT.rng(9); for (let t = 0.5; t < 11.5; t += 0.05 + 0.3 * r()) ev.push([t, 'impact', 0.4 + 1.1 * r()]); }
          return G.audioMeasure(mx, which, 12, ev);
        }, { api, mix, events, which });
      }
      rows.push([name, res.old, res.new]);
      if (!md) console.log(name.padEnd(30), 'lama', JSON.stringify(res.old), '\n'.padEnd(32), 'baru', JSON.stringify(res.new));
    }
    if (md) {
      console.log(`\n### ${id}\n`);
      console.log('| Keadaan | Versi | RMS dBFS | Puncak dBFS | Variasi dB | Fluks | Pusat Hz | Loop | Korelasi L/R |');
      console.log('| --- | --- | --- | --- | --- | --- | --- | --- | --- |');
      for (const [n, o, w] of rows) for (const [v, x] of [['lama', o], ['baru', w]]) console.log(`| ${v === 'lama' ? n : ''} | ${v} | ${x.rms} | ${x.peak} | ${x.dyn} | ${x.flux} | ${x.centroid} | ${x.loop} | ${x.corr} |`);
    }
    if (errs.length) { console.log('error halaman:', errs.join(' | ')); process.exitCode = 1; }
    await pg.close();
  }
  await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
