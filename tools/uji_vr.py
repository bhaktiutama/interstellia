"""Uji VR tanpa headset (rencana VR, docs/app/rencana-vr.md, tahap VR7) memakai XR tiruan tools/xr_tiruan.js.

Pakai:
  python tools/uji_vr.py               # semua bagian yang ada
  python tools/uji_vr.py vr0           # satu bagian
Lingkungan: THREE_LOCAL=<folder three.module.js + three.core.js> untuk sandbox tanpa CDN, CHROMIUM=<jalur chrome> opsional.

Bagian:
  vr0  halaman uji docs/app/vr/uji-webxr.html: sesi terbuka, framebuffer 2 mata, warna latar beda per mata, kepala dan tombol terbaca
  vr1  prototipe jalur render docs/app/vr/uji-jalur-render.html (shared/vr.js): kedua mata tergambar lewat rantai efek layar,
       paralaks antar mata, belok patah, menu VR (X) tergambar, keluar VR
  vr2  Gargantua (experiences/gargantua): tombol Masuk VR, kedua mata tergambar (ray tracer + efek layar ke viewport mata),
       kokpit misi berparalaks, kepala memutar pandangan, stik kiri = W (MIS.keys), picu kanan = suar, belok patah,
       notifikasi di headset, menu VR, keluar VR lalu loop layar jalan lagi
Bagian experience lain ditambahkan oleh tahap VR3-VR4 (lihat BAGIAN).
"""
import asyncio, json, os, pathlib, sys
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
TIRUAN = (ROOT / 'tools' / 'xr_tiruan.js').read_text()

async def buka(b, rel, q=''):
    pg = await b.new_page(viewport={'width': 640, 'height': 400})
    pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)[:300]))
    pg.on('console', lambda m: pg.errs.append('console: ' + m.text[:300]) if m.type == 'error' else None)
    local = os.environ.get('THREE_LOCAL')
    if local:
        async def serve(route):
            await route.fulfill(path=str(pathlib.Path(local) / route.request.url.rsplit('/', 1)[-1]), content_type='text/javascript',
                                headers={'Access-Control-Allow-Origin': '*'})
        await pg.route('https://cdn.jsdelivr.net/**', serve)
    await pg.add_init_script(TIRUAN)
    await pg.goto(ROOT.joinpath(rel).as_uri() + q)
    return pg

async def vr0(b, out):
    pg = await buka(b, 'docs/app/vr/uji-webxr.html')
    await pg.wait_for_function('window.__vr0 && window.__vr0.supported === true', timeout=30000)
    await pg.click('#enter')
    await pg.wait_for_function('window.__vr0.frames > 30', timeout=60000)
    await pg.evaluate('__xrTiruan.head.p[0] += 0.3; __xrTiruan.pad("right", 0, 1); __xrTiruan.pad("left", 4, 1); __xrTiruan.axes("left", 0.8, -0.5)')
    await pg.wait_for_timeout(800)
    R = await pg.evaluate('JSON.parse(JSON.stringify(window.__vr0, (k, v) => v instanceof Set ? [...v] : v))')
    eye = await pg.evaluate('(() => { const m = (i) => { const e = __xrTiruan.readEye(i), d = e.rgba, o = (e.h - 2) * e.w * 4; let r = 0, b = 0; for (let k = o; k < o + 4 * 40; k += 4) { r += d[k]; b += d[k + 2]; } return [r, b]; }; return [m(0), m(1)]; })()')
    out[f"vr0: sesi terbuka, framebuffer {R['fbW']} x {R['fbH']}, {R['views']} mata ({', '.join(R['viewSize'])})"] = R['fbW'] == 640 and R['views'] == 2
    out[f"vr0: frame sesi {R['frames']}, kepala bergerak {R['headMoved']:.2f} m"] = R['frames'] > 30 and R['headMoved'] > 0.25
    out[f"vr0: latar mata kiri kemerahan (r {eye[0][0]} > b {eye[0][1]}), kanan kebiruan (b {eye[1][1]} > r {eye[1][0]})"] = eye[0][0] > eye[0][1] and eye[1][1] > eye[1][0]
    out[f"vr0: tombol tercatat {R['buttons']}, stik {R['axesMax']}"] = 0 in R['buttons'].get('right', []) and 4 in R['buttons'].get('left', []) and R['axesMax'].get('left', [0, 0, 0])[2] > 0.7
    await pg.click('#exit'); await pg.wait_for_timeout(300)
    out['vr0: keluar VR, tombol Masuk aktif lagi'] = await pg.evaluate('!document.getElementById("enter").disabled')
    out[f"vr0: tanpa error halaman {pg.errs[:2]}"] = not pg.errs
    await pg.close()

MATA = """(() => { const st = (i) => { const e = __xrTiruan.readEye(i), d = e.rgba; let lit = 0, sum = 0; for (let k = 0; k < d.length; k += 4) { const v = d[k] + d[k + 1] + d[k + 2]; sum += v; if (v > 30) lit++; } return { lit: lit / (d.length / 4), mean: sum / (d.length / 4) }; };
  const a = __xrTiruan.readEye(0).rgba, b = __xrTiruan.readEye(1).rgba; let diff = 0; for (let k = 0; k < a.length; k += 4) diff += Math.abs(a[k] - b[k]) + Math.abs(a[k + 1] - b[k + 1]) + Math.abs(a[k + 2] - b[k + 2]);
  return { L: st(0), R: st(1), diff: diff / (a.length / 4) }; })()"""

async def vr1(b, out):
    pg = await buka(b, 'docs/app/vr/uji-jalur-render.html')
    await pg.wait_for_function('window.__jalur && window.__jalur.ok', timeout=60000)
    await pg.click('#vrBtn')
    await pg.wait_for_function('window.__jalur.VRU.frames > 20', timeout=60000)
    m = await pg.evaluate(MATA)
    out[f"vr1: kedua mata tergambar (terang {m['L']['lit']:.2f} / {m['R']['lit']:.2f}), beda antar mata {m['diff']:.1f} (paralaks)"] = m['L']['lit'] > 0.5 and m['R']['lit'] > 0.5 and m['diff'] > 2
    seen = await pg.evaluate('(async () => { __xrTiruan.axes("right", 0.9, 0); let t = 0; for (let k = 0; k < 30; k++) { await new Promise((r) => requestAnimationFrame(r)); t += Math.abs(VRKIT.in.turn || 0); } return t; })()')
    await pg.evaluate('__xrTiruan.axes("right", 0, 0)')
    out[f"vr1: belok patah dari stik kanan ({seen * 180 / 3.14159:.0f} derajat, sekali per dorongan)"] = abs(seen * 180 / 3.14159 - 30) < 1
    await pg.evaluate('__xrTiruan.pad("left", 4, 1)'); await pg.wait_for_timeout(200); await pg.evaluate('__xrTiruan.pad("left", 4, 0)'); await pg.wait_for_timeout(300)
    menu = await pg.evaluate('VRKIT.menu')
    m2 = await pg.evaluate(MATA)
    out[f"vr1: X membuka menu VR ({menu}), panel tergambar di atas adegan (terang kiri {m['L']['mean']:.0f} -> {m2['L']['mean']:.0f}, adegan tetap {m2['L']['lit']:.2f})"] = menu and abs(m2['L']['mean'] - m['L']['mean']) > 1 and m2['L']['lit'] > 0.5
    await pg.click('#vrBtn'); await pg.wait_for_timeout(300)
    out['vr1: keluar VR'] = await pg.evaluate('!VRKIT.on')
    out[f"vr1: tanpa error halaman {pg.errs[:2]}"] = not pg.errs
    await pg.close()

async def tunggu_frame(pg, n=6):
    await pg.evaluate(f'(async () => {{ const f0 = __xrTiruan.frames; while (__xrTiruan.frames < f0 + {n}) await new Promise((r) => setTimeout(r, 30)); }})()')

async def vr2(b, out):
    pg = await buka(b, 'experiences/gargantua/index.html', '?lang=id')
    await pg.wait_for_function('window.__gargantua !== undefined && window.VRKIT && VRKIT.ok', timeout=60000)
    out['vr2: tombol Masuk VR muncul'] = await pg.evaluate('!!document.getElementById("vrBtn")')
    await pg.evaluate('VRKIT.enter()')
    await pg.wait_for_function('__gargantua.GV.on && __xrTiruan.frames > 8', timeout=60000)
    await tunggu_frame(pg)
    m = await pg.evaluate(MATA)
    G = await pg.evaluate('({ rs: __gargantua.GV.rs, sw: 0 })')
    out[f"vr2: kedua mata tergambar di luar misi (rata-rata {m['L']['mean']:.0f} / {m['R']['mean']:.0f}, terang {m['L']['lit']:.2f} / {m['R']['lit']:.2f}, skala {G['rs']})"] = m['L']['mean'] > 3 and m['R']['mean'] > 3 and m['L']['lit'] > 0.02
    f0 = await pg.evaluate('__gargantua.state.frame')
    await tunggu_frame(pg, 4)
    out['vr2: dunia berjalan dari loop headset (tickWorld)'] = await pg.evaluate(f'__gargantua.state.frame > {f0} && __gargantua.GV.idle')
    # misi di kokpit: interior dekat = paralaks besar antar mata
    await pg.evaluate("const G = __gargantua; G.startMission('polar'); G.SHIP.view = 'cockpit'")
    await tunggu_frame(pg)
    m = await pg.evaluate(MATA)
    out[f"vr2: kokpit misi tergambar (rata-rata {m['L']['mean']:.0f}), beda antar mata {m['diff']:.1f} (paralaks interior)"] = m['L']['mean'] > 3 and m['diff'] > 2
    a = await pg.evaluate('__xrTiruan.readEye(0).rgba')
    await pg.evaluate('__xrTiruan.head.yaw = 1.2'); await tunggu_frame(pg)
    bb = await pg.evaluate('__xrTiruan.readEye(0).rgba')
    d = sum(abs(x - y) for x, y in zip(a, bb)) / (len(a) / 4)
    await pg.evaluate('__xrTiruan.head.yaw = 0')
    out[f"vr2: kepala menoleh 69 derajat mengubah gambar mata kiri (beda {d:.1f})"] = d > 5
    await pg.evaluate('__xrTiruan.axes("left", 0, -0.9)'); await tunggu_frame(pg, 3)
    w = await pg.evaluate('__gargantua.MIS.keys.has("KeyW")')
    await pg.evaluate('__xrTiruan.axes("left", 0, 0)'); await tunggu_frame(pg, 3)
    w2 = await pg.evaluate('__gargantua.MIS.keys.has("KeyW")')
    out['vr2: stik kiri maju = W (dorong) selama ditahan, lepas = berhenti'] = w and not w2
    n0 = await pg.evaluate('__gargantua.REL.flares.length')
    await pg.evaluate('__xrTiruan.pad("right", 0, 1)'); await tunggu_frame(pg, 3); await pg.evaluate('__xrTiruan.pad("right", 0, 0)'); await tunggu_frame(pg, 2)
    n1 = await pg.evaluate('__gargantua.REL.flares.length')
    out[f"vr2: picu kanan = suar ({n0} -> {n1}), notifikasi di headset {await pg.evaluate('VRKIT.noteOn()')}"] = n1 == min(4, n0 + 1) and await pg.evaluate('VRKIT.noteOn()')
    await pg.evaluate('__xrTiruan.axes("right", 0.9, 0)'); await tunggu_frame(pg, 4); await pg.evaluate('__xrTiruan.axes("right", 0, 0)'); await tunggu_frame(pg, 2)
    yaw = await pg.evaluate('__gargantua.GV.yaw')
    out[f"vr2: belok patah stik kanan ({yaw * 180 / 3.14159:.0f} derajat)"] = abs(abs(yaw * 180 / 3.14159) - 30) < 1
    await pg.evaluate('__xrTiruan.pad("right", 4, 1)'); await tunggu_frame(pg, 3); await pg.evaluate('__xrTiruan.pad("right", 4, 0)'); await tunggu_frame(pg, 2)
    out['vr2: A mengganti tampilan (kokpit -> relai)'] = await pg.evaluate('__gargantua.SHIP.view === "relay"')
    # menu: beda gambar dengan / tanpa panel dibanding beda dua frame tanpa panel (adegan tetap bergerak)
    BEDA = '(a, b) => { let d = 0; for (let k = 0; k < a.length; k += 4) d += Math.abs(a[k] - b[k]) + Math.abs(a[k + 1] - b[k + 1]) + Math.abs(a[k + 2] - b[k + 2]); return d / (a.length / 4); }'
    rows = await pg.evaluate('(VRKIT.drawPanel(), VRKIT.panel.rows.map((r) => r.label()))')   # baris menu selama misi
    await pg.evaluate('__gargantua.stopMission(); __gargantua.state.paused = true'); await tunggu_frame(pg, 3)   # luar misi + jeda: adegan diam
    await pg.evaluate('window.__fa = __xrTiruan.readEye(0).rgba'); await tunggu_frame(pg, 2)
    await pg.evaluate('window.__fb = __xrTiruan.readEye(0).rgba')
    await pg.evaluate('__xrTiruan.pad("left", 4, 1)'); await tunggu_frame(pg, 2); await pg.evaluate('__xrTiruan.pad("left", 4, 0)'); await tunggu_frame(pg, 2)
    d0, d1 = await pg.evaluate(f'(() => {{ const D = {BEDA}, c = __xrTiruan.readEye(0).rgba; return [D(__fa, __fb), D(__fb, c)]; }})()')
    out[f"vr2: X membuka menu VR (beda gambar {d1:.1f} vs antar frame {d0:.1f}), baris {rows[4:7]}"] = await pg.evaluate('VRKIT.menu') and d1 > 3 * d0 + 5 and any('GX-01' in r for r in rows)
    await pg.evaluate('VRKIT.exit()'); await pg.wait_for_timeout(300)
    f1 = await pg.evaluate('__gargantua.state.frame')
    try: await pg.wait_for_function(f'__gargantua.state.frame > {f1} + 1', timeout=30000)   # SwiftShader: frame layar sekitar 1 s
    except Exception: pass
    out['vr2: keluar VR, loop layar jalan lagi, tombol misi VR dilepas'] = await pg.evaluate(f'!__gargantua.GV.on && __gargantua.state.frame > {f1} + 1 && !VRKIT.on && !__gargantua.MIS.keys.size')
    out[f"vr2: tanpa error halaman {pg.errs[:2]}"] = not pg.errs
    await pg.close()

BAGIAN = {'vr0': vr0, 'vr1': vr1, 'vr2': vr2}

async def main():
    pilih = [a for a in sys.argv[1:] if a in BAGIAN] or list(BAGIAN)
    exe = os.environ.get('CHROMIUM')
    out = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'],
                                    **({'executable_path': exe} if exe else {}))
        for k in pilih:
            try: await BAGIAN[k](b, out)
            except Exception as e: out[f'{k}: gagal dijalankan ({str(e)[:200]})'] = False
        await b.close()
    for k, v in out.items(): print(('OK    ' if v else 'GAGAL ') + k)
    sys.exit(0 if all(out.values()) else 1)

asyncio.run(main())
