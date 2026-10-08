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
Kelompok 3 (G3, susur piringan, lempeng tebal, partikel):
- autopilot susur (melawan dan searah arus) sampai ISCO tanpa menembus piringan, tinggi terjaga, delta-v di bawah anggaran,
  dilepas di dalam ISCO lalu berakhir di singularitas; tanpa autopilot / delta-v habis = menabrak piringan,
- kecepatan gas relatif: orbit melingkar melawan arus di r 6 = 2v/(1 + v^2) = 0,575 c, di r 3 = 0,8 c, searah arus = 0,
- render dekat piringan (kokpit dan kamera luar) tanpa nilai tidak valid (lempeng tebal G3a dihapus),
- garis bara tergambar dekat piringan dan tidak ada di jalur kutub, tumbukan kaca terjadi (kokpit), kaca pecah = akhir misi,
- eksposur otomatis hanya saat misi (k = 1 di luar misi), menggelap di atas piringan terang,
- kamus ID untuk teks baru.
Kelompok 4 (G4, informasi tidak bisa keluar) + kamera luar mengitari wahana:
- waktu bersama T (Painleve-Gullstrand) = waktu wajar untuk jatuh lurus E = 1, waktu tiba sinyal di relai = integrasi numerik
  sinar radial keluar dan masuk, laju jam terlihat relai di awal = rumus Doppler + dilatasi relai,
- relai melihat jam wahana membeku tepat di waktu lewat horizon, laju turun dengan faktor e tiap 2 rs/c (gravitasi permukaan),
  pulsa dari dalam horizon tidak pernah tiba, semua pulsa dari luar akhirnya tiba,
- suar keluar dari dalam horizon tetap turun sampai r = 0, suar dari luar tiba di relai, pesan relai tetap sampai ke wahana di dalam horizon,
- jendela relai dan diagram tergambar (M), E menembak suar, layar akhir memuat pulsa dan jendela relai hidup,
- seret di kamera luar memutar kamera mengitari wahana tanpa mengubah sikap, seret kanan / kokpit = arah hidung, klik ganda kembali.
Kelompok 5 (G5, sudut masuk tesseract, fiksi):
- sudut tangkap kritis 24,62 derajat = asin(2 sqrt(21) / 22), integrator: sedikit di bawah kritis tertangkap, sedikit di atas lolos,
- zoom-whirl: sapuan sudut bertambah ln(10) / sqrt(1/2) = 186,6 derajat tiap delta 10 kali lebih kecil (eksponen ketidakstabilan orbit 2 rs),
- bidang orbit menentukan: bidang 90 derajat menembus piringan, bidang gerbang ada bidikan tepat sasaran,
- membidik: waktu beku, W/S mengubah delta, A/D bidang, Enter mengunci; terbang mengikuti lintasan acuan = prakiraan, berakhir di gerbang
  (arah dalam toleransi 5 derajat), meleset = lanjut ke singularitas, adegan tesseract lalu kartu akhir, Esc keluar.
Kelompok 7 (G7, suara disintesis):
- campuran audioMix(): gemuruh piringan dekat piringan (lebih terang melawan arus), nol di jalur kutub, nada pasang surut hanya di dalam
  horizon, pendorong saat W/S (tidak saat membidik), akord tesseract; AudioContext dibuat setelah tombol, U bisu / nyala + localStorage, panel.
Kelompok 8 (G8, peta corong dan arah partikel susur searah arus; docs/gargantua/rumus-peta-corong.md):
- z(r) = 2 sqrt(r) dan l(r) = sqrt(r (r + 1)) + asinh(sqrt r) = integral sqrt(1 + 1/r) dr (irisan Eddington-Finkelstein),
- riwayat dan prakiraan menyimpan posisi, peta corong tergambar untuk semua skenario tanpa error, tesseract: peta orbit saat membidik,
  corong setelah Enter (HUD hidup),
- susur searah arus: titik pancar partikel = arah tampak pusat lubang hitam (dicek lewat rumus aberasi shader, arah sebaliknya),
  melawan arus: arah gas relatif tidak berubah.
Kelompok 9 (G9, pandangan relai 22 rs; docs/gargantua/rumus-pandangan-relai.md):
- V di misi: kamera luar -> kokpit -> relai -> kamera luar; kamera relai di |pos| = 22 tanpa wahana (eye null),
- citra lensa: sinar shader dari arah hasil (balik aberasi diperiksa dengan rumus shader) melewati titik pancar (< 1e-4 rs),
  titik segaris relai-pusat = arah ke pusat; titik di balik piringan ditandai,
- render pandangan relai tanpa nilai tidak valid, titik wahana tergambar,
- suar dari 10 rs diterima relai saat waktu relai >= waktu tiba; suar dari dalam horizon tidak pernah diterima.
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
    harap = {'polar': 'singularity', 'drip': 'singularity', 'fast': 'singularity', 'slant': 'singularity', 'whirl': 'singularity', 'near': 'escape', 'unstable': 'singularity',
             'skim': 'disk', 'skimPro': 'disk', 'tesseract': 'singularity'}   # G5: bidikan awal (bidang 0, delta 1e-2) lewat celah dalam   # G3: susur tanpa autopilot (geodesik murni) = menembus piringan
    salah = {k: v['end'] for k, v in sim.items() if v['end'] != harap.get(k)}
    cek('10 skenario tanpa dorongan berakhir sesuai rancangan (7 skenario G2 dan bidikan awal tesseract tidak menembus piringan, susur tanpa autopilot menembus)', not salah, str(salah) if salah else ', '.join(f"{k} {v['end']}" for k, v in sim.items()))
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
             'Nose to the centre', 'Nose level: looking along the sky band', 'Free attitude (drag)',
             'Nose along the track, disk below (drag = look)', 'Canopy shattered by disk dust', 'Autopilot skim (O)',
             'Lock aim and go (Enter)', 'Entered the tesseract (fiction)'}
    keys |= set(re.findall(r"apOff\('((?:[^'\\]|\\.)*)'\)", src)) | set(re.findall(r"text: '((?:[^'\\]|\\.)*)'", src))
    hilang = sorted(k for k in keys if f"'{k}':" not in idb and k not in ('GX-01', 'RGBA16F', 'RGBA8 (fallback)', 'Q', 'Esc'))
    cek('kamus ID lengkap (semua txt(), skenario, label)', not hilang, '; '.join(hilang[:6]) or f'{len(keys)} kunci')
    await kelompok3(pg)

async def kelompok3(pg):
    # --- fisika susur: autopilot sampai ISCO ---
    sim = await pg.evaluate('''() => { const G = window.__gargantua, M = G.MIS, out = {}; G.state.paused = true;
      for (const sc of ['skim', 'skimPro']) {
        G.startMission(sc); let res = null, hErr = 0, rRel = null, n = 0;
        while (!res && n++ < 20000) {
          res = G.misFly(0.1); const rxz = Math.hypot(M.x[0], M.x[2]);
          if (M.ap.on && rxz > 4 && rxz < 12) hErr = Math.max(hErr, Math.abs(M.x[1] / rxz - M.ap.h));
          if (rRel === null && !M.ap.on) rRel = Math.hypot(...M.x);
        }
        out[sc] = { end: res && res.kind, tau: M.tau, dv: M.dvUsed, dvMax: M.dvMax, hErr, rRel };
      }
      G.startMission('skim'); G.toggleAP(); let r1 = null; for (let i = 0; !r1 && i < 20000; i++) r1 = G.misFly(0.1);
      G.startMission('skim'); for (let i = 0; i < 300; i++) G.misFly(0.1); M.dvUsed = M.dvMax - 1e-4;
      let r2 = null; for (let i = 0; !r2 && i < 20000; i++) r2 = G.misFly(0.1);
      out.off = r1 && r1.kind; out.empty = r2 && r2.kind; G.stopMission(); return out; }''')
    for sc, nama in (('skim', 'melawan arus'), ('skimPro', 'searah arus')):
        v = sim[sc]
        cek(f'susur {nama}: autopilot sampai ISCO tanpa menembus piringan, lalu singularitas', v['end'] == 'singularity' and v['rRel'] is not None and v['rRel'] < 3.05,
            f"akhir {v['end']}, dilepas di r {v['rRel']:.3f}, waktu wajar {v['tau']:.1f} rs/c ({v['tau'] * 985.27 / 3600:.1f} jam)")
        cek(f'susur {nama}: tinggi terjaga dan delta-v di bawah anggaran', v['hErr'] < 0.005 and v['dv'] < v['dvMax'],
            f"galat tinggi maks {v['hErr']:.4f} r, delta-v {v['dv']:.4f} / {v['dvMax']} c")
    cek('susur tanpa autopilot (O) menabrak piringan', sim['off'] == 'disk', str(sim['off']))
    cek('susur dengan delta-v habis: autopilot lepas, menabrak piringan', sim['empty'] == 'disk', str(sim['empty']))

    # --- kecepatan gas relatif ---
    g = await pg.evaluate('''() => { const G = window.__gargantua, out = {};
      for (const [k, r, dir] of [['retro6', 6, -1], ['pro6', 6, 1], ['retro3', 3.0001, -1]]) {
        const x = [r, 0, 0], xd = [0, 0, dir * Math.sqrt(0.5 / (r - 1.5))]; out[k] = G.gasRel(x, xd).v; }
      return out; }''')
    import math
    v6 = math.sqrt(0.5 / 5); a6 = 2 * v6 / (1 + v6 * v6)
    cek('gas relatif melawan arus r 6 = 2v/(1 + v^2)', abs(g['retro6'] - a6) < 1e-6, f"{g['retro6']:.6f} vs {a6:.6f} c")
    cek('gas relatif melawan arus r 3 (ISCO) = 0,8 c', abs(g['retro3'] - 0.8) < 1e-3, f"{g['retro3']:.5f} c")
    cek('gas relatif searah arus = 0', g['pro6'] < 1e-6, f"{g['pro6']:.2e} c")

    # --- render dekat piringan (lempeng tebal G3a dihapus), partikel, tumbukan ---
    await pg.evaluate('() => { const G = window.__gargantua; G.CONFIG.adaptive = false; G.state.postMode = 0; }')
    for rT, view, h in [(6, 'chase', 0.05), (6, 'cockpit', 0.05), (3.5, 'cockpit', 0.05), (8, 'chase', 0.01)]:
        await pg.evaluate('''([rT, view, h]) => { const G = window.__gargantua, M = G.MIS; G.startMission('skim'); G.SHIP.view = view; M.ap.h = h;
          G.state.paused = true; while (Math.hypot(...M.x) > rT) if (G.misFly(0.1)) break; G.state.paused = false; M.warp = 3; }''', [rT, view, h])
        await pg.wait_for_timeout(1500)
        st = await pg.evaluate('() => new Promise((r) => { window.__gargantua.state.readCb = r; })')
        info = await pg.evaluate('() => { const G = window.__gargantua, M = G.MIS; return { parts: G.state.partsDrawn, hits: M.hits, imps: M.imps.length }; }')
        cek(f'dekat piringan r {rT} tinggi {h} r ({view}) tanpa nilai tidak valid', st['bad'] == 0 and st['max'] < 1e4,
            f"tidak valid {st['bad']}, maks {st['max']:.1f}, rata {st['mean']:.3f}")
        if view == 'cockpit' and rT == 6:
            cek('garis bara tergambar dan debu menabrak kaca (kokpit, dekat piringan)', info['parts'] > 0 and info['hits'] > 0 and info['imps'] > 0, str(info))
    await pg.evaluate('''() => { const G = window.__gargantua, M = G.MIS; G.startMission('polar'); G.state.paused = true;
      while (Math.hypot(...M.x) > 15) G.misAdvance(M, 0.1); G.state.paused = false; }''')
    await pg.wait_for_timeout(1500)
    pol = await pg.evaluate('() => { const G = window.__gargantua, M = G.MIS; return { parts: G.state.partsDrawn, hits: M.hits, k: G.AE.k }; }')
    cek('jalur kutub: tanpa garis bara dan tumbukan', not pol['parts'] and pol['hits'] == 0, str(pol))
    await pg.evaluate("() => { const G = window.__gargantua, M = G.MIS; G.startMission('skim'); G.state.paused = false; M.glass = 99.999; M.hitAcc = 5; }")
    await pg.wait_for_function('window.__gargantua.MIS.end !== null', timeout=30000)
    e = await pg.evaluate('() => ({ kind: window.__gargantua.MIS.end.kind, title: document.getElementById("mendTitle").textContent })')
    cek('kaca rusak 100% = akhir misi (kaca pecah)', e['kind'] == 'glass', e['title'])

    # --- eksposur otomatis ---
    await pg.evaluate('''() => { const G = window.__gargantua, M = G.MIS; G.startMission('skim'); G.SHIP.view = 'chase'; G.state.paused = true;
      while (Math.hypot(...M.x) > 4) G.misFly(0.1); G.state.paused = false; M.warp = 3; }''')
    await pg.wait_for_function('window.__gargantua.AE.L !== null && window.__gargantua.AE.kt < 1', timeout=60000)
    await pg.wait_for_timeout(2500)          # ukuran pertama bisa dari frame sebelum wahana dipindah: tunggu beberapa ukuran lagi
    ae = await pg.evaluate('''() => { const G = window.__gargantua, A = G.AE, M = G.MIS; return { kt: A.kt, L: A.L, r: Math.hypot(...M.x), end: M.end && M.end.kind,
      view: G.SHIP.view, sc: G.CONFIG.renderScale, q: G.CONFIG.quality, paused: G.state.paused, post: G.state.postMode, orb: M.orb, lock: M.lock }; }''')
    cek('eksposur otomatis menggelap di atas piringan terang', ae['kt'] < 0.8, f"k sasaran {ae['kt']:.3f}, terang {ae['L']:.2f}" + ('' if ae['kt'] < 0.8 else f' {ae}'))
    await pg.evaluate('() => window.__gargantua.stopMission()')
    await pg.wait_for_timeout(400)
    k = await pg.evaluate('() => window.__gargantua.AE.k')
    cek('di luar misi eksposur tidak diubah (k = 1)', k == 1, str(k))
    await kelompok4(pg)

def simpson(f, a, b, n=20000):
    h = (b - a) / n
    return h / 3 * (f(a) + f(b) + sum((4 if i % 2 else 2) * f(a + i * h) for i in range(1, n)))

async def kelompok4(pg):
    import math
    # --- jatuh lurus E = 1: T = waktu wajar; relai melihat jam membeku di waktu lewat horizon ---
    s = await pg.evaluate('''() => { const G = window.__gargantua, M = G.MIS; G.state.paused = true; G.startMission('polar');
      let res = null, dT = 0; while (!res) { res = G.misFly(0.05, (t) => { M.tauH = t; }); dT = Math.max(dT, Math.abs(M.T - M.tau)); }
      const out = { end: res.kind, dT, tauH: M.tauH, k: G.REL.k };
      const a = G.relSeen(40); out.early = { r: a.r, rate: a.rate, tau: a.tau };
      const r1 = G.relSeen(120), r2 = G.relSeen(122); out.ratio = r2.rate / r1.rate; out.seen200 = G.relSeen(200).tau;
      const V = G.relView(); G.REL.Tx = 1e4; const V2 = G.relView(); G.REL.Tx = 0;
      out.sent = V.sent; out.never = V.never; out.recvLate = V2.recv; out.inf = G.relArrive(50, 0.999);
      const m1 = []; for (const r of [0.9, 0.5, 0.1, 0.01]) { M.x = [0, r, 0]; M.xd = [0, -Math.sqrt(1 / r), 0]; M.T = 68.13 + (2 / 3) * (1 - r ** 1.5); m1.push(G.relMsg()); }
      out.msg = m1; G.stopMission(); return out; }''')
    cek('jatuh lurus E = 1: waktu bersama T sama dengan waktu wajar', s['dT'] < 1e-9, f"selisih maks {s['dT']:.1e} rs/c")
    rs_, k = s['early']['r'], s['k']
    an = (math.sqrt(rs_) - 1) / (math.sqrt(rs_) * k)
    cek('laju jam wahana terlihat relai = Doppler x dilatasi relai (sqrt r - 1) / (sqrt r k)', abs(s['early']['rate'] - an) < 2e-4,
        f"r {rs_:.3f}: {s['early']['rate']:.5f} vs {an:.5f}")
    cek('relai melihat jam wahana membeku tepat di waktu lewat horizon', abs(s['seen200'] - s['tauH']) < 1e-6,
        f"{s['seen200']:.8f} vs {s['tauH']:.8f} rs/c ({s['tauH'] * 985.27 / 3600:.3f} jam)")
    cek('laju jam terlihat turun faktor e tiap 2 rs/c waktu relai (gravitasi permukaan 1/2)', abs(s['ratio'] - math.exp(-1)) < 2e-3,
        f"{s['ratio']:.5f} vs {math.exp(-1):.5f}")
    cek('pulsa dari dalam horizon tidak pernah tiba, semua pulsa dari luar akhirnya tiba',
        s['inf'] == float('inf') and s['never'] > 600 and s['sent'] - s['never'] - s['recvLate'] <= 1,
        f"terkirim {s['sent']}, dari dalam {s['never']}, tiba di akhir {s['recvLate']}")
    clk = [m['clock'] for m in s['msg']]
    cek('pesan relai tetap sampai ke wahana di dalam horizon (jam relai terlihat naik, laju > 0)',
        all(b > a for a, b in zip(clk, clk[1:])) and all(m['rate'] > 0 for m in s['msg']), ', '.join(f"{c:.3f}" for c in clk))

    # --- waktu tiba vs integrasi numerik sinar radial (koordinat Painleve-Gullstrand) ---
    t = await pg.evaluate('() => { const G = window.__gargantua; return [1.01, 1.5, 3, 10, 40].map((r) => G.relArrive(0, r)); }')
    num = []
    for r in (1.01, 1.5, 3, 10):          # keluar: dT/dr = 1 / (1 - 1/sqrt r), r = 1 + e^x
        num.append(simpson(lambda x: math.exp(x) / (1 - 1 / math.sqrt(1 + math.exp(x))), math.log(r - 1), math.log(21)))
    num.append(simpson(lambda r: 1 / (1 + 1 / math.sqrt(r)), 22, 40))   # masuk dari 40 rs
    err = max(abs(a - b) for a, b in zip(t, num))
    cek('waktu tiba di relai = integrasi numerik sinar radial keluar / masuk', err < 1e-6, f"galat maks {err:.1e} rs/c, dari 1,01 rs {t[0]:.4f} rs/c")

    # --- suar ---
    f = await pg.evaluate('''() => { const G = window.__gargantua, M = G.MIS; G.state.paused = true; G.startMission('polar');
      M.x = [0, 0.5, 0]; M.xd = [0, -Math.sqrt(2), 0]; M.T = 70; G.fireFlare(); const F = G.REL.flares[0], rs = [];
      for (let i = 0; i <= 10; i++) rs.push(G.flareAt(F, 70 + i * 0.05).r);
      const hit = G.flareAt(F, F.C + 1e-9).hit;
      M.x = [0, 3, 0]; M.T = 10; G.fireFlare(); const F2 = G.REL.flares[1], at = G.flareAt(F2, F2.arr).r;
      G.stopMission(); return { rs, hit, at }; }''')
    mono = all(b < a for a, b in zip(f['rs'], f['rs'][1:]))
    cek('suar ditembak keluar dari dalam horizon (r 0,5) tetap turun dan sampai r = 0', mono and f['hit'], ', '.join(f"{v:.3f}" for v in f['rs'][:4]) + ' ...')
    cek('suar dari luar horizon (r 3) naik dan tiba di relai 22 rs', abs(f['at'] - 22) < 1e-6, f"r {f['at']:.6f}")

    # --- kamera luar mengitari wahana (seret), seret kanan / kokpit = arah hidung ---
    c = await pg.evaluate('''() => { const G = window.__gargantua, M = G.MIS; G.startMission('polar'); G.state.paused = true; G.SHIP.view = 'chase';
      return { eye: G.chaseEye(), chase: M.chase, f: M.att.f.slice() }; }''')
    cek('kamera luar tanpa putaran = posisi lama (0, 0,19 d, d)', abs(c['eye'][0]) < 1e-9 and abs(c['eye'][1] - 0.19 * c['chase']) < 1e-9 and abs(c['eye'][2] - c['chase']) < 1e-9, str([round(v, 4) for v in c['eye']]))
    await pg.mouse.move(160, 100); await pg.mouse.down(); await pg.mouse.move(220, 80, steps=4); await pg.mouse.up()
    d1 = await pg.evaluate('() => { const M = window.__gargantua.MIS; return { orb: M.orb, f: M.att.f, lock: M.lock }; }')
    same = max(abs(a - b) for a, b in zip(d1['f'], c['f'])) < 1e-9
    cek('seret di kamera luar = kamera mengitari wahana, sikap wahana tetap', abs(d1['orb']['yaw']) > 0.1 and same and d1['lock'] == 'centre', str(d1['orb']))
    await pg.mouse.move(160, 100); await pg.mouse.down(button='right'); await pg.mouse.move(200, 100, steps=4); await pg.mouse.up(button='right')
    d2 = await pg.evaluate('() => { const M = window.__gargantua.MIS; return { f: M.att.f, lock: M.lock }; }')
    cek('seret kanan = arah hidung (sikap bebas)', d2['lock'] == 'free' and max(abs(a - b) for a, b in zip(d2['f'], c['f'])) > 0.01, d2['lock'])
    await pg.mouse.dblclick(160, 100)
    d3 = await pg.evaluate('() => window.__gargantua.MIS.orb')
    await pg.evaluate("() => { const G = window.__gargantua; G.SHIP.view = 'cockpit'; G.MIS.lock = 'centre'; G.misData(); }")
    await pg.mouse.move(160, 100); await pg.mouse.down(); await pg.mouse.move(200, 100, steps=4); await pg.mouse.up()
    d4 = await pg.evaluate('() => ({ lock: window.__gargantua.MIS.lock, orb: window.__gargantua.MIS.orb })')
    cek('klik ganda = kamera kembali; di kokpit seret tetap arah hidung', d3['yaw'] == 0 and d3['pitch'] == 0 and d4['lock'] == 'free' and d4['orb']['yaw'] == 0, f"{d3} {d4}")

    # --- jendela relai, suar (E), M, layar akhir ---
    await pg.set_viewport_size({'width': 900, 'height': 700})
    await pg.evaluate('''() => { const G = window.__gargantua, M = G.MIS; G.startMission('polar'); G.SHIP.view = 'chase'; G.state.paused = true;
      G.state.scale0 = G.CONFIG.renderScale; G.CONFIG.renderScale = 0.2;   // jendela HUD butuh layar besar; render kecil agar frame cepat
      while (Math.hypot(...M.x) > 6) G.misFly(0.5); M.warp = 0; G.state.paused = false; }''')
    await pg.wait_for_timeout(1500)
    await pg.keyboard.press('KeyE')
    w1 = await pg.evaluate('() => ({ n: window.__gargantua.REL.drawn, fl: window.__gargantua.REL.flares.length })')
    await pg.wait_for_function(f"window.__gargantua.REL.drawn > {w1['n']}", timeout=20000)
    w2 = await pg.evaluate('() => window.__gargantua.REL.drawn')
    await pg.keyboard.press('KeyM'); await pg.evaluate('() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)))')
    w3 = await pg.evaluate('() => { const G = window.__gargantua; G.state.f0 = G.state.frame; return G.REL.drawn; }')
    await pg.wait_for_function('window.__gargantua.state.frame > window.__gargantua.state.f0 + 3', timeout=60000)
    w4 = await pg.evaluate('() => ({ n: window.__gargantua.REL.drawn, on: window.__gargantua.REL.on })')
    await pg.keyboard.press('KeyM')
    await pg.evaluate('() => { window.__gargantua.MIS.warp = 2; }')
    cek('jendela relai dan diagram tergambar, E = suar, M menyembunyikan', w2 > w1['n'] and w1['fl'] == 1 and w4['n'] == w3 and not w4['on'], f"{w1} {w2} {w4}")
    await pg.wait_for_function('!document.getElementById("mend").hidden', timeout=120000)
    await pg.wait_for_timeout(3000)
    e = await pg.evaluate('''() => { const c = document.getElementById('mendRelay'), d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
      let n = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 0) n++;
      const G = window.__gargantua; return { body: document.getElementById('mendBody').textContent, px: n / (c.width * c.height), Tx: G.REL.Tx }; }''')
    cek('layar akhir: pulsa dari dalam horizon, pesan relai, jendela relai hidup', 'Pulsa' in e['body'] and 'Pesan relai' in e['body'] and e['px'] > 0.5 and e['Tx'] > 0.5,
        f"isi kanvas {e['px'] * 100:.0f}%, waktu relai lanjut {e['Tx']:.1f} rs/c")
    await pg.keyboard.press('Escape')
    await pg.evaluate('() => { const G = window.__gargantua; G.CONFIG.renderScale = G.state.scale0; }')
    await pg.set_viewport_size({'width': 320, 'height': 200})
    await kelompok5(pg)

async def kelompok5(pg):
    import math
    a = await pg.evaluate('''() => { const G = window.__gargantua, out = {}; G.state.paused = true; G.startMission('tesseract');
      const d = G.CONFIG.disk, r1 = d.rOut; d.rOut = d.rIn;            // ambang tangkap tanpa piringan (lintasan lolos bisa menembus piringan saat keluar)
      out.dk = G.tesD(0); out.cap = G.tesRef({ delta: 1e-3, psi: 25 }).end; out.esc = G.tesRef({ delta: -1e-3, psi: 25 }).end; d.rOut = r1;
      out.sw = [1e-4, 1e-5, 1e-6].map((d) => G.tesRef({ delta: d, psi: 0 }).gate.sweep);
      out.p90 = [1e-2, 1e-4, 1e-6].map((d) => G.tesRef({ delta: d, psi: 90 }).end);
      let best = null; for (let k = 0; k <= 400; k++) { const de = Math.pow(10, -1 - k * 8 / 400), R = G.tesRef({ delta: de, psi: 25 });
        if (R.hit && (!best || R.err < best.err)) best = { de, err: R.err, sweep: R.gate.sweep, out: R.out }; }
      out.best = best; return out; }''')
    dk = math.degrees(math.asin(2 * math.sqrt(21) / 22))
    cek('sudut tangkap kritis d = asin(2 sqrt(21) / 22) = 24,62 derajat; sedikit di bawah tertangkap, di atas lolos',
        abs(a['dk'] - dk) < 1e-9 and a['cap'] == 'singularity' and a['esc'] == 'escape', f"{a['dk']:.6f} vs {dk:.6f}, {a['cap']} / {a['esc']}")
    per = (a['sw'][2] - a['sw'][0]) / 2; th = math.log(10) / math.sqrt(0.5) * 180 / math.pi
    cek('zoom-whirl: sapuan +ln(10)/sqrt(1/2) rad tiap delta 10x lebih kecil (eksponen orbit tak stabil 2 rs)', abs(per - th) < 2, f"{per:.2f} vs {th:.2f} derajat per dekade")
    cek('bidang orbit 90 derajat menembus piringan di 3-12 rs', all(e == 'disk' for e in a['p90']), str(a['p90']))
    b = a['best']
    cek('bidang 25 derajat: ada bidikan tepat sasaran (gerbang di bidang, galat < 5 derajat)', b is not None and b['out'] < 0.01, f"delta {b['de']:.2e}, galat {b['err']:.2f}, {b['sweep'] / 360:.2f} putaran" if b else 'tidak ada')

    # --- membidik dengan tombol: waktu beku, W/S, A/D, Enter ---
    await pg.evaluate("() => { const G = window.__gargantua; G.state.paused = false; G.startMission('tesseract'); G.MIS.warp = 2; }")
    d0 = await pg.evaluate('() => ({ ...window.__gargantua.MIS.tes.aim })')
    await pg.keyboard.down('KeyW'); await pg.wait_for_timeout(1200); await pg.keyboard.up('KeyW')
    await pg.keyboard.down('KeyD'); await pg.wait_for_timeout(800); await pg.keyboard.up('KeyD')
    await pg.wait_for_timeout(300)
    d1 = await pg.evaluate('() => { const M = window.__gargantua.MIS; return { aim: { ...M.tes.aim }, tau: M.tau, refA: { ...M.tes.ref.a } }; }')
    cek('membidik: waktu beku, W mendekat ke kritis, D memutar bidang, lintasan acuan ikut', d1['aim']['delta'] < d0['delta'] and d1['aim']['psi'] > d0['psi'] and d1['tau'] == 0
        and abs(d1['refA']['delta'] - d1['aim']['delta']) < 1e-15, f"delta {d0['delta']:.1e} -> {d1['aim']['delta']:.2e}, bidang {d1['aim']['psi']:.1f}")
    await pg.evaluate(f"() => {{ const G = window.__gargantua, M = G.MIS; M.tes.aim = {{ delta: {b['de']}, psi: 25 }}; G.tesApply(); }}")
    await pg.keyboard.press('Enter')
    await pg.wait_for_function('window.__gargantua.MIS.end !== null', timeout=180000)
    e = await pg.evaluate('''() => { const G = window.__gargantua, M = G.MIS, R = M.tes.ref, n = Math.hypot(...M.x), dir = M.x.map((v) => v / n);
      const err = Math.acos(Math.min(1, dir[0] * G.TES.gate[0] + dir[1] * G.TES.gate[1] + dir[2] * G.TES.gate[2])) * 180 / Math.PI;
      return { kind: M.end.kind, locked: M.tes.locked, r: n, err, tau: M.tau, gtau: R.gate.tau, tauH: M.tauH, h: R.horizon, tess: G.TESV.on, mend: document.getElementById('mend').hidden }; }''')
    cek('terbang mengikuti prakiraan: berakhir di gerbang (r 0,6, arah dalam 5 derajat), lewat horizon tercatat',
        e['kind'] == 'tesseract' and e['locked'] and abs(e['r'] - 0.6) < 0.02 and e['err'] < 5 and abs(e['tau'] - e['gtau']) < 1e-9 and e['tauH'] is not None and abs(e['tauH'] - e['h']) < 1e-12,
        f"r {e['r']:.4f}, galat {e['err']:.2f} derajat, tau {e['tau']:.4f} vs {e['gtau']:.4f}")
    cek('adegan tesseract tampil sebelum kartu akhir', e['tess'] and e['mend'], str({k: e[k] for k in ('tess', 'mend')}))
    await pg.evaluate('() => { window.__gargantua.TESV.t = 10.5; }')
    await pg.wait_for_function('!document.getElementById("mend").hidden', timeout=30000)
    body = await pg.evaluate('() => document.getElementById("mendBody").textContent')
    await pg.keyboard.press('Escape')
    f = await pg.evaluate('() => ({ tess: document.getElementById("tess").hidden, on: window.__gargantua.MIS.on })')
    cek('kartu akhir tesseract (bidikan, putaran, label fiksi), Esc keluar', 'Fiksi / spekulatif' in body and 'putaran' in body and f['tess'] and not f['on'], body[:80])

    # --- meleset: lanjut ke singularitas, catatan meleset ---
    m = await pg.evaluate('''() => { const G = window.__gargantua, M = G.MIS; G.state.paused = true; G.startMission('tesseract'); G.tesLaunch();
      let res = null; for (let i = 0; !res && i < 200000; i++) res = G.tesFollow(0.37 + (i % 7) * 0.05);
      return { kind: res && res.kind, miss: M.tes.miss, err: M.tes.ref.err }; }''')
    cek('bidikan meleset: lanjut ke singularitas, galat tercatat', m['kind'] == 'singularity' and m['miss'] is not None and m['miss'] > 5, str(m))
    await pg.evaluate('() => window.__gargantua.stopMission()')
    await kelompok7(pg)

async def kelompok7(pg):
    m = await pg.evaluate('''() => { const G = window.__gargantua, M = G.MIS, out = {}; G.state.paused = true;
      const at = (sc, r) => { G.startMission(sc); while (Math.hypot(...M.x) > r) if (G.misFly(0.1)) break; M.gas = G.gasRel(); return G.audioMix(); };
      out.retro = at('skim', 6); out.pro = at('skimPro', 6); out.pole = at('polar', 6);
      G.startMission('polar'); const st = { x: M.x, xd: M.xd, tau: 0 }; while (Math.hypot(...st.x) > 0.5) G.misAdvance(st, 0.02); M.x = st.x; M.xd = st.xd; M.gas = G.gasRel();
      out.inside = G.audioMix();
      G.state.paused = false; M.keys.add('KeyW'); M.thr = [1, 0, 0]; out.push = G.audioMix();
      G.startMission('tesseract'); M.keys.add('KeyW'); M.thr = [1, 0, 0]; out.aim = G.audioMix(); M.keys.clear();
      G.stopMission(); Object.assign(G.TESV, { on: true, t: 5 }); out.tess = G.audioMix(); G.TESV.on = false; G.state.paused = true;
      return out; }''')
    cek('suara: gemuruh piringan dekat piringan, lebih terang melawan arus, nol di jalur kutub',
        m['retro']['roar'] > 0.3 and m['retro']['roarCut'] > m['pro']['roarCut'] and m['pole']['roar'] == 0,
        f"melawan {m['retro']['roar']:.2f} / {m['retro']['roarCut']:.0f} Hz, searah {m['pro']['roar']:.2f} / {m['pro']['roarCut']:.0f} Hz, kutub {m['pole']['roar']}")
    cek('suara: nada pasang surut hanya di dalam horizon, pendorong saat W, tidak saat membidik, akord tesseract',
        m['pole']['tidal'] == 0 and m['inside']['tidal'] > 0 and m['push']['thr'] > 0 and m['aim']['thr'] == 0 and m['tess']['tess'] > 0 and m['tess']['hum'] == 0,
        f"pasang surut {m['inside']['tidal']:.2f} ({m['inside']['tidalF']:.0f} Hz), dorong {m['push']['thr']}, bidik {m['aim']['thr']}, tesseract {m['tess']['tess']:.2f}")
    await pg.keyboard.press('KeyH'); await pg.keyboard.press('KeyH')   # gerakan pengguna: AudioContext dibuat
    a0 = await pg.evaluate('() => { const A = window.__gargantua.AUDIO; return { ctx: !!A.ctx, on: A.on }; }')
    await pg.keyboard.press('KeyU')
    a1 = await pg.evaluate("() => ({ on: window.__gargantua.AUDIO.on, ls: localStorage.getItem('gargantua.sound') })")
    await pg.keyboard.press('KeyU')
    a2 = await pg.evaluate("() => ({ on: window.__gargantua.AUDIO.on, ls: localStorage.getItem('gargantua.sound'), panel: [...document.querySelectorAll('#uiBody label')].some((l) => l.textContent.includes('Suara (U)')) })")
    cek('suara: AudioContext dibuat setelah tombol, U bisu lalu nyala (tersimpan), pilihan di panel', a0['ctx'] and a0['on'] and not a1['on'] and a1['ls'] == '0' and a2['on'] and a2['ls'] == '1' and a2['panel'], f"{a0} {a1} {a2}")
    # --- panel bertab (seperti Copper) ---
    t = await pg.evaluate('''() => { const root = document.getElementById('uiBody'), tabs = [...root.querySelectorAll('#uiTabs [data-tab]')];
      const n = root.querySelectorAll('input, select, button').length - tabs.length;
      tabs.find((b) => b.dataset.tab === 'disk').click();
      const vis = [...root.querySelectorAll('[data-pane]')].filter((p) => getComputedStyle(p).display !== 'none').map((p) => p.dataset.pane);
      [...root.querySelectorAll('.btns button')].find((b) => b.textContent === 'English').click();
      const after = document.getElementById('uiBody').querySelector('#uiTabs .on').dataset.tab, lbl = document.getElementById('uiBody').querySelector('#uiTabs .on').textContent;
      [...document.querySelectorAll('#uiBody .btns button')].find((b) => b.textContent === 'Bahasa Indonesia').click();
      return { tabs: tabs.map((b) => b.textContent), n, vis, after, lbl, ls: localStorage.getItem('gargantua.panelTab') }; }''')
    cek('panel bertab: 7 tab, hanya satu pane tampil, tab diingat setelah ganti bahasa, semua kontrol tetap ada',
        len(t['tabs']) == 7 and t['vis'] == ['disk'] and t['after'] == 'disk' and t['lbl'] == 'Disk' and t['ls'] == 'disk' and t['n'] == 38, str(t))
    await kelompok8(pg)

async def kelompok8(pg):
    m = await pg.evaluate('''() => { const G = window.__gargantua, M = G.MIS, out = {}; G.state.paused = true;
      // l(r) vs integral numerik (r = u^2: dl = 2 sqrt(u^2 + 1) du, Simpson), z di titik penting
      const L = (R) => { const n = 2000, b = Math.sqrt(R), h = b / n, f = (u) => 2 * Math.sqrt(u * u + 1); let s = f(0) + f(b);
        for (let i = 1; i < n; i++) s += (i % 2 ? 4 : 2) * f(i * h); return s * h / 3; };
      out.lerr = Math.max(...[0.6, 1, 3, 22].map((r) => Math.abs(G.funL(r) - L(r))));
      out.z = [G.funZ(1), G.funZ(3), G.funZ(22)];
      // semua skenario: riwayat dan prakiraan berisi posisi, peta corong tergambar ke kanvas uji
      const cv = document.createElement('canvas'); cv.width = 290; cv.height = 313; const g = cv.getContext('2d', { willReadFrequently: true });
      out.sc = {};
      for (const sc of Object.keys(G.SCEN)) {
        G.startMission(sc); if (M.tes) G.tesLaunch(); else G.misFly(2);
        M.hist.push([M.tau, Math.hypot(...M.x), ...M.x]);
        g.clearRect(0, 0, 290, 313); const d0 = G.FUN.drawn; let err = null;
        try { G.drawFunnel(g, 0, 0, 290, 313, 1); } catch (e) { err = String(e); }
        const px = g.getImageData(0, 0, 290, 313).data; let lit = 0; for (let i = 0; i < px.length; i += 4) if (px[i] + px[i + 1] + px[i + 2] > 150) lit++;   // garis terang (latar gelap)
        out.sc[sc] = { err, drawn: G.FUN.drawn - d0, hist: M.hist.every((q) => q.length === 5), pred: !!M.pred && M.pred.pts.every((q) => q.length === 5), lit,
          plane: Math.abs(G.FUN.n[1]) };
      }
      // arah partikel: searah arus = titik pancar di citra lubang hitam; melawan arus = gas relatif apa adanya
      const ab = (R, d) => { const np = d.map((v) => -v), vn = np[0] * R.v[0] + np[1] * R.v[1] + np[2] * R.v[2];   // rumus skyShift: foton ke kerangka rain
        const pr = np.map((v, i) => v + R.v[i] * (R.g + R.g * R.g / (R.g + 1) * vn)), l = Math.hypot(...pr); return pr.map((v) => v / l); };
      const deg = (a, b) => Math.acos(Math.max(-1, Math.min(1, a[0] * b[0] + a[1] * b[1] + a[2] * b[2]))) * 180 / Math.PI;
      out.pro = []; out.retro = [];
      for (const r of [11, 8, 4]) {                              // > 12,6 rs tanpa debu (di luar piringan)
        G.startMission('skimPro'); while (Math.hypot(...M.x) > r) if (G.misFly(0.1)) break;
        let Gs = G.misGas(); const R = G.rainOf(M.x, M.xd), src = Gs.dir.map((v) => -v);
        out.pro.push({ r: Math.hypot(...M.x), dens: Gs.dens, v: Gs.v, vRaw: G.gasRel().v, dev: deg(ab(R, src), R.rh), oldDev: deg(ab(R, G.gasRel().dir.map((v) => -v)), R.rh) });
        G.startMission('skim'); while (Math.hypot(...M.x) > r) if (G.misFly(0.1)) break;
        Gs = G.misGas(); const Gr = G.gasRel();
        out.retro.push({ r: Math.hypot(...M.x), same: Gs.dir.every((v, i) => v === Gr.dir[i]) && Gs.v === Gr.v });
      }
      G.stopMission(); return out; }''')
    cek('peta corong: l(r) = integral sqrt(1 + 1/r) dr, z = 2 sqrt(r) (2 di horizon, 3,464 di ISCO, 9,381 di 22 rs)',
        m['lerr'] < 1e-6 and abs(m['z'][0] - 2) < 1e-12 and abs(m['z'][1] - 3.4641016) < 1e-6 and abs(m['z'][2] - 9.3808315) < 1e-6,
        f"galat l {m['lerr']:.1e}, z {[round(v, 4) for v in m['z']]}")
    sc = m['sc']
    ok = all(v['err'] is None and v['drawn'] == 1 and v['hist'] and v['pred'] and v['lit'] > 300 for v in sc.values())
    cek('peta corong: semua skenario tergambar tanpa error, riwayat dan prakiraan berisi posisi',
        ok and len(sc) == 10, '; '.join(f"{k} {v['lit']}" + (f" {v['err']}" if v['err'] else '') for k, v in sc.items()))
    cek('peta corong: susur di bidang piringan (cincin), jatuh kutub di bidang tegak (garis potong)',
        sc['skim']['plane'] > 0.95 and sc['skimPro']['plane'] > 0.95 and sc['polar']['plane'] < 0.05, f"skim {sc['skim']['plane']:.3f}, kutub {sc['polar']['plane']:.3f}")
    pro, retro = m['pro'], m['retro']
    cek('susur searah arus: partikel datang dari citra lubang hitam (aberasi), laju tetap fisika',
        all(q['dens'] > 0 and q['dev'] < 0.5 and q['oldDev'] > 5 and q['v'] == q['vRaw'] for q in pro),
        '; '.join(f"r {q['r']:.1f}: {q['dev']:.2f} derajat (dulu {q['oldDev']:.1f})" for q in pro))
    cek('susur melawan arus: arah dan laju gas relatif tidak berubah', all(q['same'] for q in retro), str(retro))
    # HUD hidup: tesseract = peta orbit saat membidik, corong setelah Enter (layar cukup besar)
    await pg.set_viewport_size({'width': 1280, 'height': 720})
    a, b, c, d, box = await pg.evaluate('''() => { const G = window.__gargantua, F = G.FUN, n = []; let t = 1e12;
      const dash = () => G.drawDash(t += 1000);                   // langsung (render SwiftShader 1280 x 720 lambat)
      G.state.paused = true; G.startMission('tesseract'); n.push(F.drawn); dash(); dash(); n.push(F.drawn);
      G.tesLaunch(); dash(); n.push(F.drawn); G.startMission('polar'); dash(); n.push(F.drawn); n.push(F.box.slice()); G.stopMission(); return n; }''')
    await pg.set_viewport_size({'width': 320, 'height': 200})
    cek('HUD: panel corong seukuran jendela relai (lebar 340, tinggi sampai 380, rata bawah 44 px dari tepi)',
        abs(box[2] - 340) < 0.01 and 190 < box[3] <= 380 and abs(box[1] + box[3] - (720 - 44)) < 0.01, str([round(v, 1) for v in box]))
    cek('HUD: tesseract membidik = peta orbit (corong tidak), setelah Enter dan misi lain = peta corong', a == b and c == b + 1 and d == c + 1, f"{a} {b} {c} {d}")
    await kelompok9(pg)

async def kelompok9(pg):
    m = await pg.evaluate('''() => { const G = window.__gargantua, M = G.MIS, out = {}; G.state.paused = true;
      G.startMission('polar'); G.setShip(true, 'chase'); const seq = [];
      for (let i = 0; i < 3; i++) { G.cycleShipView(); seq.push(G.SHIP.view); }
      G.setShip(true, 'relay'); const b = G.viewBasis(); out.seq = seq; out.r = Math.hypot(...b.pos); out.eye = b.eye; out.relay = !!b.relay;
      // sinar seperti shader: arah layar -> vel (aberasi ke kerangka rain) lalu x'' = -1,5 h^2 x / r^5, jarak terdekat ke titik pancar
      const V = G.REL.view, vv = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2], add = (a, b, k = 1) => a.map((x, i) => x + k * b[i]);
      const shaderVel = (dir) => { const np = dir.map((x) => -x), o = V.obs, vn = vv(o.v, np), pr = add(np, o.v, o.g + o.g * o.g / (o.g + 1) * vn);
        const pl = Math.hypot(...pr), nr = pr.map((x) => x / pl), rh = V.pos.map((x) => x / Math.hypot(...V.pos)), vel = add(nr.map((x) => -x), rh, o.beta), l = Math.hypot(...vel); return vel.map((x) => x / l); };
      const miss = (vel, xe) => { let p = V.pos.slice(), v = vel.slice(); const L = [p[1] * v[2] - p[2] * v[1], p[2] * v[0] - p[0] * v[2], p[0] * v[1] - p[1] * v[0]], h2 = vv(L, L); let best = 1e9;
        const acc = (p) => { const r2 = vv(p, p); return p.map((x) => -1.5 * h2 * x / (r2 * r2 * Math.sqrt(r2))); };
        for (let i = 0; i < 300000; i++) { const r = Math.hypot(...p), ds = Math.min(0.002 * r, 0.05), q = p;
          const a1 = acc(p), p2 = add(p, v, ds / 2), v2 = add(v, a1, ds / 2), a2 = acc(p2), p3 = add(p, v2, ds / 2), v3_ = add(v, a2, ds / 2), a3 = acc(p3), p4 = add(p, v3_, ds), v4 = add(v, a3, ds), a4 = acc(p4);
          p = p.map((x, k) => x + ds / 6 * (v[k] + 2 * v2[k] + 2 * v3_[k] + v4[k])); v = v.map((x, k) => x + ds / 6 * (a1[k] + 2 * a2[k] + 2 * a3[k] + a4[k]));
          const d = add(p, q, -1), t = Math.max(0, Math.min(1, vv(add(xe, q, -1), d) / Math.max(vv(d, d), 1e-30))); best = Math.min(best, Math.hypot(...add(add(q, d, t), xe, -1)));
          if (Math.hypot(...p) < 1 || Math.hypot(...p) > 120) break; }
        return best; };
      const er = V.pos.map((x) => x / 22), side = (() => { const c = [er[1] * 0 - er[2] * 1, er[2] * 0 - er[0] * 0, er[0] * 1 - er[1] * 0], l = Math.hypot(...c); return c.map((x) => x / l); })();
      const t0 = (() => { const c = [side[1] * er[2] - side[2] * er[1], side[2] * er[0] - side[0] * er[2], side[0] * er[1] - side[1] * er[0]], l = Math.hypot(...c); return c.map((x) => x / l); })();
      out.pts = [[10, 0.4], [5, 1.3], [2, 2.9], [8, Math.PI - 1e-3], [1.05, 2.4], [40, 1.0]].map(([re, a]) => {
        const xe = add(er.map((x) => x * Math.cos(a) * re), t0, Math.sin(a) * re), t = performance.now(), I = G.relImage(xe), ms = performance.now() - t;
        const vel = shaderVel(I.d); return { re, a, miss: miss(vel, xe), dv: Math.hypot(...add(vel, I.vel0, -1)), ms }; });
      const c = G.relImage(er.map((x) => x * 6)), cd = Math.hypot(...add(shaderVel(c.d), er, 1));
      out.centre = cd; out.inside = G.relImage(er.map((x) => x * 0.8)) === null;
      // titik di bawah piringan dilihat dari relai di atas piringan: tertutup piringan
      const above = V.pos[1] > 0, xe = [6 * Math.cos(1), above ? -0.3 : 0.3, 6 * Math.sin(1)];
      out.occ = G.relImage(xe).occ; out.free = G.relImage([0, above ? 8 : -8, 0]).occ;
      // lapisan HUD: titik wahana tergambar
      const cv = document.createElement('canvas'); cv.width = 1280; cv.height = 720; G.REL.view.cur = null; G.drawRelayView(cv.getContext('2d'), 1280, 720, 1, 1e12);
      out.drawn = G.REL.view.drawn || 0;
      // suar: dari 10 rs diterima saat waktu relai >= waktu tiba; dari dalam horizon tidak pernah
      G.startMission('polar'); while (Math.hypot(...M.x) > 10) G.misFly(0.2);
      G.fireFlare(); const F = G.REL.flares[G.REL.flares.length - 1]; G.relStep(0.01); out.before = F.seen;
      while (!M.end && M.T < F.arr + 0.5) { const r = G.misFly(0.2); if (r) break; } G.relStep(0.01); out.after = F.seen; out.arr = F.arr;
      G.startMission('polar'); while (Math.hypot(...M.x) > 0.5) G.misFly(0.05);
      G.fireFlare(); const F2 = G.REL.flares[G.REL.flares.length - 1]; G.REL.Tx = 1e6; G.relStep(0.01); out.never = F2.seen; out.arr2 = F2.arr;
      G.stopMission(); out.after_stop = G.SHIP.view; return out; }''')
    cek('V di misi: kamera luar -> kokpit -> relai -> kamera luar; relai di 22 rs tanpa model wahana',
        m['seq'] == ['cockpit', 'relay', 'chase'] and abs(m['r'] - 22) < 1e-9 and m['eye'] is None and m['relay'] and m['after_stop'] == 'chase', str({k: m[k] for k in ('seq', 'r', 'eye', 'after_stop')}))
    pts = m['pts']
    cek('citra lensa: sinar shader dari arah titik melewati titik pancar (depan, samping, di balik lubang hitam, r 1,05, r 40)',
        all(q['miss'] < 1e-4 and q['dv'] < 1e-9 for q in pts), '; '.join(f"r {q['re']}: {q['miss']:.1e} rs {q['ms']:.0f} ms" for q in pts))
    cek('citra lensa: segaris relai-pusat = arah pusat, dari dalam horizon tidak ada citra, di balik piringan ditandai',
        m['centre'] < 1e-9 and m['inside'] and m['occ'] and not m['free'], f"pusat {m['centre']:.1e}, tertutup {m['occ']}, bebas {m['free']}")
    cek('pandangan relai: titik wahana tergambar di lapisan HUD', m['drawn'] >= 1, str(m['drawn']))
    cek('suar dari 10 rs diterima relai setelah waktu tiba; suar dari dalam horizon tidak pernah',
        m['before'] is None and m['after'] is not None and m['after'] >= m['arr'] and m['never'] is None and (m['arr2'] is None or m['arr2'] == float('inf')),
        f"tiba {m['arr']:.2f}, diterima {m['after']}, dalam horizon {m['never']}")
    # render pandangan relai tanpa nilai tidak valid
    st = await pg.evaluate('''() => new Promise((res) => { const G = window.__gargantua; G.state.paused = true; G.startMission('skim'); G.setShip(true, 'relay');
      setTimeout(() => { G.state.readCb = (r) => { G.stopMission(); res(r); }; }, 600); })''')
    cek('render pandangan relai tanpa nilai tidak valid', st['bad'] == 0 and st['mean'] > 0, str(st))

asyncio.run(main())
