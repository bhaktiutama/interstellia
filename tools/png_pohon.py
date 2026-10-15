"""Bangkitkan satu halaman PNG berisi semua jenis pohon Copper Corn Station (21 jenis x 2 template = 42 pohon).
Memuat experiences/cooper-station/index.html, memanggang tiap template (T.bakeS) ke target 480 x 600 lewat renderer game,
lalu menyusun lembar dengan Pillow. Pakai: python tools/png_pohon.py [keluaran.png]   (butuh playwright, pillow; CHROMIUM opsional)"""
import asyncio, base64, io, os, pathlib, sys
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont

TW, TH = 480, 600
JS = r"""
async (dim) => {
  const [TW, TH] = dim, st = window.__station, T = st.TREES, THREE = st.THREE, r = st.renderer, out = [];
  const rt = new THREE.WebGLRenderTarget(TW, TH, { samples: 4 });
  const buf = new Uint8Array(TW * TH * 4);
  const prev = r.getRenderTarget(), pc = new THREE.Color(), pa = r.getClearAlpha(); r.getClearColor(pc);
  T.templates.forEach((M, i) => {
    const h = M.height + 0.6, w = M.halfW * 2 + 0.6, s = Math.max(h / TH, w / TW) * 1.06;   // m per piksel
    const cam = new THREE.OrthographicCamera(-TW * s / 2, TW * s / 2, TH * s - 0.4 - (TH * s - h) / 2, -0.4 - (TH * s - h) / 2, 0.1, 200);
    cam.position.set(0, 0, 60); cam.lookAt(0, 0, 0);
    r.setRenderTarget(rt); r.setClearColor(0x000000, 0); r.clear(); r.render(M.bakeS, cam);
    r.readRenderTargetPixels(rt, 0, 0, TW, TH, buf);
    let bin = ''; for (let k = 0; k < buf.length; k += 8192) bin += String.fromCharCode.apply(null, buf.subarray(k, k + 8192));
    out.push({ i, kind: M.kind, height: M.height, halfW: M.halfW, px: btoa(bin) });
  });
  r.setRenderTarget(prev); r.setClearColor(pc, pa);
  return out;
}
"""

async def main(out):
    root = pathlib.Path(__file__).resolve().parent.parent
    kw = {'executable_path': os.environ['CHROMIUM']} if os.environ.get('CHROMIUM') else {}
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'], **kw)
        pg = await b.new_page(viewport={'width': 800, 'height': 450})
        pg.on('pageerror', lambda e: print('ERR', e))
        await pg.goto((root / 'experiences/cooper-station/index.html').as_uri())
        await pg.wait_for_function('window.__stationReady === true', timeout=300000)
        data = await pg.evaluate(JS, [TW, TH])
        await b.close()
    names = {'oak': 'Oak', 'elm': 'Elm', 'poplar': 'Poplar', 'maple': 'Maple', 'birch': 'Birch', 'pine': 'Pine', 'willow': 'Willow',
             'bunga': 'Flowering tree', 'aspen': 'Aspen', 'beech': 'Beech', 'basswood': 'Basswood', 'chestnut': 'Chestnut', 'ash': 'Ash',
             'walnut': 'Walnut', 'hickory': 'Hickory', 'blacklocust': 'Black locust', 'honeylocust': 'Honey locust', 'fir': 'Fir',
             'hemlock': 'Hemlock', 'arborvitae': 'Arborvitae', 'redcedar': 'Red cedar'}
    try: F = ImageFont.truetype('DejaVuSans.ttf', 22); F2 = ImageFont.truetype('DejaVuSans.ttf', 16); F3 = ImageFont.truetype('DejaVuSans-Bold.ttf', 34)
    except OSError: F = F2 = F3 = ImageFont.load_default()
    cols, LH, G = 6, 60, 12
    rows = (len(data) + cols - 1) // cols
    HEAD = 90
    W, H = cols * (TW + G) + G, HEAD + rows * (TH + LH + G) + G
    sheet = Image.new('RGB', (W, H), (18, 24, 33)); d = ImageDraw.Draw(sheet)
    d.text((G + 8, 18), 'Copper Corn Station: semua jenis pohon (21 jenis, 42 template)', font=F3, fill=(235, 240, 245))
    d.text((G + 8, 62), 'Hasil panggang template game (warna dasar atlas daun, tanpa pencahayaan kota dan tanpa mode Campur / Gugur); skala tiap kotak disesuaikan, tinggi dan lebar dalam meter', font=F2, fill=(150, 165, 180))
    seen = {}
    for n, t in enumerate(data):
        im = Image.frombytes('RGBA', (TW, TH), base64.b64decode(t['px'])).transpose(Image.FLIP_TOP_BOTTOM)
        bg = Image.new('RGBA', (TW, TH)); g = ImageDraw.Draw(bg)
        for y in range(TH):
            k = y / TH; g.line([(0, y), (TW, y)], fill=(int(120 + 70 * k), int(165 + 50 * k), int(205 + 30 * k), 255))
        bg.alpha_composite(im)   # latar langit sederhana; piksel semi transparan dicampur (alpha lurus)
        x, y = G + (n % cols) * (TW + G), HEAD + (n // cols) * (TH + LH + G)
        sheet.paste(bg.convert('RGB'), (x, y))
        v = seen.get(t['kind'], 0); seen[t['kind']] = v + 1
        d.text((x + 4, y + TH + 6), f"{names.get(t['kind'], t['kind'])} (varian {v + 1})", font=F, fill=(235, 240, 245))
        d.text((x + 4, y + TH + 34), f"template {t['i']}: tinggi {t['height']:.1f} m, lebar {2 * t['halfW']:.1f} m", font=F2, fill=(150, 165, 180))
    sheet.save(out); print(out, sheet.size, len(data), 'template')

asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'pohon-copper-station.png'))
