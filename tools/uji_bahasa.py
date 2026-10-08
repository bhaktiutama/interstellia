"""Uji M3 (Copper Corn Station): kamus English lengkap untuk semua teks statis dan semua t('...') di kode,
label tombol ikut berganti bahasa tanpa muat ulang, kembali ke Indonesia utuh.
Pakai: python tools/uji_bahasa.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, os, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(async () => {
  const S = window.__station, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const EN = S.I18N.en, keys = new Set(Object.keys(EN)), vals = new Set(Object.values(EN));
  const nama = new Set(['Copper Corn Station', 'Bahasa Indonesia', 'English']);
  S.setLang('en'); await wait(500);
  const sisa = [], asing = [];
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = w.nextNode(); n; n = w.nextNode()) {
    if (/^(SCRIPT|STYLE)$/.test(n.parentNode.nodeName) || n.parentNode.closest('#hud .v, #prompt, #toast, #labResult')) continue;
    const k = n.nodeValue.trim(); if (!/[A-Za-z]{2}/.test(k) || nama.has(k) || vals.has(k)) continue;
    if (keys.has(k) && EN[k] !== k) sisa.push(k); else if (!keys.has(k) && !S.LANG.labels.has(n.parentNode.id)) asing.push(k);
  }
  out[`teks statis belum diterjemahkan: ${sisa.length}`] = sisa.length === 0;
  out[`teks statis tanpa entri kamus: ${asing.length}${asing.length ? ' (' + asing.slice(0, 5).join(' | ') + ')' : ''}`] = asing.length === 0;
  const src = document.querySelector('script[type=module]').textContent, re = /\bt\((['`])((?:\\.|(?!\1).)*)\1/g; let m; const hilang = [];
  while ((m = re.exec(src))) { const k = m[2].replace(/\\n/g, '\n'); if (!keys.has(k) && k !== 'Teks {x}') hilang.push(k); }
  out[`t('...') tanpa entri English: ${hilang.length}${hilang.length ? ' (' + hilang.slice(0, 5).join(' | ') + ')' : ''}`] = hilang.length === 0;
  const lab = () => ['labTime', 'labWeather', 'labPreset', 'labSound', 'labHudMode'].map((id) => document.getElementById(id).textContent).join(' | ');
  const en = lab();
  out[`label English: ${en}`] = /Time:/.test(en) && /Weather:/.test(en) && /Sound:/.test(en) && /HUD: (compact|full)/.test(en);
  S.setLang('id'); await wait(300);
  const id = lab();
  out[`kembali ke Indonesia: ${id}`] = /Waktu:/.test(id) && /Cuaca:/.test(id) && /Suara:/.test(id) && document.querySelector('[data-ltab="lokasi"]').textContent === 'Lokasi';
  return out;
})()
"""

async def main():
    page_url = pathlib.Path(__file__).resolve().parent.parent.joinpath('experiences/cooper-station/index.html').as_uri()
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'], **({'executable_path': os.environ['CHROMIUM']} if os.environ.get('CHROMIUM') else {}))
        pg = await b.new_page(viewport={'width': 320, 'height': 200})
        errs = []
        pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
        await pg.goto(page_url)
        await pg.wait_for_function('window.__stationReady === true', timeout=240000)
        for k, v in (await pg.evaluate(UJI)).items(): print(('OK   ' if v else 'GAGAL'), k)
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())
