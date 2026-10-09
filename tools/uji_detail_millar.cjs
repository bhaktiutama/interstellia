// Uji halaman detail Millar's World (experiences/millar/detail.html) + tautan Pelajari di menu.
// Pakai: node tools/uji_detail_millar.cjs   (butuh paket playwright; CHROMIUM opsional = path executable Chromium)
// Cek: angka fisika cocok dengan CONFIG game dan konsep (17,04 jam per detik, lompat 77%, cakrawala 5,3 km, puncak terlihat 146 km,
// 19,5 menit, 123,7 m/s, orbit 10,07 km/s / 89,8 menit, dilatasi ISCO Kerr), simulasi beranimasi walau reduce-motion
// (jam, cakrawala, gelombang, orbit), tersapu bila diam, tanpa error, tanpa gulir mendatar, tanpa tombol bergaris bawah,
// ganti bahasa, tautan menu.
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
    await pg.goto(url('experiences/millar/detail.html') + '?lang=' + lang);
    await pg.waitForFunction('window.__detailReady === true');
    if (tag === 'desktop') {
      const n = await pg.evaluate(() => {
        const d = window.__detail, G = 12.75, v = 3.13;
        return { hps: d.DIL / 3600, jump: (v * v / (2 * G)) / (v * v / (2 * 9.80665)), hor: d.horizon(1.7), vis: d.horizon(1.7) + d.horizon(1200),
          warn: (d.horizon(1.7) + d.horizon(1200)) / 125 / 60, sol: Math.sqrt(G * (0.66 + 1200)), vorb: d.V_ORB, porb: d.P_ORB / 60,
          k14: d.kerrIsco(1e-14).ut, k0: d.kerrIsco(1).ut, kM: d.kerrIsco(1.333e-14).ut, w0: d.waveG(0), cur: d.current(-2500), cur0: d.current(10) };
      });
      ok('1 detik di planet = 17,04 jam di luar', Math.abs(n.hps - 17.045) < 0.01, n.hps.toFixed(3) + ' jam');
      ok('lompatan 77% lompatan Bumi', Math.abs(n.jump - 0.769) < 0.001, (n.jump * 100).toFixed(1) + '%');
      ok('cakrawala dari mata 1,7 m = 5,3 km', Math.abs(n.hor - 5306) < 10, (n.hor / 1e3).toFixed(2) + ' km');
      ok('puncak 1.200 m terlihat dari 146 km', Math.abs(n.vis / 1e3 - 146.3) < 0.5, (n.vis / 1e3).toFixed(1) + ' km');
      ok('peringatan 19,5 menit sebelum tiba', Math.abs(n.warn - 19.5) < 0.1, n.warn.toFixed(2) + ' menit');
      ok('rumus soliter 123,7 m/s', Math.abs(n.sol - 123.7) < 0.05, n.sol.toFixed(2));
      ok('orbit 350 km = 10,07 km/s, 89,8 menit', Math.abs(n.vorb - 10065) < 5 && Math.abs(n.porb - 89.8) < 0.1, `${n.vorb.toFixed(0)} m/s, ${n.porb.toFixed(2)} min`);
      ok('Kerr: tanpa putaran 1,414x', Math.abs(n.k0 - Math.SQRT2) < 1e-6, n.k0.toFixed(4));
      ok('Kerr: 1 - a = 1e-14 memberi 67.526x (Python 60 digit)', Math.abs(n.k14 - 67526.43) < 1, n.k14.toFixed(2));
      ok('Kerr: 1 - a = 1,333e-14 memberi sekitar 61.362x', Math.abs(n.kM - 61362) / 61362 < 0.001, n.kM.toFixed(1));
      ok('waveG(0) = 1, arus 0 di belakang muka, arus maks 1,6 m/s di 2,5 km', n.w0 === 1 && n.cur0 === 0 && Math.abs(n.cur - 1.6) < 0.01, `${n.w0}, ${n.cur0}, ${n.cur.toFixed(3)}`);
    }
    // jam: beranimasi walau reduce-motion
    await go(pg, 'waktu'); await pg.click('#tPlay'); await pg.waitForTimeout(1000);
    const t1 = await pg.evaluate(() => ({ t: window.__detail.TS.t, T: window.__detail.TS.T, done: window.__detail.TS.done }));
    ok(`${tag}: dua jam beranimasi walau reduce-motion`, t1.t > 0 && t1.t < t1.T && !t1.done, `${t1.t.toFixed(0)} dari ${t1.T.toFixed(0)} s`);
    // cakrawala: dari 200 km, puncak muncul di 146 km
    await go(pg, 'cakrawala'); await pg.click('#hPlay'); await pg.waitForTimeout(1000);
    const h1 = await pg.evaluate(() => ({ t: window.__detail.HZS.t, T: window.__detail.HZS.T }));
    ok(`${tag}: cakrawala beranimasi`, h1.t > 20 && h1.t < h1.T, h1.t.toFixed(0) + ' s');
    await pg.evaluate(() => { const r = document.getElementById('hTs'); r.value = 0.3; r.dispatchEvent(new Event('input')); });
    const hv = await pg.evaluate(() => document.getElementById('hVerd').textContent);
    ok(`${tag}: 140 km = puncak sudah terlihat`, /visible|terlihat|muncul|peaks|rises/i.test(hv), hv.slice(0, 60));
    // gelombang: diam = tersapu
    await go(pg, 'gelombang'); await pg.click('[data-wr="0"]'); await pg.waitForTimeout(800);
    const w1 = await pg.evaluate(() => ({ t: window.__detail.WVS.t, swept: window.__detail.WVX.swept }));
    ok(`${tag}: gelombang beranimasi`, w1.t > 1 && w1.t < 10 && !w1.swept, w1.t.toFixed(1) + ' s');
    await pg.evaluate(() => { const r = document.getElementById('wTs'); r.value = 1; r.dispatchEvent(new Event('input')); });
    const w2 = await pg.evaluate(() => ({ swept: window.__detail.WVX.swept, feet: window.__detail.waveState(window.__detail.WVS.t).feet }));
    ok(`${tag}: diam = tersapu (air di kaki > 1,7 m)`, w2.swept && w2.feet > 1.7, w2.feet.toFixed(0) + ' m');
    // orbit: naik lalu mengorbit
    await go(pg, 'orbit'); await pg.click('#oPlay'); await pg.waitForTimeout(1500);
    const o1 = await pg.evaluate(() => ({ t: window.__detail.OBS.t }));
    ok(`${tag}: orbit beranimasi (naik dulu)`, o1.t > 1 && o1.t < 40, o1.t.toFixed(1) + ' s');
    await pg.evaluate(() => { const r = document.getElementById('oTs'); r.value = 0.5; r.dispatchEvent(new Event('input')); });
    const ov = await pg.evaluate(() => document.getElementById('oV').textContent);
    ok(`${tag}: di orbit laju 10,07 km/s`, /10[.,]07 km\/s/.test(ov), ov);
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
  const href = await pg.getAttribute('#millar a.learn', 'href');
  ok('menu: tautan Pelajari Millar', href === 'experiences/millar/detail.html?lang=en', href);
  ok('menu: tanpa error', errs.length === 0, errs.join(' | '));
  await b.close();
  console.log(fail ? `${fail} GAGAL` : 'semua lulus');
  process.exit(fail ? 1 : 0);
})();
