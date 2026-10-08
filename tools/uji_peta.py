"""Uji 13d + peta A (Copper Corn Station): peta besar M. Kanvas dan latar tergambar, 22 penanda lokasi di dalam bingkai,
zoom dan pusatkan ke pemain, klik penanda memindah pemain dan menutup peta, legenda ikut bahasa; peta A: 8 tempat fisika
(lokasi tujuan tidak di dalam collider atau air, hub = melayang), tab samping (satu panel tampil, tab diingat), hologram 3D
tergambar dan sorotan memutar silinder sampai tempat itu menghadap pengamat.
Pakai: python tools/uji_peta.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, os, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(async () => {
  const S = window.__station, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms));
  document.getElementById('start').hidden = true;
  S.toggleMap(); await wait(2500);
  const cv = document.getElementById('mapCanvas');
  out[`kanvas peta ${cv.width}x${cv.height}`] = cv.width > 400 && cv.height > 250;
  const px = cv.getContext('2d').getImageData(cv.width * 0.3 | 0, cv.height / 2 | 0, 1, 1).data;
  out['latar dan rel tergambar'] = px[3] === 255 && px[0] + px[1] + px[2] > 60;
  const inside = S.MAP_MARKS.filter((m) => m.px >= 0 && m.px <= cv.width && m.py >= 0 && m.py <= cv.height).length;
  out[`penanda di dalam bingkai: ${inside} dari ${S.MAP_MARKS.length}`] = inside === S.MAP_MARKS.length && inside >= 22;
  S.mapZoomAt(3); S.mapCenterMe();
  const pxP = S.MAPV.W / 2 + (S.player.za - S.MAPV.cx) * S.MAPV.k;
  out[`zoom ${S.MAPV.zoom}, pemain terlihat di peta (x ${Math.round(pxP)} dari ${S.MAPV.W})`] = S.MAPV.zoom > 1 && pxP > 0 && pxP < S.MAPV.W;
  S.mapGo(S.MAP_MARKS[5]);
  out['klik penanda 6: pindah ke lapangan baseball, peta tertutup'] = document.getElementById('map').hidden && Math.abs(S.player.za - S.SPOTS.baseball.za) < 1;
  // peta A: tempat fisika
  const fis = S.MAP_MARKS.filter((m) => m.fis);
  out[`tempat fisika: ${fis.map((m) => m.key).join(' ')}`] = fis.length === 8 && new Set(S.MAP_MARKS.map((m) => m.key)).size === S.MAP_MARKS.length;
  for (const k of ['aqueduct', 'pump', 'lake', 'ring', 'capB']) {
    const T = S.SPOTS[k]; if (!T) { out[`lokasi ${k} ada`] = false; continue; }
    const col = S.colAt(T.s, T.za, 0.4), w = S.waterAt(T.s, T.za);
    out[`lokasi ${k}: s ${Math.round(T.s)} za ${Math.round(T.za)}, tanpa collider, tidak di air (kedalaman ${w ? w.depth.toFixed(2) : 0})`] = !col && !(w && w.depth > 0.05);
  }
  S.MAP_MARKS.find((m) => m.key === 'H').go();
  out[`H: hub nol-g, state ${S.player.state}`] = S.player.state === 'float';
  S.MAP_MARKS.find((m) => m.key === 'D').go();
  out[`D: dek pandang, h ${Math.round(S.player.h)}`] = S.player.deck && S.player.h > 170;
  S.MAP_MARKS.find((m) => m.key === 'W').go();
  out['W: danau terbesar'] = S.player.state === 'ground' && Math.abs(S.player.za - S.SPOTS.lake.za) < 1;
  // tab dan hologram (mapGo menutup peta lewat toggleMap, jadi buka hanya bila tertutup)
  if (document.getElementById('map').hidden) S.toggleMap(); await wait(300);
  S.mapTab('fisika');
  const shown = [...document.querySelectorAll('#mapLegend [data-mpane]')].filter((d) => !d.hidden).map((d) => d.dataset.mpane);
  out[`tab: panel tampil ${shown.join(',')}, ${document.querySelectorAll('#mapLegend [data-mpane=fisika] button').length} tombol fisika`] = shown.length === 1 && shown[0] === 'fisika' && document.querySelectorAll('#mapLegend [data-mpane=fisika] button').length === 8;
  out['tab diingat'] = localStorage.getItem('cooperStation.mapTab') === 'fisika';
  // hologram menimpa peta 2D di kanvas yang sama
  out['tidak ada kanvas hologram terpisah'] = !document.getElementById('mapHolo');
  const cv2 = document.getElementById('mapCanvas'), g2 = cv2.getContext('2d'), snap = () => g2.getImageData(0, 0, cv2.width, cv2.height).data;
  S.HOLO.on = false; S.HOLO.ctl = false; S.drawMap(); const d0 = snap();
  S.HOLO.on = true; S.drawMap(); const d1 = snap();
  let diff = 0; for (let i = 0; i < d0.length; i += 4) if (Math.abs(d0[i] - d1[i]) + Math.abs(d0[i + 1] - d1[i + 1]) + Math.abs(d0[i + 2] - d1[i + 2]) > 30) diff++;
  out[`hologram tergambar di atas peta 2D (${diff} piksel berubah dari ${cv2.width * cv2.height})`] = diff > 3000 && diff < cv2.width * cv2.height * 0.5;
  const m = S.MAP_MARKS.find((x) => x.key === 'U'), p = m.at();
  S.MAPV.hl = { s: p.s, za: p.za, h: 0, name: m.name, i: -1 }; for (let i = 0; i < 40; i++) S.drawHolo(g2, 0.1);   // langkah frame langsung (sandbox lambat)
  const o = S.holoP(p.s, p.za, 0, [0, 0, 0]), o2 = S.holoP(p.s + Math.PI * S.R, p.za, 0, [0, 0, 0]);   // titik di seberang keliling
  out[`sorot U: hologram berputar sampai tempat di sisi dekat (beda kedalaman dengan seberang ${(o[2] - o2[2]).toFixed(2)} dari maks 2)`] = o[2] - o2[2] > 1.8;
  S.MAPV.hl = null;
  // kendali 3D: roda = zoom hologram (peta 2D tetap), seret = putar, seret tanpa kendali 3D = geser peta 2D
  const ev = (type, x, y, extra = {}) => { const r = cv2.getBoundingClientRect(); return new PointerEvent(type, { clientX: r.left + x, clientY: r.top + y, pointerId: 7, bubbles: true, button: 0, ...extra }); };
  const drag = (x0, y0, x1, y1, extra) => { cv2.dispatchEvent(ev('pointerdown', x0, y0, extra)); for (let i = 1; i <= 5; i++) cv2.dispatchEvent(ev('pointermove', x0 + (x1 - x0) * i / 5, y0 + (y1 - y0) * i / 5, extra)); cv2.dispatchEvent(ev('pointerup', x1, y1, extra)); };
  document.getElementById('mapCtlBtn').click();
  const mz = S.MAPV.zoom, hz = S.HOLO.zoom, mcx = S.MAPV.cx;
  cv2.dispatchEvent(new WheelEvent('wheel', { deltaY: -400, clientX: cv2.getBoundingClientRect().left + 200, clientY: cv2.getBoundingClientRect().top + 150, bubbles: true, cancelable: true }));
  out[`kendali 3D: roda zoom hologram ${hz} -> ${S.HOLO.zoom.toFixed(2)}, peta 2D tetap ${mz}`] = S.HOLO.ctl && S.HOLO.zoom > hz * 1.5 && S.MAPV.zoom === mz;
  const y0 = S.HOLO.yaw, p0 = S.HOLO.pitch; drag(300, 200, 400, 240);
  out[`kendali 3D: seret memutar hologram (yaw ${y0.toFixed(2)} -> ${S.HOLO.yaw.toFixed(2)}, pitch ${p0.toFixed(2)} -> ${S.HOLO.pitch.toFixed(2)}), peta 2D tidak bergeser`] = S.HOLO.yaw > y0 + 0.5 && S.HOLO.pitch > p0 + 0.2 && S.MAPV.cx === mcx;
  const px0 = S.HOLO.px; drag(300, 200, 360, 200, { button: 2 });
  out[`kendali 3D: seret kanan menggeser hologram (${px0} -> ${Math.round(S.HOLO.px)})`] = S.HOLO.px > px0 + 50;
  S.holoReset(); document.getElementById('mapCtlBtn').click(); S.mapZoomAt(3);
  const cxA = S.MAPV.cx, yA = S.HOLO.yaw; drag(300, 200, 200, 200);
  out[`tanpa kendali 3D: seret menggeser peta 2D (cx ${Math.round(cxA)} -> ${Math.round(S.MAPV.cx)}), hologram tetap`] = S.MAPV.cx > cxA + 10 && S.HOLO.yaw === yA && !S.HOLO.ctl;
  const yB = S.HOLO.yaw; drag(300, 200, 360, 200, { button: 2 });
  out['tanpa kendali 3D: seret kanan memutar hologram'] = S.HOLO.yaw > yB + 0.3;
  document.getElementById('mapHoloBtn').click();
  out['tombol Hologram: sembunyi (kendali 3D ikut mati dan tombolnya tersembunyi)'] = !S.HOLO.on && !S.HOLO.ctl && document.getElementById('mapCtlBtn').hidden;
  document.getElementById('mapHoloBtn').click();
  out['tombol Hologram: tampil lagi, diingat'] = S.HOLO.on && localStorage.getItem('cooperStation.mapHolo') === '1';
  S.holoReset();
  S.MAPV.hl = null; S.mapTab('tempat'); S.toggleMap();
  S.setLang('en'); S.toggleMap(); await wait(300);
  const lh = [...document.querySelectorAll('#mapLegend .lh')].map((x) => x.textContent).join(' | ');
  out[`legenda English: ${lh}`] = /Places/.test(lh); S.toggleMap(); S.setLang('id');
  return out;
})()
"""

async def main():
    page_url = pathlib.Path(__file__).resolve().parent.parent.joinpath('experiences/cooper-station/index.html').as_uri()
    async with async_playwright() as p:
        kw = {'executable_path': os.environ['CHROMIUM']} if os.environ.get('CHROMIUM') else {}
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'], **kw)
        pg = await b.new_page(viewport={'width': 1200, 'height': 800})
        errs = []
        pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
        await pg.goto(page_url)
        await pg.wait_for_function('window.__stationReady === true', timeout=240000)
        for k, v in (await pg.evaluate(UJI)).items(): print(('OK   ' if v else 'GAGAL'), k)
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())
