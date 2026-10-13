"""Uji tahap 12d (Copper Corn Station): siklus tanam gandum dan mesin ladang, mode foto (FOV, blur, simpan PNG,
semua dikembalikan saat keluar), tur sinematik v2 (18 titik sekitar 4 menit, jam 12:00 sampai 07:00, cuaca cerah -> hujan -> cerah, genangan, gerhana,
pembuka dan penutup kamera luar, tanpa NaN, tidak melewati sumbu, posisi / jam / cuaca / orbit dikembalikan).
Pakai: python tools/uji_ladang_foto_tur.py   (butuh: pip install playwright && playwright install chromium; CHROMIUM opsional)"""
import asyncio, os, pathlib
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
  // C3: tur sinematik (tur v2: 18 titik, jam 12:00 -> pagi, cuaca, genangan, gerhana, pembuka dan penutup luar)
  const p0 = { th: st.player.theta, za: st.player.za };
  const w0 = { hour: st.clock.hour, rate: st.clock.hourRate, orbit: st.clock.orbit, mode: st.WEATHER.mode };
  st.startTour();
  const hour0 = st.clock.hour, N = st.TOUR.keys.length;
  let bad = false, maxH = 0, steps = 0, fadeMax = 0;
  const idx = new Set(), K = {};                                     // per judul titik: jam akhir, hujan maks, basah min, gerhana min, kamera luar
  for (let k = 0; k < 8000 && st.TOUR.on; k++, steps++) {
    const i = st.TOUR.i, key = st.TOUR.keys[i];
    st.stepTour(0.05); st.updateClouds(0.05); st.updateRain(0.05); st.updateFar();
    if (!st.TOUR.on) break;
    idx.add(st.TOUR.i);
    const r = K[key.title] || (K[key.title] = { rain: 0, wet: 1, ecl: 1, ext: false });
    r.hour = st.clock.hour; r.rain = Math.max(r.rain, st.RAIN.k); r.wet = Math.min(r.wet, st.RAIN.wet); r.ecl = Math.min(r.ecl, st.ECL.k); r.ext = r.ext || st.ext.active;
    fadeMax = Math.max(fadeMax, +document.getElementById('tourFade').style.opacity || 0);
    const P = st.player; if (!isFinite(P.theta + P.za + P.h + P.heading + P.pitch + st.clock.hour + st.camera.position.length())) bad = true;
    if (!st.ext.active) maxH = Math.max(maxH, P.h);
  }
  const T = steps * 0.05, get = (n) => K[n] || {};
  out[`tur: ${idx.size} dari ${N} titik, ${T.toFixed(0)} s (target 200-270 s), tanpa NaN`] = !bad && idx.size === N && N >= 18 && T > 200 && T < 270;
  out[`tur: tinggi maksimum ${maxH.toFixed(0)} m (tidak melewati sumbu)`] = maxH < st.R - 30;
  out[`tur: jam mulai ${hour0.toFixed(2)}, akhir ${(get('Meninggalkan stasiun').hour || 0).toFixed(2)}`] = hour0 === 12 && Math.abs(get('Meninggalkan stasiun').hour - 7) < 0.05;
  out['tur: pembuka dan penutup di kamera luar'] = !!get('Menuju Copper Corn Station').ext && !!get('Meninggalkan stasiun').ext;
  out[`tur: siang cerah tanpa hujan (${get('Ukuran stasiun').rain.toFixed(2)}), hujan di sungai ${get('Hujan miring').rain.toFixed(2)}`] = get('Ukuran stasiun').rain < 0.05 && get('Hujan miring').rain > 0.5;
  out[`tur: hujan reda di dek malam (${get('Dek pandang malam').rain.toFixed(2)} di akhir)`] = st.RAIN.k < 0.3;
  out[`tur: genangan di trem malam (basah min ${get('Trem malam').wet.toFixed(2)})`] = get('Trem malam').wet > 0.5;
  out[`tur: gerhana Saturnus (ECL.k min ${get('Gerhana Saturnus').ecl.toFixed(2)})`] = get('Gerhana Saturnus').ecl < 0.2;
  out[`tur: layar gelap saat pindah kamera (maks ${fadeMax.toFixed(2)})`] = fadeMax > 0.9;
  out['tur selesai: kembali ke posisi awal, berjalan'] = !st.TOUR.on && st.player.state === 'ground' && Math.abs(st.player.za - p0.za) < 0.01 && Math.abs(st.player.theta - p0.th) < 1e-6 && !st.ext.active;
  out['tur selesai: jam, laju jam, orbit, cuaca dikembalikan'] = st.clock.hour === w0.hour && st.clock.hourRate === w0.rate && st.clock.orbit === w0.orbit && st.WEATHER.mode === w0.mode && !st.WEATHER.fast && document.getElementById('tourFade').style.opacity === '0';
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
