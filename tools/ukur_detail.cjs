// Ukur performa halaman detail (experiences/<id>/detail.html): fps per kanvas, tugas panjang saat muat, simulasi di luar layar.
// Pakai: node tools/ukur_detail.cjs [gargantua millar cooper-station]   (butuh paket playwright; CHROMIUM opsional = path Chromium)
// Sandbox tanpa GPU: angka absolut pesimis (raster kanvas di CPU), perbandingan sebelum / sesudah tetap berlaku.
// Konfigurasi: desktop 1440 x 900 DPR 2; ponsel 390 x 844 DPR 3 dengan CPU 4x lebih lambat; simulasi berjalan = desktop CPU 4x.
const { chromium } = require('playwright');
const path = require('path');
const root = path.resolve(__dirname, '..');
const url = (id) => 'file://' + path.join(root, `experiences/${id}/detail.html`) + '?lang=id';
// tombol Jalankan per halaman: [kanvas, pemilih tombol]
const RUN = {
  gargantua: [['cvRay', '#rPre .chip:nth-of-type(1)'], ['cvFall', '#fPlay'], ['cvST', '#sPlay'], ['cvOrb', '#oFine']],
  millar: [['cvTime', '#tPlay'], ['cvHz', '#hPlay'], ['cvWave', '#wPlay'], ['cvOrb', '#oPlay'], ['cvSpin', '#sPlay']],
  'cooper-station': [['cvIn', '#cPlay'], ['cvOrb', '#oPlay']],
};
const fps = (pg, ms = 1800) => pg.evaluate((ms) => new Promise((res) => { let n = 0; const t0 = performance.now(); const f = () => { n++; if (performance.now() - t0 < ms) requestAnimationFrame(f); else res(n / (ms / 1000)); }; requestAnimationFrame(f); }), ms);
const center = (pg, id) => pg.evaluate((id) => document.getElementById(id).scrollIntoView({ behavior: 'instant', block: 'center' }), id);

async function open(b, id, phone, throttle) {
  const ctx = await b.newContext(phone ? { viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true } : { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
  const pg = await ctx.newPage();
  await pg.addInitScript(() => { window.__lt = []; try { new PerformanceObserver((l) => { for (const e of l.getEntries()) window.__lt.push(e.duration); }).observe({ type: 'longtask', buffered: true }); } catch (e) { /* abaikan */ } });
  if (throttle) { const cdp = await ctx.newCDPSession(pg); await cdp.send('Emulation.setCPUThrottlingRate', { rate: throttle }); }
  const t0 = Date.now();
  await pg.goto(url(id));
  await pg.waitForFunction('window.__detailReady === true', null, { timeout: 120000 });
  const ready = Date.now() - t0;
  await pg.waitForTimeout(1500);
  return { ctx, pg, ready };
}

(async () => {
  const ids = process.argv.slice(2).length ? process.argv.slice(2) : ['gargantua', 'millar', 'cooper-station'];
  const b = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
  for (const id of ids) {
    console.log(`\n## ${id}`);
    // 1. muat + desktop
    let { ctx, pg, ready } = await open(b, id, false, 0);
    const lt = await pg.evaluate(() => window.__lt.slice());
    console.log(`muat: siap ${ready} ms, tugas panjang ${lt.length} (terpanjang ${Math.round(Math.max(0, ...lt))} ms, total ${Math.round(lt.reduce((a, x) => a + x, 0))} ms)`);
    const panels = await pg.evaluate(() => PANELS.map((p) => p.el.id));
    const desk = {};
    for (const c of panels) { await center(pg, c); await pg.waitForTimeout(500); desk[c] = await fps(pg); }
    await ctx.close();
    // 2. ponsel CPU 4x
    ({ ctx, pg } = await open(b, id, true, 4));
    const phone = {};
    for (const c of panels) { await center(pg, c); await pg.waitForTimeout(500); phone[c] = await fps(pg); }
    await ctx.close();
    console.log('| Kanvas | Desktop DPR 2 | Ponsel DPR 3 CPU 4x |\n| --- | --- | --- |');
    for (const c of panels) console.log(`| ${c} | ${desk[c].toFixed(0)} | ${phone[c].toFixed(0)} |`);
    // 3. simulasi berjalan, lalu semua di luar layar (desktop CPU 4x)
    ({ ctx, pg } = await open(b, id, false, 4));
    const runs = [];
    for (const [c, btn] of RUN[id] || []) { await center(pg, c); await pg.waitForTimeout(300); await pg.click(btn); await pg.waitForTimeout(300); runs.push(`${c} ${(await fps(pg, 1500)).toFixed(0)}`); }
    await pg.evaluate(() => document.getElementById('galeri').scrollIntoView({ behavior: 'instant' })); await pg.waitForTimeout(400);
    console.log(`simulasi berjalan (desktop CPU 4x, fps sambil menambah satu per satu): ${runs.join(' | ')}; semua di luar layar (galeri): ${(await fps(pg, 1500)).toFixed(0)}`);
    await ctx.close();
  }
  await b.close();
})();
