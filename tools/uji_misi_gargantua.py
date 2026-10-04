"""Uji misi Gargantua (docs/gargantua/rencana-misi-lubang-hitam.md). Bagian per kelompok; sekarang kelompok 1 (G1):
- aset GX-01 termuat (jumlah verteks = metadata, ada kaca kokpit, kaki dilipat: tidak ada titik di bawah -2,45 m),
- V menyalakan wahana (kamera luar), V lagi = kokpit, Esc mematikan; tombol panel ada,
- wahana benar-benar tergambar (piksel berbeda dari tanpa wahana di kamera luar), kokpit menampilkan dasbor,
- tampilan lama tidak berubah saat wahana mati (sebelum dan sesudah menyalakan lalu mematikan wahana: piksel sama
  saat waktu dijeda),
- kamus Indonesia lengkap untuk teks baru, tanpa error konsol / WebGL.
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
        cek('V = wahana menyala, kamera luar', on['on'] and on['view'] == 'chase' and on['dash'], str(on))
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
                 'Distance to centre', 'Holding position (fall: stage G2)', 'View', 'Cockpit']
        hilang = [k for k in kunci if f"'{k}':" not in src]
        cek('kamus ID lengkap untuk teks G1', not hilang, ', '.join(hilang) or f'{len(kunci)} kunci')

        cek('tanpa error konsol / WebGL', not errs, '; '.join(errs[:3]))
        await b.close()
    print(f'\n{sum(hasil)}/{len(hasil)} lulus')
    sys.exit(0 if all(hasil) else 1)

asyncio.run(main())
