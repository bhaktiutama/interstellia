// Uji halaman detail Gargantua (experiences/gargantua/detail.html) + tautan Pelajari di menu.
// Pakai: node tools/uji_detail_gargantua.cjs   (butuh paket playwright; CHROMIUM opsional = path executable Chromium)
// Cek: angka fisika cocok dengan rumus dan teks game, hero dijejak sinar (sisi mendekat lebih terang di mode fisika), simulasi
// beranimasi walau reduce-motion (tidak langsung ke akhir), sinar / jatuh / pulsa / orbit berjalan, tanpa error, tanpa gulir mendatar,
// tanpa tombol bergaris bawah, ganti bahasa, tautan menu.
const { chromium } = require('playwright');
const path = require('path');
const root = path.resolve(__dirname, '..');
const url = (p) => 'file://' + path.join(root, p);
let fail = 0;
const underlined = (pg) => pg.evaluate(() => [...document.querySelectorAll('a, button')].filter((e) => {
  const cs = getComputedStyle(e), r = e.getBoundingClientRect();
  if (!r.width || cs.display === 'none') return false;
  const btn = parseFloat(cs.borderRadius) > 4 || cs.backgroundColor !== 'rgba(0, 0, 0, 0)' || parseFloat(cs.paddingLeft) > 4;
  return btn && [e, ...e.querySelectorAll('*')].some((c) => getComputedStyle(c).textDecorationLine.includes('underline'));
}).map((e) => `${e.tagName.toLowerCase()}.${e.className} "${e.textContent.trim().slice(0, 30)}"`));
const ok = (name, cond, info = '') => { console.log(`${cond ? 'OK   ' : 'GAGAL'} ${name}${info ? ' · ' + info : ''}`); if (!cond) fail++; };
const go = (pg, id) => pg.evaluate((id) => document.getElementById(id).scrollIntoView({ behavior: 'instant' }), id);

(async () => {
  const opt = process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {};
  const b = await chromium.launch(opt);
  for (const [vw, vh, tag, lang] of [[1440, 900, 'desktop', 'id'], [390, 844, 'ponsel', 'en']]) {
    const pg = await b.newPage({ viewport: { width: vw, height: vh }, reducedMotion: 'reduce' }); const errs = [];
    pg.on('pageerror', (e) => errs.push(e.message));
    pg.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') errs.push(m.text()); });
    await pg.goto(url('experiences/gargantua/detail.html') + '?lang=' + lang);
    await pg.waitForFunction('window.__detailReady === true');
    if (tag === 'desktop') {
      const n = await pg.evaluate(() => {
        const d = window.__detail, stop = (x, y, vx) => x > 15 && vx > 0;
        const ray = (bb) => d.rayTrace(-15, bb, 1, 0, stop, 0.012);
        const crit = d.critD(22), Lc = (22 * Math.sin((crit - 1e-4) * Math.PI / 180)) / Math.sqrt(21);
        const gw = d.geodesic(22, Lc, 1, 9000), ge = d.geodesic(22, (22 * Math.sin(26 * Math.PI / 180)) / Math.sqrt(21), 1, 9000);
        return { crit, fall: d.tauFall(22, 1), inside: d.tauFall(1, 0) * 985.27, seen: d.seenR(120), tide: d.tidalG(1), rel: 2 * d.vGas(3) / (1 + d.vGas(3) ** 2),
          r25: ray(2.5).cap, r26: ray(2.6).cap, bend7: Math.abs(ray(7).bend) * 180 / Math.PI,
          whirl: [gw.end, Math.abs(gw.ph[gw.ph.length - 1]) / (2 * Math.PI)], esc: ge.end };
      });
      ok('sudut kritis 22 rs = 24,62 derajat (teks game)', Math.abs(n.crit - 24.62) < 0.005, n.crit.toFixed(4));
      ok('jatuh 22 rs ke horizon 68,13 rs/c = 18,65 jam', Math.abs(n.fall - 68.126) < 0.01, `${n.fall.toFixed(3)} rs/c, ${(n.fall * 985.27 / 3600).toFixed(2)} h`);
      ok('horizon ke pusat 656,8 s', Math.abs(n.inside - 656.8) < 0.2, n.inside.toFixed(1) + ' s');
      ok('relai tidak pernah melihat wahana lewat horizon', n.seen > 1 && n.seen < 1.01, n.seen.toFixed(6) + ' rs');
      ok('pasang surut di horizon 2,1e-7 g', Math.abs(n.tide - 2.1e-7) < 0.05e-7, n.tide.toExponential(2));
      ok('gas melawan arus di ISCO 0,8 c', Math.abs(n.rel - 0.8) < 1e-9, n.rel.toFixed(4));
      ok('sinar b 2,5 tertangkap, b 2,6 lolos (batas 2,598)', n.r25 === true && n.r26 === false);
      ok('sinar b 7 dibelokkan sekitar 20 derajat', n.bend7 > 18 && n.bend7 < 22, n.bend7.toFixed(1) + '°');
      ok('bidik 1e-4 derajat di bawah kritis: zoom-whirl lalu tertangkap', n.whirl[0] === 'cap' && n.whirl[1] > 3, `${n.whirl[0]}, ${n.whirl[1].toFixed(2)} putaran`);
      ok('bidik 26 derajat: lolos', n.esc === 'esc');
      await pg.click('[data-hv="phys"]'); await pg.waitForTimeout(300);
      const lr = await pg.evaluate(() => { const m = window.__detail.HB.map, N = m.N; let l = 0, r = 0, nl = 0, nr = 0;
        for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) { const k = j * N + i; if (m.kind[k] !== 1) continue; if (i < N / 2) { l += m.sh[k] ** 4; nl++; } else { r += m.sh[k] ** 4; nr++; } }
        return { l: l / nl, r: r / nr, hole: m.kind.filter((x) => x === 2).length }; });
      ok('hero: sisi mendekat lebih terang (gD)^4 di mode fisika', lr.l > 2 * lr.r && lr.hole > 50, `${lr.l.toFixed(2)} vs ${lr.r.toFixed(2)}, bayangan ${lr.hole} px`);
    }
    // jatuh: beranimasi walau reduce-motion
    await go(pg, 'jatuh'); await pg.click('#fPlay'); await pg.waitForTimeout(1000);
    const f1 = await pg.evaluate(() => ({ t: window.__detail.FS.t, done: window.__detail.FS.done }));
    ok(`${tag}: jatuh beranimasi walau reduce-motion`, f1.t > 3 && f1.t < 30 && !f1.done, `t ${f1.t.toFixed(1)} rs/c`);
    await pg.evaluate(() => { const r = document.getElementById('fTs'); r.value = 0.685; r.dispatchEvent(new Event('input')); });
    const fv = await pg.evaluate(() => document.getElementById('fVerd').textContent);
    ok(`${tag}: geser waktu lewat horizon memberi pesan horizon`, /horizon/i.test(fv), fv.slice(0, 50));
    // sinar
    await go(pg, 'lensa'); await pg.click('#rPre .chip:nth-of-type(1)'); await pg.waitForTimeout(400);
    const r1 = await pg.evaluate(() => ({ t: window.__detail.RYS.t, res: !!window.__detail.RY.res }));
    ok(`${tag}: foton berjalan (tidak langsung ke akhir)`, r1.res && r1.t > 0 && r1.t < 1, r1.t.toFixed(2));
    await pg.waitForTimeout(6000);
    const ro = await pg.evaluate(() => document.getElementById('rOut').textContent);
    ok(`${tag}: sinar b 1,5 tertangkap`, /Captured|Tertangkap/.test(ro), ro);
    // pulsa relai
    await go(pg, 'relai'); await pg.click('#sPlay'); await pg.waitForTimeout(5000);
    const s1 = await pg.evaluate(() => ({ sent: window.__detail.ST.pulses.length, got: window.__detail.ST.gotN }));
    ok(`${tag}: pulsa terkirim dan tiba di relai`, s1.sent >= 2 && s1.got >= 1, `${s1.sent} terkirim, ${s1.got} tiba`);
    await pg.evaluate(() => { const r = document.getElementById('sTs'); r.value = 1; r.dispatchEvent(new Event('input')); });
    const s2 = await pg.evaluate(() => ({ sent: window.__detail.ST.pulses.length, got: window.__detail.ST.gotN, inside: window.__detail.ST.pulses.filter((p) => p.inside).length }));
    ok(`${tag}: pulsa dari dalam horizon tidak pernah tiba`, s2.inside >= 1 && s2.got === s2.sent - s2.inside, `${s2.got} dari ${s2.sent}, ${s2.inside} dari dalam`);
    // orbit
    await go(pg, 'orbit'); await pg.click('#oFine'); await pg.waitForTimeout(1200);
    const o1 = await pg.evaluate(() => ({ t: window.__detail.OS.t, path: !!window.__detail.OR.path }));
    ok(`${tag}: orbit beranimasi`, o1.path && o1.t > 0 && o1.t < 1, o1.t.toFixed(2));
    const over = await pg.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    ok(`${tag}: tanpa gulir mendatar`, over <= 0, over + ' px');
    await pg.click(`#lang button[data-lang="${lang === 'id' ? 'en' : 'id'}"]`);
    const title = await pg.title();
    ok(`${tag}: ganti bahasa`, lang === 'id' ? /Physics/.test(title) : /Fisika/.test(title), title);
    ok(`${tag}: tanpa error`, errs.length === 0, errs.slice(0, 3).join(' | '));
    ok(`${tag}: tanpa tombol bergaris bawah`, (await underlined(pg)).length === 0, (await underlined(pg)).join(' | '));
    await pg.close();
  }
  const pg = await b.newPage(); const errs = [];
  pg.on('pageerror', (e) => errs.push(e.message));
  await pg.goto(url('index.html') + '?lang=en');
  const href = await pg.getAttribute('#gargantua a.learn', 'href');
  ok('menu: tautan Pelajari Gargantua', href === 'experiences/gargantua/detail.html?lang=en', href);
  ok('menu: tanpa error', errs.length === 0, errs.join(' | '));
  await b.close();
  console.log(fail ? `${fail} GAGAL` : 'semua lulus');
  process.exit(fail ? 1 : 0);
})();
