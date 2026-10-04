"""Uji misi Gargantua (docs/gargantua/rencana-misi-lubang-hitam.md). Bagian per kelompok.
Kelompok 1 (G1):
- aset GX-01 termuat (jumlah verteks = metadata, ada kaca kokpit, kaki dilipat: tidak ada titik di bawah -2,45 m),
- V menyalakan wahana (kamera luar, HUD tampil), V lagi = kokpit, Esc mematikan; tombol panel ada,
- wahana benar-benar tergambar (piksel berbeda dari tanpa wahana di kamera luar), kokpit menampilkan dasbor,
- tampilan lama tidak berubah saat wahana mati (sebelum dan sesudah menyalakan lalu mematikan wahana: piksel sama
  saat waktu dijeda),
- kamus Indonesia lengkap untuk teks baru, tanpa error konsol / WebGL.
Kelompok 2 (G2, kamera jatuh dan misi):
- waktu wajar jatuh lurus 22 rs ke horizon dan ke singularitas vs rumus (2/3)(r0^1,5 - 1) dan (2/3) r0^1,5; dilepas diam vs (pi/2) r0^1,5,
- 7 skenario tanpa dorongan berakhir sesuai rancangan (miring dan berputar lewat celah dalam, nyaris lolos = lolos, tidak ada yang
  menembus piringan), zoom-whirl berputar lebih lama dari miring,
- dorongan mundur 0,02 c di r 6 pada skenario nyaris lolos membuat wahana tertangkap; anggaran delta-v dibatasi,
- di dalam horizon dorongan penuh ke luar tetap tidak bisa membuat dr/dtau >= 0, E tetap > 0,
- faktor langit belakang 1/(1 + beta) = 0,5 tepat di horizon (pengamat rain),
- render kamera jatuh tanpa nilai tidak valid di r 5, 1,0001, 0,5, 0,01 (buffer HDR dibaca), tidak gelap total di dalam horizon,
- tampilan lama identik dengan versi sebelum G2 (commit G1, uFall = 0) saat misi mati,
- alur misi: tombol panel Mulai, X / Z / V berganti, layar akhir muncul, Esc mengakhiri.
Pakai: python tools/uji_misi_gargantua.py   (butuh: pip install playwright; CHROMIUM=<jalur> opsional, default /opt/pw-browsers/chromium
bila ada). Tanpa GPU dipakai SwiftShader."""
import asyncio, os, pathlib, sys
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / 'experiences/gargantua/index.html'
hasil = []
def cek(nama, ok, info=''):
    hasil.append(ok); print(('OK   ' if ok else 'GAGAL') + ' ' + nama + (f'  ({info})' if info else ''))

async def pixels(pg):
    # baca kanvas lewat gambar PNG yang ditangkap, dibandingkan di halaman (tanpa pustaka gambar di Python)
    return await pg.evaluate('''() => new Promise((res) => { window.__gargantua.state.captureCb = (url) => {
      const im = new Image(); im.onload = () => { const c = document.createElement('canvas'); c.width = im.width; c.height = im.height;
        const g = c.getContext('2d'); g.drawImage(im, 0, 0); res(Array.from(g.getImageData(0, 0, im.width, im.height).data)); }; im.src = url; }; })''')

def beda(a, b):
    return sum(1 for i in range(0, len(a), 4) if abs(a[i] - b[i]) + abs(a[i + 1] - b[i + 1]) + abs(a[i + 2] - b[i + 2]) > 6) / (len(a) / 4)

async def main():
    exe = os.environ.get('CHROMIUM') or ('/opt/pw-browsers/chromium' if os.path.exists('/opt/pw-browsers/chromium') else None)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=exe, args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        pg = await b.new_page(viewport={'width': 320, 'height': 200})
        errs = []
        pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
        pg.on('console', lambda m: errs.append(m.type + ': ' + m.text[:200]) if m.type in ('error', 'warning') else None)
        await pg.goto(PAGE.as_uri() + '?lang=id')
        await pg.wait_for_function('window.__gargantua !== undefined', timeout=60000)
        await pg.wait_for_timeout(1500)

        # --- aset ---
        a = await pg.evaluate('''() => { const D = window.__GX01, raw = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));
          const pos = new Int16Array(raw(D.pos).buffer), mat = raw(D.mat); let ymin = 1e9, glass = 0;
          for (let i = 1; i < pos.length; i += 3) ymin = Math.min(ymin, pos[i] * D.scale);
          for (const m of mat) glass += m;
          return { n: D.n, np: pos.length / 3, nm: mat.length, ymin, glass, name: D.name, ready: window.__gargantua.SHIP.ready }; }''')
        cek('aset GX-01 termuat dan siap', a['ready'] and a['name'] == 'GX-01', f"nama {a['name']}")
        cek('jumlah verteks = metadata', a['n'] == a['np'] == a['nm'] and a['n'] % 3 == 0, f"{a['n']} verteks, {a['n'] // 3} segitiga")
        cek('kaca kokpit ada', a['glass'] > 0, f"{a['glass']} verteks kaca")
        cek('kaki pendarat dilipat (tidak ada titik di bawah -2,45 m)', a['ymin'] >= -2.451, f"y min {a['ymin']:.3f} m")

        # --- tampilan lama tetap: jeda waktu, tangkap, nyalakan lalu matikan wahana, tangkap lagi ---
        await pg.evaluate('() => { const G = window.__gargantua; G.state.paused = true; G.state.postMode = 2; G.CONFIG.adaptive = false; }')
        await pg.wait_for_timeout(500)
        px0 = await pixels(pg)
        await pg.keyboard.press('KeyV')
        await pg.wait_for_timeout(800)
        on = await pg.evaluate('() => ({ on: window.__gargantua.SHIP.on, view: window.__gargantua.SHIP.view, dash: document.getElementById("dash").hidden })')
        cek('V = wahana menyala, kamera luar, HUD tampil', on['on'] and on['view'] == 'chase' and not on['dash'], str(on))
        px1 = await pixels(pg)
        d1 = beda(px0, px1)
        cek('wahana tergambar di kamera luar', d1 > 0.01, f'{d1 * 100:.1f}% piksel berbeda')
        await pg.keyboard.press('KeyV')
        await pg.wait_for_timeout(800)
        ck = await pg.evaluate('() => ({ view: window.__gargantua.SHIP.view, dash: document.getElementById("dash").hidden, dw: document.getElementById("dash").width })')
        cek('V lagi = kokpit dengan dasbor', ck['view'] == 'cockpit' and not ck['dash'] and ck['dw'] > 0, str(ck))
        px2 = await pixels(pg)
        cek('kokpit berbeda dari kamera luar', beda(px1, px2) > 0.01)
        await pg.keyboard.press('Escape')
        await pg.wait_for_timeout(800)
        off = await pg.evaluate('() => ({ on: window.__gargantua.SHIP.on, dash: document.getElementById("dash").hidden })')
        cek('Esc = wahana mati, dasbor hilang', not off['on'] and off['dash'], str(off))
        px3 = await pixels(pg)
        d3 = beda(px0, px3)
        cek('tampilan lama sama setelah wahana dimatikan', d3 == 0, f'{d3 * 100:.3f}% piksel berbeda')

        # --- panel dan kamus ---
        btn = await pg.evaluate('() => [...document.querySelectorAll("#uiBody button")].some((b) => b.textContent.includes("Wahana GX-01"))')
        cek('tombol panel "Wahana GX-01" ada (bahasa Indonesia)', btn)
        src = PAGE.read_text(encoding='utf-8')
        kunci = ['GX-01 vessel', 'Vessel GX-01: chase camera (V cockpit, Esc exit)', 'Vessel GX-01: cockpit (V chase camera, Esc exit)',
                 'Vessel GX-01: off', 'Vessel GX-01 model is missing (assets/gx01.data.js)', 'Vessel view: GX-01 chase camera / cockpit (Esc exits)',
                 'Distance to centre', 'View', 'Cockpit']
        hilang = [k for k in kunci if f"'{k}':" not in src]
        cek('kamus ID lengkap untuk teks G1', not hilang, ', '.join(hilang) or f'{len(kunci)} kunci')
        await kelompok2(p, exe, pg)

        cek('tanpa error konsol / WebGL', not errs, '; '.join(errs[:3]))
        await b.close()
    print(f'\n{sum(hasil)}/{len(hasil)} lulus')
    sys.exit(0 if all(hasil) else 1)

async def kelompok2(p, exe, pg):
    import re
    G = 'window.__gargantua'
    # --- fisika tanpa render: integrasi langsung ---
    sim = await pg.evaluate('''() => { const G = window.__gargantua, out = {};
      G.state.paused = true;
      for (const id of Object.keys(G.SCEN)) {
        G.startMission(id);
        const st = { x: G.MIS.x.slice(), xd: G.MIS.xd.slice(), tau: 0, tauH: null }; st.onHorizon = (t) => { st.tauH = t; };
        let r = null; for (let n = 0; !r && n < 40000 && st.tau < 5000; n++) r = G.misAdvance(st, 0.5, 4000);
        out[id] = { end: r ? r.kind : 'none', tau: st.tau, tauH: st.tauH };
      }
      G.stopMission(); return out; }''')
    pol, drip = sim['polar'], sim['drip']
    aH, aS, aD = 2 / 3 * (22 ** 1.5 - 1), 2 / 3 * 22 ** 1.5 - 2 / 3 * 0.006 ** 1.5, None
    cek('jatuh lurus: waktu wajar 22 rs -> horizon = (2/3)(22^1,5 - 1)', abs(pol['tauH'] - aH) < 2e-3, f"{pol['tauH']:.4f} vs {aH:.4f} rs/c ({pol['tauH'] * 985.27 / 3600:.3f} jam)")
    cek('jatuh lurus: horizon -> r 0,006 = (2/3)(1 - 0,006^1,5) rs/c', abs((pol['tau'] - pol['tauH']) - (2 / 3) * (1 - 0.006 ** 1.5)) < 2e-3, f"{(pol['tau'] - pol['tauH']) * 985.27:.1f} s")
    import math
    aDrip = math.pi / 2 * 22 ** 1.5
    cek('dilepas diam: waktu ke singularitas = (pi/2) 22^1,5', abs(drip['tau'] - aDrip) < 0.01, f"{drip['tau']:.4f} vs {aDrip:.4f} rs/c")
    harap = {'polar': 'singularity', 'drip': 'singularity', 'fast': 'singularity', 'slant': 'singularity', 'whirl': 'singularity', 'near': 'escape', 'unstable': 'singularity'}
    salah = {k: v['end'] for k, v in sim.items() if v['end'] != harap[k]}
    cek('7 skenario tanpa dorongan berakhir sesuai rancangan (tidak ada yang menembus piringan)', not salah, str(salah) if salah else ', '.join(f"{k} {v['end']}" for k, v in sim.items()))
    cek('zoom-whirl lebih lama dari miring (berputar di 2 rs)', sim['whirl']['tau'] > sim['slant']['tau'] + 20, f"{sim['whirl']['tau']:.1f} vs {sim['slant']['tau']:.1f} rs/c")

    # --- kendali terbatas ---
    k = await pg.evaluate('''() => { const G = window.__gargantua, M = G.MIS, v3n = (a) => Math.hypot(...a);
      G.startMission('near');
      const st = { x: M.x, xd: M.xd, tau: 0 };
      while (v3n(st.x) > 6) G.misAdvance(st, 0.05);
      M.x = st.x; M.xd = st.xd; M.tau = st.tau;
      // dorongan mundur: lawan arah gerak menyamping, 0,02 c dalam langkah kecil (rem di r 3 terlambat: orbit terikat menembus piringan)
      const rh = M.x.map((c) => c / v3n(M.x)); let used = 0;
      for (let i = 0; i < 40; i++) { const t = M.xd.map((c, j) => c - rh[j] * (M.xd[0] * rh[0] + M.xd[1] * rh[1] + M.xd[2] * rh[2])), tl = v3n(t); used += G.misThrust(t.map((c) => -c / tl * 0.0005)); }
      const s2 = { x: M.x.slice(), xd: M.xd.slice(), tau: M.tau }; let r = null; for (let n = 0; !r && n < 20000; n++) r = G.misAdvance(s2, 0.5);
      // anggaran: stepMission tidak melampaui dvMax
      G.startMission('polar'); M.dvUsed = M.dvMax - 0.001; M.keys.add('KeyW'); M.keys.add('ShiftLeft'); G.state.paused = false;
      for (let i = 0; i < 30; i++) { M.predT = 1; }
      return { end: r && r.kind, used }; }''')
    await pg.wait_for_timeout(1500)
    bud = await pg.evaluate('() => { const M = window.__gargantua.MIS; M.keys.clear(); window.__gargantua.state.paused = true; return { used: M.dvUsed, max: M.dvMax }; }')
    cek('nyaris lolos + dorongan mundur 0,02 c di r 6 -> tertangkap', k['end'] == 'singularity', f"akhir {k['end']}, delta-v {k['used']:.4f} c")
    cek('anggaran delta-v tidak terlampaui', bud['used'] <= bud['max'] + 1e-9, f"{bud['used']:.5f} / {bud['max']} c")
    ins = await pg.evaluate('''() => { const G = window.__gargantua, M = G.MIS, n = (a) => Math.hypot(...a);
      G.startMission('polar'); const st = { x: M.x, xd: M.xd, tau: 0 }; while (n(st.x) > 0.5) G.misAdvance(st, 0.02); M.x = st.x; M.xd = st.xd;
      let urMax = -1e9, Emin = 1e9;
      for (let i = 0; i < 200; i++) { const rh = M.x.map((c) => c / n(M.x)); G.misThrust(rh.map((c) => c * 0.004));
        const R = G.rainOf(M.x, M.xd); urMax = Math.max(urMax, R.ur); Emin = Math.min(Emin, R.E); }
      const Rh = G.rainOf([0, 1, 0], [0, -1, 0]); const back = G.skyShift(Rh, [0, 1, 0]);
      return { urMax, Emin, back }; }''')
    cek('di dalam horizon dorongan penuh ke luar: dr/dtau tetap < 0', ins['urMax'] < 0, f"dr/dtau maks {ins['urMax']:.4f}")
    cek('E tetap > 0 setelah dorongan', ins['Emin'] > 0.005, f"E min {ins['Emin']:.4f}")
    cek('langit belakang di horizon (rain) = 1/(1 + beta) = 0,5', abs(ins['back'] - 0.5) < 1e-9, f"{ins['back']:.6f}")

    # --- render: tanpa nilai tidak valid ---
    await pg.evaluate('() => { const G = window.__gargantua; G.stopMission(); G.CONFIG.adaptive = false; G.state.paused = true; }')
    for rT, view, lock in [(5, 'chase', 'centre'), (1.0001, 'cockpit', 'level'), (0.5, 'chase', 'level'), (0.01, 'cockpit', 'level')]:
        await pg.evaluate('''([rT, view, lock]) => { const G = window.__gargantua, M = G.MIS; M.lock = lock; G.startMission('slant'); G.SHIP.view = view;
          const st = { x: M.x, xd: M.xd, tau: 0 }; while (Math.hypot(...st.x) > rT) { if (G.misAdvance(st, Math.min(0.02, 0.01 * Math.hypot(...st.x) ** 1.5))) break; }
          M.x = st.x; M.xd = st.xd; M.tau = st.tau; G.state.paused = true; }''', [rT, view, lock])
        await pg.wait_for_timeout(600)
        st = await pg.evaluate('() => new Promise((r) => { window.__gargantua.state.readCb = r; })')
        cek(f'render r {rT} ({view}, {lock}) tanpa nilai tidak valid', st['bad'] == 0 and st['max'] < 1e4, f"tidak valid {st['bad']}, maks {st['max']:.1f}, rata {st['mean']:.3f}")
        if rT < 1:
            cek(f'r {rT}: tidak gelap total (langit / piringan terlihat dari dalam horizon)', st['mean'] > 1e-3, f"rata {st['mean']:.4f}")

    # --- tampilan lama identik dengan versi sebelum G2 ---
    import subprocess, tempfile
    g1 = subprocess.run(['git', 'log', '--format=%H', '-1', '--grep=kelompok 1 (G1)'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    old = subprocess.run(['git', 'show', f'{g1}:experiences/gargantua/index.html'], cwd=ROOT, capture_output=True, text=True).stdout if g1 else ''
    if not old or 'uFall' in old:
        cek('pembanding versi sebelum G2 (commit G1) tersedia', False, 'commit G1 tidak ditemukan di riwayat git')
    else:
        tmp = pathlib.Path(tempfile.mkdtemp()) / 'lama.html'; tmp.write_text(old, encoding='utf-8')
        setup = '() => { const G = window.__gargantua; G.state.paused = true; G.state.simTime = 7.5; G.state.postMode = 2; G.CONFIG.adaptive = false; G.CONFIG.renderScale = 0.8; }'
        await pg.evaluate('() => { window.__gargantua.stopMission(); }')
        await pg.evaluate(setup); await pg.wait_for_timeout(500); baru = await pixels(pg)
        pg2 = await (await pg.context.browser.new_context(viewport={'width': 320, 'height': 200})).new_page()
        await pg2.goto(tmp.as_uri() + '?lang=id'); await pg2.wait_for_function('window.__gargantua !== undefined'); await pg2.wait_for_timeout(1000)
        await pg2.evaluate(setup); await pg2.wait_for_timeout(500); lama = await pixels(pg2)
        d = beda(baru, lama)
        cek('misi mati: render identik dengan versi sebelum G2 (uFall = 0)', d == 0, f'{d * 100:.3f}% piksel berbeda')

    # --- alur misi lewat UI ---
    await pg.evaluate("() => { const s = [...document.querySelectorAll('#uiBody select')].find((x) => [...x.options].some((o) => o.value === 'fast')); s.value = 'fast'; s.dispatchEvent(new Event('change')); }")
    await pg.evaluate("() => [...document.querySelectorAll('#uiBody button')].find((b) => b.textContent === 'Mulai misi').click()")
    a = await pg.evaluate('() => ({ on: window.__gargantua.MIS.on, sc: window.__gargantua.MIS.sc, lock: window.__gargantua.MIS.lock, dash: document.getElementById("dash").hidden })')
    cek('panel: pilih skenario + Mulai misi', a['on'] and a['sc'] == 'fast' and not a['dash'], str(a))
    await pg.keyboard.press('KeyX'); await pg.keyboard.press('KeyZ'); await pg.keyboard.press('KeyV')
    b2 = await pg.evaluate('() => ({ lock: window.__gargantua.MIS.lock, warp: window.__gargantua.MIS.warp, view: window.__gargantua.SHIP.view })')
    cek('X ganti sikap, Z ganti waktu, V ganti tampilan', b2['lock'] != a['lock'] and b2['warp'] == 1, str(b2))
    await pg.evaluate('() => { const G = window.__gargantua; G.MIS.warp = 2; G.state.paused = false; }')
    await pg.wait_for_function('!document.getElementById("mend").hidden', timeout=90000)
    e = await pg.evaluate('() => ({ title: document.getElementById("mendTitle").textContent, body: document.getElementById("mendBody").textContent, kind: window.__gargantua.MIS.end && window.__gargantua.MIS.end.kind })')
    cek('misi berakhir di singularitas dengan layar ringkasan', e['kind'] == 'singularity' and 'horizon' in e['body'], e['title'])
    await pg.keyboard.press('Escape')
    f = await pg.evaluate('() => ({ on: window.__gargantua.MIS.on, mend: document.getElementById("mend").hidden, ship: window.__gargantua.SHIP.on })')
    cek('Esc mengakhiri misi', not f['on'] and f['mend'] and not f['ship'], str(f))

    # --- kamus ---
    src = PAGE.read_text(encoding='utf-8')
    idb = src[src.index('const ID = {'):src.index('const txt =')]
    keys = set(re.findall(r"txt\('((?:[^'\\]|\\.)*)'\)", src))
    i0, i1 = src.index('const SCEN = {'), src.index('const MIS = {')
    keys |= set(re.findall(r"(?:name|info): '((?:[^'\\]|\\.)*)'", src[i0:i1]))
    keys |= set(re.findall(r"(?:label|sec): '((?:[^'\\]|\\.)*)'", src))
    keys |= {'Start mission', 'End mission (Esc)', 'Torn apart by tides near the singularity', 'Destroyed in the accretion disk', 'Escaped: thrown back out',
             'Nose to the centre', 'Nose level: looking along the sky band', 'Free attitude (drag)'}
    hilang = sorted(k for k in keys if f"'{k}':" not in idb and k not in ('GX-01', 'RGBA16F', 'RGBA8 (fallback)', 'Q', 'Esc'))
    cek('kamus ID lengkap (semua txt(), skenario, label)', not hilang, '; '.join(hilang[:6]) or f'{len(keys)} kunci')

asyncio.run(main())
