"""Uji UI seragam (docs/app/rencana-ui-seragam.md UI7) di Copper, Millar, Gargantua.
Per experience: kartu mulai tampil tanpa HUD / panel / tombol menu / petunjuk; setelah Mulai: tombol menu, HUD, panel ciut,
petunjuk tombol di tengah bawah; gaya terhitung komponen sama di ketiga experience (font, latar, garis, radius, blur);
H menyembunyikan semua, ` membuka panel; ponsel 375 px tanpa gulir mendatar; tanpa error halaman.
Pakai: python tools/uji_ui.py [cooper|millar|gargantua ...]   (CHROMIUM opsional, three.js dari CDN)"""
import asyncio, json, os, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

EXP = {
    'cooper': {'path': 'experiences/cooper-station/index.html', 'ready': 'window.__stationReady === true',
               'go': "() => document.getElementById('go').click()", 'panel': '#lab', 'menu': '#menuBtn', 'hud': '#hud', 'keys': '#hint', 'toast': '#toast'},
    'millar': {'path': 'experiences/millar/index.html', 'ready': "window.__millarReady === true && !document.getElementById('ready').hidden",
               'go': '() => window.__millar.start()', 'panel': '#lab', 'menu': '#back', 'hud': '#hud', 'keys': '#keys', 'toast': '#msg'},
    'gargantua': {'path': 'experiences/gargantua/index.html', 'ready': "!!window.__gargantua && !document.getElementById('ready').hidden",
                  'go': "() => document.getElementById('go').click()", 'panel': '#ui', 'menu': '#menuLink', 'hud': None, 'keys': '#hint', 'toast': '#toast'},
}

# gaya yang wajib sama di ketiga experience
STYLE_JS = r"""(sel) => {
  const q = (s) => document.querySelector(s), cs = (s, k) => { const e = q(s); return e ? getComputedStyle(e)[k] : null; };
  const pick = (s) => ({ bg: cs(s, 'backgroundColor'), border: cs(s, 'borderTopColor'), radius: cs(s, 'borderTopLeftRadius'), blur: cs(s, 'backdropFilter'),
    font: cs(s, 'fontFamily'), size: cs(s, 'fontSize') });
  return { body: { font: cs('body', 'fontFamily'), size: cs('body', 'fontSize') }, panel: pick(sel.panel), menu: pick(sel.menu),
    head: pick(sel.panel + ' .ui-phead'), card: pick('#start .ui-card'), help: pick('#help .ui-card'), keys: pick(sel.keys), toast: pick(sel.toast),
    tab: pick(sel.panel + ' .ui-tabs button:not(.on)'), tabOn: pick(sel.panel + ' .ui-tabs button.on') };
}"""

VIS_JS = r"""(ids) => { const out = {}; for (const s of ids) { if (!s) continue; const e = document.querySelector(s);
  out[s] = !!e && !e.hidden && getComputedStyle(e).display !== 'none' && getComputedStyle(e).visibility !== 'hidden' && parseFloat(getComputedStyle(e).opacity) > 0.01; }
  return out; }"""


async def run(b, name, cfg, mobile=False):
    vw = {'width': 375, 'height': 740} if mobile else {'width': 1280, 'height': 720}
    ctx = await b.new_context(viewport=vw)
    await ctx.add_init_script("try { localStorage.setItem('cooperStation.tourSeen', '1'); localStorage.setItem('millar.cine', '0'); } catch (e) {}")
    pg = await ctx.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
    pg.on('console', lambda m: errs.append(m.text[:300]) if m.type == 'error' else None)
    await pg.goto((ROOT / cfg['path']).as_uri() + '?lang=id')
    await pg.wait_for_function(cfg['ready'], timeout=600000)
    await pg.wait_for_timeout(1500)
    res, ids = {}, [cfg['menu'], cfg['hud'], cfg['panel'], cfg['keys']]
    pre = await pg.evaluate(VIS_JS, ids)
    res['kartu mulai: tanpa tombol menu, HUD, panel, petunjuk'] = not any(pre.values())
    res['kartu mulai: tombol Mulai terlihat'] = await pg.evaluate("() => !document.getElementById('ready').hidden && document.getElementById('go').offsetParent !== null")
    st = None
    if not mobile:
        st = await pg.evaluate(STYLE_JS, {'panel': cfg['panel'], 'menu': cfg['menu'], 'keys': cfg['keys'], 'toast': cfg['toast']})
        await pg.evaluate("() => { const h = document.getElementById('help'); h.hidden = false; }")
        st['help'] = (await pg.evaluate(STYLE_JS, {'panel': cfg['panel'], 'menu': cfg['menu'], 'keys': cfg['keys'], 'toast': cfg['toast']}))['help']
        res['bantuan bertab (> 2 tab)'] = await pg.evaluate("() => document.querySelectorAll('#help .ui-htabs button').length > 2")
        await pg.evaluate("() => { document.getElementById('help').hidden = true; }")
    await pg.evaluate(cfg['go'])
    await pg.wait_for_timeout(2500)
    post = await pg.evaluate(VIS_JS, ids)
    res['setelah Mulai: tombol menu dan panel terlihat'] = post[cfg['menu']] and post[cfg['panel']]
    if cfg['hud']: res['setelah Mulai: HUD terlihat'] = post[cfg['hud']]
    pc = await pg.evaluate(f"() => {{ const e = document.querySelector('{cfg['panel']}'), r = e.getBoundingClientRect(); return {{ c: e.classList.contains('collapsed'), h: r.height, w: r.width }}; }}")
    res[f"setelah Mulai: panel ciut, kepala saja ({pc['w']:.0f} x {pc['h']:.0f} px)"] = pc['c'] and pc['h'] < 45 and pc['w'] < 260
    k = await pg.evaluate(f"() => {{ const r = document.querySelector('{cfg['keys']}').getBoundingClientRect(); return {{ vis: !document.querySelector('{cfg['keys']}').hidden, cx: (r.left + r.right) / 2, bottom: innerHeight - r.bottom, h: r.height, w: innerWidth }}; }}")
    res[f"petunjuk tombol tengah bawah ({k['cx']:.0f} px dari {k['w']} px, tinggi {k['h']:.0f} px)"] = k['vis'] and abs(k['cx'] - k['w'] / 2) < 2 and k['bottom'] < 120 and k['h'] < 80
    res['tanpa gulir mendatar'] = await pg.evaluate('() => document.documentElement.scrollWidth <= innerWidth + 1')
    if not mobile:
        await pg.mouse.move(640, 360)
        await pg.keyboard.press('Backquote'); await pg.wait_for_timeout(300)
        res['` membuka panel'] = await pg.evaluate(f"() => !document.querySelector('{cfg['panel']}').classList.contains('collapsed')")
        await pg.keyboard.press('Backquote'); await pg.wait_for_timeout(200)
        await pg.keyboard.press('KeyH'); await pg.wait_for_timeout(300)
        hid = await pg.evaluate(VIS_JS, ids)
        res['H menyembunyikan tombol menu, HUD, panel'] = not hid[cfg['menu']] and not hid[cfg['panel']] and not (cfg['hud'] and hid[cfg['hud']])
        await pg.keyboard.press('KeyH'); await pg.wait_for_timeout(300)
        back = await pg.evaluate(VIS_JS, ids)
        res['H lagi = tampil lagi'] = back[cfg['menu']] and back[cfg['panel']]
    res[f'tanpa error halaman ({len(errs)})'] = not errs
    if errs: print('   ', errs[:5])
    await ctx.close()
    return res, st


async def main(names):
    from playwright.async_api import async_playwright
    ok, styles = True, {}
    async with async_playwright() as p:
        kw = {'args': ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required']}
        if os.environ.get('CHROMIUM'): kw['executable_path'] = os.environ['CHROMIUM']
        b = await p.chromium.launch(**kw)
        for n in names:
            for mobile in (False, True):
                res, st = await run(b, n, EXP[n], mobile)
                if st: styles[n] = st
                for k, v in res.items():
                    print(('LULUS ' if v else 'GAGAL ') + f"{n}{' ponsel' if mobile else ''}: {k}"); ok = ok and bool(v)
        await b.close()
    if len(styles) > 1:
        base = next(iter(styles.values()))
        for comp in base:
            for key in base[comp]:
                vals = {n: styles[n][comp].get(key) for n in styles}
                same = len(set(json.dumps(v) for v in vals.values())) == 1
                print(('LULUS ' if same else 'GAGAL ') + f'gaya sama: {comp}.{key} = ' + (json.dumps(base[comp][key]) if same else json.dumps(vals)))
                ok = ok and same
    print('SEMUA LULUS' if ok else 'ADA YANG GAGAL')
    return ok


if __name__ == '__main__':
    sel = [a for a in sys.argv[1:] if a in EXP] or list(EXP)
    sys.exit(0 if asyncio.run(main(sel)) else 1)
