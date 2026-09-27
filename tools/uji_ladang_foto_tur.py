"""Uji tahap 12d (Copper Corn Station): siklus tanam gandum dan mesin ladang, mode foto (FOV, blur, simpan PNG,
semua dikembalikan saat keluar), tur sinematik (9 titik, tanpa NaN, tidak melewati sumbu, kembali ke posisi awal).
Pakai: python tools/uji_ladang_foto_tur.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(async () => {
  const st = window.__station, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms));
  // B4: siklus tanam dan mesin
  const wheat = st.fieldList.filter((f) => f.crop === 'wheat' && !f.meadow), n = [0, 0, 0, 0];
  for (const f of wheat) { const ph = st.farmStage(f); n[ph < 0.45 ? 0 : ph < 0.72 ? 1 : ph < 0.82 ? 2 : 3]++; }
  out[`gandum per tahap: tumbuh ${n[0]}, menguning ${n[1]}, masak ${n[2]}, tunggul ${n[3]}`] = n.every((x) => x > 0);
  st.clock.hour = 11; st.teleport('wheat'); await wait(4000);
  out[`mesin ladang dekat pemain: ${st.FARM.machines.length}`] = st.FARM.machines.length > 0;
  // C2: mode foto
  const rate0 = st.clock.hourRate;
  st.togglePhoto(true);
  const set = (id, v, ev) => { const el = document.getElementById(id); if (el.type === 'checkbox') el.checked = v; else el.value = v; el.dispatchEvent(new Event(ev || 'input')); };
  set('phFov', 40); set('phBlur', 0.6); set('phPause', true, 'change');
  await wait(300);
  out[`mode foto: FOV ${st.camera.fov}, blur ${st.compMat.uniforms.uDof.value}, waktu berhenti`] = st.camera.fov === 40 && st.compMat.uniforms.uDof.value === 0.6 && st.clock.hourRate === 0;
  out['mode foto: HUD tersembunyi'] = getComputedStyle(document.getElementById('hud')).display === 'none';
  const url = await new Promise((r) => { window.__captureCb = r; });
  out[`tangkapan PNG ${url.length} karakter`] = url.startsWith('data:image/png') && url.length > 5000;
  st.togglePhoto(false);
  out['keluar mode foto: FOV, blur, waktu kembali'] = st.camera.fov === st.CONFIG.fov && st.compMat.uniforms.uDof.value === 0 && st.clock.hourRate === rate0;
  // C3: tur sinematik
  const p0 = { th: st.player.theta, za: st.player.za };
  st.startTour();
  let bad = false, maxH = 0, ext = false, steps = 0;
  const idx = new Set();
  for (let k = 0; k < 6000 && st.TOUR.on; k++, steps++) {
    st.stepTour(0.05); if (st.TOUR.on) idx.add(st.TOUR.i);
    const P = st.player; if (!isFinite(P.theta + P.za + P.h + P.heading + P.pitch)) bad = true;
    maxH = Math.max(maxH, P.h); if (st.ext.active) ext = true;
  }
  out[`tur: ${idx.size} titik, ${(steps * 0.05).toFixed(0)} s, tanpa NaN`] = !bad && idx.size >= 9;
  out[`tur: tinggi maksimum ${maxH.toFixed(0)} m (tidak melewati sumbu)`] = maxH < st.R - 30;
  out['tur: segmen kamera luar'] = ext;
  out['tur selesai: kembali ke posisi awal, berjalan'] = !st.TOUR.on && st.player.state === 'ground' && Math.abs(st.player.za - p0.za) < 0.01 && Math.abs(st.player.theta - p0.th) < 1e-6 && !st.ext.active;
  return out;
})()
"""

async def main():
    page_url = pathlib.Path(__file__).resolve().parent.parent.joinpath('experiences/cooper-station/index.html').as_uri()
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        pg = await b.new_page(viewport={'width': 320, 'height': 200})
        errs = []
        pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
        await pg.goto(page_url)
        await pg.wait_for_function('window.__stationReady === true', timeout=240000)
        for k, v in (await pg.evaluate(UJI)).items(): print(('OK   ' if v else 'GAGAL'), k)
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())
