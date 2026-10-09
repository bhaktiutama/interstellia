// Uji halaman detail Copper Corn Station (experiences/cooper-station/detail.html) + tautan Pelajari di menu.
// Pakai: node tools/uji_detail_copper.cjs   (butuh paket playwright; CHROMIUM opsional = path executable Chromium)
// Cek: termuat tanpa error di desktop dan ponsel, tanpa gulir mendatar, tanpa tombol bergaris bawah (juga di menu), angka fisika cocok dengan rumus dan teks game,
// simulasi Coriolis dan lift berjalan, ganti bahasa, tautan menu ke halaman detail.
const { chromium } = require('playwright');
const path = require('path');
const root = path.resolve(__dirname, '..');
const url = (p) => 'file://' + path.join(root, p);
let fail = 0;
// tombol (a / button berlatar, bersudut bulat, atau berpadding) yang teksnya bergaris bawah
const underlined = (pg) => pg.evaluate(() => [...document.querySelectorAll('a, button')].filter((e) => {
  const cs = getComputedStyle(e), r = e.getBoundingClientRect();
  if (!r.width || cs.display === 'none') return false;
  const btn = parseFloat(cs.borderRadius) > 4 || cs.backgroundColor !== 'rgba(0, 0, 0, 0)' || parseFloat(cs.paddingLeft) > 4;
  return btn && [e, ...e.querySelectorAll('*')].some((c) => getComputedStyle(c).textDecorationLine.includes('underline'));
}).map((e) => `${e.tagName.toLowerCase()}.${e.className} "${e.textContent.trim().slice(0, 30)}"`));
const ok = (name, cond, info = '') => { console.log(`${cond ? 'OK   ' : 'GAGAL'} ${name}${info ? ' · ' + info : ''}`); if (!cond) fail++; };

(async () => {
  const opt = process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {};
  const b = await chromium.launch(opt);
  for (const [vw, vh, tag, lang] of [[1440, 900, 'desktop', 'id'], [390, 844, 'ponsel', 'en']]) {
    const pg = await b.newPage({ viewport: { width: vw, height: vh } }); const errs = [];
    pg.on('pageerror', (e) => errs.push(e.message));
    pg.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') errs.push(m.text()); });
    await pg.goto(url('experiences/cooper-station/detail.html') + '?lang=' + lang);
    await pg.waitForFunction('window.__detailReady === true');
    if (tag === 'desktop') {
      const n = await pg.evaluate(() => {
        const d = window.__detail, a = d.traj(176.5, 0), f = d.traj(0, 10), s = (t) => { d.LF.d = t[0]; d.LF.dir = 1; d.LF.v = t[1]; d.LF.a = t[2]; d.LF.run = true; return d.liftState(); };
        return { dropT: a.T, miss: -a.land, fount: f.land, peak: f.hmax, cruise: s([500, 20, 0]), ceil: s([950, 6, -1]) };
      });
      ok('bola dek 176,5 m: 6,96 s', Math.abs(n.dropT - 6.955) < 0.002, n.dropT.toFixed(3) + ' s');
      ok('bola dek: 85,7 m melawan putaran (sama dengan catatan peta di game)', Math.abs(n.miss - 85.67) < 0.05, n.miss.toFixed(2) + ' m');
      ok('air mancur 10 m/s: puncak 5,1 m, mendarat 1,3-1,4 m di depan', n.peak > 5 && n.peak < 5.2 && n.fount > 1.3 && n.fount < 1.4, `${n.peak.toFixed(2)} m, ${n.fount.toFixed(3)} m`);
      ok('lift 20 m/s di 500 m: dorongan samping 2 omega v = 0,40 g', Math.abs(n.cruise.side / 9.81 - 0.404) < 0.002, (n.cruise.side / 9.81).toFixed(3) + ' g');
      ok('lift mengerem di 950 m: terangkat ke langit-langit', n.ceil.down < 0, n.ceil.down.toFixed(3) + ' m/s2');
    }
    await pg.evaluate(() => document.getElementById('coriolis').scrollIntoView({ behavior: 'instant' }));
    await pg.click('#cPlay'); await pg.waitForTimeout(4500);
    const done = await pg.evaluate(() => window.__detail.CS.done);
    ok(`${tag}: simulasi Coriolis selesai`, done === true);
    for (const v of ['in', 'out']) await pg.evaluate((v) => document.querySelector(`[data-hv="${v}"]`).click(), v);
    const cap = await pg.evaluate(() => document.getElementById('heroCap').textContent);
    ok(`${tag}: keterangan mode hero`, cap.length > 20, cap.slice(0, 50));
    await pg.evaluate(() => document.getElementById('lift').scrollIntoView({ behavior: 'instant' }));
    await pg.click('#lUp'); await pg.waitForTimeout(2500);
    const h = await pg.evaluate(() => parseFloat(document.getElementById('lH').textContent.replace(/[^\d,.]/g, '').replace(',', '.')));
    ok(`${tag}: lift bergerak`, h > 10, h + ' m');
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
  const href = await pg.getAttribute('a.learn', 'href');
  ok('menu: tautan Pelajari', href === 'experiences/cooper-station/detail.html?lang=en', href);
  ok('menu: tanpa error', errs.length === 0, errs.join(' | '));
  ok('menu: tanpa tombol bergaris bawah', (await underlined(pg)).length === 0, (await underlined(pg)).join(' | '));
  await b.close();
  console.log(fail ? `${fail} GAGAL` : 'semua lulus');
  process.exit(fail ? 1 : 0);
})();
